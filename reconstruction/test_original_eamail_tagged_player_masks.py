"""Original shipped T+P/T+C transferred-player markup fragment alpha only."""
from pathlib import Path
from unittest import TestCase, main

from original_eamail_player_name import (
    ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT,
    ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT,
    original_eam_player_initial_surname,
)
from original_eamail_tagged_player_masks import (
    OriginalEAMTaggedMaskError,
    native_player_markup_fragment_masks,
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
