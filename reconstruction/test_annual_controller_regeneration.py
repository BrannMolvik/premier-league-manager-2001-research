import unittest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from datetime import date

from competition_state import PremierLeagueState
from game_state import GameState
from human_gameplay import (
    HumanGameplayController,
    _annual_cup_child_procedural_ids,
)
from match_schedule import MsvcCrtRng


@dataclass(frozen=True)
class Competition:
    id: int = 0
    runtime_kind_code: int = 1
    schedule_container_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 1
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 3


@dataclass(frozen=True)
class Round:
    id: int
    competition_id: int = 0
    type_code: int = 4
    team_count: int = 4
    new_entrants: int = 0
    scheduled_week: int = 7
    scheduled_weekday: int = 6
    replay_week: int = 0
    replay_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class Club:
    index: int
    short_name: str
    competition_id: int = 0
    historical_competition_id: int = 0
    historical_slot_index: int = 0
    country_id: int = 1
    runtime_value_1c_source: int = 0
    team_category_code: int = 1


@dataclass(frozen=True)
class Country:
    id: int = 1
    eu_status_flag: int = 0


@dataclass(frozen=True)
class Fixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


@dataclass(frozen=True)
class LeagueAllocation:
    id: int
    competition_a_id: int = 0
    competition_a_start: int = 0
    competition_a_end: int = 0
    competition_b_id: int = 0
    competition_b_start: int = 1
    competition_b_end: int = 1


class AnnualControllerRegenerationTests(unittest.TestCase):
    def build_controller(self):
        state = GameState.from_players((), date(2001, 6, 30))
        old = PremierLeagueState((Fixture(999, 0, 10, 11),))
        old.record_result(999, 2, 0)
        state.premier_league = old
        state.competitions = {0: Competition()}
        state.round_definitions = tuple(
            Round(
                id=index,
                scheduled_week=index + 7,
                scheduled_weekday=6,
            )
            for index in range(3)
        )
        state.cup_allocation_instructions = ()
        state.league_allocation_records = tuple(
            LeagueAllocation(allocation_id)
            for allocation_id in (0, 1, 2, 3, 4, 5, 6, 25)
        )
        state.clubs = {
            10: Club(10, "A", historical_slot_index=0),
            11: Club(11, "B", historical_slot_index=1),
            12: Club(12, "C", historical_slot_index=2),
            13: Club(13, "D", historical_slot_index=3),
        }
        state.countries = {1: Country()}
        state.club_competition_membership = {
            10: 0,
            11: 0,
            12: 0,
            13: 0,
        }
        state.cup_results.replace_competition_ranking(
            0,
            (10, 11, 12, 13),
        )
        controller = HumanGameplayController(
            state,
            None,
            None,
            MsvcCrtRng(0x12345678),
        )
        return controller, old

    def test_annual_cup_child_procedural_ids_follow_parent_relationships(self):
        competitions = (
            Competition(id=9, runtime_kind_code=2),
            Competition(id=14, parent_competition_id=9),
            Competition(id=167, parent_competition_id=9),
            Competition(id=101, runtime_kind_code=2),
            Competition(id=192, parent_competition_id=101),
            Competition(id=500, parent_competition_id=400),
        )

        self.assertEqual(
            _annual_cup_child_procedural_ids(competitions, (9, 101)),
            (14, 167, 192),
        )

    def test_success_commits_state_and_controller_rng_together(self):
        controller, old = self.build_controller()
        rng_before = controller.match_rng.state

        regeneration = controller.regenerate_annual_primary_season(
            season_year=2001,
            procedural_league_ids=(),
        )

        self.assertIsNot(controller.state.premier_league, old)
        self.assertNotIn(999, controller.state.premier_league.fixtures)
        self.assertEqual(controller.state.premier_league.results, {})
        self.assertTrue(controller.state.primary_matchday_order)
        self.assertEqual(
            controller.match_rng.state,
            regeneration.state_after,
        )
        self.assertNotEqual(controller.match_rng.state, rng_before)
        self.assertEqual(
            controller.state.club_competition_membership,
            {10: 0, 11: 0, 12: 0, 13: 0},
        )

    def test_default_rollover_keeps_all_played_annual_sources_live(self):
        controller, _old = self.build_controller()
        original_install = controller.state.install_annual_primary_regeneration
        controller.state.install_annual_primary_regeneration = Mock(
            wraps=original_install
        )

        with patch(
            "season_regeneration.partition_annual_type3_league_sources",
            return_value=((0, 77, 88), ()),
        ):
            controller.regenerate_annual_primary_season(
                season_year=2001,
            )

        installed_ids = (
            controller.state.install_annual_primary_regeneration.call_args.kwargs[
                "procedural_league_ids"
            ]
        )
        self.assertIn(77, installed_ids)
        self.assertIn(88, installed_ids)
        self.assertNotIn(14, installed_ids)
        self.assertNotIn(167, installed_ids)
        self.assertEqual(len(installed_ids), len(set(installed_ids)))

    def test_failed_preview_consumes_neither_state_nor_controller_rng(self):
        controller, old = self.build_controller()
        controller.state.cup_results.clear_competition_ranking(0)
        rng_before = controller.match_rng.state
        memberships_before = dict(controller.state.club_competition_membership)

        with self.assertRaisesRegex(
            RuntimeError,
            "season transition ranking is unresolved",
        ):
            controller.regenerate_annual_primary_season(
                season_year=2001,
                procedural_league_ids=(),
            )

        self.assertIs(controller.state.premier_league, old)
        self.assertEqual(controller.match_rng.state, rng_before)
        self.assertEqual(
            controller.state.club_competition_membership,
            memberships_before,
        )


if __name__ == "__main__":
    unittest.main()
