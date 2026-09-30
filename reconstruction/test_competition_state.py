import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_state import LeagueRow, PremierLeagueState
from cup_progression import CupResultRegistry
from game_state import GameState


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

    def test_original_numeric_league_comparator_precedes_goal_difference_with_played(self):
        # Two wins + two heavy losses vs six draws, both 6 points.
        # Source native 0x4F45E0 prioritizes fewer matches played even
        # though the higher-ranked club has a much worse goal difference.
        first = LeagueRow(
            club_id=10, played=4, wins=2, losses=2,
            goals_for=2, goals_against=9, points=6,
        )
        second = LeagueRow(
            club_id=30, played=6, draws=6,
            goals_for=0, goals_against=0, points=6,
        )
        self.assertLess(
            PremierLeagueState._original_numeric_table_key(first),
            PremierLeagueState._original_numeric_table_key(second),
        )
        self.assertEqual(
            PremierLeagueState._original_numeric_table_key(first),
            (-6, 4, 7, -2, 9),
        )

    def test_exact_premier_ranking_uses_original_short_name_bytes_not_club_id(self):
        league = PremierLeagueState((
            Fixture(0, 0, 10, 20),
            Fixture(1, 0, 30, 40),
        ))
        league.record_result(0, 1, 0)
        league.record_result(1, 1, 0)
        names = {10: b"Zulu", 20: b"Beta", 30: b"Alpha", 40: b"Gamma"}
        self.assertEqual(
            tuple(row.club_id for row in league.table()), (10, 30, 20, 40)
        )
        self.assertEqual(
            tuple(row.club_id for row in league.table(names.get)),
            (30, 10, 20, 40),
        )
        self.assertIsNone(league.exact_ranking())
        self.assertEqual(league.exact_ranking(names.get), (30, 10, 20, 40))
        registry = CupResultRegistry()
        self.assertEqual(
            league.publish_exact_ranking(registry, names.get),
            (30, 10, 20, 40),
        )
        self.assertEqual(registry.competition_rankings[0], (30, 10, 20, 40))

    def test_unproven_full_source_key_ties_cannot_be_published(self):
        league = PremierLeagueState((
            Fixture(0, 0, 10, 20),
            Fixture(1, 0, 30, 40),
        ))
        league.record_result(0, 1, 0)
        league.record_result(1, 1, 0)
        tied = {10: b"Same", 30: b"Same", 20: b"Beta", 40: b"Gamma"}
        with self.assertRaisesRegex(ValueError, "qsort tie order"):
            league.table(tied.get)
        self.assertIsNone(league.exact_ranking(tied.get))
        self.assertIsNone(league.exact_ranking(lambda _club: None))
        registry = CupResultRegistry()
        self.assertIsNone(league.publish_exact_ranking(registry, tied.get))
        self.assertEqual(registry.competition_rankings, {})

    def test_gamestate_table_adapts_canonical_club_short_names_and_fallbacks(self):
        league = PremierLeagueState((
            Fixture(0, 0, 10, 20),
            Fixture(1, 0, 30, 40),
        ))
        league.record_result(0, 1, 0)
        league.record_result(1, 1, 0)
        names = {10: "Zulu", 20: "Beta", 30: "Alpha", 40: "Gamma"}
        fake = SimpleNamespace(
            premier_league=league,
            clubs={k: SimpleNamespace(short_name=v) for k, v in names.items()},
        )
        self.assertEqual(
            tuple(r.club_id for r in GameState.premier_league_table(fake)),
            (30, 10, 20, 40),
        )
        fake.clubs[30] = SimpleNamespace()  # Missing source byte name.
        self.assertEqual(
            tuple(r.club_id for r in GameState.premier_league_table(fake)),
            (10, 30, 20, 40),
        )
        fake.clubs[30] = SimpleNamespace(short_name="Zulu")
        self.assertEqual(
            tuple(r.club_id for r in GameState.premier_league_table(fake)),
            (10, 30, 20, 40),
        )

    def test_original_short_name_byte_order_differs_from_unicode_order(self):
        league = PremierLeagueState((
            Fixture(0, 0, 10, 20),
            Fixture(1, 0, 30, 40),
        ))
        league.record_result(0, 1, 0)
        league.record_result(1, 1, 0)
        # CP1252 0x9F (Ÿ) sorts before 0xC0 (À), even though the
        # Python Unicode codepoint order is the opposite.
        names = {10: b"\xc0", 30: b"\x9f", 20: b"Beta", 40: b"Gamma"}
        self.assertEqual(
            tuple(row.club_id for row in league.table(names.get))[:2],
            (30, 10),
        )
        with self.assertRaisesRegex(ValueError, "CP1252"):
            league.table(lambda _club: "not original source bytes")

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

    def test_annual_procedural_nodes_project_to_fresh_premier_state(self):
        nodes = (
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=0,
                competition_context=0,
                round_id=None,
                pair_index=0,
                schedule_index=0,
                scheduled_week=7,
                scheduled_weekday=6,
                participant_0_ref=direct_club_ref(20),
                participant_1_ref=direct_club_ref(10),
                node_token=("league_match", 0, 0, 41),
            ),
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=0,
                competition_context=0,
                round_id=None,
                pair_index=1,
                schedule_index=0,
                scheduled_week=7,
                scheduled_weekday=6,
                participant_0_ref=direct_club_ref(11),
                participant_1_ref=direct_club_ref(12),
                node_token=("league_match", 0, 0, 42),
            ),
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=0,
                competition_context=0,
                round_id=None,
                pair_index=0,
                schedule_index=1,
                scheduled_week=8,
                scheduled_weekday=3,
                participant_0_ref=direct_club_ref(10),
                participant_1_ref=direct_club_ref(11),
                node_token=("league_match", 0, 0, 43),
            ),
        )

        league = PremierLeagueState.from_procedural_schedule_nodes(
            nodes,
            season_year=2001,
        )

        self.assertEqual(league.fixture_source_order, (41, 42, 43))
        self.assertEqual(league.round_source_order, (0, 1))
        self.assertEqual(
            (league.fixtures[41].home_club_id, league.fixtures[41].away_club_id),
            (20, 10),
        )
        self.assertEqual(league.round_date(0).year, 2001)
        self.assertEqual(league.results, {})

    def test_duplicate_result_is_rejected(self):
        self.league.record_result(0, 1, 0)
        with self.assertRaises(ValueError):
            self.league.record_result(0, 0, 0)


if __name__ == '__main__':
    unittest.main()
