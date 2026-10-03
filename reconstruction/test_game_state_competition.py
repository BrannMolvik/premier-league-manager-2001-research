import unittest
from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

from competition_schedule import StartupScheduleNode, direct_club_ref
from domestic_cup_state import DomesticCupScheduleState
import game_state as game_state_module
from game_state import GameState
from match_calculator import PositionRole
from match_lineup import AI_FORMATIONS
from match_events import BoundaryRecord, BoundaryType
from match_preparation import prepare_ai_match_selection
from match_simulation import NormalMatchResult, PreparedMatchPlayer, PreparedMatchSide
from match_strength import TeamStrengthContext
from primary_schedule_shadow import PrimaryScheduleResolutionPending


@dataclass(frozen=True)
class FakePlayer:
    index: int
    first_name: str = "A"
    surname: str = "Player"
    club_id: int = 1
    nationality_id: int = 0
    date_of_birth: date | None = date(1980, 1, 1)
    shirt_number: int = 1
    height_cm: int = 180
    weight_kg: int = 75
    positions: tuple[int, int, int] = (0, 0, 0)
    current_raw: tuple[int, ...] = (100,) * 17
    target_raw: tuple[int, ...] = (150,) * 17


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


class FakeDatabase:
    players = [FakePlayer(1), FakePlayer(2, club_id=2)]
    real_fixtures = [Fixture(0, 0, 1, 2), Fixture(1, 1, 2, 1)]
    premier_league_rounds = [
        Round(1, 0, 6),
        Round(2, 1, 6),
    ]


@dataclass(frozen=True)
class AutoClub:
    index: int
    manager_id: int
    country_id: int = 0


@dataclass(frozen=True)
class AutoManager:
    index: int
    formation_default: int = 0
    formation_class3: int = 2
    formation_class1: int = 1


@dataclass(frozen=True)
class AutoCompetition:
    id: int = 0
    substitute_quota: int = 5
    max_non_eu_players: int = 3


def auto_players_for_club(club_id, start_index):
    roles = [slot.role for slot in AI_FORMATIONS[0]] + [
        PositionRole.CENTRE_MIDFIELD,
        PositionRole.STRIKER,
        PositionRole.CENTRE_BACK,
        PositionRole.GOALKEEPER,
        PositionRole.RIGHT_MIDFIELD,
    ]
    return [
        FakePlayer(
            start_index + offset,
            club_id=club_id,
            positions=(int(role), 0, 0),
            current_raw=(160,) * 17,
            target_raw=(180,) * 17,
        )
        for offset, role in enumerate(roles)
    ]


class AutonomousDatabase:
    players = auto_players_for_club(1, 100) + auto_players_for_club(2, 200)
    real_fixtures = [
        Fixture(0, 0, 1, 2),
        Fixture(1, 0, 3, 4),
        Fixture(2, 0, 5, 6),
        Fixture(3, 0, 7, 8),
        Fixture(4, 0, 9, 10),
        Fixture(5, 0, 11, 12),
        Fixture(6, 0, 13, 14),
        Fixture(7, 0, 15, 16),
        Fixture(8, 0, 17, 18),
        Fixture(9, 0, 19, 20),
    ]
    premier_league_rounds = [Round(1, 0, 6)]
    clubs = [AutoClub(1, 10), AutoClub(2, 20)]
    managers = [AutoManager(10), AutoManager(20)]
    competitions = [AutoCompetition()]
    countries = []

class MidpointRng:
    def __init__(self):
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        return bound // 2


def coefficient_matrix(value=1.0):
    return tuple(
        tuple(
            tuple(float(value) for _ in range(17))
            for _ in range(20)
        )
        for _ in range(4)
    )


