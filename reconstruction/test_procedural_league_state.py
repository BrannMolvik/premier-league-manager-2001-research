import unittest
from datetime import date

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_startup import CupClubRefDescriptor
from cup_progression import CupResultRegistry
from game_state import GameCalendar, GameState
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

    def test_ambiguous_complete_group_withdraws_any_stale_ranking(self):
        registry = CupResultRegistry()
        nodes = (
            league_node(0, 10, 20),
            league_node(1, 30, 40),
        )
        state = LiveProceduralLeagueState.from_schedule_nodes(
            nodes,
            registry.resolve_club_ref,
        )
        registry.record_competition_ranking(
            14,
            (10, 20, 30, 40),
            competition_context=3,
        )
        state.record_result(nodes[0].node_token, 1, 0)
        state.record_result(nodes[1].node_token, 1, 0)
        self.assertTrue(state.is_complete)
        self.assertIsNone(state.publish_exact_ranking(registry))
        self.assertEqual(registry.competition_rankings, {})

    def test_snapshot_roundtrip_preserves_fixtures_and_results(self):
        registry = CupResultRegistry()
        nodes = (league_node(0, 10, 20), league_node(1, 30, 40))
        state = LiveProceduralLeagueState.from_schedule_nodes(
            nodes,
            registry.resolve_club_ref,
        )
        state.record_result(nodes[0].node_token, 3, 1)
        restored = LiveProceduralLeagueState.restore(state.snapshot())
        self.assertEqual(restored.competition_id, 14)
        self.assertEqual(restored.competition_context, 3)
        self.assertEqual(restored.club_ids, state.club_ids)
        self.assertEqual(restored.fixtures, state.fixtures)
        self.assertEqual(restored.results, state.results)

    def test_game_state_materializes_phase2_after_phase1_ranking_is_published(self):
        phase1 = (
            league_node(0, 10, 20, competition_id=14, context=0),
            league_node(1, 30, 40, competition_id=14, context=0),
            league_node(2, 10, 30, competition_id=14, context=0),
            league_node(3, 20, 40, competition_id=14, context=0),
        )
        phase2_ref = CupClubRefDescriptor(
            type_code=2,
            selector=1,
            competition_id=14,
            competition_context=0,
        )
        phase2 = league_node(
            0,
            phase2_ref,
            50,
            competition_id=167,
            context=0,
        )
        state = GameState(calendar=GameCalendar(date(2000, 7, 1)), players={})
        buckets = tuple((node,) for node in phase1 + (phase2,))
        state.install_primary_schedule_shadow(buckets, season_year=2000)

        state.refresh_european_procedural_leagues()
        self.assertIn((14, 0), state.procedural_leagues)
        self.assertNotIn((167, 0), state.procedural_leagues)

        scores = ((3, 0), (1, 0), (2, 1), (0, 2))
        for node, score in zip(phase1, scores):
            state.record_procedural_league_result(node.node_token, *score)

        self.assertEqual(
            state.cup_results.competition_rankings[(14, 0)],
            (10, 40, 30, 20),
        )
        self.assertIn((167, 0), state.procedural_leagues)
        self.assertEqual(state.procedural_leagues[(167, 0)].club_ids, (40, 50))

    def test_advancement_places_follow_canonical_type2_selectors_only(self):
        source0 = CupClubRefDescriptor(
            type_code=2,
            selector=0,
            competition_id=14,
            competition_context=3,
        )
        source1 = CupClubRefDescriptor(
            type_code=2,
            selector=1,
            competition_id=14,
            competition_context=3,
        )
        uefa_third = CupClubRefDescriptor(
            type_code=3,
            selector=2,
            competition_id=14,
            competition_context=3,
        )
        nodes = (
            league_node(0, source0, 50, competition_id=167, context=0),
            league_node(1, source1, 51, competition_id=167, context=0),
            league_node(2, uefa_third, 52, competition_id=10, context=0),
        )
        state = GameState(calendar=GameCalendar(date(2000, 7, 1)), players={})
        state.install_primary_schedule_shadow(
            tuple((node,) for node in nodes),
            season_year=2000,
        )
        self.assertEqual(state.procedural_league_advancement_places(14, 3), 2)

    def test_non_contiguous_advancement_selectors_are_rejected(self):
        source = CupClubRefDescriptor(
            type_code=2,
            selector=2,
            competition_id=14,
            competition_context=3,
        )
        node = league_node(0, source, 50, competition_id=167, context=0)
        state = GameState(calendar=GameCalendar(date(2000, 7, 1)), players={})
        state.install_primary_schedule_shadow(((node,),), season_year=2000)
        with self.assertRaisesRegex(RuntimeError, "non-contiguous"):
            state.procedural_league_advancement_places(14, 3)

    def test_due_group_entry_is_exposed_and_blocks_unimplemented_execution(self):
        node = league_node(0, 10, 20, competition_id=14, context=2)
        state = GameState(calendar=GameCalendar(date(2000, 8, 26)), players={})
        state.primary_matchday_order = {
            date(2000, 8, 26): (
                ("procedural_league", node.node_token),
            )
        }
        live = LiveProceduralLeagueState.from_schedule_nodes(
            (node,),
            state.cup_results.resolve_club_ref,
        )
        state.procedural_leagues[(14, 2)] = live

        self.assertEqual(
            state.procedural_league_nodes_due_today(),
            (node.node_token,),
        )
        self.assertEqual(
            state.primary_entries_due_today(),
            (("procedural_league", node.node_token),),
        )
        with self.assertRaisesRegex(RuntimeError, "do not skip or reorder"):
            state.simulate_primary_ai_entry(
                ("procedural_league", node.node_token),
                (),
                (),
                object(),
            )

        state.record_procedural_league_result(node.node_token, 2, 0)
        self.assertEqual(state.procedural_league_nodes_due_today(), ())
        self.assertEqual(state.primary_entries_due_today(), ())

    def test_refresh_preserves_existing_group_results(self):
        nodes = (
            league_node(0, 10, 20, competition_id=14, context=1),
            league_node(1, 30, 40, competition_id=14, context=1),
        )
        state = GameState(calendar=GameCalendar(date(2000, 7, 1)), players={})
        state.install_primary_schedule_shadow(
            tuple((node,) for node in nodes),
            season_year=2000,
        )
        state.refresh_european_procedural_leagues()
        live = state.procedural_leagues[(14, 1)]
        state.record_procedural_league_result(nodes[0].node_token, 1, 0)

        state.refresh_european_procedural_leagues()

        self.assertIs(state.procedural_leagues[(14, 1)], live)
        self.assertEqual(
            live.results[nodes[0].node_token].home_goals,
            1,
        )

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
