import unittest
from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

from finance_state import BalanceRuntimeState, FinancialObjectiveState
from competition_schedule import StartupScheduleNode, direct_club_ref
from domestic_cup_state import DomesticCupScheduleState
from game_state import GameState
from human_gameplay import HumanGameplayController
from match_engine_rng import MatchEngineRng
from match_lineup import AI_FORMATIONS
from match_schedule import MsvcCrtRng
from procedural_league_state import LiveProceduralLeagueState, ProceduralLeagueFixture
from scouting import ScoutingFilterControls, ScoutingReseedState
from match_team_setup import TeamTacticalState
from transfer_decision import SellingClubDecision
from transfer_negotiation import OrdinaryMoneyResponse
from transfer_state import ContractTerms
from youth_state import YouthRecord, YouthTeamState


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    positions: tuple[int, int, int]
    first_name: str = "Test"
    surname: str = "Player"
    nationality_id: int = 0
    date_of_birth: date | None = date(1980, 1, 1)
    shirt_number: int = 1
    height_cm: int = 180
    weight_kg: int = 75
    current_raw: tuple[int, ...] = (160,) * 17
    target_raw: tuple[int, ...] = (180,) * 17
    eu_status_code: int = 2
    joined_current_club_date: date | None = None


@dataclass(frozen=True)
class Club:
    index: int
    manager_id: int
    country_id: int = 0
    competition_id: int = 0


@dataclass(frozen=True)
class Country:
    id: int = 0
    name: str = "Testland"
    nationality_id: int = 0
    european_index: int = 1
    eu_status_flag: int = 1
    continent_id: int = 0
    financial_multiplier_percent: int = 100


@dataclass(frozen=True)
class Manager:
    index: int
    formation_default: int = 0
    formation_class3: int = 2
    formation_class1: int = 1


@dataclass(frozen=True)
class Competition:
    id: int = 0
    substitute_quota: int = 5
    max_non_eu_players: int = 10


@dataclass(frozen=True)
class Fixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


@dataclass(frozen=True)
class Round:
    round_number: int
    scheduled_week: int
    scheduled_weekday: int


def players_for_club(club_id: int):
    roles = [slot.role for slot in AI_FORMATIONS[0]]
    roles += [12, 19, 4, 1, 10, 11, 18, 9, 2]
    return [
        Player(
            index=club_id * 1000 + offset,
            club_id=club_id,
            positions=(int(role), 0, 0),
            shirt_number=offset + 1,
        )
        for offset, role in enumerate(roles)
    ]


def round_fixtures(round_index: int, start_id: int):
    fixtures = []
    for pair in range(10):
        left = pair * 2 + 1
        right = left + 1
        if round_index % 2:
            home, away = right, left
        else:
            home, away = left, right
        fixtures.append(
            Fixture(start_id + pair, round_index, home, away)
        )
    return fixtures


class Database:
    players = [
        player
        for club_id in range(1, 21)
        for player in players_for_club(club_id)
    ]
    clubs = tuple(Club(club_id, club_id) for club_id in range(1, 21))
    managers = tuple(Manager(club_id) for club_id in range(1, 21))
    competitions = (Competition(),)
    countries = (Country(),)
    real_fixtures = tuple(
        round_fixtures(0, 0)
        + round_fixtures(1, 10)
        + round_fixtures(2, 20)
    )
    premier_league_rounds = (
        Round(1, 0, 6),
        Round(2, 1, 6),
        Round(3, 2, 6),
    )


def coefficient_matrix(value=1.0):
    return tuple(
        tuple(
            tuple(float(value) for _ in range(17))
            for _ in range(20)
        )
        for _ in range(4)
    )


