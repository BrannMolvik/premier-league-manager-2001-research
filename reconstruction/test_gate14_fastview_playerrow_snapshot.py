"""Tests for the complete source-backed FastView PlayerRow snapshot."""
from pathlib import Path
import unittest

from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_snapshot,
)
from gate14_fastview_team import (
    FastViewTeamError,
    TEAM_NAME_GRID_1,
    TEAM_NAME_GRID_2,
    TEAM_NAME_GRID_3,
)


class FastViewPlayerRowSnapshotTests(unittest.TestCase):
    def test_composes_source_order_cells_without_inventing_goal_history(self):
        row = build_fastview_player_row_snapshot(
            side_index=0,
            row_index=0,
            shirt_number=9,
            source_position_code=19,
            surname="Striker",
            first_name_initial="A",
            form_value=4,
            energy_value=79,
        )

        self.assertIs(row.name_grid_resource, TEAM_NAME_GRID_1)
        self.assertEqual(row.shirt_number.text, "9")
        self.assertEqual(row.shirt_number.rect, (37, 27, 61, 43))
        self.assertEqual(row.position.localization_key, "PositionST")
        self.assertEqual(row.position.rect, (64, 27, 104, 43))
        self.assertEqual(row.player_name.text, "A Striker")
        self.assertEqual(row.player_name.rect, (107, 27, 243, 43))
        self.assertIsNone(row.goal_count)
        self.assertIsNone(row.own_goal_count)
        self.assertEqual(row.form.text, "4")
        self.assertEqual(row.form.rect, (276, 27, 296, 43))
        self.assertEqual(row.energy.dynamic_rect, (309, 27, 351, 43))
        self.assertEqual(
            [item.text_cell_index if item is not None else None
             for item in row.text_cells],
            [1, 2, 3, None, None, 6],
        )

    def test_explicit_event_written_goal_counts_keep_distinct_source_channels(self):
        row = build_fastview_player_row_snapshot(
            side_index=1,
            row_index=2,
            shirt_number=4,
            source_position_code=4,
            surname="Defender",
            first_name_initial="-",
            form_value=7,
            energy_value=99,
            displayed_goal_count=2,
            displayed_own_goal_count=1,
        )

        self.assertIs(row.name_grid_resource, TEAM_NAME_GRID_3)
        self.assertEqual(row.player_name.text, "Defender")
        self.assertEqual(row.goal_count.text, "(2)")
        self.assertEqual(row.goal_count.stored_value, 2)
        self.assertEqual(row.goal_count.rect, (743, 61, 763, 77))
        self.assertFalse(row.goal_count.source_color_update)
        self.assertEqual(row.own_goal_count.text, "(1)")
        self.assertEqual(row.own_goal_count.stored_value, 1)
        self.assertEqual(row.own_goal_count.rect, (723, 61, 743, 77))
        self.assertTrue(row.own_goal_count.source_color_update)

    def test_row_eleven_uses_source_alternate_name_grid(self):
        row = build_fastview_player_row_snapshot(
            side_index=0,
            row_index=11,
            shirt_number=12,
            source_position_code=1,
            surname="Keeper",
            first_name_initial="K",
            form_value=3,
            energy_value=90,
        )
        self.assertIs(row.name_grid_resource, TEAM_NAME_GRID_2)

    def test_invalid_counter_does_not_get_sanitized(self):
        kwargs = dict(
            side_index=0,
            row_index=0,
            shirt_number=9,
            source_position_code=19,
            surname="Striker",
            first_name_initial="A",
            form_value=4,
            energy_value=79,
        )
        for bad in (-1, 0x100000000, True, "1"):
            with self.subTest(bad=bad):
                with self.assertRaises(FastViewTeamError):
                    build_fastview_player_row_snapshot(
                        **kwargs,
                        displayed_goal_count=bad,
                    )

    def test_snapshot_layer_does_not_import_simulation_rng_or_controller_code(self):
        source = Path(__file__).with_name(
            "gate14_fastview_playerrow_snapshot.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "human_gameplay",
            "gameplay_controller",
            "random",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
