"""Tests for the source-bounded Gate-14 FastView semantic shell."""
from pathlib import Path
from types import SimpleNamespace
import unittest

from fastview_semantic_shell import (
    SOURCE_BACKED_COMPONENTS,
    build_fastview_semantic_shell,
)
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
        self.assertEqual(figures.side0_percent_text, "45%")
        self.assertEqual(figures.neutral_percent_text, "20%")
        self.assertEqual(figures.side1_percent_text, "35%")
        self.assertEqual(figures.territory_raw, 55)
        self.assertIs(figures.record, possession)

    def test_shell_declares_only_persisted_component_and_fidelity_boundaries(self):
        presentation, *_ = self._presentation()

        shell = build_fastview_semantic_shell(presentation)

        self.assertEqual(
            shell.source_backed_components,
            ("FastViewPanel", "ScoreComposite", "PossessionFigures"),
        )
        self.assertEqual(shell.source_backed_components, SOURCE_BACKED_COMPONENTS)
        self.assertFalse(shell.original_layout_recovered)
        self.assertFalse(shell.audio_mapping_recovered)
        self.assertFalse(shell.choreography_3d_recovered)

    def test_shell_module_does_not_import_simulation_rng_audio_or_commentary_layers(self):
        source = (
            Path(__file__).resolve().parent / "fastview_semantic_shell.py"
        ).read_text(encoding="utf-8")
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
