import unittest
from dataclasses import dataclass

from competition_state import PremierLeagueState


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

    def test_next_club_match_date_is_strictly_after_current_fixture(self):
        league = PremierLeagueState(
            (
                Fixture(0, 0, 1, 2),
                Fixture(1, 1, 1, 3),
                Fixture(2, 2, 2, 3),
            ),
            (
                Round(1, 7, 6),
                Round(2, 8, 3),
                Round(3, 9, 6),
            ),
            2000,
        )
        first = league.round_date(0)
        second = league.round_date(1)
        third = league.round_date(2)

        league.record_result(0, 1, 0)

        self.assertEqual(
            league.next_club_match_date(1, after_date=first),
            second,
        )
        self.assertEqual(
            league.next_club_match_date(2, after_date=first),
            third,
        )
        self.assertIsNone(
            league.next_club_match_date(1, after_date=second),
        )


    def test_fixed_fixture_builder_preserves_round_then_source_order(self):
        league = PremierLeagueState(
            (
                # Deliberately interleave rounds and scramble fixture IDs.
                Fixture(40, 0, 1, 2),
                Fixture(3, 1, 3, 4),
                Fixture(10, 0, 5, 6),
                Fixture(7, 0, 7, 8),
            ),
            (
                Round(1, 7, 6),
                Round(2, 8, 3),
            ),
            2000,
        )

        self.assertEqual(
            league.fixed_fixture_insertion_ids(),
            (40, 10, 7, 3),
        )

    def test_fixed_date_bucket_head_insertion_reverses_source_insertion(self):
        league = PremierLeagueState(
            (
                Fixture(40, 0, 1, 2),
                Fixture(10, 0, 3, 4),
                Fixture(7, 0, 5, 6),
            ),
            (Round(1, 7, 6),),
            2000,
        )
        on_date = league.round_date(0)

        self.assertEqual(
            league.fixed_fixture_insertion_ids_on(on_date),
            (40, 10, 7),
        )
        self.assertEqual(
            league.fixed_fixture_pre_shuffle_ids_on(on_date),
            (7, 10, 40),
        )

        league.record_result(10, 0, 0)
        self.assertEqual(
            league.fixed_fixture_pre_shuffle_ids_on(on_date),
            (7, 40),
        )

    def test_duplicate_result_is_rejected(self):
        self.league.record_result(0, 1, 0)
        with self.assertRaises(ValueError):
            self.league.record_result(0, 0, 0)


if __name__ == '__main__':
    unittest.main()
