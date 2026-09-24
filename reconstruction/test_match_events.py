import unittest

from match_events import (
    BoundaryRecord,
    BoundaryType,
    ChanceOutcome,
    ChanceRecord,
    ChanceSource,
    IncidentKind,
    IncidentRecord,
    MatchTimeline,
    PossessionRecord,
    SUBSTITUTION_RECORD_TYPE,
)


class MatchEventTests(unittest.TestCase):
    def test_verified_numeric_taxonomy(self):
        self.assertEqual(int(ChanceSource.OPEN_PLAY), 1)
        self.assertEqual(int(ChanceSource.FREE_KICK), 2)
        self.assertEqual(int(ChanceSource.CORNER), 3)
        self.assertEqual(int(ChanceSource.PENALTY), 4)
        self.assertEqual(int(BoundaryType.HALF_TIME), 6)
        self.assertEqual(int(BoundaryType.FULL_TIME), 7)
        self.assertEqual(int(BoundaryType.EXTRA_TIME), 8)
        self.assertEqual(int(BoundaryType.PENALTIES), 9)
        self.assertEqual(SUBSTITUTION_RECORD_TYPE, 10)

    def test_outcome_modulo_three_and_presentation_bank(self):
        expected = [
            ChanceOutcome.GOAL,
            ChanceOutcome.MISS,
            ChanceOutcome.SAVE,
            ChanceOutcome.GOAL,
            ChanceOutcome.MISS,
            ChanceOutcome.SAVE,
        ]
        for raw, outcome in enumerate(expected):
            event = ChanceRecord(1, raw, 0, 3)
            self.assertEqual(event.outcome, outcome)
            self.assertEqual(event.presentation_variant, raw >= 3)

    def test_normal_goal_is_credited_to_players_side(self):
        event = ChanceRecord(ChanceSource.OPEN_PLAY, 0, 0, 9)
        self.assertTrue(event.is_goal)
        self.assertFalse(event.is_own_goal)
        self.assertEqual(event.credited_side, 0)

    def test_side_inversion_encodes_own_goal(self):
        event = ChanceRecord(ChanceSource.CORNER, 3, 0, 4, side_inversion=True)
        self.assertTrue(event.is_goal)
        self.assertTrue(event.is_own_goal)
        self.assertEqual(event.credited_side, 1)

    def test_miss_and_save_do_not_change_score(self):
        timeline = MatchTimeline([
            ChanceRecord(1, 1, 0, 1),
            ChanceRecord(2, 5, 1, 2),
        ])
        self.assertEqual(timeline.score(), (0, 0))

    def test_timeline_score_uses_verified_goal_attribution(self):
        timeline = MatchTimeline([
            ChanceRecord(1, 0, 0, 1),
            ChanceRecord(2, 3, 1, 2),
            ChanceRecord(3, 0, 0, 3, side_inversion=True),
            ChanceRecord(4, 2, 0, 4),
        ])
        self.assertEqual(timeline.score(), (1, 2))

    def test_incident_subtypes(self):
        self.assertEqual(int(IncidentKind.BOOKED), 0)
        self.assertEqual(int(IncidentKind.SENT_OFF), 1)
        self.assertEqual(int(IncidentKind.INJURED), 2)
        incident = IncidentRecord(2, 1, 7)
        self.assertEqual(incident.kind, IncidentKind.INJURED)

    def test_type_zero_is_rejected_as_active_chance_source(self):
        with self.assertRaises(ValueError):
            ChanceRecord(0, 0, 0, 1)

    def test_context_flag_preserves_verified_one_bit_semantics(self):
        self.assertFalse(ChanceRecord(1, 0, 0, 1, context_flag=0).context_flag)
        self.assertTrue(ChanceRecord(1, 0, 0, 1, context_flag=1).context_flag)

    def test_boundary_record_numeric_mapping(self):
        self.assertEqual(BoundaryRecord(7).kind, BoundaryType.FULL_TIME)


    def test_possession_record_reconstructs_side1_remainder(self):
        event = PossessionRecord(territory=55, side0_percent=43, neutral_percent=12)
        self.assertEqual(event.side1_percent, 45)

    def test_possession_record_validates_percentages(self):
        with self.assertRaises(ValueError):
            PossessionRecord(territory=50, side0_percent=70, neutral_percent=40)
        with self.assertRaises(ValueError):
            PossessionRecord(territory=101, side0_percent=50, neutral_percent=0)

    def test_possession_event_does_not_change_score(self):
        timeline = MatchTimeline([PossessionRecord(50, 45, 10)])
        self.assertEqual(timeline.score(), (0, 0))


if __name__ == '__main__':
    unittest.main()
