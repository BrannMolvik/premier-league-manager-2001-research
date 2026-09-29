import unittest

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_startup import CupClubRefDescriptor
from cup_progression import CupResultRegistry
from procedural_league_state import LiveProceduralLeagueState


def league_node(index, home, away, *, competition_id=14, context=3):
    def ref(value):
        if isinstance(value, CupClubRefDescriptor):
            return value
        return direct_club_ref(value)

    return StartupScheduleNode(
        node_kind="league_match",
        competition_id=competition_id,
        competition_context=context,
        round_id=None,
        pair_index=index,
        schedule_index=index,
        scheduled_week=10 + index,
        scheduled_weekday=3,
        participant_0_ref=ref(home),
        participant_1_ref=ref(away),
        node_token=("league_match", competition_id, context, index),
    )


class LiveProceduralLeagueStateTests(unittest.TestCase):
    def test_materializes_resolved_schedule_nodes_and_records_table(self):
        registry = CupResultRegistry()
        nodes = (
            league_node(0, 10, 20),
            league_node(1, 30, 40),
            league_node(2, 10, 30),
            league_node(3, 20, 40),
        )
        state = LiveProceduralLeagueState.from_schedule_nodes(
            nodes,
            registry.resolve_club_ref,
        )
        self.assertIsNotNone(state)
        self.assertEqual(state.club_ids, (10, 20, 30, 40))

        state.record_result(nodes[0].node_token, 3, 0)
        state.record_result(nodes[1].node_token, 1, 0)
        state.record_result(nodes[2].node_token, 2, 1)
        state.record_result(nodes[3].node_token, 0, 2)

        table = state.table()
        self.assertEqual(tuple(row.club_id for row in table), (10, 40, 30, 20))
        self.assertEqual(state.exact_ranking(), (10, 40, 30, 20))

    def test_symbolic_type2_participant_waits_for_source_ranking(self):
        registry = CupResultRegistry()
        symbolic = CupClubRefDescriptor(
            type_code=2,
            selector=1,
            competition_id=7,
            competition_context=0,
        )
        node = league_node(0, symbolic, 20)

        self.assertIsNone(
            LiveProceduralLeagueState.from_schedule_nodes(
                (node,),
                registry.resolve_club_ref,
            )
        )

        registry.record_competition_ranking(7, (100, 101, 102))
        state = LiveProceduralLeagueState.from_schedule_nodes(
            (node,),
            registry.resolve_club_ref,
        )
        self.assertIsNotNone(state)
        self.assertEqual(state.club_ids, (101, 20))

    def test_equal_proven_keys_keep_ranking_pending(self):
        registry = CupResultRegistry()
        nodes = (
            league_node(0, 10, 20),
            league_node(1, 30, 40),
        )
        state = LiveProceduralLeagueState.from_schedule_nodes(
            nodes,
            registry.resolve_club_ref,
        )
        state.record_result(nodes[0].node_token, 1, 0)
        state.record_result(nodes[1].node_token, 1, 0)

        # 10 and 30 are both 3 pts, +1 GD, 1 GF. The clean-room table can
        # display a stable order, but that unresolved fallback is not published.
        self.assertIsNone(state.exact_ranking())
        self.assertIsNone(state.publish_exact_ranking(registry))
        self.assertEqual(registry.competition_rankings, {})

    def test_unique_ranking_publishes_to_type2_registry(self):
        registry = CupResultRegistry()
        nodes = (
            league_node(0, 10, 20),
            league_node(1, 30, 40),
            league_node(2, 10, 30),
            league_node(3, 20, 40),
        )
        state = LiveProceduralLeagueState.from_schedule_nodes(
            nodes,
            registry.resolve_club_ref,
        )
        state.record_result(nodes[0].node_token, 3, 0)
        state.record_result(nodes[1].node_token, 1, 0)
        state.record_result(nodes[2].node_token, 2, 1)
        state.record_result(nodes[3].node_token, 0, 2)

        self.assertEqual(
            state.publish_exact_ranking(registry),
            (10, 40, 30, 20),
        )
        ref = CupClubRefDescriptor(
            type_code=2,
            selector=2,
            competition_id=14,
            competition_context=3,
        )
        self.assertEqual(registry.resolve_club_ref(ref), 30)

    def test_duplicate_result_is_rejected(self):
        registry = CupResultRegistry()
        node = league_node(0, 10, 20)
        state = LiveProceduralLeagueState.from_schedule_nodes(
            (node,),
            registry.resolve_club_ref,
        )
        state.record_result(node.node_token, 2, 1)
        with self.assertRaises(ValueError):
            state.record_result(node.node_token, 0, 0)


if __name__ == "__main__":
    unittest.main()
