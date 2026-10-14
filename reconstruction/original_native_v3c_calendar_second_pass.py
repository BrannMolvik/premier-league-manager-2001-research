"""Original v3C reschedule 2nd pass and 0x615D10 date-window source.

Owner-private canonical footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
STATIC-only native source projection, not a reconstructed reschedule, native
calendar insertion, returned event pointer, 0x615C50 search, or world write.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_v3c_reschedule_gate import (
    OriginalV3CFirstCalendarLookupReceipt,
    OriginalV3CRescheduleGateError,
    OriginalV3CRescheduleGateReceipt,
    SOURCE_GLOBAL_DATE_INDEX_VA,
)
from original_schedule_event_native_constructor import (
    SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
    SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA,
)


SOURCE_RESCHEDULE_TWO_PASS_OWNER_VA = 0x5127A0
SOURCE_SECOND_PASS_SETUP_VA = 0x5127BB
SOURCE_ORIGINAL_DATE_LOOKUP_VA = 0x615D10
SOURCE_ORIGINAL_DATE_LOOKUP_ITERATOR_VA = 0x615C50
SOURCE_SECOND_OWNER_DWORD_OFFSET = 0x5B0
SOURCE_SECOND_OWNER_SIDE_SLOTS_OFFSET = 0x5B4
SOURCE_SECOND_OWNER_SIDE_FLAGS_OFFSET = 0x5FC
SOURCE_SECOND_OWNER_SIDE_COUNT_OFFSET = 0xB54


@dataclass(frozen=True)
class OriginalV3CSecondCalendarLookupReceipt:
    original_source_vtable_va: int
    original_second_pass_reached: bool
    source_original_second_team_pointer: int
    source_original_first_team_pointer: int
    source_second_side_slots_offset: int
    source_second_side_flags_offset: int
    source_second_side_count: int
    native_calendar_registry_va: int
    original_date_global_index: int
    second_requested_date_index: int
    original_615d10_return_known: bool = False
    later_5127a0_world_callbacks_proven: bool = False
    native_match_completion_proven: bool = False


@dataclass(frozen=True)
class OriginalNative615D10DateWindow:
    original_calendar_registry_va: int
    source_calendar_slots_base_pointer: int
    source_calendar_slot_count_raw: int
    source_calendar_date_base_raw: int
    original_requested_date_index: int
    source_date_delta_signed: int
    source_calendar_capacity_signed: int
    source_would_enter_615c50_search: bool
    first_candidate_slot_pointer: int | None
    negative_source_slot_index_unqualified: bool
    null_original_slot_vector_unqualified: bool
    native_search_result_proven: bool = False


def _uint32(value: int, desc: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise OriginalV3CRescheduleGateError(
            f"actual original {desc} uint32 required")
    return value


def _int32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value if value < 0x80000000 else value - 0x100000000


def source_original_5127a0_second_calendar_request(
    *,
    original_gate: OriginalV3CRescheduleGateReceipt,
    original_first_calendar_lookup: OriginalV3CFirstCalendarLookupReceipt,
    original_match_record_at_second_pass: bytes,
    original_processing_owner_at_second_pass: bytes,
    original_reached_second_pass: bool,
    original_reached_global_date_index_9847fc: int,
) -> OriginalV3CSecondCalendarLookupReceipt:
    """Model exactly the *second* EBX=1 lookup request, not its effects.

    Original first iteration invokes 0x615D10 and may mutate context/world.
    Original processing-owner bytes here must therefore be reached **after**
    first iteration completion, not copied from its entry snapshot. The
    source loops EBX 0 then 1, and reloads the global date each time.
    """
    if (not isinstance(original_gate, OriginalV3CRescheduleGateReceipt)
            or not original_gate.original_5127a0_called):
        raise OriginalV3CRescheduleGateError(
            "second pass requires source-qualified reached 0x5127A0 gate")
    first = original_first_calendar_lookup
    if (not isinstance(first, OriginalV3CFirstCalendarLookupReceipt)
            or first.original_source_vtable_va != original_gate.original_source_vtable_va
            or not first.native_615d10_reached):
        raise OriginalV3CRescheduleGateError(
            "first original EBX=0 calendar lookup receipt required")
    if original_reached_second_pass is not True:
        raise OriginalV3CRescheduleGateError(
            "actual reached original EBX=1 second pass required")
    match = original_match_record_at_second_pass
    if type(match) is not bytes or len(match) < 0x10:
        raise OriginalV3CRescheduleGateError(
            "original match record through +0x0C at second pass required")
    if unpack_from("<I", match)[0] != original_gate.original_source_vtable_va:
        raise OriginalV3CRescheduleGateError(
            "second pass source match vtable differs from first")
    owner = original_processing_owner_at_second_pass
    if type(owner) is not bytes or len(owner) < SOURCE_SECOND_OWNER_SIDE_COUNT_OFFSET + 4:
        raise OriginalV3CRescheduleGateError(
            "actual original after-first-pass processing owner through +B54 required")
    primary_ptr = unpack_from("<I", owner, 0)[0]
    second_ptr = unpack_from("<I", owner, SOURCE_SECOND_OWNER_DWORD_OFFSET)[0]
    if not primary_ptr or not second_ptr:
        raise OriginalV3CRescheduleGateError(
            "actual original first and second team owner pointers required")
    date = _uint32(original_reached_global_date_index_9847fc,
                   "second pass global 0x9847FC date index")
    collection = (
        SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA
        if unpack_from("<I", match, 0x0C)[0] & 1
        else SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA
    )
    return OriginalV3CSecondCalendarLookupReceipt(
        original_source_vtable_va=original_gate.original_source_vtable_va,
        original_second_pass_reached=True,
        source_original_second_team_pointer=second_ptr,
        source_original_first_team_pointer=primary_ptr,
        source_second_side_slots_offset=SOURCE_SECOND_OWNER_SIDE_SLOTS_OFFSET,
        source_second_side_flags_offset=SOURCE_SECOND_OWNER_SIDE_FLAGS_OFFSET,
        source_second_side_count=unpack_from(
            "<I",owner,SOURCE_SECOND_OWNER_SIDE_COUNT_OFFSET)[0],
        native_calendar_registry_va=collection,
        original_date_global_index=date,
        second_requested_date_index=(date+1)&0xFFFFFFFF,
    )


def source_original_615d10_calendar_date_window(
    *,
    original_calendar_registry_va: int,
    original_registry_record: bytes,
    original_requested_date_index: int,
) -> OriginalNative615D10DateWindow:
    """Project source 0x615D10's signed index/count check only.

    The original reads registry +8 date-base, +4 slot-count and +0 pointer.
    It computes signed 32-bit (date - base), compares signed delta against
    signed count, and invokes 0x615C50 in a linear search if delta < count.
    Native code does NOT reject a negative delta before forming the pointer;
    this records the resulting unqualified before-start candidate without
    dereferencing it or claiming the search was safe/completed.
    """
    if type(original_calendar_registry_va) is not int or original_calendar_registry_va not in (
            SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
            SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA):
        raise OriginalV3CRescheduleGateError(
            "actual original first/second calendar collection address required")
    if type(original_registry_record) is not bytes or len(original_registry_record) < 0x0C:
        raise OriginalV3CRescheduleGateError(
            "actual native calendar collection through DWORD +8 required")
    date = _uint32(original_requested_date_index,"calendar requested date")
    base, count, start = unpack_from("<III",original_registry_record,0)
    delta = _int32(date-start)
    signed_count = _int32(count)
    enter = delta < signed_count
    slot = ((base + 4*delta)&0xFFFFFFFF) if enter else None
    return OriginalNative615D10DateWindow(
        original_calendar_registry_va=original_calendar_registry_va,
        source_calendar_slots_base_pointer=base,
        source_calendar_slot_count_raw=count,
        source_calendar_date_base_raw=start,
        original_requested_date_index=date,
        source_date_delta_signed=delta,
        source_calendar_capacity_signed=signed_count,
        source_would_enter_615c50_search=enter,
        first_candidate_slot_pointer=slot,
        negative_source_slot_index_unqualified=bool(enter and delta < 0),
        null_original_slot_vector_unqualified=bool(enter and base == 0),
    )
