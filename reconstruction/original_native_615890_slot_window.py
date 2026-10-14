"""Original FM2001 0x615890 bounded calendar slot-window selection.

Read-only pure projection of the source 0x615890 outer range and the
REACHED AL from original 0x615790 per-slot virtual callbacks.
The inner original 0x615790 uses mutable source node v0, so its return
MUST be caller-supplied, never inferred from symbolic club identities.
Original private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from
from typing import Mapping


class Original615890SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original615890ReachedWindow:
    first_source_index: int
    end_exclusive_index: int
    called_615790_indices: tuple[int, ...]
    first_matched_index: int | None
    original_returned_eax: int
    source_inner_virtual_callbacks_reconstructed: bool = False
    native_calendar_world_mutated: bool = False


def source_original_615890_slot_window_from_reached_callbacks(
    *, original_calendar_registry: bytes,
    original_requested_index: int,
    original_reached_615790_al_by_slot: Mapping[int, int],
) -> Original615890ReachedWindow:
    """Original 0x615890: [max(index-1,0),min(index+2,owner+4)).

    Source 0x6158BF invokes 0x615790 for every visited index in order.
    When its EAX is nonzero, writes the matching index to caller's
    output DWORD and returns EAX=1; else returns EAX=0 with output
    unchanged. No original caller output/slot pointer is materialized.
    """
    rec=original_calendar_registry
    if type(rec) is not bytes or len(rec)<8:
        raise Original615890SourceError("actual original registry pointer/count required")
    ptr=unpack_from("<I",rec,0)[0]
    count=unpack_from("<i",rec,4)[0]
    if count<0 or (count and not ptr):
        raise Original615890SourceError("native registry count/pointer unqualified")
    idx=original_requested_index
    if type(idx) is not int or not 0<=idx<=0x7FFFFFFD:
        raise Original615890SourceError(
            "actual nonnegative signed index with no +2 overflow required")
    if not isinstance(original_reached_615790_al_by_slot,Mapping):
        raise Original615890SourceError("reached original 615790 callback outcomes required")
    start=idx-1 if idx else 0
    end=min(idx+2,count)
    called=[]
    match=None
    for i in range(start,end):
        if i not in original_reached_615790_al_by_slot:
            raise Original615890SourceError(
                "actual reached per-slot original 615790 EAX is missing")
        value=original_reached_615790_al_by_slot[i]
        if type(value) is not int or not 0<=value<=0xFFFFFFFF:
            raise Original615890SourceError(
                "actual original 615790 EAX uint32 required")
        called.append(i)
        if value:
            match=i
            break
    if set(original_reached_615790_al_by_slot)!=set(called):
        raise Original615890SourceError(
            "skipped original 615790 slot results cannot be supplied")
    return Original615890ReachedWindow(
        start,end,tuple(called),match,int(match is not None))
