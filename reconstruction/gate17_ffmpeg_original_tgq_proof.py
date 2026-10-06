"""Bind exact private FM2001 TGQ conversion to the proven minimal FFmpeg helper.

This is an external/private Gate-17 proof producer. It never embeds original
TGQ bytes in Git. It accepts only the exact minimal helper binaries represented
by a successful build proof and successful synthetic-roundtrip proof, then
reuses the canonical private startup-media converter with the Windows Media
Foundation profile.

A successful receipt proves exact-original conversion only. It deliberately
keeps external playback, source-material completeness, production migration
readiness, and legal-compliance claims false.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from gate14_startup_media_convert import (
    StartupMediaConversionAuditError,
    convert_and_receipt_startup_media,
    require_outside_repository,
)
from original_startup_media import (
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE,
)


class MinimalFfmpegOriginalTgqError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_file(path: str | Path, label: str) -> Path:
    target = Path(path).resolve()
    if not target.is_file() or target.stat().st_size <= 0:
        raise MinimalFfmpegOriginalTgqError(f"{label} is missing or empty: {target}")
    return target


def _load_json(path: str | Path, label: str) -> tuple[Path, dict]:
    target = _require_file(path, label)
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MinimalFfmpegOriginalTgqError(f"{label} is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MinimalFfmpegOriginalTgqError(f"{label} root must be an object")
    return target, payload


def validate_prior_proofs(
    *,
    build_proof: Mapping[str, object],
    roundtrip_proof: Mapping[str, object],
    build_proof_sha256: str,
    ffmpeg_sha256: str,
    ffprobe_sha256: str,
) -> dict:
    if (
        build_proof.get("schema_version") != 1
        or build_proof.get("audit_kind") != "gate17_minimal_ffmpeg_build"
        or build_proof.get("passed") is not True
        or build_proof.get("build_verified") is not True
        or build_proof.get("synthetic_roundtrip_verified") is not False
        or build_proof.get("exact_original_tgq_verified") is not False
        or build_proof.get("external_windows11_playback_verified") is not False
        or build_proof.get("source_material_complete") is not False
        or build_proof.get("production_migration_ready") is not False
        or build_proof.get("legal_compliance_claimed") is not False
    ):
        raise MinimalFfmpegOriginalTgqError(
            "minimal build proof is not a valid pre-original receipt"
        )
    if build_proof.get("ffmpeg_sha256") != ffmpeg_sha256:
        raise MinimalFfmpegOriginalTgqError("minimal ffmpeg.exe differs from build proof")
    if build_proof.get("ffprobe_sha256") != ffprobe_sha256:
        raise MinimalFfmpegOriginalTgqError("minimal ffprobe.exe differs from build proof")

    if (
        roundtrip_proof.get("schema_version") != 1
        or roundtrip_proof.get("audit_kind") != "gate17_minimal_ffmpeg_synthetic_roundtrip"
        or roundtrip_proof.get("passed") is not True
        or roundtrip_proof.get("build_verified") is not True
        or roundtrip_proof.get("synthetic_roundtrip_verified") is not True
        or roundtrip_proof.get("exact_original_tgq_verified") is not False
        or roundtrip_proof.get("external_windows11_playback_verified") is not False
        or roundtrip_proof.get("source_material_complete") is not False
        or roundtrip_proof.get("production_migration_ready") is not False
        or roundtrip_proof.get("legal_compliance_claimed") is not False
    ):
        raise MinimalFfmpegOriginalTgqError(
            "synthetic roundtrip proof is not a valid pre-original receipt"
        )
    if roundtrip_proof.get("build_proof_sha256") != build_proof_sha256:
        raise MinimalFfmpegOriginalTgqError(
            "synthetic roundtrip proof is bound to a different build proof"
        )
    if roundtrip_proof.get("build_proof_ffmpeg_sha256") != ffmpeg_sha256:
        raise MinimalFfmpegOriginalTgqError(
            "synthetic roundtrip proof is bound to a different ffmpeg.exe"
        )
    if roundtrip_proof.get("build_proof_ffprobe_sha256") != ffprobe_sha256:
        raise MinimalFfmpegOriginalTgqError(
            "synthetic roundtrip proof is bound to a different ffprobe.exe"
        )
    return {
        "build_proof_ffmpeg_sha256": ffmpeg_sha256,
        "build_proof_ffprobe_sha256": ffprobe_sha256,
        "build_proof_sha256": build_proof_sha256,
    }


def validate_conversion_result(payload: Mapping[str, object]) -> list[dict]:
    profile = payload.get("profile")
    outputs = payload.get("outputs")
    if payload.get("passed") is not True or not isinstance(profile, Mapping):
        raise MinimalFfmpegOriginalTgqError("private conversion receipt did not pass")
    if (
        profile.get("video_encoder") != "h264_mf"
        or profile.get("video_codec") != "h264"
        or profile.get("audio_encoder") != "aac"
        or profile.get("audio_codec") != "aac"
        or profile.get("output_width") != 640
        or profile.get("output_height") != 480
        or profile.get("video_filter") != "scale=640:480:flags=neighbor"
    ):
        raise MinimalFfmpegOriginalTgqError(
            "private conversion profile differs from canonical minimal path"
        )
    if not isinstance(outputs, list) or len(outputs) != len(ORIGINAL_STARTUP_MEDIA_SEQUENCE):
        raise MinimalFfmpegOriginalTgqError(
            "private conversion output sequence is incomplete"
        )

    verified: list[dict] = []
    for spec, item in zip(ORIGINAL_STARTUP_MEDIA_SEQUENCE, outputs, strict=True):
        if not isinstance(item, Mapping):
            raise MinimalFfmpegOriginalTgqError(
                "private conversion output row is invalid"
            )
        if (
            item.get("source_path") != spec.source_path
            or item.get("source_sha256") != spec.source_sha256
            or item.get("source_size_bytes") != spec.size_bytes
            or item.get("video_codec") != "h264"
            or item.get("pixel_format") != "yuv420p"
            or item.get("video_width") != 640
            or item.get("video_height") != 480
            or item.get("frame_rate") != 25
            or item.get("decoded_video_frames") != spec.decoded_video_frames
            or item.get("audio_codec") != "aac"
            or item.get("audio_sample_rate") != 22050
            or item.get("audio_channels") != 2
            or item.get("container") != "mp4"
        ):
            raise MinimalFfmpegOriginalTgqError(
                f"private conversion output differs from exact contract: {spec.source_path}"
            )
        converted_sha = item.get("converted_sha256")
        converted_size = item.get("converted_size_bytes")
        if not isinstance(converted_sha, str) or len(converted_sha) != 64:
            raise MinimalFfmpegOriginalTgqError(
                "converted derivative SHA-256 is invalid"
            )
        if type(converted_size) is not int or converted_size <= 0:
            raise MinimalFfmpegOriginalTgqError(
                "converted derivative size is invalid"
            )
        verified.append(
            {
                "source_path": spec.source_path,
                "source_sha256": spec.source_sha256,
                "source_size_bytes": spec.size_bytes,
                "decoded_video_frames": spec.decoded_video_frames,
                "converted_sha256": converted_sha,
                "converted_size_bytes": converted_size,
            }
        )
    return verified


def audit_exact_original_tgq_conversion(
    *,
    repo_root: str | Path,
    source_root: str | Path,
    output_root: str | Path,
    conversion_receipt: str | Path,
    output_receipt: str | Path,
    ffmpeg_exe: str | Path,
    ffprobe_exe: str | Path,
    build_proof: str | Path,
    roundtrip_proof: str | Path,
) -> dict:
    repo = Path(repo_root).resolve()
    ffmpeg = _require_file(ffmpeg_exe, "minimal ffmpeg.exe")
    ffprobe = _require_file(ffprobe_exe, "minimal ffprobe.exe")
    build_path, build = _load_json(build_proof, "minimal build proof")
    roundtrip_path, roundtrip = _load_json(
        roundtrip_proof, "minimal synthetic roundtrip proof"
    )
    try:
        final_receipt = require_outside_repository(
            Path(output_receipt), repo, label="Gate-17 exact-original receipt"
        )
    except StartupMediaConversionAuditError as exc:
        raise MinimalFfmpegOriginalTgqError(str(exc)) from exc
    if final_receipt.exists():
        raise MinimalFfmpegOriginalTgqError(
            "Refusing to overwrite an existing Gate-17 exact-original receipt"
        )

    identity = validate_prior_proofs(
        build_proof=build,
        roundtrip_proof=roundtrip,
        build_proof_sha256=_sha256_file(build_path),
        ffmpeg_sha256=_sha256_file(ffmpeg),
        ffprobe_sha256=_sha256_file(ffprobe),
    )

    try:
        conversion = convert_and_receipt_startup_media(
            source_root=Path(source_root),
            output_root=Path(output_root),
            receipt_path=Path(conversion_receipt),
            repo_root=repo,
            ffmpeg_executable=str(ffmpeg),
            ffprobe_executable=str(ffprobe),
            profile=WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE,
        )
    except StartupMediaConversionAuditError as exc:
        raise MinimalFfmpegOriginalTgqError(
            f"exact original startup conversion failed: {exc}"
        ) from exc

    conversion_path = _require_file(
        conversion_receipt, "private conversion receipt"
    )
    verified_outputs = validate_conversion_result(conversion)

    result = {
        "schema_version": 1,
        "audit_kind": "gate17_minimal_ffmpeg_exact_original_tgq",
        "passed": True,
        **identity,
        "roundtrip_proof_sha256": _sha256_file(roundtrip_path),
        "conversion_receipt_sha256": _sha256_file(conversion_path),
        "exact_original_outputs": verified_outputs,
        "build_verified": True,
        "synthetic_roundtrip_verified": True,
        "exact_original_tgq_verified": True,
        "external_windows11_playback_verified": False,
        "source_material_complete": False,
        "production_migration_ready": False,
        "legal_compliance_claimed": False,
    }
    final_receipt.parent.mkdir(parents=True, exist_ok=True)
    final_receipt.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--conversion-receipt", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    parser.add_argument("--ffmpeg", type=Path, required=True)
    parser.add_argument("--ffprobe", type=Path, required=True)
    parser.add_argument("--build-proof", type=Path, required=True)
    parser.add_argument("--roundtrip-proof", type=Path, required=True)
    args = parser.parse_args()
    result = audit_exact_original_tgq_conversion(
        repo_root=args.repo_root,
        source_root=args.source_root,
        output_root=args.output_root,
        conversion_receipt=args.conversion_receipt,
        output_receipt=args.output_receipt,
        ffmpeg_exe=args.ffmpeg,
        ffprobe_exe=args.ffprobe,
        build_proof=args.build_proof,
        roundtrip_proof=args.roundtrip_proof,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
