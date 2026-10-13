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


# Authenticated source 0x52F690 refresh, called only for original first
# callback high-event family 0x8877AE..0x8877B8. The original writes
# list/name/display buffers and invokes virtual +0x3C redraw. These
# projections DO NOT replace that mutable source code or invoke GUI events.
SOURCE_FASTVIEW_ROW_REFRESH_VA = 0x52F690
SOURCE_FASTVIEW_ROW_REFRESH_MAPPED_ROWS_OFFSET = 0xB46
SOURCE_FASTVIEW_ROW_REFRESH_CLUB_ROSTER_COUNT_VA = 0xA14BCC
SOURCE_FASTVIEW_ROW_REFRESH_CLUB_RECORD_STRIDE = 1556
SOURCE_FASTVIEW_ROW_REFRESH_PLAYER_RECORD_STRIDE = 72
SOURCE_FASTVIEW_ROW_REFRESH_NATIVE_CANDIDATE_START = 11
SOURCE_FASTVIEW_ROW_REFRESH_SOURCE_ENABLED_OFFSET = 0xB58
SOURCE_FASTVIEW_ROW_REFRESH_SOURCE_BYPASS_OFFSET = 0xB45
SOURCE_FASTVIEW_ROW_REFRESH_SOURCE_SCOPED_FLAG_VA = 0xA14C0C
SOURCE_FASTVIEW_ROW_REFRESH_REMAP_OFFSET = 0x4848
SOURCE_FASTVIEW_ROW_REFRESH_TEXT_POINTERS_OFFSET = 0x4864
SOURCE_FASTVIEW_ROW_REFRESH_TEXT_BUFFER_OFFSET = 0x4768
SOURCE_FASTVIEW_ROW_REFRESH_REDRAW_SOURCE_VSLOT = 0x3C
SOURCE_FASTVIEW_ROW_REFRESH_REDRAW_ALL_SENTINEL = 11
SOURCE_FASTVIEW_ROW_REFRESH_REDRAW_ALL_FIELD_OFFSET = 0xA68
SOURCE_FASTVIEW_ROW_REFRESH_REDRAW_MODE_BYTE_OFFSET = 0xB44
SOURCE_FASTVIEW_ROW_REFRESH_REDRAW_ROW_TRIPLET_OFFSET = 0xB6D


@dataclass(frozen=True)
class SourceFastViewNativeCandidate:
    """Index eligible for original 0x52F690 name/display list, not UI text."""
    source_roster_slot: int
    mapped_player_index: int


def source_fastview_native_candidates_52f690(
    *,
    visible_row: int,
    source_club_roster_count: int,
    source_mapped_player_by_roster_slot: tuple[int, ...],
    source_enabled_by_player_index: tuple[int, ...],
    source_club_guard_by_player_index: tuple[int, ...],
    source_current_row_bypass_byte: int,
) -> tuple[SourceFastViewNativeCandidate, ...]:
    """Read-only source ordering/filter of optional rows 11..count-1.

    Original source: 0x52F6A1..0x52F6F1 derives guard bypass from +0xB45
    OR club[+0x38] of the player mapped by the clicked visible row.
    0x52F721..0x52F7F7 then visits source slots starting at 11, accepting
    +0xB58[map[slot]] != 0 and (bypass OR club[+0x38] == 0).
    It ALSO formats original names and mutates a native dropdown/list owner.
    Neither that rendering nor any selection/writeback is implemented here.
    """
    def _byte(v: int) -> bool:
        return type(v) is int and 0 <= v <= 255

    if type(visible_row) is not int or not 0 <= visible_row < 11:
        raise SourceFastViewTacticsSelectionError("original clicked visible row required")
    # The native loop assumes count >= 11; a smaller value is not a valid
    # reconstructed world input and would otherwise risk non-termination.
    if type(source_club_roster_count) is not int or source_club_roster_count < 11:
        raise SourceFastViewTacticsSelectionError("native club roster count >= 11 required")
    if any(type(seq) is not tuple for seq in (
        source_mapped_player_by_roster_slot,
        source_enabled_by_player_index,
        source_club_guard_by_player_index,
    )):
        raise SourceFastViewTacticsSelectionError("native source owner snapshots must be tuples")
    if len(source_mapped_player_by_roster_slot) < source_club_roster_count:
        raise SourceFastViewTacticsSelectionError("source map is shorter than native club count")
    if not _byte(source_current_row_bypass_byte):
        raise SourceFastViewTacticsSelectionError("native +0xB45 byte required")
    if any(not _byte(v) for v in source_mapped_player_by_roster_slot):
        raise SourceFastViewTacticsSelectionError("source mapping entries must be BYTEs")
    if any(not _byte(v) for seq in (
        source_enabled_by_player_index, source_club_guard_by_player_index
    ) for v in seq):
        raise SourceFastViewTacticsSelectionError("native guard/enable flags must be BYTEs")
    max_mapped_index = max(source_mapped_player_by_roster_slot[:source_club_roster_count])
    if (max_mapped_index >= len(source_enabled_by_player_index) or
            max_mapped_index >= len(source_club_guard_by_player_index)):
        raise SourceFastViewTacticsSelectionError("original mapped-player status is unavailable")
    current_index = source_mapped_player_by_roster_slot[visible_row]
    bypass = (source_current_row_bypass_byte != 0 or
              source_club_guard_by_player_index[current_index] != 0)
    accepted = []
    for source_slot in range(SOURCE_FASTVIEW_ROW_REFRESH_NATIVE_CANDIDATE_START,
                             source_club_roster_count):
        player = source_mapped_player_by_roster_slot[source_slot]
        if source_enabled_by_player_index[player] == 0:
            continue
        if not bypass and source_club_guard_by_player_index[player] != 0:
            continue
        accepted.append(SourceFastViewNativeCandidate(source_slot, player))
    return tuple(accepted)


def source_fastview_redraw_rows_52f690(
    *, visible_row: int, native_popup_selection: int,
    native_redraw_all_mode_byte: int, native_mapped_player_triplet_flag: int
) -> tuple[int, ...]:
    """Exact original +0x3C redraw targets, NOT mouse hit or text selection.

    0x52F818..0x52F851: all 11 when +0xA68 == 11 OR (+0xB44 != 0 AND
    +0xB6D + 3 * mapped_player_index != 0). Otherwise 0x52F855..0x52F880
    refreshes only the clicked visible-row child if its triplet flag is set.
    """
    if type(visible_row) is not int or not 0 <= visible_row < 11:
        raise SourceFastViewTacticsSelectionError("native visible row required")
    if type(native_popup_selection) is not int or not 0 <= native_popup_selection <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("native popup DWORD required")
    if any(type(v) is not int or not 0 <= v <= 255 for v in (
        native_redraw_all_mode_byte, native_mapped_player_triplet_flag
    )):
        raise SourceFastViewTacticsSelectionError("native redraw status bytes required")
    if native_popup_selection == 11 or (
        native_redraw_all_mode_byte != 0 and native_mapped_player_triplet_flag != 0
    ):
        return tuple(range(11))
    if native_mapped_player_triplet_flag != 0:
        return (visible_row,)
    return ()


# 0x52EC15 only reaches 0x6C2770 when the opaque 0x633020
# collection/validator returns AL==0 after native +0x40 status is zero.
# Do not invoke the following raw primitive merely because a UI row was
# clicked. It does not perform that missing validator or queue 0x6335D0.
SOURCE_FASTVIEW_PLAYER_REPLACE_SOURCE_VA = 0x6C2770
SOURCE_FASTVIEW_PLAYER_REPLACE_CALL_VA = 0x52EC23
SOURCE_FASTVIEW_PLAYER_REPLACE_NATIVE_VALIDATOR_CALL_VA = 0x52EC0D
SOURCE_FASTVIEW_PLAYER_REPLACE_ORDER_OFFSET = 0xF2
SOURCE_FASTVIEW_PLAYER_REPLACE_COUNT_FIELD_OFFSET = 0x14
SOURCE_FASTVIEW_PLAYER_REPLACE_BYTE_COUNT_OFFSET = 0xF0
SOURCE_FASTVIEW_PLAYER_REPLACE_BYTE_FLAG_COUNT_OFFSET = 0xF1
SOURCE_FASTVIEW_PLAYER_REPLACE_TARGET_RESET_OFFSET = 0x104
SOURCE_FASTVIEW_PLAYER_REPLACE_COPY_WORD_OFFSETS = (0x18, 0x60)


