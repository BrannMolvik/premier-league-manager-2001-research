"""Create a fail-closed private receipt for real Windows startup-FMV playback.

This audit reuses the exact runtime components used by normal Windows launch:
source-verified TGQ validation/conversion cache, the built-in Windows MCI
backend, and the source-proven two-item startup playback order.

A passing receipt additionally requires explicit post-playback human
confirmation that both videos were visible and both audio tracks were audible
in the expected order. It does not recover skip input, fades, transition
timing, or exact display/scaling treatment and cannot complete Gate 14.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import platform
import sys
from typing import Callable

from original_startup_media import ORIGINAL_STARTUP_MEDIA_SEQUENCE
from startup_media_playback import (
    StartupMediaPlaybackError,
    play_verified_startup_sequence,
)
from startup_media_runtime_cache import (
    RuntimeStartupMediaError,
    prepare_runtime_startup_media,
)
from startup_media_windows_backend import (
    WindowsMciStartupMediaBackend,
    WindowsStartupMediaBackendError,
)


class Gate14WindowsStartupMediaAuditError(RuntimeError):
    pass


RECEIPT_SCHEMA_VERSION = 1
VISIBLE_AUDIBLE_CONFIRMATION_TOKEN = "YES-BOTH"


def _require_external_windows_11(
    *,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
) -> dict:
    """Require an actual Windows 11 client workstation, never hosted/server CI."""
    system = platform.system() if platform_system is None else platform_system
    release = platform.release() if platform_release is None else platform_release
    version = platform.version() if platform_version is None else platform_version
    actions = (
        str(os.environ.get("GITHUB_ACTIONS", ""))
        if github_actions is None
        else str(github_actions)
    )
    if system != "Windows":
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance audit must run on Windows 11"
        )
    if actions.casefold() == "true":
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance evidence cannot be produced under GitHub Actions"
        )

    if windows_product_type is None:
        try:
            product_type = int(sys.getwindowsversion().product_type)
        except Exception as exc:
            raise Gate14WindowsStartupMediaAuditError(
                "unable to verify Windows workstation product type"
            ) from exc
    else:
        product_type = int(windows_product_type)
    if product_type != 1:
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance requires a Windows client workstation"
        )

    # Windows 11 client builds start at 22000. Keep the parsed build in evidence
    # but do not infer product type from the build number alone.
    try:
        build_text = str(version).split(".")[-1]
        build = int(build_text)
    except (TypeError, ValueError) as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "unable to parse Windows build number"
        ) from exc
    if build < 22000:
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance requires Windows 11 build 22000 or newer"
        )
    return {
        "platform_system": "Windows",
        "platform_release": str(release),
        "platform_version": str(version),
        "windows_build": build,
        "windows_product_type": product_type,
        "windows_11": True,
        "outside_github_actions": True,
    }


def _require_private_receipt(
    path: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> Path:
    root = (
        Path(__file__).resolve().parent.parent
        if repository_root is None
        else Path(repository_root)
    ).resolve()
    target = Path(path).resolve()
    if target.is_relative_to(root):
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance receipt must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsStartupMediaAuditError(
            "Use a new startup-media receipt path; do not overwrite prior evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _human_confirmation(
    confirmer: Callable[[str], str],
) -> bool:
    source_names = ", then ".join(
        Path(spec.source_path).name for spec in ORIGINAL_STARTUP_MEDIA_SEQUENCE
    )
    prompt = (
        "The verified startup sequence has completed: "
        f"{source_names}.\n"
        "If BOTH videos were visibly displayed, BOTH had audible audio, and "
        "they appeared in that order, type "
        f"{VISIBLE_AUDIBLE_CONFIRMATION_TOKEN} exactly and press Enter. "
        "Any other response fails closed: "
    )
    try:
        response = confirmer(prompt)
    except Exception as exc:
        raise Gate14WindowsStartupMediaAuditError(
            f"human startup-media confirmation failed: {type(exc).__name__}: {exc}"
        ) from exc
    return response == VISIBLE_AUDIBLE_CONFIRMATION_TOKEN


def run_windows_startup_media_audit(
    game_dir: str | Path,
    application_root: str | Path,
    *,
    backend=None,
    confirmer: Callable[[str], str] = input,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
    preparer=None,
) -> dict:
    """Replay the exact runtime startup-media components and require human acceptance."""
    windows = _require_external_windows_11(
        platform_system=platform_system,
        platform_release=platform_release,
        platform_version=platform_version,
        github_actions=github_actions,
        windows_product_type=windows_product_type,
    )
    prepare = prepare_runtime_startup_media if preparer is None else preparer
    if not callable(prepare):
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media preparer must be callable"
        )
    try:
        derivatives = tuple(prepare(game_dir, application_root))
    except (RuntimeStartupMediaError, OSError) as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "runtime startup-media preparation failed"
        ) from exc

    player = (
        WindowsMciStartupMediaBackend(platform_system="Windows")
        if backend is None
        else backend
    )
    if type(player) is not WindowsMciStartupMediaBackend:
        raise Gate14WindowsStartupMediaAuditError(
            "real startup-media acceptance requires exact WindowsMciStartupMediaBackend"
        )

    try:
        summary = play_verified_startup_sequence(derivatives, player)
    except (StartupMediaPlaybackError, WindowsStartupMediaBackendError) as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "real Windows startup-media playback failed"
        ) from exc

    expected_count = len(ORIGINAL_STARTUP_MEDIA_SEQUENCE)
    if (
        not summary.source_order_preserved
        or len(summary.steps) != expected_count
        or not all(step.completed for step in summary.steps)
    ):
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media playback summary does not prove the complete source order"
        )

    if not _human_confirmation(confirmer):
        raise Gate14WindowsStartupMediaAuditError(
            "visible and audible Windows startup media were not explicitly confirmed"
        )

    items = []
    for derivative, step in zip(derivatives, summary.steps, strict=True):
        items.append(
            {
                "sequence": derivative.sequence,
                "source_path": derivative.spec.source_path,
                "source_sha256": derivative.spec.source_sha256,
                "source_size_bytes": derivative.spec.size_bytes,
                "decoded_video_frames": derivative.spec.decoded_video_frames,
                "audio_sample_rate": derivative.spec.audio_sample_rate,
                "audio_channels": derivative.spec.audio_channels,
                "playback_flag_bit0": derivative.spec.playback_flag_bit0,
                "converted_filename": Path(derivative.path).name,
                "converted_sha256": derivative.converted_sha256,
                "converted_size_bytes": derivative.converted_size_bytes,
                "container": derivative.container,
                "video_codec": derivative.video_codec,
                "pixel_format": derivative.pixel_format,
                "audio_codec": derivative.audio_codec,
                "playback_completed": step.completed,
            }
        )

    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "audit_kind": "gate14_windows_startup_media_acceptance",
        "passed": True,
        **windows,
        "playback_backend": "WindowsMciStartupMediaBackend",
        "startup_sequence": items,
        "source_order_preserved": True,
        "human_visibility_confirmation": True,
        "human_audibility_confirmation": True,
        "startup_media_real_windows_verified": True,
        "default_runtime_components_replayed": True,
        "normal_application_launch_invoked": False,
        "skip_input_recovered": False,
        "transition_timing_recovered": False,
        "exact_display_treatment_recovered": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This receipt proves the exact runtime startup-media components completed "
            "on a real Windows 11 client workstation and a human confirmed both "
            "videos visible and both audio tracks audible in source order. It does "
            "not prove the full normal application launch wrapper, native skip input, "
            "fade/transition timing, exact display/scaling treatment, or Gate 14."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--application-root", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    output = _require_private_receipt(args.output_receipt)
    receipt = run_windows_startup_media_audit(
        args.game_dir,
        args.application_root,
    )
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: real Windows 11 startup-media visibility/audibility verified; "
        f"private receipt written to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
