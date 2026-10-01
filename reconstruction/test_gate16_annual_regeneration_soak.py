"""Gate-16 work-ahead destructive tests for repeated annual replacement."""
import unittest
from dataclasses import dataclass
from datetime import date

from competition_state import PremierLeagueState
from game_state import GameState
from gate16_annual_regeneration_soak import audit_repeated_annual_regeneration
from human_gameplay import HumanGameplayController
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


def build_controller():
    state = GameState.from_players((), date(2001, 6, 30))
    state.premier_league = PremierLeagueState((Fixture(999, 0, 10, 11),))
    state.competitions = {0: Competition()}
    state.round_definitions = tuple(
        Round(index, scheduled_week=index + 7) for index in range(3)
    )
    state.cup_allocation_instructions = ()
    state.league_allocation_records = tuple(
        LeagueAllocation(value) for value in (0, 1, 2, 3, 4, 5, 6, 25)
    )
    state.clubs = {
        value: Club(value, chr(65 + offset), historical_slot_index=offset)
        for offset, value in enumerate((10, 11, 12, 13))
    }
    state.countries = {1: Country()}
    state.club_competition_membership = {10: 0, 11: 0, 12: 0, 13: 0}
    return HumanGameplayController(
        state, None, None, MsvcCrtRng(0x12345678)
    )


class Gate16AnnualRegenerationSoakTests(unittest.TestCase):
    def test_thirty_destructive_rollovers_do_not_accumulate_prior_runtime_state(self):
        controller = build_controller()

        def prepare(ctrl, cycle, _year):
            state = ctrl.state
            state.cup_results.replace_competition_ranking(
                0, (10, 11, 12, 13)
            )
            fixture_id = next(iter(state.premier_league.fixtures))
            if fixture_id not in state.premier_league.results:
                state.premier_league.record_result(
                    fixture_id, cycle % 4, (cycle + 1) % 3
                )
            state.prepared_match_environments[fixture_id] = object()

        snapshots = audit_repeated_annual_regeneration(
            controller,
            range(2001, 2031),
            prepare_completed_season=prepare,
            procedural_league_ids=(),
        )

        self.assertEqual(len(snapshots), 30)
        self.assertEqual(len({item.fixture_count for item in snapshots}), 1)
        self.assertTrue(all(item.fixture_count > 0 for item in snapshots))
        self.assertTrue(
            all(item.scheduler_fixture_count == item.fixture_count for item in snapshots)
        )
        self.assertTrue(all(item.result_count_after == 0 for item in snapshots))
        self.assertTrue(
            all(item.prepared_environment_count_after == 0 for item in snapshots)
        )
        self.assertTrue(all(item.runtime_object_replaced for item in snapshots))
        self.assertEqual(
            controller.state.club_competition_membership,
            {10: 0, 11: 0, 12: 0, 13: 0},
        )

    def test_soak_rejects_non_increasing_years_before_mutation(self):
        controller = build_controller()
        original = controller.state.premier_league
        with self.assertRaisesRegex(ValueError, "must increase"):
            audit_repeated_annual_regeneration(
                controller,
                (2002, 2001),
                prepare_completed_season=lambda *_: None,
                procedural_league_ids=(),
            )
        self.assertIs(controller.state.premier_league, original)

    def test_missing_qualification_still_fails_closed_instead_of_being_synthesized(self):
        controller = build_controller()
        original = controller.state.premier_league
        rng_before = controller.match_rng.state
        with self.assertRaisesRegex(
            RuntimeError, "season transition ranking is unresolved"
        ):
            audit_repeated_annual_regeneration(
                controller,
                (2001,),
                prepare_completed_season=lambda *_: None,
                procedural_league_ids=(),
            )
        self.assertIs(controller.state.premier_league, original)
        self.assertEqual(controller.match_rng.state, rng_before)


if __name__ == "__main__":
    unittest.main()
