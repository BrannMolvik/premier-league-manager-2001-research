"""Native original 613EC0/617D70 insertion and 613EE0/4EA190 removal.

Source: original private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3;
static x86, not original runtime execution. Source records model byte-level
doubly-linked original queue at 947AA8, but they are NOT a saveable GameState
queue, actual malloc/free or original delivered Inbox.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

from original_native_7d7760_due_cleanup import (
    Original7D7760DueNonhumanReached,
    Original7D7760DueCleanupReceipt,
    source_original_7d7760_due_nonhuman_cleanup,
)


class Original613EE0SourceError(ValueError):
    pass


def _ptr(value: int, name: str, *, allow_zero: bool = False) -> int:
    if type(value) is not int or not 0 <= value <= 0xffffffff or (value==0 and not allow_zero):
        raise Original613EE0SourceError(f"actual native {name} pointer required")
    return value


@dataclass(frozen=True)
class Original613EC0InsertReached:
    """One native allocated wrapper about to be appended at queue tail."""
    original_queue_header_before: bytes
    original_new_wrapper_pointer: int
    original_event_pointer: int
    original_last_wrapper_pointer_before: int | None = None
    original_last_wrapper_record_before: bytes | None = None


@dataclass(frozen=True)
class Original613EC0InsertReceipt:
    original_queue_header_after_source: bytes
    original_new_wrapper_source_bytes: bytes
    original_last_wrapper_after_source: bytes | None
    original_source_tail_append: bool = True
    original_native_queue_insert_executed: bool = False
    live_game_state_updated: bool = False


def source_original_613ec0_insert_from_reached(reached: Original613EC0InsertReached) -> Original613EC0InsertReceipt:
    """Original 613EC0 allocates 12 bytes, writes object+0=event pointer,
    and calls 617D70 to append the wrapper after current tail.

    Header+4 is first, header+8 last, node+4 NEXT, node+8 PREV.
    Native allocator success or object lifetime cannot be guessed.
    """
    if not isinstance(reached,Original613EC0InsertReached):
        raise Original613EE0SourceError("typed native queue insertion source required")
    head=reached.original_queue_header_before
    if type(head) is not bytes or len(head)<0x14:
        raise Original613EE0SourceError("original queue header bytes through +10 required")
    wrapper=_ptr(reached.original_new_wrapper_pointer,"new node")
    event=_ptr(reached.original_event_pointer,"event")
    first=unpack_from("<I",head,4)[0]
    tail=unpack_from("<I",head,8)[0]
    hdr=bytearray(head)
    node=bytearray(12)
    pack_into("<I",node,0,event)
    last=None
    if first==0 and tail==0:
        if (reached.original_last_wrapper_pointer_before is not None
                or reached.original_last_wrapper_record_before is not None):
            raise Original613EE0SourceError("empty original queue cannot claim prior tail")
        pack_into("<I",hdr,4,wrapper)
        pack_into("<I",hdr,8,wrapper)
        pack_into("<I",node,4,0)
        pack_into("<I",node,8,0)
    else:
        if not first or not tail:
            raise Original613EE0SourceError("original linked list first/tail inconsistent")
        previous=_ptr(reached.original_last_wrapper_pointer_before,"reached old tail")
        if previous!=tail or wrapper in (first,tail):
            raise Original613EE0SourceError("native new wrapper and reached last pointer mismatch")
        raw=reached.original_last_wrapper_record_before
        if type(raw) is not bytes or len(raw)!=12 or unpack_from("<I",raw,4)[0]!=0:
            raise Original613EE0SourceError("native previous tail must have no next")
        old=bytearray(raw)
        pack_into("<I",old,4,wrapper)
        last=bytes(old)
        pack_into("<I",hdr,8,wrapper)
        pack_into("<I",node,8,tail)
        pack_into("<I",node,4,0)
    return Original613EC0InsertReceipt(bytes(hdr),bytes(node),last)


@dataclass(frozen=True)
class Original613EE0SingleNodeReached:
    """Native single queue element, not a synthetic full-queue acceptance."""
    original_queue_header_before: bytes
    original_queue_wrapper_pointer: int
    original_queue_wrapper_before: bytes
    original_event_pointer: int
    original_event_date_raw_dword: int
    original_target_date_raw_dword: int
    original_remove_after_callback_flag: int
    original_due_nonhuman_player_callback_if_reached: Original7D7760DueNonhumanReached | None


@dataclass(frozen=True)
class Original613EE0SingleNodeReceipt:
    original_signed_due: bool
    original_due_virtual_dispatch_source_reached: bool
    original_source_header_after_scan_before_delivery: bytes
    original_source_wrapper_retained: bytes | None
    original_7d7760_player_cleanup_source_receipt: Original7D7760DueCleanupReceipt | None
    original_event_virtual_zero_destructor_if_removed: bool
    original_wrapper_heap_free_if_removed: bool
    original_postloop_registered_user_5cf990_unresolved: bool = True
    original_native_queue_callback_executed: bool = False
    original_native_queue_mutated: bool = False
    original_mail_delivered: bool = False
    live_game_state_updated: bool = False


def _s32(raw: int) -> int:
    return raw-0x100000000 if raw>=0x80000000 else raw


def source_original_613ee0_single_due_from_reached(
    reached: Original613EE0SingleNodeReached,
) -> Original613EE0SingleNodeReceipt:
    """Original 613EE0 JG compare and flagged 4EA190→42CBF0 queue unlink.

    All five known actual 613EE0 callers pass flag=1 and current 9847FC
    DWORD, but this projection requires original caller flag explicitly.
    On due, 613EE0 invokes vtable+0x10 BEFORE optional unlink. Full
    original 5CF990 per-user delivery after loop is unresolved.
    """
    if not isinstance(reached,Original613EE0SingleNodeReached):
        raise Original613EE0SourceError("single native 613EE0 reached node record required")
    hdr=reached.original_queue_header_before
    if type(hdr) is not bytes or len(hdr)<0x14:
        raise Original613EE0SourceError("original queue header +4/+8/+10 required")
    ptr=_ptr(reached.original_queue_wrapper_pointer,"single node")
    event=_ptr(reached.original_event_pointer,"event")
    if (unpack_from("<I",hdr,4)[0]!=ptr or unpack_from("<I",hdr,8)[0]!=ptr):
        raise Original613EE0SourceError("original single node must be BOTH first and tail")
    node=reached.original_queue_wrapper_before
    if (type(node) is not bytes or len(node)!=12 or
            unpack_from("<I",node,0)[0]!=event or
            unpack_from("<I",node,4)[0]!=0 or
            unpack_from("<I",node,8)[0]!=0):
        raise Original613EE0SourceError("actual one-node wrapper+0/+4/+8 owner/chain required")
    due=_ptr(reached.original_event_date_raw_dword,"event due day",allow_zero=True)
    target=_ptr(reached.original_target_date_raw_dword,"reached target day",allow_zero=True)
    flag=reached.original_remove_after_callback_flag
    if type(flag) is not int or flag not in (0,1):
        raise Original613EE0SourceError("reached original remove callback flag 0 or 1 required")
    is_due=_s32(due)<=_s32(target)
    # 613EE0 always resets header+0xC active flag and +0x10 pending cursor
    # at loop exit before unrelated 5CF990 per-user delivery starts.
    after_scan=bytearray(hdr)
    pack_into("<I",after_scan,0xc,0)
    pack_into("<I",after_scan,0x10,0)
    callback=reached.original_due_nonhuman_player_callback_if_reached
    if not is_due:
        if callback is not None:
            raise Original613EE0SourceError("future original event skips due virtual callback")
        return Original613EE0SingleNodeReceipt(
            False,False,bytes(after_scan),node,None,False,False)
    if not isinstance(callback,Original7D7760DueNonhumanReached):
        raise Original613EE0SourceError("due original event demands qualified native 7D7760 callback")
    if (callback.original_native_event_object_pointer!=event or
            callback.original_613ee0_queue_node_pointer!=ptr or
            callback.original_613ee0_queue_node_bytes!=node or
            callback.original_613ee0_target_day_raw_dword!=target or
            unpack_from("<I",callback.original_native_event_object_bytes,4)[0]!=due):
        raise Original613EE0SourceError("native due callback must match exact queue node/event/date")
    projected=source_original_7d7760_due_nonhuman_cleanup(callback)
    if flag==0:
        # Original virtual handler still runs, but 4EA190 is not reached.
        return Original613EE0SingleNodeReceipt(
            True,True,bytes(after_scan),node,projected,False,False)
    out=after_scan
    pack_into("<I",out,4,0)
    pack_into("<I",out,8,0)
    # Original 4EA190 optionally invokes the event virtual destructor
    # only when queue header+0 is nonzero and native event pointer non-null.
    destructor=unpack_from("<I",hdr,0)[0]!=0
    return Original613EE0SingleNodeReceipt(
        True,True,bytes(out),None,projected,destructor,True)
