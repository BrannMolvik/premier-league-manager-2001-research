"""Source original Inbox ID3/ID0 font masks — not final colored text pixels."""
from dataclasses import replace
from pathlib import Path
from unittest import TestCase, main

from original_eamail_plain_glyph_masks import (
    ORIGINAL_EAMAIL_NATIVE_PLAIN_CHILD_IDS,
    ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA,
    OriginalEAMailGlyphError,
    original_eamail_plain_field_glyph_masks,
)
from original_management_canvas import build_management_canvas_frame
from original_management_presenter import OriginalManagementPresenter
from original_management_text import load_verified_management_text_resources
from test_original_eamail_live_host_route import (
    FixtureEAMBridge, delivered, ordinary_inbox,
)


def source_rows_with_font():
    session = ordinary_inbox()
    delivered(session)
    presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
    presenter.source_accepted_pmenu_action("title", 1, 0)
    presenter.source_accepted_pmenu_action("child", 0x65, 0)
    visible = build_management_canvas_frame(presenter).presentation.eamail
    root = Path(__file__).resolve().parents[1] / "original_assets/source"
    return visible, load_verified_management_text_resources(root)


class OriginalEAMailPlainGlyphTests(TestCase):
    def test_real_original_delivered_title_and_date_alpha_only(self):
        rows, resources = source_rows_with_font()
        result = original_eamail_plain_field_glyph_masks(rows, resources)
        self.assertEqual(ORIGINAL_EAMAIL_NATIVE_PLAIN_CHILD_IDS, (3, 0))
        self.assertEqual(len(result), 2)
        self.assertEqual([x.child_id for x in result], [3, 0])
        self.assertEqual([x.source_verified_text for x in result],
                         ["Transfer List", "1/Aug/2000"])
        self.assertEqual(result[0].screen_control_rect, (489, 178, 215, 16))
        self.assertEqual(result[1].screen_control_rect, (707, 178, 71, 16))
        for prepared in result:
            self.assertEqual(prepared.native_font_object_va,
                             ORIGINAL_EAMAIL_TEXT_FONT_OBJECT_VA)
            self.assertEqual(prepared.native_font_object_va, 0x9269F0)
            self.assertFalse(prepared.source_color_and_layout_verified)
            mask = prepared.glyph_mask
            self.assertGreater(mask.width, 0)
            self.assertGreater(mask.height, 0)
            self.assertEqual(len(mask.alpha), mask.width*mask.height)
            self.assertTrue(any(a for a in mask.alpha))
            self.assertNotIn("<", prepared.source_verified_text)

    def test_native_dynamic_player_markup_is_never_rasterized_as_literal(self):
        rows, resources = source_rows_with_font()
        # Production ID2 has original <T+P>/<T+C> markup; even when its
        # string is known it is excluded from the plain-font pipeline.
        native_row = rows.native_rows[0]
        fields = list(native_row.original_text_fields)
        self.assertEqual(fields[0].child_id, 2)
        fields[0] = replace(fields[0], source_verified_visible_text="<T+P>A. Player<T->")
        mutated = replace(rows, native_rows=(replace(native_row, original_text_fields=tuple(fields)),))
        result = original_eamail_plain_field_glyph_masks(mutated, resources)
        self.assertEqual([x.child_id for x in result], [3, 0])

    def test_unqualified_plain_markup_or_geometry_fails_closed(self):
        rows, resources = source_rows_with_font()
        original = rows.native_rows[0]
        for value in ("<T+P>Transfer List<T->", "Unsafe<", "Date>", "a\\x00b", ""):
            text = original.original_text_fields[1]
            replaced_field = replace(text, source_verified_visible_text=value)
            fields = (original.original_text_fields[0], replaced_field,
                      original.original_text_fields[2])
            changed = replace(rows, native_rows=(
                replace(original, original_text_fields=fields),))
            with self.subTest(value=repr(value)), self.assertRaises(OriginalEAMailGlyphError):
                original_eamail_plain_field_glyph_masks(changed, resources)
        date_field = original.original_text_fields[2]
        changed_date = replace(date_field, screen_rect=(700, 178, 71, 16))
        changed = replace(rows, native_rows=(
            replace(original, original_text_fields=(
                *original.original_text_fields[:2], changed_date)),))
        with self.assertRaisesRegex(OriginalEAMailGlyphError, "geometry"):
            original_eamail_plain_field_glyph_masks(changed, resources)

    def test_no_delivered_messages_emits_no_placeholder_text(self):
        rows, resources = source_rows_with_font()
        self.assertEqual(original_eamail_plain_field_glyph_masks(
            replace(rows, native_rows=(), original_filtered_count=0), resources), ())


if __name__ == "__main__":
    main()
