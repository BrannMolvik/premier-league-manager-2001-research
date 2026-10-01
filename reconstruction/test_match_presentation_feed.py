"""Tests that Gate-14 presentation consumes, not recreates, match output."""
from pathlib import Path
import unittest

from match_events import (
    BoundaryRecord,
    BoundaryType,
    ChanceRecord,
    ChanceSource,
    IncidentKind,
    IncidentRecord,
    PossessionRecord,
    SubstitutionRecord,
)
from match_presentation_feed import (
    MatchPresentationFeedError,
    build_match_presentation_feed,
)
from match_simulation import NormalMatchResult, SegmentPossession, TimedMatchEvent


class MatchPresentationFeedTests(unittest.TestCase):
    def test_feed_preserves_event_objects_order_and_running_score(self):
        goal = ChanceRecord(
            ChanceSource.OPEN_PLAY,
            raw_outcome=0,
            player_side=0,
            player_index=4,
        )
        own_goal = ChanceRecord(
            ChanceSource.CORNER,
            raw_outcome=3,
            player_side=0,
            player_index=7,
            side_inversion=True,
        )
        booking = IncidentRecord(IncidentKind.BOOKED, 1, 2)
        sub = SubstitutionRecord(1, 9, 14)
        full_time = BoundaryRecord(BoundaryType.FULL_TIME)
        events = (
            TimedMatchEvent(12, goal),
            TimedMatchEvent(37, booking),
            TimedMatchEvent(60, sub),
            TimedMatchEvent(75, own_goal),
            TimedMatchEvent(90, full_time),
        )
        result = NormalMatchResult(events)
        feed = build_match_presentation_feed(result.events)
        self.assertEqual(feed.final_score, result.score)
        self.assertEqual(feed.final_score, (1, 1))
        self.assertEqual([item.sequence for item in feed.events], list(range(5)))
        self.assertEqual(
            [item.score_after for item in feed.events],
            [(1, 0), (1, 0), (1, 0), (1, 1), (1, 1)],
        )
        self.assertTrue(
            all(item.event is expected for item, expected in zip(feed.events, [
                goal, booking, sub, own_goal, full_time
            ], strict=True))
        )

    def test_possession_records_are_projected_without_recalculation(self):
        first = PossessionRecord(territory=55, side0_percent=40, neutral_percent=20)
        second = PossessionRecord(territory=35, side0_percent=30, neutral_percent=10)
        segments = (
            SegmentPossession(0, first),
            SegmentPossession(5, second),
        )
        feed = build_match_presentation_feed((), segments)
        self.assertEqual(feed.final_score, (0, 0))
        self.assertEqual(
            [item.calculation_minute for item in feed.possession_segments],
            [0, 5],
        )
        self.assertIs(feed.possession_segments[0].record, first)
        self.assertIs(feed.possession_segments[1].record, second)

    def test_projection_rejects_reordered_or_invalid_inputs_instead_of_sorting_them(self):
        event = BoundaryRecord(BoundaryType.HALF_TIME)
        with self.assertRaisesRegex(
            MatchPresentationFeedError, "chronological order"
        ):
            build_match_presentation_feed((
                TimedMatchEvent(45, event),
                TimedMatchEvent(40, event),
            ))
        with self.assertRaisesRegex(
            MatchPresentationFeedError, "cannot be negative"
        ):
            build_match_presentation_feed((TimedMatchEvent(-1, event),))

    def test_presentation_module_has_no_simulation_rng_or_commentary_generator_imports(self):
        source = (
            Path(__file__).resolve().parent / "match_presentation_feed.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "random",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)
        self.assertNotIn("commentary_text", source)
        self.assertNotIn("sound_effect", source)


if __name__ == "__main__":
    unittest.main()
