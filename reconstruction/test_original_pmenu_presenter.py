from __future__ import annotations

import unittest

from original_pmenu_presenter import (
    OriginalPMenuPresentationError,
    build_fresh_pmenu_snapshot,
    build_pmenu_snapshot,
    candidate_pmenu_row_at_screen_point,
)


class OriginalPMenuPresenterTests(unittest.TestCase):
    def test_fresh_route_is_team_then_six_children_then_remaining_roots(self):
        snapshot = build_fresh_pmenu_snapshot()

        self.assertEqual(snapshot.list_size, (201, 504))
        self.assertEqual(snapshot.list_screen_origin, (599, 96))
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

    def test_expanded_root_can_differ_from_selected_panel_after_title_action(self):
        snapshot = build_pmenu_snapshot(0xCE, expanded_root_id=0x259)

        self.assertEqual(
            (snapshot.selected_root_id, snapshot.selected_child_id),
            (0x259, 0xCE),
        )
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows),
            (
                "Team", "Transfers", "Calendar", "Calendar",
                "League Fixtures", "TABLES", "Analysis", "ADMIN",
                "ACCOUNTS", "EAMail", "GAME OPTIONS",
            ),
        )
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows if row.selected),
            ("Calendar",),
        )
        self.assertEqual(
            tuple(row.caption for row in snapshot.rows if row.expanded),
            ("Calendar",),
        )

    def test_invalid_expanded_root_fails_closed(self):
        with self.assertRaisesRegex(
            OriginalPMenuPresentationError,
            "root ID",
        ):
            build_pmenu_snapshot(0xCE, expanded_root_id=0xDEADBEEF)
        with self.assertRaisesRegex(
            OriginalPMenuPresentationError,
            "root ID must be an integer",
        ):
            build_pmenu_snapshot(0xCE, expanded_root_id=True)
    def test_rows_retain_exact_title_child_assets_and_font(self):
        snapshot = build_fresh_pmenu_snapshot()

        self.assertEqual(
            snapshot.font_source_paths,
            (
                "Fonts/Zurich_XCn_BT_25pixel.fnt",
                "Fonts/Zurich_XCn_BT_16pixel.fnt",
            ),
        )
        self.assertEqual(snapshot.rows[0].text_line_origin, (30, 1))
        self.assertEqual(snapshot.rows[1].text_line_origin, (30, 46))
        self.assertEqual(snapshot.rows[0].text_clip_rect, (30, 0, 198, 29))
        self.assertEqual(snapshot.rows[1].text_clip_rect, (30, 29, 198, 58))
        self.assertEqual(snapshot.rows[0].text_color_16, 0xFFFF)
        self.assertEqual(snapshot.rows[0].background_state_bits, 0x8002)
        self.assertEqual(snapshot.rows[1].text_color_16, 0xFFFF)
        self.assertEqual(snapshot.rows[1].background_state_bits, 0x8002)
        self.assertEqual(snapshot.rows[2].text_color_16, 0x0000)
        self.assertEqual(snapshot.rows[2].background_state_bits, 0x2)
        self.assertEqual(len(snapshot.resource_source_paths), 4)
        self.assertTrue(snapshot.rows[0].arrow_source_path.endswith("menu_arrow_anim.444"))
        self.assertTrue(snapshot.rows[0].box_source_path.endswith("submenu_main_box.444"))
        self.assertTrue(snapshot.rows[1].arrow_source_path.endswith("menu_anim.444"))
        self.assertTrue(snapshot.rows[1].box_source_path.endswith("menu_main_box.444"))


    def test_candidate_row_hit_testing_uses_exact_half_open_native_geometry_only(self):
        snapshot = build_fresh_pmenu_snapshot()

        first = candidate_pmenu_row_at_screen_point(snapshot, 599, 96)
        self.assertEqual((first.visible_index, first.caption, first.menu_id), (0, "Team", 2))
        self.assertIs(
            candidate_pmenu_row_at_screen_point(snapshot, 799, 124),
            first,
        )

        squad = candidate_pmenu_row_at_screen_point(snapshot, 600, 125)
        self.assertEqual(
            (squad.visible_index, squad.caption, squad.menu_id),
            (1, "Squad", 0xCE),
        )

        for point in (
            (598, 96),
            (800, 96),
            (599, 95),
            (599, 600),
            (700, 96 + 15 * 29),
            (700, 599),
        ):
            with self.subTest(point=point):
                self.assertIsNone(
                    candidate_pmenu_row_at_screen_point(snapshot, *point)
                )

    def test_candidate_row_lookup_rejects_noninteger_coordinates_and_wrong_snapshot(self):
        snapshot = build_fresh_pmenu_snapshot()
        for x, y in ((True, 96), (599, False), (599.0, 96), (599, "96")):
            with self.subTest(x=x, y=y):
                with self.assertRaisesRegex(
                    OriginalPMenuPresentationError,
                    "coordinates must be integers",
                ):
                    candidate_pmenu_row_at_screen_point(snapshot, x, y)
        with self.assertRaisesRegex(
            OriginalPMenuPresentationError,
            "OriginalPMenuSnapshot",
        ):
            candidate_pmenu_row_at_screen_point(object(), 599, 96)

    def test_unrecovered_or_invalid_child_ids_fail_closed(self):
        with self.assertRaisesRegex(OriginalPMenuPresentationError, "not source-proven"):
            build_pmenu_snapshot(0xDEADBEEF)
        with self.assertRaisesRegex(OriginalPMenuPresentationError, "integer"):
            build_pmenu_snapshot("Squad")


if __name__ == "__main__":
    unittest.main()
