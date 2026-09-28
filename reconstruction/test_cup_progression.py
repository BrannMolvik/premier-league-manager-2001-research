import unittest

from competition_startup import CupClubRefDescriptor
from cup_progression import CupResultRegistry


class CupResultRegistryTests(unittest.TestCase):
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
