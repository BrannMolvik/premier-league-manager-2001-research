"""Tests for the complete source-backed FastView PlayerRow snapshot."""
from dataclasses import replace
from pathlib import Path
import unittest

from gate14_fastview_player_history import FastViewPlayerHistories
from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_render_plan,
    build_fastview_player_row_snapshot,
    build_fastview_player_row_snapshot_from_histories,
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

    def test_history_adapter_uses_exact_form_and_energy_at_tick(self):
        condition = tuple(max(70, 100 - index) for index in range(24))
        match_form = (5, 6, 6, 4, 4, 5) + (5,) * 18
        histories = FastViewPlayerHistories(condition, match_form)

        row = build_fastview_player_row_snapshot_from_histories(
            side_index=0,
            row_index=0,
            shirt_number=9,
            source_position_code=19,
            surname="Striker",
            first_name_initial="A",
            histories=histories,
            global_tick=11,
            energy_rng6_roll=2,
        )

        self.assertEqual(row.form.text, "6")
        self.assertEqual(row.form.stored_value, 6)
        self.assertEqual(row.energy.energy_value, 97)
        self.assertEqual(row.energy.dynamic_rect, (309, 27, 387, 43))

    def test_history_adapter_preserves_event_written_counter_channels(self):
        histories = FastViewPlayerHistories((90,) * 24, (7,) * 24)
        row = build_fastview_player_row_snapshot_from_histories(
            side_index=1,
            row_index=2,
            shirt_number=4,
            source_position_code=4,
            surname="Defender",
            first_name_initial="-",
            histories=histories,
            global_tick=5,
            energy_rng6_roll=3,
            displayed_goal_count=2,
            displayed_own_goal_count=1,
        )
        self.assertEqual(row.form.text, "7")
        self.assertEqual(row.energy.energy_value, 90)
        self.assertEqual(row.goal_count.text, "(2)")
        self.assertEqual(row.own_goal_count.text, "(1)")

    def test_history_adapter_rejects_bad_energy_roll_without_rng_side_effect(self):
        histories = FastViewPlayerHistories((90,) * 24, (7,) * 24)
        with self.assertRaises(ValueError):
            build_fastview_player_row_snapshot_from_histories(
                side_index=0,
                row_index=0,
                shirt_number=9,
                source_position_code=19,
                surname="Striker",
                first_name_initial="A",
                histories=histories,
                global_tick=5,
                energy_rng6_roll=6,
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

    def test_render_plan_preserves_literal_localized_and_unwritten_channels(self):
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
        plan = build_fastview_player_row_render_plan(row)

        self.assertEqual(plan.name_grid_rect, (37, 27, 296, 43))
        self.assertEqual(plan.name_grid_resource.name, "team_name_grid")
        self.assertEqual(plan.static_energy_resource.name, "blank_bar")
        self.assertEqual(plan.dynamic_energy_resource.name, "team_bar_1")
        self.assertEqual(plan.energy_full_rect, (309, 27, 391, 43))
        self.assertEqual(plan.energy_dynamic_rect, (309, 27, 351, 43))
        self.assertFalse(plan.raster_ready)
        self.assertEqual(
            [
                (
                    item.text_cell_index,
                    item.semantic,
                    item.value_kind,
                    item.value,
                )
                for item in plan.text_instructions
            ],
            [
                (1, "player_shirt_number", "literal", "9"),
                (2, "player_position", "localization_key", "PositionST"),
                (3, "player_display_name", "literal", "A Striker"),
                (4, "player_goal_count", "unwritten", None),
                (5, "player_own_goal_count", "unwritten", None),
                (6, "player_form", "literal", "4"),
            ],
        )

    def test_render_plan_keeps_event_written_goal_channels_and_own_goal_color_flag(self):
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
        plan = build_fastview_player_row_render_plan(row)
        self.assertEqual(plan.static_energy_resource.name, "team_bar_2")
        self.assertEqual(plan.dynamic_energy_resource.name, "blank_bar")
        self.assertEqual(plan.text_instructions[3].value, "(2)")
        self.assertEqual(plan.text_instructions[3].value_kind, "literal")
        self.assertFalse(plan.text_instructions[3].source_color_update)
        self.assertEqual(plan.text_instructions[4].value, "(1)")
        self.assertEqual(plan.text_instructions[4].value_kind, "literal")
        self.assertTrue(plan.text_instructions[4].source_color_update)

    def test_render_plan_preserves_source_negative_width_energy_without_sanitizing(self):
        row = build_fastview_player_row_snapshot(
            side_index=0,
            row_index=0,
            shirt_number=9,
            source_position_code=19,
            surname="Striker",
            first_name_initial="A",
            form_value=4,
            energy_value=57,
        )
        plan = build_fastview_player_row_render_plan(row)
        self.assertEqual(plan.energy_dynamic_rect, (309, 27, 307, 43))
        self.assertFalse(plan.raster_ready)

    def test_render_plan_rejects_snapshot_geometry_or_resource_drift(self):
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
        with self.assertRaisesRegex(FastViewTeamError, "name-grid"):
            build_fastview_player_row_render_plan(
                replace(row, name_grid_resource=TEAM_NAME_GRID_2)
            )

        bad_energy = replace(row.energy, row_index=1)
        with self.assertRaisesRegex(FastViewTeamError, "energy state"):
            build_fastview_player_row_render_plan(
                replace(row, energy=bad_energy)
            )

        bad_shirt = replace(row.shirt_number, rect=(38, 27, 62, 43))
        with self.assertRaisesRegex(FastViewTeamError, "text cell 1"):
            build_fastview_player_row_render_plan(
                replace(row, shirt_number=bad_shirt)
            )

        with self.assertRaisesRegex(FastViewTeamError, "exact retained snapshot"):
            build_fastview_player_row_render_plan(object())

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
