import json
import tempfile
import unittest
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from commercial_timers import UserCommercialTimerState
from contract_maintenance import (
    ContractRenewalSuggestion,
    ContractRenewalSuggestionKind,
)
from concession_offer import ConcessionRuntimeSource
from competition_schedule import StartupScheduleNode, direct_club_ref
from cup_progression import CupMatchResolutionSnapshot, complete_cup_match
from domestic_cup_state import DomesticCupScheduleState
from finance_state import FinancialObjectiveState
from game_state import GameState
from human_gameplay import HumanGameplayController
from internal_save import (
    SAVE_SCHEMA_VERSION,
    dumps_human_gameplay,
    loads_human_gameplay,
    restore_human_gameplay,
    save_human_gameplay,
    load_human_gameplay,
    snapshot_human_gameplay,
)
from match_postmatch import PlayerTransferRequest
from procedural_league_state import LiveProceduralLeagueState
from primary_schedule_shadow import PrimaryScheduleShadowState
from match_schedule import MsvcCrtRng
from test_human_gameplay import Database, coefficient_matrix
from transfer_state import (
    ContractTerms,
    PlayerMovement,
    ScheduledTransfer,
    TransferProposal,
)
from youth_state import YouthRecord, YouthTeamState


SCHEDULER_ORDER = (
    (0, (5, 6, 7, 8, 9, 0, 1, 2, 3, 4)),
    (1, (15, 16, 17, 18, 19, 10, 11, 12, 13, 14)),
    (2, (25, 26, 27, 28, 29, 20, 21, 22, 23, 24)),
)


@dataclass(frozen=True)
class CupCompetition:
    id: int = 1
    substitute_quota: int = 5
    max_non_eu_players: int = 10
    scheduled_matchday_count: int = 8
    initialization_order_value: int = 6


@dataclass(frozen=True)
class LeagueCupCompetition:
    id: int = 5
    substitute_quota: int = 5
    max_non_eu_players: int = 10
    scheduled_matchday_count: int = 7
    initialization_order_value: int = 5


class CupDatabase(Database):
    competitions = Database.competitions + (
        CupCompetition(),
        LeagueCupCompetition(),
    )



