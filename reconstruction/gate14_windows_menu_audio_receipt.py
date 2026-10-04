"""Strict replay validator for private Gate-14 Windows menu-audio receipts.

A receipt that says "audible" is not accepted on flags alone. Validation also
requires the exact canonical menus.bnk bytes and deterministically replays the
numeric AudioHooks route plus sample decode. Only after source identity, routed
slot, decoded format and decoded PCM SHA-256 all match the receipt is its
human-audibility evidence exposed.

This still does not recover semantic event/sample names, modern UI-event
equivalence, or login/menu integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_pcm import decode_audiohooks_menu_pcm
from gate14_windows_menu_audio_audit import RECEIPT_SCHEMA_VERSION


class Gate14WindowsMenuAudioReceiptError(ValueError):
    pass


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class VerifiedWindowsMenuAudioReceipt:
    event_id: int
    state_value: int
    sample_slot: int
    sample_rate: int
    channels: int
    sample_count: int
    pcm_sha256: str
    platform: str
    python_version: str
    source_identity_replayed: bool = True
    numeric_route_replayed: bool = True
    pcm_identity_replayed: bool = True
    adapter_delivery_completed: bool = True
    human_audibility_confirmation: bool = True
    audible_windows_verified: bool = True
    semantic_event_binding_recovered: bool = False
    sample_meaning_recovered: bool = False
    modern_ui_event_equivalence_recovered: bool = False
    login_menu_audio_integrated: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.event_id) is not int or type(self.state_value) is not int:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt event/state values must be integers"
            )
        if type(self.sample_slot) is not int or not 0 <= self.sample_slot <= 22:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt sample slot must be 0..22"
            )
        if type(self.sample_rate) is not int or self.sample_rate <= 0:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt sample rate must be positive"
            )
        if type(self.channels) is not int or self.channels <= 0:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt channels must be positive"
            )
        if type(self.sample_count) is not int or self.sample_count <= 0:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt sample count must be positive"
            )
        if not isinstance(self.pcm_sha256, str) or _SHA256_RE.fullmatch(
            self.pcm_sha256
        ) is None:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt PCM SHA-256 must be lowercase hex"
            )
        if not isinstance(self.platform, str) or not self.platform:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt platform must be non-empty"
            )
        if not isinstance(self.python_version, str) or not self.python_version:
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt Python version must be non-empty"
            )
        if not (
            self.source_identity_replayed
            and self.numeric_route_replayed
            and self.pcm_identity_replayed
            and self.adapter_delivery_completed
            and self.human_audibility_confirmation
            and self.audible_windows_verified
        ):
            raise Gate14WindowsMenuAudioReceiptError(
                "verified receipt cannot weaken replayed audible evidence"
            )
        if (
            self.semantic_event_binding_recovered
            or self.sample_meaning_recovered
            or self.modern_ui_event_equivalence_recovered
            or self.login_menu_audio_integrated
            or self.gate14_complete
        ):
            raise Gate14WindowsMenuAudioReceiptError(
                "audible receipt replay cannot promote semantic or Gate-14 completion claims"
            )


def _require_bool(receipt: dict, name: str, expected: bool) -> None:
    value = receipt.get(name)
    if type(value) is not bool or value is not expected:
        raise Gate14WindowsMenuAudioReceiptError(
            f"receipt field {name} must be exactly {expected}"
        )


def _require_canonical_bank_bytes(menus_bnk: bytes) -> tuple[int, str]:
    if not isinstance(menus_bnk, bytes):
        raise Gate14WindowsMenuAudioReceiptError(
            "canonical menus.bnk replay input must be bytes"
        )
    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    digest = sha256(menus_bnk).hexdigest()
    if (
        len(menus_bnk) != profile["size_bytes"]
        or digest != profile["sha256"]
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "replay menus.bnk does not match canonical source identity"
        )
    return len(menus_bnk), digest


def validate_windows_menu_audio_receipt(
    receipt: dict,
    menus_bnk: bytes,
) -> VerifiedWindowsMenuAudioReceipt:
    """Require a schema-1 passing receipt and replay all source-derived fields."""
    if type(receipt) is not dict:
        raise Gate14WindowsMenuAudioReceiptError(
            "Windows menu-audio receipt must be a JSON object"
        )
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise Gate14WindowsMenuAudioReceiptError(
            "unsupported Windows menu-audio receipt schema"
        )

    for name in (
        "passed",
        "adapter_delivery_completed",
        "human_audibility_confirmation",
        "audible_windows_verified",
        "numeric_routing_recovered",
        "sample_decode_recovered",
    ):
        _require_bool(receipt, name, True)
    for name in (
        "semantic_event_binding_recovered",
        "sample_meaning_recovered",
        "modern_ui_event_equivalence_recovered",
        "login_menu_audio_integrated",
        "gate14_complete",
    ):
        _require_bool(receipt, name, False)

    if receipt.get("platform_system") != "Windows":
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt platform_system must be exactly Windows"
        )
    platform_text = receipt.get("platform")
    python_version = receipt.get("python_version")
    if not isinstance(platform_text, str) or not platform_text:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt platform must be non-empty"
        )
    if not isinstance(python_version, str) or not python_version:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt python_version must be non-empty"
        )

    bank_size, bank_sha = _require_canonical_bank_bytes(menus_bnk)
    bank = receipt.get("source_bank")
    if type(bank) is not dict:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt source_bank must be an object"
        )
    if (
        bank.get("filename") != "menus.bnk"
        or bank.get("size_bytes") != bank_size
        or bank.get("sha256") != bank_sha
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt source_bank does not match replayed canonical menus.bnk"
        )

    route = receipt.get("numeric_route")
    if type(route) is not dict:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt numeric_route must be an object"
        )
    event_id = route.get("event_id")
    state_value = route.get("state_value")
    sample_slot = route.get("sample_slot")
    if type(event_id) is not int or type(state_value) is not int:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt numeric route event/state must be integers"
        )
    if type(sample_slot) is not int:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt numeric route must identify a real sample slot"
        )

    try:
        decoded = decode_audiohooks_menu_pcm(
            menus_bnk,
            event_id,
            state_value,
        )
    except Exception as exc:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt numeric route could not be replayed"
        ) from exc
    if decoded.sample_slot is None:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt route replays to an original no-sound path"
        )
    if decoded.sample_slot != sample_slot:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt sample slot differs from replayed numeric route"
        )

    pcm = receipt.get("decoded_pcm")
    if type(pcm) is not dict:
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt decoded_pcm must be an object"
        )
    replay_count = len(decoded.pcm_samples or ())
    if (
        pcm.get("sample_rate") != decoded.sample_rate
        or pcm.get("channels") != decoded.channels
        or pcm.get("sample_count") != replay_count
        or pcm.get("sha256") != decoded.pcm_sha256
    ):
        raise Gate14WindowsMenuAudioReceiptError(
            "receipt decoded PCM identity differs from canonical replay"
        )

    return VerifiedWindowsMenuAudioReceipt(
        event_id=event_id,
        state_value=state_value,
        sample_slot=sample_slot,
        sample_rate=int(decoded.sample_rate),
        channels=int(decoded.channels),
        sample_count=replay_count,
        pcm_sha256=str(decoded.pcm_sha256),
        platform=platform_text,
        python_version=python_version,
    )


def load_and_validate_windows_menu_audio_receipt(
    receipt_path: str | Path,
    menus_bnk: bytes,
) -> VerifiedWindowsMenuAudioReceipt:
    path = Path(receipt_path)
    try:
        raw = path.read_text(encoding="utf-8")
        receipt = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise Gate14WindowsMenuAudioReceiptError(
            f"could not read valid Windows menu-audio receipt: {exc}"
        ) from exc
    return validate_windows_menu_audio_receipt(receipt, menus_bnk)
