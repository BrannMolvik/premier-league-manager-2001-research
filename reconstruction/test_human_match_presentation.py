"""Tests for the presentation-only completed-human-match adapter."""
from pathlib import Path
from types import SimpleNamespace
import unittest

from gate14_fastview_playerrow_snapshot import build_fastview_player_row_snapshot
from human_match_presentation import (
    HumanMatchPresentationError,
    build_human_match_presentation,
)
from match_events import (
    BoundaryRecord,
    BoundaryType,
    ChanceRecord,
    ChanceSource,
    PossessionRecord,
)
from match_presentation_feed import FastViewSemanticEvent
from match_simulation import NormalMatchResult, SegmentPossession, TimedMatchEvent


class HumanMatchPresentationTests(unittest.TestCase):
    def test_premier_league_outcome_projects_existing_result_without_mutation(self):
        goal = ChanceRecord(
            ChanceSource.OPEN_PLAY,
            raw_outcome=0,
            player_side=0,
            player_index=4,
        )
        full_time = BoundaryRecord(BoundaryType.FULL_TIME)
        possession = PossessionRecord(
            territory=55,
            side0_percent=45,
            neutral_percent=20,
        )
        result = NormalMatchResult(
            events=(
                TimedMatchEvent(12, goal),
                TimedMatchEvent(90, full_time),
            ),
            possession_segments=(SegmentPossession(10, possession),),
        )
        outcome = SimpleNamespace(fixture_id=23, user_result=result)

        presentation = build_human_match_presentation(outcome)

        self.assertEqual(presentation.match_reference, 23)
        self.assertEqual(presentation.feed.final_score, result.score)
        self.assertIs(presentation.feed.events[0].event, goal)
        self.assertIs(presentation.feed.events[1].event, full_time)
        self.assertIs(
            presentation.feed.events[0].fastview_event,
            FastViewSemanticEvent.PLAYER_GOAL,
        )
        self.assertIs(
            presentation.feed.events[1].fastview_event,
            FastViewSemanticEvent.FULL_TIME,
        )
        self.assertIs(
            presentation.feed.possession_segments[0].record,
            possession,
        )

    def test_primary_cup_outcome_preserves_tagged_match_reference(self):
        result = NormalMatchResult(
            events=(TimedMatchEvent(90, BoundaryRecord(BoundaryType.FULL_TIME)),),
        )
        entry = ("domestic_cup", ("cup_result", 4, 10, 2))
        outcome = SimpleNamespace(match_entry=entry, user_result=result)

        presentation = build_human_match_presentation(outcome)

        self.assertEqual(presentation.match_reference, entry)
        self.assertEqual(presentation.feed.final_score, (0, 0))


    def test_adapter_preserves_explicit_source_backed_player_rows_only(self):
        result = NormalMatchResult(events=())
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
        presentation = build_human_match_presentation(
            SimpleNamespace(
                fixture_id=23,
                user_result=result,
                fastview_player_rows=(row,),
            )
        )
        self.assertEqual(len(presentation.player_rows), 1)
        self.assertIs(presentation.player_rows[0], row)

        empty = build_human_match_presentation(
            SimpleNamespace(fixture_id=24, user_result=result)
        )
        self.assertEqual(empty.player_rows, ())

        with self.assertRaisesRegex(
            HumanMatchPresentationError,
            "non-source-backed FastView player rows",
        ):
            build_human_match_presentation(
                SimpleNamespace(
                    fixture_id=25,
                    user_result=result,
                    fastview_player_rows=(object(),),
                )
            )

    def test_adapter_fails_closed_when_completed_result_is_missing(self):
        with self.assertRaisesRegex(
            HumanMatchPresentationError,
            "no user_result",
        ):
            build_human_match_presentation(SimpleNamespace(fixture_id=1))
        with self.assertRaisesRegex(
            HumanMatchPresentationError,
            "no reconstructed event timeline",
        ):
            build_human_match_presentation(
                SimpleNamespace(fixture_id=1, user_result=object())
            )

    def test_adapter_has_no_simulation_controller_or_rng_imports(self):
        source = (
            Path(__file__).resolve().parent / "human_match_presentation.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "human_gameplay",
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "random",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
