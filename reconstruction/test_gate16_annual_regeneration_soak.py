"""Gate-16 work-ahead destructive tests for repeated annual replacement."""
import unittest
from dataclasses import dataclass
from datetime import date

from competition_state import PremierLeagueState
from game_state import GameState
from gate16_annual_regeneration_soak import audit_repeated_annual_regeneration
from human_gameplay import HumanGameplayController
from internal_save import (
    dumps_human_gameplay,
    loads_human_gameplay,
    snapshot_human_gameplay,
)
from match_schedule import MsvcCrtRng
from test_gate11_management_season import coefficient_matrix
from test_gate16_consecutive_seasons import ConsecutiveSeasonDatabase


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


def _scheduler_order(state):
    return tuple(
        (
            round_index,
            tuple(
                int(fixture.id)
                for fixture in state.premier_league.fixtures_for_round(round_index)
            ),
        )
        for round_index in range(38)
    )


def _build_save_growth_controller():
    database = ConsecutiveSeasonDatabase()
    state = GameState.from_database(
        database,
        date(2000, 8, 18),
        seed=0x13579BDF,
        season_year=2000,
    )
    state.install_premier_league_scheduler_order(_scheduler_order(state))
    controller = HumanGameplayController(
        state,
        coefficient_matrix(),
        coefficient_matrix(),
        MsvcCrtRng(0x2468ACE0),
    )
    return database, controller


def _season_owned_shape(state):
    """Bound collections that should be replaced rather than accumulated."""
    scheduler_ids = tuple(
        int(fixture_id)
        for round_index in sorted(state.premier_league_scheduler_order)
        for fixture_id in state.premier_league_scheduler_order[round_index]
    )
    return (
        len(state.premier_league.fixtures),
        len(state.premier_league.results),
        len(state.prepared_match_environments),
        len(state.premier_league_scheduler_order),
        len(scheduler_ids),
        len(set(scheduler_ids)),
        len(state.primary_matchday_order),
        len(state.primary_schedule_shadow.days),
        len(state.domestic_cups.nodes),
        len(state.european_cups.nodes),
        len(state.qualification_cups.nodes),
        len(state.procedural_leagues),
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

    def test_twelve_regeneration_save_roundtrips_keep_serialized_state_bounded(self):
        database, controller = _build_save_growth_controller()
        payload_sizes = []
        season_shapes = []

        for cycle, season_year in enumerate(range(2001, 2013)):
            state = controller.state
            old_runtime = state.premier_league

            # Synthetic qualification evidence is intentionally exact and
            # bounded. This stress tests replacement/persistence, not standings
            # or qualification fidelity.
            state.cup_results.replace_competition_ranking(
                0, tuple(range(1, 21))
            )

            # Dirty season-owned state immediately before rollover so the test
            # proves replacement rather than merely observing empty defaults.
            fixture_id = next(iter(state.premier_league.fixtures))
            if fixture_id not in state.premier_league.results:
                state.premier_league.record_result(
                    fixture_id,
                    cycle % 4,
                    (cycle + 1) % 3,
                )
            state.prepared_match_environments[fixture_id] = object()

            controller.regenerate_annual_primary_season(
                season_year=season_year,
                procedural_league_ids=(),
            )
            state = controller.state

            self.assertIsNot(state.premier_league, old_runtime)
            self.assertEqual(len(state.premier_league.fixtures), 380)
            self.assertEqual(state.premier_league.results, {})
            self.assertEqual(state.prepared_match_environments, {})

            shape_before = _season_owned_shape(state)
            self.assertEqual(shape_before[0], 380)
            self.assertEqual(shape_before[1], 0)
            self.assertEqual(shape_before[2], 0)
            self.assertEqual(shape_before[4], 380)
            self.assertEqual(shape_before[5], 380)

            before = snapshot_human_gameplay(controller)
            payload = dumps_human_gameplay(controller)
            restored = loads_human_gameplay(
                database,
                controller.attack_matrix,
                controller.defence_matrix,
                payload,
            )
            after = snapshot_human_gameplay(restored)
            self.assertEqual(after, before)
            self.assertEqual(dumps_human_gameplay(restored), payload)
            self.assertEqual(_season_owned_shape(restored.state), shape_before)

            payload_sizes.append(len(payload))
            season_shapes.append(shape_before)
            controller = restored

        self.assertEqual(len(payload_sizes), 12)
        self.assertEqual(len(set(season_shapes)), 1)
        # The compact JSON contains changing dates/RNG integers, so byte-for-byte
        # size equality is not a useful invariant. A 4 KiB spread is a generous
        # corruption guard: accumulating even one additional full PL season
        # schedule would exceed it by far.
        self.assertLessEqual(max(payload_sizes) - min(payload_sizes), 4096)

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
