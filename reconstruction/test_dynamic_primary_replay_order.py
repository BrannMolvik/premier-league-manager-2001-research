import unittest
from datetime import date, timedelta
from types import SimpleNamespace

from competition_schedule import direct_club_ref
from domestic_cup_state import DomesticCupScheduledNode, DomesticCupScheduleState
from game_state import GameState
from primary_schedule_shadow import (
    PrimaryScheduleShadowEntry,
    PrimaryScheduleShadowState,
)


def shadow_entry(token, left, right):
    return PrimaryScheduleShadowEntry(
        node_kind="fixed_league_match",
        competition_id=0,
        competition_context=0,
        node_token=tuple(token),
        participant_0_ref=direct_club_ref(left),
        participant_1_ref=direct_club_ref(right),
        participant_0_candidates=frozenset((int(left),)),
        participant_1_candidates=frozenset((int(right),)),
    )


def replay_node(on_date):
    return DomesticCupScheduledNode(
        node_kind="replay_match",
        competition_id=1,
        competition_context=0,
        round_id=38,
        pair_index=0,
        scheduled_date=on_date,
        participant_0_ref=direct_club_ref(20),
        participant_1_ref=direct_club_ref(10),
        node_token=("cup_replay", 1, 38, 0),
        round_number=1,
        extra_time_capable=True,
        decisive_tiebreak=True,
    )


class DynamicPrimaryReplayOrderTests(unittest.TestCase):
    def test_615a60_restarts_two_days_after_each_nearby_conflict(self):
        requested = date(2000, 12, 2)
        shadow = PrimaryScheduleShadowState(
            days={
                requested: (shadow_entry(("league", 1), 10, 30),),
                requested + timedelta(days=3): (
                    shadow_entry(("league", 2), 20, 40),
                ),
            }
        )

        chosen = shadow.choose_dynamic_insertion_date(
            replay_node(requested),
            requested_date=requested,
            current_date=date(2000, 11, 18),
        )

        self.assertEqual(chosen, requested + timedelta(days=5))

    def test_615a60_clamps_candidate_to_current_day_plus_one(self):
        current = date(2000, 12, 10)
        shadow = PrimaryScheduleShadowState(days={})

        chosen = shadow.choose_dynamic_insertion_date(
            replay_node(date(2000, 12, 2)),
            requested_date=date(2000, 12, 2),
            current_date=current,
        )

        self.assertEqual(chosen, current + timedelta(days=1))

    def test_game_state_reschedules_and_head_inserts_dynamic_replay(self):
        requested = date(2000, 12, 2)
        conflict_date = requested
        chosen = requested + timedelta(days=2)
        replay = replay_node(requested)
        state = GameState.from_players((), date(2000, 11, 18))
        state.domestic_cups = DomesticCupScheduleState(nodes=(replay,))
        state.primary_schedule_shadow = PrimaryScheduleShadowState(
            days={
                conflict_date: (
                    shadow_entry(("league", 1), 10, 30),
                ),
                chosen: (
                    shadow_entry(("old", 1), 50, 60),
                ),
            }
        )
        old_entry = ("premier_league", 999)
        state.primary_matchday_order = {chosen: (old_entry,)}
        completion = SimpleNamespace(
            replay=SimpleNamespace(node_token=replay.node_token)
        )

        integrated = state._integrate_dynamic_cup_replay(
            state.domestic_cups,
            completion,
        )

        self.assertEqual(integrated.scheduled_date, chosen)
        self.assertEqual(
            state.domestic_cups.node(replay.node_token).scheduled_date,
            chosen,
        )
        self.assertEqual(
            state.primary_matchday_order[chosen],
            (("domestic_cup", replay.node_token), old_entry),
        )
        self.assertEqual(
            state.primary_schedule_shadow.days[chosen][0].node_token,
            replay.node_token,
        )


if __name__ == "__main__":
    unittest.main()
