"""Source-qualified original PEAMail small-list sorting and eight-row window.

Original footballmanager.exe SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
The original PEAMail +0x68 filter runs at 0x472680; sorter 0x472880:
0x472919..0x472920 selects the <=16-pointer insertion path; 0x47293D..
0x4729A4 inserts each later pointer using native strict binary comparators.
Longer lists enter 0x4729AB..0x472B4B hybrid partition/sort: NOT modeled.
This source slice is restricted to initially delivered, unmodified,
native-class-verified EAMPlayerAskTransferListsub records.

It does not synthesize original record+0x1C string, category labels,
message status transitions, row fonts/bitmaps, detail dialog or GUI input.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from original_eamail_mailbox import OriginalDeliveredEAMail
from original_eamail_language import load_verified_original_eamail_language
from original_eamail_native_filter import (
    OriginalEAMailFilterSourceError,
    original_filter_initial_transfer_mail,
)
from original_eamail_source_contract import (
    OriginalEAMailFilteredWindow,
    original_eamail_filtered_window,
)


ORIGINAL_EAMAIL_SORTER_VA = 0x472880
ORIGINAL_EAMAIL_SMALL_INSERTION_VA = 0x47293D
ORIGINAL_EAMAIL_SMALL_THRESHOLD = 16
ORIGINAL_EAMAIL_SORT_COMPARATORS = (
    0x472C80,  # first status bit 0x01
    0x472CA0,  # second status bit 0x02
    0x472BA0,  # source record +0x1C string
    0x472C00,  # source record virtual +0x18 string
    0x472C60,  # native numeric record date descending
)


@dataclass(frozen=True)
class OriginalInitialEAMailSortedWindow:
    """Source-selected initial transfer messages in an original eight-row slice.

    The list order is source-qualified for <=16 initially-unmodified transfer
    messages using original small-list sorter. The result is still NOT a
    rendered CMessageList, actionable message or physical pointer region.
    """

    selected_filter_index: int
    selected_sort_index: int
    native_comparator_va: int
    original_filtered_count: int
    original_sorted_rows: tuple[OriginalDeliveredEAMail, ...]
    viewport: OriginalEAMailFilteredWindow


def original_initial_transfer_eam_sorted_window(
    selected_user_delivered: tuple[OriginalDeliveredEAMail, ...],
    *,
    filter_index: int,
    sort_index: int | None,
    scroll_offset: int = 0,
) -> OriginalInitialEAMailSortedWindow:
    """Exact source small-array sort and native viewport for proven input only.

    Original sort choice index 4 is the fallback when none is selected.
    The two status comparators can use the independently verified immutable
    0x06 initial record flags: bit1 always false, bit2 always true.
    Their strict comparisons are always false, so insertion preserves
    delivered-owner order for the <=16-native algorithm.

    The date comparator uses the source scheduled envelope date (record+4)
    and original strict greater-than; the port's date is its source-backed
    chronological representation for these records. Equal-date rows preserve
    original insertion order. Source-exact native +0x18 produces the SAME
    'Transfer List' caption for every initial subtype record (IDX 1313),
    so native sort3 is a strict tie and preserves original mailbox order.
    Native record+0x1C descriptor resolves each specific player and is still
    unknown in actual byte output: source sort2 refuses >=2 rows.
    """
    filtered = original_filter_initial_transfer_mail(
        selected_user_delivered, filter_index,
    )
    if sort_index is not None and (type(sort_index) is not int or not 0 <= sort_index < 5):
        raise OriginalEAMailFilterSourceError(
            "Exactly one native order-control index 0..4 is required"
        )
    selected = 4 if sort_index is None else sort_index
    rows = list(filtered.filtered_in_native_mailbox_order)
    if len(rows) > ORIGINAL_EAMAIL_SMALL_THRESHOLD:
        raise OriginalEAMailFilterSourceError(
            "Native original >16 pointer hybrid sorter not yet source-qualified"
        )
    if selected == 2 and len(rows) > 1:
        raise OriginalEAMailFilterSourceError(
            "Original record +0x1C player-specific source string bytes unresolved"
        )
    # The initial class constructor/status producer gives every included
    # record status 0x06. Source comparator 0/1 thus returns false on all
    # pairs; their insertion path is stable original mailbox ordering.
    # The fourth/native sort3 compares identical source-qualified +0x18
    # EnglishEAM.idx ordinal 1313 'Transfer List' for this one class,
    # so strict text comparator 0x472C00 also returns false on all pairs.
    if selected == 4:
        for row in rows:
            if type(row.record_date) is not date:
                raise OriginalEAMailFilterSourceError(
                    "Source scheduled envelope record date not qualified"
                )
        # Original source 47293D..4729A4 is insertion, including two
        # strict-compare branches. The equivalent order for this native
        # date comparator moves only strictly newer records before older ones.
        for i in range(1, len(rows)):
            current = rows[i]
            pos = i
            while pos > 0 and current.record_date > rows[pos - 1].record_date:
                rows[pos] = rows[pos - 1]
                pos -= 1
            rows[pos] = current
    ordered = tuple(rows)
    view = original_eamail_filtered_window(
        ordered, scroll_offset, native_filtered_array_qualified=True,
    )
    return OriginalInitialEAMailSortedWindow(
        selected_filter_index=filtered.selected_filter_index,
        selected_sort_index=selected,
        native_comparator_va=ORIGINAL_EAMAIL_SORT_COMPARATORS[selected],
        original_filtered_count=len(ordered),
        original_sorted_rows=ordered,
        viewport=view,
    )


def build_selected_user_initial_eamail_window(
    source_bridge: object,
    *,
    filter_index: int,
    sort_index: int | None,
    scroll_offset: int = 0,
) -> OriginalInitialEAMailSortedWindow:
    """Build the native data+viewport from the actual selected human manager.

    The supplied read-only presentation bridge must verify the actual
    DBRUser+0x6B4 recipient, and reject pending MPM or another manager's mail.
    No importing the gameplay runtime into its source-presentation bridge,
    no substitute generic default (unregistered/unknown original user fails).
    """
    reader = getattr(source_bridge, "source_delivered_mailbox_for_selected_user", None)
    if not callable(reader):
        raise OriginalEAMailFilterSourceError(
            "Original registered selected-human mailbox reader is required"
        )
    return original_initial_transfer_eam_sorted_window(
        reader(),
        filter_index=filter_index,
        sort_index=sort_index,
        scroll_offset=scroll_offset,
    )


@dataclass(frozen=True)
class OriginalInitialEAMailCaptionedWindow:
    """Actual source-language title data for real visible selected-user rows.

    The native row title resource has been proven for the initial
    EAMPlayerAskTransferListsub ONLY. Original row child/font/render positions,
    body/action/flag changes and GUI input are deliberately not synthesized.
    """
    window: OriginalInitialEAMailSortedWindow
    visible_original_subjects: tuple[str, ...]


def build_source_captioned_selected_user_initial_eamail_window(
    source_bridge: object,
    *,
    original_source_root: str | Path,
    filter_index: int,
    sort_index: int | None,
    scroll_offset: int = 0,
) -> OriginalInitialEAMailCaptionedWindow:
    """Project the real selected registered manager mailbox to source captions.

    Load SHA-checked original EnglishEAM bytes, reproduce native filter and
    <=16 native insertion order, then resolve only the source-proved
    EAMPlayerAskTransferListsub +0x18 title through IDX ordinal 1313.
    Never use pending events or generic English string fallback.
    """
    resource = load_verified_original_eamail_language(original_source_root)
    title = resource.original_player_asks_transfer_list_subject()
    window = build_selected_user_initial_eamail_window(
        source_bridge,
        filter_index=filter_index,
        sort_index=sort_index,
        scroll_offset=scroll_offset,
    )
    return OriginalInitialEAMailCaptionedWindow(
        window=window,
        visible_original_subjects=(
            (title,) * len(window.viewport.visible_rows)
        ),
    )
