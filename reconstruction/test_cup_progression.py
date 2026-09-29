import unittest

from competition_startup import CupClubRefDescriptor
from cup_progression import CupMatchResolutionSnapshot, CupResultRegistry


class CupMatchResolutionTests(unittest.TestCase):
    def test_incomplete_or_drawn_single_match_has_no_result_club(self):
        self.assertIsNone(
            CupMatchResolutionSnapshot(1, 2, 2, 1, complete=False).result_club_id()
        )
        self.assertIsNone(
            CupMatchResolutionSnapshot(1, 2, 1, 1).result_club_id()
        )

    def test_single_match_returns_higher_scoring_side(self):
        self.assertEqual(
            CupMatchResolutionSnapshot(1, 2, 3, 1).result_club_id(),
            1,
        )
        self.assertEqual(
            CupMatchResolutionSnapshot(1, 2, 0, 2).result_club_id(),
            2,
        )

    def test_linked_match_uses_reversed_aggregate_totals(self):
        first_leg = CupMatchResolutionSnapshot(1, 2, 2, 0)
        second_leg = CupMatchResolutionSnapshot(
            2,
            1,
            1,
            0,
            previous=first_leg,
        )

        self.assertEqual(second_leg.result_club_id(), 1)

    def test_tied_aggregate_uses_shared_virtual_secondary_comparison(self):
        # Leg 1: club 1 beats club 2 2-1.
        # Leg 2 reverses participants: club 2 beats club 1 1-0.
        # Aggregate is 2-2. current score_1 (club 1 away) is 0 while
        # previous score_1 (club 2 away) is 1, so 0x514000 returns club 2.
        first_leg = CupMatchResolutionSnapshot(1, 2, 2, 1)
        second_leg = CupMatchResolutionSnapshot(
            2,
            1,
            1,
            0,
            previous=first_leg,
        )

        self.assertEqual(second_leg.result_club_id(), 2)

    def test_exact_linked_tie_remains_unresolved(self):
        first_leg = CupMatchResolutionSnapshot(1, 2, 1, 1)
        second_leg = CupMatchResolutionSnapshot(
            2,
            1,
            1,
            1,
            previous=first_leg,
        )

        self.assertIsNone(second_leg.result_club_id())


class CupResultRegistryTests(unittest.TestCase):
    def test_match_snapshot_records_definitive_result_without_manual_winner(self):
        registry = CupResultRegistry()
        token = ("cup_result", 1, 38, 0)
        snapshot = CupMatchResolutionSnapshot(10, 20, 2, 0)

        outcome = registry.record_match_resolution(token, snapshot)

        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.winner_club_id, 10)
        self.assertEqual(registry.outcomes[token].loser_club_id, 20)

    def test_unresolved_snapshot_leaves_result_token_available(self):
        registry = CupResultRegistry()
        token = ("cup_result", 1, 38, 0)

        self.assertIsNone(
            registry.record_match_resolution(
                token,
                CupMatchResolutionSnapshot(10, 20, 1, 1),
            )
        )
        self.assertNotIn(token, registry.outcomes)

        recorded = registry.record_match_resolution(
            token,
            CupMatchResolutionSnapshot(
                20,
                10,
                2,
                0,
                previous=CupMatchResolutionSnapshot(10, 20, 1, 1),
            ),
        )
        self.assertIsNotNone(recorded)
        self.assertEqual(recorded.winner_club_id, 20)

    def test_linked_two_leg_snapshot_records_shared_virtual_result(self):
        registry = CupResultRegistry()
        token = ("cup_result", 5, 185, 4)
        first_leg = CupMatchResolutionSnapshot(1, 2, 2, 1)
        second_leg = CupMatchResolutionSnapshot(
            2,
            1,
            1,
            0,
            previous=first_leg,
        )

        outcome = registry.record_match_resolution(token, second_leg)

        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.winner_club_id, 2)
        self.assertEqual(outcome.loser_club_id, 1)

    def test_direct_club_ref_resolves_without_result_state(self):
        registry = CupResultRegistry()
        ref = CupClubRefDescriptor(type_code=0, direct_club_id=123)

        self.assertEqual(registry.resolve_club_ref(ref), 123)

    def test_match_result_ref_resolves_winner_and_loser_selectors(self):
        registry = CupResultRegistry()
        token = ("cup_result", 1, 38, 7)
        registry.record_knockout_outcome(token, 10, 20, 20)

        winner_ref = CupClubRefDescriptor(
            type_code=1,
            selector=0,
            reference_token=token,
        )
        loser_ref = CupClubRefDescriptor(
            type_code=1,
            selector=1,
            reference_token=token,
        )

        self.assertEqual(registry.resolve_club_ref(winner_ref), 20)
        self.assertEqual(registry.resolve_club_ref(loser_ref), 10)

    def test_unplayed_match_result_ref_remains_unresolved(self):
        registry = CupResultRegistry()
        ref = CupClubRefDescriptor(
            type_code=1,
            selector=0,
            reference_token=("cup_result", 1, 38, 0),
        )

        self.assertIsNone(registry.resolve_club_ref(ref))

    def test_record_rejects_non_participant_winner_and_duplicate_token(self):
        registry = CupResultRegistry()
        token = ("cup_result", 5, 185, 0)

        with self.assertRaises(ValueError):
            registry.record_knockout_outcome(token, 1, 2, 3)

        registry.record_knockout_outcome(token, 1, 2, 1)
        with self.assertRaises(ValueError):
            registry.record_knockout_outcome(token, 1, 2, 2)

    def test_next_round_pair_resolves_from_recorded_prior_results(self):
        registry = CupResultRegistry()
        left_token = ("cup_result", 1, 38, 0)
        right_token = ("cup_result", 1, 38, 1)
        registry.record_knockout_outcome(left_token, 100, 101, 100)
        registry.record_knockout_outcome(right_token, 102, 103, 103)

        pair = registry.resolve_pair(
            CupClubRefDescriptor(
                type_code=1,
                selector=0,
                reference_token=left_token,
            ),
            CupClubRefDescriptor(
                type_code=1,
                selector=0,
                reference_token=right_token,
            ),
        )

        self.assertEqual(pair, (100, 103))

    def test_unsupported_competition_position_ref_is_not_guessed(self):
        registry = CupResultRegistry()
        ref = CupClubRefDescriptor(
            type_code=2,
            selector=0,
            competition_id=0,
            reference_token=("competition_position", 0, 0),
        )

        self.assertIsNone(registry.resolve_club_ref(ref))


if __name__ == "__main__":
    unittest.main()
