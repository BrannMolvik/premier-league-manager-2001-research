"""Original interactive FastView per-frame event owner selection.

Shipped owner-private footballmanager.exe original verified hash:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Only statically inspected, never executed. Source 0x51F9F0 is the
SECOND virtual function in original nested view vtable 0x7CA58C.
It resolves match owner via 0x62AC80, then 0x5112E0 calls owner+0x4C
virtual+0x30 and masks result to an 8-bit mode. It chooses one of two
distinct original global event arrays and relative source index for
0x51FA70. No event array index bounds check exists in the original;
this portable model refuses unsafe original pointers. This is NOT
match event-generation logic, FastView rendering, or PResults.
"""
from __future__ import annotations

from dataclasses import dataclass

NATIVE_FASTVIEW_NESTED_VTABLE_VA = 0x7CA58C
NATIVE_FASTVIEW_NESTED_VIRTUAL1_VA = 0x51F9F0
NATIVE_FASTVIEW_EVENT_MODE_GETTER_VA = 0x5112E0
NATIVE_FASTVIEW_EVENT_RENDERER_VA = 0x51FA70
NATIVE_FASTVIEW_CURRENT_EVENT_INDEX_GLOBAL_VA = 0x9847FC
NATIVE_FASTVIEW_MODE_NONZERO_EVENT_ARRAY_GLOBAL_VA = 0x947AF0
NATIVE_FASTVIEW_MODE_NONZERO_EVENT_BASE_GLOBAL_VA = 0x947AF8
NATIVE_FASTVIEW_MODE_ZERO_EVENT_ARRAY_GLOBAL_VA = 0x947AD8
NATIVE_FASTVIEW_MODE_ZERO_EVENT_BASE_GLOBAL_VA = 0x947AE0


class OriginalFastViewEventCollectionSourceError(ValueError):
    """Source event index, record or callback owner is unavailable."""


@dataclass(frozen=True)
class OriginalFastViewSelectedEventSource:
    mode_5112e0_byte: int
    chosen_source_event_array_global_va: int
    chosen_source_event_base_global_va: int
    original_offset_from_source_base: int
    original_source_event_record_pointer: int


def source_fastview_original_current_event_51f9f0(
    *, original_5112e0_virtual30_return_byte: int,
    original_native_event_current_9847fc: int,
    original_nonzero_event_base_947af8: int,
    original_zero_event_base_947ae0: int,
    original_nonzero_events_by_native_index: tuple[int, ...],
    original_zero_events_by_native_index: tuple[int, ...],
) -> OriginalFastViewSelectedEventSource:
    """Source 0x51F9F0 chooses native event reference for 0x51FA70.

    Native if 0x5112E0 AL!=0: EAX=(DWORD 0x9847FC)-(DWORD0x947AF8)
    and pointer=*(DWORD0x947AF0 + 4*EAX). If zero: chooses
    pointer=*(DWORD0x947AD8 + 4*(DWORD0x9847FC-DWORD0x947AE0)).
    Caller supplies *actual original native array entries*, not
    reconstructed news, calculated scores or an ordered GUI list.
    Null or missing source pointer cannot enter original 0x51FA70.
    """
    fields=(original_5112e0_virtual30_return_byte,
            original_native_event_current_9847fc,
            original_nonzero_event_base_947af8,
            original_zero_event_base_947ae0)
    limits=(255,0xFFFFFFFF,0xFFFFFFFF,0xFFFFFFFF)
    if any(type(v) is not int or not 0<=v<=limit
           for v,limit in zip(fields,limits)):
        raise OriginalFastViewEventCollectionSourceError(
            "qualified original virtual event mode and native DWORD cursor/bases required")
    for items in (original_nonzero_events_by_native_index,
                  original_zero_events_by_native_index):
        if (type(items) is not tuple or any(type(addr) is not int or
            not 0 < addr <= 0xFFFFFFFF for addr in items)):
            raise OriginalFastViewEventCollectionSourceError(
                "authentic nonnull original native event-record pointer tuple required")
    if original_5112e0_virtual30_return_byte:
        base=original_nonzero_event_base_947af8
        chosen=original_nonzero_events_by_native_index
        array_va=NATIVE_FASTVIEW_MODE_NONZERO_EVENT_ARRAY_GLOBAL_VA
        base_va=NATIVE_FASTVIEW_MODE_NONZERO_EVENT_BASE_GLOBAL_VA
    else:
        base=original_zero_event_base_947ae0
        chosen=original_zero_events_by_native_index
        array_va=NATIVE_FASTVIEW_MODE_ZERO_EVENT_ARRAY_GLOBAL_VA
        base_va=NATIVE_FASTVIEW_MODE_ZERO_EVENT_BASE_GLOBAL_VA
    index=(original_native_event_current_9847fc-base)&0xFFFFFFFF
    if index>=len(chosen):
        raise OriginalFastViewEventCollectionSourceError(
            "original event cursor resolves outside validated source array")
    return OriginalFastViewSelectedEventSource(
        mode_5112e0_byte=original_5112e0_virtual30_return_byte,
        chosen_source_event_array_global_va=array_va,
        chosen_source_event_base_global_va=base_va,
        original_offset_from_source_base=index,
        original_source_event_record_pointer=chosen[index])


