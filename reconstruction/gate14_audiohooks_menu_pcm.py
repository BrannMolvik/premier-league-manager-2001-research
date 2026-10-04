"""Fail-closed numeric AudioHooks -> canonical menus.bnk PCM bridge.

This module composes two independently source-backed Gate-14 facts:

* AudioHooks::0x5DBFC0 numeric event/state routing to literal menus.bnk slots;
* exact canonical FM2001 BNKl v2 parsing and modern sample decode.

It deliberately does not assign human-readable event/sample meanings and does
not claim that PCM has been sent to or heard through a Windows audio device.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_audio_bank_format import (
    CANONICAL_FM2001_BANK_PROFILES,
    Gate14BnkFormatError,
    decode_fm2001_bnk_sample,
    parse_fm2001_bnk,
    pcm16le_bytes,
)
from gate14_audiohooks_menu_dispatch import menus_sample_for_audiohooks_event


class Gate14AudioHooksMenuPcmError(ValueError):
    pass


@dataclass(frozen=True)
class DecodedMenuPcmDispatch:
    event_id: int
    state_value: int
    sample_slot: int | None
    sample_rate: int | None
    channels: int | None
    pcm_samples: tuple[int, ...] | None
    pcm_sha256: str | None
    source_identity_verified: bool = True
    numeric_routing_recovered: bool = True
    sample_decode_recovered: bool = True
    semantic_event_binding_recovered: bool = False
    sample_meaning_recovered: bool = False
    host_audio_output_verified: bool = False

    def __post_init__(self) -> None:
        if type(self.event_id) is not int or type(self.state_value) is not int:
            raise Gate14AudioHooksMenuPcmError("event/state values must be integers")
        if not (
            self.source_identity_verified
            and self.numeric_routing_recovered
            and self.sample_decode_recovered
        ):
            raise Gate14AudioHooksMenuPcmError(
                "decoded menu PCM result cannot weaken verified source/routing/decode"
            )
        if (
            self.semantic_event_binding_recovered
            or self.sample_meaning_recovered
            or self.host_audio_output_verified
        ):
            raise Gate14AudioHooksMenuPcmError(
                "decoded menu PCM bridge cannot promote semantic or audible-host claims"
            )

        if self.sample_slot is None:
            if any(
                value is not None
                for value in (
                    self.sample_rate,
                    self.channels,
                    self.pcm_samples,
                    self.pcm_sha256,
                )
            ):
                raise Gate14AudioHooksMenuPcmError(
                    "silent numeric dispatch cannot carry decoded sample fields"
                )
            return

        if type(self.sample_slot) is not int or not 0 <= self.sample_slot <= 22:
            raise Gate14AudioHooksMenuPcmError("menus.bnk sample slot must be 0..22")
        if type(self.sample_rate) is not int or self.sample_rate <= 0:
            raise Gate14AudioHooksMenuPcmError("decoded sample rate must be positive")
        if type(self.channels) is not int or self.channels <= 0:
            raise Gate14AudioHooksMenuPcmError("decoded channel count must be positive")
        if type(self.pcm_samples) is not tuple or any(
            type(value) is not int for value in self.pcm_samples
        ):
            raise Gate14AudioHooksMenuPcmError(
                "decoded PCM samples must be an exact tuple[int,...]"
            )
        if not isinstance(self.pcm_sha256, str) or len(self.pcm_sha256) != 64:
            raise Gate14AudioHooksMenuPcmError(
                "decoded PCM SHA-256 must be a 64-character string"
            )


def _require_canonical_menus_bank(data: bytes) -> None:
    if not isinstance(data, bytes):
        raise Gate14AudioHooksMenuPcmError("menus.bnk payload must be bytes")
    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    if (
        len(data) != profile["size_bytes"]
        or sha256(data).hexdigest() != profile["sha256"]
    ):
        raise Gate14AudioHooksMenuPcmError(
            "menus.bnk does not match canonical source identity"
        )


def decode_audiohooks_menu_pcm(
    menus_bnk: bytes,
    event_id: int,
    state_value: int,
) -> DecodedMenuPcmDispatch:
    """Resolve one original numeric AudioHooks event to decoded menus PCM.

    The input bank must be byte-identical to the canonical source-owned
    menus.bnk profile. Semantic names remain intentionally unresolved.
    """
    _require_canonical_menus_bank(menus_bnk)
    dispatch = menus_sample_for_audiohooks_event(event_id, state_value)

    if dispatch.sample_slot is None:
        return DecodedMenuPcmDispatch(
            event_id=event_id,
            state_value=state_value,
            sample_slot=None,
            sample_rate=None,
            channels=None,
            pcm_samples=None,
            pcm_sha256=None,
        )

    try:
        bank = parse_fm2001_bnk(menus_bnk)
    except Gate14BnkFormatError as exc:
        raise Gate14AudioHooksMenuPcmError(
            "canonical menus.bnk failed source-backed parser"
        ) from exc

    sample = next(
        (item for item in bank.samples if item.slot_index == dispatch.sample_slot),
        None,
    )
    if sample is None:
        raise Gate14AudioHooksMenuPcmError(
            "numeric AudioHooks route targets a missing menus.bnk sample slot"
        )

    try:
        pcm = decode_fm2001_bnk_sample(menus_bnk, sample)
        digest = sha256(pcm16le_bytes(pcm)).hexdigest()
    except Gate14BnkFormatError as exc:
        raise Gate14AudioHooksMenuPcmError(
            "routed menus.bnk sample failed source-backed decode"
        ) from exc

    return DecodedMenuPcmDispatch(
        event_id=event_id,
        state_value=state_value,
        sample_slot=sample.slot_index,
        sample_rate=sample.sample_rate,
        channels=sample.channels,
        pcm_samples=pcm,
        pcm_sha256=digest,
    )
