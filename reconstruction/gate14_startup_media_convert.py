"""Private fail-closed converter/receipt runner for original FM2001 startup TGQs.

This tool is intentionally separate from the player-visible runtime. It accepts
only exact source TGQs that satisfy original_startup_media.py, writes converted
media outside Git, probes every derivative, and writes one private JSON receipt
only after the whole requested startup sequence validates.

It does not infer the meaning of the original playback flag, skip input, fades,
scaling/interlace treatment, or front-end transition behavior.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Iterable

from original_startup_media import (
    DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    OriginalStartupMediaError,
    OriginalStartupMediaSpec,
    StartupMediaConversionProfile,
    build_startup_media_conversion_plans,
    build_startup_media_ffprobe_args,
    validate_startup_media_probe,
)


class StartupMediaConversionAuditError(RuntimeError):
    """Private conversion could not be proven against the source contract."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_outside_repository(path: Path, repo_root: Path, *, label: str) -> Path:
    """Reject original media, derivatives and receipts placed inside Git."""
    target = Path(path).resolve()
    root = Path(repo_root).resolve()
    if target == root or target.is_relative_to(root):
        raise StartupMediaConversionAuditError(
            f"{label} must remain outside the Git repository"
        )
    return target


def _run_command(command: tuple[str, ...], *, label: str) -> str:
    """Run one external media command and return stdout/stderr text."""
    try:
        result = subprocess.run(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise StartupMediaConversionAuditError(
            f"{label} could not start: {exc}"
        ) from exc
    if result.returncode != 0:
        tail = (result.stdout or "")[-4000:]
        raise StartupMediaConversionAuditError(
            f"{label} failed with exit code {result.returncode}:\n{tail}"
        )
    return result.stdout or ""


def _tool_version(executable: str, *, label: str) -> str:
    output = _run_command((executable, "-version"), label=f"{label} version check")
    first = output.splitlines()[0].strip() if output.splitlines() else ""
    if not first:
        raise StartupMediaConversionAuditError(f"{label} version output was empty")
    return first


def _parse_probe_json(text: str, *, source_path: str) -> dict:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StartupMediaConversionAuditError(
            f"FFprobe returned invalid JSON for {source_path}"
        ) from exc
    if not isinstance(payload, dict):
        raise StartupMediaConversionAuditError(
            f"FFprobe JSON root is not an object for {source_path}"
        )
    return payload


def convert_and_receipt_startup_media(
    *,
    source_root: Path,
    output_root: Path,
    receipt_path: Path,
    repo_root: Path,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> dict:
    """Convert exact originals and create a receipt only after all outputs pass.

    The original source root, converted output directory and receipt all have to
    remain outside the repository. Existing derivative files are rejected before
    any external process runs; the conversion plan itself also uses FFmpeg -n.
    """
    source = require_outside_repository(
        source_root, repo_root, label="Original startup-media source root"
    )
    output = require_outside_repository(
        output_root, repo_root, label="Converted startup-media output root"
    )
    receipt = require_outside_repository(
        receipt_path, repo_root, label="Startup-media conversion receipt"
    )

    if not source.is_dir():
        raise StartupMediaConversionAuditError(
            f"Original startup-media source root is not a directory: {source}"
        )
    if receipt.exists():
        raise StartupMediaConversionAuditError(
            "Refusing to overwrite an existing startup-media conversion receipt"
        )

    ordered_specs = tuple(specs)
    try:
        plans = build_startup_media_conversion_plans(
            source,
            output,
            specs=ordered_specs,
            ffmpeg_executable=ffmpeg_executable,
            profile=profile,
        )
    except (OSError, OriginalStartupMediaError) as exc:
        raise StartupMediaConversionAuditError(
            f"Original startup media failed source validation: {exc}"
        ) from exc

    for plan in plans:
        if plan.output_path.exists():
            raise StartupMediaConversionAuditError(
                f"Refusing to overwrite existing converted media: {plan.output_path}"
            )

    output.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_version = _tool_version(ffmpeg_executable, label="FFmpeg")
    ffprobe_version = _tool_version(ffprobe_executable, label="FFprobe")

    verified_outputs: list[dict] = []
    for sequence, plan in enumerate(plans):
        _run_command(
            plan.ffmpeg_args,
            label=f"FFmpeg conversion for {plan.spec.source_path}",
        )
        if not plan.output_path.is_file():
            raise StartupMediaConversionAuditError(
                f"FFmpeg reported success but output is missing: {plan.output_path}"
            )
        output_size = plan.output_path.stat().st_size
        if output_size <= 0:
            raise StartupMediaConversionAuditError(
                f"Converted startup media is empty: {plan.output_path}"
            )

        probe_args = build_startup_media_ffprobe_args(
            plan.output_path,
            ffprobe_executable=ffprobe_executable,
        )
        probe_payload = _parse_probe_json(
            _run_command(
                probe_args,
                label=f"FFprobe validation for {plan.spec.source_path}",
            ),
            source_path=plan.spec.source_path,
        )
        try:
            verified = validate_startup_media_probe(
                plan.spec,
                probe_payload,
                profile=profile,
            )
        except OriginalStartupMediaError as exc:
            raise StartupMediaConversionAuditError(
                f"Converted startup media failed probe contract "
                f"for {plan.spec.source_path}: {exc}"
            ) from exc

        verified_outputs.append(
            {
                "sequence": sequence,
                "source_path": plan.spec.source_path,
                "source_sha256": plan.spec.source_sha256,
                "source_size_bytes": plan.spec.size_bytes,
                "startup_callsite_va": f"0x{plan.spec.startup_callsite_va:X}",
                "playback_wrapper_va": f"0x{plan.spec.playback_wrapper_va:X}",
                "playback_flag_bit0": plan.spec.playback_flag_bit0,
                "converted_path": str(plan.output_path.resolve()),
                "converted_size_bytes": output_size,
                "converted_sha256": _sha256_file(plan.output_path),
                "container": verified.container_name,
                "video_codec": verified.video_codec,
                "video_width": plan.spec.video_width,
                "video_height": plan.spec.video_height,
                "frame_rate": plan.spec.frame_rate,
                "decoded_video_frames": verified.video_frames,
                "pixel_format": verified.pixel_format,
                "audio_codec": verified.audio_codec,
                "audio_sample_rate": verified.audio_sample_rate,
                "audio_channels": verified.audio_channels,
            }
        )

    result = {
        "schema_version": 1,
        "passed": True,
        "audit_kind": "private_original_startup_media_conversion",
        "ffmpeg_version": ffmpeg_version,
        "ffprobe_version": ffprobe_version,
        "profile": {
            "container": profile.container_name,
            "video_encoder": profile.ffmpeg_video_encoder,
            "video_codec": profile.probe_video_codec,
            "pixel_format": profile.pixel_format,
            "audio_encoder": profile.ffmpeg_audio_encoder,
            "audio_codec": profile.probe_audio_codec,
        },
        "outputs": verified_outputs,
        "fidelity_boundary": (
            "Receipt proves exact original TGQ source identity plus converted "
            "stream/frame/audio geometry only. It does not prove native skip "
            "input, fade/transition timing, scaling/interlace treatment or "
            "player-visible Windows playback."
        ),
        "gate14_complete": False,
    }
    receipt.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()

    result = convert_and_receipt_startup_media(
        source_root=args.source_root,
        output_root=args.output_root,
        receipt_path=args.receipt,
        repo_root=args.repo_root,
        ffmpeg_executable=args.ffmpeg,
        ffprobe_executable=args.ffprobe,
    )
    print(
        "Verified private FM2001 startup-media conversion receipt: "
        f"{Path(args.receipt).resolve()}"
    )
    print(
        json.dumps(
            {
                "passed": result["passed"],
                "outputs": [
                    {
                        "source_path": item["source_path"],
                        "converted_sha256": item["converted_sha256"],
                        "decoded_video_frames": item["decoded_video_frames"],
                    }
                    for item in result["outputs"]
                ],
                "gate14_complete": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
