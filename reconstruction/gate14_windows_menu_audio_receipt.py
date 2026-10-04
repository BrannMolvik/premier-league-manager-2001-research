"""Strict validator for private Gate-14 Windows menu-audio receipts.

The real-Windows audit receipt contains one human audibility observation that
cannot be recreated by an offline validator. This module therefore validates
that receipt fail-closed and deterministically replays only the source-backed
portion against the exact canonical menus.bnk bytes:

canonical bank identity -> numeric AudioHooks route -> literal sample slot ->
decoded PCM identity.

A successful validation preserves the prior human audibility evidence, but it
does not create new device-output evidence, semantic event/sample names,
modern UI-event equivalence, login/menu integration, or Gate-14 completion.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Mapping

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_pcm import decode_audiohooks_menu_pcm
from gate14_windows_menu_audio_audit import RECEIPT_SCHEMA_VERSION


class Gate14WindowsMenuAudioReceiptError(RuntimeError):
    pass


_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "passed",
        "platform_system",
        "platform",
        "python_version",
        "source_bank",
        "numeric_route",
        "decoded_pcm",
        "playback_backend",
        "adapter_delivery_completed",
        "human_audibility_confirmation",
        "audible_windows_verified",
        "numeric_routing_recovered",
        "sample_decode_recovered",
        "semantic_event_binding_recovered",
        "sample_meaning_recovered",
        "modern_ui_event_equivalence_recovered",
        "login_menu_audio_integrated",
        "gate14_complete",
        "evidence_limit",
    }
)
_EXPECTED_TRUE_FIELDS = (
    "passed",
    "adapter_delivery_completed",
    "human_audibility_confirmation",
    "audible_windows_verified",
    "numeric_routing_recovered",
    "sample_decode_recovered",
)
_EXPECTED_FALSE_FIELDS = (
    "semantic_event_binding_recovered",
    "sample_meaning_recovered",
    "modern_ui_event_equivalence_recovered",
    "login_menu_audio_integrated",
    "gate14_complete",
)
_WINDOWS_MEMORY_FLAG = 4


def _require_exact_mapping(
    value: object,
    *,
    label: str,
    expected_keys: frozenset[str],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise Gate14WindowsMenuAudioReceiptError(f"{label} must be an object")
    actual = set(value.keys())
    if actual != set(expected_keys):
        missing = sorted(set(expected_keys) - actual)
        unexpected = sorted(actual - set(expected_keys))
        raise Gate14WindowsMenuAudioReceiptError(
            f"{label} schema keys differ; missing={missing}, unexpected={unexpected}"
        )
    return value


def _require_nonempty_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Gate14WindowsMenuAudioReceiptError(
            f"{label} must be a non-empty string"
        )
    return value


def _require_exact_bool(
    receipt: Mapping[str, object],
    field: str,
    expected: bool,
) -> None:
    if type(receipt.get(field)) is not bool or receipt.get(field) is not expected:
        raise Gate14WindowsMenuAudioReceiptError(
            f"{field} must be exactly {str(expected).lower()}"
        )


def _canonical_bank_identity(menus_bnk: bytes) -> dict:
    if not isinstance(menus_bnk, bytes):
        raise Gate14WindowsMenuAudioReceiptError(
            "menus.bnk payload must be bytes"
        )
    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    digest = sha256(menus_bnk).hexdigest()
    if (
        len(menus_bnk) != profile["size_bytes"]
        or digest != profile["sha256"]
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "menus.bnk does not match canonical source identity"
        )
    return {
        "filename": "menus.bnk",
        "size_bytes": len(menus_bnk),
        "sha256": digest,
    }


def _require_private_validation_output(
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
        raise Gate14WindowsMenuAudioReceiptError(
            "Windows menu-audio validation receipts must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsMenuAudioReceiptError(
            "Use a new validation-receipt path; do not overwrite prior evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def validate_windows_menu_audio_receipt(
    receipt: Mapping[str, object],
    menus_bnk: bytes,
) -> dict:
    """Validate one private audible receipt and replay its deterministic route.

    The prior human audibility observation is accepted only if the exact audit
    schema remains intact. Device audio is not replayed here. The numeric route
    and decoded PCM are freshly recomputed from canonical menus.bnk bytes.
    """
    checked = _require_exact_mapping(
        receipt,
        label="Windows menu-audio receipt",
        expected_keys=_EXPECTED_TOP_LEVEL_KEYS,
    )

    if (
        type(checked.get("schema_version")) is not int
        or checked["schema_version"] != RECEIPT_SCHEMA_VERSION
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "unsupported Windows menu-audio receipt schema version"
        )

    for field in _EXPECTED_TRUE_FIELDS:
        _require_exact_bool(checked, field, True)
    for field in _EXPECTED_FALSE_FIELDS:
        _require_exact_bool(checked, field, False)

    if checked.get("platform_system") != "Windows":
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt does not prove Windows platform execution"
        )
    _require_nonempty_string(checked.get("platform"), label="platform")
    _require_nonempty_string(
        checked.get("python_version"),
        label="python_version",
    )
    _require_nonempty_string(
        checked.get("evidence_limit"),
        label="evidence_limit",
    )

    canonical_bank = _canonical_bank_identity(menus_bnk)
    source_bank = _require_exact_mapping(
        checked.get("source_bank"),
        label="source_bank",
        expected_keys=frozenset({"filename", "size_bytes", "sha256"}),
    )
    if dict(source_bank) != canonical_bank:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt source_bank differs from canonical menus.bnk identity"
        )

    numeric_route = _require_exact_mapping(
        checked.get("numeric_route"),
        label="numeric_route",
        expected_keys=frozenset({"event_id", "state_value", "sample_slot"}),
    )
    for field in ("event_id", "state_value", "sample_slot"):
        if type(numeric_route.get(field)) is not int:
            raise Gate14WindowsMenuAudioReceiptError(
                f"numeric_route.{field} must be an exact integer"
            )
    if not 0 <= int(numeric_route["sample_slot"]) <= 22:
        raise Gate14WindowsMenuAudioReceiptError(
            "numeric_route.sample_slot must be 0..22"
        )

    decoded_pcm = _require_exact_mapping(
        checked.get("decoded_pcm"),
        label="decoded_pcm",
        expected_keys=frozenset(
            {"sample_rate", "channels", "sample_count", "sha256"}
        ),
    )
    for field in ("sample_rate", "channels", "sample_count"):
        if type(decoded_pcm.get(field)) is not int or int(decoded_pcm[field]) <= 0:
            raise Gate14WindowsMenuAudioReceiptError(
                f"decoded_pcm.{field} must be a positive integer"
            )
    if (
        not isinstance(decoded_pcm.get("sha256"), str)
        or not _HEX64.fullmatch(str(decoded_pcm["sha256"]))
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "decoded_pcm.sha256 must be lowercase SHA-256 hex"
        )

    playback_backend = _require_exact_mapping(
        checked.get("playback_backend"),
        label="playback_backend",
        expected_keys=frozenset({"class", "memory_flag"}),
    )
    if playback_backend.get("class") != "WindowsMemoryWaveMenuPcmBackend":
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt playback backend class is not canonical"
        )
    if (
        type(playback_backend.get("memory_flag")) is not int
        or playback_backend["memory_flag"] != _WINDOWS_MEMORY_FLAG
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt playback backend does not use winsound SND_MEMORY"
        )

    try:
        replayed = decode_audiohooks_menu_pcm(
            menus_bnk,
            int(numeric_route["event_id"]),
            int(numeric_route["state_value"]),
        )
    except Exception as exc:
        raise Gate14WindowsMenuAudioReceiptError(
            "canonical numeric route could not be replayed"
        ) from exc

    if replayed.sample_slot is None or replayed.pcm_samples is None:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt route replays to silence instead of a menu sample"
        )

    expected_route = {
        "event_id": replayed.event_id,
        "state_value": replayed.state_value,
        "sample_slot": replayed.sample_slot,
    }
    if dict(numeric_route) != expected_route:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt numeric route differs from canonical replay"
        )

    expected_pcm = {
        "sample_rate": replayed.sample_rate,
        "channels": replayed.channels,
        "sample_count": len(replayed.pcm_samples),
        "sha256": replayed.pcm_sha256,
    }
    if dict(decoded_pcm) != expected_pcm:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt decoded PCM differs from canonical replay"
        )

    return {
        "schema_version": 1,
        "passed": True,
        "validated_receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "source_bank_verified": True,
        "deterministic_numeric_route_replay_verified": True,
        "numeric_route": expected_route,
        "decoded_pcm": expected_pcm,
        "prior_human_audibility_receipt_accepted": True,
        "audible_windows_verified": True,
        "new_device_audibility_replayed": False,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "modern_ui_event_equivalence_recovered": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This validation strictly checks the private schema and replays the "
            "numeric route/PCM identity against canonical menus.bnk. It accepts "
            "the prior receipt's human audibility observation but does not "
            "replay or newly prove device output, semantic event/sample meaning, "
            "modern UI-event equivalence, login/menu integration, or Gate 14."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("menus_bnk", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output-validation", type=Path, required=True)
    args = parser.parse_args()

    output = _require_private_validation_output(args.output_validation)
    try:
        bank = args.menus_bnk.read_bytes()
    except OSError as exc:
        raise Gate14WindowsMenuAudioReceiptError(
            f"could not read menus.bnk: {exc}"
        ) from exc
    try:
        raw_receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Gate14WindowsMenuAudioReceiptError(
            "Windows menu-audio receipt is not readable JSON"
        ) from exc

    validation = validate_windows_menu_audio_receipt(raw_receipt, bank)
    output.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: private Windows menu-audio receipt strictly validated and "
        f"numeric route replayed; validation receipt written to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