def prepared_side(side_id):
    roles = (
        PositionRole.GOALKEEPER,
        PositionRole.RIGHT_BACK,
        PositionRole.LEFT_BACK,
        PositionRole.CENTRE_BACK,
        PositionRole.CENTRE_BACK,
        PositionRole.DEFENSIVE_MIDFIELD,
        PositionRole.RIGHT_MIDFIELD,
        PositionRole.LEFT_MIDFIELD,
        PositionRole.CENTRE_MIDFIELD,
        PositionRole.CENTRE_FORWARD,
        PositionRole.STRIKER,
    )
    players = tuple(
        PreparedMatchPlayer(
            side=side_id,
            player_index=index,
            condition=100,
            form_state=2,
            current_position=role,
            balance_position_code=int(role),
            preferred_positions=(int(role), 0, 0),
            skills=(50,) * 17,
        )
        for index, role in enumerate(roles)
    )
    context = TeamStrengthContext(
        tactic_style=0,
        match_bias=2,
        user_controlled=True,
        aggression=5,
    )
    return PreparedMatchSide(
        players=players,
        attack_context=context,
        defence_context=context,
        penalty_taker_priority=(10,),
        corner_taker_priority=(10,),
        free_kick_taker_priority=(10,),
    )


class DomesticCupGatePolicyAdapterTests(unittest.TestCase):
    def test_adapter_uses_host_league_root_index_and_host_owning_division(self):
        competitions = {
            0: SimpleNamespace(
                id=0,
                runtime_kind_code=1,
                parent_competition_id=None,
                initialization_order_value=9,
                country_region_id=26,
                valuation_division_category=2,
            ),
            90: SimpleNamespace(
                id=90,
                runtime_kind_code=2,
                parent_competition_id=None,
                initialization_order_value=15,
                country_region_id=26,
            ),
            89: SimpleNamespace(
                id=89,
                runtime_kind_code=3,
                parent_competition_id=None,
                initialization_order_value=14,
                country_region_id=26,
            ),
            7: SimpleNamespace(
                id=7,
                runtime_kind_code=2,
                parent_competition_id=None,
                initialization_order_value=13,
                country_region_id=26,
            ),
            4: SimpleNamespace(
                id=4,
                runtime_kind_code=2,
                parent_competition_id=None,
                initialization_order_value=12,
                country_region_id=26,
            ),
            1: SimpleNamespace(
                id=1,
                runtime_kind_code=2,
                parent_competition_id=None,
                initialization_order_value=5,
                country_region_id=26,
                scheduled_matchday_count=8,
            ),
        }
        state = GameState(
            calendar=__import__("game_state").GameCalendar(date(2000, 8, 19)),
            players={},
            clubs={10: SimpleNamespace(competition_id=0, country_id=26)},
            competitions=competitions,
        )

        policy = state.domestic_cup_gate_policy_inputs(
            1,
            round_number=8,
            host_club_id=10,
        )

        # 0x5DA2F0 indexes host club competition 0 in country +0x48, not Cup 1.
        self.assertEqual(policy.tier_factor, 0.9)
        self.assertEqual(policy.round_attendance_modifier, 3.0)
        self.assertEqual(policy.seating_reference, 16.0)
        self.assertEqual(policy.terrace_reference, 12.0)


