import unittest

from competition_startup import CupClubRefDescriptor
from cup_progression import (
    CUP_MATCH_FIRST_LEG,
    CUP_MATCH_NORMAL,
    CUP_MATCH_REPLAY,
    CUP_MATCH_SECOND_LEG,
    CupMatchResolutionSnapshot,
    CupMatchRuntimeState,
    CupResultRegistry,
    complete_cup_match,
)


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




class FixedRng:
    def __init__(self, value):
        self.value = int(value)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(int(bound))
        return self.value


class CupMatchLifecycleTests(unittest.TestCase):
    def test_fa_cup_draw_creates_reversed_decisive_replay_without_rng(self):
        registry = CupResultRegistry()
        token = ("cup_result", 1, 38, 0)
        first = CupMatchRuntimeState.normal(
            token,
            10,
            20,
            extra_time_capable=True,
            decisive_tiebreak=False,
        )

        self.assertEqual(first.match_kind, CUP_MATCH_NORMAL)
        self.assertFalse(first.uses_extra_time)

        completion = complete_cup_match(first, registry, 1, 1)

        self.assertIsNone(completion.outcome)
        self.assertFalse(completion.used_rng_tiebreak_fallback)
        self.assertEqual(registry.outcomes, {})
        replay = completion.replay
        self.assertIsNotNone(replay)
        self.assertEqual(replay.match_kind, CUP_MATCH_REPLAY)
        self.assertEqual(
            (replay.participant_0_club_id, replay.participant_1_club_id),
            (20, 10),
        )
        self.assertTrue(replay.extra_time_capable)
        self.assertTrue(replay.uses_extra_time)
        self.assertTrue(replay.decisive_tiebreak)
        self.assertIs(replay.prior_match, first)
        self.assertIs(first.following_match, replay)

        replay_completion = complete_cup_match(replay, registry, 2, 1)
        self.assertIsNone(replay_completion.replay)
        self.assertEqual(replay_completion.outcome.winner_club_id, 20)
        self.assertEqual(registry.outcomes[token].winner_club_id, 20)

    def test_drawn_replay_uses_decisive_fallback_not_away_goal_comparison(self):
        registry = CupResultRegistry()
        token = ("cup_result", 1, 38, 1)
        first = CupMatchRuntimeState.normal(
            token,
            10,
            20,
            extra_time_capable=True,
            decisive_tiebreak=False,
        )
        replay = complete_cup_match(first, registry, 2, 2).replay
        rng = FixedRng(1)

        completion = complete_cup_match(
            replay,
            registry,
            1,
            1,
            rng=rng,
            decisive_event_score_0=4,
            decisive_event_score_1=4,
        )

        self.assertEqual(rng.calls, [2])
        self.assertTrue(completion.used_rng_tiebreak_fallback)
        self.assertEqual(replay.decisive_score_0, 5)
        self.assertEqual(replay.decisive_score_1, 4)
        self.assertEqual(completion.outcome.winner_club_id, 20)

    def test_two_leg_pair_reverses_second_leg_and_waits_for_it(self):
        registry = CupResultRegistry()
        token = ("cup_result", 5, 185, 3)
        first, second = CupMatchRuntimeState.two_leg_pair(
            token,
            1,
            2,
            second_leg_extra_time_capable=True,
        )

        self.assertEqual(first.match_kind, CUP_MATCH_FIRST_LEG)
        self.assertEqual(second.match_kind, CUP_MATCH_SECOND_LEG)
        self.assertEqual(
            (first.participant_0_club_id, first.participant_1_club_id),
            (1, 2),
        )
        self.assertEqual(
            (second.participant_0_club_id, second.participant_1_club_id),
            (2, 1),
        )
        self.assertFalse(first.uses_extra_time)
        self.assertTrue(second.uses_extra_time)
        self.assertTrue(second.decisive_tiebreak)
        self.assertIs(first.following_match, second)
        self.assertIs(second.prior_match, first)

        first_completion = complete_cup_match(first, registry, 2, 1)
        self.assertIsNone(first_completion.outcome)
        self.assertEqual(registry.outcomes, {})

        second_completion = complete_cup_match(second, registry, 1, 0)
        self.assertEqual(second_completion.outcome.winner_club_id, 2)
        self.assertFalse(second_completion.used_rng_tiebreak_fallback)

    def test_exact_two_leg_tie_consumes_one_rng2_after_event_tiebreak_ties(self):
        registry = CupResultRegistry()
        token = ("cup_result", 5, 190, 0)
        first, second = CupMatchRuntimeState.two_leg_pair(
            token,
            1,
            2,
            second_leg_extra_time_capable=True,
        )
        complete_cup_match(first, registry, 1, 1)
        rng = FixedRng(0)

        completion = complete_cup_match(
            second,
            registry,
            1,
            1,
            rng=rng,
        )

        self.assertEqual(rng.calls, [2])
        self.assertTrue(completion.used_rng_tiebreak_fallback)
        self.assertEqual(second.decisive_score_0, 0)
        self.assertEqual(second.decisive_score_1, 1)
        self.assertEqual(completion.outcome.winner_club_id, 1)

    def test_second_leg_secondary_comparison_precedes_rng_after_decisive_events(self):
        registry = CupResultRegistry()
        token = ("cup_result", 5, 190, 2)
        first, second = CupMatchRuntimeState.two_leg_pair(
            token,
            1,
            2,
            second_leg_extra_time_capable=True,
        )
        complete_cup_match(first, registry, 1, 1)
        rng = FixedRng(0)

        completion = complete_cup_match(
            second,
            registry,
            1,
            1,
            rng=rng,
            decisive_event_score_0=4,
            decisive_event_score_1=4,
        )

        self.assertEqual(rng.calls, [])
        self.assertFalse(completion.used_rng_tiebreak_fallback)
        self.assertEqual(completion.outcome.winner_club_id, 1)

    def test_event_tiebreak_that_already_resolves_match_consumes_no_rng(self):
        registry = CupResultRegistry()
        token = ("cup_result", 5, 190, 1)
        first, second = CupMatchRuntimeState.two_leg_pair(
            token,
            1,
            2,
            second_leg_extra_time_capable=True,
        )
        complete_cup_match(first, registry, 1, 1)
        rng = FixedRng(1)

        completion = complete_cup_match(
            second,
            registry,
            1,
            1,
            rng=rng,
            decisive_event_score_0=5,
            decisive_event_score_1=4,
        )

        self.assertEqual(rng.calls, [])
        self.assertFalse(completion.used_rng_tiebreak_fallback)
        self.assertEqual(completion.outcome.winner_club_id, 2)

    def test_decisive_single_match_exact_tie_uses_same_rng2_fallback(self):
        registry = CupResultRegistry()
        token = ("cup_result", 1, 43, 0)
        match = CupMatchRuntimeState.normal(
            token,
            10,
            20,
            extra_time_capable=True,
            decisive_tiebreak=True,
        )
        rng = FixedRng(1)

        completion = complete_cup_match(match, registry, 0, 0, rng=rng)

        self.assertTrue(match.uses_extra_time)
        self.assertEqual(rng.calls, [2])
        self.assertEqual(match.decisive_score_0, 1)
        self.assertEqual(match.decisive_score_1, 0)
        self.assertEqual(completion.outcome.winner_club_id, 10)


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

    def test_competition_position_ref_resolves_zero_based_rank(self):
        registry = CupResultRegistry()
        registry.record_competition_ranking(
            14,
            (101, 202, 303, 404),
            competition_context=3,
        )
        ref = CupClubRefDescriptor(
            type_code=2,
            selector=2,
            competition_id=14,
            competition_context=3,
            reference_token=("group_position", 14, 3, 2),
        )

        self.assertEqual(registry.resolve_club_ref(ref), 303)

    def test_competition_position_ref_waits_for_live_ranking(self):
        registry = CupResultRegistry()
        ref = CupClubRefDescriptor(
            type_code=2,
            selector=1,
            competition_id=14,
            competition_context=7,
        )

        self.assertIsNone(registry.resolve_club_ref(ref))
        registry.replace_competition_ranking(
            14,
            (900, 901, 902),
            competition_context=7,
        )
        self.assertEqual(registry.resolve_club_ref(ref), 901)

    def test_competition_ranking_refresh_changes_position_resolution(self):
        registry = CupResultRegistry()
        ref = CupClubRefDescriptor(
            type_code=2,
            selector=0,
            competition_id=14,
            competition_context=1,
        )
        registry.record_competition_ranking(
            14,
            (10, 20, 30),
            competition_context=1,
        )
        self.assertEqual(registry.resolve_club_ref(ref), 10)

        registry.replace_competition_ranking(
            14,
            (20, 10, 30),
            competition_context=1,
        )
        self.assertEqual(registry.resolve_club_ref(ref), 20)

    def test_competition_ranking_rejects_duplicate_clubs(self):
        registry = CupResultRegistry()
        with self.assertRaises(ValueError):
            registry.record_competition_ranking(14, (1, 1), competition_context=0)

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
