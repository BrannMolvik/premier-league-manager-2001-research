"""Original 0x615790/0x615890 native adjacent-date conflict traversal.

Proven from owner-private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
through static x86 byte and vtable analysis only, NEVER original execution.
This is a strict reached-source read-only probe, not the game's date allocator.

Original 0x615790 skips native events with event+8 nonzero, then tests
source return-this vtable+0x18 payload flags DWORD+0x44 bit6, then calls
native vtable+0 with the actual comparison object. All seven verified
LeagueMatch vtables use +0x00=0x510A80 (two ClubRef comparisons through
the *comparison match* virtual+0x04), and +0x18=0x6559A0.
No clean-room node_kind, reconstructed club equality, Python fixture
result or unverified virtual return can substitute for reached native EAX.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_leaguematch_native_process_owners import (
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
)

SOURCE_ORIGINAL_DATE_SLOT_EVENT_CONFLICT_615790=0x615790
SOURCE_ORIGINAL_DATE_NEIGHBOR_SEARCH_615890=0x615890
SOURCE_ORIGINAL_LEAGUEMATCH_VIRTUAL_00=0x510A80
SOURCE_ORIGINAL_LEAGUEMATCH_VIRTUAL_04=0x510A40
SOURCE_ORIGINAL_LEAGUEMATCH_VIRTUAL_18=0x6559A0
SOURCE_ORIGINAL_EVENT_LINK_OFFSET=0x04
SOURCE_ORIGINAL_EVENT_LINKED_SKIP_OFFSET=0x08
SOURCE_ORIGINAL_MATCH_FLAGS_OFFSET=0x44
SOURCE_ORIGINAL_DATE_CONFLICT_EXCLUSION_FLAG=0x40
SOURCE_ORIGINAL_SOURCE_U32_MAX=0xFFFFFFFF


class OriginalNativeNeighborConflictSourceError(ValueError):
    """Native event chain, source flags, or reached compare result unresolved."""


@dataclass(frozen=True)
class OriginalNativeNeighborConflictReceipt:
    original_source_candidate_bucket_index: int
    original_source_neighbor_start_index: int
    original_source_neighbor_exclusive_end_index: int
    original_source_found_first_conflict: bool
    original_source_first_conflict_bucket_index: int | None
    original_source_visited_event_pointers: tuple[int, ...]
    original_source_called_virtual0_event_pointers: tuple[int, ...]


def source_original_neighbor_match_conflict_615890(
    *,
    original_source_date_bucket_head_pointers: tuple[int, ...],
    original_source_candidate_bucket_index: int,
    original_source_comparison_match_pointer: int,
    original_source_comparison_match_record: bytes,
    original_source_match_records_by_pointer: dict[int, bytes],
    original_reached_virtual0_conflict_eax_by_event_pointer: dict[int, int],
) -> OriginalNativeNeighborConflictReceipt:
    """Replay actual original 0x615890 -> 0x615790 qualified read semantics.

    Source 0x615890 probes max(index-1,0) to min(index+2,count)
    EXCLUSIVE in ascending slot order; source 0x615790 walks each
    bucket's actual event+4 singly-linked native list head-to-tail.
    Calls event virtual+0 only where actual event+8==0 and actual
    payload DWORD+0x44 bit6==0. A supplied v0 result MUST match each
    reached callback, and no unreached callback may be invented.
    This API cannot evaluate 0x510A80 virtual comparison or alter
    a game calendar: the original reached EAX must be supplied.
    """
    heads=original_source_date_bucket_head_pointers
    candidate=original_source_candidate_bucket_index
    compare_ptr=original_source_comparison_match_pointer
    comparison=original_source_comparison_match_record
    nodes=original_source_match_records_by_pointer
    returns=original_reached_virtual0_conflict_eax_by_event_pointer
    if (type(heads) is not tuple or not heads or len(heads)>0x7FFFFFFD or
        any(type(x) is not int or not 0<=x<=SOURCE_ORIGINAL_SOURCE_U32_MAX for x in heads) or
        type(candidate) is not int or not 0<=candidate<len(heads)):
        raise OriginalNativeNeighborConflictSourceError(
            "original source candidate bucket index/collection DWORD array required")
    if (type(compare_ptr) is not int or not 0<compare_ptr<=SOURCE_ORIGINAL_SOURCE_U32_MAX or
        type(comparison) is not bytes or len(comparison)<4 or
        unpack_from("<I",comparison,0)[0] not in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS):
        raise OriginalNativeNeighborConflictSourceError(
            "original comparison native match+0 self vtable and pointer required")
    if (type(nodes) is not dict or type(returns) is not dict or
        any(type(p) is not int or not 0<p<=SOURCE_ORIGINAL_SOURCE_U32_MAX or
            type(r) is not bytes or len(r)<0x0C for p,r in nodes.items()) or
        any(type(p) is not int or not 0<p<=SOURCE_ORIGINAL_SOURCE_U32_MAX or
            type(eax) is not int or not 0<=eax<=SOURCE_ORIGINAL_SOURCE_U32_MAX
            for p,eax in returns.items())):
        raise OriginalNativeNeighborConflictSourceError(
            "authentic original pointer-to-record map and reached v0 results required")
    start=candidate-1 if candidate else 0
    stop=min(candidate+2,len(heads))
    visited=[]
    calls=[]
    found=None
    # A cyclic chain is invalid for this bounded source replay, never hang.
    for bucket_index in range(start,stop):
        pointer=heads[bucket_index]
        chain_seen=set()
        while pointer:
            if pointer in chain_seen:
                raise OriginalNativeNeighborConflictSourceError(
                    "original event+4 source list cycle cannot be replayed")
            chain_seen.add(pointer)
            record=nodes.get(pointer)
            if record is None or len(record)<4:
                raise OriginalNativeNeighborConflictSourceError(
                    "actual source native event pointer/record missing")
            vt=unpack_from("<I",record,0)[0]
            if vt not in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
                raise OriginalNativeNeighborConflictSourceError(
                    "original date list has unqualified non-LeagueMatch vtable")
            visited.append(pointer)
            event8=unpack_from("<I",record,SOURCE_ORIGINAL_EVENT_LINKED_SKIP_OFFSET)[0]
            if not event8:
                if len(record)<0x48:
                    raise OriginalNativeNeighborConflictSourceError(
                        "reached original virtual+18 match flags+44 source record required")
                flags=unpack_from("<I",record,SOURCE_ORIGINAL_MATCH_FLAGS_OFFSET)[0]
                if not flags & SOURCE_ORIGINAL_DATE_CONFLICT_EXCLUSION_FLAG:
                    result=returns.get(pointer)
                    if type(result) is not int:
                        raise OriginalNativeNeighborConflictSourceError(
                            "actual reached original vtable+0 EAX conflict required")
                    calls.append(pointer)
                    if result!=0:
                        found=bucket_index
                        break
            pointer=unpack_from("<I",record,SOURCE_ORIGINAL_EVENT_LINK_OFFSET)[0]
        if found is not None:
            break
    if set(returns)!=set(calls):
        raise OriginalNativeNeighborConflictSourceError(
            "source virtual+0 results supplied for unreached/filtered match events")
    return OriginalNativeNeighborConflictReceipt(
        candidate,start,stop,found is not None,found,
        tuple(visited),tuple(calls))
