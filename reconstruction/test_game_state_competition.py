import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState
from match_calculator import PositionRole
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
        penalty_taker_index=10,
        corner_taker_index=10,
        free_kick_taker_index=10,
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
