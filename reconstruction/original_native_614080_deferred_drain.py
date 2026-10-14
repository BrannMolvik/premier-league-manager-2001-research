"""Original 0x614080 active-list deferred processing, not a cursor reset.

Original private executable 4,714,541 bytes SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Source disassembly 613EE0 (postscan) and 614080 + event vtables.
Read-only source decision. It does not execute native callbacks,
deallocate 4EA190 wrappers, drain the entire linked list, deliver mail or
change GameState.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from, pack_into


class Original614080DrainSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original614080Reached:
    # Exact original 947AA8 owner +0 policy/+4 head/+8 tail/+C active/+10 deferred.
    original_queue_header_before: bytes
    # Only if active==0 and original queue first node != NULL.
    original_single_node_pointer: int | None = None
    original_single_node_before: bytes | None = None
    original_event_pointer: int | None = None
    original_event_object_bytes: bytes | None = None
    # Needed ONLY for 7BD564 whose +18=404610 jumps payload+24;
    # original source cannot infer payload virtual result from vtable alone.
    original_7bd564_reached_payload_virtual24_result: int | None = None


@dataclass(frozen=True)
class Original614080SourceReceipt:
    original_deferred_flag_set: bool
    original_header_source_after: bytes
    original_single_node_retained: bool | None
    original_virtual4_source_result_if_called: int | None
    original_virtual18_source_result_if_called: int | None
    original_4ea190_wrapper_unlink_required: bool
    original_event_virtual4_executed: bool = False
    original_event_virtual18_executed: bool = False
    original_native_queue_mutated: bool = False
    original_inbox_delivery_verified: bool = False
    live_game_state_updated: bool = False


def source_original_614080_deferred_drain_from_reached(
    reached: Original614080Reached,
) -> Original614080SourceReceipt:
    """614080 early call while queue active sets deferred DWORD+0x10=1 and
    returns. Inactive normal drain reads first node and original event
    vft+4, then vft+18, and removes via 4EA190 only when result says so.

    This covers exact ONE native wrapper in the inactive branch; a complete
    multi-node/reentrant queue world requires independently traced mutation.
    """
    if not isinstance(reached,Original614080Reached):
        raise Original614080DrainSourceError("typed native 614080 reached call required")
    hdr=reached.original_queue_header_before
    if type(hdr) is not bytes or len(hdr)<0x14:
        raise Original614080DrainSourceError("native queue header through +10 required")
    active=unpack_from("<I",hdr,0xc)[0]
    if active:
        if any(x is not None for x in (
            reached.original_single_node_pointer,
            reached.original_single_node_before,
            reached.original_event_pointer,
            reached.original_event_object_bytes,
            reached.original_7bd564_reached_payload_virtual24_result)):
            raise Original614080DrainSourceError("active 614080 returns BEFORE scanning any queue node")
        after=bytearray(hdr);pack_into("<I",after,0x10,1)
        return Original614080SourceReceipt(True,bytes(after),None,None,None,False)
    first=unpack_from("<I",hdr,4)[0]
    tail=unpack_from("<I",hdr,8)[0]
    if first==0:
        if tail!=0 or any(x is not None for x in (
            reached.original_single_node_pointer,
            reached.original_single_node_before,
            reached.original_event_pointer,
            reached.original_event_object_bytes,
            reached.original_7bd564_reached_payload_virtual24_result)):
            raise Original614080DrainSourceError("empty 614080 queue cannot claim events or tail")
        return Original614080SourceReceipt(False,hdr,None,None,None,False)
    if first!=tail:
        raise Original614080DrainSourceError("multiple native nodes need reached complete order")
    ptr=reached.original_single_node_pointer
    eventptr=reached.original_event_pointer
    if (type(ptr) is not int or ptr!=first
            or type(eventptr) is not int or not 0<eventptr<=0xffffffff):
        raise Original614080DrainSourceError("actual original first wrapper/event identity required")
    node=reached.original_single_node_before
    if (type(node) is not bytes or len(node)!=12
            or unpack_from("<III",node)!=(eventptr,0,0)):
        raise Original614080DrainSourceError("original single wrapper and two null neighbor links required")
    event=reached.original_event_object_bytes
    if type(event) is not bytes or len(event)<0x14:
        raise Original614080DrainSourceError("actual original event bytes through vtable/status required")
    v=unpack_from("<I",event,0)[0]
    payload_result=reached.original_7bd564_reached_payload_virtual24_result
    if v==0x7d7760:
        if payload_result is not None:
            raise Original614080DrainSourceError("7D7760 virtual+18 returns literal1; no payload virtual")
        # Original [7D7760+4], [7D7760+18] both point to 4093E0:
        # mov eax,1; ret. The second v+4 is called and equals 1.
        return Original614080SourceReceipt(False,hdr,True,1,1,False)
    if v==0x7bd564:
        if type(payload_result) is not int or payload_result not in (0,1):
            raise Original614080DrainSourceError("7BD564 404610 payload virtual24 reached BOOL required")
        # +4=40DFB0 constant 0, +18=404610 -> payload+24 virtual.
        # If returned 0, 6140D9 calls 4EA190 to unlink single wrapper.
        if payload_result:
            return Original614080SourceReceipt(False,hdr,True,0,1,False)
        after=bytearray(hdr)
        pack_into("<I",after,4,0);pack_into("<I",after,8,0)
        return Original614080SourceReceipt(False,bytes(after),False,0,0,True)
    raise Original614080DrainSourceError("unqualified original event vtable in deferred drain")