def source_fastview_6c2770_side_payload_value_only(
    draft: OriginalFastViewTacticsSelectionDraft,
    *, source_from_player_index: int, source_to_player_index: int,
    source_club_guard_flags: tuple[int, ...],
) -> OriginalFastViewTacticsSelectionDraft:
    """Exact reached 0x6C2770 side-byte edits for bounded valid-world inputs.

    This is the *raw* primitive reached AFTER the separate source +0x40
    and 0x633020 gates, NOT permission to apply a clicked replacement.
    Native 0x6C2770 obtains source ordering count from DWORD +0x14,
    locates both byte indices in +0xF2's first count entries, swaps
    their positions, copies from-index DWORDs at +0x18/+0x60 onto the
    to-index, resets +0x104[to] to zero, decrements byte +0xF0,
    then adjusts byte +0xF1 by the two club +0x38 source guard flags.
    0x6335D0 edit-node enqueue and actual modal/world effects are separate.
    """
    if type(draft) is not OriginalFastViewTacticsSelectionDraft:
        raise SourceFastViewTacticsSelectionError("original side-buffer draft required")
    for player in (source_from_player_index, source_to_player_index):
        if type(player) is not int or player < 0:
            raise SourceFastViewTacticsSelectionError("native player indices required")
        if SOURCE_FASTVIEW_PLAYER_REPLACE_TARGET_RESET_OFFSET + player >= SOURCE_SIDE_BUFFER_SIZE:
            raise SourceFastViewTacticsSelectionError("source byte field would escape side buffer")
        for offset in SOURCE_FASTVIEW_PLAYER_REPLACE_COPY_WORD_OFFSETS:
            if offset + 4 * player + 4 > SOURCE_SIDE_BUFFER_SIZE:
                raise SourceFastViewTacticsSelectionError("source DWORD field would escape side buffer")
    if type(source_club_guard_flags) is not tuple or any(
        type(x) is not int or not 0 <= x <= 255 for x in source_club_guard_flags
    ) or max(source_from_player_index, source_to_player_index) >= len(source_club_guard_flags):
        raise SourceFastViewTacticsSelectionError("authenticated native club flags required")
    data = bytearray(draft.original_side_bytes)
    (source_count,) = unpack_from(
        "<I", data, SOURCE_FASTVIEW_PLAYER_REPLACE_COUNT_FIELD_OFFSET
    )
    if not 1 <= source_count <= SOURCE_SIDE_BUFFER_SIZE - SOURCE_FASTVIEW_PLAYER_REPLACE_ORDER_OFFSET:
        raise SourceFastViewTacticsSelectionError("unverified native +0x14 player ordering count")
    order = data[SOURCE_FASTVIEW_PLAYER_REPLACE_ORDER_OFFSET:
                 SOURCE_FASTVIEW_PLAYER_REPLACE_ORDER_OFFSET + source_count]
    # The native loop defaults to position zero for absent entries. This
    # contract intentionally rejects that unsafe world-state boundary; it
    # does NOT assert that the real validator accepts such missing players.
    if source_from_player_index not in order or source_to_player_index not in order:
        raise SourceFastViewTacticsSelectionError("original ordered player indices unavailable")
    from_slot = order.index(source_from_player_index)
    to_slot = order.index(source_to_player_index)
    data[SOURCE_FASTVIEW_PLAYER_REPLACE_ORDER_OFFSET + from_slot] = source_to_player_index
    data[SOURCE_FASTVIEW_PLAYER_REPLACE_ORDER_OFFSET + to_slot] = source_from_player_index
    data[SOURCE_FASTVIEW_PLAYER_REPLACE_TARGET_RESET_OFFSET + source_to_player_index] = 0
    for offset in SOURCE_FASTVIEW_PLAYER_REPLACE_COPY_WORD_OFFSETS:
        (source_value,) = unpack_from("<I", draft.original_side_bytes,
                                     offset + 4 * source_from_player_index)
        pack_into("<I", data, offset + 4 * source_to_player_index, source_value)
    byte_count = SOURCE_FASTVIEW_PLAYER_REPLACE_BYTE_COUNT_OFFSET
    data[byte_count] = (data[byte_count] - 1) & 0xFF
    guarded_count = SOURCE_FASTVIEW_PLAYER_REPLACE_BYTE_FLAG_COUNT_OFFSET
    data[guarded_count] = (
        data[guarded_count] +
        (1 if source_club_guard_flags[source_from_player_index] != 0 else 0) -
        (1 if source_club_guard_flags[source_to_player_index] != 0 else 0)
    ) & 0xFF
    return OriginalFastViewTacticsSelectionDraft(bytes(data))


# Native 0x651AC0 is itself a wrapper over base 0x64F7A0.
# The original child selection result is NOT a source mouse click.
SOURCE_FASTVIEW_AUX_CHILD_INPUT_VA = 0x651AC0
SOURCE_FASTVIEW_AUX_CHILD_SELECTION_SENTINEL = 0xFFFF
SOURCE_FASTVIEW_AUX_CHILD_LIST_RESULT_OFFSET = 0x3C
SOURCE_FASTVIEW_AUX_CHILD_STATUS_OFFSET = 0x40
SOURCE_FASTVIEW_AUX_CHILD_OWN_EVENT_OFFSET = 0x20
SOURCE_FASTVIEW_AUX_CHILD_PARENT_OFFSET = 0x24
SOURCE_FASTVIEW_AUX_CHILD_SELECTED_RENDER_OWNER_OFFSET = 0x34
SOURCE_FASTVIEW_AUX_CHILD_ROW_ITEM_ARRAY_OFFSET = 0x38
SOURCE_FASTVIEW_AUX_CHILD_PARENT_CALLBACK_VSLOT = 0x10
# The wrapper 0x651AC6 deliberately PUSHes 0 as the base 0x64F7A0
# SECOND argument; both native base parent callback+0x0C and +0x10
# explicitly require that argument nonzero at 0x64F7CF/0x64F811.
# Thus this exact child wrapper cannot double-deliver from its base call.
SOURCE_FASTVIEW_AUX_CHILD_BASE_PARENT_CALLBACK_ARG = 0


@dataclass(frozen=True)
class SourceFastViewAuxChildInputOutcome:
    """Only the reached 0x651AC0 fields; no GUI event inferred."""
    source_handled: bool
    source_status_byte: int | None
    source_saved_selected_index: int | None
    native_parent_second_callback_reached: bool

    @property
    def source_parent_callbacks_from_this_child_route(self) -> tuple[int, ...]:
        """Callback slots from exactly native 0x651AC0 wrapper, not all controls.

        Its nested base 0x64F7A0 runs with callback-permission arg0 and
        invokes NEITHER parent callback. The child can invoke +0x10
        ONCE at 0x651B55 when its separate gates pass, including after
        0xFFFF sentinel status1. Never infer actual click acceptance.
        """
        return (0x10,) if self.native_parent_second_callback_reached else ()


def source_fastview_aux_child_input_outcome_651ac0(
    *, base_dispatch_result: int,
    native_selection_index: int | None,
    child_has_registered_event: bool,
    child_input_callback_argument_nonzero: bool,
) -> SourceFastViewAuxChildInputOutcome:
    """Conservatively project the native child post-base control-flow.

    0x651ACB runs base 0x64F7A0; when it returns zero, native 0x651AD2
    returns without evaluating or updating selection/status. Otherwise
    the child obtains vft+0x98 -> +0x9C and collection vft+0x20
    selection index. 0xFFFF writes status1, other values write status0
    and child+0x3C=index. 0x651B3F..0x651B55 *regardless of sentinel*
    invokes parent+0x10 iff child+0x20 !=0 and callback argument !=0.
    It does not necessarily prove a complete original mouse click or
    the subsequent mutation, even if status0 and callback reached.
    """
    if type(base_dispatch_result) is not int or not 0 <= base_dispatch_result <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("native base DWORD return required")
    if type(child_has_registered_event) is not bool or type(child_input_callback_argument_nonzero) is not bool:
        raise SourceFastViewTacticsSelectionError("original registered event and argument presence required")
    if base_dispatch_result == 0:
        if native_selection_index is not None:
            raise SourceFastViewTacticsSelectionError("base denied input; selection result unavailable")
        return SourceFastViewAuxChildInputOutcome(False, None, None, False)
    if type(native_selection_index) is not int or not 0 <= native_selection_index <= 0xFFFF:
        raise SourceFastViewTacticsSelectionError("native list selection WORD required")
    missing = native_selection_index == SOURCE_FASTVIEW_AUX_CHILD_SELECTION_SENTINEL
    return SourceFastViewAuxChildInputOutcome(
        source_handled=not missing,
        source_status_byte=1 if missing else 0,
        source_saved_selected_index=None if missing else native_selection_index,
        native_parent_second_callback_reached=(
            child_has_registered_event and child_input_callback_argument_nonzero
        ),
    )


# 0x633240 counts only *replacement-class* staged edit nodes via the
# polymorphic vft+4 visitor. Seven other source record types forward to
# visitor slots +0x08..+0x20, which are native 0x6596D0 no-op stubs. The original base record
# virtual +4 is NOT a benign no-op;
# vft 0x7D7F90 (0x6335D0 replacement record) +4 -> 0x633600,
# forwards to count-visitor vft 0x7D803C+4 -> 0x634E40.
# 0x633020 returns AL==0 *when this replacement count is zero*;
# for nonzero replacement-class count it executes the original 0x6331A0/
# 0x634B00 visitor that
# may replay edits, set conflict flags or mutate transient linked nodes.
# A zero count proves only the validator's own outcome, not any earlier
# +0x40 status, source player/world validity or actual edit permission.
SOURCE_FASTVIEW_REPLACEMENT_VALIDATOR_VA = 0x633020
SOURCE_FASTVIEW_REPLACEMENT_COUNT_VISITOR_VA = 0x633240
SOURCE_FASTVIEW_REPLACEMENT_COUNT_METHOD_VA = 0x634E40
SOURCE_FASTVIEW_REPLACEMENT_COUNT_VTABLE = 0x7D803C
SOURCE_FASTVIEW_REPLACEMENT_EDIT_VTABLE = 0x7D7F90
SOURCE_FASTVIEW_REPLACEMENT_EDIT_FORWARD_METHOD_VA = 0x633600
SOURCE_FASTVIEW_REPLACEMENT_REPLAY_VISITOR_VA = 0x6331A0
SOURCE_FASTVIEW_REPLACEMENT_REPLAY_CALLBACK_VA = 0x634B00
SOURCE_FASTVIEW_REPLACEMENT_REPLAY_FLAG_GETTER_VA = 0x634DF0
SOURCE_FASTVIEW_REPLACEMENT_STAGED_COUNT_OFFSET = 0x48AC
SOURCE_FASTVIEW_REPLACEMENT_STAGED_LIST_OFFSET = 0x48A4


def source_fastview_633020_result_when_original_list_empty(
    *, original_staged_edit_count: int
) -> int:
    """Read-only 0x633020 AL when native TOTAL staged list is empty.

    Source 0x633020 first calls 0x633240 and checks EAX==0 at 0x63304E.
    The zero-count path branches to 0x63317E and returns AL=0. An empty
    *total* staged list is sufficient but not necessary: other source edit
    classes do not increment the replacement visitor's counter. This is
    independent of earlier child status and dropdown event dispatch.
    A positive TOTAL node count MUST NOT be modeled by this restricted
    helper: it needs an authenticated eight-type record inventory to tell
    whether the original replacement visitor still returned zero.
    This helper does not produce an edit or write match-side state.
    """
    if (type(original_staged_edit_count) is not int or
            not 0 <= original_staged_edit_count <= 0xFFFFFFFF):
        raise SourceFastViewTacticsSelectionError(
            "original native staged edit count DWORD required"
        )
    if original_staged_edit_count != 0:
        raise SourceFastViewTacticsSelectionError(
            "nonempty original polymorphic replacement replay not yet source complete"
        )
    return 0


