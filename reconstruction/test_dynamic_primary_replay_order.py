import unittest
import os
from pathlib import Path
from datetime import date, timedelta
from dataclasses import replace
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
        # Original freshly constructed 0x5103D0 match +0x44 is zero.
        # Explicitly qualified only for these normal fixed-League fixtures.
        payload_filter_bits=0,
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

    def test_original_dynamic_event8_linked_skip_precedes_flag_and_club_comparison(self):
        requested=date(2000,12,2)
        root=shadow_entry(("league",1),20,30)
        linked=replace(root,wrapper_link_state="linked",payload_filter_bits=None)
        shadow=PrimaryScheduleShadowState(days={requested:(linked,)})
        chosen=shadow.choose_dynamic_insertion_date(
            replay_node(requested),requested_date=requested,
            current_date=date(2000,11,18))
        self.assertEqual(chosen,requested)
        self.assertEqual(shadow.days[requested],(linked,))

    def test_original_dynamic_payload_bit6_skip_precedes_symbolic_club_comparison(self):
        requested=date(2000,12,2)
        root=shadow_entry(("league",1),20,30)
        skipped=replace(root,wrapper_link_state="clear",payload_filter_bits=0x40)
        shadow=PrimaryScheduleShadowState(days={requested:(skipped,)})
        self.assertEqual(shadow.first_dynamic_conflict_near(replay_node(requested),requested),None)
        self.assertEqual(shadow.choose_dynamic_insertion_date(
            replay_node(requested),requested_date=requested,
            current_date=date(2000,11,18)),requested)

    def test_unknown_original_dynamic_event_filters_fail_closed(self):
        requested=date(2000,12,2)
        root=shadow_entry(("league",1),20,30)
        for item in (
            replace(root,wrapper_link_state="unknown"),
            replace(root,payload_filter_bits=None),
            replace(root,node_kind="unverified_original_class"),
        ):
            with self.subTest(item=item):
                shadow=PrimaryScheduleShadowState(days={requested:(item,)})
                before=shadow.snapshot()
                with self.assertRaises(RuntimeError):
                    shadow.first_dynamic_conflict_near(replay_node(requested),requested)
                self.assertEqual(shadow.snapshot(),before)

    def test_true_original_adjacent_filter_order_preserves_earliest_eligible_bucket(self):
        requested=date(2000,12,2)
        linked=replace(shadow_entry(("linked",1),20,30),
                       wrapper_link_state="linked",payload_filter_bits=None)
        bit6=replace(shadow_entry(("flagged",1),20,30),payload_filter_bits=0x40)
        eligible=shadow_entry(("eligible",1),20,30)
        shadow=PrimaryScheduleShadowState(days={
            requested-timedelta(days=1):(linked,),
            requested:(bit6,eligible),
            requested+timedelta(days=1):(shadow_entry(("later",1),20,40),),
        })
        self.assertEqual(
            shadow.first_dynamic_conflict_near(replay_node(requested),requested),
            requested)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner private original executable not available in hosted CI")
    def test_original_615a60_forward_insert_native_site_evidence(self):
        from gate13_button_source_trace import OriginalPE32
        original=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x615A60:"a1 fc 47 98 00",
            0x615A6E:"2b 43 08",
            0x615A71:"40",
            0x615A72:"3b f8",
            0x615A85:"e8 06 fe ff ff",
            0x615A97:"8d 79 02",
            0x615A9E:"e8 ed fd ff ff",
            0x615AAD:"8d 3c b8",
            0x615AB0:"ff 52 18",
            0x615AB5:"e8 46 a8 ef ff",
            0x615AC0:"c1 f9 02",
            0x615AC3:"89 4e 10",
            0x615AC6:"8b 17",
            0x615AC8:"89 56 04",
            0x615ACB:"89 37",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(original.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))

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
        replay_state = SimpleNamespace()
        state.domestic_cups.match_states[replay.node_token] = replay_state
        completion = SimpleNamespace(replay=replay_state)

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
