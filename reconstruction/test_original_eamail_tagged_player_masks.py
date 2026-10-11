"""Original shipped T+P/T+C transferred-player markup fragment alpha only."""
from dataclasses import replace
from pathlib import Path
from unittest import TestCase, main

from original_eamail_player_name import (
    ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT,
    ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT,
    original_eam_player_initial_surname,
)
from original_eamail_tagged_player_masks import (
    OriginalEAMTaggedMaskError,
    native_player_markup_fragment_masks, native_visible_player_fragment_masks,
)
from original_management_text import load_verified_management_text_resources


def original_font():
    root = Path(__file__).resolve().parents[1] / "original_assets/source"
    return load_verified_management_text_resources(root)


class NativeEAMPlayerTaggedMaskTests(TestCase):
    def test_original_no_association_format_keeps_one_player_run(self):
        native_name = original_eam_player_initial_surname("Kari", "Larsen")
        formatted = ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT % native_name
        runs = native_player_markup_fragment_masks(formatted, original_font())
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0].native_template_role, "player")
        self.assertEqual(runs[0].source_text, "K. Larsen")
        self.assertEqual((runs[0].start_byte, runs[0].end_byte),
                         (5, 5 + len(native_name)))
        self.assertFalse(runs[0].final_color_and_placement_verified)
        self.assertEqual(runs[0].source_hit_selector_byte, ord("P"))
        self.assertFalse(runs[0].native_hit_target_and_action_verified)
        self.assertTrue(any(runs[0].glyph_alpha.alpha))

    def test_original_positive_club_format_preserves_all_source_runs(self):
        player = "K. Larsen"
        club = "Arsenal"
        suffix = "Football Club"
        text = ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT % (
            player, club, suffix,
        )
        runs = native_player_markup_fragment_masks(text, original_font())
        self.assertEqual([run.native_template_role for run in runs],
                         ["player", "separator", "club"])
        self.assertEqual([run.source_text for run in runs],
                         ["K. Larsen", " @ ", "Arsenal Football Club"])
        self.assertEqual([run.source_hit_selector_byte for run in runs],
                         [ord("P"), 0, ord("C")])
        self.assertTrue(all(not run.native_hit_target_and_action_verified for run in runs))
        for run in runs:
            self.assertEqual(
                text[run.start_byte:run.end_byte],
                run.source_text,
            )
            self.assertEqual(run.native_font_object_va, 0x9269F0)
            self.assertFalse(run.final_color_and_placement_verified)
            self.assertGreater(run.glyph_alpha.width, 0)
            self.assertEqual(len(run.glyph_alpha.alpha),
                             run.glyph_alpha.width * run.glyph_alpha.height)

    def test_actual_registered_human_delivered_player_id2_fragment_owner(self):
        from test_original_eamail_plain_glyph_masks import source_rows_with_font
        visible, font = source_rows_with_font()
        native_text = visible.native_rows[0].original_text_fields[0].source_verified_visible_text
        self.assertIsNotNone(native_text)
        self.assertTrue(native_text.startswith("<T+P>"))
        rows = native_visible_player_fragment_masks(visible, font)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].native_node_serial,
                         visible.native_rows[0].original_internal_node_serial)
        self.assertEqual(rows[0].screen_control_rect, (271, 178, 215, 16))
        self.assertEqual(rows[0].raw_original_label, native_text)
        self.assertEqual(rows[0].fragments[0].source_hit_selector_byte, ord("P"))
        if len(rows[0].fragments) == 3:
            self.assertEqual([frag.source_hit_selector_byte
                              for frag in rows[0].fragments],
                             [ord("P"), 0, ord("C")])
        self.assertFalse(rows[0].native_final_draw_verified)
        self.assertTrue(all(not fragment.final_color_and_placement_verified
                            for fragment in rows[0].fragments))
        self.assertEqual(native_visible_player_fragment_masks(
            replace(visible, native_rows=(), original_filtered_count=0), font), ())

    def test_real_owner_rejects_invalid_markup_and_geometry(self):
        from test_original_eamail_plain_glyph_masks import source_rows_with_font
        visible, font = source_rows_with_font()
        native_row = visible.native_rows[0]
        child = native_row.original_text_fields[0]
        bad = replace(child, source_verified_visible_text="<T+P>No end")
        changed = replace(visible, native_rows=(replace(
            native_row, original_text_fields=(bad, *native_row.original_text_fields[1:])),))
        with self.assertRaises(OriginalEAMTaggedMaskError):
            native_visible_player_fragment_masks(changed, font)
        bad = replace(child, screen_rect=(0, 0, 215, 16))
        changed = replace(visible, native_rows=(replace(
            native_row, original_text_fields=(bad, *native_row.original_text_fields[1:])),))
        with self.assertRaisesRegex(OriginalEAMTaggedMaskError, "rectangle"):
            native_visible_player_fragment_masks(changed, font)

    def test_alternate_native_markup_or_corrupt_values_are_rejected(self):
        font = original_font()
        for text in (
            "K. Larsen", "<T+X>Bad<T->", "<T+P>Name",
            "<T+P><T->", "<T+P>A<T-> @ <T+C>Bad",
            "<T+P>A<T-> @ <T+C>Club<T->",
            "<T+P>A<T-> @ <T+C>Club Football Club<T+C>",
            "<T+P>A<T-> @ <T+P>Club Football Club<T->",
            "<T+P>A" + chr(0) + "<T->",
            "<T+P>A ☃<T->",
        ):
            with self.subTest(text=repr(text)), self.assertRaises(OriginalEAMTaggedMaskError):
                native_player_markup_fragment_masks(text, font)


if __name__ == "__main__":
    main()
