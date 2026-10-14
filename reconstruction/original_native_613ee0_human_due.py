"""Source original 613EE0 one queued 7BD564 human notice -> 413020 recipient.

Composer links original 606540 human constructor receipt with independently
reached 947AA8 list wrapper, native signed due check, 7BD564 vft+0x10 5CFA20
and native 4EA190 unlink with flag1; first matched DBRUser+6B4 route remains
a SOURCE CANDIDATE, not an executed user queue insertion.

Private canonical footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into,unpack_from

from original_native_606540_human_mail_route import (
    Original606540HumanDueReached,Original606540HumanDueReceipt,
    source_original_606540_human_notice_due_to_user,
)
from original_native_5cfa20_due_event_transfer import SOURCE_CURRENT_DAY_REMOVE_CALL_SITES


class Original613EE0HumanSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original613EE0HumanReached:
    original_global_947aa8_queue_header_before: bytes
    original_global_947aa8_wrapper_node_pointer: int
    original_global_947aa8_wrapper_node_before: bytes
    original_human_due_source: Original606540HumanDueReached
    original_native_613ee0_caller_va: int
    # Original caller obtains current 9847FC raw day before native call.
    original_native_9847fc_raw_date_at_caller: int
    # Reentrant native 614080 can flag +10=1 DURING vft+10 callback.
    original_613ee0_post_callback_deferred_614080_flag: int


@dataclass(frozen=True)
class Original613EE0HumanReceipt:
    original_source_human_due: Original606540HumanDueReceipt
    original_source_global_queue_after: bytes
    original_source_global_node_unlinked: bool
    original_source_4ea190_calls_virtual_destructor: bool
    original_actual_global_node_free: bool = False
    original_actual_notice_constructor_executed: bool = False
    original_actual_5cfa20_callback_executed: bool = False
    original_actual_413020_per_user_append: bool = False
    original_visible_inbox_delivered: bool = False
    live_game_state_updated: bool = False


def source_original_613ee0_human_one_due(
    reached: Original613EE0HumanReached,
) -> Original613EE0HumanReceipt:
    """Source five direct 613EE0 callsites all pass remove=1.

    Require independently reached actual native list wrapper and no pending
    reentrant 614080 work, then model **potential** original vft+10 callback
    and source due unlink order. A real successful 413020 append is not
    inferred from the source candidate route. No original original executable
    process was run.
    """
    if not isinstance(reached,Original613EE0HumanReached):
        raise Original613EE0HumanSourceError("typed original native 613EE0 reached stage required")
    original=reached.original_global_947aa8_queue_header_before
    if type(original) is not bytes or len(original)<0x14:
        raise Original613EE0HumanSourceError("native 947AA8 owner +0 through +10 required")
    nodeptr=reached.original_global_947aa8_wrapper_node_pointer
    if type(nodeptr) is not int or not 0<nodeptr<=0xffffffff:
        raise Original613EE0HumanSourceError("actual global queue wrapper pointer required")
    if unpack_from("<II",original,4)!=(nodeptr,nodeptr):
        raise Original613EE0HumanSourceError("only actual one-node global pending queue first+last qualified")
    if unpack_from("<I",original,0xc)[0]!=0:
        raise Original613EE0HumanSourceError("original due scan queue+0C must be inactive before entry")
    # Queue+10 native stale value is overwritten at entry; only postcallback
    # flag controls deferred 614080 branch.
    node=reached.original_global_947aa8_wrapper_node_before
    eventptr=reached.original_human_due_source.original_7bd564_wrapper_pointer
    if (type(node) is not bytes or len(node)!=12 or
            unpack_from("<III",node)!=(eventptr,0,0)):
        raise Original613EE0HumanSourceError("actual original pending node+0 event and null neighbors required")
    caller=reached.original_native_613ee0_caller_va
    if type(caller) is not int or caller not in SOURCE_CURRENT_DAY_REMOVE_CALL_SITES:
        raise Original613EE0HumanSourceError("only five source-confirmed flag1/current day callers qualified")
    day=reached.original_native_9847fc_raw_date_at_caller
    if type(day) is not int or not 0<=day<=0xffffffff:
        raise Original613EE0HumanSourceError("native current date raw DWORD required")
    if day!=reached.original_human_due_source.original_native_current_date_raw_u32:
        raise Original613EE0HumanSourceError("source queue-caller calendar and callback day mismatch")
    deferred=reached.original_613ee0_post_callback_deferred_614080_flag
    if type(deferred) is not int or deferred not in (0,1):
        raise Original613EE0HumanSourceError("actual 613EE0 postcallback deferred drain flag required")
    if deferred:
        raise Original613EE0HumanSourceError("reentrant 614080 after human due callback must be source-qualified separately")
    # Native vft+10 is 5CFA20 for 7BD564, which checks referenced
    # virtual+3C readiness, stamps date, clears wrapper+8, calls 413020.
    due=source_original_606540_human_notice_due_to_user(reached.original_human_due_source)
    out=bytearray(original)
    pack_into("<I",out,4,0)
    pack_into("<I",out,8,0)
    pack_into("<I",out,0xc,0)
    pack_into("<I",out,0x10,0)
    return Original613EE0HumanReceipt(
        due,bytes(out),True,unpack_from("<I",original,0)[0]!=0,
    )