# Original 0x633240 and 0x6331A0 traverse the native staged edit list
# with element vft+4. All EIGHT observed native record vtables forward
# to a *different* visitor callback slot, not one generic replacement.
# Original PE rdata 0x7D7F3C..0x7D7F90 (12-byte vtable records) and code
# 0x633450..0x633600, original SHA256 documented in source report.
# This is an immutable class/dispatch map, not a real validator/replay.
SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH = (
    # record vtable, record.vft+4 trampoline, visitor virtual byte offset
    (0x7D7F3C, 0x633450, 0x20),
    (0x7D7F48, 0x633480, 0x1C),
    (0x7D7F54, 0x6334B0, 0x18),
    (0x7D7F60, 0x6334E0, 0x14),
    (0x7D7F6C, 0x633530, 0x10),
    (0x7D7F78, 0x633580, 0x0C),
    (0x7D7F84, 0x6335C0, 0x08),
    (0x7D7F90, 0x633600, 0x04),
)
SOURCE_FASTVIEW_REPLAY_VISITOR_VTABLE = 0x7D8014
SOURCE_FASTVIEW_COUNT_VISITOR_VTABLE = 0x7D803C


@dataclass(frozen=True)
class OriginalFastViewStagedEditVisitorDispatch:
    """Which native visitor vft slot a source-known edit class invokes."""
    record_vtable: int
    record_virtual_four_target: int
    visitor_callback_offset: int


def source_fastview_original_staged_record_visitor_dispatch(
    *, native_record_vtable: int
) -> OriginalFastViewStagedEditVisitorDispatch:
    """Classify one authenticated original staged edit record vtable only.

    Every source record class has separate virtual behavior in 0x633240
    count and 0x6331A0 replay. The actual native visitor implementations
    0x634920..0x634B00 are NOT replaced by this map.
    """
    if type(native_record_vtable) is not int or not 0 <= native_record_vtable <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("native source DWORD vtable required")
    for vtable, target, offset in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH:
        if native_record_vtable == vtable:
            return OriginalFastViewStagedEditVisitorDispatch(vtable, target, offset)
    raise SourceFastViewTacticsSelectionError("unverified native FastView staged edit class")


# Source 0x633240's visitor (0x7D803C): only offset +0x04 increments
# the counter; +0x08/+0x0C/+0x10/+0x14/+0x18/+0x1C/+0x20 all
# point to original 0x6596D0 (ret 4, does not touch counter). Therefore
# a nonempty original staged list containing NO 0x7D7F90 replacement
# records STILL returns zero from native 0x633240/0x633020.
# This corrects Recovery590/591's overbroad "counts all edits" claim.
SOURCE_FASTVIEW_COUNT_VISITOR_NOOP_VA = 0x6596D0
SOURCE_FASTVIEW_COUNT_VISITOR_INCREMENT_SLOT = 0x04
SOURCE_FASTVIEW_REPLACEMENT_RECORD_CLASS_VTABLE = 0x7D7F90
SOURCE_FASTVIEW_STAGED_TOTAL_NODE_COUNT_OFFSET = 0x48AC


def source_fastview_633240_count_replacement_records(
    *, original_staged_record_vtables: tuple[int, ...]
) -> int:
    """Source-equivalent bounded 0x633240 counter for eight known record types.

    Requires the actual original staged-list record-class inventory; this
    is NOT equivalent to screen+0x48AC total node count. The exact source
    counts only visitor+0x04 0x7D7F90 replacement records. All other seven
    verified source edit classes dispatch native no-op visitor callbacks.
    Unknown or invalid record classes fail closed before any simulated
    counting. No edits, callbacks or original GUI state are changed.
    """
    if type(original_staged_record_vtables) is not tuple:
        raise SourceFastViewTacticsSelectionError(
            "native staged edit record-class inventory must be a tuple"
        )
    valid = {row[0] for row in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH}
    count = 0
    for vtable in original_staged_record_vtables:
        if type(vtable) is not int or vtable not in valid:
            raise SourceFastViewTacticsSelectionError(
                "original native staged record vtable not source verified"
            )
        if vtable == SOURCE_FASTVIEW_REPLACEMENT_RECORD_CLASS_VTABLE:
            count += 1
    return count


def source_fastview_633020_result_without_replacement_records(
    *, original_staged_record_vtables: tuple[int, ...]
) -> int:
    """Bounded native validator AL==0 when its replacement count is zero.

    Unlike the earlier *total-list-empty* projection, this also admits
    genuine other-type-only edit inventories. A replacement-class node
    triggers the original 0x6331A0 polymorphic replay, which this helper
    must NOT pretend to understand. All earlier control status/range
    guards and possible callback duplicates remain independent.
    """
    count = source_fastview_633240_count_replacement_records(
        original_staged_record_vtables=original_staged_record_vtables
    )
    if count:
        raise SourceFastViewTacticsSelectionError(
            "native replacement-class replay is not yet source-complete"
        )
    return 0


# Native 0x6331A0 replay visitor vtable 0x7D8014 uses eight slots
# +0x04..+0x20. Actual PE DWORD table (not original type names):
# replacement +4 -> 0x634B00; 5 of the other classes forward to
# list-forwarding 0x634AB0; two have independent conditional handlers
# 0x634990 and 0x634920. These methods are NOT assumed passive:
# 0x634AB0 appends original record pointers into the native list.
SOURCE_FASTVIEW_REPLAY_VISITOR_VTABLE_METHODS = (
    (0x04, 0x634B00),
    (0x08, 0x634AB0),
    (0x0C, 0x634AB0),
    (0x10, 0x634990),
    (0x14, 0x634920),
    (0x18, 0x634AB0),
    (0x1C, 0x634AB0),
    (0x20, 0x634AB0),
)


@dataclass(frozen=True)
class OriginalFastViewReplayMethodResolution:
    native_record_vtable: int
    source_record_dispatch_va: int
    source_visitor_method_va: int
    source_visitor_virtual_offset: int


def source_fastview_staged_record_native_replay_method(
    *, native_record_vtable: int
) -> OriginalFastViewReplayMethodResolution:
    """Source-only original record virtual +4 -> visitor virtual dispatch.

    Does not run any of 0x634920, 0x634990, 0x634AB0 or 0x634B00;
    none may be promoted to no-op or one-shot UI save. Validating which
    callback the real original *would reach* is necessary before model-
    driven linked-list replay or complete human FastView mode2 support.
    """
    record = source_fastview_original_staged_record_visitor_dispatch(
        native_record_vtable=native_record_vtable
    )
    for slot, method in SOURCE_FASTVIEW_REPLAY_VISITOR_VTABLE_METHODS:
        if slot == record.visitor_callback_offset:
            return OriginalFastViewReplayMethodResolution(
                record.record_vtable,
                record.record_virtual_four_target, method, slot
            )
    raise SourceFastViewTacticsSelectionError("unverified original visitor method")


# Two original specialized non-replacement replay callbacks:
# record class 0x7D7F60 -> visitor+0x14 -> 0x634920 (may OMIT),
# record class 0x7D7F6C -> visitor+0x10 -> 0x634990 (may RECONSTRUCT).
# The predicates share original scratch BYTE visitor+0x09 and native
# 0x6335B0 (record+0x04) compared with visitor+0x0C. Source-only outcomes,
# NOT actual native list or side-state writes, nor source player identity.
SOURCE_FASTVIEW_REPLAY_FLAG_NINE_OFFSET = 0x09
SOURCE_FASTVIEW_REPLAY_RECORD_DWORD_FOUR_GETTER_VA = 0x6335B0
SOURCE_FASTVIEW_REPLAY_OMIT_CLASS_VTABLE = 0x7D7F60
SOURCE_FASTVIEW_REPLAY_OMIT_METHOD_VA = 0x634920
SOURCE_FASTVIEW_REPLAY_RECONSTRUCT_CLASS_VTABLE = 0x7D7F6C
SOURCE_FASTVIEW_REPLAY_RECONSTRUCT_METHOD_VA = 0x634990
SOURCE_FASTVIEW_REPLAY_RECONSTRUCT_CTOR_VA = 0x6334F0


def source_fastview_special_replay_record_branch(
    *, native_record_vtable: int, visitor_status9: int,
    native_record_dword_four: int, requested_source_dword: int
) -> str:
    """Return 0x634920/0x634990 source branch, not its side effects.

    If status9 is nonzero and native record +4 equals visitor +0x0C:
    0x634920 returns without appending the current record to output.
    0x634990 instead allocates and constructs 0x6334F0 record with
    other original fields (not implemented) and deletes the old node.
    Otherwise both callbacks preserve/append the current record.
    This does NOT complete 0x633020 or authorize a live match edit.
    """
    if native_record_vtable not in (
        SOURCE_FASTVIEW_REPLAY_OMIT_CLASS_VTABLE,
        SOURCE_FASTVIEW_REPLAY_RECONSTRUCT_CLASS_VTABLE,
    ) or type(native_record_vtable) is not int:
        raise SourceFastViewTacticsSelectionError("unqualified special replay record class")
    if type(visitor_status9) is not int or not (0 <= visitor_status9 <= 255):
        raise SourceFastViewTacticsSelectionError("native visitor BYTE +9 required")
    if any(type(v) is not int or not (0 <= v <= 0xFFFFFFFF) for v in (
        native_record_dword_four, requested_source_dword
    )):
        raise SourceFastViewTacticsSelectionError("native unsigned original record DWORDs required")
    match = visitor_status9 != 0 and native_record_dword_four == requested_source_dword
    if not match:
        return "append_original_record"
    if native_record_vtable == SOURCE_FASTVIEW_REPLAY_OMIT_CLASS_VTABLE:
        return "omit_record"
    return "reconstruct_0x6334f0_record"


# Native 0x634B00 replacement-record visitor has FOUR distinct reached
# source branches; class 0x7D7F90's native forwarding virtual+4 calls
# this method only under the source 0x7D8014 replay visitor. This is a
# branch classifier, NOT linked-list writes, replay or completed match.
SOURCE_FASTVIEW_REPLAY_REPLACEMENT_VISITOR_VA = 0x634B00
SOURCE_FASTVIEW_REPLAY_PREVIOUS_TARGET_GETTER_VA = 0x6335F0
SOURCE_FASTVIEW_REPLAY_CHAIN_CTOR_VA = 0x6335D0


