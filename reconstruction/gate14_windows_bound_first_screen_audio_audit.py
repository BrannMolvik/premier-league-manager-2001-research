"""Audit the real production first-screen press-audio path on Windows 11.

The audit launches the source-backed host with its ordinary production
first-screen audio wrapper and no synthetic click injection. The operator must
click the real Start Menu "Quit to Windows" control exactly once. After the Tk
mainloop exits, the retained production binding must prove one successful
source-backed press delivery before the original host action, and the operator
must explicitly confirm the sound was heard.

This is narrower than application-wide login/menu audio integration. It does
not add hover audio, music, semantic sample naming, or any new gameplay path.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable

from front_end_state import FrontEndScreen
from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_first_screen_audio_binding import Gate14FirstScreenAudioHostBinding
from gate14_windows_menu_pcm_backend import WindowsMemoryWaveMenuPcmBackend
from gate14_windows_startup_media_audit import _require_external_windows_11
from original_game_host import run_original_game_ui


class Gate14WindowsBoundFirstScreenAudioAuditError(RuntimeError):
    pass


RECEIPT_SCHEMA_VERSION = 1
AUDIBLE_CONFIRMATION_TOKEN = "YES"
EXPECTED_EVENT_ID = 10
EXPECTED_STATE_VALUE = 0
EXPECTED_SAMPLE_SLOT = 2


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
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen audio receipt must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "Use a new bound-audio receipt path; do not overwrite prior evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _confirm_audible(confirmer: Callable[[str], str]) -> bool:
    prompt = (
        "The real source-backed Start Menu has exited through Quit to Windows.\n"
        "If you personally heard the menu click sound immediately before the "
        f"window closed, type {AUDIBLE_CONFIRMATION_TOKEN} exactly and press Enter. "
        "Any other response fails closed: "
    )
    try:
        response = confirmer(prompt)
    except Exception as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            f"human bound-audio confirmation failed: {type(exc).__name__}: {exc}"
        ) from exc
    return response == AUDIBLE_CONFIRMATION_TOKEN


def _validate_bound_result(host, binding) -> dict:
    if type(binding) is not Gate14FirstScreenAudioHostBinding:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production first-screen audio binding was not retained"
        )
    if not binding.installed or not binding.press_binding_integrated:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production first-screen press binding was not installed"
        )
    if binding.hover_binding_integrated:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound audit cannot promote unrecovered hover audio"
        )
    if type(binding.backend) is not WindowsMemoryWaveMenuPcmBackend:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound audit requires the exact production Windows memory-wave backend"
        )
    if binding.audio_attempt_count != 1 or binding.audio_success_count != 1:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "audit requires exactly one successful first-screen audio attempt"
        )
    if binding.last_audio_error is not None:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production binding recorded an audio delivery error"
        )
    summary = binding.last_audio_summary
    if summary is None:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production binding did not retain an audio delivery summary"
        )
    if (
        summary.event_id != EXPECTED_EVENT_ID
        or summary.state_value != EXPECTED_STATE_VALUE
        or summary.sample_slot != EXPECTED_SAMPLE_SLOT
        or not summary.backend_invoked
        or not summary.adapter_delivery_completed
    ):
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production binding summary differs from the source-backed press route"
        )

    if getattr(host, "last_status", None) != "QUIT_TO_WINDOWS":
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "audit requires the real Quit to Windows action to complete"
        )
    try:
        screen = host.presenter.session.navigation.screen
    except AttributeError as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "host no longer exposes the first-screen navigation state"
        ) from exc
    if screen is not FrontEndScreen.START_MENU:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "audit action did not originate from the Start Menu"
        )

    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    bank = binding.menus_bnk
    bank_sha = sha256(bank).hexdigest()
    if len(bank) != profile["size_bytes"] or bank_sha != profile["sha256"]:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "retained production binding no longer owns canonical menus.bnk"
        )

    return {
        "source_bank": {
            "filename": "menus.bnk",
            "size_bytes": len(bank),
            "sha256": bank_sha,
        },
        "numeric_route": {
            "event_id": summary.event_id,
            "state_value": summary.state_value,
            "sample_slot": summary.sample_slot,
        },
        "binding": {
            "class": "Gate14FirstScreenAudioHostBinding",
            "installed": True,
            "press_binding_integrated": True,
            "hover_binding_integrated": False,
            "audio_attempt_count": binding.audio_attempt_count,
            "audio_success_count": binding.audio_success_count,
            "adapter_delivery_completed": True,
        },
        "playback_backend": "WindowsMemoryWaveMenuPcmBackend",
        "host_action": "QUIT_TO_WINDOWS",
        "host_screen": FrontEndScreen.START_MENU.value,
    }


def run_bound_first_screen_audio_audit(
    game_dir: str | Path,
    *,
    source_root: str | Path | None = None,
    confirmer: Callable[[str], str] = input,
    host_runner=None,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
) -> dict:
    """Run the production host and validate one real audible Quit press."""
    try:
        windows = _require_external_windows_11(
            platform_system=platform_system,
            platform_release=platform_release,
            platform_version=platform_version,
            github_actions=github_actions,
            windows_product_type=windows_product_type,
        )
    except Exception as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            f"external Windows 11 requirement failed: {exc}"
        ) from exc

    runner = run_original_game_ui if host_runner is None else host_runner
    if not callable(runner):
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen host runner must be callable"
        )

    captured = []

    def capture(host, binding):
        captured.append((host, binding))

    kwargs = {"first_screen_audio_audit_callback": capture}
    if source_root is not None:
        kwargs["source_root"] = Path(source_root)

    try:
        runner(Path(game_dir), **kwargs)
    except Exception as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            f"source-backed host audit run failed: {type(exc).__name__}: {exc}"
        ) from exc

    if len(captured) != 1:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "source-backed host did not return exactly one post-mainloop audit result"
        )
    host, binding = captured[0]
    bound = _validate_bound_result(host, binding)

    if not _confirm_audible(confirmer):
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound application audio was not explicitly confirmed audible"
        )

    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "audit_kind": "gate14_bound_first_screen_audio_acceptance",
        "passed": True,
        **windows,
        **bound,
        "human_audibility_confirmation": True,
        "audible_windows_verified": True,
        "bounded_first_screen_press_equivalence_verified": True,
        "application_wide_audio_event_binding_recovered": False,
        "hover_audio_integrated": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This receipt proves one real Start Menu Quit press traversed the "
            "production source-backed Button audio wrapper, completed numeric "
            "(10,0)->menus.bnk slot 2 delivery through the exact Windows backend, "
            "delegated to QUIT_TO_WINDOWS, and was explicitly heard by the human "
            "operator. It does not prove hover audio, menu music, application-wide "
            "audio event semantics, full login/menu audio integration, or Gate 14."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    output = _require_private_receipt(args.output_receipt)
    print(
        "AUDIT INSTRUCTION: when the real Start Menu appears, click "
        "'Quit to Windows' exactly once. Do not click another first-screen action."
    )
    receipt = run_bound_first_screen_audio_audit(
        args.game_dir,
        source_root=args.source_root,
    )
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: bound first-screen Windows audio was audibly verified; "
        f"private receipt written to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
