"""Original FastView 0x510C30 live event human-club pointer ownership.

Owner-authorized shipped footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
STATIC ORIGINAL PE32 DISASSEMBLY ONLY; original executable NOT launched.

The original at 0x510C30 reads DWORD human count global 0x8755E4.
For each manager index it calls the global user linked list accessor
0x413B10 on owner 0x874C10. That accessor returns a DBRUser pointer;
0x510C30 reads actual user+0x5B4 CLUB POINTER, and compares it with
the ACTUAL club object pointers returned by event+0x14 and event+0x28
virtual +0 accessors. If either pointer matches ANY manager's club
pointer, it returns AL=1; otherwise AL=0. It does NOT compare club
names, reconstruct club IDs, privilege only the first manager or check
whether the match result is known. Exact original pointer identity is
caller-supplied here; no original heap simulated.
"""
from __future__ import annotations

from dataclasses import dataclass

SOURCE_FASTVIEW_EVENT_HUMAN_PREDICATE_VA = 0x510C30
SOURCE_FASTVIEW_EVENT_HUMAN_COUNT_GLOBAL_VA = 0x8755E4
SOURCE_FASTVIEW_EVENT_NATIVE_MANAGER_OWNER_VA = 0x874C10
SOURCE_FASTVIEW_EVENT_MANAGER_BY_ORDINAL_VA = 0x413B10
SOURCE_FASTVIEW_EVENT_USER_CLUB_POINTER_OFFSET = 0x5B4
SOURCE_FASTVIEW_EVENT_FIRST_CLUB_SUBOBJECT_OFFSET = 0x14
SOURCE_FASTVIEW_EVENT_SECOND_CLUB_SUBOBJECT_OFFSET = 0x28
SOURCE_FASTVIEW_EVENT_SELECTED_BOTH_HUMAN_VA = 0x51FB1C
SOURCE_FASTVIEW_EVENT_SELECTED_CLUB_OWNER_TEST_VA = 0x4037B0


class OriginalFastViewHumanEventSourceError(ValueError):
    """Actual native manager club identity is unavailable or contradictory."""


@dataclass(frozen=True)
class OriginalFastViewHumanEventSourceReceipt:
    """Native return AL plus diagnostic first matching original manager/side.

    The original returns only AL: the ordinals here merely explain the
    exact source pointer comparisons and are NOT original GameState fields.
    """
    original_callback_510c30_nonzero: bool
    first_matching_original_human_ordinal: int | None
    matched_event_club_ordinal: int | None


def source_fastview_original_human_event_510c30(
    *, original_human_count_global_8755e4: int,
    original_manager_club_pointers_by_413b10_index: tuple[int, ...],
    original_event_first_club_pointer: int | None,
    original_event_second_club_pointer: int | None,
) -> OriginalFastViewHumanEventSourceReceipt:
    """Native original mode2 event+0x14/0x28 pointer identity test.

    A zero human count skips event club pointer dereferences in the
    original. A positive human count must resolve the exact 0x413B10
    user pointer and +0x5B4 club pointer for every linked manager,
    and actual event accessor+0 results. Original walks manager indexes
    0..human_count-1 in source order, testing first club before second.
    """
    count=original_human_count_global_8755e4
    clubs=original_manager_club_pointers_by_413b10_index
    if (type(count) is not int or not 0<=count<=6 or
        type(clubs) is not tuple or len(clubs)!=count or
        any(type(ptr) is not int or not 0<ptr<=0xFFFFFFFF for ptr in clubs)):
        raise OriginalFastViewHumanEventSourceError(
            "exact original 0..6 human manager linked club object pointers required")
    if count==0:
        if (original_event_first_club_pointer is not None or
            original_event_second_club_pointer is not None):
            raise OriginalFastViewHumanEventSourceError(
                "no-human original source returns before dereferencing event clubs")
        return OriginalFastViewHumanEventSourceReceipt(False,None,None)
    for ptr in (original_event_first_club_pointer,original_event_second_club_pointer):
        if type(ptr) is not int or not 0<ptr<=0xFFFFFFFF:
            raise OriginalFastViewHumanEventSourceError(
                "source event club accessor+0 must return a qualified pointer")
    for ordinal,human_pointer in enumerate(clubs):
        if original_event_first_club_pointer==human_pointer:
            return OriginalFastViewHumanEventSourceReceipt(True,ordinal,0)
        if original_event_second_club_pointer==human_pointer:
            return OriginalFastViewHumanEventSourceReceipt(True,ordinal,1)
    return OriginalFastViewHumanEventSourceReceipt(False,None,None)


def source_fastview_original_selected_event_both_human_51fb1c(
    *, original_event_first_club_id_from_getter: int,
    original_event_second_club_id_from_getter: int,
    original_human_manager_club_ids_in_link_order: tuple[int, ...],
) -> bool:
    """Selected-event branch uses 0x4037B0 CLUB ID, unlike 0x510C30.

    Original 0x51FB1C and 0x51FB2F independently call 0x4037B0
    with the two event-derived CLUB POINTERS; that original callback
    compares club DWORD+0x04 IDs against original human manager club IDs.
    If BOTH calls pass, source local display flag BYTE+0x23 is reset.
    Original 0x510C30, in contrast, compares the club POINTERS directly.
    Keep these independent and do not silently collapse pointer identity
    into DBRClub DWORD IDs.
    """
    from original_fastview_native_player_roster_stage import (
        source_fastview_original_human_club_4037b0,
    )
    first=source_fastview_original_human_club_4037b0(
        original_club_reference_dword=original_event_first_club_id_from_getter,
        original_human_registry_club_ids_in_link_order=original_human_manager_club_ids_in_link_order)
    second=source_fastview_original_human_club_4037b0(
        original_club_reference_dword=original_event_second_club_id_from_getter,
        original_human_registry_club_ids_in_link_order=original_human_manager_club_ids_in_link_order)
    return first is not None and second is not None