class DomesticCupPostMatchPreflightTests(unittest.TestCase):
    def test_preflight_returns_both_exact_dates_as_one_atomic_result(self):
        state = GameState(
            calendar=__import__("game_state").GameCalendar(date(2000, 8, 19)),
            players={},
        )
        state.primary_schedule_shadow.days = {date(2000, 8, 20): ()}
        expected = {
            1: date(2000, 8, 23),
            2: date(2000, 8, 26),
        }

        def lookup(club_id, *, after_date):
            self.assertEqual(after_date, date(2000, 8, 19))
            return expected[int(club_id)]

        state.next_primary_match_date_for_club = lookup
        self.assertEqual(
            state._preflight_domestic_cup_post_match_dates(
                1,
                2,
                date(2000, 8, 19),
            ),
            (True, date(2000, 8, 23), date(2000, 8, 26)),
        )

    def test_preflight_collapses_either_pending_side_without_partial_result(self):
        state = GameState(
            calendar=__import__("game_state").GameCalendar(date(2000, 8, 19)),
            players={},
        )
        state.primary_schedule_shadow.days = {date(2000, 8, 20): ()}

        def lookup(club_id, *, after_date):
            if int(club_id) == 1:
                return date(2000, 8, 23)
            raise PrimaryScheduleResolutionPending(2, date(2000, 8, 21))

        state.next_primary_match_date_for_club = lookup
        self.assertEqual(
            state._preflight_domestic_cup_post_match_dates(
                1,
                2,
                date(2000, 8, 19),
            ),
            (False, None, None),
        )

    def test_shared_cup_postmatch_orders_incidents_before_morale_when_exact(self):
        state = GameState(
            calendar=__import__("game_state").GameCalendar(date(2000, 8, 19)),
            players={},
        )
        state.primary_schedule_shadow.days = {date(2000, 8, 20): ()}
        state.next_primary_match_date_for_club = lambda club_id, *, after_date: (
            date(2000, 8, 23) if int(club_id) == 1 else date(2000, 8, 26)
        )
        state.pitch_wear[1] = 0

        home_side = prepared_side(0)
        away_side = prepared_side(1)
        home_participants = [
            SimpleNamespace(index=i, condition=0) for i in range(11)
        ]
        away_participants = [
            SimpleNamespace(index=100 + i, condition=0) for i in range(11)
        ]
        calls = []
        original_incidents = game_state_module.persist_premier_league_match_incidents
        original_morale = game_state_module.persist_premier_league_morale_and_form

        def record_incidents(roster, participants, side, result, fixture_date,
                             next_fixture_date, rng, **kwargs):
            calls.append(("incidents", int(side), next_fixture_date))
            return None

        def record_morale(roster, side, participants, result, fixture_date, rng,
                          **kwargs):
            calls.append(("morale", int(side.side)))
            return frozenset()

        game_state_module.persist_premier_league_match_incidents = record_incidents
        game_state_module.persist_premier_league_morale_and_form = record_morale
        try:
            exact = state._persist_domestic_cup_shared_post_match(
                home_club_id=1,
                away_club_id=2,
                home_side=home_side,
                away_side=away_side,
                home_participants=home_participants,
                away_participants=away_participants,
                result=NormalMatchResult(events=()),
                environment=SimpleNamespace(weather_code=0),
                pitch_wear_before=0,
                rng=MidpointRng(),
            )
        finally:
            game_state_module.persist_premier_league_match_incidents = original_incidents
            game_state_module.persist_premier_league_morale_and_form = original_morale

        self.assertTrue(exact)
        self.assertEqual(
            calls,
            [
                ("incidents", 0, date(2000, 8, 23)),
                ("incidents", 1, date(2000, 8, 26)),
                ("morale", 0),
                ("morale", 1),
            ],
        )
        self.assertTrue(all(player.condition == 100 for player in home_participants))
        self.assertTrue(all(player.condition == 100 for player in away_participants))

    def test_shared_cup_postmatch_consumes_no_incident_or_morale_rng_when_pending(self):
        state = GameState(
            calendar=__import__("game_state").GameCalendar(date(2000, 8, 19)),
            players={},
        )
        state.primary_schedule_shadow.days = {date(2000, 8, 20): ()}

        def lookup(club_id, *, after_date):
            if int(club_id) == 1:
                return date(2000, 8, 23)
            raise PrimaryScheduleResolutionPending(2, date(2000, 8, 21))

        state.next_primary_match_date_for_club = lookup
        state.pitch_wear[1] = 0
        calls = []
        original_incidents = game_state_module.persist_premier_league_match_incidents
        original_morale = game_state_module.persist_premier_league_morale_and_form

        def unexpected(*args, **kwargs):
            calls.append("unexpected")
            raise AssertionError("pending preflight must not enter RNG-consuming persistence")

        game_state_module.persist_premier_league_match_incidents = unexpected
        game_state_module.persist_premier_league_morale_and_form = unexpected
        try:
            exact = state._persist_domestic_cup_shared_post_match(
                home_club_id=1,
                away_club_id=2,
                home_side=prepared_side(0),
                away_side=prepared_side(1),
                home_participants=[
                    SimpleNamespace(index=i, condition=0) for i in range(11)
                ],
                away_participants=[
                    SimpleNamespace(index=100 + i, condition=0) for i in range(11)
                ],
                result=NormalMatchResult(events=()),
                environment=SimpleNamespace(weather_code=0),
                pitch_wear_before=0,
                rng=MidpointRng(),
            )
        finally:
            game_state_module.persist_premier_league_match_incidents = original_incidents
            game_state_module.persist_premier_league_morale_and_form = original_morale

        self.assertFalse(exact)
        self.assertEqual(calls, [])


