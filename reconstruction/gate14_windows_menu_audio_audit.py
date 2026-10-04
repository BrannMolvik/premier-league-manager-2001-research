"""Real-Windows audible audit for the source-backed numeric FM2001 menu-audio path.

This harness is deliberately separate from hosted/synthetic audio tests. It
requires a real Windows 11 client workstation, the exact canonical menus.bnk,
an explicit numeric AudioHooks event/state pair, the synchronous playback seam,
and the real Windows in-memory WAV backend.

A passing receipt additionally requires same-run human confirmation that the
sample was audible. The receipt does not recover event/sample semantics and does
not claim login/menu integration into the reconstructed UI.
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
from gate14_audiohooks_menu_pcm import (
    Gate14AudioHooksMenuPcmError,
    decode_audiohooks_menu_pcm,
)
from gate14_audiohooks_menu_playback import (
    Gate14MenuPcmPlaybackError,
    play_audiohooks_menu_pcm,
)
from gate14_windows_menu_pcm_backend import (
    Gate14WindowsMenuPcmBackendError,
    WindowsMemoryWaveMenuPcmBackend,
)
from gate17_release_readiness import (
    ReleaseReadinessError,
    require_external_windows_11_workstation,
)


class Gate14WindowsMenuAudioAuditError(RuntimeError):
    pass


AUDIT_KIND = "gate14_windows_numeric_menu_audio"
CONFIRMATION_TOKEN = "YES"


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
            "Windows menu-audio audit receipt must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsMenuAudioAuditError(
            "use a new receipt path; do not overwrite prior audio evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _load_canonical_menus_bank(path: str | Path) -> tuple[bytes, dict]:
    source = Path(path).resolve()
    if not source.is_file():
        raise Gate14WindowsMenuAudioAuditError(
            f"menus.bnk does not exist: {source}"
        )
    data = source.read_bytes()
    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    digest = sha256(data).hexdigest()
    if (
        len(data) != profile["size_bytes"]
        or digest != profile["sha256"]
    ):
        raise Gate14WindowsMenuAudioAuditError(
            "menus.bnk does not match the canonical source identity"
        )
    return data, {
        "source_filename": "menus.bnk",
        "source_size_bytes": len(data),
        "source_sha256": digest,
    }


def _require_human_audibility_confirmation(
    reader: Callable[[str], str],
) -> str:
    if not callable(reader):
        raise Gate14WindowsMenuAudioAuditError(
            "audibility confirmation reader must be callable"
        )
    response = reader(
        "If the FM2001 sample was clearly audible from this Windows workstation, "
        f"type {CONFIRMATION_TOKEN} exactly and press Enter: "
    )
    if response != CONFIRMATION_TOKEN:
        raise Gate14WindowsMenuAudioAuditError(
            "human audibility confirmation was not provided; no passing receipt "
            "may be written"
        )
    return response


def run_windows_menu_audio_audit(
    *,
    menus_bnk_path: str | Path,
    event_id: int,
    state_value: int,
    receipt_path: str | Path,
    repository_root: str | Path | None = None,
    backend=None,
    confirmation_reader: Callable[[str], str] = input,
    windows_probe: Callable[[], dict] = require_external_windows_11_workstation,
) -> dict:
    """Run one real-Windows numeric menu-audio audit and write one new receipt."""
    if type(event_id) is not int or type(state_value) is not int:
        raise Gate14WindowsMenuAudioAuditError(
            "event_id and state_value must be integers"
        )
    target = _require_private_receipt(
        Path(receipt_path),
        repository_root=(
            None if repository_root is None else Path(repository_root)
        ),
    )

    try:
        windows = windows_probe()
    except ReleaseReadinessError as exc:
        raise Gate14WindowsMenuAudioAuditError(
            "real external Windows 11 workstation requirement failed"
        ) from exc
    if not isinstance(windows, dict) or windows.get("windows_11") is not True:
        raise Gate14WindowsMenuAudioAuditError(
            "Windows probe did not return verified Windows 11 evidence"
        )

    data, source_identity = _load_canonical_menus_bank(menus_bnk_path)

    try:
        decoded = decode_audiohooks_menu_pcm(data, event_id, state_value)
    except Gate14AudioHooksMenuPcmError as exc:
        raise Gate14WindowsMenuAudioAuditError(
            "canonical numeric menu-audio decode failed"
        ) from exc
    if decoded.sample_slot is None:
        raise Gate14WindowsMenuAudioAuditError(
            "audible Windows audit requires an explicitly non-silent numeric route"
        )

    if backend is None:
        try:
            backend = WindowsMemoryWaveMenuPcmBackend()
        except Gate14WindowsMenuPcmBackendError as exc:
            raise Gate14WindowsMenuAudioAuditError(
                "Windows menu-audio backend could not initialize"
            ) from exc

    try:
        playback = play_audiohooks_menu_pcm(
            data,
            event_id,
            state_value,
            backend,
        )
    except Gate14MenuPcmPlaybackError as exc:
        raise Gate14WindowsMenuAudioAuditError(
            "Windows numeric menu-audio playback failed"
        ) from exc

    if (
        not playback.backend_invoked
        or not playback.adapter_delivery_completed
        or playback.sample_slot != decoded.sample_slot
    ):
        raise Gate14WindowsMenuAudioAuditError(
            "Windows playback seam did not complete the exact decoded sample route"
        )

    _require_human_audibility_confirmation(confirmation_reader)

    receipt = {
        "schema_version": 1,
        "passed": True,
        "audit_kind": AUDIT_KIND,
        **windows,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        **source_identity,
        "event_id": event_id,
        "state_value": state_value,
        "sample_slot": decoded.sample_slot,
        "sample_rate": decoded.sample_rate,
        "channels": decoded.channels,
        "pcm_sample_count": len(decoded.pcm_samples or ()),
        "pcm_sha256": decoded.pcm_sha256,
        "backend_class": type(backend).__name__,
        "backend_invoked": True,
        "adapter_delivery_completed": True,
        "human_audibility_confirmation": True,
        "audible_windows_verified": True,
        "numeric_routing_recovered": True,
        "sample_decode_recovered": True,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "reconstructed_ui_event_equivalence_recovered": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
    }
    target.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--menus-bnk", type=Path, required=True)
    parser.add_argument("--event-id", type=int, required=True)
    parser.add_argument("--state-value", type=int, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    receipt = run_windows_menu_audio_audit(
        menus_bnk_path=args.menus_bnk,
        event_id=args.event_id,
        state_value=args.state_value,
        receipt_path=args.receipt,
    )
    print(
        "Windows menu-audio audible audit passed for numeric route "
        f"event={receipt['event_id']} state={receipt['state_value']} "
        f"slot={receipt['sample_slot']}."
    )
    print(
        "Semantic event/sample meaning and reconstructed UI-event equivalence "
        "remain unresolved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
