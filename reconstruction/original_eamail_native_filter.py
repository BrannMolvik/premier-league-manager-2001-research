"""Original PEAMail filter for the one source-qualified initial EAM subclass.

Original PE independently verified 11 Oct 2026 (SHA-256 833bf95e...b7cc3):
PEAMail::0x472680 selects one of 10 control indices; index 0 tests
record+8 bit0x04, index 1 accepts all, indices 2..9 compare record+0x0c.
EAMPlayerAskTransferListsub constructor 0x56FAD0 writes status=0x04,
category=5; 0x41B68B ORs 0x06, giving initial record status=0x06.

This is a manager-owned delivered-list FILTER only, preserving append order.
It does NOT claim to reconstruct PEAMail+0x68 sorted order, original
five comparison controls, native status labels, text/font/row graphics,
mutable read/action flags, mouse acceptance, or the GUI Inbox itself.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_eamail_mailbox import (
    EAM_PLAYER_ASK_TRANSFER_LIST_CLASS,
    OriginalDeliveredEAMail,
)


class OriginalEAMailFilterSourceError(ValueError):
    """The actual native record/status/category source is unqualified."""


ORIGINAL_EAMAIL_FILTER_OPTION_COUNT = 10
ORIGINAL_EAMAIL_FIRST_STATUS_FILTER_BIT = 0x04
ORIGINAL_TRANSFER_EAM_NATIVE_CATEGORY = 5
ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS = 0x06


@dataclass(frozen=True)
class OriginalInitialTransferEAMFilterResult:
    selected_filter_index: int
    source_delivered_count: int
    filtered_in_native_mailbox_order: tuple[OriginalDeliveredEAMail, ...]
    # Not an original PEAMail+0x68 sorted array or a final native row raster.
    sort_and_native_gui_unverified: bool = True


def original_filter_initial_transfer_mail(
    delivered_for_selected_source_user: tuple[OriginalDeliveredEAMail, ...],
    filter_index: int,
) -> OriginalInitialTransferEAMFilterResult:
    """Reproduce PEAMail::0x472680's ten native filter predicates for
    the **initial, not yet user-modified** source transfer-request class.

    The caller must independently prove the selected manager's DBRUser+0x6B4
    recipient ownership. No pending MPM queue or global union is accepted.
    The native filter's index-zero bit predicate does not establish a
    human-readable "unread" label.
    """
    if (type(delivered_for_selected_source_user) is not tuple
            or type(filter_index) is not int
            or not 0 <= filter_index < ORIGINAL_EAMAIL_FILTER_OPTION_COUNT):
        raise OriginalEAMailFilterSourceError(
            "Exact source qualified ten-control filter index and delivered tuple required"
        )
    for row in delivered_for_selected_source_user:
        if (type(row) is not OriginalDeliveredEAMail
                or row.event_class != EAM_PLAYER_ASK_TRANSFER_LIST_CLASS
                or row.native_status_decoded or row.original_screen_rendered):
            raise OriginalEAMailFilterSourceError(
                "Native initial transfer EAM record fields are not source qualified"
            )
    # 0x56FAD0 writes category5/status4; 0x41B68B ORs 0x06 and
    # 0x5CFA20 stamps scheduled date before original mailbox append.
    # This is NOT a guess about other subclasses or later status mutation.
    status = ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS
    category = ORIGINAL_TRANSFER_EAM_NATIVE_CATEGORY
    if filter_index == 0:
        accepted = bool(status & ORIGINAL_EAMAIL_FIRST_STATUS_FILTER_BIT)
    elif filter_index == 1:
        accepted = True
    else:
        accepted = category == filter_index
    return OriginalInitialTransferEAMFilterResult(
        selected_filter_index=filter_index,
        source_delivered_count=len(delivered_for_selected_source_user),
        filtered_in_native_mailbox_order=(
            delivered_for_selected_source_user if accepted else ()
        ),
    )