def source_fastview_replacement_replay_branch_634b00(
    *, visitor_status8: int, visitor_status9: int,
    native_skip_replacement_count: int,
    previous_replacement_target_dword: int,
    requested_source_dword: int,
) -> str:
    """Read-only original ordered branch selection for visitor 0x634B00.

    0x634B1C..0x634B2C: status9 OR status8 -> append existing record.
    0x634B32..0x634B79: nonzero remaining skip decremented and a
    list node with no payload is appended, without target comparison.
    0x634B82..0x634B8C: old replacement target compared with current
    requested source (visitor +0x0C); if equal the original *also*
    constructs chained edit and mutates side data, otherwise forwards
    the existing record and sets status8. These further mutations are
    intentionally NOT implemented by returning a branch identifier.
    """
    for x in (visitor_status8, visitor_status9):
        if type(x) is not int or not 0 <= x <= 255:
            raise SourceFastViewTacticsSelectionError("original visitor status BYTE required")
    for x in (native_skip_replacement_count, previous_replacement_target_dword,
              requested_source_dword):
        if type(x) is not int or not 0 <= x <= 0xFFFFFFFF:
            raise SourceFastViewTacticsSelectionError("original visitor native DWORD required")
    if visitor_status9 or visitor_status8:
        return "forward_old_record_after_prior_status"
    if native_skip_replacement_count:
        return "decrement_skip_and_append_empty_link"
    if previous_replacement_target_dword == requested_source_dword:
        return "chained_replacement_side_rewrite"
    return "forward_old_record_mark_status8"


# Original 0x634B00 linked replacement-chain match branch mutates its OWN
# 280-byte transient match-side payload at 0x634C1D..0x634CF4,
# separately from the new replacement handler 0x6C2770. This is not a
# live match writeback or the polymorphic 0x633020 list replay.
SOURCE_FASTVIEW_CHAIN_SOURCE_VA = 0x634C1D
SOURCE_FASTVIEW_CHAIN_ORDER_LOOKUP_VA = 0x634DB0
SOURCE_FASTVIEW_CHAIN_STATUS_ON_OFFSET = 0x104
SOURCE_FASTVIEW_CHAIN_STATUS_OFF_OFFSET = 0x104
SOURCE_FASTVIEW_CHAIN_ORDER_OFFSET = 0xF2
SOURCE_FASTVIEW_CHAIN_COUNT_OFFSET = 0x14
SOURCE_FASTVIEW_CHAIN_SOURCE_WORD_OFFSETS = (0x18, 0x60)
SOURCE_FASTVIEW_CHAIN_GUARD_COUNTER_OFFSET = 0xF1
SOURCE_FASTVIEW_CHAIN_VISITOR_STATUS9_SET_VA = 0x634CF4


def source_fastview_634b00_matched_chain_payload_value_only(
    draft: OriginalFastViewTacticsSelectionDraft,
    *, requested_from_index: int, requested_to_index: int,
    original_club_guard_flags: tuple[int, ...],
) -> OriginalFastViewTacticsSelectionDraft:
    """Preserve 0x634C1D..0x634CF4 actual side write ORDER as immutable bytes.

    Entry requires the separate original replay visitor's matching
    0x634B82 old replacement target == requested_from_index, and all
    native status8/status9/skip/class/caller conditions. Those are NOT
    checked or authorized here; use the original branch classifier and
    complete 0x633020 owner once source-proven, not a row click.

    Native side writes:
      +0x104[from] = 1; +0x104[to] = 0;
      +0xF2[to] = previous +0xF2[from];
      +0xF2[from] = BYTE from;
      +0xF2[first_position_of_from] = BYTE to;
      +0x18/+0x60 DWORD[to] = previous DWORD[from];
      +0xF1 += nonzero_club_guard[from] - nonzero_club_guard[to].
    The native visitor sets its OWN +9 flag afterwards. This helper
    does not model that flag, list transfer, edit count, or match state.
    Absent source order entry fails closed, unlike unsafe native
    end-position fallback whose prerequisites are not established.
    """
    if type(draft) is not OriginalFastViewTacticsSelectionDraft:
        raise SourceFastViewTacticsSelectionError("original immutable side payload required")
    if type(original_club_guard_flags) is not tuple or any(
        type(flag) is not int or not 0 <= flag <= 255 for flag in original_club_guard_flags
    ):
        raise SourceFastViewTacticsSelectionError("original club player BYTE flags required")
    side = bytearray(draft.original_side_bytes)
    (count,) = unpack_from("<I", side, SOURCE_FASTVIEW_CHAIN_COUNT_OFFSET)
    # The original +0x104 byte array starts immediately after the
    # source +0xF2 order's 18-byte dedicated region. An oversized count
    # would alias unrelated status bytes; do not treat that unproven
    # native memory state as a valid immutable side record.
    source_order_capacity = (
        SOURCE_FASTVIEW_CHAIN_STATUS_ON_OFFSET - SOURCE_FASTVIEW_CHAIN_ORDER_OFFSET
    )
    if not 1 <= count <= source_order_capacity:
        raise SourceFastViewTacticsSelectionError("bounded native side ordering count required")
    if (type(requested_from_index) is not int or
            not 0 <= requested_from_index < count):
        raise SourceFastViewTacticsSelectionError("original active source must index native side order")
    for idx in (requested_from_index, requested_to_index):
        if type(idx) is not int or not 0 <= idx < source_order_capacity:
            raise SourceFastViewTacticsSelectionError("original dedicated order BYTE index required")
        if type(idx) is not int or not 0 <= idx <= 0xFF:
            raise SourceFastViewTacticsSelectionError("original requested player index BYTE required")
        if idx >= len(original_club_guard_flags):
            raise SourceFastViewTacticsSelectionError("original club player status unavailable")
        if SOURCE_FASTVIEW_CHAIN_ORDER_OFFSET + idx >= len(side) or (
            SOURCE_FASTVIEW_CHAIN_STATUS_ON_OFFSET + idx >= len(side)
        ) or any(
            offset + 4 * idx + 4 > len(side) for offset in SOURCE_FASTVIEW_CHAIN_SOURCE_WORD_OFFSETS
        ):
            raise SourceFastViewTacticsSelectionError("source player index escapes native 280-byte side")
    start = SOURCE_FASTVIEW_CHAIN_ORDER_OFFSET
    source_order = side[start:start + count]
    if requested_from_index not in source_order:
        raise SourceFastViewTacticsSelectionError("native replay source player absent from side order")
    pos = source_order.index(requested_from_index)
    source_old_order_byte = side[start + requested_from_index]
    side[SOURCE_FASTVIEW_CHAIN_STATUS_ON_OFFSET + requested_from_index] = 1
    side[SOURCE_FASTVIEW_CHAIN_STATUS_OFF_OFFSET + requested_to_index] = 0
    side[start + requested_to_index] = source_old_order_byte
    side[start + requested_from_index] = requested_from_index
    side[start + pos] = requested_to_index
    for offset in SOURCE_FASTVIEW_CHAIN_SOURCE_WORD_OFFSETS:
        value, = unpack_from("<I", draft.original_side_bytes, offset + 4 * requested_from_index)
        pack_into("<I", side, offset + 4 * requested_to_index, value)
    key = SOURCE_FASTVIEW_CHAIN_GUARD_COUNTER_OFFSET
    side[key] = (
        side[key]
        + (1 if original_club_guard_flags[requested_from_index] != 0 else 0)
        - (1 if original_club_guard_flags[requested_to_index] != 0 else 0)
    ) & 0xFF
    return OriginalFastViewTacticsSelectionDraft(bytes(side))


# 0x633020 with EXACTLY ONE prior 0x7D7F90 replacement record
# (and no other staged records) runs exactly one 0x6331A0 replay pass.
# Its visitor is initialized with skip DWORD+4=0 (native loop index
# EBX=0), BYTE status8=0 and BYTE status9=0. The single old record's
# virtual+4 calls 0x634B00:
# - old.to == requested.from => new replacement (old.from, requested.to)
#   is constructed at 0x634BB8, old deleted and the 0x634C1D side
#   change executes, setting visitor+9=1 and validator AL1.
# - old.to != requested.from => old record is re-appended unchanged at
#   0x634CFD..0x634D3F, sets visitor+8=1, visitor+9 stays0, AL0.
# After AL0, original 0x52EC23 invokes fresh 0x6C2770. Neither that
# later call nor original click/status/selection gates run here.
SOURCE_FASTVIEW_SINGLE_REPLACEMENT_REPLAY_CALLER_VA = 0x633107
SOURCE_FASTVIEW_SINGLE_REPLACEMENT_REPLAY_INITIAL_SKIP = 0
SOURCE_FASTVIEW_SINGLE_REPLACEMENT_CLASS_VTABLE = 0x7D7F90


@dataclass(frozen=True)
class SourceFastViewNativeReplacementRecord:
    """Original 0x6335D0 record's two DWORD fields (+4,+8)."""
    native_from_index: int
    native_to_index: int

    def __post_init__(self) -> None:
        for value in (self.native_from_index, self.native_to_index):
            if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
                raise SourceFastViewTacticsSelectionError(
                    "original native replacement record DWORD required"
                )


@dataclass(frozen=True)
class SourceFastViewOneReplacementReplayValue:
    """Only original one-existing-record replay outcome, NOT live GUI."""
    replay_validator_al: int
    replacement_record_after_replay: SourceFastViewNativeReplacementRecord
    side_after_replay: OriginalFastViewTacticsSelectionDraft
    fresh_replacement_source_call_reachable: bool


def source_fastview_633020_one_existing_replacement_replay_value_only(
    original_side: OriginalFastViewTacticsSelectionDraft,
    *, original_single_replacement_record: SourceFastViewNativeReplacementRecord,
    requested_from_index: int, requested_to_index: int,
    original_club_guard_flags: tuple[int, ...],
) -> SourceFastViewOneReplacementReplayValue:
    """Source-exact one-record replay, with independent prior caller gates.

    This helper requires caller-proven original native list inventory:
    EXACTLY ONE previously staged class0x7D7F90 replacement, NO other
    types. It cannot discover that from a mouse click or a total count.
    The source 0x633020 clears the list and replays one node before
    returning. For this 1-record case, the only reached 0x634B00
    branches are matched chain or mismatched prior destination.

    The result does not perform the subsequent 0x6C2770 fresh write
    even when AL0, does not commit the side buffer, and does not model
    native event, match state, PResults, or management return. All
    external +0x40/dropdown/row/club/side validity must still be proven.
    """
    if type(original_side) is not OriginalFastViewTacticsSelectionDraft:
        raise SourceFastViewTacticsSelectionError("authentic side draft required")
    if type(original_single_replacement_record) is not SourceFastViewNativeReplacementRecord:
        raise SourceFastViewTacticsSelectionError("authenticated single source replacement record required")
    if type(requested_from_index) is not int or not 0 <= requested_from_index <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("native requested source DWORD required")
    if type(requested_to_index) is not int or not 0 <= requested_to_index <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("native requested destination DWORD required")
    if type(original_club_guard_flags) is not tuple or any(
        type(value) is not int or not 0 <= value <= 255 for value in original_club_guard_flags
    ):
        raise SourceFastViewTacticsSelectionError("native club guard BYTE snapshot required")
    old = original_single_replacement_record
    if old.native_to_index != requested_from_index:
        return SourceFastViewOneReplacementReplayValue(
            replay_validator_al=0,
            replacement_record_after_replay=old,
            side_after_replay=original_side,
            fresh_replacement_source_call_reachable=True,
        )
    edited_side = source_fastview_634b00_matched_chain_payload_value_only(
        original_side, requested_from_index=requested_from_index,
        requested_to_index=requested_to_index,
        original_club_guard_flags=original_club_guard_flags,
    )
    # Original 0x634BB8 passes new target and the previous replacement's
    # +4 from-player field, recreating a single native 0x6335D0 record.
    new_record = SourceFastViewNativeReplacementRecord(
        old.native_from_index, requested_to_index
    )
    return SourceFastViewOneReplacementReplayValue(
        replay_validator_al=1,
        replacement_record_after_replay=new_record,
        side_after_replay=edited_side,
        fresh_replacement_source_call_reachable=False,
    )


