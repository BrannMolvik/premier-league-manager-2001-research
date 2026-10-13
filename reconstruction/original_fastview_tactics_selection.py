"""Source-bounded human FastViewTactics selector values from the shipped FM2001.

This module does NOT implement the live modal, Apply/Cancel, player-record
mutations, child-control updates or a simulated match. Original event IDs
61..68 change DWORDs 1..4 inside a preexisting 70-DWORD source side buffer.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

SOURCE_HUMAN_TACTICS_VTABLE = 0x7CACFC
SOURCE_NATIVE_DISPATCH = 0x52E3F0
SOURCE_SCREEN_PAYLOAD_OFFSET = 0xA54
SOURCE_SIDE_WORD_COUNT = 70
SOURCE_SIDE_BUFFER_SIZE = SOURCE_SIDE_WORD_COUNT * 4

# decrease, increase, DWORD index, low, high, exact NUL-key identities
SOURCE_SELECTOR_RULES = (
    (61, 62, 1, 1, 3, ("NOT_USED", "PlayAttack", "PlayNormal", "PlayDefend")),
    (63, 64, 2, 0, 3, ("WithBallNormal", "WithBallShortPass", "WithBallLongBall", "WithBallCounter")),
    (65, 66, 3, 0, 3, ("WithoutBallNormal", "WithoutBallContain", "WithoutBallPress", "WithoutBallOffsideTrap")),
    (67, 68, 4, 0, 2, ("AggressionLow", "AggressionMedium", "AggressionHigh")),
)


class SourceFastViewTacticsSelectionError(ValueError):
    """A required native selector/event contract is not source verified."""



# These six 11-ID native event families are distinct from low IDs 4..58.
# They are selected in 0x52E975..0x52EC9D after the low-ID switch. Source
# effects are nontrivial and must NOT be simulated by the event classifier.
SOURCE_PLAYER_CONTROL_EVENT_FAMILIES = (
    (0x23D65A, "source_guarded_side_action"),
    (0x247276, "source_side_action_flag1"),
    (0x246E8E, "source_side_action_flag0"),
    (0x2466BE, "player_row_step_decrease"),
    (0x246AA6, "player_row_step_increase"),
    (0x8877AE, "source_guarded_player_apply"),
)
SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT = 11

# Authenticated original native dispatch: child+0x20 event and child+0x24
# parent assigned by 0x64F3C0. 0x64F7A0 invokes parent vft+0x0C
# conditionally; later invokes parent vft+0x10, and 0x651AC0 can invoke
# the +0x10 callback through a second reached source path. Neither callback
# slot is labeled mouse-up/down until the external input producer is traced.
SOURCE_NATIVE_EVENT_OWNER_REGISTRATION = 0x64F3C0
SOURCE_NATIVE_BASE_INPUT_DISPATCH = 0x64F7A0
SOURCE_NATIVE_CHILD_INPUT_DISPATCH = 0x651AC0
SOURCE_NATIVE_CONTROL_FLAGS_OFFSET = 0x18
SOURCE_NATIVE_CONTROL_ACTIVE_MASK = 0x02
SOURCE_NATIVE_CONTROL_BLOCKED_MASK = 0x10
SOURCE_NATIVE_CHILD_EVENT_OFFSET = 0x20
SOURCE_NATIVE_CHILD_PARENT_OFFSET = 0x24
SOURCE_NATIVE_PARENT_CALLBACK_FIRST_SLOT = 0x0C
SOURCE_NATIVE_PARENT_CALLBACK_SECOND_SLOT = 0x10
SOURCE_HUMAN_TACTICS_CALLBACK_FIRST = 0x52E3C0
SOURCE_HUMAN_TACTICS_CALLBACK_SECOND = 0x52E3F0
SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_EVENT_BASE = 0x8877AE
SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_ROW_TARGET = 0x52F690
SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_ACCEPTED_RETURN = 1
SOURCE_NATIVE_STATUS_BYTE_GETTER = 0x651AB0
SOURCE_NATIVE_STATUS_BYTE_OFFSET = 0x40


def source_fastview_native_base_dispatch_flags_allow_processing(flags: int) -> bool:
    """Source preconditions in 0x64F7A0, *not* a complete mouse hit-test.

    For the reached base handler the child must have bit1 set and bit4
    clear. The native parent callback, pointer parameters, sprite state,
    global dispatch and all subsequent guards still determine the outcome.
    """
    if type(flags) is not int or not (0 <= flags <= 0xFFFFFFFF):
        raise SourceFastViewTacticsSelectionError("unsigned original control DWORD required")
    return bool(flags & SOURCE_NATIVE_CONTROL_ACTIVE_MASK) and not bool(
        flags & SOURCE_NATIVE_CONTROL_BLOCKED_MASK
    )


def source_fastview_first_callback_8877ae_row(event_id: int) -> int | None:
    """Map only native +0x0C callback 0x52E3C0's 11-ID special call.

    The source callback returns 1 for *all* event IDs; only 0x8877AE..B8
    calls 0x52F690 with row0..10. Returning None does NOT mean rejection by
    the original callback, nor does a mapped row mean a completed click.
    """
    if type(event_id) is not int or not (0 <= event_id <= 0xFFFFFFFF):
        raise SourceFastViewTacticsSelectionError("unsigned original event DWORD required")
    if SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_EVENT_BASE <= event_id < (
        SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_EVENT_BASE + SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT
    ):
        return event_id - SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_EVENT_BASE
    return None


def source_fastview_guarded_status_allows_followup(native_status_byte: int) -> bool:
    """Necessary-only original +0x40 byte gate before 0x633020.

    When source 0x651AB0 reads a nonzero byte, 0x52EBE3 jumps past the
    guarded mutation path. Zero alone does not prove source predicates or
    final side effects and must never be treated as authorization to edit.
    """
    if type(native_status_byte) is not int or not (0 <= native_status_byte <= 255):
        raise SourceFastViewTacticsSelectionError("unsigned original status byte required")
    return native_status_byte == 0


@dataclass(frozen=True)
class OriginalFastViewPlayerControlEvent:
    family: str
    player_row_index: int
    native_event_id: int


def source_classify_fastview_player_control_event(event_id: int) -> OriginalFastViewPlayerControlEvent:
    """Read-only source decoder of six original eleven-row event families.

    Never performs original 0x6C2170, 0x633020, 0x6C2770, linked-list changes,
    preview, or persistent player/match edits. Those remain source dependencies.
    """
    if type(event_id) is not int:
        raise SourceFastViewTacticsSelectionError("source event ID must be an integer")
    for start, family in SOURCE_PLAYER_CONTROL_EVENT_FAMILIES:
        if start <= event_id < start + SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT:
            return OriginalFastViewPlayerControlEvent(family, event_id - start, event_id)
    raise SourceFastViewTacticsSelectionError("not an original human FastView player-row event")


@dataclass(frozen=True)
class OriginalFastViewTacticsSelectionDraft:
    """Copy of native 280-byte side buffer, never the live world-state owner."""

    original_side_bytes: bytes

    def __post_init__(self):
        if type(self.original_side_bytes) is not bytes or len(self.original_side_bytes) != SOURCE_SIDE_BUFFER_SIZE:
            raise SourceFastViewTacticsSelectionError("original side buffer must be exactly 280 bytes")

    def source_four_values(self) -> tuple[int, int, int, int]:
        return tuple(
            unpack_from("<I", self.original_side_bytes, 4 * index)[0]
            for index in range(1, 5)
        )

    def with_original_selector_event_value_only(self, event_id: int) -> "OriginalFastViewTacticsSelectionDraft":
        """Stage only the original numeric DWORD change for event61..68.

        The real handler ALSO changes native control/list owners. This is NOT
        a complete click, nor does it commit the changed buffer to the match.
        """
        if type(event_id) is not int:
            raise SourceFastViewTacticsSelectionError("event id must be an integer")
        for decrease, increase, index, lowest, highest, _keys in SOURCE_SELECTOR_RULES:
            if event_id not in (decrease, increase):
                continue
            (current,) = unpack_from("<I", self.original_side_bytes, 4 * index)
            if current < lowest or current > highest:
                raise SourceFastViewTacticsSelectionError("unverified native selector value")
            value = current - 1 if event_id == decrease else current + 1
            if value < lowest:
                value = highest
            elif value > highest:
                value = lowest
            data = bytearray(self.original_side_bytes)
            pack_into("<I", data, 4 * index, value)
            return OriginalFastViewTacticsSelectionDraft(bytes(data))
        raise SourceFastViewTacticsSelectionError("not one of four verified +/- native selector pairs")

    def with_original_player_row_step_value_only(
        self, event_id: int, *, mapped_source_row: int
    ) -> "OriginalFastViewTacticsSelectionDraft":
        """Source-bounded payload DWORD change, not the full original event.

        High native event IDs encode a *visible* row0..10, but the actual DWORD
        index is BYTE screen+0xB46+visible_row. This mapping must be supplied
        from the original live screen; never assume visible row==payload row.
        The reached handler also allocates a 0x6334C0 edit, appends its source
        linked-list node and increments a native edit count, none of which this
        nonlive immutable projection attempts to simulate.
        """
        event = source_classify_fastview_player_control_event(event_id)
        if event.family not in ("player_row_step_decrease", "player_row_step_increase"):
            raise SourceFastViewTacticsSelectionError("native row event has nonnumeric source effects")
        if type(mapped_source_row) is not int or not (0 <= mapped_source_row < 11):
            raise SourceFastViewTacticsSelectionError("original 11-row byte mapping required")
        word_index = 42 + mapped_source_row  # (screen+0xAFC)-(screen+0xA54) = 0xA8
        current, = unpack_from("<I", self.original_side_bytes, 4 * word_index)
        if not 0 <= current <= 10:
            raise SourceFastViewTacticsSelectionError("unverified player-row selector DWORD")
        if event.family == "player_row_step_decrease":
            new_value = 10 if current == 0 else current - 1
        else:
            new_value = 0 if current == 10 else current + 1
        data = bytearray(self.original_side_bytes)
        pack_into("<I", data, 4 * word_index, new_value)
        return OriginalFastViewTacticsSelectionDraft(bytes(data))
