import unittest

from gate14_fastview_league_table import (
    CURRENT_TABLE_GRID_1_BYTES,
    CURRENT_TABLE_GRID_1_PATH_LITERAL_VA,
    CURRENT_TABLE_GRID_1_SHA256,
    CURRENT_TABLE_GRID_1_SIZE,
    CURRENT_TABLE_GRID_2_BYTES,
    CURRENT_TABLE_GRID_2_PATH_LITERAL_VA,
    CURRENT_TABLE_GRID_2_SHA256,
    CURRENT_TABLE_GRID_2_SIZE,
    HEADING_RTTI,
    HEADING_TEXT_LOCAL_RECTS,
    HEADING_VFTABLE,
    LEAGUE_TABLE_COMPOSITE_PRIMARY_VFTABLE,
    LEAGUE_TABLE_COMPOSITE_SECONDARY_VFTABLE,
    LEAGUE_TABLE_COMPOSITE_SENDER_VFTABLE,
    LEAGUE_TABLE_SCREEN_ORIGIN,
    ROW_RTTI,
    ROW_TEXT_LOCAL_RECTS,
    ROW_VFTABLE,
    FastViewLeagueTableError,
    league_table_composite_frame,
    league_table_heading_rect,
    league_table_heading_text_rects,
    league_table_row_rect,
    league_table_row_text_rects,
    league_table_visible_row_count,
)


class FastViewLeagueTableTests(unittest.TestCase):
    def test_nested_class_ownership_and_exact_source_identity(self):
        self.assertEqual(HEADING_VFTABLE, 0x7CA3F0)
        self.assertEqual(HEADING_RTTI, ".?AVHeading@LeagueTableComposite@@")
        self.assertEqual(ROW_VFTABLE, 0x7CA3E8)
        self.assertEqual(ROW_RTTI, ".?AVRow@LeagueTableComposite@@")
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_PRIMARY_VFTABLE, 0x7CA400)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_SECONDARY_VFTABLE, 0x7CA3F8)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_SENDER_VFTABLE, 0x7CA40C)

        self.assertEqual(CURRENT_TABLE_GRID_1_BYTES, 4496)
        self.assertEqual(CURRENT_TABLE_GRID_1_SIZE, (381, 19))
        self.assertEqual(CURRENT_TABLE_GRID_1_PATH_LITERAL_VA, 0x829114)
        self.assertEqual(
            CURRENT_TABLE_GRID_1_SHA256,
            "db8114130becce71ba84f890ccd157606d04bf68501484df308564da28957a5f",
        )
        self.assertEqual(CURRENT_TABLE_GRID_2_BYTES, 4276)
        self.assertEqual(CURRENT_TABLE_GRID_2_SIZE, (381, 16))
        self.assertEqual(CURRENT_TABLE_GRID_2_PATH_LITERAL_VA, 0x8290B4)
        self.assertEqual(
            CURRENT_TABLE_GRID_2_SHA256,
            "e5a1b5688115cc8a63d47c738cf5af7f66f20eee9433292e47ee4e7c152ed70b",
        )

    def test_parent_call_fixes_heading_and_row_screen_geometry(self):
        self.assertEqual(LEAGUE_TABLE_SCREEN_ORIGIN, (382, 32))
        self.assertEqual(league_table_heading_rect(), (382, 32, 763, 51))
        self.assertEqual(league_table_row_rect(0), (382, 55, 763, 71))
        self.assertEqual(league_table_row_rect(1), (382, 74, 763, 90))
        self.assertEqual(league_table_row_rect(11), (382, 264, 763, 280))

    def test_heading_has_seven_exact_30_by_19_text_columns(self):
        self.assertEqual(len(HEADING_TEXT_LOCAL_RECTS), 7)
        self.assertEqual(
            league_table_heading_text_rects(),
            (
                (550, 32, 580, 51),
                (580, 32, 610, 51),
                (610, 32, 640, 51),
                (640, 32, 670, 51),
                (670, 32, 700, 51),
                (700, 32, 730, 51),
                (730, 32, 760, 51),
            ),
        )

    def test_row_has_nine_exact_text_rectangles_without_semantic_names(self):
        self.assertEqual(
            ROW_TEXT_LOCAL_RECTS,
            (
                (168, 0, 198, 16),
                (198, 0, 228, 16),
                (228, 0, 258, 16),
                (258, 0, 288, 16),
                (288, 0, 318, 16),
                (318, 0, 348, 16),
                (348, 0, 378, 16),
                (0, 0, 26, 16),
                (30, 0, 160, 16),
            ),
        )
        self.assertEqual(
            league_table_row_text_rects(0),
            (
                (550, 55, 580, 71),
                (580, 55, 610, 71),
                (610, 55, 640, 71),
                (640, 55, 670, 71),
                (670, 55, 700, 71),
                (700, 55, 730, 71),
                (730, 55, 760, 71),
                (382, 55, 408, 71),
                (412, 55, 542, 71),
            ),
        )

    def test_visible_row_count_matches_source_halfing_above_twelve(self):
        self.assertEqual(league_table_visible_row_count(1), 1)
        self.assertEqual(league_table_visible_row_count(12), 12)
        self.assertEqual(league_table_visible_row_count(13), 7)
        self.assertEqual(league_table_visible_row_count(20), 10)
        self.assertEqual(league_table_visible_row_count(24), 12)

    def test_frame_keeps_semantics_and_binary_import_fail_closed(self):
        frame = league_table_composite_frame(20)
        self.assertEqual(len(frame.row_grid_rects), 10)
        self.assertEqual(len(frame.row_text_rects), 10)
        self.assertFalse(frame.text_semantics_recovered)
        self.assertFalse(frame.bitmap_resources_imported)

    def test_invalid_counts_and_rows_fail_closed(self):
        for value in (0, -1, True, 1.5, "12"):
            with self.subTest(value=value):
                with self.assertRaises(FastViewLeagueTableError):
                    league_table_visible_row_count(value)
        with self.assertRaises(FastViewLeagueTableError):
            league_table_row_rect(-1)
        with self.assertRaises(FastViewLeagueTableError):
            league_table_row_text_rects(True)


if __name__ == "__main__":
    unittest.main()
