import unittest
from datetime import date
from unittest.mock import Mock

from competition_schedule import StartupScheduleNode, direct_club_ref
from cup_progression import CupResultRegistry
from domestic_cup_state import (
    ANNUAL_QUALIFICATION_CUP_IDS,
    DomesticCupScheduleState,
)
from game_state import GameState
from primary_schedule import gate12_primary_matchday_order


def cup_node(competition_id=19, round_number=1, token=None):
    if token is None:
        token = ("cup_result", competition_id, 500 + round_number, 0)
    return StartupScheduleNode(
        node_kind="cup_match",
        competition_id=competition_id,
        competition_context=0,
        round_id=500 + round_number,
        pair_index=0,
        schedule_index=None,
        scheduled_week=7,
        scheduled_weekday=6,
        participant_0_ref=direct_club_ref(10),
        participant_1_ref=direct_club_ref(20),
        node_token=token,
        round_number=round_number,
    )


class QualificationCupRuntimeTests(unittest.TestCase):
    def test_required_additional_cup_set_is_exact(self):
        self.assertEqual(
            ANNUAL_QUALIFICATION_CUP_IDS,
            frozenset((19, 23, 33, 91, 98, 101)),
        )

    def test_primary_order_tags_qualification_cup(self):
        node = cup_node()
        buckets = [() for _ in range(55)]
        buckets[54] = (node,)

        self.assertEqual(
            gate12_primary_matchday_order(buckets, season_year=2000),
            ((
                date(2000, 8, 26),
                (("qualification_cup", tuple(node.node_token)),),
            ),),
        )

    def test_primary_due_entries_include_qualification_cup(self):
        node = cup_node()
        on_date = date(2000, 8, 26)
        state = GameState.from_players((), on_date)
        state.qualification_cups = DomesticCupScheduleState.from_startup_nodes(
            (node,),
            season_year=2000,
            competition_ids=ANNUAL_QUALIFICATION_CUP_IDS,
        )
        entry = ("qualification_cup", tuple(node.node_token))
        state.primary_matchday_order = {on_date: (entry,)}

        self.assertEqual(state.primary_entries_due_today(), (entry,))

    def test_generic_ai_wrapper_uses_separate_qualification_owner(self):
        state = GameState.from_players((), date(2000, 8, 26))
        sentinel = (object(), object())
        state.simulate_domestic_cup_ai_node = Mock(return_value=sentinel)

        result = state.simulate_qualification_cup_ai_node(
            ("cup_result", 19, 501, 0),
            "attack",
            "defence",
            "rng",
        )

        self.assertIs(result, sentinel)
        state.simulate_domestic_cup_ai_node.assert_called_once_with(
            ("cup_result", 19, 501, 0),
            "attack",
            "defence",
            "rng",
            _schedule_state=state.qualification_cups,
            _schedule_label="qualification Cup",
        )

    def test_two_leg_final_uses_only_decisive_second_leg_outcome(self):
        first = StartupScheduleNode(
            node_kind="first_leg_match",
            competition_id=19,
            competition_context=0,
            round_id=777,
            pair_index=0,
            schedule_index=None,
            scheduled_week=40,
            scheduled_weekday=3,
            participant_0_ref=direct_club_ref(10),
            participant_1_ref=direct_club_ref(20),
            node_token=("cup_first_leg", 19, 777, 0),
            round_number=6,
        )
        second = StartupScheduleNode(
            node_kind="second_leg_match",
            competition_id=19,
            competition_context=0,
            round_id=777,
            pair_index=0,
            schedule_index=None,
            scheduled_week=42,
            scheduled_weekday=3,
            participant_0_ref=direct_club_ref(20),
            participant_1_ref=direct_club_ref(10),
            node_token=("cup_result", 19, 777, 0),
            round_number=6,
        )
        schedule = DomesticCupScheduleState.from_startup_nodes(
            (first, second),
            season_year=2000,
            competition_ids=ANNUAL_QUALIFICATION_CUP_IDS,
        )
        registry = CupResultRegistry()
        registry.record_knockout_outcome(
            tuple(second.node_token),
            20,
            10,
            20,
        )

        self.assertEqual(schedule.competition_final_pair(19, registry), (20, 10))

    def test_final_pair_uses_shared_winner_loser_semantics(self):
        final = cup_node(19, round_number=2)
        schedule = DomesticCupScheduleState.from_startup_nodes(
            (final,),
            season_year=2000,
            competition_ids=ANNUAL_QUALIFICATION_CUP_IDS,
        )
        registry = CupResultRegistry()
        registry.record_knockout_outcome(
            tuple(final.node_token),
            10,
            20,
            20,
        )

        self.assertEqual(schedule.competition_final_pair(19, registry), (20, 10))


if __name__ == "__main__":
    unittest.main()