class HumanGameplayControllerTests(unittest.TestCase):
    def build_controller(self):
        state = GameState.from_database(
            Database(),
            date(2000, 6, 30),
            seed=1,
            season_year=2000,
        )
        state.positions.update(
            {role: SimpleNamespace(lineup_group=0) for role in range(20)}
        )
        # Put the human club-1 fixture in the middle of each same-day list so
        # the controller must execute AI matches both before and after it.
        state.install_premier_league_scheduler_order(
            (
                (0, (5, 6, 7, 8, 9, 0, 1, 2, 3, 4)),
                (1, (15, 16, 17, 18, 19, 10, 11, 12, 13, 14)),
                (2, (25, 26, 27, 28, 29, 20, 21, 22, 23, 24)),
            )
        )
        return HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )

    def set_available_lineup(self, controller):
        available = [
            player.index
            for player in controller.squad()
            if not player.base_match_unavailable
        ]
        self.assertGreaterEqual(len(available), 16)
        controller.set_lineup(
            0,
            available[:11],
            available[11:16],
        )

    def test_human_scouting_search_excludes_controlled_club_and_sorts_by_name(self):
        controller = self.build_controller()
        controller.select_club(1)

        controller.state.players[2000].surname = "Zulu"
        controller.state.players[3000].surname = "Alpha"
        controller.state.players[4000].surname = "Mike"
        controller.state.players[2000].first_name = "A"
        controller.state.players[3000].first_name = "B"
        controller.state.players[4000].first_name = "C"

        result = controller.search_scouting_players(
            ScoutingReseedState(field_64e4=3),
            candidate_predicate=lambda player: int(player.index) in {
                1000, 2000, 3000, 4000
            },
            sort_mode=0,
        )

        self.assertEqual(
            tuple(int(player.index) for player in result),
            (3000, 4000, 2000),
        )
        self.assertNotIn(1000, tuple(int(player.index) for player in result))

    def test_human_scouting_uses_live_history_and_requires_only_unmaterialized_sort_values(self):
        controller = self.build_controller()
        controller.select_club(1)
        state = ScoutingReseedState()

        controller.state.players[2000].append_match_performance(5)
        controller.state.players[3000].append_match_performance(9)
        controller.state.players[4000].append_match_performance(7)
        result = controller.search_scouting_players(
            state,
            candidate_predicate=lambda player: int(player.index) in {
                2000, 3000, 4000
            },
            sort_mode=2,
        )
        self.assertEqual(
            tuple(int(player.index) for player in result),
            (3000, 4000, 2000),
        )

        with self.assertRaisesRegex(ValueError, "position_label_resolver"):
            controller.search_scouting_players(
                state,
                candidate_predicate=lambda _player: True,
                sort_mode=3,
            )
        with self.assertRaisesRegex(ValueError, "valuation_resolver"):
            controller.search_scouting_players(
                state,
                candidate_predicate=lambda _player: True,
                sort_mode=5,
            )

    def test_human_scouting_secondary_score_uses_runtime_player_state(self):
        controller = self.build_controller()
        controller.select_club(1)

        target_ids = {2000, 3000, 4000}
        result = controller.search_scouting_players(
            ScoutingReseedState(age_low_64d8=18, field_64e4=5),
            candidate_predicate=lambda player: int(player.index) in target_ids,
            sort_mode=0,
            secondary_score_mode=16,
            secondary_caller_argument=4,
        )

        self.assertEqual(
            {int(player.index) for player in result},
            target_ids,
        )
        self.assertEqual(len(result), 3)

    def test_mapped_human_scouting_applies_runtime_age_class_value_and_transfer_status(self):
        controller = self.build_controller()
        controller.select_club(1)

        target_ids = {2000, 3000, 4000}
        for player_id in target_ids:
            player = controller.state.players[player_id]
            preferred = int(player.positions[0])
            controller.state.positions[preferred] = SimpleNamespace(lineup_group=0)
        controller.state.players[2000].surname = "Zulu"
        controller.state.players[3000].surname = "Alpha"
        controller.state.players[4000].surname = "Mike"
        controller.state.players[2000].transfer_listed = True
        controller.state.players[3000].transfer_listed = False
        controller.state.players[4000].transfer_listed = True

        panel = ScoutingReseedState(
            age_low_64d8=18,
            age_high_64dc=30,
            value_low_64c8=50.0,
            value_high_64d0=150.0,
            class_selector_64c0=1,
        )
        result = controller.search_scouting_players_mapped(
            panel,
            page_mode=16,
            valuation_resolver=lambda player: 100.0,
            team_selector_predicate=lambda player: int(player.index) in target_ids,
            optional_position_predicate=lambda _player: True,
            threshold_predicate=lambda _player: True,
            status_controls=ScoutingFilterControls(transfer_listed=True),
            sort_mode=0,
        )

        self.assertEqual(
            tuple(int(player.index) for player in result),
            (4000, 2000),
        )

    def test_mapped_human_scouting_uses_live_country_context_and_preferred_position(self):
        controller = self.build_controller()
        controller.select_club(1)

        # Club 2 shares the active club country. Club 3 is moved to a second
        # European country so panel mode 1 can select it from live metadata.
        controller.state.countries[1] = Country(
            id=1,
            name="Otherland",
            nationality_id=1,
            european_index=1,
        )
        club3 = controller.state.clubs[3]
        controller.state.clubs[3] = type(club3)(
            index=club3.index,
            manager_id=club3.manager_id,
            country_id=1,
        )

        player2 = controller.state.players[2000]
        player3 = controller.state.players[3000]
        player2.positions = (1, 7, 11)
        player3.positions = (1, 7, 11)
        controller.state.positions[1] = SimpleNamespace(lineup_group=0)

        panel = ScoutingReseedState(
            age_low_64d8=0,
            age_high_64dc=99,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=1,
            field_64e0=1,
        )
        result = controller.search_scouting_players_mapped(
            panel,
            page_mode=16,
            valuation_resolver=lambda _player: 100.0,
            threshold_predicate=lambda _player: True,
            selected_position_id=7,
            sort_mode=0,
        )

        ids = tuple(int(player.index) for player in result)
        self.assertIn(3000, ids)
        self.assertNotIn(2000, ids)

        player3.positions = (1, 5, 11)
        result = controller.search_scouting_players_mapped(
            panel,
            page_mode=16,
            valuation_resolver=lambda _player: 100.0,
            threshold_predicate=lambda _player: True,
            selected_position_id=7,
            sort_mode=0,
        )
        self.assertNotIn(3000, tuple(int(player.index) for player in result))

    def test_mapped_human_scouting_uses_live_strengths_selector_without_callback(self):
        controller = self.build_controller()
        controller.select_club(1)

        target_ids = {2000, 4000}
        for player_id in target_ids:
            player = controller.state.players[player_id]
            preferred = int(player.positions[0])
            controller.state.positions[preferred] = SimpleNamespace(lineup_group=0)
            player.current_raw[0] = 166
        controller.state.players[4000].current_raw[0] = 165

        panel = ScoutingReseedState(
            age_low_64d8=0,
            age_high_64dc=99,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=1,
            field_64e4=1,
        )
        result = controller.search_scouting_players_mapped(
            panel,
            page_mode=16,
            valuation_resolver=lambda _player: 100.0,
            team_selector_predicate=lambda player: int(player.index) in target_ids,
            sort_mode=0,
        )

        self.assertIn(2000, tuple(int(player.index) for player in result))
        self.assertNotIn(4000, tuple(int(player.index) for player in result))

    def test_mapped_human_scouting_uses_live_out_of_contract_status(self):
        controller = self.build_controller()
        controller.select_club(1)
        panel = ScoutingReseedState(
            age_low_64d8=0,
            age_high_64dc=99,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=1,
        )
        common = dict(
            page_mode=16,
            valuation_resolver=lambda _player: 100.0,
            team_selector_predicate=lambda _player: True,
            optional_position_predicate=lambda _player: True,
            threshold_predicate=lambda _player: True,
        )

        player = controller.state.players[2000]
        player.out_of_contract = True
        result = controller.search_scouting_players_mapped(
            panel,
            status_controls=ScoutingFilterControls(out_of_contract=True),
            **common,
        )
        self.assertIn(2000, tuple(int(value.index) for value in result))

        # The compatibility resolver can still explicitly override live state.
        result = controller.search_scouting_players_mapped(
            panel,
            status_controls=ScoutingFilterControls(out_of_contract=True),
            out_of_contract_resolver=lambda _player: False,
            **common,
        )
        self.assertNotIn(2000, tuple(int(value.index) for value in result))

        player.out_of_contract = False
        player.loan_listed = True
        club2 = controller.state.clubs[2]
        controller.state.clubs[2] = type(club2)(
            index=club2.index,
            manager_id=club2.manager_id,
            country_id=club2.country_id,
            competition_id=1,
        )
        result = controller.search_scouting_players_mapped(
            panel,
            status_controls=ScoutingFilterControls(loan_listed=True),
            **common,
        )
        self.assertIn(2000, tuple(int(value.index) for value in result))

    def test_human_youth_controller_promotes_and_releases_from_separate_list(self):
        controller = self.build_controller()
        controller.select_club(1)

        promoted = controller.state.players[2000]
        promoted.club_id = 1
        promoted.status_bit_3 = True
        released = controller.state.players[3000]
        released.club_id = 1
        released.status_bit_3 = True
        controller.state.user_youth = YouthTeamState(
            [
                YouthRecord(player_id=2000, source_roster_club_id=2),
                YouthRecord(player_id=3000, source_roster_club_id=3),
            ]
        )

        self.assertEqual(
            tuple(player.index for player in controller.youth_players()),
            (2000, 3000),
        )
        self.assertNotIn(2000, controller.state.club_roster_order[1])

        controller.promote_youth_player(
            2000,
            weekly_wage=1500.0,
            contract_months=24,
        )
        self.assertIn(2000, controller.state.club_roster_order[1])
        self.assertNotIn(2000, controller.state.club_roster_order[2])
        self.assertFalse(controller.state.players[2000].status_bit_3)
        self.assertEqual(controller.state.players[2000].weekly_wage, 1500)

        self.assertTrue(controller.release_youth_player(3000))
        self.assertNotIn(3000, controller.state.club_roster_order[3])
        self.assertEqual(controller.state.players[3000].club_id, -1)
        self.assertTrue(controller.state.players[3000].out_of_contract)
        self.assertEqual(
            tuple(player.index for player in controller.youth_players()),
            (),
        )

    def test_human_manager_can_change_training_method_for_own_player_only(self):
        controller = self.build_controller()
        controller.select_club(1)
        player = controller.squad()[0]
        player.training_countdown = 4
        player.training_modifiers[0] = 2

        controller.set_player_training_method(player.index, 1)

        self.assertEqual(player.training_method_id, 1)
        self.assertEqual(player.training_countdown, 4)
        self.assertEqual(player.training_modifiers[0], 2)

        with self.assertRaisesRegex(ValueError, "human-controlled squad"):
            controller.set_player_training_method(2000, 2)
        with self.assertRaisesRegex(ValueError, "0..6"):
            controller.set_player_training_method(player.index, 7)

    def test_club_squad_lineup_and_tactics_persist(self):
        controller = self.build_controller()
        human = controller.select_club(1)
        self.assertEqual(human.club_id, 1)
        self.assertEqual(len(controller.squad()), 20)

        tactics = TeamTacticalState(
            play_style=2,
            without_ball_style=1,
            with_ball_style=3,
            aggression=7,
        )
        controller.set_tactics(tactics)
        self.assertEqual(controller.state.team_tactics[1], tactics)

        self.set_available_lineup(controller)
        roster = controller.squad()
        self.assertEqual(sum(player.match_active for player in roster), 11)
        self.assertEqual(
            sum(player.match_substitute_available for player in roster),
            5,
        )
        self.assertEqual(controller.human.formation_id, 0)

    def test_shared_primary_controller_stops_for_human_cup_and_preserves_order(self):
        controller = self.build_controller()
        controller.select_club(1)
        self.set_available_lineup(controller)
        controller.state.competitions[1] = SimpleNamespace(
            id=1,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=8,
            initialization_order_value=6,
        )
        token = ("cup_result", 1, 43, 4)
        controller.state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=43,
                    pair_index=4,
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
        controller.state.primary_matchday_order = {
            date(2000, 7, 8): (
                ("premier_league", 5),
                ("domestic_cup", token),
                ("premier_league", 6),
            )
        }

        pending = controller.advance_to_next_user_primary_match()

        self.assertEqual(pending, ("domestic_cup", token))
        self.assertIn(5, controller.state.premier_league.results)
        self.assertNotIn(6, controller.state.premier_league.results)
        self.assertNotIn(token, controller.state.cup_results.outcomes)

        outcome = controller.play_user_primary_match()

        self.assertEqual(outcome.match_entry, ("domestic_cup", token))
        self.assertEqual(
            tuple(entry for entry, _result in outcome.matchday_results),
            (
                ("premier_league", 5),
                ("domestic_cup", token),
                ("premier_league", 6),
            ),
        )
        self.assertIn(token, controller.state.cup_results.outcomes)
        self.assertIn(6, controller.state.premier_league.results)
        self.assertIsNone(controller.pending_primary_entry)

    def test_shared_primary_controller_stops_for_human_european_knockout(self):
        controller = self.build_controller()
        controller.select_club(1)
        self.set_available_lineup(controller)
        controller.state.competitions[9] = SimpleNamespace(
            id=9,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=8,
            initialization_order_value=6,
        )
        token = ("cup_result", 9, 200, 4)
        node = StartupScheduleNode(
            node_kind="cup_match",
            competition_id=9,
            competition_context=0,
            round_id=200,
            pair_index=4,
            schedule_index=None,
            scheduled_week=0,
            scheduled_weekday=6,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=token,
            round_number=1,
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=False,
        )
        controller.state.european_cups = DomesticCupScheduleState.from_startup_nodes(
            (node,),
            season_year=2000,
            competition_ids=(9, 10),
        )
        controller.state.primary_matchday_order = {
            date(2000, 7, 8): (
                ("premier_league", 5),
                ("european_cup", token),
                ("premier_league", 6),
            )
        }

        pending = controller.advance_to_next_user_primary_match()

        self.assertEqual(pending, ("european_cup", token))
        self.assertIn(5, controller.state.premier_league.results)
        self.assertNotIn(6, controller.state.premier_league.results)
        self.assertNotIn(token, controller.state.cup_results.outcomes)

        outcome = controller.play_user_primary_match()

        self.assertEqual(outcome.match_entry, ("european_cup", token))
        self.assertEqual(
            tuple(entry for entry, _result in outcome.matchday_results),
            (
                ("premier_league", 5),
                ("european_cup", token),
                ("premier_league", 6),
            ),
        )
        self.assertIn(token, controller.state.cup_results.outcomes)
        self.assertIn(token, controller.state.european_cups.completed_node_tokens)
        self.assertIn(6, controller.state.premier_league.results)
        self.assertIsNone(controller.pending_primary_entry)

    def test_shared_primary_controller_plays_human_procedural_league_entry(self):
        controller = self.build_controller()
        controller.select_club(1)
        self.set_available_lineup(controller)

        competition_id = 14
        token = ("league_match", competition_id, 0, 0, 0)
        controller.state.competitions[competition_id] = Competition(id=competition_id)
        controller.state.procedural_leagues[(competition_id, 0)] = (
            LiveProceduralLeagueState(
                competition_id=competition_id,
                competition_context=0,
                fixtures={
                    token: ProceduralLeagueFixture(
                        node_token=token,
                        home_club_id=1,
                        away_club_id=2,
                    )
                },
                club_ids=(1, 2),
            )
        )
        controller.state.primary_matchday_order = {
            date(2000, 7, 8): (
                ("premier_league", 5),
                ("procedural_league", token),
                ("premier_league", 6),
            )
        }

        pending = controller.advance_to_next_user_primary_match()

        self.assertEqual(pending, ("procedural_league", token))
        self.assertIn(5, controller.state.premier_league.results)
        self.assertNotIn(6, controller.state.premier_league.results)
        live = controller.state.procedural_leagues[(competition_id, 0)]
        self.assertNotIn(token, live.results)

        outcome = controller.play_user_primary_match()

        self.assertEqual(outcome.match_entry, ("procedural_league", token))
        self.assertEqual(
            tuple(entry for entry, _result in outcome.matchday_results),
            (
                ("premier_league", 5),
                ("procedural_league", token),
                ("premier_league", 6),
            ),
        )
        self.assertIn(token, live.results)
        self.assertEqual(
            (
                live.results[token].home_goals,
                live.results[token].away_goals,
            ),
            tuple(int(value) for value in outcome.user_result.score),
        )
        self.assertIn(6, controller.state.premier_league.results)
        self.assertIsNone(controller.pending_primary_entry)

    def test_advance_stops_before_human_fixture_then_shared_backend_finishes_day(self):
        controller = self.build_controller()
        controller.select_club(1)
        self.set_available_lineup(controller)

        fixture = controller.advance_to_next_user_fixture()
        self.assertEqual(fixture.id, 0)
        self.assertEqual(controller.state.calendar.current_date, date(2000, 7, 8))
        self.assertNotIn(0, controller.state.premier_league.results)
        self.assertEqual(controller.pending_fixture_id, 0)
        self.assertEqual(
            tuple(sorted(controller.state.premier_league.results)),
            (5, 6, 7, 8, 9),
        )

        outcome = controller.play_user_fixture()

        self.assertEqual(outcome.fixture_id, 0)
        self.assertEqual(
            [fixture_id for fixture_id, _ in outcome.matchday_results],
            [5, 6, 7, 8, 9, 0, 1, 2, 3, 4],
        )
        self.assertEqual(len(controller.state.premier_league.results), 10)
        self.assertEqual(sum(row.played for row in outcome.table), 20)
        self.assertIsNone(controller.pending_fixture_id)

    def test_distinct_match_engine_rng_retains_live_fastview_histories(self):
        controller = self.build_controller()
        controller.match_engine_rng = MatchEngineRng(0x12345678)
        controller.select_club(1)
        self.set_available_lineup(controller)

        engine_before = controller.match_engine_rng.snapshot_state()
        fixture = controller.advance_to_next_user_fixture()
        self.assertEqual(fixture.id, 0)
        outcome = controller.play_user_fixture()

        self.assertEqual(outcome.user_result.condition_history_sample_count, 18)
        self.assertTrue(outcome.user_result.raw_condition_history_prefixes)
        self.assertTrue(outcome.user_result.fastview_form_histories)
        self.assertTrue(
            all(
                len(history.samples) == 24
                for history in outcome.user_result.fastview_form_histories
            )
        )
        self.assertNotEqual(
            controller.match_engine_rng.snapshot_state(),
            engine_before,
        )

    def test_three_week_human_loop_reuses_same_backend(self):
        controller = self.build_controller()
        controller.select_club(1)

        completed = []
        for expected_fixture_id in (0, 10, 20):
            self.set_available_lineup(controller)
            fixture = controller.advance_to_next_user_fixture()
            self.assertEqual(fixture.id, expected_fixture_id)
            outcome = controller.play_user_fixture()
            completed.append(outcome.fixture_id)

        self.assertEqual(completed, [0, 10, 20])
        self.assertEqual(len(controller.state.premier_league.results), 30)
        self.assertEqual(
            sum(row.played for row in controller.state.premier_league_table()),
            60,
        )
        self.assertTrue(
            all(
                0 <= player.condition <= 100
                for player in controller.squad()
            )
        )

    def test_final_human_matchday_runs_objective_season_transition(self):
        controller = self.build_controller()
        controller.select_club(1)
        objective = FinancialObjectiveState(
            base_cash=1_000_000,
            candidate_ids=(1, 5, 6),
        )
        objective.select(2, date(1999, 8, 1))
        controller.state.finance_balances[1] = BalanceRuntimeState(
            current_cash=objective.starting_funds,
            financial_objective=objective,
        )

        for expected_fixture_id in (0, 10, 20):
            self.set_available_lineup(controller)
            fixture = controller.advance_to_next_user_fixture()
            self.assertEqual(fixture.id, expected_fixture_id)
            controller.play_user_fixture()

        self.assertEqual(
            len(controller.state.premier_league.results),
            len(controller.state.premier_league.fixtures),
        )
        self.assertTrue(objective.progression_gate_reached)
        self.assertEqual(objective.progression_state, 1)

    def test_financial_objective_dismissal_ends_single_user_control(self):
        controller = self.build_controller()
        controller.select_club(1)
        objective = FinancialObjectiveState(
            base_cash=1_000_000,
            candidate_ids=(1, 5, 6),
        )
        # Three-year deadline falls in the synthetic 2000 season. ID 6 reaches
        # its same-PL sporting gate, but current cash remains below 95% target.
        objective.select(2, date(1997, 8, 1))
        balance = BalanceRuntimeState(
            current_cash=objective.starting_funds,
            financial_objective=objective,
        )
        controller.state.finance_balances[1] = balance

        for expected_fixture_id in (0, 10, 20):
            self.set_available_lineup(controller)
            self.assertEqual(
                controller.advance_to_next_user_fixture().id,
                expected_fixture_id,
            )
            controller.play_user_fixture()

        self.assertEqual(controller.state.user_sacking_reason, 5)
        self.assertIsNone(controller.state.user_controlled_club_id)
        self.assertIsNone(controller.human)
        # Original +0x10D8 handling leaves DBRUser/Balance state intact while
        # the single-user outer loop returns to PStartMenu.
        self.assertIs(controller.state.finance_balances[1], balance)
        self.assertEqual(balance.financial_objective.selected_objective_id, 6)

    def test_human_cash_transfer_controller_path_moves_player_safely(self):
        controller = self.build_controller()
        controller.select_club(1)
        state = controller.state

        # Add the source-backed tables required by Gate-9 valuation/contract
        # helpers without changing the existing Gate-7 fixture test database.
        state.clubs = {
            club_id: SimpleNamespace(
                index=club_id,
                name=f"Club {club_id}",
                manager_id=club_id,
                competition_id=0,
                country_id=0,
                team_category_code=0,
                fan_base_index=22,
                related_club_id_0=-1,
                related_club_id_1=-1,
                related_club_id_2=-1,
            )
            for club_id in state.club_roster_order
        }
        state.countries = {
            0: SimpleNamespace(
                id=0,
                financial_multiplier_percent=100,
                eu_status_flag=1,
            )
        }
        state.positions = {
            role: SimpleNamespace(lineup_group=0)
            for role in range(20)
        }
        state.access_skill_financial_values = tuple(
            SimpleNamespace(
                id=i,
                field_08=100_000,
                field_0c=100_000,
                weekly_wage_base=1_000,
                weekly_wage_random_range=100,
                field_18=1_000,
                field_1c=100,
            )
            for i in range(100)
        )

        target_id = 2000
        bid = controller.submit_cash_bid(target_id, 500_000)
        self.assertEqual(bid.decision, SellingClubDecision.ACCEPTED)

        response = controller.offer_player_contract(
            target_id,
            ContractTerms(
                weekly_wage=2_000,
                signing_on_fee=2_000,
                contract_length_months=36,
            ),
        )
        self.assertEqual(response.outcome, OrdinaryMoneyResponse.ACCEPTED)
        self.assertEqual(len(state.transfers.scheduled_transfers), 1)

        scheduled = state.transfers.scheduled_transfers[0]
        self.assertEqual(scheduled.due_date, date(2000, 7, 1))
        controller.set_current_cash(750_000)
        self.assertEqual(
            state.advance_one_day(),
            date(2000, 7, 1),
        )
        # 1 July 2000 is Saturday. The due transfer executes first in the
        # current reconstructed ordering, then the recovered weekly payroll
        # debits the newly registered player's negotiated wage (category 101).
        self.assertEqual(state.current_cash(1), 248_000)
        self.assertEqual(
            [(posting.amount, posting.category) for posting in state.finance_balances[1].ledger],
            [(-500_000, 1000), (-2_000, 101)],
        )

        self.assertEqual(state.players[target_id].club_id, 1)
        self.assertIn(target_id, state.club_roster_order[1])
        self.assertNotIn(target_id, state.club_roster_order[2])
        self.assertEqual(state.players[target_id].weekly_wage, 2_000)
        self.assertEqual(len(state.transfers.movements), 1)

    def test_autofill_produces_persistent_legal_11_plus_5(self):
        controller = self.build_controller()
        controller.select_club(1)

        selection = controller.autofill_lineup(0)

        self.assertEqual(len(selection.lineup.starters), 11)
        self.assertEqual(len(selection.lineup.substitutes), 5)
        self.assertEqual(
            tuple(
                int(assignment.player_index)
                for assignment in selection.lineup.starters
            ),
            controller.human.starter_ids,
        )
        self.assertEqual(
            tuple(int(value) for value in selection.lineup.substitutes),
            controller.human.substitute_ids,
        )

    def test_unavailable_human_player_is_rejected(self):
        controller = self.build_controller()
        controller.select_club(1)
        player = controller.squad()[0]
        player.injured = True
        ids = [entry.index for entry in controller.squad()]

        with self.assertRaisesRegex(ValueError, "unavailable"):
            controller.set_lineup(
                0,
                ids[:11],
                ids[11:16],
            )


if __name__ == "__main__":
    unittest.main()
