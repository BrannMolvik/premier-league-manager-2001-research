import unittest
from datetime import date

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_startup import CupClubRefDescriptor
from cup_progression import CupResultRegistry, complete_cup_match
from domestic_cup_state import DomesticCupScheduleState
from primary_schedule import place_primary_schedule_nodes


def cup_node(
    *,
    node_kind,
    competition_id,
    round_id,
    pair_index,
    week,
    weekday,
    left,
    right,
    token,
    extra_time_capable=False,
    decisive_tiebreak=False,
    auxiliary_flag=False,
):
    return StartupScheduleNode(
        node_kind=node_kind,
        competition_id=competition_id,
        competition_context=0,
        round_id=round_id,
        pair_index=pair_index,
        schedule_index=None,
        scheduled_week=week,
        scheduled_weekday=weekday,
        participant_0_ref=left,
        participant_1_ref=right,
        node_token=token,
        extra_time_capable=extra_time_capable,
        decisive_tiebreak=decisive_tiebreak,
        auxiliary_flag=auxiliary_flag,
    )


class DomesticCupScheduleStateTests(unittest.TestCase):
    def test_install_maps_source_weekday_and_filters_non_domestic_nodes(self):
        domestic = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=38,
            pair_index=0,
            week=19,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(20),
            token=("cup_result", 1, 38, 0),
        )
        other = cup_node(
            node_kind="cup_match",
            competition_id=9,
            round_id=200,
            pair_index=0,
            week=0,
            weekday=6,
            left=direct_club_ref(30),
            right=direct_club_ref(40),
            token=("cup_result", 9, 200, 0),
        )

        state = DomesticCupScheduleState.from_startup_nodes(
            (domestic, other),
            season_year=2000,
        )

        self.assertEqual(len(state.nodes), 1)
        self.assertEqual(state.nodes[0].scheduled_date, date(2000, 11, 18))
        self.assertEqual(state.nodes[0].node_token, ("cup_result", 1, 38, 0))

    def test_primary_buckets_apply_conflict_displacement_to_cup_date(self):
        blocker = cup_node(
            node_kind="cup_match",
            competition_id=9,
            round_id=200,
            pair_index=0,
            week=19,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(30),
            token=("cup_result", 9, 200, 0),
        )
        domestic = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=38,
            pair_index=0,
            week=19,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(20),
            token=("cup_result", 1, 38, 0),
        )

        placed = place_primary_schedule_nodes((blocker, domestic))
        self.assertEqual(placed.chosen_bucket_indices, (138, 140))

        state = DomesticCupScheduleState.from_primary_schedule_buckets(
            placed.buckets,
            season_year=2000,
        )

        self.assertEqual(len(state.nodes), 1)
        self.assertEqual(state.nodes[0].scheduled_date, date(2000, 11, 20))

    def test_primary_buckets_preserve_supplied_head_to_tail_cup_order(self):
        first = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=38,
            pair_index=0,
            week=19,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(20),
            token=("cup_result", 1, 38, 0),
        )
        second = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=38,
            pair_index=1,
            week=19,
            weekday=6,
            left=direct_club_ref(30),
            right=direct_club_ref(40),
            token=("cup_result", 1, 38, 1),
        )
        buckets = [() for _ in range(139)]
        buckets[138] = (second, first)

        state = DomesticCupScheduleState.from_primary_schedule_buckets(
            buckets,
            season_year=2000,
        )
        due = state.due_nodes(date(2000, 11, 18), CupResultRegistry())

        self.assertEqual(
            tuple(node.node_token for node in due),
            (("cup_result", 1, 38, 1), ("cup_result", 1, 38, 0)),
        )

    def test_scheduled_node_preserves_constructor_policy_through_roundtrip(self):
        scheduled = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=43,
            pair_index=0,
            week=38,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(20),
            token=("cup_result", 1, 43, 0),
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=True,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (scheduled,),
            season_year=2000,
        )

        node = state.nodes[0]
        self.assertTrue(node.extra_time_capable)
        self.assertTrue(node.decisive_tiebreak)
        self.assertTrue(node.auxiliary_flag)

        restored = DomesticCupScheduleState.restore(state.snapshot())
        self.assertEqual(restored.nodes[0], node)

    def test_normal_materialization_defaults_to_scheduled_constructor_policy(self):
        token = ("cup_result", 1, 43, 0)
        scheduled = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=43,
            pair_index=0,
            week=38,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(20),
            token=token,
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=True,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (scheduled,),
            season_year=2000,
        )

        match = state.materialize_normal_match(token, CupResultRegistry())

        self.assertTrue(match.extra_time_capable)
        self.assertTrue(match.decisive_tiebreak)
        self.assertTrue(match.auxiliary_flag)
        self.assertTrue(match.uses_extra_time)

    def test_two_leg_materialization_defaults_to_second_leg_policy(self):
        first_token = ("cup_first_leg", 5, 185, 3)
        result_token = ("cup_result", 5, 185, 3)
        first = cup_node(
            node_kind="first_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=7,
            weekday=3,
            left=direct_club_ref(1),
            right=direct_club_ref(2),
            token=first_token,
        )
        second = cup_node(
            node_kind="second_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=9,
            weekday=3,
            left=direct_club_ref(2),
            right=direct_club_ref(1),
            token=result_token,
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=True,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (first, second),
            season_year=2000,
        )

        first_match, second_match = state.materialize_two_leg_pair(
            first_token,
            CupResultRegistry(),
        )

        self.assertFalse(first_match.extra_time_capable)
        self.assertFalse(first_match.decisive_tiebreak)
        self.assertTrue(second_match.extra_time_capable)
        self.assertTrue(second_match.decisive_tiebreak)
        self.assertTrue(second_match.auxiliary_flag)

    def test_symbolic_participant_becomes_playable_only_after_prior_result(self):
        prior = ("cup_result", 1, 38, 0)
        next_node = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=39,
            pair_index=0,
            week=1,
            weekday=6,
            left=CupClubRefDescriptor(
                type_code=1,
                selector=0,
                reference_token=prior,
            ),
            right=direct_club_ref(30),
            token=("cup_result", 1, 39, 0),
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (next_node,),
            season_year=2000,
        )
        registry = CupResultRegistry()
        due_date = date(2000, 7, 15)

        self.assertEqual(state.due_nodes(due_date, registry), ())

        registry.record_knockout_outcome(prior, 10, 20, 10)
        due = state.due_nodes(due_date, registry)

        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].resolve_pair(registry), (10, 30))

    def test_second_leg_waits_for_first_leg_completion_identity(self):
        first_token = ("cup_first_leg", 5, 185, 3)
        result_token = ("cup_result", 5, 185, 3)
        first = cup_node(
            node_kind="first_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=2,
            weekday=3,
            left=direct_club_ref(1),
            right=direct_club_ref(2),
            token=first_token,
        )
        second = cup_node(
            node_kind="second_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=3,
            weekday=3,
            left=direct_club_ref(2),
            right=direct_club_ref(1),
            token=result_token,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (first, second),
            season_year=2000,
        )
        registry = CupResultRegistry()
        second_date = date(2000, 7, 26)

        self.assertEqual(state.due_nodes(second_date, registry), ())

        state.mark_completed(first_token)
        due = state.due_nodes(second_date, registry)

        self.assertEqual(tuple(node.node_token for node in due), (result_token,))
        self.assertEqual(due[0].resolve_pair(registry), (2, 1))

    def test_two_leg_match_scores_and_links_survive_state_roundtrip(self):
        first_token = ("cup_first_leg", 5, 185, 3)
        result_token = ("cup_result", 5, 185, 3)
        first_node = cup_node(
            node_kind="first_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=2,
            weekday=3,
            left=direct_club_ref(1),
            right=direct_club_ref(2),
            token=first_token,
        )
        second_node = cup_node(
            node_kind="second_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=3,
            weekday=3,
            left=direct_club_ref(2),
            right=direct_club_ref(1),
            token=result_token,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (first_node, second_node),
            season_year=2000,
        )
        registry = CupResultRegistry()
        first, second = state.materialize_two_leg_pair(
            first_token,
            registry,
            second_leg_extra_time_capable=True,
        )
        complete_cup_match(first, registry, 2, 1)
        state.mark_completed(first_token)

        restored = DomesticCupScheduleState.restore(state.snapshot())
        restored_first = restored.match_state(first_token)
        restored_second = restored.match_state(result_token)

        self.assertTrue(restored_first.complete)
        self.assertEqual((restored_first.base_score_0, restored_first.base_score_1), (2, 1))
        self.assertIs(restored_second.prior_match, restored_first)
        self.assertIs(restored_first.following_match, restored_second)
        self.assertFalse(restored_second.complete)
        self.assertTrue(restored_second.extra_time_capable)

    def test_normal_match_materialization_waits_for_symbolic_participant(self):
        prior = ("cup_result", 1, 38, 0)
        token = ("cup_result", 1, 39, 0)
        scheduled = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=39,
            pair_index=0,
            week=1,
            weekday=6,
            left=CupClubRefDescriptor(
                type_code=1,
                selector=0,
                reference_token=prior,
            ),
            right=direct_club_ref(30),
            token=token,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (scheduled,),
            season_year=2000,
        )
        registry = CupResultRegistry()

        with self.assertRaisesRegex(ValueError, "unresolved"):
            state.materialize_normal_match(
                token,
                registry,
                extra_time_capable=True,
                decisive_tiebreak=False,
            )

        registry.record_knockout_outcome(prior, 10, 20, 10)
        match = state.materialize_normal_match(
            token,
            registry,
            extra_time_capable=True,
            decisive_tiebreak=False,
        )

        self.assertEqual(
            (match.participant_0_club_id, match.participant_1_club_id),
            (10, 30),
        )
        self.assertFalse(match.uses_extra_time)

    def test_drawn_fa_cup_match_inserts_reversed_replay_fourteen_days_later(self):
        result_token = ("cup_result", 1, 38, 0)
        scheduled = cup_node(
            node_kind="cup_match",
            competition_id=1,
            round_id=38,
            pair_index=0,
            week=19,
            weekday=6,
            left=direct_club_ref(10),
            right=direct_club_ref(20),
            token=result_token,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (scheduled,),
            season_year=2000,
        )
        registry = CupResultRegistry()
        original = state.materialize_normal_match(
            result_token,
            registry,
            extra_time_capable=True,
            decisive_tiebreak=False,
        )
        completion = complete_cup_match(original, registry, 1, 1)

        replay_node = state.insert_replay_from_completion(
            result_token,
            completion,
            current_date=date(2000, 11, 18),
        )
        replay_token = ("cup_replay", 1, 38, 0)

        self.assertEqual(replay_node.node_token, replay_token)
        self.assertEqual(replay_node.scheduled_date, date(2000, 12, 2))
        self.assertEqual(replay_node.resolve_pair(registry), (20, 10))
        self.assertIn(result_token, state.completed_node_tokens)
        self.assertNotIn(replay_token, state.completed_node_tokens)
        self.assertEqual(
            tuple(node.node_token for node in state.due_nodes(
                date(2000, 12, 2),
                registry,
            )),
            (replay_token,),
        )
        self.assertIs(state.match_state(replay_token), completion.replay)
        self.assertTrue(replay_node.extra_time_capable)
        self.assertTrue(replay_node.decisive_tiebreak)
        self.assertEqual(replay_node.auxiliary_flag, original.auxiliary_flag)
        self.assertIs(completion.replay.prior_match, original)
        self.assertIs(original.following_match, completion.replay)

        restored = DomesticCupScheduleState.restore(state.snapshot())
        restored_original = restored.match_state(result_token)
        restored_replay = restored.match_state(replay_token)

        self.assertEqual(restored.node(replay_token).scheduled_date, date(2000, 12, 2))
        self.assertIs(restored_replay.prior_match, restored_original)
        self.assertIs(restored_original.following_match, restored_replay)

        replay_completion = complete_cup_match(
            restored_replay,
            registry,
            2,
            1,
        )
        restored.mark_completed(replay_token)
        self.assertEqual(replay_completion.outcome.winner_club_id, 20)
        self.assertEqual(registry.outcomes[result_token].winner_club_id, 20)

    def test_snapshot_roundtrip_preserves_symbolic_refs_and_completion(self):
        first_token = ("cup_first_leg", 5, 185, 3)
        first = cup_node(
            node_kind="first_leg_match",
            competition_id=5,
            round_id=185,
            pair_index=3,
            week=2,
            weekday=3,
            left=CupClubRefDescriptor(
                type_code=1,
                selector=1,
                competition_id=5,
                competition_context=0,
                reference_token=("cup_result", 5, 184, 1),
            ),
            right=direct_club_ref(2),
            token=first_token,
        )
        state = DomesticCupScheduleState.from_startup_nodes(
            (first,),
            season_year=2000,
        )
        state.mark_completed(first_token)

        restored = DomesticCupScheduleState.restore(state.snapshot())

        self.assertEqual(restored, state)


if __name__ == "__main__":
    unittest.main()