@dataclass(frozen=True)
class SourceFastViewOneReplacementFollowupValue:
    """Original bounded after-validator state; no live game-world mutation."""
    native_validator_al: int
    source_followup_6c2770_was_applied: bool
    original_side_after: OriginalFastViewTacticsSelectionDraft
    original_staged_replacements_after: tuple[SourceFastViewNativeReplacementRecord, ...]


def source_fastview_one_prior_replacement_followup_value_only(
    original_side: OriginalFastViewTacticsSelectionDraft,
    *, native_child_status_byte: int,
    original_single_replacement_record: SourceFastViewNativeReplacementRecord,
    native_current_mapped_from_index: int,
    native_selected_to_index: int,
    original_club_guard_flags: tuple[int, ...],
) -> SourceFastViewOneReplacementFollowupValue:
    """Exact 1-prior-replacement value effects of 0x633020 + caller 0x52EC23.

    Caller MUST independently source-qualify actual native pointer/child
    callback delivery, current club/side, selected dropdown, row/player
    mapping and original edit-list inventory exactly one replacement with
    no other native records. This is a pure bounded transition, never an
    authorization to dispatch a click or commit a match.

    When the old target matches requested new source, native 0x634B00
    rewrites its one staged record and original side, then returns AL1,
    so human 0x52EC17 SKIPS fresh 0x6C2770.
    Otherwise the old record is preserved, AL0, and the real handler
    0x52EC23 invokes 0x6C2770, then queues new 0x6335D0 record and
    increments native edit-list count. The existing source-constrained
    0x6C2770 helper intentionally fails closed if it cannot locate
    required original ordering indices rather than fabricating them.
    """
    if not source_fastview_guarded_status_allows_followup(native_child_status_byte):
        raise SourceFastViewTacticsSelectionError("native row +0x40 status disallows followup")
    replay = source_fastview_633020_one_existing_replacement_replay_value_only(
        original_side,
        original_single_replacement_record=original_single_replacement_record,
        requested_from_index=native_current_mapped_from_index,
        requested_to_index=native_selected_to_index,
        original_club_guard_flags=original_club_guard_flags,
    )
    if replay.replay_validator_al != 0:
        return SourceFastViewOneReplacementFollowupValue(
            1, False, replay.side_after_replay,
            (replay.replacement_record_after_replay,)
        )
    fresh_side = source_fastview_6c2770_side_payload_value_only(
        replay.side_after_replay,
        source_from_player_index=native_current_mapped_from_index,
        source_to_player_index=native_selected_to_index,
        source_club_guard_flags=original_club_guard_flags,
    )
    return SourceFastViewOneReplacementFollowupValue(
        0, True, fresh_side,
        (
            replay.replacement_record_after_replay,
            SourceFastViewNativeReplacementRecord(
                native_current_mapped_from_index,
                native_selected_to_index,
            ),
        ),
    )


def source_fastview_two_distinct_prior_replacements_followup_value_only(
    original_side: OriginalFastViewTacticsSelectionDraft,
    *, native_child_status_byte: int,
    original_two_replacement_records: tuple[
        SourceFastViewNativeReplacementRecord,
        SourceFastViewNativeReplacementRecord,
    ],
    native_current_mapped_from_index: int,
    native_selected_to_index: int,
    original_club_guard_flags: tuple[int, ...],
) -> SourceFastViewOneReplacementFollowupValue:
    """Source-bounded TWO prior replacements, distinct original targets.

    Source 0x633020 calls 0x6331A0 precisely once per original native
    replacement-class node. 0x6348E0 initializes visitor DWORD+4 from
    the outer loop index. 0x634B00 forwards/skips previous replacement
    nodes while decrementing that index, then processes the current
    node; its replay status8/status9 is local to THAT visitor pass.
    Earlier matched chains still contribute to the outer OR of AL.
    This narrow projection admits two prior replacement records ONLY,
    with distinct previous targets so no unverified repeated alias
    chain on the same requested source can occur.

    Each pass preserves native old-node relative order; a matching
    record is replaced in-place in that source order, updates the
    original side via 0x634C1D and yields AL1 for that pass; no match
    preserves that original record and yields AL0. When neither
    pass chains, 0x52EC23 applies fresh 0x6C2770 then the caller
    appends one 0x6335D0 record. This helper models only original
    values under caller-qualified native event/list state; it never
    simulates Win32 controls, commits match state or invents a PResult.
    """
    if not source_fastview_guarded_status_allows_followup(native_child_status_byte):
        raise SourceFastViewTacticsSelectionError("native +0x40 child status blocks original edit")
    if (type(original_two_replacement_records) is not tuple or
            len(original_two_replacement_records) != 2 or
            any(type(x) is not SourceFastViewNativeReplacementRecord
                for x in original_two_replacement_records)):
        raise SourceFastViewTacticsSelectionError("exact two original replacement-only nodes required")
    first, second = original_two_replacement_records
    if first.native_to_index == second.native_to_index:
        raise SourceFastViewTacticsSelectionError(
            "duplicate prior replacement targets require separate native chain alias proof"
        )
    if type(original_side) is not OriginalFastViewTacticsSelectionDraft:
        raise SourceFastViewTacticsSelectionError("original side draft required")
    if type(native_current_mapped_from_index) is not int or not (
        0 <= native_current_mapped_from_index <= 0xFFFFFFFF
    ) or type(native_selected_to_index) is not int or not (
        0 <= native_selected_to_index <= 0xFFFFFFFF
    ):
        raise SourceFastViewTacticsSelectionError("original native source and target DWORDs required")
    if type(original_club_guard_flags) is not tuple or any(
        type(f) is not int or not 0 <= f <= 255 for f in original_club_guard_flags
    ):
        raise SourceFastViewTacticsSelectionError("native club BYTE guards required")

    updated_side = original_side
    records = []
    any_matched = False
    for prior in (first, second):
        if prior.native_to_index == native_current_mapped_from_index:
            updated_side = source_fastview_634b00_matched_chain_payload_value_only(
                updated_side,
                requested_from_index=native_current_mapped_from_index,
                requested_to_index=native_selected_to_index,
                original_club_guard_flags=original_club_guard_flags,
            )
            records.append(SourceFastViewNativeReplacementRecord(
                prior.native_from_index, native_selected_to_index
            ))
            any_matched = True
        else:
            records.append(prior)
    if any_matched:
        return SourceFastViewOneReplacementFollowupValue(
            1, False, updated_side, tuple(records)
        )
    fresh = source_fastview_6c2770_side_payload_value_only(
        updated_side, source_from_player_index=native_current_mapped_from_index,
        source_to_player_index=native_selected_to_index,
        source_club_guard_flags=original_club_guard_flags,
    )
    records.append(SourceFastViewNativeReplacementRecord(
        native_current_mapped_from_index, native_selected_to_index
    ))
    return SourceFastViewOneReplacementFollowupValue(
        0, True, fresh, tuple(records)
    )


# All eleven x133 FastView controls at screen+0x263C+0x44*row are
# constructed as an actual 0x52DD30 object array by the original
# FastViewTactics constructor 0x52D894..0x52D8A9 (native CRT vector
# constructor 0x6687C1, count11, stride0x44). Original 0x52DD30 calls
# 0x651A30 and assigns derived vtable 0x7CB010; virtual+0x6C is
# 0x52D0D0, +0x98 0x52D120 and +0x9C 0x52D190.
# Its outer input handler may dispatch original parent+0x0C FIRST,
# veto the child if return zero, and otherwise invokes 0x651AC0.
# The inner 0x651AC0 calls base 0x64F7A0 with callback argument ZERO,
# suppressing base parent callbacks; it may itself call parent+0x10
# once. This sequence is source-proven for the x133 fifth-family child,
# NOT a blanket rule for all original input controls.
SOURCE_FASTVIEW_X133_VECTOR_CTOR_OWNER_VA = 0x52D894
SOURCE_FASTVIEW_X133_VECTOR_CTOR_VA = 0x6687C1
SOURCE_FASTVIEW_X133_CHILD_CTOR_VA = 0x52DD30
SOURCE_FASTVIEW_X133_CHILD_DERIVED_VTABLE_VA = 0x7CB010
SOURCE_FASTVIEW_X133_INPUT_OUTER_VA = 0x52D0D0
SOURCE_FASTVIEW_X133_INPUT_INNER_VA = 0x651AC0
SOURCE_FASTVIEW_X133_INPUT_OUTER_FIRST_CALLBACK_VSLOT = 0x0C
SOURCE_FASTVIEW_X133_INPUT_INNER_SECOND_CALLBACK_VSLOT = 0x10
SOURCE_FASTVIEW_X133_CHILD_ROW_COUNT = 11
SOURCE_FASTVIEW_X133_CHILD_ROW_STRIDE = 0x44
SOURCE_FASTVIEW_X133_CHILD_ROW_ZERO_OFFSET = 0x263C


@dataclass(frozen=True)
class OriginalFastViewX133InputRoute:
    """Original callback delivery stages, not a synthetic mouse input."""
    source_first_callback_reached: bool
    source_first_callback_refresh_row: int | None
    source_first_callback_vetoed_child: bool
    source_inner_child_reached: bool
    source_inner_child_outcome: SourceFastViewAuxChildInputOutcome | None
    source_parent_callback_slots: tuple[int, ...]


