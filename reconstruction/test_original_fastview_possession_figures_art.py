from pathlib import Path
import unittest

from gate14_possession_figures import (
    SIDE0_TEXT_RECT,
    SIDE1_TEXT_RECT,
    NEUTRAL_TEXT_RECT,
    SOURCE_TEXT_FONT_ATLAS_SIZE,
    SOURCE_TEXT_FONT_BYTE_SIZE,
    SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
    SOURCE_TEXT_FONT_SHA256,
)
from original_fastview_possession_figures_art import (
    OriginalFastViewPossessionFiguresArtError,
    build_possession_figures_art,
    load_verified_possession_figures_font,
)


class OriginalFastViewPossessionFiguresArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.font = load_verified_possession_figures_font(cls.repo_root)

    def test_staged_source_font_identity_and_metrics_are_exact(self):
        self.assertEqual(SOURCE_TEXT_FONT_BYTE_SIZE, 83174)
        self.assertEqual(
            SOURCE_TEXT_FONT_SHA256,
            "4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd",
        )
        self.assertEqual(SOURCE_TEXT_FONT_ATLAS_SIZE, (1633, 18))
        self.assertEqual(SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT, 20)
        self.assertEqual(
            (self.font.atlas_width, self.font.atlas_height),
            (1633, 18),
        )
        self.assertEqual(self.font.native_line_height(), 20)

    def test_exact_percentage_art_uses_control_top_left_and_white_endpoint(self):
        art = build_possession_figures_art(self.font, 45, 20)
        self.assertEqual(
            [
                (
                    row.source.text,
                    row.line_origin,
                    row.clip_rect,
                    row.native_color_16,
                    (row.glyph_width, row.glyph_height),
                )
                for row in art.rows
            ],
            [
                ("35%", (311, 181), SIDE1_TEXT_RECT, 0xFFFF, (27, 17)),
                ("20%", (382, 181), NEUTRAL_TEXT_RECT, 0xFFFF, (28, 17)),
                ("45%", (454, 181), SIDE0_TEXT_RECT, 0xFFFF, (28, 17)),
            ],
        )
        for row in art.rows:
            self.assertEqual(
                len(row.glyph_rgba),
                row.glyph_width * row.glyph_height * 4,
            )
            self.assertTrue(any(row.glyph_rgba[i + 3] for i in range(0, len(row.glyph_rgba), 4)))
            self.assertTrue(art.match_role_orientation_recovered)
            self.assertTrue(art.human_side_orientation_requires_fixture_role)

    def test_all_source_percentage_strings_fit_40x18_controls(self):
        sizes = [
            (
                self.font.render_text_alpha(f"{value}%").width,
                self.font.render_text_alpha(f"{value}%").height,
            )
            for value in range(101)
        ]
        self.assertEqual(max(width for width, _ in sizes), 34)
        self.assertEqual(max(height for _, height in sizes), 17)
        self.assertTrue(all(width <= 40 and height <= 18 for width, height in sizes))

    def test_wrong_font_object_fails_closed(self):
        with self.assertRaises(OriginalFastViewPossessionFiguresArtError):
            build_possession_figures_art(object(), 45, 20)


if __name__ == "__main__":
    unittest.main()
