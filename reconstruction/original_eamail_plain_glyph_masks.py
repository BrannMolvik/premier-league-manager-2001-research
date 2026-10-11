"""Native eCText *glyph alpha* preparation for qualified Inbox row fields.

The original PMessageRow constructor (0x46E737/0x46E774/0x46E7A5)
creates three eCText children, whose shared parser 0x5D75B0 initializes
font object 0x9269F0. Other work independently binds that exact object
to the shipped Zurich_BdXCn_BT_16pixel.fnt. This pure preparation seam
does not claim the source's final colors, tag editing, clipping, baseline,
bit4 visual gate, or a completed rendered Inbox.

Only original plain subject (ID3) and localized date (ID0) are rasterized.
ID2 can contain native <T+P>/<T+C> editing/markup and cannot safely
be treated as literal text or heuristically stripped of tags.
"""
from __future__ import annotations

from dataclasses import dataclass

from ea_font import EAFont, EATextMask
from original_eamail_native_row_fields import OriginalEAMNativeVisibleRowsSource
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_TEXT_CHILDREN, ORIGINAL_EAMAIL_VISIBLE_ROWS,
)
from original_management_text import (
    OriginalManagementTextResources,
    LEAGUE_TABLES_ROW_FONT_OBJECT_VA,
    LEAGUE_TABLES_ROW_FONT_SOURCE_PATH,
)


class OriginalEAMailGlyphError(ValueError):
    """Row text left the source-qualified native font/field boundary."""


ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA = 0x9269F0
ORIGINAL_EAMAIL_TEXT_FONT_SOURCE_PATH = LEAGUE_TABLES_ROW_FONT_SOURCE_PATH
ORIGINAL_EAMAIL_NATIVE_PLAIN_CHILD_IDS = (3, 0)


@dataclass(frozen=True)
class OriginalEAMailPlainGlyphMask:
    native_node_serial: int
    child_id: int
    source_verified_text: str
    screen_control_rect: tuple[int, int, int, int]
    native_font_object_va: int
    font_source_path: str
    glyph_mask: EATextMask
    # This representation is alpha only.  It cannot become a visible frame
    # without a separately verified native baseline/color/clip/visibility.
    source_color_and_layout_verified: bool = False


def original_eamail_plain_field_glyph_masks(
    visible: OriginalEAMNativeVisibleRowsSource,
    resources: OriginalManagementTextResources,
) -> tuple[OriginalEAMailPlainGlyphMask, ...]:
    """Prepare original uncolored alpha for known subject/date controls.

    The font is not a stand-in for dynamic <T> tags.  Later integration
    must independently trace 0x5D75B0 glyph color/position and editor
    mutation before painting the returned masks.
    """
    if (type(visible) is not OriginalEAMNativeVisibleRowsSource
            or type(resources) is not OriginalManagementTextResources):
        raise OriginalEAMailGlyphError(
            "Native Inbox viewport and verified source font resources required"
        )
    if LEAGUE_TABLES_ROW_FONT_OBJECT_VA != ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA:
        raise OriginalEAMailGlyphError("Original eCText default font owner drifted")
    if len(visible.native_rows) > ORIGINAL_EAMAIL_VISIBLE_ROWS:
        raise OriginalEAMailGlyphError("Original PMessageList has eight visible slots")
    native_ids = tuple(child_id for child_id, _rect, _buffer_offset
                       in ORIGINAL_EAMAIL_TEXT_CHILDREN)
    if native_ids != (2, 3, 0):
        raise OriginalEAMailGlyphError("Original PMessageRow native child order drifted")
    font: EAFont = resources.league_tables_row_font
    masks = []
    seen = set()
    for row in visible.native_rows:
        if row.original_internal_node_serial in seen:
            raise OriginalEAMailGlyphError("Duplicated native Inbox row owner")
        seen.add(row.original_internal_node_serial)
        if tuple(f.child_id for f in row.original_text_fields) != native_ids:
            raise OriginalEAMailGlyphError("Native Inbox child identity mismatch")
        for field in row.original_text_fields:
            if field.child_id not in ORIGINAL_EAMAIL_NATIVE_PLAIN_CHILD_IDS:
                continue
            text = field.source_verified_visible_text
            if text is None:
                continue
            if (type(text) is not str or not text
                    or any(ch in text for ch in "<>") or chr(0) in text):
                raise OriginalEAMailGlyphError(
                    "Only source-verified non-markup Inbox text can use plain glyphs"
                )
            screen_x, screen_y, cw, ch = field.screen_rect
            rx, ry, rw, rh = row.row_screen_rect
            cx, cy, expected_w, expected_h = field.source_rect_in_row
            if ((cw, ch) != (expected_w, expected_h)
                    or (screen_x, screen_y) != (rx + cx, ry + cy)
                    or not (rw > 0 and rh > 0 and cw > 0 and ch > 0)):
                raise OriginalEAMailGlyphError("Native eCText control geometry drifted")
            try:
                alpha = font.render_text_alpha(text)
            except ValueError as exc:
                raise OriginalEAMailGlyphError("Original font cannot render native text") from exc
            masks.append(OriginalEAMailPlainGlyphMask(
                native_node_serial=row.original_internal_node_serial,
                child_id=field.child_id,
                source_verified_text=text,
                screen_control_rect=field.screen_rect,
                native_font_object_va=ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA,
                font_source_path=ORIGINAL_EAMAIL_TEXT_FONT_SOURCE_PATH,
                glyph_mask=alpha,
            ))
    return tuple(masks)