def source_fastview_x133_native_input_route_52d0d0(
    *, native_child_flags: int,
    native_registered_event_id: int | None,
    original_parent_first_callback_return: int | None,
    inner_original_base_dispatch_result: int | None,
    inner_original_native_selection_index: int | None,
    original_child_second_callback_argument_nonzero: bool,
) -> OriginalFastViewX133InputRoute:
    """Source-order 0x52D0D0 -> 0x651AC0 x133 child dispatch contract.

    The source outer first-callback is gated by native bit1 set, bit4
    clear, and registered child event+0x20 nonzero. With these gates,
    parent vft+0x0C is invoked (0x52E3C0 for FastViewTactics), which
    on 0x8877AE..0x8877B8 rows calls the SOURCE row refresh 0x52F690.
    Parent first return zero vetoes ALL inner child processing.
    When outer first-callback not eligible, it nevertheless forwards
    to the child. The inner child calls base with SECOND arg0 so it
    cannot duplicate callbacks, but can itself invoke parent +0x10
    after selection under independent child event/input gates.

    This is not a pointer hit-test, mouse-up semantic, modal owner,
    player replacement permission, or genuine match writeback.
    """
    if type(native_child_flags) is not int or not 0 <= native_child_flags <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("native child flags DWORD required")
    if native_registered_event_id is not None and (
        type(native_registered_event_id) is not int or
        not 0 <= native_registered_event_id <= 0xFFFFFFFF
    ):
        raise SourceFastViewTacticsSelectionError("original child event DWORD required")
    if type(original_child_second_callback_argument_nonzero) is not bool:
        raise SourceFastViewTacticsSelectionError("original child second argument gate required")
    registered = native_registered_event_id is not None and native_registered_event_id != 0
    first_reached = (
        source_fastview_native_base_dispatch_flags_allow_processing(native_child_flags)
        and registered
    )
    if first_reached:
        if type(original_parent_first_callback_return) is not int or not (
            0 <= original_parent_first_callback_return <= 0xFFFFFFFF
        ):
            raise SourceFastViewTacticsSelectionError("native first parent callback result required")
        first_row = source_fastview_first_callback_8877ae_row(native_registered_event_id)
        if original_parent_first_callback_return == 0:
            if inner_original_base_dispatch_result is not None or inner_original_native_selection_index is not None:
                raise SourceFastViewTacticsSelectionError("source outer parent veto prevents inner input")
            return OriginalFastViewX133InputRoute(True, first_row, True, False, None, (0x0C,))
    else:
        if original_parent_first_callback_return is not None:
            raise SourceFastViewTacticsSelectionError("unreached parent first callback must not be invented")
        first_row = None
    if type(inner_original_base_dispatch_result) is not int or not (
        0 <= inner_original_base_dispatch_result <= 0xFFFFFFFF
    ):
        raise SourceFastViewTacticsSelectionError("original reached inner base return required")
    inner = source_fastview_aux_child_input_outcome_651ac0(
        base_dispatch_result=inner_original_base_dispatch_result,
        native_selection_index=inner_original_native_selection_index,
        child_has_registered_event=registered,
        child_input_callback_argument_nonzero=original_child_second_callback_argument_nonzero,
    )
    slots = ((0x0C,) if first_reached else ()) + inner.source_parent_callbacks_from_this_child_route
    return OriginalFastViewX133InputRoute(
        first_reached, first_row, False, True, inner, slots
    )


# The authentic x133 child vft+0x98 0x52D120 allocates 0x18C bytes
# and calls native popup constructor 0x52D1F0(child+0x38). This does
# not show the popup, choose a row or prove pointer hit geometry.
# Its distinct vft+0x9C 0x52D190 constructs a context-relative
# screen clip by adding child x/y to parent x/y, then clamping the
# *right/bottom* against original 800x600. No negative-edge clipping
# is shown by the recovered native source; do not invent it.
SOURCE_FASTVIEW_X133_POPUP_FACTORY_VA = 0x52D120
SOURCE_FASTVIEW_X133_POPUP_FACTORY_ALLOC_BYTES = 0x18C
SOURCE_FASTVIEW_X133_POPUP_CONSTRUCTOR_VA = 0x52D1F0
SOURCE_FASTVIEW_X133_POPUP_FACTORY_CHILD_LIST_OFFSET = 0x38
SOURCE_FASTVIEW_X133_POPUP_DRAW_VA = 0x52D190
SOURCE_FASTVIEW_X133_POPUP_DRAW_VIRTUAL_PARENT_OFFSET = 0x24
SOURCE_FASTVIEW_X133_POPUP_DRAW_NATIVE_RECT = (800, 600)
SOURCE_FASTVIEW_X133_POPUP_DRAW_BLITTER_VA = 0x653320


def source_fastview_x133_popup_clip_52d190(
    *, child_x: int, child_y: int, parent_x: int, parent_y: int,
    context_x: int, context_y: int
) -> tuple[int, int, int, int]:
    """Reproduce only original vft+0x9C right/bottom clip arithmetic.

    Native source 0x52D190 reads parent via child+0x24, obtains child
    [+0x10,+0x0C] and parent [+0x0C,+0x10] component sums,
    uses context+0x70/+0x74 and caps resulting width against x=800
    and height against y=600. Its six-argument blitter 0x653320
    receives computed (width,height,context_x,context_y,4,1).
    Input coordinates are source-supplied signed DWORDs. This is
    neither mouse hit-testing nor popup item/selection geometry.
    """
    values = (child_x, child_y, parent_x, parent_y, context_x, context_y)
    if any(type(v) is not int or not -0x80000000 <= v <= 0x7FFFFFFF for v in values):
        raise SourceFastViewTacticsSelectionError("original signed coordinate DWORDs required")
    width = child_x + parent_x
    height = child_y + parent_y
    if context_x + width > 800:
        width = 800 - context_x
    if context_y + height > 600:
        height = 600 - context_y
    return (width, height, context_x, context_y)


# Native popup constructed at 0x52D1F0 has final vtable 0x7CAC64,
# whose +0x34 key handler 0x52D350 checks WORD 0x1B (Escape).
# It routes WORD 0xFFFF via 0x6539F0 -> 0x659650:
# 0x6539F0 masks to 16 bits, follows owner +0x64 and sends event
# message 0x400 through the external thunk pointer 0x7BD2D8.
# The destination/side effects of that thunk are NOT source qualified.
SOURCE_FASTVIEW_POPUP_VTABLE = 0x7CAC64
SOURCE_FASTVIEW_POPUP_KEY_CALLBACK_OFFSET = 0x34
SOURCE_FASTVIEW_POPUP_ESCAPE_HANDLER_VA = 0x52D350
SOURCE_FASTVIEW_POPUP_ESCAPE_KEY_WORD = 0x1B
SOURCE_FASTVIEW_POPUP_ESCAPE_SENTINEL = 0xFFFF
SOURCE_FASTVIEW_POPUP_EVENT_SENDER_VA = 0x6539F0
SOURCE_FASTVIEW_POPUP_EVENT_ROUTER_VA = 0x659650
SOURCE_FASTVIEW_POPUP_EVENT_CODE = 0x400


def source_fastview_popup_escape_event_value_only(*, original_key_word: int) -> int | None:
    """Only original 0x52D350's Escape dispatch, never modal cancellation.

    None means the original handler returns without this specific event.
    A returned WORD 0xFFFF means 0x6539F0 is called, NOT a proved menu
    close/lineup rollback or post-match navigation.
    """
    if type(original_key_word) is not int or not 0 <= original_key_word <= 0xFFFF:
        raise SourceFastViewTacticsSelectionError("original key WORD required")
    return (SOURCE_FASTVIEW_POPUP_ESCAPE_SENTINEL
            if original_key_word == SOURCE_FASTVIEW_POPUP_ESCAPE_KEY_WORD else None)


# Original popup final vtable 0x7CAC64 also has virtual+0x20
# 0x446690: a nonzero argument emits the SAME 0xFFFF via 0x6539F0
# as the Escape+0x34 handler. Both requests go through a queued
# Win32 PostMessageA(HWND, WM_USER=0x400, wParam=0xFFFF, lParam=0).
# Original import thunk 0x7BD2D8 is USER32.PostMessageA, not SendMessage.
# The +0x64 owner is dereferenced to get HWND at +0x04 by 0x659650.
# A separate original message-pump virtual 0x532B80 recognizes 0x400
# after GetMessageA and returns without Translate/DispatchMessage;
# actual reachability of that pump FROM x133 popup remains unproven.
SOURCE_FASTVIEW_POPUP_NONZERO_EVENT_METHOD_VA = 0x446690
SOURCE_FASTVIEW_POPUP_NONZERO_EVENT_METHOD_OFFSET = 0x20
SOURCE_FASTVIEW_POPUP_WIN32_POSTMESSAGE_IMPORT_VA = 0x7BD2D8
SOURCE_FASTVIEW_POPUP_MESSAGE_PUMP_FILTER_VA = 0x532B80
SOURCE_FASTVIEW_POPUP_EVENT_OWNER_POINTER_OFFSET = 0x64
SOURCE_FASTVIEW_POPUP_EVENT_OWNER_HWND_OFFSET = 0x04


@dataclass(frozen=True)
class SourceFastViewPopupPostedMessage:
    """Unsent native Win32 queue request; NEVER a completed modal action."""
    win32_message: int
    native_wparam_word: int
    native_lparam: int


def source_fastview_popup_posted_message_from_event(
    *, native_event_word: int
) -> SourceFastViewPopupPostedMessage:
    """Source 0x6539F0/0x659650 *request*, no window/process execution.

    This projects a posted message only; caller must separately have
    actual original +0x64 event owner and verified HWND; no user click,
    GUI close, state rollback or selected-index interpretation occurs.
    """
    if type(native_event_word) is not int or not 0 <= native_event_word <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("original unsigned native event DWORD required")
    return SourceFastViewPopupPostedMessage(
        win32_message=SOURCE_FASTVIEW_POPUP_EVENT_CODE,
        native_wparam_word=native_event_word & 0xFFFF,
        native_lparam=0,
    )


def source_fastview_popup_virtual20_posted_event_value_only(
    *, native_event_argument: int
) -> SourceFastViewPopupPostedMessage | None:
    """0x446690: nonzero DWORD generates asynchronous sentinel event."""
    if type(native_event_argument) is not int or not 0 <= native_event_argument <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("original callback argument DWORD required")
    if native_event_argument == 0:
        return None
    return source_fastview_popup_posted_message_from_event(native_event_word=0xFFFF)


