"""Fail-closed real-Windows acceptance for bound first-screen menu audio.

This audit exercises the already-integrated production OriginalGameTkHost path:
run_original_game_ui() installs the canonical first-screen audio binding, the
real Tk canvas receives one source-backed Start New Game <Button-1> event, and
the existing synchronous Windows memory-WAV backend delivers the recovered
numeric AudioHooks (10, 0) -> menus.bnk slot 2 route.

A passing receipt additionally requires explicit human confirmation that the
sound was heard. It does not recover sample meaning, broader semantic AudioHooks
senders, hover audio, full login/menu audio integration, or Gate 14 completion.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
from typing import Callable

from front_end_state import FrontEndScreen
from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_playback import MenuPcmPlaybackSummary
from gate14_first_screen_audio_binding import Gate14FirstScreenAudioHostBinding
from gate14_first_screen_button_audio import (
    BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID,
    BUTTON_PRESS_MENU_SAMPLE_SLOT,
    BUTTON_PRESS_STATE_VALUE,
)
from gate14_windows_menu_pcm_backend import WindowsMemoryWaveMenuPcmBackend
from original_front_end_layout import PSTARTMENU_ACTIONS
from original_game_host import run_original_game_ui


class Gate14WindowsBoundFirstScreenAudioAuditError(RuntimeError):
    pass


RECEIPT_SCHEMA_VERSION = 1
AUDIBLE_CONFIRMATION_TOKEN = "YES-HEARD"
START_NEW_GAME_EVENT = 2


def _require_external_windows_11(
    *,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
) -> dict:
    system = platform.system() if platform_system is None else platform_system
    release = platform.release() if platform_release is None else platform_release
    version = platform.version() if platform_version is None else platform_version
    actions = (
        str(os.environ.get("GITHUB_ACTIONS", ""))
        if github_actions is None
        else str(github_actions)
    )
    if system != "Windows":
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen audio acceptance must run on Windows 11"
        )
    if actions.casefold() == "true":
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen audio acceptance cannot run under GitHub Actions"
        )
    if windows_product_type is None:
        try:
            product_type = int(sys.getwindowsversion().product_type)
        except Exception as exc:
            raise Gate14WindowsBoundFirstScreenAudioAuditError(
                "unable to verify Windows workstation product type"
            ) from exc
    else:
        product_type = int(windows_product_type)
    if product_type != 1:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen audio acceptance requires a Windows client workstation"
        )
    try:
        build = int(str(version).split(".")[-1])
    except (TypeError, ValueError) as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "unable to parse Windows build number"
        ) from exc
    if build < 22000:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen audio acceptance requires Windows 11 build 22000 or newer"
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
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen audio receipt must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "Use a new bound-audio receipt path; do not overwrite prior evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _human_confirmation(confirmer: Callable[[str], str]) -> bool:
    prompt = (
        "The production FM2001 first-screen Start New Game press completed its "
        "verified menu-audio delivery. If you personally heard the sound, type "
        f"{AUDIBLE_CONFIRMATION_TOKEN} exactly and press Enter. "
        "Any other response fails closed: "
    )
    try:
        response = confirmer(prompt)
    except Exception as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            f"human bound-audio confirmation failed: {type(exc).__name__}: {exc}"
        ) from exc
    return response == AUDIBLE_CONFIRMATION_TOKEN


def _start_new_game_action():
    matches = tuple(item for item in PSTARTMENU_ACTIONS if item.event == START_NEW_GAME_EVENT)
    if len(matches) != 1:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "canonical Start New Game action is not uniquely defined"
        )
    return matches[0]


def _validated_binding_record(
    binding: Gate14FirstScreenAudioHostBinding,
) -> dict:
    if type(binding) is not Gate14FirstScreenAudioHostBinding:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production host did not expose the exact first-screen audio binding"
        )
    if not binding.installed:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "first-screen audio binding was not installed on the production host"
        )
    if not binding.press_binding_integrated or binding.hover_binding_integrated:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "acceptance covers only the source-backed fixed-frame press binding"
        )
    if binding.audible_windows_verified or binding.login_menu_audio_integrated:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "runtime binding must not self-promote audibility or broad integration"
        )
    if type(binding.backend) is not WindowsMemoryWaveMenuPcmBackend:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound acceptance requires exact WindowsMemoryWaveMenuPcmBackend"
        )

    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    bank_sha256 = sha256(binding.menus_bnk).hexdigest()
    if (
        len(binding.menus_bnk) != profile["size_bytes"]
        or bank_sha256 != profile["sha256"]
    ):
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound production host did not retain canonical menus.bnk bytes"
        )

    if binding.audio_attempt_count != 1 or binding.audio_success_count != 1:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "real Tk press did not produce exactly one successful audio attempt"
        )
    if binding.last_audio_error is not None:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound production audio path recorded a playback error"
        )
    summary = binding.last_audio_summary
    if type(summary) is not MenuPcmPlaybackSummary:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound production audio path did not retain exact playback summary"
        )
    if (
        summary.event_id != BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID
        or summary.state_value != BUTTON_PRESS_STATE_VALUE
        or summary.sample_slot != BUTTON_PRESS_MENU_SAMPLE_SLOT
        or not summary.backend_invoked
        or not summary.adapter_delivery_completed
    ):
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "bound first-screen press drifted from source-backed (10,0)->slot-2 delivery"
        )
    if (
        summary.semantic_event_binding_recovered
        or summary.sample_meaning_recovered
        or summary.audible_windows_verified
        or summary.login_menu_audio_integrated
    ):
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "adapter summary illegally promoted semantic or audibility claims"
        )

    return {
        "binding_class": type(binding).__name__,
        "binding_installed": True,
        "audio_attempt_count": 1,
        "audio_success_count": 1,
        "menus_bank_size_bytes": len(binding.menus_bnk),
        "menus_bank_sha256": bank_sha256,
        "backend_class": type(binding.backend).__name__,
        "backend_memory_flag": binding.backend.memory_flag,
        "numeric_event_id": summary.event_id,
        "state_value": summary.state_value,
        "sample_slot": summary.sample_slot,
        "backend_invoked": True,
        "adapter_delivery_completed": True,
    }


def run_windows_bound_first_screen_audio_audit(
    game_dir: str | Path,
    *,
    source_root: str | Path | None = None,
    confirmer: Callable[[str], str] = input,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
) -> dict:
    """Drive one real production-host Tk press and require human audibility."""

    windows = _require_external_windows_11(
        platform_system=platform_system,
        platform_release=platform_release,
        platform_version=platform_version,
        github_actions=github_actions,
        windows_product_type=windows_product_type,
    )
    result: dict[str, object] = {}
    action = _start_new_game_action()

    def host_ready(host, binding) -> None:
        try:
            root = host.root
            canvas = host.canvas
        except AttributeError as exc:
            raise Gate14WindowsBoundFirstScreenAudioAuditError(
                "production host must expose root and canvas"
            ) from exc
        if not callable(getattr(root, "after", None)):
            raise Gate14WindowsBoundFirstScreenAudioAuditError(
                "production Tk root must expose after()"
            )
        if not callable(getattr(canvas, "event_generate", None)):
            raise Gate14WindowsBoundFirstScreenAudioAuditError(
                "production Tk canvas must expose event_generate()"
            )

        def probe() -> None:
            try:
                before = host.presenter.session.navigation.screen
                if before is not FrontEndScreen.START_MENU:
                    raise Gate14WindowsBoundFirstScreenAudioAuditError(
                        "bound-audio audit must begin on START_MENU"
                    )
                x = action.rect.x + action.rect.width // 2
                y = action.rect.y + action.rect.height // 2
                canvas.event_generate("<Button-1>", x=x, y=y)
                after = host.presenter.session.navigation.screen
                if after is not FrontEndScreen.TEAM_SELECT:
                    raise Gate14WindowsBoundFirstScreenAudioAuditError(
                        "real Tk Start New Game press did not delegate to TEAM_SELECT"
                    )
                binding_record = _validated_binding_record(binding)
                if not _human_confirmation(confirmer):
                    raise Gate14WindowsBoundFirstScreenAudioAuditError(
                        "bound first-screen menu sound was not explicitly confirmed audible"
                    )
                result["receipt"] = {
                    "schema_version": RECEIPT_SCHEMA_VERSION,
                    "audit_kind": "gate14_windows_bound_first_screen_audio_acceptance",
                    "passed": True,
                    **windows,
                    "production_host_runner": "run_original_game_ui",
                    "normal_application_host_path_invoked": True,
                    "normal_app_cli_invoked": False,
                    "startup_media_in_this_receipt": False,
                    "source_screen_before": before.name,
                    "source_screen_after": after.name,
                    "source_action_event": action.event,
                    "source_action_rect": [
                        action.rect.x,
                        action.rect.y,
                        action.rect.width,
                        action.rect.height,
                    ],
                    **binding_record,
                    "human_audibility_confirmation": True,
                    "bound_application_press_audio_verified": True,
                    "audible_windows_verified": True,
                    "first_screen_press_binding_source_recovered": True,
                    "broad_audio_event_binding_recovered": False,
                    "sample_meaning_recovered": False,
                    "hover_audio_integrated": False,
                    "login_menu_audio_integrated": False,
                    "gate14_complete": False,
                    "evidence_limit": (
                        "This receipt proves one source-backed Start New Game Tk press "
                        "through the production host delivered canonical numeric "
                        "AudioHooks (10,0) to menus.bnk slot 2 through the exact "
                        "Windows memory-wave backend and a human heard it. It does "
                        "not recover broader AudioHooks sender semantics, sample "
                        "meaning, hover audio, full login/menu audio integration, "
                        "startup media, match-presentation completeness, or Gate 14."
                    ),
                }
            except Exception as exc:
                result["error"] = exc
            finally:
                try:
                    root.destroy()
                except Exception:
                    pass

        root.after(0, probe)

    try:
        run_original_game_ui(
            game_dir,
            source_root=source_root,
            host_ready_callback=host_ready,
        )
    except Gate14WindowsBoundFirstScreenAudioAuditError:
        raise
    except Exception as exc:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            f"production host bound-audio audit failed: {type(exc).__name__}: {exc}"
        ) from exc

    if "error" in result:
        error = result["error"]
        if isinstance(error, Gate14WindowsBoundFirstScreenAudioAuditError):
            raise error
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            f"bound first-screen audio probe failed: {type(error).__name__}: {error}"
        ) from error
    receipt = result.get("receipt")
    if type(receipt) is not dict:
        raise Gate14WindowsBoundFirstScreenAudioAuditError(
            "production host exited without a bound first-screen audio receipt"
        )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    output = _require_private_receipt(args.output_receipt)
    receipt = run_windows_bound_first_screen_audio_audit(
        args.game_dir,
        source_root=args.source_root,
    )
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: production-host first-screen press audio was heard on Windows 11; "
        f"private receipt written to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
