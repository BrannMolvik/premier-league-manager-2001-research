import unittest
from types import SimpleNamespace

from competition_schedule import (
    club_refs_conflict,
    direct_club_ref,
    materialize_cup_round_schedule_nodes,
    materialize_fixed_league_schedule_nodes,
    materialize_procedural_league_schedule_nodes,
    materialize_scot_premier_split_schedule_nodes,
    ordered_league_schedule_entries,
)
from competition_startup import (
    CupClubRefDescriptor,
    CupPairingDescriptor,
    MaterializedCupRound,
)
from procedural_league import (
    ProceduralLeagueMatchEmission,
    materialize_scot_premier_split_match_emissions,
)


class CompetitionScheduleTests(unittest.TestCase):
    def _round_definition(self, type_code):
        return SimpleNamespace(
            id=77,
            type_code=type_code,
            scheduled_week=12,
            scheduled_weekday=6,
            replay_week=13,
            replay_weekday=3,
        )

    def _pairing(self, round_type):
        left = direct_club_ref(10)
        right = direct_club_ref(20)
        return CupPairingDescriptor(
            competition_id=5,
            round_id=77,
            round_type=round_type,
            pair_index=0,
            left_ref=left,
            right_ref=right,
            result_token=("cup_result", 5, 77, 0),
        )

    def test_normal_cup_round_emits_one_node_per_pair(self):
        pairing = self._pairing(1)
        runtime_round = MaterializedCupRound(
            round_id=77,
            round_type=1,
            participant_refs=(pairing.left_ref, pairing.right_ref),
            pairings=(pairing,),
        )

        nodes = materialize_cup_round_schedule_nodes(
            runtime_round,
            self._round_definition(1),
            competition_id=5,
        )

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].node_kind, "cup_match")
        self.assertEqual(
            (nodes[0].scheduled_week, nodes[0].scheduled_weekday),
            (12, 6),
        )
        self.assertEqual(nodes[0].participant_0_ref.direct_club_id, 10)
        self.assertEqual(nodes[0].participant_1_ref.direct_club_id, 20)
        self.assertEqual(nodes[0].node_token, ("cup_result", 5, 77, 0))

    def test_two_leg_round_reverses_second_leg_refs(self):
        pairing = self._pairing(2)
        runtime_round = MaterializedCupRound(
            round_id=77,
            round_type=2,
            participant_refs=(pairing.left_ref, pairing.right_ref),
            pairings=(pairing,),
        )

        nodes = materialize_cup_round_schedule_nodes(
            runtime_round,
            self._round_definition(2),
            competition_id=5,
        )

        self.assertEqual(
            [node.node_kind for node in nodes],
            ["first_leg_match", "second_leg_match"],
        )
        self.assertEqual(
            [
                (
                    node.participant_0_ref.direct_club_id,
                    node.participant_1_ref.direct_club_id,
                    node.scheduled_week,
                    node.scheduled_weekday,
                )
                for node in nodes
            ],
            [
                (10, 20, 12, 6),
                (20, 10, 13, 3),
            ],
        )
        self.assertEqual(nodes[1].node_token, ("cup_result", 5, 77, 0))

    def test_minileague_parent_round_emits_no_match_nodes(self):
        runtime_round = MaterializedCupRound(
            round_id=77,
            round_type=3,
            participant_refs=(),
            pairings=(),
            minileague_groups=(),
        )
        self.assertEqual(
            materialize_cup_round_schedule_nodes(
                runtime_round,
                self._round_definition(3),
                competition_id=5,
            ),
            (),
        )

    def test_fixed_league_nodes_preserve_round_then_fixture_table_order(self):
        rounds = (
            SimpleNamespace(
                id=10,
                competition_id=0,
                scheduled_week=1,
                scheduled_weekday=6,
            ),
            SimpleNamespace(
                id=11,
                competition_id=0,
                scheduled_week=2,
                scheduled_weekday=3,
            ),
            SimpleNamespace(
                id=12,
                competition_id=99,
                scheduled_week=1,
                scheduled_weekday=1,
            ),
        )
        fixtures = (
            SimpleNamespace(
                id=100,
                round_index=11,
                home_club_id=1,
                away_club_id=2,
            ),
            SimpleNamespace(
                id=101,
                round_index=10,
                home_club_id=3,
                away_club_id=4,
            ),
            SimpleNamespace(
                id=102,
                round_index=10,
                home_club_id=5,
                away_club_id=6,
            ),
        )

        nodes = materialize_fixed_league_schedule_nodes(
            rounds,
            fixtures,
            competition_id=0,
        )

        self.assertEqual(
            [
                (
                    node.round_id,
                    node.pair_index,
                    node.participant_0_ref.direct_club_id,
                    node.participant_1_ref.direct_club_id,
                    node.scheduled_week,
                    node.scheduled_weekday,
                )
                for node in nodes
            ],
            [
                (10, 0, 3, 4, 1, 6),
                (10, 1, 5, 6, 1, 6),
                (11, 0, 1, 2, 2, 3),
            ],
        )

    def test_league_schedule_entries_sort_runtime_week_then_weekday(self):
        rounds = (
            SimpleNamespace(scheduled_week=12, scheduled_weekday=6),
            SimpleNamespace(scheduled_week=10, scheduled_weekday=6),
            SimpleNamespace(scheduled_week=10, scheduled_weekday=3),
            SimpleNamespace(scheduled_week=10, scheduled_weekday=3),
        )

        self.assertEqual(
            ordered_league_schedule_entries(rounds),
            ((10, 3), (10, 3), (10, 6), (12, 6)),
        )

    def test_procedural_league_node_uses_exact_schedule_index(self):
        emission = ProceduralLeagueMatchEmission(
            round_index=1,
            pair_index=0,
            cycle_index=1,
            schedule_index=4,
            home_team=30,
            away_team=40,
        )
        dates = [(10 + index, 6) for index in range(6)]

        node = materialize_procedural_league_schedule_nodes(
            (emission,),
            dates,
            competition_id=14,
            competition_context=2,
        )[0]

        self.assertEqual(node.node_kind, "league_match")
        self.assertEqual(node.schedule_index, 4)
        self.assertEqual((node.scheduled_week, node.scheduled_weekday), (14, 6))
        self.assertEqual(node.participant_0_ref.direct_club_id, 30)
        self.assertEqual(node.participant_1_ref.direct_club_id, 40)

    def test_scottish_split_nodes_preserve_type4_symbolic_identity(self):
        emissions = materialize_scot_premier_split_match_emissions(12, 38)
        dates = [(index, 6) for index in range(38)]

        nodes = materialize_scot_premier_split_schedule_nodes(
            emissions,
            dates,
        )

        self.assertEqual(len(nodes), 30)
        self.assertEqual(
            (
                nodes[0].schedule_index,
                nodes[0].participant_0_ref.type_code,
                nodes[0].participant_0_ref.selector,
                nodes[0].participant_1_ref.selector,
            ),
            (33, 4, 3, 1),
        )
        self.assertEqual(
            (
                nodes[1].schedule_index,
                nodes[1].participant_0_ref.selector,
                nodes[1].participant_1_ref.selector,
            ),
            (33, 2, 0),
        )
        self.assertEqual(nodes[-1].schedule_index, 37)

    def test_club_ref_conflict_matches_direct_and_symbolic_rules(self):
        self.assertTrue(club_refs_conflict(direct_club_ref(1), direct_club_ref(1)))
        self.assertFalse(club_refs_conflict(direct_club_ref(1), direct_club_ref(2)))

        symbolic_a = CupClubRefDescriptor(
            type_code=2,
            selector=3,
            competition_id=14,
            competition_context=1,
            reference_token=("group_position", 14, 1, 3),
        )
        symbolic_same = CupClubRefDescriptor(
            type_code=2,
            selector=3,
            competition_id=14,
            competition_context=1,
            reference_token=("different_semantic_label",),
        )
        symbolic_other_slot = CupClubRefDescriptor(
            type_code=2,
            selector=2,
            competition_id=14,
            competition_context=1,
        )

        self.assertTrue(club_refs_conflict(symbolic_a, symbolic_same))
        self.assertFalse(club_refs_conflict(symbolic_a, symbolic_other_slot))
        self.assertFalse(club_refs_conflict(direct_club_ref(1), symbolic_a))


if __name__ == "__main__":
    unittest.main()
