"""Original FM2001 0x615790 calendar slot-node linked-chain predicate.

Source native PE original SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
0x615790 walks node+4 and calls node v+0 with actual original argument.
Virtual methods MAY mutate world; returns must be supplied from an
actual reached original source state, never fake team equality.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from
from typing import Mapping


class Original615790SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original615790ReachedNode:
    original_reached_virtual18_event_pointer: int | None = None
    original_event_record_after_v18: bytes | None = None
    original_reached_virtual0_eax: int | None = None


@dataclass(frozen=True)
class Original615790LinkedSlotReceipt:
    original_slot_head_pointer: int
    visited_node_pointers: tuple[int, ...]
    original_result_eax: int
    first_source_matching_node_pointer: int | None
    original_world_callback_results_reconstructed: bool = False
    native_calendar_world_mutated: bool = False


def source_original_615790_slot_chain_from_reached(
    *, original_slot_head_pointer: int,
    original_node_records_by_pointer: Mapping[int, bytes],
    original_reached_node_calls: Mapping[int, Original615790ReachedNode],
    max_nodes: int=4096,
) -> Original615790LinkedSlotReceipt:
    """Strict source 0x615790 first matching virtual+0 callback and +4 walk.

    Original node+8 nonzero skips event and virtual+0; node v+18 event
    null is NOT qualified as 0x6157AA directly reads event+44.
    Bit6 skips virtual+0. Remaining reached v+0 AL nonzero stops.
    All source virtual outputs must correspond exactly to reached nodes.
    """
    p=original_slot_head_pointer
    if type(p) is not int or not 0<=p<=0xFFFFFFFF:
        raise Original615790SourceError("original source slot head uint32 required")
    if not isinstance(original_node_records_by_pointer,Mapping) or not isinstance(original_reached_node_calls,Mapping):
        raise Original615790SourceError("original node graph and reached calls required")
    if type(max_nodes) is not int or not 1<=max_nodes<=1_000_000:
        raise Original615790SourceError("positive traversal bound required")
    visited=[]
    seen=set()
    match=None
    while p:
        if p in seen:
            raise Original615790SourceError("original native node chain contains a cycle")
        if len(visited)>=max_nodes:
            raise Original615790SourceError("original slot chain exceeds caller traversal bound")
        seen.add(p)
        visited.append(p)
        try:
            rec=original_node_records_by_pointer[p]
        except (KeyError,TypeError) as e:
            raise Original615790SourceError("reached native node pointer missing from graph") from e
        if type(rec) is not bytes or len(rec)<0x0C or not unpack_from("<I",rec)[0]:
            raise Original615790SourceError("original reached node vtable and +8 state required")
        nextptr=unpack_from("<I",rec,4)[0]
        active=unpack_from("<I",rec,8)[0]
        reached=original_reached_node_calls.get(p)
        if active:
            if reached is not None:
                raise Original615790SourceError("node+8 skips all original virtual calls")
        else:
            if not isinstance(reached,Original615790ReachedNode):
                raise Original615790SourceError("actual native virtual18 reached result required")
            eventptr=reached.original_reached_virtual18_event_pointer
            if type(eventptr) is not int or not 0<eventptr<=0xFFFFFFFF:
                raise Original615790SourceError("actual nonnull native v18 event pointer required")
            event=reached.original_event_record_after_v18
            if type(event) is not bytes or len(event)<0x48:
                raise Original615790SourceError("actual original event+44 flag DWORD required")
            flags=unpack_from("<I",event,0x44)[0]
            if flags&0x40:
                if reached.original_reached_virtual0_eax is not None:
                    raise Original615790SourceError("original bit6 skips node virtual0 callback")
            else:
                eax=reached.original_reached_virtual0_eax
                if type(eax) is not int or not 0<=eax<=0xFFFFFFFF:
                    raise Original615790SourceError("actual reached original node v0 EAX required")
                if eax:
                    match=p
                    break
        p=nextptr
    if set(original_reached_node_calls)!=set(
        q for q in visited if unpack_from("<I",original_node_records_by_pointer[q],8)[0]==0
    ):
        raise Original615790SourceError("source skipped/extra virtual event outputs supplied")
    return Original615790LinkedSlotReceipt(
        original_slot_head_pointer,tuple(visited),int(match is not None),match)
