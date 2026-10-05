"""Tests for source-closed nested score/table static text inventory."""
import unittest

from gate14_fastview_static_text_inventory import (
    FastViewStaticTextInventoryError,
    league_scores_static_text_inventory,
    league_table_static_text_inventory,
    static_text_inventory_contract,
)


class FastViewStaticTextInventoryTests(unittest.TestCase):
    def test_score_rows_have_four_exact_source_ordered_text_rectangles(self):
        controls = league_scores_static_text_inventory(2)
        self.assertEqual(len(controls), 8)
        self.assertEqual(
            tuple(control.rect for control in controls[:4]),
            (
                (40, 55, 170, 71),
                (215, 55, 345, 71),
                (177, 55, 190, 71),
                (196, 55, 209, 71),
            ),
        )
        self.assertEqual(
            tuple(control.rect for control in controls[4:]),
            (
                (40, 74, 170, 90),
                (215, 74, 345, 90),
                (177, 74, 190, 90),
                (196, 74, 209, 90),
            ),
        )
        self.assertTrue(
            all(control.owner == "score_composite_normal" for control in controls)
        )
        self.assertEqual(
            tuple(control.source_index for control in controls),
            (0, 0, 0, 0, 1, 1, 1, 1),
        )

    def test_league_table_inventory_has_heading_plus_visible_rows(self):
        controls = league_table_static_text_inventory(20)
        # 20 -> 10 visible rows; seven heading cells + 9 per row.
        self.assertEqual(len(controls), 97)
        self.assertEqual(
            tuple(control.rect for control in controls[:7]),
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
        self.assertEqual(controls[7].rect, (550, 55, 580, 71))
        self.assertEqual(controls[15].rect, (412, 55, 542, 71))
        self.assertEqual(controls[-1].rect, (412, 226, 542, 242))
        self.assertEqual(controls[0].owner, "league_table_heading")
        self.assertEqual(controls[7].owner, "league_table_row")
        self.assertIsNone(controls[0].source_index)
        self.assertEqual(controls[7].source_index, 0)

    def test_contract_keeps_semantics_pixels_and_later_controls_fail_closed(self):
        contract = static_text_inventory_contract(
            league_scores_source_count=12,
            league_table_source_count=20,
        )
        self.assertEqual(contract["league_scores_static_text_control_count"], 48)
        self.assertEqual(contract["league_table_static_text_control_count"], 97)
        self.assertTrue(contract["geometry_recovered"])
        self.assertTrue(contract["source_control_order_recovered"])
        self.assertFalse(contract["user_facing_semantics_recovered"])
        self.assertFalse(contract["final_text_values_recovered"])
        self.assertFalse(contract["font_style_color_recovered"])
        self.assertFalse(contract["pixels_rasterized"])
        self.assertFalse(
            contract["later_league_scores_title_button_controls_included"]
        )
        self.assertFalse(contract["score_subpanel_complete_pixels_recovered"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])

    def test_invalid_score_page_or_table_count_fails_closed(self):
        for count in (0, 13, -1, True, 1.5):
            with self.subTest(score_count=count):
                with self.assertRaises(FastViewStaticTextInventoryError):
                    league_scores_static_text_inventory(count)

        for count in (0, -1, True, 1.5):
            with self.subTest(table_count=count):
                with self.assertRaises(FastViewStaticTextInventoryError):
                    league_table_static_text_inventory(count)


if __name__ == "__main__":
    unittest.main()
