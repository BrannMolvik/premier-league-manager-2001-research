import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState
from match_calculator import PositionRole
from match_lineup import AI_FORMATIONS
from match_simulation import PreparedMatchPlayer, PreparedMatchSide
from match_strength import TeamStrengthContext


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
    def randbelow(self, bound):
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
        home, away = state.prepare_premier_league_ai_fixture_sides(0)

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

    def test_due_ai_fixture_can_prepare_simulate_and_store_result(self):
        state = GameState.from_database(
            AutonomousDatabase(),
            date(2000, 7, 1),
            seed=1,
            season_year=2000,
        )
        result = state.simulate_premier_league_ai_fixture(
            0,
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        self.assertIn(0, state.premier_league.results)
        stored = state.premier_league.results[0]
        self.assertEqual((stored.home_goals, stored.away_goals), result.score)
        self.assertEqual(sum(row.played for row in state.premier_league_table()), 2)
    def test_due_fixture_can_be_simulated_and_written_to_table(self):
        state = GameState.from_database(
            FakeDatabase(),
            date(2000, 7, 1),
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


if __name__ == '__main__':
    unittest.main()
