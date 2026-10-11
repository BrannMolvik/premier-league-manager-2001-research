"""Original PMessageRow three native text columns for source-proven Inbox records.

Canonical shipped PE SHA-256 833bf95e...b7cc3. 0x471ED7..0x471F56
builds native 0x79c-byte PMessageRow from PEAMail+0x68 selected pointers:
- virtual record +0x18 -> row+0x74 -> PMessageRow child ID3;
- native typed record+0x1C via 0x5CE6A0 -> row+0x174 -> child ID2;
- native record+0x04 through 0x64CCD0/0x471FA0 -> row+0x274 -> child ID0.
Constructor 0x46E680 binds three native child rectangles, original row
532x18, CMessageList eight visible rows pitched at 20 px.

Only the first native title is text-exact for the initial transfer subclass.
The player-specific native string and localized date bytes are unresolved;
their typed provenance is retained, not replaced by guessed caption/date.
Native GUI is NOT painted and event handlers are NOT asserted here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from original_eamail_native_small_window import (
    OriginalInitialEAMailCaptionedWindow,
    build_source_captioned_selected_user_initial_eamail_window,
)
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_LIST_RECT,
    ORIGINAL_EAMAIL_PANEL_RECT,
    ORIGINAL_EAMAIL_ROW_PITCH,
    ORIGINAL_EAMAIL_ROW_RECT,
    ORIGINAL_EAMAIL_TEXT_CHILDREN,
    ORIGINAL_EAMAIL_VISIBLE_ROWS,
)


class OriginalEAMailRowFieldSourceError(ValueError):
    """Current record is not qualified for one original native row field."""


ORIGINAL_EAMAIL_ROW_FACTORY_VA = 0x471D20
ORIGINAL_EAMAIL_ROW_TITLE_VIRTUAL_OFFSET = 0x18
ORIGINAL_EAMAIL_ROW_RECORD_PLAYER_FIELD_OFFSET = 0x1C
ORIGINAL_EAMAIL_ROW_RECORD_DATE_FIELD_OFFSET = 0x04
ORIGINAL_EAMAIL_ROW_PLAYER_STRING_RESOLVER_VA = 0x5CE6A0
ORIGINAL_EAMAIL_ROW_DATE_BUFFER_BUILDER_VA = 0x64CCD0
ORIGINAL_EAMAIL_ROW_DATE_WRITER_VA = 0x471FA0
ORIGINAL_EAMAIL_ROW_INITIAL_BITMAP_VA = 0x945E30

ORIGINAL_EAMAIL_ROW_SCREEN_START = (
    ORIGINAL_EAMAIL_PANEL_RECT[0] + ORIGINAL_EAMAIL_LIST_RECT[0],
    ORIGINAL_EAMAIL_PANEL_RECT[1] + ORIGINAL_EAMAIL_LIST_RECT[1],
)
ORIGINAL_ROW_NATIVE_FIELDS = (
    (2, "player_typed_descriptor", ORIGINAL_EAMAIL_ROW_RECORD_PLAYER_FIELD_OFFSET),
    (3, "original_subject_virtual", ORIGINAL_EAMAIL_ROW_TITLE_VIRTUAL_OFFSET),
    (0, "original_date_localization", ORIGINAL_EAMAIL_ROW_RECORD_DATE_FIELD_OFFSET),
)


@dataclass(frozen=True)
class OriginalEAMNativeTextField:
    child_id: int
    origin_va: int
    source_kind: str
    source_rect_in_row: tuple[int, int, int, int]
    screen_rect: tuple[int, int, int, int]
    # Only the source-verified original EnglishEAM title is available as
    # visible CP1252; the other two MUST remain unrendered until exact proof.
    source_verified_visible_text: str | None


@dataclass(frozen=True)
class OriginalEAMNativeRowSource:
    native_visible_ordinal: int
    original_internal_node_serial: int
    native_record_class: str
    qualified_player_id: int
    qualified_record_date: date
    original_title: str
    row_screen_rect: tuple[int, int, int, int]
    original_text_fields: tuple[OriginalEAMNativeTextField, ...]
    source_default_background_va: int = ORIGINAL_EAMAIL_ROW_INITIAL_BITMAP_VA
    native_full_text_and_art_rendered: bool = False


@dataclass(frozen=True)
class OriginalEAMNativeVisibleRowsSource:
    original_filtered_count: int
    original_max_scroll_offset: int
    original_scroll_offset: int
    native_rows: tuple[OriginalEAMNativeRowSource, ...]
    original_gui_accepted: bool = False


def project_original_native_eam_row_fields(
    captioned: OriginalInitialEAMailCaptionedWindow,
) -> OriginalEAMNativeVisibleRowsSource:
    """Source-exact column assignment, without invented localization/layout."""
    if type(captioned) is not OriginalInitialEAMailCaptionedWindow:
        raise OriginalEAMailRowFieldSourceError(
            "Native selected-user original captioned Inbox window is required"
        )
    window = captioned.window
    visible = window.viewport.visible_rows
    if (len(captioned.visible_original_subjects) != len(visible)
            or len(visible) > ORIGINAL_EAMAIL_VISIBLE_ROWS
            or len(ORIGINAL_EAMAIL_TEXT_CHILDREN) != 3):
        raise OriginalEAMailRowFieldSourceError(
            "The selected native CMessageList eight-row projection is invalid"
        )
    result: list[OriginalEAMNativeRowSource] = []
    for i, (record, title) in enumerate(
        zip(visible, captioned.visible_original_subjects)
    ):
        if title != "Transfer List":
            raise OriginalEAMailRowFieldSourceError(
                "Only source-proven original transfer caption is qualified"
            )
        # PMessageRow's created physical row is a source relative to its
        # original list and panel owners; this is not click acceptance.
        left, top = ORIGINAL_EAMAIL_ROW_SCREEN_START
        row_rect = (
            left, top + i * ORIGINAL_EAMAIL_ROW_PITCH,
            ORIGINAL_EAMAIL_ROW_RECT[2], ORIGINAL_EAMAIL_ROW_RECT[3],
        )
        children: list[OriginalEAMNativeTextField] = []
        for (child_id, kind, origin_va), (source_id, rect, _buffer_offset) in zip(
            ORIGINAL_ROW_NATIVE_FIELDS, ORIGINAL_EAMAIL_TEXT_CHILDREN
        ):
            if child_id != source_id:
                raise OriginalEAMailRowFieldSourceError(
                    "Native original PMessageRow column IDs do not match owner"
                )
            x, y, width, height = rect
            children.append(OriginalEAMNativeTextField(
                child_id=child_id,
                origin_va=origin_va,
                source_kind=kind,
                source_rect_in_row=rect,
                screen_rect=(left+x, row_rect[1]+y, width, height),
                source_verified_visible_text=title if child_id == 3 else None,
            ))
        result.append(OriginalEAMNativeRowSource(
            native_visible_ordinal=window.viewport.scroll_offset+i,
            original_internal_node_serial=record.node_serial,
            native_record_class=record.event_class,
            qualified_player_id=record.player_id,
            qualified_record_date=record.record_date,
            original_title=title,
            row_screen_rect=row_rect,
            original_text_fields=tuple(children),
        ))
    return OriginalEAMNativeVisibleRowsSource(
        original_filtered_count=window.original_filtered_count,
        original_max_scroll_offset=window.viewport.max_scroll_offset,
        original_scroll_offset=window.viewport.scroll_offset,
        native_rows=tuple(result),
    )


def build_selected_user_original_eam_source_rows(
    source_bridge: object,
    *,
    original_source_root: str | Path,
    filter_index: int,
    sort_index: int | None,
    scroll_offset: int = 0,
) -> OriginalEAMNativeVisibleRowsSource:
    """Prepare the real manager's original full row-column source ownership.

    This is the layer immediately below a future native art/font renderer.
    No pending queue, inferred row statuses or imaginary click routes.
    """
    return project_original_native_eam_row_fields(
        build_source_captioned_selected_user_initial_eamail_window(
            source_bridge,
            original_source_root=original_source_root,
            filter_index=filter_index,
            sort_index=sort_index,
            scroll_offset=scroll_offset,
        )
    )
