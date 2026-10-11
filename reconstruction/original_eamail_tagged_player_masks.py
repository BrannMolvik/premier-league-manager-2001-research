"""Literal original transfer-mail player label fragments, native font alpha only.

Native 0x5CE784/0x5CE73C produce exactly the two original template
spellings in original_eamail_player_name. eCText 0x5D75B0 switches the
T tag state without switching its default 0x9269F0 font object.

This module extracts *source template fragments*, NOT final rendered runs:
native mutable-tag buffer edits, color selectors P/C, glyph positions,
caret state, clipping and on-screen placement remain source-unresolved.
Never join masks or treat the fragments as the native drawn string.
"""
from __future__ import annotations

from dataclasses import dataclass

from ea_font import EATextMask
from original_eamail_player_name import (
    ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT,
    ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT,
)
from original_management_text import OriginalManagementTextResources
from original_eamail_native_row_fields import OriginalEAMNativeVisibleRowsSource
from original_eamail_source_contract import ORIGINAL_EAMAIL_VISIBLE_ROWS, ORIGINAL_EAMAIL_TEXT_CHILDREN
from original_eamail_plain_glyph_masks import ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA


class OriginalEAMTaggedMaskError(ValueError):
    pass


SOURCE_NO_ASSOCIATION_TEMPLATE = "<T+P>%s<T->"
SOURCE_ASSOCIATION_TEMPLATE = "<T+P>%s<T-> @ <T+C>%s %s<T->"


@dataclass(frozen=True)
class OriginalEAMPlayerSourceFragmentMask:
    native_template_role: str
    source_text: str
    start_byte: int
    end_byte: int
    native_font_object_va: int
    glyph_alpha: EATextMask
    final_color_and_placement_verified: bool = False


def native_player_markup_fragment_masks(
    source_exact_row_text: str,
    resources: OriginalManagementTextResources,
) -> tuple[OriginalEAMPlayerSourceFragmentMask, ...]:
    """Parse only the two native player-label C-format templates.

    Every returned fragment is supplied by native name/caption values in the
    source-proven assembled label; ranges index the original CP1252 source
    string, not final bytes after native in-place control-tag mutations.
    """
    if type(resources) is not OriginalManagementTextResources:
        raise OriginalEAMTaggedMaskError("Original Zurich font resource required")
    if type(source_exact_row_text) is not str:
        raise OriginalEAMTaggedMaskError("Original native player label required")
    if (ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT != SOURCE_ASSOCIATION_TEMPLATE
            or ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT != SOURCE_NO_ASSOCIATION_TEMPLATE):
        raise OriginalEAMTaggedMaskError("Original native template evidence drifted")
    try:
        encoded = source_exact_row_text.encode("cp1252", "strict")
    except UnicodeEncodeError as exc:
        raise OriginalEAMTaggedMaskError("Original player label is not CP1252") from exc
    if not encoded or b"\x00" in encoded:
        raise OriginalEAMTaggedMaskError("Invalid original source player label bytes")
    opener, closer, middle, club_opener = "<T+P>", "<T->", " @ ", "<T+C>"
    if not source_exact_row_text.startswith(opener):
        raise OriginalEAMTaggedMaskError("Original player markup must begin T+P")
    value = source_exact_row_text[len(opener):]
    marker = closer + middle + club_opener
    if marker in value:
        player, suffix = value.split(marker, 1)
        if not suffix.endswith(closer):
            raise OriginalEAMTaggedMaskError("Original club markup terminator absent")
        club = suffix[:-len(closer)]
        if not club.endswith(" Football Club"):
            raise OriginalEAMTaggedMaskError("Original club language suffix is not source-qualified")
        data = [("player", player, len(opener))]
        sep_start = len(opener) + len(player) + len(closer)
        data.append(("separator", middle, sep_start))
        club_start = sep_start + len(middle) + len(club_opener)
        data.append(("club", club, club_start))
    else:
        if not value.endswith(closer):
            raise OriginalEAMTaggedMaskError("Original player markup terminator absent")
        player = value[:-len(closer)]
        data = [("player", player, len(opener))]
    if any((not fragment or "<" in fragment or ">" in fragment
            or chr(0) in fragment) for _, fragment, _ in data):
        raise OriginalEAMTaggedMaskError("Nested or empty original player template fragment")
    font = resources.league_tables_row_font
    output = []
    for role, text, start in data:
        try:
            mask = font.render_text_alpha(text)
        except ValueError as exc:
            raise OriginalEAMTaggedMaskError("Original font rejected native player fragment") from exc
        end = start + len(text.encode("cp1252", "strict"))
        output.append(OriginalEAMPlayerSourceFragmentMask(
            native_template_role=role, source_text=text,
            start_byte=start, end_byte=end,
            native_font_object_va=ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA,
            glyph_alpha=mask,
        ))
    return tuple(output)



@dataclass(frozen=True)
class OriginalEAMPlayerRowSourceFragments:
    native_node_serial: int
    screen_control_rect: tuple[int, int, int, int]
    raw_original_label: str
    fragments: tuple[OriginalEAMPlayerSourceFragmentMask, ...]
    native_final_draw_verified: bool = False


def native_visible_player_fragment_masks(
    visible: OriginalEAMNativeVisibleRowsSource,
    resources: OriginalManagementTextResources,
) -> tuple[OriginalEAMPlayerRowSourceFragments, ...]:
    """Prepare native ID2 source template fragments for current delivered rows.

    Output is a source-data/glyph *staging* seam only; there are no claimed
    original T+P / T+C colors, screen glyph baselines or popup actions.
    """
    if type(visible) is not OriginalEAMNativeVisibleRowsSource:
        raise OriginalEAMTaggedMaskError("Original delivered Inbox viewport required")
    if type(resources) is not OriginalManagementTextResources:
        raise OriginalEAMTaggedMaskError("Original source font resources required")
    if len(visible.native_rows) > ORIGINAL_EAMAIL_VISIBLE_ROWS:
        raise OriginalEAMTaggedMaskError("Original Inbox has only eight visible row owners")
    source_child_ids = tuple(x[0] for x in ORIGINAL_EAMAIL_TEXT_CHILDREN)
    if source_child_ids != (2, 3, 0):
        raise OriginalEAMTaggedMaskError("Native PMessageRow children drifted")
    outputs = []
    seen = set()
    for row in visible.native_rows:
        if row.original_internal_node_serial in seen:
            raise OriginalEAMTaggedMaskError("Repeated native source Inbox row")
        seen.add(row.original_internal_node_serial)
        if tuple(f.child_id for f in row.original_text_fields) != source_child_ids:
            raise OriginalEAMTaggedMaskError("Original player child ID2 owner mismatch")
        field = row.original_text_fields[0]
        text = field.source_verified_visible_text
        if text is None:
            continue
        rx, ry, _, _ = row.row_screen_rect
        if (field.screen_rect != (rx + 38, ry, 215, 16)
                or field.source_rect_in_row != (38, 0, 215, 16)):
            raise OriginalEAMTaggedMaskError("Native player child rectangle differs")
        fragments = native_player_markup_fragment_masks(text, resources)
        outputs.append(OriginalEAMPlayerRowSourceFragments(
            native_node_serial=row.original_internal_node_serial,
            screen_control_rect=field.screen_rect,
            raw_original_label=text,
            fragments=fragments,
        ))
    return tuple(outputs)
