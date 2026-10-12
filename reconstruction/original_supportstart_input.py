"""Source-bounded original PSupportStart row bit15 interaction and dispatch flags.

Based on original footballmanager.exe SHA-256 833bf95e...b7cc3.
- Seven native rows, five children registered via 0x5D4580 at 0x4C9486.
- Row +0x98 = 0x5D6200, row +0x6C = 0x5D6270.
- Accepted 0x5D4790 input flips bit15, but physical hit ownership is not proven.
- 0x4D0830 stores the inverse bit15 as the selected-record byte.

This is an isolated native-control transition for a VERIFIED upstream event
result, not a mouse-coordinate predictor, full editor or Apply transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from support_staff import original_supportstart_flag_after_selector_state

ORIGINAL_ROW_PARENT_VTABLE = 0x7C6780
ORIGINAL_ROW_CHILD_OFFSETS = (0x38, 0x3C, 0x40, 0x44, 0x48)
# Actual final vtables, not initial constructor-base temporary vtable.
ORIGINAL_ROW_CHILD_VTABLES = (0x7BE9BC, 0x7C66C8, 0x7C66C8, 0x7BE530, 0x7BFF14)
ORIGINAL_ROW_REGISTRATION_FLAGS = (0x33, 0x31, 0x31, 0x15, 0x15)
ORIGINAL_ROW_STATE_MASK = 0x8000
ORIGINAL_ROW_CHILD_STATE_FLAG = 0x20
ORIGINAL_ROW_CHILD_INPUT_FLAG = 0x04


def _dword(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("Original control flags must be unsigned DWORD")
    return value


@dataclass(frozen=True)
class OriginalSupportStartRowBitState:
    """Native row+five child DWORD bitsets, not presentation geometry."""
    parent: int
    children: tuple[int, int, int, int, int]

    def __post_init__(self) -> None:
        _dword(self.parent)
        if type(self.children) is not tuple or len(self.children) != 5:
            raise ValueError("Original SupportStart row has five registered children")
        for state in self.children:
            _dword(state)

    @property
    def stored_staff_selection_byte_if_applied(self) -> int:
        """Native 0x4D0830 persists inverse row bit15, not child bit15."""
        return original_supportstart_flag_after_selector_state(self.parent)


def original_supportstart_row_set_bit15(
    row: OriginalSupportStartRowBitState, enabled: bool,
) -> OriginalSupportStartRowBitState:
    """Original 0x5D6200 sets/clears parent + ONLY child flags & 0x20.

    Other bits survive. This function simulates a bounded source transition;
    it does not synthesize native redraw callback side effects.
    """
    if type(row) is not OriginalSupportStartRowBitState or type(enabled) is not bool:
        raise TypeError("Require an original row state and explicit Boolean")

    def update(dword: int) -> int:
        return (dword | ORIGINAL_ROW_STATE_MASK if enabled
                else dword & ~ORIGINAL_ROW_STATE_MASK)

    return OriginalSupportStartRowBitState(
        update(row.parent),
        tuple(update(child) if flag & ORIGINAL_ROW_CHILD_STATE_FLAG else child
              for child, flag in zip(row.children, ORIGINAL_ROW_REGISTRATION_FLAGS)),
    )


def original_supportstart_row_refresh(
    row: OriginalSupportStartRowBitState, selected_byte: int,
) -> OriginalSupportStartRowBitState:
    """0x4D0796: source selected_byte == 0 becomes row bit15 set.

    Uninitialized empty record bytes have not been established; forbid None.
    """
    if type(selected_byte) is not int or not 0 <= selected_byte <= 255:
        raise ValueError("Native selected byte must be an initialized byte")
    return original_supportstart_row_set_bit15(row, selected_byte == 0)


def original_supportstart_row_native_event(
    row: OriginalSupportStartRowBitState, accepted_by_native_gate: bool,
) -> OriginalSupportStartRowBitState:
    """0x5D6270 toggles bit15 after a *verified* 0x5D4790 acceptance.

    Caller must establish native input acceptance; it is NOT inferred from
    reconstructed geometry or a hypothetical mouse click.
    """
    if type(row) is not OriginalSupportStartRowBitState or type(accepted_by_native_gate) is not bool:
        raise TypeError("Require an original row and an explicit native-gate result")
    if not accepted_by_native_gate:
        return row
    return original_supportstart_row_set_bit15(
        row, not bool(row.parent & ORIGINAL_ROW_STATE_MASK)
    )


@dataclass(frozen=True)
class OriginalSupportStartRowNativeDispatchObservation:
    """Exact source call order, with caller-observed callback results only.

    Parent virtual+0x6C runs when the second native event argument is
    nonnull. It is allowed to accept the row WITHOUT any eligible child.
    Children are still iterated after parent acceptance; if the parent
    rejects, 0x5D4790 RETURNS EARLY without visiting any child.
    """
    parent_invoked: bool
    parent_accepted: bool | None
    invoked_child_indices: tuple[int, ...]
    observed_child_acceptances: tuple[bool, ...]
    early_parent_reject: bool
    native_handler_accepted: bool
    source_row_before: OriginalSupportStartRowBitState
    # Original native selector identity supplied by the owner, never DWORD guesses.
    source_row_index: int | None
    source_post_virtual_gate_row: OriginalSupportStartRowBitState

    @property
    def source_after_row_bit15_toggle(self) -> OriginalSupportStartRowBitState:
        """0x5D6270: after all accepted source +0x6C calls, flip bit15.

        The earlier accepted 0x64F7A0 calls source virtual+0x1C(1),
        setting state bit0x10 on the *accepted* native control.
        Then 0x5D6270 calls row virtual+0x98 only for nonzero result.
        Does not model optional opaque input/global callbacks.
        """
        return original_supportstart_row_native_event(
            self.source_post_virtual_gate_row, self.native_handler_accepted
        )


def project_original_supportstart_row_native_dispatch(
    row: OriginalSupportStartRowBitState,
    *,
    native_second_argument_present: bool,
    observed_parent_acceptance: bool | None,
    observed_child_acceptances: tuple[bool, ...],
    source_row_index: int | None = None,
) -> OriginalSupportStartRowNativeDispatchObservation:
    """Source 0x5D6270 -> 0x5D4790 parent/children acceptance order.

    Original 0x5D479B tests whether *second event argument* is nonnull.
    If so 0x5D47A5 calls 0x64F7A0 on the PARENT. A false return at
    0x5D47AC exits immediately, regardless of child state. A true
    parent result is ORed with child vft+0x6C results at 0x5D47EB.
    Crucially, parent alone may accept: child candidates are NOT
    necessary for row toggle. Native 0x5D6270 toggles bit15 when the
    final 0x5D4790 result is nonzero.

    Source 0x5D47CA requires registered child flag bit0x04, then
    0x64F570 requires child state bit0. Every such child has its
    virtual+0x6C invoked, even if its base 0x64F7A0 state bits
    (bit1 set / bit0x10 clear) require it to return 0. External
    +0x24 hit-object callbacks remain UNKNOWN. Results here are
    caller observations, not invented physical mouse acceptance,
    side-effect execution, source CRT draws, or gameplay mutations.
    Optional `source_row_index` must be supplied by the actual native
    row owner, not inferred from equal DWORD values or mouse geometry.
    The returned source-post-virtual-gate DWORDs project ONLY the direct
    vft+0x1C(1) state bit0x10 set in accepted parent/children; additional
    source callback state mutations must be qualified separately.
    """
    if type(row) is not OriginalSupportStartRowBitState:
        raise TypeError("Require exact original five-child row state")
    if source_row_index is not None and (
        type(source_row_index) is not int or not 0 <= source_row_index < 7
    ):
        raise ValueError("Native selector row index must be a source-owned 0..6 identity")
    if type(native_second_argument_present) is not bool:
        raise TypeError("Native event-pointer presence requires Boolean")
    if type(observed_child_acceptances) is not tuple or any(
        type(x) is not bool for x in observed_child_acceptances
    ):
        raise TypeError("Each actual native child callback return requires Boolean")
    if native_second_argument_present:
        if type(observed_parent_acceptance) is not bool:
            raise TypeError("Native parent callback result must be explicit")
        if observed_parent_acceptance and (
            not row.parent & 0x0002 or row.parent & 0x0010
        ):
            raise ValueError("Parent cannot accept with original base control gate closed")
        if not observed_parent_acceptance:
            if observed_child_acceptances:
                raise ValueError("Native parent rejection short-circuits all children")
            return OriginalSupportStartRowNativeDispatchObservation(
                True, False, (), (), True, False, row, source_row_index, row
            )
    elif observed_parent_acceptance is not None:
        raise ValueError("Native parent cannot report result when not invoked")
    invoked = tuple(
        i for i, (registration, control) in enumerate(
            zip(ORIGINAL_ROW_REGISTRATION_FLAGS, row.children)
        )
        if registration & ORIGINAL_ROW_CHILD_INPUT_FLAG and control & 0x0001
    )
    if len(observed_child_acceptances) != len(invoked):
        raise ValueError("Exactly one explicit callback result per invoked child required")
    for index, accepted in zip(invoked, observed_child_acceptances):
        control = row.children[index]
        if accepted and (not control & 0x0002 or control & 0x0010):
            raise ValueError("Original child cannot accept with bit1 clear or bit4 set")
    # 0x64F7A0 on acceptance invokes native vft+0x1C(1) ->
    # 0x64F470 -> 0x64F710; this sets control DWORD bit0x10.
    # The first row vft+0x98 bit15 toggle happens only AFTER this.
    child_bits = list(row.children)
    for index, accepted in zip(invoked, observed_child_acceptances):
        if accepted:
            child_bits[index] |= 0x0010
    post_gate = OriginalSupportStartRowBitState(
        row.parent | (0x0010 if observed_parent_acceptance is True else 0),
        tuple(child_bits),
    )
    return OriginalSupportStartRowNativeDispatchObservation(
        native_second_argument_present, observed_parent_acceptance,
        invoked, observed_child_acceptances, False,
        (observed_parent_acceptance is True or any(observed_child_acceptances)),
        row, source_row_index, post_gate,
    )


def original_supportstart_fifth_child_native_rect(row_index: int) -> tuple[int, int, int, int]:
    """Source fifth child +0x48 native (x,y,w,h), not a proven hit area.

    Original 0x4C9510 calls 0x652400 with row x+0xE6,
    row y+0x15, width0x5F, height0x0F. The first four
    arguments are forwarded unchanged through 0x651F00,
    0x651E90, 0x651BF0 to native rectangle setter 0x64F380.
    No parent coordinate transform or actual input capture is inferred.
    """
    if type(row_index) is not int or not 0 <= row_index < 7:
        raise ValueError("Source support row must be 0 through 6")
    return (621, 202 + 40*row_index, 95, 15)


def original_supportstart_teamselect_modal_entry(
    native_teamselect_control_dword: int,
    accepted_by_native_64f960: bool,
) -> bool:
    """TeamSelect source 0x4D91C0 entry predicate for 0x450BB0 modal.

    Native 0x64F960 must accept its full event context AND the source
    TeamSelect control bit15 must be set (getter 0x652F80).
    The original 0x64F960 first requires bit0x2 set and bit0x20 clear,
    independent of subsequent native owner/input callbacks. Actual hit/event
    routing is not reconstructed by this predicate; neither step can be guessed.
    """
    _dword(native_teamselect_control_dword)
    if type(accepted_by_native_64f960) is not bool:
        raise TypeError("TeamSelect native 0x64F960 result must be explicit Boolean")
    return (accepted_by_native_64f960
            and bool(native_teamselect_control_dword & 0x0002)
            and not bool(native_teamselect_control_dword & 0x0020)
            and bool(native_teamselect_control_dword & ORIGINAL_ROW_STATE_MASK))


def original_supportstart_source_dispatch_candidates(
    row: OriginalSupportStartRowBitState,
) -> tuple[int, ...]:
    """Necessary child virtual-acceptance gates, NOT whole-row acceptance.

    Source first requires registered child flags bit0x04 and native
    0x64F570 bit0x01; for the actual last two source child vtables,
    virtual+0x6C points to native 0x64F7A0 which additionally requires
    child control bit0x02 set, bit0x10 clear. Subsequent native event
    predicates and parent callback may still reject: returning an index
    here does NOT establish a mouse hit or accepted row toggle. Also,
    0x5D4790 calls the parent FIRST when event argument2 is nonnull;
    a parent acceptance alone can toggle the row even if this tuple is empty.
    """
    if type(row) is not OriginalSupportStartRowBitState:
        raise TypeError("Require an original row with five child control DWORDs")
    return tuple(
        i for i, (flags, child) in enumerate(
            zip(ORIGINAL_ROW_REGISTRATION_FLAGS, row.children)
        )
        if (flags & ORIGINAL_ROW_CHILD_INPUT_FLAG)
        and (child & 0x0001)
        and (child & 0x0002)
        and not (child & 0x0010)
    )


@dataclass(frozen=True)
class OriginalSupportStartTeamSelectEventOutcome:
    """Original 0x4D91C0 return is the input acceptance, not modal outcome."""
    native_handler_return: int
    modal_called: bool
    modal_result_byte: int | None


def original_supportstart_teamselect_event_outcome(
    native_64f960_accepted: bool,
    native_control_dword: int,
    modal_result_byte: int | None,
) -> OriginalSupportStartTeamSelectEventOutcome:
    """Model 0x4D91C0 -> 0x450BB0 -> 0x4D922C with explicit inputs.

    Native 0x450BB0 yields the modal's 0/1 result; caller 0x4D922C
    discards EAX and restores EBX from 0x64F960 as its handler return.
    The modal itself performs staff/name Apply or Cancel effects
    separately; this function does NOT simulate those mutations.
    """
    if type(native_64f960_accepted) is not bool:
        raise TypeError("Require an actual source input acceptance result")
    _dword(native_control_dword)
    called = original_supportstart_teamselect_modal_entry(
        native_control_dword, native_64f960_accepted
    )
    if called:
        if type(modal_result_byte) is not int or modal_result_byte not in (0, 1):
            raise ValueError("Called original modal must return a source result byte 0 or 1")
    elif modal_result_byte is not None:
        raise ValueError("No original modal could return a result on a rejected route")
    return OriginalSupportStartTeamSelectEventOutcome(
        int(native_64f960_accepted), called, modal_result_byte
    )


SOURCE_ORIGINAL_CONTROL_INIT_DWORD = 0x183


def original_supportstart_fresh_native_row() -> OriginalSupportStartRowBitState:
    """Constructor-time row and child control DWORDs, before row setup.

    Exact original 0x64F300 initializes control+0x18 to 0x183.
    PSupportStart row 0x4C9340 -> 0x5D45B0 -> 0x64F300,
    first three 0x42DE80 -> 0x64F300 and last two direct
    0x64F300. This describes the constructor, not a promised
    final state after all setup and source selection refresh.
    """
    return OriginalSupportStartRowBitState(
        SOURCE_ORIGINAL_CONTROL_INIT_DWORD,
        (SOURCE_ORIGINAL_CONTROL_INIT_DWORD,) * 5,
    )


def original_supportstart_empty_row_after_refresh(
    row: OriginalSupportStartRowBitState,
) -> OriginalSupportStartRowBitState:
    """Native 0x4D07B0 empty-row branch, exact child and parent flag effects.

    Source 0x4D07CB row virtual+0x3C -> 0x64F540 -> virtual+0x10
    -> 0x4C97A0(0) -> fifth child virtual+0x0C -> 0x64F3E0(0):
    clear bits0x8 and0x1 on fifth child. 0x4C97A0 then invokes
    0x5D4940(0), which invokes virtual+0x10 for all five children
    and 0x64F410(0) on parent, clearing bit0x02 on all six.
    This captures control flags only, not drawing or pointer hit geometry.
    """
    if type(row) is not OriginalSupportStartRowBitState:
        raise TypeError("Require five-child source native row state")
    children = list(row.children)
    children[4] &= ~(0x0008 | 0x0001)
    children = [child & ~0x0002 for child in children]
    return OriginalSupportStartRowBitState(
        row.parent & ~0x0002, tuple(children)
    )


def original_supportstart_initial_seven_rows(
    source_slots: tuple,
) -> tuple[OriginalSupportStartRowBitState, ...]:
    """Source 0x4D06B0: seven original staff rows without fabricating staff.

    A non-null source staff pointer invokes original 0x5D6200 with
    (original_selected_byte == 0). A null source staff pointer invokes
    0x4C9830 with empty labels/rating and then vft+0x3C disabling
    native input, without ever reading the uninitialized selected byte.
    This function constructs original CONTROL state only, not GUI.
    """
    from support_staff import OriginalSupportStartSourceSlot

    if (type(source_slots) is not tuple or len(source_slots) != 7
            or any(type(item) is not OriginalSupportStartSourceSlot
                   or item.index != i for i, item in enumerate(source_slots))):
        raise ValueError("Expected seven original ordered support source slots")
    results = []
    for slot in source_slots:
        row = original_supportstart_fresh_native_row()
        if slot.staff is None:
            results.append(original_supportstart_empty_row_after_refresh(row))
        else:
            results.append(original_supportstart_row_refresh(
                row, slot.original_selected_byte
            ))
    return tuple(results)


def original_teamselect_native_private_staff_record_address(
    *,
    teamselect_owner_va: int,
    pressed_control_va: int,
    source_group_start: int,
    source_group_end: int,
) -> int:
    """0x4D9240: map a native TeamSelect 0x40-stride control to 0x30 record.

    Exact arithmetic from the shipped executable:
      record = owner - 0x310 + 0x30 * (
          ((control - owner - 0x2EE4) >> 6)
          + 24 * (group_end - group_start)
      )
    Native SAR floors negative/misaligned values, but these are not
    proven legal source control pointers. Fail closed on them here.
    The parameters are source object addresses/field VALUES, not GUI x/y,
    club IDs or a manager index; this never creates a missing source user.
    """
    for arg in (teamselect_owner_va, pressed_control_va, source_group_start, source_group_end):
        _dword(arg)
    relative = pressed_control_va - teamselect_owner_va - 0x2EE4
    delta = source_group_end - source_group_start
    if relative < 0 or relative % 0x40 != 0 or delta < 0:
        raise ValueError("Unqualified source native TeamSelect record pointer")
    result = teamselect_owner_va - 0x310 + 0x30 * ((relative >> 6) + 24 * delta)
    if not 0 <= result <= 0xFFFFFFFF:
        raise ValueError("Source TeamSelect private record address out of DWORD")
    return result
