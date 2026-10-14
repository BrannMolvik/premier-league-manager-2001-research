"""Bounded original due-event transfer 0x613EE0->0x5CFA20 for vtables 7D1514/7D1568.

Owner-private source footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
STATIC source only; source-identified vtables, no original execution.
This models the immutable memory projection before the native 0x413020 call.
Neither 0x413020 routing, manager Inbox, pending queue removal nor GameState
mutation is performed here. Actual reached original event/object bytes required.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from


SOURCE_DUE_QUEUE_OWNER_VA = 0x947AA8
SOURCE_DUE_QUEUE_DISPATCH_VA = 0x613EE0
SOURCE_ENQUEUED_WRAPPER_EVENT_VTABLE = 0x7BD564
SOURCE_ENQUEUED_WRAPPER_VIRTUAL10_VA = 0x5CFA20
SOURCE_REFERENCED_EVENT_VTABLES = (0x7D1514, 0x7D1568)
SOURCE_REFERENCED_VIRTUAL3C_VA = 0x4093E0
SOURCE_ACTIVE_WORLD_DISPATCH_OWNER_VA = 0x874C10
SOURCE_ACTIVE_WORLD_DISPATCH_VA = 0x413020

# Independently enumerated native direct 0x613EE0 CALL sites, each PUSH 1,
# PUSH [0x9847FC], ECX=0x947AA8, CALL 0x613EE0. This is a bounded
# code-site inventory, NOT proof all possible indirect callers.
SOURCE_CURRENT_DAY_REMOVE_CALL_SITES = (
    0x41A364, 0x41A475, 0x43216C, 0x4A8084, 0x5E3335
)


class OriginalQueuedEventTransferError(ValueError):
    """An original prerequisite or reached-memory ownership is unqualified."""


@dataclass(frozen=True)
class OriginalQueuedEventTransferReceipt:
    original_event_pointer: int
    original_referenced_pointer: int
    original_event_due_date_signed: int
    original_processing_date_signed: int
    original_event_after_5cfa20: bytes
    original_referenced_after_5cfa20: bytes
    dispatch_global_owner_va: int = SOURCE_ACTIVE_WORLD_DISPATCH_OWNER_VA
    dispatch_function_va: int = SOURCE_ACTIVE_WORLD_DISPATCH_VA
    native_413020_executed: bool = False
    native_613ee0_wrapper_deleted: bool = False
    live_game_state_updated: bool = False
    player_visible_inbox_delivered: bool = False


def source_original_5cfa20_reached_due_transfer(
    *,
    original_613ee0_caller_va: int,
    original_613ee0_processing_date: int,
    original_queue_event_pointer: int,
    original_queue_event_record: bytes,
    original_referenced_pointer: int,
    original_referenced_object_record: bytes,
) -> OriginalQueuedEventTransferReceipt:
    """Qualify the exact concrete original native transfer, not delivery.

    The five confirmed direct source callers supply global date and literal
    remove=1. 613EE0 calls event virtual+10 only when signed(event+4)<=date.
    Event vtable 7BD564 virtual+10 = 5CFA20; referenced concrete class
    7D1514/7D1568 virtual+3C = 4093E0, constant EAX=1. 5CFA20 writes
    referenced+4=event+4, zeroes event+8, invokes global 874C10/413020.
    It does NOT decide eventual mailbox delivery; routing remains unproven.
    """
    if type(original_613ee0_caller_va) is not int or (
            original_613ee0_caller_va not in SOURCE_CURRENT_DAY_REMOVE_CALL_SITES):
        raise OriginalQueuedEventTransferError(
            "reached original due-date queue call site must be one of five verified direct callers")
    if type(original_613ee0_processing_date) is not int or not (
            -0x80000000 <= original_613ee0_processing_date <= 0x7fffffff):
        raise OriginalQueuedEventTransferError("signed reached original queue day required")
    for ptr, name in ((original_queue_event_pointer, "event pointer"),
                      (original_referenced_pointer, "referenced object pointer")):
        if type(ptr) is not int or not 0 < ptr <= 0xffffffff or ptr & 3:
            raise OriginalQueuedEventTransferError(f"valid original {name} required")
    raw = original_queue_event_record
    ref = original_referenced_object_record
    if type(raw) is not bytes or len(raw) < 12 or type(ref) is not bytes or len(ref) < 0x48:
        raise OriginalQueuedEventTransferError(
            "actual original event through +8 and referenced object through +44 required")
    if unpack_from("<I", raw)[0] != SOURCE_ENQUEUED_WRAPPER_EVENT_VTABLE:
        raise OriginalQueuedEventTransferError(
            "source 0x5CFA20 virtual+10 only proven for original 7BD564 event")
    if unpack_from("<I", raw, 8)[0] != original_referenced_pointer:
        raise OriginalQueuedEventTransferError(
            "original event+8 must own actual reached referenced object pointer")
    if unpack_from("<I", ref)[0] not in SOURCE_REFERENCED_EVENT_VTABLES:
        raise OriginalQueuedEventTransferError(
            "referenced virtual+3C constant one only proven for two native classes")
    if unpack_from("<I", ref, 0x10)[0] != 1 or unpack_from("<I", ref, 0x1C)[0] != 12:
        raise OriginalQueuedEventTransferError(
            "concrete 419490 original event must have category 1 and subtype 12")
    event_date = unpack_from("<i", raw, 4)[0]
    if event_date > original_613ee0_processing_date:
        raise OriginalQueuedEventTransferError(
            "native 0x613EE0 skips virtual+10 when event signed date is in future")
    next_raw = bytearray(raw)
    next_ref = bytearray(ref)
    pack_into("<I", next_raw, 8, 0)
    pack_into("<I", next_ref, 4, unpack_from("<I", raw, 4)[0])
    return OriginalQueuedEventTransferReceipt(
        original_queue_event_pointer,
        original_referenced_pointer,
        event_date,
        original_613ee0_processing_date,
        bytes(next_raw),
        bytes(next_ref),
    )
