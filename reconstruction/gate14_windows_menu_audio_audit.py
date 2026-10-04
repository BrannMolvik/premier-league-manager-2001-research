"""Real-Windows audible audit for one explicit numeric FM2001 menu sound.

This harness is deliberately narrower than Gate-14 login/menu integration. It
requires the exact canonical menus.bnk bytes, an explicit numeric AudioHooks
(event_id, state_value) pair, the real Windows in-memory WAV backend, and an
explicit post-playback human YES confirmation before setting
audible_windows_verified=true.

The receipt remains private outside Git. Semantic event names, sample names,
modern UI-event equivalence, and login/menu integration stay false even when
the sound is audibly confirmed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import platform
from pathlib import Path
import sys
from typing import Callable

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_pcm import decode_audiohooks_menu_pcm
from gate14_audiohooks_menu_playback import play_audiohooks_menu_pcm
from gate14_windows_menu_pcm_backend import WindowsMemoryWaveMenuPcmBackend


class Gate14WindowsMenuAudioAuditError(RuntimeError):
    pass


RECEIPT_SCHEMA_VERSION = 1
AUDIBLE_CONFIRMATION_TOKEN = "YES"


def _require_private_receipt(
    path: Path,
    *,
    repository_root: Path | None = None,
) -> Path:
    root = (
        Path(__file__).resolve().parent.parent
        if repository_root is None
        else Path(repository_root)
    ).resolve()
    target = Path(path).resolve()
    if target.is_relative_to(root):
        raise Gate14WindowsMenuAudioAuditError(
            "Windows menu-audio audit receipts must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsMenuAudioAuditError(
            "Use a new receipt path; do not overwrite prior menu-audio evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _require_windows(platform_system: str | None = None) -> str:
    system = platform.system() if platform_system is None else platform_system
    if system != "Windows":
        raise Gate14WindowsMenuAudioAuditError(
            "Real menu-audio audibility audit must run on Windows"
        )
    return system


def _require_canonical_menus_identity(data: bytes) -> dict:
    if not isinstance(data, bytes):
        raise Gate14WindowsMenuAudioAuditError("menus.bnk payload must be bytes")
    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    digest = sha256(data).hexdigest()
    if len(data) != profile["size_bytes"] or digest != profile["sha256"]:
        raise Gate14WindowsMenuAudioAuditError(
            "menus.bnk does not match canonical source identity"
        )
    return {
        "size_bytes": len(data),
        "sha256": digest,
    }


def _explicit_human_audibility_confirmation(
    confirmer: Callable[[str], str],
    *,
    event_id: int,
    state_value: int,
    sample_slot: int,
) -> bool:
    if not callable(confirmer):
        raise Gate14WindowsMenuAudioAuditError(
            "audibility confirmer must be callable"
        )
    prompt = (
        "\nThe exact numeric FM2001 menu sample has just been played.\n"
        f"event_id={event_id}, state_value={state_value}, sample_slot={sample_slot}.\n"
        "If you personally heard an audible sound from the Windows audio device, "
        f"type {AUDIBLE_CONFIRMATION_TOKEN} exactly and press Enter. "
        "Any other response fails closed: "
    )
    try:
        response = confirmer(prompt)
    except Exception as exc:
        raise Gate14WindowsMenuAudioAuditError(
            "human audibility confirmation failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    return response == AUDIBLE_CONFIRMATION_TOKEN


def run_windows_menu_audio_audit(
    menus_bnk: bytes,
    *,
    event_id: int,
    state_value: int,
    backend=None,
    confirmer: Callable[[str], str] = input,
    platform_system: str | None = None,
    platform_text: str | None = None,
    python_version: str | None = None,
) -> dict:
    """Play one explicit numeric route and require post-playback human audibility.

    A passing receipt proves only:
      * exact canonical menus.bnk identity;
      * source-backed numeric route and sample decode;
      * synchronous Windows adapter completion;
      * a human explicitly confirmed audible output.

    It does not recover semantic event/sample names or runtime UI integration.
    """
    _require_windows(platform_system)
    source = _require_canonical_menus_identity(menus_bnk)

    try:
        decoded = decode_audiohooks_menu_pcm(
            menus_bnk,
            event_id,
            state_value,
        )
    except Exception as exc:
        raise Gate14WindowsMenuAudioAuditError(
            "canonical numeric menu route could not be decoded"
        ) from exc

    if decoded.sample_slot is None:
        raise Gate14WindowsMenuAudioAuditError(
            "audibility audit requires a numeric route that calls a real menus.bnk sample"
        )

    real_backend = (
        WindowsMemoryWaveMenuPcmBackend()
        if backend is None
        else backend
    )
    if type(real_backend) is not WindowsMemoryWaveMenuPcmBackend:
        raise Gate14WindowsMenuAudioAuditError(
            "real audibility audit requires exact WindowsMemoryWaveMenuPcmBackend"
        )
    try:
        delivery = play_audiohooks_menu_pcm(
            menus_bnk,
            event_id,
            state_value,
            real_backend,
        )
    except Exception as exc:
        raise Gate14WindowsMenuAudioAuditError(
            "real Windows menu PCM adapter delivery failed"
        ) from exc

    if (
        not delivery.backend_invoked
        or not delivery.adapter_delivery_completed
        or delivery.sample_slot != decoded.sample_slot
    ):
        raise Gate14WindowsMenuAudioAuditError(
            "menu PCM delivery summary differs from decoded numeric route"
        )

    audible = _explicit_human_audibility_confirmation(
        confirmer,
        event_id=event_id,
        state_value=state_value,
        sample_slot=decoded.sample_slot,
    )
    if not audible:
        raise Gate14WindowsMenuAudioAuditError(
            "audible Windows output was not explicitly confirmed"
        )

    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "passed": True,
        "platform_system": "Windows",
        "platform": platform.platform() if platform_text is None else platform_text,
        "python_version": (
            platform.python_version()
            if python_version is None
            else python_version
        ),
        "source_bank": {
            "filename": "menus.bnk",
            **source,
        },
        "numeric_route": {
            "event_id": decoded.event_id,
            "state_value": decoded.state_value,
            "sample_slot": decoded.sample_slot,
        },
        "decoded_pcm": {
            "sample_rate": decoded.sample_rate,
            "channels": decoded.channels,
            "sample_count": len(decoded.pcm_samples or ()),
            "sha256": decoded.pcm_sha256,
        },
        "playback_backend": {
            "class": "WindowsMemoryWaveMenuPcmBackend",
            "memory_flag": real_backend.memory_flag,
        },
        "adapter_delivery_completed": True,
        "human_audibility_confirmation": True,
        "audible_windows_verified": True,
        "numeric_routing_recovered": True,
        "sample_decode_recovered": True,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "modern_ui_event_equivalence_recovered": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This receipt proves one exact numeric canonical menus.bnk route "
            "decoded and completed through the real Windows adapter, followed "
            "by explicit human audibility confirmation. It does not prove a "
            "human-readable event/sample meaning, reconstructed UI-event "
            "equivalence, general login/menu integration, or Gate-14 completion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("menus_bnk", type=Path)
    parser.add_argument("--event-id", type=int, required=True)
    parser.add_argument("--state-value", type=int, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    _require_windows()
    output = _require_private_receipt(args.output_receipt)
    try:
        data = args.menus_bnk.read_bytes()
    except OSError as exc:
        raise Gate14WindowsMenuAudioAuditError(
            f"could not read menus.bnk: {exc}"
        ) from exc

    receipt = run_windows_menu_audio_audit(
        data,
        event_id=args.event_id,
        state_value=args.state_value,
    )
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: real Windows numeric menu-audio audibility verified; "
        f"private receipt written to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
