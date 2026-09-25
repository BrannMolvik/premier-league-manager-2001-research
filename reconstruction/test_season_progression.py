import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState
from match_calculator import PositionRole
from match_lineup import AI_FORMATIONS


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    positions: tuple[int, int, int]
    first_name: str = "A"
    surname: str = "Player"
    nationality_id: int = 0
    date_of_birth: date | None = date(1980, 1, 1)
    shirt_number: int = 1
    height_cm: int = 180
    weight_kg: int = 75
    current_raw: tuple[int, ...] = (160,) * 17
    target_raw: tuple[int, ...] = (180,) * 17


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


@dataclass(frozen=True)
class Club:
    index: int
    manager_id: int
    country_id: int = 0


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
    max_non_eu_players: int = 3


def players_for_club(club_id: int, start_index: int):
    roles = [slot.role for slot in AI_FORMATIONS[0]] + [
        PositionRole.CENTRE_MIDFIELD,
        PositionRole.STRIKER,
        PositionRole.CENTRE_BACK,
        PositionRole.GOALKEEPER,
        PositionRole.RIGHT_MIDFIELD,
    ]
    return [
        Player(
            start_index + offset,
            club_id,
            (int(role), 0, 0),
        )
        for offset, role in enumerate(roles)
    ]


class TwoRoundDatabase:
    players = players_for_club(1, 100) + players_for_club(2, 200)
    real_fixtures = [
        Fixture(0, 0, 1, 2),
        Fixture(1, 1, 2, 1),
    ]
    # 2000-01: round week/day 7/6 = Aug 19; 8/3 = Aug 23.
    premier_league_rounds = [
        Round(1, 7, 6),
        Round(2, 8, 3),
    ]
    clubs = [Club(1, 10), Club(2, 20)]
    managers = [Manager(10), Manager(20)]
    competitions = [Competition()]
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


class SeasonProgressionTests(unittest.TestCase):
    def test_fast_day_step_runs_fixture_before_return_and_daily_maintenance(self):
        state = GameState.from_database(
            TwoRoundDatabase(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        returning = state.players[100]
        returning.injured = True
        returning.injury_return_date = date(2000, 8, 19)
        returning.injury_source_mode = 0
        returning.injury_severity_code = 1

        results = state.advance_one_day_with_premier_league_ai_fixtures(
            coefficient_matrix(),
            coefficient_matrix(),
            MidpointRng(),
        )

        self.assertEqual(state.calendar.current_date, date(2000, 8, 19))
        self.assertEqual([fixture_id for fixture_id, _ in results], [0])
        self.assertIn(0, state.premier_league.results)

        # MPMInjuryReverse runs after the dated-match scheduler. The player is
        # therefore absent from the Aug 19 selection, then cleared afterward.
        self.assertFalse(returning.injured)
        self.assertIsNone(returning.injury_return_date)
        self.assertFalse(returning.match_active)
        self.assertFalse(returning.match_substitute_available)

        # The home pitch takes +16 normal wear, then the same day's exact
        # autonomous PitchRecover=2 maintenance runs.
        self.assertEqual(state.pitch_wear[1], 14)
        self.assertEqual(state.pitch_wear[2], 0)

    def test_repeated_fast_day_steps_reach_and_persist_next_fixture(self):
        state = GameState.from_database(
            TwoRoundDatabase(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        rng = MidpointRng()
        attack = coefficient_matrix()
        defence = coefficient_matrix()

        first = state.advance_one_day_with_premier_league_ai_fixtures(
            attack,
            defence,
            rng,
        )
        self.assertEqual([fixture_id for fixture_id, _ in first], [0])

        for expected_date in (
            date(2000, 8, 20),
            date(2000, 8, 21),
            date(2000, 8, 22),
        ):
            self.assertEqual(
                state.advance_one_day_with_premier_league_ai_fixtures(
                    attack,
                    defence,
                    rng,
                ),
                (),
            )
            self.assertEqual(state.calendar.current_date, expected_date)

        second = state.advance_one_day_with_premier_league_ai_fixtures(
            attack,
            defence,
            rng,
        )
        self.assertEqual(state.calendar.current_date, date(2000, 8, 23))
        self.assertEqual([fixture_id for fixture_id, _ in second], [1])
        self.assertEqual(set(state.premier_league.results), {0, 1})
        self.assertEqual(sum(row.played for row in state.premier_league_table()), 4)
        self.assertIsNone(state.next_match_date())

        # Club 1: Aug 19 +16-2, then four further daily recoveries.
        # Club 2: Aug 23 home wear +16 followed by that day's -2 recovery.
        self.assertEqual(state.pitch_wear[1], 6)
        self.assertEqual(state.pitch_wear[2], 14)

    def test_explicit_same_day_order_must_cover_due_set_exactly_once(self):
        state = GameState.from_database(
            TwoRoundDatabase(),
            date(2000, 8, 19),
            seed=1,
            season_year=2000,
        )
        with self.assertRaises(ValueError):
            state.simulate_due_premier_league_ai_fixtures(
                coefficient_matrix(),
                coefficient_matrix(),
                MidpointRng(),
                fixture_order=(),
            )
        with self.assertRaises(ValueError):
            state.simulate_due_premier_league_ai_fixtures(
                coefficient_matrix(),
                coefficient_matrix(),
                MidpointRng(),
                fixture_order=(0, 0),
            )


if __name__ == "__main__":
    unittest.main()
