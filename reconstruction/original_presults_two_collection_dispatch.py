"""Source-original PResults 4A8260 two registry execution/return order.

0x4A8260 calls original 6168C0 on PRIMARY 947AD8, retains its AL in BL,
then calls 6168C0 on SECONDARY 947AF0, restores AL from BL and returns.
The original 4A71F0 global PResults tick is invoked by actual callbacks
from EITHER registry. Original 4A7210 precount uses only primary 947AD8,
not a count of secondary events.

No live GameState event vtable execution or calendar mutations occur here.
This models independently qualified two 6168C0 source receipts and their
ordered display tick intents. Overfull original progress is recorded as a
counter state; the current 800px sprite renderer must refuse drawing an
oversized native fill without separately proving original clipping semantics.
"""
from dataclasses import dataclass

from original_presults_native_event_work import (
    OriginalPResultsDatedEventReceipt,
    OriginalPResultsSourceCallback,
    SOURCE_PRESULTS_NATIVE_SIGNED_MAX,
    SOURCE_PRESULTS_TICK_VA,
    OriginalPResultsEventSourceError,
)
from human_gameplay import OriginalResultsProgress

ORIGINAL_PRIMARY_6168C0_COLLECTION_VA = 0x947AD8
ORIGINAL_SECONDARY_6168C0_COLLECTION_VA = 0x947AF0
ORIGINAL_PRESULTS_TWO_COLLECTION_DISPATCH_VA = 0x4A8260
ORIGINAL_PRIMARY_6168C0_CALL_VA = 0x4A8266
ORIGINAL_SECONDARY_6168C0_CALL_VA = 0x4A8272


@dataclass(frozen=True)
class OriginalPResultsTwoCollectionSourceReceipt:
    original_primary_947ad8: OriginalPResultsDatedEventReceipt
    original_secondary_947af0: OriginalPResultsDatedEventReceipt
    ordered_source_callbacks: tuple[OriginalPResultsSourceCallback, ...]
    original_4a8260_return_al_nonzero: bool
    original_primary_6168c0_return_al_nonzero: bool
    original_secondary_6168c0_return_al_nonzero: bool
    original_native_date_event_callbacks_executed: bool = False
    original_game_state_advanced: bool = False
    original_presults_gui_rendered: bool = False


def source_original_4a8260_two_collection_date_callbacks(
    *, original_primary_947ad8: OriginalPResultsDatedEventReceipt,
    original_secondary_947af0: OriginalPResultsDatedEventReceipt,
) -> OriginalPResultsTwoCollectionSourceReceipt:
    if (type(original_primary_947ad8) is not OriginalPResultsDatedEventReceipt or
        type(original_secondary_947af0) is not OriginalPResultsDatedEventReceipt):
        raise OriginalPResultsEventSourceError(
            "actual separate original primary and secondary 6168C0 receipts required")
    for name,receipt in (("primary",original_primary_947ad8),
                         ("secondary",original_secondary_947af0)):
        if (type(receipt.original_progress_callbacks) is not tuple or
            type(receipt.original_6168c0_return_al_nonzero) is not bool):
            raise OriginalPResultsEventSourceError(
                "source "+name+" ordered callback tuple and native AL required")
        for callback in receipt.original_progress_callbacks:
            if (type(callback) is not OriginalPResultsSourceCallback or
                type(callback.original_event_pointer) is not int or
                not 0<callback.original_event_pointer<=0xffffffff or
                type(callback.source_pass) is not int or
                callback.source_pass not in (1,2) or
                callback.native_event_virtual_method_offset!=0x10 or
                callback.native_progress_callback_va!=SOURCE_PRESULTS_TICK_VA):
                raise OriginalPResultsEventSourceError(
                    "invalid source 6168C0 "+name+" actual native event v+0x10 tick")
        if receipt.original_6168c0_return_al_nonzero and not any(
                cb.source_pass==2 for cb in receipt.original_progress_callbacks):
            raise OriginalPResultsEventSourceError(
                "source "+name+" AL true requires reached second-pass tick")
        if not receipt.original_6168c0_return_al_nonzero and any(
                cb.source_pass==2 for cb in receipt.original_progress_callbacks):
            raise OriginalPResultsEventSourceError(
                "source "+name+" second-pass tick requires native AL true")
        if any(b.source_pass==1 for b in receipt.original_progress_callbacks[
            next((i for i,cb in enumerate(receipt.original_progress_callbacks)
                  if cb.source_pass==2),len(receipt.original_progress_callbacks)):]):
            raise OriginalPResultsEventSourceError(
                "native "+name+" 6168C0 first and second passes out of order")
    a=original_primary_947ad8.original_progress_callbacks
    b=original_secondary_947af0.original_progress_callbacks
    if {v.original_event_pointer for v in a} & {v.original_event_pointer for v in b}:
        raise OriginalPResultsEventSourceError(
            "source original date event pointer assigned to two different native registries")
    return OriginalPResultsTwoCollectionSourceReceipt(
        original_primary_947ad8,original_secondary_947af0,a+b,
        original_primary_947ad8.original_6168c0_return_al_nonzero,
        original_primary_947ad8.original_6168c0_return_al_nonzero,
        original_secondary_947af0.original_6168c0_return_al_nonzero,
    )


def source_original_4a8260_native_progress_counter_receipts(
    *, original_two_collection_receipt: OriginalPResultsTwoCollectionSourceReceipt,
    original_before_processed_64: int,
    original_first_collection_4a7210_total_68: int,
) -> tuple[OriginalResultsProgress, ...]:
    if type(original_two_collection_receipt) is not OriginalPResultsTwoCollectionSourceReceipt:
        raise OriginalPResultsEventSourceError(
            "original 4A8260 two native collection receipt required")
    before=original_before_processed_64
    total=original_first_collection_4a7210_total_68
    if (type(before) is not int or type(total) is not int
        or not 0<=before<=SOURCE_PRESULTS_NATIVE_SIGNED_MAX
        or not 0<=total<=SOURCE_PRESULTS_NATIVE_SIGNED_MAX
        or before+len(original_two_collection_receipt.ordered_source_callbacks)>
            SOURCE_PRESULTS_NATIVE_SIGNED_MAX):
        raise OriginalPResultsEventSourceError(
            "actual original PResults+64/+68 counters required without signed overflow")
    return tuple(OriginalResultsProgress(before+i,total) for i,_ in enumerate(
        original_two_collection_receipt.ordered_source_callbacks,1))