NATIVE_FASTVIEW_EVENT_COMPARE_BY_INDIRECT_NAME_VA = 0x51F3C0
NATIVE_FASTVIEW_EVENT_LIST_SORT_VA = 0x526DF0


def source_fastview_original_event_name_less_51f3c0(
    *, first_event_virtual14_returned_name_nul: bytes,
    second_event_virtual14_returned_name_nul: bytes,
) -> bool:
    """Exact original name comparator passed to 0x526DF0 sort.

    Native 0x51F3C0 invokes each candidate event+0x14 vtable+0,
    dereferences its return+0x0C then follows its C-string pointer.
    Caller supplies those REAL returned byte strings after original
    dereferences; no names are inferred from modern GameState.
    The source compares original unsigned byte values, returning 1
    when first string is strictly lexicographically less. Equal names
    return 0. Byte case, accents and non-ASCII are not normalized.
    Reproducing 0x526DF0's complete ordering/tie algorithm and the
    original 0x51FA70 child candidate selection is a separate step.
    """
    a,b=first_event_virtual14_returned_name_nul,second_event_virtual14_returned_name_nul
    if (type(a) is not bytes or b"\x00" not in a
        or type(b) is not bytes or b"\x00" not in b):
        raise OriginalFastViewEventCollectionSourceError(
            "two source-indirect original NUL-terminated event-name byte strings required")
    a=a[:a.index(b"\x00")]
    b=b[:b.index(b"\x00")]
    return a<b


NATIVE_FASTVIEW_EVENT_FILTER_AND_SORT_VA = 0x51FA70
NATIVE_FASTVIEW_EVENT_OBJECT_LIST_START = 0xA4
NATIVE_FASTVIEW_EVENT_OBJECT_LIST_SORTED_INDEX = 0x2A4
NATIVE_FASTVIEW_EVENT_MAX_SOURCE_SAFE_CANDIDATES = (
    (NATIVE_FASTVIEW_EVENT_OBJECT_LIST_SORTED_INDEX
     - NATIVE_FASTVIEW_EVENT_OBJECT_LIST_START)//4
)


@dataclass(frozen=True)
class OriginalFastViewNativeEventPointerSortReceipt:
    original_sorted_source_event_pointers: tuple[int, ...]
    original_selected_event_sorted_ordinal: int


def source_fastview_original_unique_named_event_sort_51fa70(
    *, original_selected_event_pointer: int,
    original_51fa70_filtered_candidate_pointers_and_indirect_names:
        tuple[tuple[int, bytes], ...],
) -> OriginalFastViewNativeEventPointerSortReceipt:
    """Only source 0x51FA70's 0x526DF0 comparator/sorted-index stage.

    Caller MUST already resolve complete candidate membership using the
    original linked event graph and filters in 0x51FA70. Its very first
    candidate is original selected event, not a new generic fixture.
    Original 0x526DF0 sorts pointers with comparator 0x51F3C0, which
    compares the indirect original C-name strings bytewise. A portable
    sorted order is unambiguous only for DISTINCT source byte names;
    tied names fail closed until native tie behavior is reproduced.
    0x51FA70 records selected pointer's new index at owner+0x2A4.
    """
    if (type(original_selected_event_pointer) is not int or
            not 0 < original_selected_event_pointer <= 0xFFFFFFFF):
        raise OriginalFastViewEventCollectionSourceError(
            "native selected event pointer required")
    candidates=original_51fa70_filtered_candidate_pointers_and_indirect_names
    if (type(candidates) is not tuple or
            not 1 <= len(candidates) <= NATIVE_FASTVIEW_EVENT_MAX_SOURCE_SAFE_CANDIDATES):
        raise OriginalFastViewEventCollectionSourceError(
            "qualified complete original 1..128 filtered event candidate tuple required")
    pointers=set()
    names=set()
    for item in candidates:
        if type(item) is not tuple or len(item)!=2:
            raise OriginalFastViewEventCollectionSourceError("original event pointer and C-name pair required")
        pointer,name=item
        if (type(pointer) is not int or not 0 < pointer <= 0xFFFFFFFF or
            type(name) is not bytes or b"\0" not in name):
            raise OriginalFastViewEventCollectionSourceError(
                "authentic nonnull event pointer and source resolved original name required")
        c_name=name[:name.index(b"\0")]
        if pointer in pointers or c_name in names:
            raise OriginalFastViewEventCollectionSourceError(
                "duplicate pointer or ambiguous same-name native event tie requires source runtime")
        pointers.add(pointer)
        names.add(c_name)
    if original_selected_event_pointer not in pointers or candidates[0][0]!=original_selected_event_pointer:
        raise OriginalFastViewEventCollectionSourceError(
            "original 0x51FA70 must seed selected event as first source candidate")
    ordered=sorted(candidates,key=lambda pair:pair[1][:pair[1].index(b"\0")])
    sorted_ptrs=tuple(event_pointer for event_pointer,_ in ordered)
    return OriginalFastViewNativeEventPointerSortReceipt(
        sorted_ptrs,sorted_ptrs.index(original_selected_event_pointer))
