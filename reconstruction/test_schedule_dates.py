import unittest
from dataclasses import dataclass
from datetime import date

from competition_state import PremierLeagueState, season_weekday_date


@dataclass(frozen=True)
class Round:
    round_number: int
    scheduled_week: int
    scheduled_weekday: int


@dataclass(frozen=True)
class Fixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


class ScheduleDateTests(unittest.TestCase):
    def test_known_2000_01_round_dates(self):
        self.assertEqual(season_weekday_date(2000, 7, 6), date(2000, 8, 19))
        self.assertEqual(season_weekday_date(2000, 8, 3), date(2000, 8, 23))
        self.assertEqual(season_weekday_date(2000, 26, 2), date(2000, 12, 26))
        self.assertEqual(season_weekday_date(2000, 27, 1), date(2001, 1, 1))
        self.assertEqual(season_weekday_date(2000, 46, 7), date(2001, 5, 20))

    def test_fixtures_due_on_round_date(self):
        fixtures = [Fixture(0, 0, 1, 2), Fixture(1, 1, 2, 1)]
        rounds = [Round(1, 7, 6), Round(2, 8, 3)]
        league = PremierLeagueState(fixtures, rounds, 2000)
        self.assertEqual([f.id for f in league.fixtures_on(date(2000, 8, 19))], [0])
        self.assertEqual(league.next_match_date(date(2000, 7, 1)), date(2000, 8, 19))
        league.record_result(0, 1, 0)
        self.assertEqual(league.next_match_date(date(2000, 8, 19)), date(2000, 8, 23))


if __name__ == "__main__":
    unittest.main()
