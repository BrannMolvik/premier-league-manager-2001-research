"""Native 5CF990 per-user 606540 notice retention after 413020 routing.

Original private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This is an immutable source one-node projection, not original game execution,
a confirmed queue append, a rendered Inbox row, or live GameState mutation.

All fifteen concrete 606540 vtables have virtual+40 470CE0:
signed(global 9847FC day) <= signed(record+4 + 365 with 32-bit wrap).
Their virtual+44 is 667D30 (RET). 5CF990 only performs retention/expiry
on ALREADY owned DBRUser+6B4 queue items; it does not deliver global
947AA8 pending envelopes.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from,pack_into

from original_native_606540_human_mail_route import (
    Original606540HumanDueReached,
    source_original_606540_human_notice_due_to_user,
)


class Original606540UserRetentionSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original606540UserQueueReached:
    original_human_due_source: Original606540HumanDueReached
    original_registered_user_queue_pointer: int
    original_registered_user_queue_before: bytes
    original_per_user_wrapper_pointer: int
    original_per_user_wrapper_before: bytes
    original_source_current_day_9847fc: int


@dataclass(frozen=True)
class Original606540UserRetentionReceipt:
    original_player_id: int
    original_notice_class_vtable: int
    original_registered_user_pointer: int
    original_per_user_queue_pointer: int
    original_event_date_raw_u32: int
    original_expiry_date_raw_u32: int
    original_current_date_raw_u32: int
    original_source_keeps_user_notice: bool
    original_source_calls_667d30_and_42cc30_on_expiry: bool
    original_user_queue_after_source: bytes
    original_source_node_retained: bytes | None
    original_native_user_queue_mutated: bool = False
    original_native_5cf990_executed: bool = False
    original_inbox_rendered: bool = False
    live_game_state_updated: bool = False


def _u32(n: int, name: str, nonzero: bool = False) -> int:
    if type(n) is not int or not 0<=n<=0xffffffff or (nonzero and n==0):
        raise Original606540UserRetentionSourceError(f"original {name} 32-bit source required")
    return n


def _s32(n: int) -> int:
    return n if n<0x80000000 else n-0x100000000


def source_original_606540_user_notice_retention(
    reached: Original606540UserQueueReached,
) -> Original606540UserRetentionReceipt:
    """5CF990 source retention of ONE already-owned native user list item.

    Original 5CF995 walks first user+6B4 queue +4; at each wrapper+0
    event object, calls vtable+40 (470CE0); on false invokes vtable+44
    (667D30 no-op) and 42CC30 unlinks the user wrapper. The actual
    completed native enqueue and live list ownership must be separately
    witnessed, not inferred from a candidate 413020 route.
    """
    if not isinstance(reached,Original606540UserQueueReached):
        raise Original606540UserRetentionSourceError("typed reached original user queue required")
    due_source=reached.original_human_due_source
    due=source_original_606540_human_notice_due_to_user(due_source)
    userptr=due.original_413020_qualified_recipient_user_pointer
    queueptr=due.original_413020_candidate_user_queue_pointer
    if userptr is None or queueptr is None or due.original_413020_deferred_lookup_gated_out:
        raise Original606540UserRetentionSourceError("only first matched source-qualified 413020 recipient may have a list")
    if _u32(reached.original_registered_user_queue_pointer,"user+6B4 owner pointer",True)!=queueptr:
        raise Original606540UserRetentionSourceError("original user+6B4 reached queue pointer disagrees with due route")
    hdr=reached.original_registered_user_queue_before
    if type(hdr) is not bytes or len(hdr)<12:
        raise Original606540UserRetentionSourceError("actual per-user queue through+8 required")
    ptr=_u32(reached.original_per_user_wrapper_pointer,"per-user wrapper",True)
    if unpack_from("<II",hdr,4)!=(ptr,ptr):
        raise Original606540UserRetentionSourceError("only exact one-node first+last source list qualified")
    node=reached.original_per_user_wrapper_before
    if (type(node) is not bytes or len(node)!=12 or
            unpack_from("<III",node)!=(due_source.original_constructed_notice_pointer,0,0)):
        raise Original606540UserRetentionSourceError("actual source owned user+6B4 wrapper+0/+4/+8 required")
    notice=due.original_source_notice_after_5cfa20
    if unpack_from("<I",notice,0)[0]!=due.original_concrete_notice_vtable:
        raise Original606540UserRetentionSourceError("concrete vtable lost between due callback and 5CF990")
    source_date=unpack_from("<I",notice,4)[0]
    day=_u32(reached.original_source_current_day_9847fc,"native retention day")
    expiry=(source_date+0x16d)&0xffffffff
    keep=_s32(day)<=_s32(expiry)
    after=bytearray(hdr)
    if not keep:
        pack_into("<I",after,4,0)
        pack_into("<I",after,8,0)
    return Original606540UserRetentionReceipt(
        due.original_player_id,due.original_concrete_notice_vtable,
        userptr,queueptr,source_date,expiry,day,keep,not keep,
        bytes(after),node if keep else None,
    )
