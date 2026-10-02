from __future__ import annotations

import unittest

from original_pmenu_presenter import (
    OriginalPMenuPresentationError,
    build_fresh_pmenu_snapshot,
    build_pmenu_snapshot,
)


class OriginalPMenuPresenterTests(unittest.TestCase):
    def test_fresh_route_is_team_then_six_children_then_remaining_roots(self):
        snapshot = build_fresh_pmenu_snapshot()

        self.assertEqual(snapshot.list_size, (201, 504))
        self.assertEqual(snapshot.row_capacity, 16)
        self.assertEqual(snapshot.row_step, 29)
        self.assertEqual((snapshot.selected_root_id, snapshot.selected_child_id), (2, 0xCE))
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows),
            (
                "Team", "Squad", "Stats", "Indiv. Orders", "Team Orders",
                "Training", "Youth Team", "Transfers", "Calendar", "TABLES",
                "Analysis", "ADMIN", "ACCOUNTS", "EAMail", "GAME OPTIONS",
            ),
        )
        self.assertEqual(tuple(row.y for row in snapshot.rows), tuple(range(0, 435, 29)))
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows if row.selected),
            ("Team", "Squad"),
        )
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows if row.expanded),
            ("Team",),
        )

    def test_league_tables_route_preserves_root_first_preorder(self):
        snapshot = build_pmenu_snapshot(0x25A)

        self.assertEqual((snapshot.selected_root_id, snapshot.selected_child_id), (6, 0x25A))
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows),
            (
                "Team", "Transfers", "Calendar", "TABLES", "League Tables",
                "Cup Tables", "Analysis", "ADMIN", "ACCOUNTS", "EAMail",
                "GAME OPTIONS",
            ),
        )

    def test_rows_retain_exact_title_child_assets_and_font(self):
        snapshot = build_fresh_pmenu_snapshot()

        self.assertEqual(snapshot.font_source_path, "Fonts/Zurich_BdXCn_BT_16pixel.fnt")
        self.assertEqual(len(snapshot.resource_source_paths), 4)
        self.assertTrue(snapshot.rows[0].arrow_source_path.endswith("menu_arrow_anim.444"))
        self.assertTrue(snapshot.rows[0].box_source_path.endswith("submenu_main_box.444"))
        self.assertTrue(snapshot.rows[1].arrow_source_path.endswith("menu_anim.444"))
        self.assertTrue(snapshot.rows[1].box_source_path.endswith("menu_main_box.444"))

    def test_unrecovered_or_invalid_child_ids_fail_closed(self):
        with self.assertRaisesRegex(OriginalPMenuPresentationError, "not source-proven"):
            build_pmenu_snapshot(0xDEADBEEF)
        with self.assertRaisesRegex(OriginalPMenuPresentationError, "integer"):
            build_pmenu_snapshot("Squad")


if __name__ == "__main__":
    unittest.main()
