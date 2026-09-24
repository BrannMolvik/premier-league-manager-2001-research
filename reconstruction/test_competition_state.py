import unittest
from dataclasses import dataclass

from competition_state import PremierLeagueState


@dataclass(frozen=True)
class Fixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


class LeagueStateTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = [
            Fixture(0, 0, 1, 2),
            Fixture(1, 0, 3, 4),
            Fixture(2, 1, 2, 3),
            Fixture(3, 1, 4, 1),
        ]
        self.league = PremierLeagueState(self.fixtures)

    def test_round_lookup_and_next_round(self):
        self.assertEqual([f.id for f in self.league.fixtures_for_round(0)], [0, 1])
        self.assertEqual(self.league.next_unplayed_round(), 0)
        self.league.record_result(0, 2, 0)
        self.assertEqual(self.league.next_unplayed_round(), 0)
        self.league.record_result(1, 1, 1)
        self.assertEqual(self.league.next_unplayed_round(), 1)

    def test_table_accumulates_points_and_goal_difference(self):
        self.league.record_result(0, 2, 0)
        self.league.record_result(1, 1, 1)
        table = self.league.table()
        self.assertEqual(table[0].club_id, 1)
        self.assertEqual((table[0].played, table[0].wins, table[0].points), (1, 1, 3))
        club3 = next(r for r in table if r.club_id == 3)
        self.assertEqual((club3.draws, club3.points), (1, 1))
        club2 = next(r for r in table if r.club_id == 2)
        self.assertEqual(club2.goal_difference, -2)

    def test_duplicate_result_is_rejected(self):
        self.league.record_result(0, 1, 0)
        with self.assertRaises(ValueError):
            self.league.record_result(0, 0, 0)


if __name__ == '__main__':
    unittest.main()
