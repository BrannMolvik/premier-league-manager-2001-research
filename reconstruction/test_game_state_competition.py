import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState


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


class FakeDatabase:
    players = [FakePlayer(1), FakePlayer(2, club_id=2)]
    real_fixtures = [Fixture(0, 0, 1, 2), Fixture(1, 1, 2, 1)]


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


if __name__ == '__main__':
    unittest.main()
