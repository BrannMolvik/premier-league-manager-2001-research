"""Source-closed numeric AudioHooks -> menus.bnk sample routing.

The original AudioHooks dispatcher at 0x5DBFC0 switches on numeric event IDs
2..35 and conditionally calls the menus-bank helper at 0x6CFF10 with literal
sample slots. This module preserves only that numeric contract.

It does not assign human-readable event names, UI meanings, match semantics, or
music semantics to those numeric IDs or samples.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14AudioHooksDispatchError(ValueError):
    pass


AUDIO_HOOKS_DISPATCH_VA = 0x5DBFC0
MENUS_PLAYBACK_VA = 0x6CFF10
EVENT_ID_MIN = 2
EVENT_ID_MAX = 35


@dataclass(frozen=True)
class MenuSampleDispatch:
    event_id: int
    state_value: int
    sample_slot: int | None
    event_semantics_recovered: bool = False
    sample_semantics_recovered: bool = False

    def __post_init__(self) -> None:
        if type(self.event_id) is not int or not EVENT_ID_MIN <= self.event_id <= EVENT_ID_MAX:
            raise Gate14AudioHooksDispatchError("event_id must be within original switch range 2..35")
        if type(self.state_value) is not int:
            raise Gate14AudioHooksDispatchError("state_value must be integer")
        if self.sample_slot is not None and (
            type(self.sample_slot) is not int or not 0 <= self.sample_slot <= 22
        ):
            raise Gate14AudioHooksDispatchError("menus.bnk sample slot must be 0..22 or None")
        if self.event_semantics_recovered or self.sample_semantics_recovered:
            raise Gate14AudioHooksDispatchError(
                "numeric dispatch cannot promote unrecovered event/sample meaning"
            )


_UNCONDITIONAL = {
    17: 6,
    18: 7,
    19: 1,
    23: 16,
    24: 17,
    25: 16,
    26: 17,
    31: 20,
    32: 20,
}

_ZERO_STATE = {
    5: 11,
    6: 12,
    20: 13,
    21: 15,
    22: 14,
    27: 8,
    28: 9,
    29: 4,
    30: 5,
    33: 22,
    34: 21,
}

_NO_SOUND_EVENTS = frozenset({7, 9, 11, 12, 13, 14, 15, 16})


def menus_sample_for_audiohooks_event(event_id: int, state_value: int) -> MenuSampleDispatch:
    """Reproduce 0x5DBFC0's numeric switch and second-argument predicates."""
    if type(event_id) is not int or not EVENT_ID_MIN <= event_id <= EVENT_ID_MAX:
        raise Gate14AudioHooksDispatchError("event_id must be within original switch range 2..35")
    if type(state_value) is not int:
        raise Gate14AudioHooksDispatchError("state_value must be integer")

    sample = None
    if event_id in _UNCONDITIONAL:
        sample = _UNCONDITIONAL[event_id]
    elif event_id in _ZERO_STATE:
        sample = _ZERO_STATE[event_id] if state_value == 0 else None
    elif event_id in (2, 3, 4):
        sample = 2 if state_value in (0, 3) else None
    elif event_id == 8:
        sample = 10 if state_value == 8 else None
    elif event_id == 10:
        if state_value in (0, 3):
            sample = 2
        elif state_value == 6:
            sample = 3
    elif event_id == 35:
        if state_value == 0:
            sample = 18
        elif state_value == 1:
            sample = 19
    elif event_id not in _NO_SOUND_EVENTS:
        raise Gate14AudioHooksDispatchError(
            "unclassified original AudioHooks switch entry"
        )

    return MenuSampleDispatch(
        event_id=event_id,
        state_value=state_value,
        sample_slot=sample,
    )


def directly_reachable_menu_sample_slots() -> tuple[int, ...]:
    """Return literal sample slots directly called by 0x5DBFC0.

    Slot 0 is intentionally absent: no direct call from this dispatcher passes
    zero to 0x6CFF10.
    """
    return tuple(range(1, 23))


@dataclass(frozen=True)
class AudioHooksMenuDispatchBoundary:
    numeric_switch_recovered: bool = True
    literal_sample_slots_recovered: bool = True
    state_predicates_recovered: bool = True
    semantic_event_binding_recovered: bool = False
    sample_meaning_recovered: bool = False

    def __post_init__(self) -> None:
        if not (
            self.numeric_switch_recovered
            and self.literal_sample_slots_recovered
            and self.state_predicates_recovered
        ):
            raise Gate14AudioHooksDispatchError(
                "AudioHooks boundary cannot weaken recovered numeric routing"
            )
        if self.semantic_event_binding_recovered or self.sample_meaning_recovered:
            raise Gate14AudioHooksDispatchError(
                "numeric routing cannot promote semantic bindings"
            )


SOURCE_BOUNDARY = AudioHooksMenuDispatchBoundary()
