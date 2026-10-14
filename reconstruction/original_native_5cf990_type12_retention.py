"""Original per-user type12 queued-event retention 5CF990->470CE0->667D30.

Original executable SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Both concrete vtables 7D1514 and 7D1568 virtual+40 are 470CE0,
which compares signed global current day <= signed(event+4 + 0x16D),
using native wraparound; virtual+44 is 667D30 (return-only).
Projection only: no live user event lifecycle, Inbox render or queue removal.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_native_5cfa20_due_event_transfer import (
    OriginalQueuedEventTransferReceipt,
    SOURCE_REFERENCED_EVENT_VTABLES,
)
from original_native_413020_type12_human_route import Original413020ManagerRouteReceipt


class OriginalType12RetentionError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalType12RetentionReceipt:
    source_selected_user_pointer: int
    source_user_queue_pointer: int
    original_event_day_signed: int
    original_current_day_signed: int
    original_expiry_day_signed: int
    source_5cf990_keeps_event: bool
    source_5cf990_would_call_event_virtual44_and_42cc30: bool
    native_queue_mutated: bool = False
    native_event_deleted: bool = False
    visible_inbox_lifecycle_proven: bool = False


def _signed(value: int) -> int:
    v = value & 0xffffffff
    return v if v < 0x80000000 else v-0x100000000


def source_original_5cf990_type12_retention(
    *,
    original_due_transfer: OriginalQueuedEventTransferReceipt,
    original_selected_user_route: Original413020ManagerRouteReceipt,
    original_global_current_day_9847fc: int,
) -> OriginalType12RetentionReceipt:
    """Classify native 5CF990 one event after owner route and date transfer.

    Only exact original 419490 type12 instances (two known concrete vtables)
    and an already selected per-human owner are qualified. Native 470CE0
    computes event+4 date +365 as 32-bit signed arithmetic. On false,
    5CF990 calls virtual+44 (667D30) then 42CC30 removes its wrapper.
    Those original operations are NOT executed here.
    """
    transfer = original_due_transfer
    route = original_selected_user_route
    if not isinstance(transfer, OriginalQueuedEventTransferReceipt):
        raise OriginalType12RetentionError("source-qualified due event transfer required")
    if not isinstance(route, Original413020ManagerRouteReceipt):
        raise OriginalType12RetentionError("source-qualified human manager route required")
    if (route.original_selected_user_pointer is None
            or route.original_selected_user_event_queue_pointer is None
            or route.original_event_object_pointer != transfer.original_referenced_pointer):
        raise OriginalType12RetentionError(
            "source selected per-user queue and original event pointer identity required")
    obj=transfer.original_referenced_after_5cfa20
    if (type(obj) is not bytes or len(obj) < 0x48
            or unpack_from("<I", obj)[0] not in SOURCE_REFERENCED_EVENT_VTABLES
            or unpack_from("<I", obj, 0x10)[0] != 1
            or unpack_from("<I", obj, 0x1c)[0] != 12):
        raise OriginalType12RetentionError("concrete original class category1/subtype12 required")
    if type(original_global_current_day_9847fc) is not int or not (
            0 <= original_global_current_day_9847fc <= 0xffffffff):
        raise OriginalType12RetentionError("actual original current date uint32 required")
    event_day=unpack_from("<i",obj,4)[0]
    current=_signed(original_global_current_day_9847fc)
    expiry=_signed(event_day + 0x16d)
    keep=current <= expiry
    return OriginalType12RetentionReceipt(
        route.original_selected_user_pointer,
        route.original_selected_user_event_queue_pointer,
        event_day,current,expiry,keep,not keep,
    )