class IntegratedGameStateTests(unittest.TestCase):
    def test_database_load_creates_player_and_league_state(self):
        state = GameState.from_database(FakeDatabase(), date(2000, 7, 1), seed=1)
        self.assertEqual(set(state.players), {1, 2})
        self.assertIsNotNone(state.premier_league)
        self.assertEqual(state.premier_league.next_unplayed_round(), 0)

    def test_result_updates_table_inside_game_state(self):
        state = GameState.from_database(FakeDatabase(), date(2000, 7, 1), seed=1)
        state.record_premier_league_result(0, 2, 1)
        table = state.premier_league_table()
        self.assertEqual(table[0].club_id, 1)
        self.assertEqual(table[0].points, 3)
        self.assertEqual(state.premier_league.next_unplayed_round(), 1)

    def test_database_initial_roster_order_matches_player_iteration_order(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 1),
            seed=1,
            season_year=2000,
        )
        self.assertEqual(
            [player.index for player in state.ordered_club_roster(1)],
            list(range(100, 116)),
        )
        self.assertEqual(
            [player.index for player in state.ordered_club_roster(2)],
            list(range(200, 216)),
        )

    def test_due_ai_fixture_prepares_both_sides_without_lineup_inputs(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 1),
            seed=1,
            season_year=2000,
        )
        home, away = state.prepare_premier_league_ai_fixture_sides(
            0,
            MidpointRng(),
        )

        self.assertEqual(home.preparation.formation_id, 0)
        self.assertEqual(away.preparation.formation_id, 0)
        self.assertEqual(home.preparation.substitute_quota, 5)
        self.assertEqual(away.preparation.substitute_quota, 5)
        self.assertEqual(len(home.match_side.starting_player_indices), 11)
        self.assertEqual(len(away.match_side.starting_player_indices), 11)
        self.assertEqual(len(home.match_side.players), 16)
        self.assertEqual(len(away.match_side.players), 16)
        self.assertEqual(home.match_side.attack_context.tactic_style, 0)
        self.assertEqual(away.match_side.attack_context.tactic_style, 0)
        self.assertFalse(home.match_side.attack_context.user_controlled)
        self.assertFalse(away.match_side.attack_context.user_controlled)
        environment = state.prepared_match_environments[0]
        self.assertEqual(environment.temperature_c, 30)
        self.assertEqual(environment.weather_code, 1)
        self.assertFalse(environment.weekday_evening)
        self.assertTrue(
            all(player.condition == 95 for player in state.ordered_club_roster(1))
        )
        self.assertTrue(
            all(player.condition == 95 for player in state.ordered_club_roster(2))
        )

    def test_decisive_domestic_cup_ai_node_uses_shared_extra_time_backend(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        state.competitions[1] = SimpleNamespace(
            id=1,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=8,
            initialization_order_value=6,
        )
        token = ("cup_result", 1, 43, 0)
        state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=43,
                    pair_index=0,
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

        rng = MidpointRng()
        completion_gate_suffix = []
        complete_scheduled_match = state.domestic_cups.complete_scheduled_match

        def traced_complete_scheduled_match(*args, **kwargs):
            completion_gate_suffix[:] = rng.calls[-4:]
            return complete_scheduled_match(*args, **kwargs)

        state.domestic_cups.complete_scheduled_match = traced_complete_scheduled_match
        result, completion = state.simulate_domestic_cup_ai_node(
            token,
            coefficient_matrix(),
            coefficient_matrix(),
            rng,
        )

        self.assertEqual(completion_gate_suffix, [32768, 32768, 32768, 32768])
        boundaries = [
            (timed.minute, timed.event.kind)
            for timed in result.events
            if isinstance(timed.event, BoundaryRecord)
        ]
        self.assertEqual(
            boundaries,
            [
                (45, BoundaryType.HALF_TIME),
                (90, BoundaryType.EXTRA_TIME),
                (105, BoundaryType.EXTRA_TIME),
                (120, BoundaryType.FULL_TIME),
            ],
        )
        self.assertIsNotNone(completion.outcome)
        self.assertIn(token, state.domestic_cups.completed_node_tokens)
        self.assertIn(token, state.cup_results.outcomes)

    def test_shared_primary_ai_day_interleaves_cup_before_league(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 7),
            seed=1,
            season_year=2000,
        )
        state.competitions[1] = SimpleNamespace(
            id=1,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=8,
            initialization_order_value=6,
        )
        token = ("cup_result", 1, 43, 2)
        state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=43,
                    pair_index=2,
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
                ("domestic_cup", token),
                ("premier_league", 0),
            )
        }

        results = state.advance_one_day_with_primary_ai_matches(
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        self.assertEqual(
            tuple(entry for entry, _result in results),
            (
                ("domestic_cup", token),
                ("premier_league", 0),
            ),
        )
        self.assertIn(token, state.cup_results.outcomes)
        self.assertIn(0, state.premier_league.results)

    def test_primary_ai_entry_executes_european_knockout_and_records_result(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        state.competitions[9] = SimpleNamespace(
            id=9,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=8,
            initialization_order_value=6,
        )
        token = ("cup_result", 9, 200, 0)
        node = StartupScheduleNode(
            node_kind="cup_match",
            competition_id=9,
            competition_context=0,
            round_id=200,
            pair_index=0,
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
        state.european_cups = DomesticCupScheduleState.from_startup_nodes(
            (node,),
            season_year=2000,
            competition_ids=(9, 10),
        )
        state.primary_matchday_order = {
            date(2000, 7, 8): (("european_cup", token),)
        }

        self.assertEqual(
            state.primary_entries_due_today(),
            (("european_cup", token),),
        )
        result = state.simulate_primary_ai_entry(
            ("european_cup", token),
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        self.assertIn(token, state.european_cups.completed_node_tokens)
        self.assertIn(token, state.cup_results.outcomes)
        outcome = state.cup_results.outcomes[token]
        self.assertEqual(
            (outcome.participant_0_club_id, outcome.participant_1_club_id),
            (1, 2),
        )
        self.assertIn(outcome.winner_club_id, (1, 2))
        match = state.european_cups.match_state(token)
        self.assertEqual(
            tuple(result.score),
            (int(match.base_score_0), int(match.base_score_1)),
        )

    def test_generic_primary_procedural_league_bridge_executes_selected_competition(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        state.competitions[2] = SimpleNamespace(
            id=2,
            substitute_quota=5,
            max_non_eu_players=3,
        )
        token = ("league_match", 2, 0, 0)
        node = StartupScheduleNode(
            node_kind="league_match",
            competition_id=2,
            competition_context=0,
            round_id=None,
            pair_index=0,
            schedule_index=0,
            scheduled_week=1,
            scheduled_weekday=6,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=token,
        )
        buckets = ((node,),)
        state.install_primary_schedule_shadow(buckets, season_year=2000)
        state.install_primary_matchday_order(
            buckets,
            season_year=2000,
            procedural_league_ids=(2,),
        )
        state.refresh_primary_procedural_leagues((2,))
        state.calendar.current_date = next(iter(state.primary_matchday_order))

        self.assertEqual(
            state.primary_entries_due_today(),
            (("procedural_league", token),),
        )
        result = state.simulate_primary_ai_entry(
            ("procedural_league", token),
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        live = state.procedural_leagues[(2, 0)]
        stored = live.results[token]
        self.assertEqual((stored.home_goals, stored.away_goals), result.score)
        self.assertEqual(sum(row.played for row in live.table()), 2)
        self.assertEqual(state.procedural_league_nodes_due_today(), ())

    def test_primary_ai_entry_executes_procedural_league_and_records_result(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        state.competitions[14] = SimpleNamespace(
            id=14,
            substitute_quota=5,
            max_non_eu_players=3,
        )
        token = ("league_match", 14, 0, 0)
        node = StartupScheduleNode(
            node_kind="league_match",
            competition_id=14,
            competition_context=0,
            round_id=None,
            pair_index=0,
            schedule_index=0,
            scheduled_week=0,
            scheduled_weekday=6,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=token,
        )
        state.install_primary_schedule_shadow(((node,),), season_year=2000)
        state.primary_matchday_order = {
            date(2000, 7, 8): (("procedural_league", token),)
        }
        state.refresh_european_procedural_leagues()

        result = state.simulate_primary_ai_entry(
            ("procedural_league", token),
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        live = state.procedural_leagues[(14, 0)]
        stored = live.results[token]
        self.assertEqual((stored.home_goals, stored.away_goals), result.score)
        self.assertEqual(sum(row.played for row in live.table()), 2)
        self.assertEqual(state.procedural_league_nodes_due_today(), ())

    def test_decisive_domestic_cup_human_node_uses_shared_backend(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        state.competitions[1] = SimpleNamespace(
            id=1,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=8,
            initialization_order_value=6,
        )
        token = ("cup_result", 1, 43, 1)
        state.install_domestic_cup_schedule_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=1,
                    competition_context=0,
                    round_id=43,
                    pair_index=1,
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
        human_selection = prepare_ai_match_selection(
            1,
            state.ordered_club_roster(1),
            formation_id=0,
            substitute_quota=5,
            non_eu_limit=10,
        )

        rng = MidpointRng()
        completion_gate_suffix = []
        complete_scheduled_match = state.domestic_cups.complete_scheduled_match

        def traced_complete_scheduled_match(*args, **kwargs):
            completion_gate_suffix[:] = rng.calls[-4:]
            return complete_scheduled_match(*args, **kwargs)

        state.domestic_cups.complete_scheduled_match = traced_complete_scheduled_match
        result, completion = state.simulate_domestic_cup_human_node(
            token,
            1,
            human_selection,
            coefficient_matrix(),
            coefficient_matrix(),
            rng,
        )

        self.assertEqual(completion_gate_suffix, [32768, 32768, 32768, 32768])
        boundaries = [
            (timed.minute, timed.event.kind)
            for timed in result.events
            if isinstance(timed.event, BoundaryRecord)
        ]
        self.assertEqual(boundaries[-1], (120, BoundaryType.FULL_TIME))
        self.assertIsNotNone(completion.outcome)
        self.assertIn(token, state.domestic_cups.completed_node_tokens)
        self.assertIn(token, state.cup_results.outcomes)

    def test_due_ai_fixture_can_prepare_simulate_and_store_result(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        rng = MidpointRng()
        morale_before = {
            player.index: player.morale
            for club_id in (1, 2)
            for player in state.ordered_club_roster(club_id)
        }
        result = state.simulate_premier_league_ai_fixture(
            0,
            coefficient_matrix(),
            coefficient_matrix(),
            rng,
        )

        self.assertIn(0, state.premier_league.results)
        stored = state.premier_league.results[0]
        self.assertEqual((stored.home_goals, stored.away_goals), result.score)
        self.assertEqual(sum(row.played for row in state.premier_league_table()), 2)
        # The July fixture is a hot/non-rain weather state, so the home pitch receives
        # the exact normal PitchWear increment of 16.
        self.assertEqual(state.pitch_wear[1], 16)
        self.assertEqual(state.pitch_wear[2], 0)
        # Detailed post-match persistence mirrors 0x404CE0 roster order.
        # Midpoint RNG makes neutral Form fail on RNG(100)=50 and makes every
        # eligible non-appeared player skip the not-played penalty on RNG(10)=5.
        # A non-draw adds one RNG(2) morale draw before each appeared Form draw.
        home_goals, away_goals = result.score
        result_has_winner = home_goals != away_goals
        expected_tail = []
        for _side in (0, 1):
            for _ in range(11):
                if result_has_winner:
                    expected_tail.append(2)
                expected_tail.append(100)
            expected_tail.extend([10] * 5)
        self.assertEqual(rng.calls[-len(expected_tail):], expected_tail)
        self.assertTrue(
            all(player.form_state == 2 for player in state.ordered_club_roster(1))
        )
        self.assertTrue(
            all(player.form_state == 2 for player in state.ordered_club_roster(2))
        )

        for club_id, own_goals, opponent_goals in (
            (1, home_goals, away_goals),
            (2, away_goals, home_goals),
        ):
            roster = state.ordered_club_roster(club_id)
            for player in roster[:11]:
                before = morale_before[player.index]
                if own_goals > opponent_goals:
                    self.assertEqual(player.morale, min(100, before + 15))
                elif own_goals < opponent_goals:
                    self.assertEqual(player.morale, max(0, before - 4))
                else:
                    self.assertEqual(player.morale, before)
            for player in roster[11:]:
                self.assertEqual(player.morale, morale_before[player.index])
    def test_explicit_match_engine_rng_populates_live_performance_history(self):
        legacy = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        legacy.simulate_premier_league_ai_fixture(
            0,
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )
        self.assertEqual(legacy.prepared_match_participant_statistics, {})
        self.assertEqual(
            sum(
                player.match_performance_history_count
                for club_id in (1, 2)
                for player in legacy.ordered_club_roster(club_id)
            ),
            0,
        )

        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        shared = MidpointRng()
        engine = MidpointRng()
        state.simulate_premier_league_ai_fixture(
            0,
            coefficient_matrix(),
            coefficient_matrix(),
            shared,
            match_engine_rng=engine,
        )
        populated = [
            player
            for club_id in (1, 2)
            for player in state.ordered_club_roster(club_id)
            if player.match_performance_history_count
        ]
        self.assertGreaterEqual(len(populated), 22)
        self.assertTrue(
            all(player.match_performance_history_count == 1 for player in populated)
        )
        self.assertTrue(
            all(4 <= player.latest_match_performance() <= 10 for player in populated)
        )
        statistics = state.prepared_match_participant_statistics[0]
        self.assertEqual(len(statistics), 2)
        for side in statistics:
            self.assertEqual(tuple(item.player_index for item in side.statistics), tuple(range(16)))
            self.assertEqual(sum(item.rating != 0 for item in side.statistics), 11)
            self.assertTrue(all(len(item.skill_flags) == 8 for item in side.statistics))
            self.assertEqual(len(set(side.player_ids)), 16)
            for identity, item in zip(side.player_ids, side.statistics):
                if item.rating:
                    self.assertEqual(state.players[identity].latest_match_performance(), item.rating)
        # Genuine simulation did not promote a statistics fragment into a
        # persistent capture owner or expose PMatchInfo context.
        self.assertFalse(hasattr(state, 'captured_match_reports'))
        self.assertFalse(hasattr(state, 'fixture_match_info_links'))

    def test_daily_injury_return_clears_exact_persistent_state(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 1),
            seed=1,
            season_year=2000,
        )
        player = state.players[100]
        player.injured = True
        player.injury_return_date = date(2000, 7, 2)
        player.injury_source_mode = 0
        player.injury_severity_code = 2
        player.condition = 37

        state.advance_one_day()

        self.assertFalse(player.injured)
        self.assertIsNone(player.injury_return_date)
        self.assertIsNone(player.injury_source_mode)
        self.assertIsNone(player.injury_severity_code)
        self.assertEqual(player.condition, 37)

    def test_injury_return_reenables_player_for_ai_selection(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 1),
            seed=1,
            season_year=2000,
        )
        player = state.players[100]
        player.injured = True
        player.injury_return_date = date(2000, 7, 2)
        player.injury_source_mode = 0
        player.injury_severity_code = 1

        home, _ = state.prepare_premier_league_ai_fixture_sides(
            0,
            MidpointRng(),
        )
        selected_before = {
            assignment.player_index
            for assignment in home.preparation.selection.lineup.starters
        } | set(home.preparation.selection.lineup.substitutes)
        self.assertNotIn(100, selected_before)

        state.advance_one_day()
        self.assertFalse(player.injured)

        home, _ = state.prepare_premier_league_ai_fixture_sides(
            0,
            MidpointRng(),
        )
        selected_after = {
            assignment.player_index
            for assignment in home.preparation.selection.lineup.starters
        } | set(home.preparation.selection.lineup.substitutes)
        self.assertIn(100, selected_after)

    def test_daily_ai_pitch_recovery_uses_exact_base_value(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 1),
            seed=1,
            season_year=2000,
        )
        state.pitch_wear[1] = 16
        state.pitch_wear[2] = 1

        state.advance_one_day()

        self.assertEqual(state.pitch_wear[1], 14)
        self.assertEqual(state.pitch_wear[2], 0)

    def test_due_fixture_can_be_simulated_and_written_to_table(self):
        state = GameState.from_database(
            FakeDatabase(),
            date(2000, 7, 8),
            seed=1,
            season_year=2000,
        )
        self.assertEqual([fixture.id for fixture in state.fixtures_due_today()], [0])

        result = state.simulate_premier_league_fixture(
            0,
            prepared_side(0),
            prepared_side(1),
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        self.assertEqual(result.score, (0, 0))
        self.assertEqual(state.premier_league.results[0].home_goals, 0)
        self.assertEqual(state.premier_league.results[0].away_goals, 0)
        table = state.premier_league_table()
        self.assertEqual({row.club_id: row.points for row in table}, {1: 1, 2: 1})




@dataclass(frozen=True)
class LeagueAllocation:
    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int


class EnglishSeasonTransitionIntegrationTests(unittest.TestCase):
    def test_exact_rankings_and_playoff_winners_drive_live_membership_swaps(self):
        state = GameState.from_players((), date(2001, 6, 1))
        state.league_allocation_records = (
            LeagueAllocation(0, 0, 18, 19, 2, 0, 1),
            LeagueAllocation(1, 0, 17, 17, 11, 0, 0),
            LeagueAllocation(2, 2, 22, 23, 3, 0, 1),
            LeagueAllocation(3, 2, 21, 21, 12, 0, 0),
            LeagueAllocation(4, 3, 21, 23, 4, 0, 2),
            LeagueAllocation(5, 3, 20, 20, 13, 0, 0),
            LeagueAllocation(6, 4, 23, 23, 7, 0, 0),
            LeagueAllocation(25, 7, 19, 21, 89, 0, 2),
        )
        rankings = {
            0: tuple(range(100, 120)),
            2: tuple(range(200, 224)),
            3: tuple(range(300, 324)),
            4: tuple(range(400, 424)),
            7: tuple(range(700, 722)),
            89: tuple(range(890, 905)),
        }
        for competition_id, ranking in rankings.items():
            state.cup_results.replace_competition_ranking(
                competition_id,
                ranking,
            )

        playoff_winners = {11: 205, 12: 305, 13: 405}
        final_nodes = []
        for competition_id, winner in playoff_winners.items():
            token = ("cup_result", competition_id, 1000 + competition_id, 0)
            final_nodes.append(
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=competition_id,
                    competition_context=0,
                    round_id=1000 + competition_id,
                    pair_index=0,
                    schedule_index=None,
                    scheduled_week=47,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(winner),
                    participant_1_ref=direct_club_ref(winner + 1000),
                    node_token=token,
                    round_number=2,
                )
            )
            state.cup_results.record_knockout_outcome(
                token,
                winner,
                winner + 1000,
                winner,
            )
        state.domestic_cups = DomesticCupScheduleState.from_startup_nodes(
            final_nodes,
            season_year=2000,
        )

        memberships = {}
        for competition_id, ranking in rankings.items():
            for club_id in ranking:
                memberships[club_id] = competition_id
        state.club_competition_membership = memberships

        result = state.apply_english_season_transition()

        self.assertEqual(len(result.exchanges), 14)
        self.assertEqual(state.club_competition_membership[117], 2)
        self.assertEqual(state.club_competition_membership[205], 0)
        self.assertEqual(state.club_competition_membership[423], 7)
        self.assertEqual(state.club_competition_membership[700], 4)
        self.assertEqual(state.club_competition_membership[719], 89)
        self.assertEqual(state.club_competition_membership[890], 7)


if __name__ == '__main__':
    unittest.main()