# Source-closed for the x133 child built at screen+0x263C+0x44*row:
# 0x5D71A0 pushes GLOBAL 0x877960 as the eighth native constructor
# input, stored child+0x30 by 0x651A50. Global GUI object ctor
# 0x532570 installs vtable 0x7CB294. x133 0x651AC0 calls its vft+0x20
# 0x532650 with the newly built popup and zero. That calls 0x654210:
# it writes popup+0x64 event owner, invokes popup setup 0x6542B0,
# then invokes the original GUI object vft+0 0x532B80.
# 0x532B80 consumes GetMessageA WM_USER=0x400 and returns MSG.wParam
# without TranslateMessageA / DispatchMessageA; other messages use
# those functions and keep pumping. Popup Escape and virtual+0x20
# queue PostMessageA(hwnd,0x400,0xffff,0). 0x651AC0 compares its
# modal result against 0xffff to set child+0x40=1 (invalid) and skip
# the array-selected-index update. No match modal exit is implied.
SOURCE_FASTVIEW_X133_GLOBAL_UI_CONTROLLER_VA = 0x877960
SOURCE_FASTVIEW_X133_GLOBAL_UI_VTABLE = 0x7CB294
SOURCE_FASTVIEW_X133_GLOBAL_UI_MODAL_SLOT = 0x20
SOURCE_FASTVIEW_X133_GLOBAL_UI_MODAL_METHOD_VA = 0x532650
SOURCE_FASTVIEW_X133_UI_MODAL_WRAPPER_VA = 0x654210
SOURCE_FASTVIEW_X133_UI_MODAL_EVENT_PUMP_VA = 0x532B80
SOURCE_FASTVIEW_X133_UI_MODAL_POPUP_SETUP_VA = 0x6542B0
SOURCE_FASTVIEW_X133_UI_MODAL_RESULT_SENTINEL = 0xFFFF


@dataclass(frozen=True)
class SourceFastViewNativeDropdownModalResult:
    selected_index_dword: int
    invalid_selection_status_byte: int
    writes_selected_index: bool


def source_fastview_native_dropdown_posted_wm_user_result(
    *, native_message: int, native_wparam: int
) -> SourceFastViewNativeDropdownModalResult | None:
    """Source 0x532B80 -> 0x651AC0 for an already delivered WM_USER.

    None means non-WM_USER is dispatched normally and the modal keeps
    pumping (not a selected option). 0xFFFF means native child+0x40=1,
    no source array selection write. Other full DWORD results are stored
    in child+0x3C and mark status0. Actual list bounds, HWND lifetime,
    message delivery and parent callback remain separate source gates.
    """
    for value in (native_message, native_wparam):
        if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
            raise SourceFastViewTacticsSelectionError("native Win32 message DWORDs required")
    if native_message != SOURCE_FASTVIEW_POPUP_EVENT_CODE:
        return None
    if native_wparam == SOURCE_FASTVIEW_X133_UI_MODAL_RESULT_SENTINEL:
        return SourceFastViewNativeDropdownModalResult(0xFFFF, 1, False)
    return SourceFastViewNativeDropdownModalResult(native_wparam, 0, True)


# Next actual dropdown list ownership source after original PR670:
# human x133 0x52D120 allocates popup -> ctor 0x52D1F0
# writes child+0x38 list pointer into popup+0x68 at 0x52D21E.
# Ctor sets popup+0x70=0x96 (150) at 0x52D2A4, then calls
# original 0x449610 at 0x52D2AB (opcode e8 60 c3 f1 ff).
# 0x449610 computes popup+0x78=popup+0x70-6 (144), resets
# popup+0x6C list count, scans DWORD first entries at +8 bytes
# from list owner until DWORD0, and writes popup+0x74=15*N+3.
# This is *content dimension math*, NOT pointer hitboxes,
# text strings, scroll or item click / selection calculations.
SOURCE_FASTVIEW_POPUP_LIST_GEOMETRY_VA = 0x449610
SOURCE_FASTVIEW_POPUP_LIST_POINTER_OFFSET = 0x68
SOURCE_FASTVIEW_POPUP_OPTION_FIRST_DWORD_STRIDE = 8
SOURCE_FASTVIEW_POPUP_NATIVE_FRAME_WIDTH = 150
SOURCE_FASTVIEW_POPUP_INNER_CONTENT_WIDTH = 144
SOURCE_FASTVIEW_POPUP_OPTION_ROW_PITCH = 15
SOURCE_FASTVIEW_POPUP_OPTION_HEIGHT_ADDITION = 3
SOURCE_FASTVIEW_POPUP_NUMBER_OF_OPTIONS_OFFSET = 0x6C
SOURCE_FASTVIEW_POPUP_OPTIONS_HEIGHT_OFFSET = 0x74
SOURCE_FASTVIEW_POPUP_CONTENT_WIDTH_OFFSET = 0x78


@dataclass(frozen=True)
class SourceFastViewNativePopupOptionDimensions:
    native_count: int
    native_inner_width: int
    native_height: int


def source_fastview_native_popup_option_dimensions_449610(
    *, list_first_dwords_with_null: tuple[int, ...]
) -> SourceFastViewNativePopupOptionDimensions:
    """Project only native 0x449610 sentinel count and dimensions.

    Input must represent the exact original list+8*i first DWORD at
    each 8-byte record, including a single NULL terminal. The original
    scans until the first NULL. Fail closed for truncated/noncanonical
    input instead of dereferencing arbitrary host pointers. No GUI
    position, selection-index or clickable-row assumption is made.
    """
    if (type(list_first_dwords_with_null) is not tuple or
            not list_first_dwords_with_null):
        raise SourceFastViewTacticsSelectionError("native terminated option records required")
    if any(type(d) is not int or d < 0 or d > 0xFFFFFFFF
           for d in list_first_dwords_with_null):
        raise SourceFastViewTacticsSelectionError("original list-entry DWORDs required")
    if list_first_dwords_with_null[-1] != 0 or 0 in list_first_dwords_with_null[:-1]:
        raise SourceFastViewTacticsSelectionError(
            "original native option inventory must end with exactly one sentinel"
        )
    count = len(list_first_dwords_with_null) - 1
    if count > (0x7FFFFFFF - SOURCE_FASTVIEW_POPUP_OPTION_HEIGHT_ADDITION)//15:
        raise SourceFastViewTacticsSelectionError(
            "unqualified original native 32-bit option height overflow"
        )
    return SourceFastViewNativePopupOptionDimensions(
        native_count=count,
        native_inner_width=SOURCE_FASTVIEW_POPUP_INNER_CONTENT_WIDTH,
        native_height=SOURCE_FASTVIEW_POPUP_OPTION_ROW_PITCH * count
                      + SOURCE_FASTVIEW_POPUP_OPTION_HEIGHT_ADDITION,
    )


# The original popup vtable+4 0x449300 creates native nested list at
# popup+0x13C (vtable 0x7BFD5C). At 0x449434..0x449457 it invokes
# nested virtual+B0=0x446740 with live popup+0x68 source list, N
# computed at +0x6C, child+0x78 width, row pitch 15, record stride 8,
# and content height 15*N. Adapter 0x446740 calls 0x6510F0, which
# allocates 4+48*N bytes for N native row child records, constructor
# 0x651280 (vtable 0x7D8118), stores child+0x64=parent list, and
# child+0x68=parent+0x3C native index base + ordinal. This is not
# evidence for screen-space hit rectangles or delivery order.
SOURCE_FASTVIEW_POPUP_NESTED_LIST_PARENT_OFFSET = 0x13C
SOURCE_FASTVIEW_POPUP_NESTED_LIST_VTABLE = 0x7BFD5C
SOURCE_FASTVIEW_POPUP_NESTED_LIST_SETUP_SLOT = 0xB0
SOURCE_FASTVIEW_POPUP_NESTED_LIST_SETUP_ADAPTER_VA = 0x446740
SOURCE_FASTVIEW_POPUP_NESTED_LIST_ALLOCATOR_VA = 0x6510F0
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_ROW_CONSTRUCTOR_VA = 0x651280
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_ROW_VTABLE = 0x7D8118
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_ROW_SIZE = 0x30
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_ROW_ARRAY_COUNT_HEADER = 4
SOURCE_FASTVIEW_POPUP_OPTION_CHILD_NATIVE_INDEX_OFFSET = 0x68
SOURCE_FASTVIEW_POPUP_OPTION_CHILD_OWNER_OFFSET = 0x64


@dataclass(frozen=True)
class SourceFastViewPopupNativeOptionRow:
    ordinal: int
    native_row_blob_byte_offset: int
    native_callback_index: int


def source_fastview_popup_native_option_rows_6510f0(
    *, native_option_count: int, native_first_index: int
) -> tuple[SourceFastViewPopupNativeOptionRow, ...]:
    """Read-only native constructed-row identities without click inference.

    Native 0x6510F0 creates 0x30-byte children in ordinal order,
    assigning each child+0x68 = parent+0x3C + ordinal. For the x133
    popup, the source +8 record stride and 15px nominal pitch are
    supplied earlier by original 0x449300/0x446740, not generated here.
    """
    if type(native_option_count) is not int or not 0 <= native_option_count <= (0x7FFFFFFF - 4)//0x30:
        raise SourceFastViewTacticsSelectionError("qualified native option row count required")
    if type(native_first_index) is not int or not 0 <= native_first_index <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("original native row index base DWORD required")
    if native_first_index + native_option_count > 0x100000000:
        raise SourceFastViewTacticsSelectionError("unqualified native row index DWORD overflow")
    return tuple(
        SourceFastViewPopupNativeOptionRow(
            ordinal=i,
            native_row_blob_byte_offset=4+i*0x30,
            native_callback_index=native_first_index+i,
        )
        for i in range(native_option_count)
    )


# Original native popup option *activation* source (not pixel hit):
# 0x6510F0's vft+0x9C 0x449470 constructs each rich option at
# +0x17C bytes and stores list_parent+0x4C option data item pointer
# +8*row_index into the option object+0x70. Its final class vtable
# 0x7C0334 has vft+0x10=0x653A10. The original 0x6511B4 writes
# option+0x68 = list_parent+0x3C + ordinal. At 0x653A10 a NONZERO
# callback argument (DWORD) loads the *WORD* at item+0x68, follows
# item+0x08 list-parent pointer then owner+0x24 popup pointer, and
# invokes 0x6539F0. That method POSTS WM_USER=0x400 and native WORD
# index to the parent modal, which returns this index to 0x651AC0.
# No pixel hit-testing, event timing or actual mouse transport proven.
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_FACTORY_VA = 0x449470
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_ALLOC_BYTES = 0x17C
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_VTABLE = 0x7C0334
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_EVENT_VFT_OFFSET = 0x10
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_EVENT_METHOD_VA = 0x653A10
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_SOURCE_ITEM_POINTER_OFFSET = 0x70
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_INDEX_DWORD_OFFSET = 0x68
SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_LIST_PARENT_OFFSET = 0x08
SOURCE_FASTVIEW_POPUP_LIST_TO_POPUP_OWNER_OFFSET = 0x24


