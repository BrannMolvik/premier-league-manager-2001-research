import unittest
from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

from competition_state import PremierLeagueState
from cup_progression import CupResultRegistry
from game_state import GameState
from match_schedule import MsvcCrtRng
from season_regeneration import materialize_annual_primary_schedule


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    schedule_container_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 1
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 3


@dataclass(frozen=True)
class Round:
    id: int
    competition_id: int
    type_code: int
    team_count: int
    new_entrants: int
    scheduled_week: int
    scheduled_weekday: int
    replay_week: int = 0
    replay_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class Club:
    index: int
    short_name: str
    competition_id: int
    historical_competition_id: int
    historical_slot_index: int
    country_id: int = 1
    runtime_value_1c_source: int = 0
    team_category_code: int = 1


@dataclass(frozen=True)
class Country:
    id: int
    eu_status_flag: int = 0


@dataclass(frozen=True)
class Fixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


class AnnualPrimaryStateInstallTests(unittest.TestCase):
    def materialize(self):
        competition = Competition(0, 1)
        rounds = tuple(
            Round(
                id=index,
                competition_id=0,
                type_code=4,
                team_count=4,
                new_entrants=0,
                scheduled_week=index + 7,
                scheduled_weekday=6,
            )
            for index in range(3)
        )
        clubs = (
            Club(10, "A", 0, 0, 0),
            Club(11, "B", 0, 0, 1),
            Club(12, "C", 0, 0, 2),
            Club(13, "Relegated", 0, 0, 3),
            Club(20, "Promoted", 2, 2, 0),
        )
        return materialize_annual_primary_schedule(
            MsvcCrtRng(0x12345678),
            (competition,),
            rounds,
            clubs,
            (Country(1),),
            (),
            (),
            club_competition_membership={13: 2, 20: 0},
            season_year=2001,
        )

    def test_install_replaces_prior_season_primary_runtime_together(self):
        state = GameState.from_players((), date(2001, 6, 30))
        old = PremierLeagueState((Fixture(999, 0, 10, 13),))
        old.record_result(999, 4, 0)
        state.premier_league = old
        state.cup_results.replace_competition_ranking(0, (10, 13))
        state.primary_matchday_order = {
            date(2001, 1, 1): (("premier_league", 999),)
        }
        state.prepared_match_environments[999] = object()

        regeneration = self.materialize()
        state.install_annual_primary_regeneration(
            regeneration,
            club_competition_membership={10: 0, 11: 0, 12: 0, 13: 2, 20: 0},
            procedural_league_ids=(),
        )

        self.assertIsNot(state.premier_league, old)
        self.assertEqual(state.premier_league.results, {})
        self.assertIn(20, state.premier_league.club_ids)
        self.assertNotIn(13, state.premier_league.club_ids)
        self.assertNotIn(999, state.premier_league.fixtures)
        self.assertFalse(state.cup_results.outcomes)
        self.assertNotIn((0, 0), state.cup_results.competition_rankings)
        self.assertTrue(state.primary_matchday_order)
        self.assertNotIn(date(2001, 1, 1), state.primary_matchday_order)
        self.assertTrue(
            all(
                entry[0] == "premier_league"
                for entries in state.primary_matchday_order.values()
                for entry in entries
            )
        )
        self.assertEqual(state.prepared_match_environments, {})
        self.assertEqual(state.club_competition_membership[13], 2)
        self.assertEqual(state.club_competition_membership[20], 0)

    def test_invalid_regeneration_does_not_mutate_existing_season(self):
        state = GameState.from_players((), date(2001, 6, 30))
        old = PremierLeagueState((Fixture(999, 0, 10, 13),))
        state.premier_league = old
        state.club_competition_membership = {10: 0, 13: 0}
        old_order = {date(2001, 1, 1): (("premier_league", 999),)}
        state.primary_matchday_order = dict(old_order)

        invalid = SimpleNamespace(
            season_year=2001,
            competition=SimpleNamespace(
                schedule_nodes=(),
                cup_runtime=SimpleNamespace(ranked_source_club_ids=()),
            ),
            shuffle=SimpleNamespace(buckets=()),
        )

        with self.assertRaisesRegex(
            ValueError,
            "annual Premier League schedule contains no LeagueMatch nodes",
        ):
            state.install_annual_primary_regeneration(
                invalid,
                club_competition_membership={10: 2, 13: 0},
                procedural_league_ids=(),
            )

        self.assertIs(state.premier_league, old)
        self.assertEqual(state.club_competition_membership, {10: 0, 13: 0})
        self.assertEqual(state.primary_matchday_order, old_order)


if __name__ == "__main__":
    unittest.main()