class InternalSaveTests(unittest.TestCase):
    def build_controller(self):
        state = GameState.from_database(
            Database(),
            date(2000, 6, 30),
            seed=1,
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(SCHEDULER_ORDER)
        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )
        controller.select_club(1)
        controller.autofill_lineup(0)
        return controller

    def build_cup_controller(self):
        state = GameState.from_database(
            CupDatabase(),
            date(2000, 7, 7),
            seed=1,
            season_year=2000,
        )
        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )
        controller.select_club(1)
        controller.autofill_lineup(0)
        token = ("cup_result", 1, 43, 7)
        state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=43,
                    pair_index=7,
                    schedule_index=None,
                    scheduled_week=0,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(1),
                    participant_1_ref=direct_club_ref(2),
                    node_token=token,
                    round_number=8,
                    extra_time_capable=True,
                    decisive_tiebreak=True,
                    auxiliary_flag=False,
                ),
            ),
            season_year=2000,
        )
        state.primary_matchday_order = {
            date(2000, 7, 8): (
                ("premier_league", 5),
                ("domestic_cup", token),
                ("premier_league", 6),
            )
        }
        return controller, token

    def test_json_roundtrip_preserves_mid_matchday_controller_state(self):
        original = self.build_controller()
        fixture = original.advance_to_next_user_fixture()
        self.assertEqual(fixture.id, 0)
        self.assertEqual(original.pending_fixture_id, 0)
        self.assertEqual(
            tuple(sorted(original.state.premier_league.results)),
            (5, 6, 7, 8, 9),
        )

        text = dumps_human_gameplay(original)
        decoded = json.loads(text)
        self.assertEqual(decoded["schema_version"], SAVE_SCHEMA_VERSION)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            text,
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_primary_schedule_shadow_survives_roundtrip(self):
        original = self.build_controller()
        node = StartupScheduleNode(
            node_kind="fixed_league_match",
            competition_id=0,
            competition_context=0,
            round_id=1,
            pair_index=0,
            schedule_index=None,
            scheduled_week=0,
            scheduled_weekday=1,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=("fixed_league_match", 0, 0, 99),
        )
        original.state.install_primary_schedule_shadow(
            ((node,),),
            season_year=2000,
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.primary_schedule_shadow,
            original.state.primary_schedule_shadow,
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_primary_matchday_order_survives_roundtrip(self):
        original = self.build_controller()
        original.state.primary_matchday_order = {
            date(2000, 7, 8): (
                ("domestic_cup", ("cup_result", 1, 38, 0)),
                ("premier_league", 0),
            )
        }

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.primary_matchday_order,
            original.state.primary_matchday_order,
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_tagged_primary_pending_state_survives_roundtrip(self):
        original = self.build_controller()
        original.pending_primary_entry = (
            "domestic_cup",
            ("cup_result", 1, 43, 4),
        )
        original._pending_after_primary_entries = (
            ("premier_league", 6),
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.pending_primary_entry,
            original.pending_primary_entry,
        )
        self.assertEqual(
            restored._pending_after_primary_entries,
            original._pending_after_primary_entries,
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_mid_matchday_human_cup_save_reload_continues_identically(self):
        original, token = self.build_cup_controller()
        pending = original.advance_to_next_user_primary_match()
        self.assertEqual(pending, ("domestic_cup", token))
        self.assertIn(5, original.state.premier_league.results)
        self.assertNotIn(6, original.state.premier_league.results)

        restored = loads_human_gameplay(
            CupDatabase(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

        original_outcome = original.play_user_primary_match()
        restored_outcome = restored.play_user_primary_match()

        self.assertEqual(
            original_outcome.user_result.score,
            restored_outcome.user_result.score,
        )
        self.assertEqual(
            tuple(entry for entry, _result in original_outcome.matchday_results),
            tuple(entry for entry, _result in restored_outcome.matchday_results),
        )
        self.assertEqual(
            original.state.cup_results.outcomes,
            restored.state.cup_results.outcomes,
        )
        self.assertEqual(
            original.state.premier_league.results,
            restored.state.premier_league.results,
        )
        self.assertEqual(original.match_rng.state, restored.match_rng.state)
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_reloaded_fa_cup_replay_executes_identically(self):
        original, _token = self.build_cup_controller()
        token = ("cup_result", 1, 38, 9)
        original.state.domestic_cups = original.state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=38,
                    pair_index=9,
                    schedule_index=None,
                    scheduled_week=0,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(1),
                    participant_1_ref=direct_club_ref(2),
                    node_token=token,
                    round_number=3,
                    extra_time_capable=True,
                    decisive_tiebreak=False,
                    auxiliary_flag=False,
                ),
            ),
            season_year=2000,
        )
        original.state.calendar.current_date = date(2000, 7, 8)
        first = original.state.domestic_cups.materialize_normal_match(
            token,
            original.state.cup_results,
        )
        first_completion = complete_cup_match(
            first,
            original.state.cup_results,
            1,
            1,
        )
        replay = original.state.domestic_cups.insert_replay_from_completion(
            token,
            first_completion,
            current_date=original.state.calendar.current_date,
        )
        original.state.calendar.current_date = replay.scheduled_date

        restored = loads_human_gameplay(
            CupDatabase(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        original_result, original_completion = original.state.simulate_domestic_cup_ai_node(
            replay.node_token,
            coefficient_matrix(),
            coefficient_matrix(),
            original.match_rng,
        )
        restored_result, restored_completion = restored.state.simulate_domestic_cup_ai_node(
            replay.node_token,
            coefficient_matrix(),
            coefficient_matrix(),
            restored.match_rng,
        )

        self.assertEqual(original_result.score, restored_result.score)
        self.assertEqual(
            original_completion.outcome.winner_club_id,
            restored_completion.outcome.winner_club_id,
        )
        self.assertEqual(original.match_rng.state, restored.match_rng.state)
        self.assertEqual(
            original.state.domestic_cups.snapshot(),
            restored.state.domestic_cups.snapshot(),
        )
        self.assertEqual(
            original.state.cup_results.outcomes,
            restored.state.cup_results.outcomes,
        )

    def test_reloaded_league_cup_second_leg_executes_identically(self):
        original, _token = self.build_cup_controller()
        first_token = ("cup_first_leg", 5, 185, 10)
        result_token = ("cup_result", 5, 185, 10)
        original.state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="first_leg_match",
                    competition_id=5,
                    competition_context=0,
                    round_id=185,
                    pair_index=10,
                    schedule_index=None,
                    scheduled_week=0,
                    scheduled_weekday=3,
                    participant_0_ref=direct_club_ref(1),
                    participant_1_ref=direct_club_ref(2),
                    node_token=first_token,
                    round_number=6,
                    extra_time_capable=False,
                    decisive_tiebreak=False,
                    auxiliary_flag=False,
                ),
                StartupScheduleNode(
                    node_kind="second_leg_match",
                    competition_id=5,
                    competition_context=0,
                    round_id=185,
                    pair_index=10,
                    schedule_index=None,
                    scheduled_week=1,
                    scheduled_weekday=3,
                    participant_0_ref=direct_club_ref(2),
                    participant_1_ref=direct_club_ref(1),
                    node_token=result_token,
                    round_number=6,
                    extra_time_capable=True,
                    decisive_tiebreak=True,
                    auxiliary_flag=False,
                ),
            ),
            season_year=2000,
        )
        first, _second = original.state.domestic_cups.materialize_two_leg_pair(
            first_token,
            original.state.cup_results,
        )
        complete_cup_match(first, original.state.cup_results, 2, 1)
        original.state.domestic_cups.mark_completed(first_token)
        original.state.calendar.current_date = original.state.domestic_cups.node(
            result_token
        ).scheduled_date

        restored = loads_human_gameplay(
            CupDatabase(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        original_result, original_completion = original.state.simulate_domestic_cup_ai_node(
            result_token,
            coefficient_matrix(),
            coefficient_matrix(),
            original.match_rng,
        )
        restored_result, restored_completion = restored.state.simulate_domestic_cup_ai_node(
            result_token,
            coefficient_matrix(),
            coefficient_matrix(),
            restored.match_rng,
        )

        self.assertEqual(original_result.score, restored_result.score)
        self.assertEqual(
            original_completion.outcome.winner_club_id,
            restored_completion.outcome.winner_club_id,
        )
        self.assertEqual(original.match_rng.state, restored.match_rng.state)
        self.assertEqual(
            original.state.domestic_cups.snapshot(),
            restored.state.domestic_cups.snapshot(),
        )
        self.assertEqual(
            original.state.cup_results.outcomes,
            restored.state.cup_results.outcomes,
        )

    def test_cup_result_registry_survives_roundtrip(self):
        original = self.build_controller()
        token = ("cup_result", 1, 38, 0)
        outcome = original.state.record_cup_match_resolution(
            token,
            CupMatchResolutionSnapshot(
                participant_0_club_id=1,
                participant_1_club_id=2,
                score_0=2,
                score_1=1,
            ),
        )
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.winner_club_id, 1)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(restored.state.cup_results.outcomes, original.state.cup_results.outcomes)
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_competition_position_rankings_survive_roundtrip(self):
        original = self.build_controller()
        original.state.cup_results.record_competition_ranking(
            14,
            (101, 202, 303, 404),
            competition_context=6,
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.cup_results.competition_rankings,
            original.state.cup_results.competition_rankings,
        )
        ref = __import__("competition_startup").CupClubRefDescriptor(
            type_code=2,
            selector=2,
            competition_id=14,
            competition_context=6,
        )
        self.assertEqual(restored.state.cup_results.resolve_club_ref(ref), 303)
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_group_position_rankings_survive_roundtrip(self):
        original = self.build_controller()
        original.state.cup_results.replace_group_position_ranking(
            14,
            2,
            (801, 802, 803, 804),
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.cup_results.group_position_rankings,
            original.state.cup_results.group_position_rankings,
        )
        ref = __import__("competition_startup").CupClubRefDescriptor(
            type_code=3,
            selector=2,
            competition_id=14,
            competition_context=3,
        )
        self.assertEqual(restored.state.cup_results.resolve_club_ref(ref), 804)

    def test_type3_uefa_dependency_survives_roundtrip_and_resolves(self):
        original = self.build_controller()
        original.state.competitions[14] = SimpleNamespace(
            id=14,
            runtime_instance_count=2,
        )

        type3_ref = __import__("competition_startup").CupClubRefDescriptor(
            type_code=3,
            selector=1,
            competition_id=14,
            competition_context=0,
        )
        uefa_token = ("cup_result", 10, 210, 0)
        uefa_node = StartupScheduleNode(
            node_kind="cup_match",
            competition_id=10,
            competition_context=0,
            round_id=210,
            pair_index=0,
            schedule_index=None,
            scheduled_week=0,
            scheduled_weekday=6,
            participant_0_ref=type3_ref,
            participant_1_ref=direct_club_ref(5),
            node_token=uefa_token,
            round_number=1,
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=False,
        )
        original.state.european_cups = DomesticCupScheduleState.from_startup_nodes(
            (uefa_node,),
            season_year=2000,
            competition_ids=(9, 10),
        )
        original.state.primary_schedule_shadow = (
            PrimaryScheduleShadowState.from_primary_schedule_buckets(
                ((uefa_node,),),
                season_year=2000,
            )
        )

        group_nodes = (
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=14,
                competition_context=0,
                round_id=None,
                pair_index=0,
                schedule_index=0,
                scheduled_week=0,
                scheduled_weekday=3,
                participant_0_ref=direct_club_ref(1),
                participant_1_ref=direct_club_ref(2),
                node_token=("league_match", 14, 0, 0),
            ),
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=14,
                competition_context=1,
                round_id=None,
                pair_index=0,
                schedule_index=0,
                scheduled_week=0,
                scheduled_weekday=3,
                participant_0_ref=direct_club_ref(3),
                participant_1_ref=direct_club_ref(4),
                node_token=("league_match", 14, 1, 0),
            ),
        )
        for node in group_nodes:
            live = LiveProceduralLeagueState.from_schedule_nodes(
                (node,),
                original.state.cup_results.resolve_club_ref,
            )
            self.assertIsNotNone(live)
            original.state.procedural_leagues[
                (node.competition_id, node.competition_context)
            ] = live

        original.state.record_procedural_league_result(
            ("league_match", 14, 0, 0),
            2,
            0,
        )
        original.state.record_procedural_league_result(
            ("league_match", 14, 1, 0),
            1,
            0,
        )
        self.assertEqual(
            original.state.cup_results.group_position_rankings[(14, 1)],
            (4, 2),
        )
        self.assertEqual(
            original.state.cup_results.resolve_club_ref(type3_ref),
            4,
        )
        original.state.calendar.current_date = date(2000, 7, 8)
        due = original.state.european_cup_nodes_due_today()
        self.assertEqual(len(due), 1)
        self.assertEqual(
            due[0].resolve_pair(original.state.cup_results),
            (4, 5),
        )

        reload_database = Database()
        reload_database.competitions = Database.competitions + (
            SimpleNamespace(id=14, runtime_instance_count=2),
        )
        restored = loads_human_gameplay(
            reload_database,
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.cup_results.group_position_rankings[(14, 1)],
            (4, 2),
        )
        restored_due = restored.state.european_cup_nodes_due_today()
        self.assertEqual(len(restored_due), 1)
        self.assertEqual(
            restored_due[0].resolve_pair(restored.state.cup_results),
            (4, 5),
        )

    def test_european_cup_schedule_state_survives_roundtrip(self):
        original = self.build_controller()
        node = StartupScheduleNode(
            node_kind="cup_match",
            competition_id=9,
            competition_context=0,
            round_id=200,
            pair_index=0,
            schedule_index=None,
            scheduled_week=10,
            scheduled_weekday=3,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=("cup_result", 9, 200, 0),
            round_number=1,
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=False,
        )
        original.state.european_cups = DomesticCupScheduleState.from_startup_nodes(
            (node,),
            season_year=2000,
            competition_ids=(9, 10),
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.european_cups.snapshot(),
            original.state.european_cups.snapshot(),
        )

    def test_live_club_competition_membership_survives_roundtrip(self):
        original = self.build_controller()
        original.state.club_competition_membership[1] = 2
        original.state.club_competition_membership[2] = 0

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(restored.state.club_competition_membership[1], 2)
        self.assertEqual(restored.state.club_competition_membership[2], 0)

    def test_english_divisional_live_set_executes_across_save_reload(self):
        original = self.build_controller()
        competition_ids = (2, 3, 4, 7)
        club_pairs = ((1, 2), (3, 4), (5, 6), (7, 8))
        first_date = date(2000, 7, 1)
        second_date = date(2000, 7, 8)
        first_entries = []
        second_entries = []

        for competition_id, (home_club_id, away_club_id) in zip(
            competition_ids,
            club_pairs,
        ):
            original.state.competitions[competition_id] = SimpleNamespace(
                id=competition_id,
                substitute_quota=5,
                max_non_eu_players=10,
            )
            first_token = ("league_match", competition_id, 0, 0)
            second_token = ("league_match", competition_id, 0, 1)
            nodes = (
                StartupScheduleNode(
                    node_kind="league_match",
                    competition_id=competition_id,
                    competition_context=0,
                    round_id=None,
                    pair_index=0,
                    schedule_index=0,
                    scheduled_week=0,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(home_club_id),
                    participant_1_ref=direct_club_ref(away_club_id),
                    node_token=first_token,
                ),
                StartupScheduleNode(
                    node_kind="league_match",
                    competition_id=competition_id,
                    competition_context=0,
                    round_id=None,
                    pair_index=1,
                    schedule_index=1,
                    scheduled_week=1,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(away_club_id),
                    participant_1_ref=direct_club_ref(home_club_id),
                    node_token=second_token,
                ),
            )
            live = LiveProceduralLeagueState.from_schedule_nodes(
                nodes,
                original.state.cup_results.resolve_club_ref,
            )
            self.assertIsNotNone(live)
            original.state.procedural_leagues[(competition_id, 0)] = live
            original.state.record_procedural_league_result(first_token, 2, 1)
            first_entries.append(("procedural_league", first_token))
            second_entries.append(("procedural_league", second_token))

        original.state.primary_matchday_order = {
            first_date: tuple(first_entries),
            second_date: tuple(second_entries),
        }
        original.state.calendar.current_date = first_date

        reload_database = Database()
        reload_database.competitions = Database.competitions + tuple(
            SimpleNamespace(
                id=competition_id,
                substitute_quota=5,
                max_non_eu_players=10,
            )
            for competition_id in competition_ids
        )
        restored = loads_human_gameplay(
            reload_database,
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        for competition_id in competition_ids:
            live = restored.state.procedural_leagues[(competition_id, 0)]
            self.assertEqual(len(live.results), 1)
            self.assertEqual(sum(row.played for row in live.table()), 2)

        restored.state.calendar.current_date = second_date
        self.assertEqual(
            restored.state.primary_entries_due_today(),
            tuple(second_entries),
        )
        outcomes = restored.state.simulate_due_primary_ai_entries(
            coefficient_matrix(),
            coefficient_matrix(),
            restored.match_rng,
        )
        self.assertEqual(
            tuple(entry for entry, _result in outcomes),
            tuple(second_entries),
        )
        for competition_id in competition_ids:
            live = restored.state.procedural_leagues[(competition_id, 0)]
            self.assertEqual(len(live.results), 2)
            self.assertEqual(sum(row.played for row in live.table()), 4)

    def test_live_procedural_league_state_survives_roundtrip(self):
        original = self.build_controller()
        node = StartupScheduleNode(
            node_kind="league_match",
            competition_id=14,
            competition_context=2,
            round_id=None,
            pair_index=0,
            schedule_index=0,
            scheduled_week=10,
            scheduled_weekday=3,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=("league_match", 14, 2, 0),
        )
        live = LiveProceduralLeagueState.from_schedule_nodes(
            (node,),
            original.state.cup_results.resolve_club_ref,
        )
        original.state.procedural_leagues[(14, 2)] = live
        original.state.record_procedural_league_result(node.node_token, 2, 0)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.procedural_leagues[(14, 2)].snapshot(),
            original.state.procedural_leagues[(14, 2)].snapshot(),
        )
        self.assertEqual(
            restored.state.cup_results.competition_rankings[(14, 2)],
            (1, 2),
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_domestic_cup_schedule_state_survives_roundtrip(self):
        original = self.build_controller()
        first_token = ("cup_first_leg", 5, 185, 3)
        result_token = ("cup_result", 5, 185, 3)
        original.state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="first_leg_match",
                    competition_id=5,
                    competition_context=0,
                    round_id=185,
                    pair_index=3,
                    schedule_index=None,
                    scheduled_week=2,
                    scheduled_weekday=3,
                    participant_0_ref=direct_club_ref(1),
                    participant_1_ref=direct_club_ref(2),
                    node_token=first_token,
                ),
                StartupScheduleNode(
                    node_kind="second_leg_match",
                    competition_id=5,
                    competition_context=0,
                    round_id=185,
                    pair_index=3,
                    schedule_index=None,
                    scheduled_week=3,
                    scheduled_weekday=3,
                    participant_0_ref=direct_club_ref(2),
                    participant_1_ref=direct_club_ref(1),
                    node_token=result_token,
                ),
            ),
            season_year=2000,
        )
        first, second = original.state.domestic_cups.materialize_two_leg_pair(
            first_token,
            original.state.cup_results,
            second_leg_extra_time_capable=True,
        )
        complete_cup_match(first, original.state.cup_results, 2, 1)
        original.state.domestic_cups.mark_completed(first_token)
        self.assertIs(second.prior_match, first)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.domestic_cups.snapshot(),
            original.state.domestic_cups.snapshot(),
        )
        restored_first = restored.state.domestic_cups.match_state(first_token)
        restored_second = restored.state.domestic_cups.match_state(result_token)
        self.assertEqual(
            (restored_first.base_score_0, restored_first.base_score_1),
            (2, 1),
        )
        self.assertIs(restored_second.prior_match, restored_first)
        self.assertIs(restored_first.following_match, restored_second)
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_dynamic_fa_cup_replay_survives_controller_roundtrip(self):
        original = self.build_controller()
        result_token = ("cup_result", 1, 38, 0)
        original.state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=38,
                    pair_index=0,
                    schedule_index=None,
                    scheduled_week=19,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(1),
                    participant_1_ref=direct_club_ref(2),
                    node_token=result_token,
                ),
            ),
            season_year=2000,
        )
        first = original.state.domestic_cups.materialize_normal_match(
            result_token,
            original.state.cup_results,
            extra_time_capable=True,
            decisive_tiebreak=False,
        )
        completion = complete_cup_match(
            first,
            original.state.cup_results,
            1,
            1,
        )
        replay_node = original.state.domestic_cups.insert_replay_from_completion(
            result_token,
            completion,
            current_date=date(2000, 11, 18),
        )
        replay_token = replay_node.node_token

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.domestic_cups.snapshot(),
            original.state.domestic_cups.snapshot(),
        )
        restored_first = restored.state.domestic_cups.match_state(result_token)
        restored_replay = restored.state.domestic_cups.match_state(replay_token)
        self.assertEqual(
            restored.state.domestic_cups.node(replay_token).scheduled_date,
            date(2000, 12, 2),
        )
        self.assertEqual(
            (
                restored_replay.participant_0_club_id,
                restored_replay.participant_1_club_id,
            ),
            (2, 1),
        )
        self.assertIs(restored_replay.prior_match, restored_first)
        self.assertIs(restored_first.following_match, restored_replay)
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_save_reload_branch_continues_identically_across_multiple_matchdays(self):
        original = self.build_controller()
        original.advance_to_next_user_fixture()
        snapshot = snapshot_human_gameplay(original)
        restored = restore_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            snapshot,
        )

        for expected_fixture_id in (0, 10, 20):
            if original.pending_fixture_id is None:
                original.autofill_lineup(0)
                restored.autofill_lineup(0)
                self.assertEqual(
                    original.advance_to_next_user_fixture().id,
                    expected_fixture_id,
                )
                self.assertEqual(
                    restored.advance_to_next_user_fixture().id,
                    expected_fixture_id,
                )
            else:
                self.assertEqual(original.pending_fixture_id, expected_fixture_id)
                self.assertEqual(restored.pending_fixture_id, expected_fixture_id)

            left = original.play_user_fixture()
            right = restored.play_user_fixture()
            self.assertEqual(left.user_result, right.user_result)
            self.assertEqual(left.matchday_results, right.matchday_results)
            self.assertEqual(left.table, right.table)
            self.assertEqual(
                snapshot_human_gameplay(restored),
                snapshot_human_gameplay(original),
            )

        self.assertEqual(len(original.state.premier_league.results), 30)
        self.assertEqual(len(restored.state.premier_league.results), 30)

    def test_gzip_file_roundtrip_preserves_state(self):
        original = self.build_controller()
        original.advance_to_next_user_fixture()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "gate8.fm2k"
            save_human_gameplay(original, path)
            self.assertEqual(path.read_bytes()[:2], b"\x1f\x8b")
            restored = load_human_gameplay(
                Database(),
                coefficient_matrix(),
                coefficient_matrix(),
                path,
            )

        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_source_signature_ignores_live_skill_changes_but_binds_source_identity(self):
        original = self.build_controller()
        original.state.players[1000].current_raw[0] += 1
        snapshot = snapshot_human_gameplay(original)

        restored = restore_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            snapshot,
        )
        self.assertEqual(
            restored.state.players[1000].current_raw[0],
            original.state.players[1000].current_raw[0],
        )

        class AlteredDatabase(Database):
            players = [
                replace(player, surname="Changed") if player.index == 1000 else player
                for player in Database.players
            ]

        with self.assertRaisesRegex(ValueError, "source database"):
            restore_human_gameplay(
                AlteredDatabase(),
                coefficient_matrix(),
                coefficient_matrix(),
                snapshot,
            )

    def test_source_signature_preserves_raw_join_date_across_live_changes(self):
        joined_date = date(1999, 1, 2)

        class JoinedDatabase(Database):
            players = [
                replace(player, joined_current_club_date=joined_date)
                if player.index == 1000
                else player
                for player in Database.players
            ]

        state = GameState.from_database(
            JoinedDatabase(),
            date(2000, 6, 30),
            seed=1,
            season_year=2000,
        )
        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )
        player = controller.state.players[1000]
        self.assertEqual(player.source_joined_current_club_date, joined_date)

        player.current_club_join_date = date(2000, 6, 29)
        snapshot = snapshot_human_gameplay(controller)
        restored = restore_human_gameplay(
            JoinedDatabase(),
            coefficient_matrix(),
            coefficient_matrix(),
            snapshot,
        )

        self.assertEqual(
            restored.state.players[1000].source_joined_current_club_date,
            joined_date,
        )
        self.assertEqual(
            restored.state.players[1000].current_club_join_date,
            date(2000, 6, 29),
        )

    def test_contract_wage_and_expiry_survive_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[1000]
        player.weekly_wage = 4321
        player.contract_expiry_date = date(2004, 6, 30)
        player.promotion_bonus = 9000
        player.appearance_fee = 450
        player.relegation_transfer_request_clause = True
        player.big_club_offer_clause = True
        player.big_money_offer_clause = False
        player.house = True
        player.car = True

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[1000]
        self.assertEqual(restored_player.weekly_wage, 4321)
        self.assertEqual(
            restored_player.contract_expiry_date,
            date(2004, 6, 30),
        )
        self.assertEqual(restored_player.promotion_bonus, 9000)
        self.assertEqual(restored_player.appearance_fee, 450)
        self.assertTrue(restored_player.relegation_transfer_request_clause)
        self.assertTrue(restored_player.big_club_offer_clause)
        self.assertFalse(restored_player.big_money_offer_clause)
        self.assertTrue(restored_player.house)
        self.assertTrue(restored_player.car)

    def test_gate11_training_commercial_calendar_survives_roundtrip(self):
        original = self.build_controller()
        original.state.configure_user_training_calendar(
            recovery_threshold=50,
            quality_multiplier=1.30,
        )
        original.state.user_commercial_timers = UserCommercialTimerState(
            concession_wait_days=15,
            concession_elapsed_days=4,
            sponsor_wait_days=8,
            sponsor_elapsed_days=2,
        )
        original.state.user_concession_source = ConcessionRuntimeSource(
            selector_capacities=(0, 16, 0, 20, 0, 12, 0, 14),
            stadium_total=62,
            club_metric=38500,
            access_metric=80000,
        )

        restored = restore_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            snapshot_human_gameplay(original),
        )

        self.assertEqual(restored.state.user_training_recovery_threshold, 50)
        self.assertEqual(restored.state.user_training_quality_multiplier, 1.30)
        self.assertEqual(
            restored.state.user_commercial_timers,
            original.state.user_commercial_timers,
        )
        self.assertEqual(
            restored.state.user_concession_source,
            original.state.user_concession_source,
        )

    def test_original_training_state_survives_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[1000]
        player.set_training_method(3)
        player.training_countdown = 2
        player.training_active_count = 4
        player.training_modifiers[1] = 2
        player.training_skill_states[1] = 0
        player.training_method_results[3] = 6

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[1000]
        self.assertEqual(restored_player.training_method_id, 3)
        self.assertEqual(restored_player.training_countdown, 2)
        self.assertEqual(restored_player.training_active_count, 4)
        self.assertEqual(restored_player.training_modifiers[1], 2)
        self.assertEqual(restored_player.training_skill_states[1], 0)
        self.assertEqual(restored_player.training_method_results[3], 6)

    def test_match_performance_history_survives_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[1000]
        for value in (6, 7, 8, 9, 10, 5, 4):
            player.append_match_performance(value)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[1000]
        self.assertEqual(
            restored_player.match_performance_history,
            [4, 7, 8, 9, 10, 5],
        )
        self.assertEqual(restored_player.match_performance_history_count, 6)
        self.assertEqual(restored_player.match_performance_history_write_index, 1)
        self.assertAlmostEqual(restored_player.match_performance_average(), 43 / 6)

    def test_current_club_join_date_survives_roundtrip(self):
        original = self.build_controller()
        original.state.players[1000].current_club_join_date = date(2000, 5, 1)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.players[1000].current_club_join_date,
            date(2000, 5, 1),
        )

    def test_signed_for_other_club_status_survives_roundtrip(self):
        original = self.build_controller()
        original.state.players[1000].signed_for_other_club = True

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertTrue(
            restored.state.players[1000].signed_for_other_club
        )

    def test_transfer_list_and_loan_status_survive_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[1000]
        player.transfer_listed = True
        player.wanted = True
        player.out_of_contract = True
        player.loan_listed = True
        player.loan_club_id = 2

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[1000]
        self.assertTrue(restored_player.transfer_listed)
        self.assertTrue(restored_player.wanted)
        self.assertTrue(restored_player.out_of_contract)
        self.assertTrue(restored_player.loan_listed)
        self.assertEqual(restored_player.loan_club_id, 2)
        self.assertTrue(restored_player.selling_squad_count_excluded)

    def test_low_morale_transfer_request_mail_survives_roundtrip(self):
        original = self.build_controller()
        original.state.player_transfer_requests.append(
            PlayerTransferRequest(
                player_id=1000,
                queued_on=date(2000, 7, 1),
                due_on=date(2000, 7, 2),
            )
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            restored.state.player_transfer_requests,
            [
                PlayerTransferRequest(
                    player_id=1000,
                    queued_on=date(2000, 7, 1),
                    due_on=date(2000, 7, 2),
                )
            ],
        )
        request = restored.state.player_transfer_requests[0]
        restored.state.calendar.current_date = date(2000, 7, 2)
        self.assertEqual(restored.state.due_player_transfer_requests(), (request,))
        restored.state.respond_to_player_transfer_request(request, accept=True)
        self.assertEqual(restored.state.player_transfer_requests, [])
        self.assertTrue(restored.state.players[1000].transfer_listed)
        self.assertTrue(restored.state.players[1000].wanted)

    def test_controlled_contract_state_and_renewal_mail_survive_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[1000]
        player.contract_special_state_138 = 7
        player.contract_renewal_suggestion_pending = True
        player.previous_club_id_74 = 2
        original.state.contract_renewal_suggestions.append(
            ContractRenewalSuggestion(
                player_id=1000,
                queued_on=date(2000, 7, 1),
                kind=ContractRenewalSuggestionKind.BOSMAN,
            )
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[1000]
        self.assertEqual(restored_player.contract_special_state_138, 7)
        self.assertTrue(restored_player.contract_renewal_suggestion_pending)
        self.assertEqual(restored_player.previous_club_id_74, 2)
        self.assertEqual(len(restored.state.contract_renewal_suggestions), 1)
        suggestion = restored.state.contract_renewal_suggestions[0]
        self.assertEqual(suggestion.player_id, 1000)
        self.assertEqual(suggestion.queued_on, date(2000, 7, 1))
        self.assertEqual(suggestion.kind, ContractRenewalSuggestionKind.BOSMAN)
        self.assertIn(
            restored.state._run_monthly_contract_maintenance,
            restored.state.calendar.monthly_hooks,
        )

    def test_youth_list_and_generated_identity_survive_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[2000]
        source_first_name = player.first_name
        source_surname = player.surname
        source_nationality = player.nationality_id
        source_dob = player.date_of_birth

        # Mirror 0x41E510/0x61DD30 live identity mutation without changing the
        # immutable source mirrors used by database validation.
        player.first_name = "Generated"
        player.surname = "Youth"
        player.nationality_id = 26
        player.date_of_birth = date(1983, 7, 1)
        player.club_id = 1
        player.status_bit_3 = True

        original.state.user_youth = YouthTeamState(
            [YouthRecord(player_id=2000, source_roster_club_id=2)]
        )
        record = original.state.user_youth.records[0]
        record.field_08 = 4
        record.field_0c = 5
        record.field_10 = 6
        record.status_14 = True
        record.training.method_id = 1
        record.training.countdown = 6
        record.training.modifiers[0] = 7

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[2000]
        self.assertEqual(restored_player.first_name, "Generated")
        self.assertEqual(restored_player.surname, "Youth")
        self.assertEqual(restored_player.nationality_id, 26)
        self.assertEqual(restored_player.date_of_birth, date(1983, 7, 1))
        self.assertTrue(restored_player.status_bit_3)

        # Immutable mirrors still identify the original supplied database.
        self.assertEqual(restored_player.source_first_name, source_first_name)
        self.assertEqual(restored_player.source_surname, source_surname)
        self.assertEqual(restored_player.source_nationality_id, source_nationality)
        self.assertEqual(restored_player.source_date_of_birth, source_dob)

        youth = restored.state.user_youth
        self.assertIsNotNone(youth)
        self.assertEqual(youth.player_ids(), (2000,))
        restored_record = youth.records[0]
        self.assertEqual(restored_record.source_roster_club_id, 2)
        self.assertEqual(
            (restored_record.field_08, restored_record.field_0c, restored_record.field_10),
            (4, 5, 6),
        )
        self.assertTrue(restored_record.status_14)
        self.assertEqual(restored_record.training.method_id, 1)
        self.assertEqual(restored_record.training.countdown, 6)
        self.assertEqual(restored_record.training.modifiers[0], 7)

    def test_weekly_ai_transfer_runtime_state_survives_roundtrip(self):
        original = self.build_controller()
        player = original.state.players[1000]
        player.ai_transfer_block_value_64 = 17
        player.ai_transfer_status_bit_9 = True
        original.state.ai_transfer_buy_counter[2] = 3
        original.state.country_transfer_window_open[0] = False
        original.state.user_controlled_club_id = 1

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_player = restored.state.players[1000]
        self.assertEqual(restored_player.ai_transfer_block_value_64, 17)
        self.assertTrue(restored_player.ai_transfer_status_bit_9)
        self.assertEqual(restored.state.ai_transfer_buy_counter[2], 3)
        self.assertFalse(restored.state.country_transfer_window_open[0])
        self.assertEqual(restored.state.user_controlled_club_id, 1)
        self.assertEqual(
            restored.state.ai_transfer_startup_roster_count,
            original.state.ai_transfer_startup_roster_count,
        )

    def test_balance_cash_and_transfer_ledger_survive_roundtrip(self):
        original = self.build_controller()
        original.state.set_current_cash(1, 1_000_000)
        original.state.set_current_cash(2, 250_000)
        original.state.post_transfer_cash(
            buyer_club_id=1,
            seller_club_id=2,
            amount=300_000,
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(restored.state.current_cash(1), 700_000)
        self.assertEqual(restored.state.current_cash(2), 549_400)
        self.assertEqual(
            [
                (entry.amount, entry.category, entry.posting_date)
                for entry in restored.state.finance_balances[1].ledger
            ],
            [(-300_000, 1000, date(2000, 6, 30))],
        )
        self.assertEqual(
            [
                (entry.amount, entry.category, entry.posting_date)
                for entry in restored.state.finance_balances[2].ledger
            ],
            [
                (-600, 1600, date(2000, 6, 30)),
                (300_000, 1000, date(2000, 6, 30)),
            ],
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_financial_objective_state_survives_roundtrip(self):
        original = self.build_controller()
        balance = original.state.set_current_cash(1, 28_000_000)
        balance.financial_objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        replacement = original.state.select_financial_objective(1, 0)
        self.assertEqual(replacement, 47_600_000)
        original.state.set_financial_objective_progression_gate(1)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        restored_balance = restored.state.finance_balances[1]
        objective = restored_balance.financial_objective
        self.assertIsNotNone(objective)
        self.assertEqual(objective.candidate_ids, (13, 1, 5))
        self.assertEqual(objective.selected_objective_id, 13)
        self.assertEqual(objective.starting_funds, 47_600_000)
        self.assertEqual(objective.target_cash, 51_800_000)
        self.assertEqual(objective.selected_on, date(2000, 6, 30))
        self.assertEqual(objective.deadline, date(2003, 6, 30))
        self.assertTrue(objective.active)
        self.assertTrue(objective.progression_gate_reached)
        self.assertEqual(objective.progression_state, 1)
        self.assertEqual(restored_balance.current_cash, 47_600_000)
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_transfer_runtime_state_survives_roundtrip(self):
        original = self.build_controller()
        terms = ContractTerms(
            weekly_wage=9000,
            signing_on_fee=120000,
            promotion_bonus=25000,
            contract_length_months=36,
            appearance_fee=500,
            big_club_offer_clause=True,
            house=True,
        )
        proposal = TransferProposal(
            target_player_id=2000,
            buying_club_id=1,
            cash_fee=1_750_000,
            exchange_player_ids=(1000, -1, -1),
            contract_terms=terms,
            previous_wage_offer=8000,
            previous_signing_on_fee_offer=100000,
            previous_total_value=2_000_000,
        )
        original.state.transfers.submit_proposal(
            proposal,
            selling_club_id=2,
            current_date=date(2000, 7, 2),
        )
        original.state.transfers.deals[2000].mark_ready()
        original.state.transfers.bid_log[(2000, 1)].status_counter = 3
        original.state.transfers.record_movement(
            PlayerMovement(
                player_id=1001,
                from_club_id=1,
                to_club_id=2,
                consideration=500000,
                movement_date=date(2000, 7, 1),
            )
        )
        original.state.transfers.schedule_transfer(
            ScheduledTransfer(
                proposal=proposal,
                due_date=date(2000, 7, 9),
                mode=1,
            )
        )

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            dumps_human_gameplay(original),
        )

        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )
        self.assertEqual(
            restored.state.transfers.proposals[(2000, 1)],
            proposal,
        )
        self.assertTrue(
            restored.state.transfers.deals[2000].ready_for_execution
        )
        self.assertEqual(
            restored.state.transfers.bid_log[(2000, 1)].status_counter,
            3,
        )
        self.assertEqual(
            restored.state.transfers.movements[-1].player_id,
            1001,
        )
        self.assertEqual(
            restored.state.transfers.scheduled_transfers,
            original.state.transfers.scheduled_transfers,
        )

    def test_wrong_source_database_is_rejected(self):
        original = self.build_controller()
        snapshot = snapshot_human_gameplay(original)

        class WrongDatabase(Database):
            players = Database.players[:-1]

        with self.assertRaisesRegex(ValueError, "source database"):
            restore_human_gameplay(
                WrongDatabase(),
                coefficient_matrix(),
                coefficient_matrix(),
                snapshot,
            )

    def test_unknown_schema_is_rejected(self):
        original = self.build_controller()
        snapshot = snapshot_human_gameplay(original)
        snapshot["schema_version"] = 999

        with self.assertRaisesRegex(ValueError, "unsupported internal save schema"):
            restore_human_gameplay(
                Database(),
                coefficient_matrix(),
                coefficient_matrix(),
                snapshot,
            )


if __name__ == "__main__":
    unittest.main()
