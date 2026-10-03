import unittest

from gate14_fastview_league_table import (
    CURRENT_TABLE_GRID_1,
    CURRENT_TABLE_GRID_2,
    FASTVIEW_CURRENT_TABLE_GRID_RESOURCES,
    LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA,
    LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA,
    LEAGUE_TABLE_COMPOSITE_PRIMARY_VFTABLE,
    LEAGUE_TABLE_COMPOSITE_SECONDARY_VFTABLE,
    LEAGUE_TABLE_EVENT_SCORE_BASE_VFTABLE,
    LEAGUE_TABLE_EVENT_UPDATE_BASE_VFTABLE,
    LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA,
    LEAGUE_TABLE_HEADING_TEXT_LOCAL_RECTS,
    LEAGUE_TABLE_HEADING_VFTABLE,
    LEAGUE_TABLE_ORIGIN,
    LEAGUE_TABLE_ROW_CONSTRUCTOR_VA,
    LEAGUE_TABLE_ROW_STEP,
    LEAGUE_TABLE_ROW_TEXT_LOCAL_RECTS,
    LEAGUE_TABLE_ROW_VFTABLE,
    FastViewLeagueTableError,
    league_table_heading_rects,
    league_table_row_origin,
    league_table_row_rects,
    league_table_visible_row_count,
)


class FastViewLeagueTableTests(unittest.TestCase):
    def test_current_table_assets_have_distinct_heading_and_row_owners(self):
        self.assertEqual(CURRENT_TABLE_GRID_1.size, (381, 19))
        self.assertEqual(CURRENT_TABLE_GRID_1.byte_size, 4496)
        self.assertEqual(CURRENT_TABLE_GRID_1.path_literal_va, 0x829114)
        self.assertEqual(
            CURRENT_TABLE_GRID_1.sha256,
            "db8114130becce71ba84f890ccd157606d04bf68501484df308564da28957a5f",
        )
        self.assertEqual(CURRENT_TABLE_GRID_1.owner, "LeagueTableComposite::Heading")

        self.assertEqual(CURRENT_TABLE_GRID_2.size, (381, 16))
        self.assertEqual(CURRENT_TABLE_GRID_2.byte_size, 4276)
        self.assertEqual(CURRENT_TABLE_GRID_2.path_literal_va, 0x8290B4)
        self.assertEqual(
            CURRENT_TABLE_GRID_2.sha256,
            "e5a1b5688115cc8a63d47c738cf5af7f66f20eee9433292e47ee4e7c152ed70b",
        )
        self.assertEqual(CURRENT_TABLE_GRID_2.owner, "LeagueTableComposite::Row")
        self.assertEqual(len(FASTVIEW_CURRENT_TABLE_GRID_RESOURCES), 2)
        self.assertFalse(CURRENT_TABLE_GRID_1.imported)
        self.assertFalse(CURRENT_TABLE_GRID_2.imported)

    def test_rtti_and_constructor_contract_is_source_bound(self):
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA, 0x51E000)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA, 0x523472)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_PRIMARY_VFTABLE, 0x7CA400)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_SECONDARY_VFTABLE, 0x7CA3F8)
        self.assertEqual(LEAGUE_TABLE_EVENT_SCORE_BASE_VFTABLE, 0x7CA3B0)
        self.assertEqual(LEAGUE_TABLE_EVENT_UPDATE_BASE_VFTABLE, 0x7CA40C)
        self.assertEqual(LEAGUE_TABLE_ROW_CONSTRUCTOR_VA, 0x51D730)
        self.assertEqual(LEAGUE_TABLE_ROW_VFTABLE, 0x7CA3E8)
        self.assertEqual(LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA, 0x51DCB0)
        self.assertEqual(LEAGUE_TABLE_HEADING_VFTABLE, 0x7CA3F0)

    def test_heading_grid_and_seven_text_rectangles_are_exact(self):
        self.assertEqual(LEAGUE_TABLE_ORIGIN, (382, 32))
        self.assertEqual(
            LEAGUE_TABLE_HEADING_TEXT_LOCAL_RECTS,
            (
                (168, 0, 198, 19),
                (198, 0, 228, 19),
                (228, 0, 258, 19),
                (258, 0, 288, 19),
                (288, 0, 318, 19),
                (318, 0, 348, 19),
                (348, 0, 378, 19),
            ),
        )
        grid, text = league_table_heading_rects()
        self.assertEqual(grid, (382, 32, 763, 51))
        self.assertEqual(text[0], (550, 32, 580, 51))
        self.assertEqual(text[-1], (730, 32, 760, 51))

    def test_row_grid_and_nine_text_rectangles_are_exact(self):
        self.assertEqual(
            LEAGUE_TABLE_ROW_TEXT_LOCAL_RECTS,
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
        grid0, text0 = league_table_row_rects(0)
        self.assertEqual(grid0, (382, 55, 763, 71))
        self.assertEqual(text0[0], (550, 55, 580, 71))
        self.assertEqual(text0[7], (382, 55, 408, 71))
        self.assertEqual(text0[8], (412, 55, 542, 71))

        self.assertEqual(league_table_row_origin(1), (382, 74))
        grid1, _ = league_table_row_rects(1)
        self.assertEqual(grid1, (382, 74, 763, 90))
        self.assertEqual(LEAGUE_TABLE_ROW_STEP, 19)

    def test_source_count_transform_is_exact_and_neutrally_named(self):
        self.assertEqual(league_table_visible_row_count(1), 1)
        self.assertEqual(league_table_visible_row_count(12), 12)
        self.assertEqual(league_table_visible_row_count(13), 7)
        self.assertEqual(league_table_visible_row_count(20), 10)
        self.assertEqual(league_table_visible_row_count(24), 12)

    def test_invalid_inputs_fail_closed(self):
        for bad in (0, -1, True, 1.5, "12"):
            with self.subTest(bad=bad):
                with self.assertRaises(FastViewLeagueTableError):
                    league_table_visible_row_count(bad)
        for bad in (-1, True, 1.5, "0"):
            with self.subTest(bad=bad):
                with self.assertRaises(FastViewLeagueTableError):
                    league_table_row_origin(bad)


if __name__ == "__main__":
    unittest.main()