@dataclass(frozen=True)
class SourceFastViewOriginalPopupOptionActivation:
    native_option_ordinal: int
    source_item_record_byte_offset: int
    native_option_index_dword: int
    posted_wm_user: SourceFastViewPopupPostedMessage | None


def source_fastview_original_popup_option_activation_653a10(
    *, original_option_ordinal: int,
    original_list_index_base: int,
    original_option_count: int,
    native_callback_argument: int,
) -> SourceFastViewOriginalPopupOptionActivation:
    """Source-bounded row-object callback result, NOT mouse hit inference.

    The native vft+0x10 callback posts only when its input argument
    is nonzero. On activation the original item+0x68 DWORD is read as
    a WORD (selected index wraps modulo 2^16) before calling 0x6539F0.
    The list item data pointer is list+8*ordinal. Must independently
    prove a real HWND and pointer/controller route to deliver the
    POST; this function does not send an event or edit a match.
    """
    values=(original_option_ordinal,original_list_index_base,
            original_option_count,native_callback_argument)
    if any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in values):
        raise SourceFastViewTacticsSelectionError("original option callback DWORDs required")
    if original_option_count > (0x7FFFFFFF-4)//SOURCE_FASTVIEW_POPUP_NATIVE_OPTION_ROW_SIZE:
        raise SourceFastViewTacticsSelectionError("native child-array size overflow")
    if original_option_ordinal >= original_option_count:
        raise SourceFastViewTacticsSelectionError("original item ordinal outside list")
    if original_list_index_base+original_option_ordinal > 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("original child index DWORD overflow")
    source_index=original_list_index_base+original_option_ordinal
    posted=(source_fastview_popup_posted_message_from_event(
        native_event_word=source_index & 0xFFFF)
        if native_callback_argument else None)
    return SourceFastViewOriginalPopupOptionActivation(
        native_option_ordinal=original_option_ordinal,
        source_item_record_byte_offset=8*original_option_ordinal,
        native_option_index_dword=source_index,
        posted_wm_user=posted,
    )


# Original native nested option list vtable 0x7BFD5C+0x6C=0x6516F0
# pointer receiver: invokes 0x64F7A0 with a zero second argument,
# then scans its 0x30-byte row descriptor array in ordinal order.
# Per row: x >= DWORD+8 and x < DWORD+0x10 and
#          y >= DWORD+0x0C and y < DWORD+0x14.
# Only FIRST such row is forwarded to that row's vft+0x6C,
# 0x650F00. If no row matches, returns EAX=0. The receiving
# 0x650F00 has additional owner/event gating and a separate
# 0x650C30 callback; matching the rectangle alone is NOT a click
# or a source-approved PostMessageA selected-index event.
SOURCE_FASTVIEW_POPUP_POINTER_LIST_DISPATCH_VA = 0x6516F0
SOURCE_FASTVIEW_POPUP_ROW_POINTER_DISPATCH_VA = 0x650F00
SOURCE_FASTVIEW_POPUP_ROW_VTABLE_POINTER_CALLBACK_OFFSET = 0x6C
SOURCE_FASTVIEW_POPUP_ROW_RECT_STRIDE = 0x30
SOURCE_FASTVIEW_POPUP_ROW_LEFT_OFFSET = 0x08
SOURCE_FASTVIEW_POPUP_ROW_TOP_OFFSET = 0x0C
SOURCE_FASTVIEW_POPUP_ROW_RIGHT_OFFSET = 0x10
SOURCE_FASTVIEW_POPUP_ROW_BOTTOM_OFFSET = 0x14


@dataclass(frozen=True)
class SourceFastViewPopupOriginalRowHitRectangle:
    x_left: int
    y_top: int
    x_right: int
    y_bottom: int


def source_fastview_popup_first_native_row_hit_6516f0(
    *, pointer_x: int, pointer_y: int,
    ordered_native_row_rects: tuple[SourceFastViewPopupOriginalRowHitRectangle, ...],
) -> int | None:
    """Source-only original first matching rectangle *owner*, not click.

    0x6516F0 dispatches only first matching ordinal to row vft+0x6C.
    The physical source of pointer coordinates, child enable flags,
    original 0x650F00 and true item click-to-selection callback
    still need independent source proof.
    """
    if (type(pointer_x) is not int or type(pointer_y) is not int or
            any(not -0x80000000 <= v <= 0x7FFFFFFF for v in (pointer_x,pointer_y))):
        raise SourceFastViewTacticsSelectionError("native signed pointer DWORD coordinates required")
    if type(ordered_native_row_rects) is not tuple:
        raise SourceFastViewTacticsSelectionError("source row descriptor tuple required")
    for i,rect in enumerate(ordered_native_row_rects):
        if type(rect) is not SourceFastViewPopupOriginalRowHitRectangle:
            raise SourceFastViewTacticsSelectionError("original native row rectangle type required")
        coords=(rect.x_left,rect.y_top,rect.x_right,rect.y_bottom)
        if any(type(v) is not int or not -0x80000000 <= v <= 0x7FFFFFFF for v in coords):
            raise SourceFastViewTacticsSelectionError("native signed row boundary DWORDs required")
        if (pointer_x >= rect.x_left and pointer_x < rect.x_right and
                pointer_y >= rect.y_top and pointer_y < rect.y_bottom):
            return i
    return None


# Source-closed conditional native rich row pointer callback:
# 0x4491A0 registers exactly ONE input nested child +0x13C, final
# vtable 0x7BE340; child vft+8=0x64F3C0 invoked at 0x4492B1
# with event-enabled=1 and rich-row parent as owner, so
# child+0x20=1 and child+0x24=row item. Child native 0x64F300 ctor
# sets flags +0x18=0x183 (bit1 enabled; bit4 clear).
# Actual row vft+0x6C 0x650F00 -> base 0x650C30 routes pointer
# to rich item 0x653480: loops registered child ptrs at item+0x20
# (count item+0x3C=1) and checks bit0 of child's +0x18 and
# half-open rectangle on pointer normalized by item+0x0C/+0x10.
# On accepted hit 0x653480 passes SECOND callback arg ONE into
# child vft+0x6C=0x64F7A0. That gated base calls item parent
# vft+0x0C=0x42DE00 (RET 1), then parent vft+0x10=0x653A10
# to PostMessageA selected index (verified merged PR671).
# The other rich item child+0x10C is registered with event=0;
# source does not equate all graphics controls to clickable items.
SOURCE_FASTVIEW_POPUP_RICH_ROW_SETUP_VA = 0x4491A0
SOURCE_FASTVIEW_POPUP_RICH_ROW_ACTIVE_CONTROL_OFFSET = 0x13C
SOURCE_FASTVIEW_POPUP_RICH_ROW_ACTIVE_CONTROL_VTABLE = 0x7BE340
SOURCE_FASTVIEW_POPUP_RICH_ROW_ACTIVE_CONTROL_REGISTERED_EVENT = 1
SOURCE_FASTVIEW_POPUP_RICH_ROW_ACTIVE_CONTROL_NATIVE_FLAGS = 0x183
SOURCE_FASTVIEW_POPUP_RICH_ROW_POINTER_FORWARDER_VA = 0x653480
SOURCE_FASTVIEW_POPUP_RICH_ROW_FIRST_CALLBACK_VA = 0x42DE00
SOURCE_FASTVIEW_POPUP_RICH_ROW_ACTIVE_POINTER_SECOND_ARG = 1


def source_fastview_original_popup_rich_row_child_pointer_gate(
    *, pointer_x: int, pointer_y: int,
    rich_item_origin_x: int, rich_item_origin_y: int,
    active_child_rectangle: SourceFastViewPopupOriginalRowHitRectangle,
    native_child_flags: int,
    native_child_registered_event: int,
) -> bool:
    """Read-only native 0x653480 +0x64F7A0 enabled pointer callback gates.

    Does not derive a rectangle from the original 15px content pitch.
    The native rich item origin and actual nested child rectangle MUST
    come from source-qualified live controls, not fabricated screen
    positions. A True only proves enabled nested child vft+0x6C gets
    a nonzero callback argument; it DOES NOT send mouse/Win32 events.
    """
    values=(pointer_x,pointer_y,rich_item_origin_x,rich_item_origin_y)
    if any(type(v) is not int or not -0x80000000 <= v <= 0x7FFFFFFF for v in values):
        raise SourceFastViewTacticsSelectionError("original signed pointer/origin DWORDs required")
    if type(native_child_flags) is not int or not 0 <= native_child_flags <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("original native child flags DWORD required")
    if type(native_child_registered_event) is not int or not 0 <= native_child_registered_event <= 0xFFFFFFFF:
        raise SourceFastViewTacticsSelectionError("original native child registered event DWORD required")
    if type(active_child_rectangle) is not SourceFastViewPopupOriginalRowHitRectangle:
        raise SourceFastViewTacticsSelectionError("native child rectangle type required")
    coords=(active_child_rectangle.x_left,active_child_rectangle.y_top,
            active_child_rectangle.x_right,active_child_rectangle.y_bottom)
    if any(type(v) is not int or not -0x80000000 <= v <= 0x7FFFFFFF for v in coords):
        raise SourceFastViewTacticsSelectionError("original native child boundary DWORDs required")
    if not (native_child_flags & 1):
        return False
    x=pointer_x-rich_item_origin_x
    y=pointer_y-rich_item_origin_y
    if not (active_child_rectangle.x_left <= x < active_child_rectangle.x_right and
            active_child_rectangle.y_top <= y < active_child_rectangle.y_bottom):
        return False
    # Nested base 0x64F7A0 requires bit1 enabled, bit4 clear and
    # nonzero child+0x20 for parent callbacks. The original second
    # callback input is nonzero (1), and rich item first +0x0C
    # returns one unconditionally as 0x42DE00.
    return bool((native_child_flags & 2) and not (native_child_flags & 0x10)
                and native_child_registered_event)
