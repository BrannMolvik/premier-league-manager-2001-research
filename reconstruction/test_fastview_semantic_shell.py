"""Tests for the source-bounded Gate-14 FastView semantic shell."""
from pathlib import Path
from types import SimpleNamespace
import unittest

from fastview_semantic_shell import (
    SOURCE_BACKED_COMPONENTS,
    build_fastview_semantic_shell,
)
from gate14_fastview_playerrow_snapshot import build_fastview_player_row_snapshot
from human_match_presentation import build_human_match_presentation
from match_events import (
    BoundaryRecord,
    BoundaryType,
    ChanceRecord,
    ChanceSource,
    IncidentKind,
    IncidentRecord,
    PossessionRecord,
)
from match_simulation import NormalMatchResult, SegmentPossession, TimedMatchEvent


class FastViewSemanticShellTests(unittest.TestCase):
    def _presentation(self):
        goal = ChanceRecord(
            ChanceSource.OPEN_PLAY,
            raw_outcome=0,
            player_side=0,
            player_index=4,
        )
        booking = IncidentRecord(IncidentKind.BOOKED, 1, 2)
        full_time = BoundaryRecord(BoundaryType.FULL_TIME)
        possession = PossessionRecord(
            territory=55,
            side0_percent=45,
            neutral_percent=20,
        )
        result = NormalMatchResult(
            events=(
                TimedMatchEvent(12, goal),
                TimedMatchEvent(37, booking),
                TimedMatchEvent(90, full_time),
            ),
            possession_segments=(SegmentPossession(10, possession),),
        )
        outcome = SimpleNamespace(fixture_id=23, user_result=result)
        return build_human_match_presentation(outcome), goal, booking, full_time, possession

    def test_shell_reuses_existing_event_objects_and_exact_sender_names(self):
        presentation, goal, booking, full_time, _ = self._presentation()

        shell = build_fastview_semantic_shell(presentation)

        self.assertEqual(shell.match_reference, 23)
        self.assertEqual(shell.final_score, (1, 0))
        self.assertEqual(
            [(row.minute, row.score_after, row.sender_name) for row in shell.events],
            [
                (12, (1, 0), "EventPlayerGoal"),
                (37, (1, 0), None),
                (90, (1, 0), "FastView:FullTime"),
            ],
        )
        self.assertIs(shell.events[0].event, goal)
        self.assertIs(shell.events[1].event, booking)
        self.assertIs(shell.events[2].event, full_time)

    def test_possession_figures_use_proven_percent_format_without_team_orientation(self):
        presentation, _, _, _, possession = self._presentation()

        shell = build_fastview_semantic_shell(presentation)
        figures = shell.possession_figures[0]

        self.assertEqual(figures.calculation_minute, 10)
        self.assertEqual(figures.source_global_tick, 10)
        self.assertEqual(figures.source_possession_array_index, 2)
        self.assertEqual(figures.side0_percent_text, "45%")
        self.assertEqual(figures.neutral_percent_text, "20%")
        self.assertEqual(figures.side1_percent_text, "35%")
        self.assertEqual(figures.territory_raw, 55)
        self.assertIs(figures.record, possession)

    def test_non_five_minute_possession_segment_fails_source_bridge_closed(self):
        possession = PossessionRecord(
            territory=55,
            side0_percent=45,
            neutral_percent=20,
        )
        result = NormalMatchResult(
            events=(),
            possession_segments=(SegmentPossession(7, possession),),
        )
        presentation = build_human_match_presentation(
            SimpleNamespace(fixture_id=23, user_result=result)
        )
        with self.assertRaisesRegex(ValueError, "divisible by five"):
            build_fastview_semantic_shell(presentation)


    def test_shell_preserves_retained_player_row_snapshot_objects(self):
        presentation, *_ = self._presentation()
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
        presentation = presentation.__class__(
            match_reference=presentation.match_reference,
            feed=presentation.feed,
            player_rows=(row,),
        )
        shell = build_fastview_semantic_shell(presentation)
        self.assertEqual(len(shell.player_rows), 1)
        self.assertIs(shell.player_rows[0], row)
        self.assertEqual(len(shell.player_row_render_plans), 1)
        plan = shell.player_row_render_plans[0]
        self.assertEqual((plan.side_index, plan.row_index), (0, 0))
        self.assertEqual(plan.name_grid_rect, (37, 27, 296, 43))
        self.assertEqual(plan.energy_dynamic_rect, (309, 27, 351, 43))
        self.assertEqual(
            [item.value_kind for item in plan.text_instructions],
            [
                "literal",
                "localization_key",
                "literal",
                "unwritten",
                "unwritten",
                "literal",
            ],
        )
        self.assertFalse(plan.raster_ready)

    def test_shell_keeps_render_plan_order_identical_to_retained_row_order(self):
        presentation, *_ = self._presentation()
        rows = (
            build_fastview_player_row_snapshot(
                side_index=1,
                row_index=2,
                shirt_number=4,
                source_position_code=4,
                surname="Defender",
                first_name_initial="-",
                form_value=7,
                energy_value=99,
                displayed_goal_count=2,
            ),
            build_fastview_player_row_snapshot(
                side_index=0,
                row_index=0,
                shirt_number=9,
                source_position_code=19,
                surname="Striker",
                first_name_initial="A",
                form_value=4,
                energy_value=79,
            ),
        )
        shell = build_fastview_semantic_shell(
            presentation.__class__(
                match_reference=presentation.match_reference,
                feed=presentation.feed,
                player_rows=rows,
            )
        )
        self.assertEqual(
            [(plan.side_index, plan.row_index) for plan in shell.player_row_render_plans],
            [(1, 2), (0, 0)],
        )
        self.assertEqual(shell.player_row_render_plans[0].text_instructions[3].value, "(2)")
        self.assertEqual(shell.player_row_render_plans[1].text_instructions[3].value_kind, "unwritten")

    def test_shell_declares_only_persisted_component_and_fidelity_boundaries(self):
        presentation, *_ = self._presentation()

        shell = build_fastview_semantic_shell(presentation)

        self.assertEqual(
            shell.source_backed_components,
            ("FastViewPanel", "ScoreComposite", "PossessionFigures", "PossessionDiagram"),
        )
        self.assertEqual(shell.source_backed_components, SOURCE_BACKED_COMPONENTS)
        self.assertFalse(shell.original_layout_recovered)
        self.assertFalse(shell.audio_mapping_recovered)
        self.assertFalse(shell.choreography_3d_recovered)

    def test_shell_module_does_not_import_simulation_rng_audio_or_commentary_layers(self):
        source = (
            Path(__file__).resolve().parent / "fastview_semantic_shell.py"
        ).read_text(encoding="utf-8")
        self.assertIn("build_fastview_player_row_render_plan", source)
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "random",
            "sound_effect",
            "commentary_text",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
