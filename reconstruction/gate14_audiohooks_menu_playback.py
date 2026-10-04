"""Fail-closed synchronous playback seam for decoded numeric menu PCM.

This module is an orchestration boundary only. It composes the canonical
AudioHooks -> menus.bnk PCM bridge with a caller-supplied synchronous backend.

A backend returning exactly True proves only that the adapter accepted and
completed the supplied decoded packet according to its own contract. It is not
human-audible Windows verification and does not recover semantic event/sample
names.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gate14_audiohooks_menu_pcm import (
    DecodedMenuPcmDispatch,
    Gate14AudioHooksMenuPcmError,
    decode_audiohooks_menu_pcm,
)


class Gate14MenuPcmPlaybackError(RuntimeError):
    pass


class MenuPcmPlaybackBackend(Protocol):
    """Minimal synchronous platform-audio boundary."""

    def play(self, item: DecodedMenuPcmDispatch) -> bool:
        """Return exactly True only after synchronous adapter completion."""


@dataclass(frozen=True)
class MenuPcmPlaybackSummary:
    event_id: int
    state_value: int
    sample_slot: int | None
    backend_invoked: bool
    adapter_delivery_completed: bool
    numeric_routing_recovered: bool = True
    sample_decode_recovered: bool = True
    semantic_event_binding_recovered: bool = False
    sample_meaning_recovered: bool = False
    audible_windows_verified: bool = False
    login_menu_audio_integrated: bool = False

    def __post_init__(self) -> None:
        if type(self.event_id) is not int or type(self.state_value) is not int:
            raise Gate14MenuPcmPlaybackError("event/state values must be integers")
        if not self.numeric_routing_recovered or not self.sample_decode_recovered:
            raise Gate14MenuPcmPlaybackError(
                "playback seam cannot weaken verified numeric routing/sample decode"
            )
        if (
            self.semantic_event_binding_recovered
            or self.sample_meaning_recovered
            or self.audible_windows_verified
            or self.login_menu_audio_integrated
        ):
            raise Gate14MenuPcmPlaybackError(
                "adapter delivery cannot promote semantic, audible, or integration claims"
            )

        if self.sample_slot is None:
            if self.backend_invoked or self.adapter_delivery_completed:
                raise Gate14MenuPcmPlaybackError(
                    "silent numeric route cannot invoke or complete a playback backend"
                )
        else:
            if type(self.sample_slot) is not int or not 0 <= self.sample_slot <= 22:
                raise Gate14MenuPcmPlaybackError(
                    "menus.bnk sample slot must be 0..22 or None"
                )
            if self.adapter_delivery_completed and not self.backend_invoked:
                raise Gate14MenuPcmPlaybackError(
                    "adapter completion requires an invoked backend"
                )


def play_audiohooks_menu_pcm(
    menus_bnk: bytes,
    event_id: int,
    state_value: int,
    backend: MenuPcmPlaybackBackend | None,
) -> MenuPcmPlaybackSummary:
    """Decode one original numeric route and synchronously deliver non-silent PCM.

    Silent routes intentionally do not require or invoke a backend. Non-silent
    routes require a backend whose play() method returns exactly True.
    """
    try:
        decoded = decode_audiohooks_menu_pcm(menus_bnk, event_id, state_value)
    except Gate14AudioHooksMenuPcmError as exc:
        raise Gate14MenuPcmPlaybackError(
            "numeric menu PCM decode failed before platform delivery"
        ) from exc

    if decoded.sample_slot is None:
        return MenuPcmPlaybackSummary(
            event_id=decoded.event_id,
            state_value=decoded.state_value,
            sample_slot=None,
            backend_invoked=False,
            adapter_delivery_completed=False,
        )

    if backend is None or not callable(getattr(backend, "play", None)):
        raise Gate14MenuPcmPlaybackError(
            "non-silent numeric menu PCM requires a backend with play()"
        )

    try:
        completed = backend.play(decoded)
    except Exception as exc:
        raise Gate14MenuPcmPlaybackError(
            "menu PCM playback backend raised during synchronous delivery: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    if completed is not True:
        raise Gate14MenuPcmPlaybackError(
            "menu PCM playback backend did not report exact synchronous completion"
        )

    return MenuPcmPlaybackSummary(
        event_id=decoded.event_id,
        state_value=decoded.state_value,
        sample_slot=decoded.sample_slot,
        backend_invoked=True,
        adapter_delivery_completed=True,
    )
