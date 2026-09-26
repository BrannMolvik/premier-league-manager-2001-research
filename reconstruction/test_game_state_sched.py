import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState
from match_schedule import MsvcCrtRng


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    first_name: str = "A"
    surname: str = "P"
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


class Database:
    players = [Player(1, 1), Player(2, 2)]
    real_fixtures = [Fixture(0, 0, 1, 2), Fixture(1, 1, 2, 1)]
    premier_league_rounds = [Round(1, 7, 6), Round(2, 8, 3)]


class SameDayDatabase:
    players = [Player(1, 1), Player(2, 2)]
    real_fixtures = [
        Fixture(0, 0, 1, 2),
        Fixture(1, 0, 3, 4),
    ]
    premier_league_rounds = [Round(1, 7, 6)]


class GameScheduleIntegrationTests(unittest.TestCase):
    def test_database_startup_preserves_two_phase_original_rng_order(self):
        state = GameState.from_database(
            Database(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )

        self.assertIsInstance(state.rng, MsvcCrtRng)
        self.assertEqual(state.players[1].morale, 100)
        self.assertEqual(state.players[2].morale, 92)
        self.assertEqual(
            (
                state.players[1].development.peak_ages.physical,
                state.players[1].development.peak_ages.skill,
                state.players[1].development.peak_ages.late,
                state.players[1].startup_month_span,
            ),
            (25, 28, 31, 36),
        )
        self.assertEqual(
            (
                state.players[2].development.peak_ages.physical,
                state.players[2].development.peak_ages.skill,
                state.players[2].development.peak_ages.late,
                state.players[2].startup_month_span,
            ),
            (25, 28, 31, 48),
        )
        self.assertEqual(state.rng.state, 0xDF90722B)

    def test_database_state_resolves_its_shared_rng_by_default(self):
        state = GameState.from_database(
            Database(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        self.assertIs(state._resolve_rng(), state.rng)

    def test_player_only_state_requires_explicit_rng(self):
        state = GameState.from_players([], date(2000, 8, 18))
        with self.assertRaises(RuntimeError):
            state._resolve_rng()

    def test_next_match_date_and_due_fixtures_follow_calendar(self):
        state = GameState.from_database(Database(), date(2000, 8, 18), seed=1, season_year=2000)
        self.assertEqual(state.next_match_date(), date(2000, 8, 19))
        self.assertEqual(state.fixtures_due_today(), ())
        state.advance_one_day()
        self.assertEqual([f.id for f in state.fixtures_due_today()], [0])
        state.record_premier_league_result(0, 2, 1)
        self.assertEqual(state.fixtures_due_today(), ())
        self.assertEqual(state.next_match_date(), date(2000, 8, 23))


    def test_installed_scheduler_order_becomes_default_due_order(self):
        state = GameState.from_database(
            SameDayDatabase(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(
            ((0, (1, 0)),)
        )
        state.advance_one_day()
        self.assertEqual(
            state.due_premier_league_fixture_ids_in_scheduler_order(),
            (1, 0),
        )

    def test_scheduler_order_requires_exact_round_fixture_set(self):
        state = GameState.from_database(
            SameDayDatabase(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        with self.assertRaises(ValueError):
            state.install_premier_league_scheduler_order(
                ((0, (1,)),)
            )

    def test_missing_installed_round_keeps_stable_fixture_id_fallback(self):
        state = GameState.from_database(
            SameDayDatabase(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        state.advance_one_day()
        self.assertEqual(
            state.due_premier_league_fixture_ids_in_scheduler_order(),
            (0, 1),
        )


if __name__ == "__main__":
    unittest.main()
