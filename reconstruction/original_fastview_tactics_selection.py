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


@dataclass(frozen=True)
class SourceFastViewAuxChildInputOutcome:
    """Only the reached 0x651AC0 fields; no GUI event inferred."""
    source_handled: bool
    source_status_byte: int | None
    source_saved_selected_index: int | None
    native_parent_second_callback_reached: bool


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


# 0x633240 counts original staged edit nodes via the polymorphic vft+4
# visitor. The original base record virtual +4 is NOT a benign no-op;
# vft 0x7D7F90 (0x6335D0 replacement record) +4 -> 0x633600,
# forwards to count-visitor vft 0x7D803C+4 -> 0x634E40.
# 0x633020 returns AL==0 *when this count is zero*; for nonzero
# staged edits it executes the original 0x6331A0/0x634B00 visitor that
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
    """Read-only 0x633020 AL when authentic staged replacement list empty.

    Source 0x633020 first calls 0x633240 and checks EAX==0 at 0x63304E.
    The zero-count path branches to 0x63317E and returns AL=0. This is
    independent of earlier child status and dropdown event dispatch.
    A positive node count MUST NOT be modeled as AL=0/1 here: it needs
    complete original polymorphic replay and a valid list identity.
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
