"""Gate-16 consecutive played-season stress in one live synthetic world."""
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
import unittest

from game_state import GameState
from human_gameplay import HumanGameplayController
from internal_save import (
    dumps_human_gameplay,
    loads_human_gameplay,
    snapshot_human_gameplay,
)
from match_schedule import MsvcCrtRng
from test_gate11_management_season import (
    Player,
    coefficient_matrix,
    players_for_club,
    round_robin_fixtures,
)


@dataclass(frozen=True)
class Club:
    index: int
    manager_id: int
    short_name: str
    country_id: int = 0
    competition_id: int = 0
    historical_competition_id: int = 0
    historical_slot_index: int = 0
    runtime_value_1c_source: int = 0
    team_category_code: int = 1


@dataclass(frozen=True)
class Country:
    id: int = 0
    name: str = "Testland"
    nationality_id: int = 0
    european_index: int = 1
    eu_status_flag: int = 1
    continent_id: int = 0
    financial_multiplier_percent: int = 100


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
    max_non_eu_players: int = 10
    runtime_kind_code: int = 1
    schedule_container_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 0
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 38


@dataclass(frozen=True)
class PremierRound:
    round_number: int
    scheduled_week: int
    scheduled_weekday: int


@dataclass(frozen=True)
class AnnualRound:
    id: int
    competition_id: int = 0
    type_code: int = 4
    team_count: int = 20
    new_entrants: int = 0
    scheduled_week: int = 7
    scheduled_weekday: int = 6
    replay_week: int = 0
    replay_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class LeagueAllocation:
    id: int
    competition_a_id: int = 0
    competition_a_start: int = 0
    competition_a_end: int = 0
    competition_b_id: int = 0
    competition_b_start: int = 1
    competition_b_end: int = 1


class ConsecutiveSeasonDatabase:
    players = tuple(
        player
        for club_id in range(1, 21)
        for player in players_for_club(club_id)
    )
    clubs = tuple(
        Club(
            club_id,
            club_id,
            f"C{club_id:02d}",
            historical_slot_index=club_id - 1,
        )
        for club_id in range(1, 21)
    )
    managers = tuple(Manager(club_id) for club_id in range(1, 21))
    competitions = (Competition(),)
    countries = (Country(),)
    real_fixtures = round_robin_fixtures()
    premier_league_rounds = tuple(
        PremierRound(round_index + 1, 7 + round_index, 6)
        for round_index in range(38)
    )
    rounds = tuple(
        AnnualRound(
            id=round_index,
            scheduled_week=7 + round_index,
            scheduled_weekday=6,
        )
        for round_index in range(38)
    )
    cup_allocation_instructions = ()
    # The annual transition API intentionally requires the eight recovered
    # English allocation IDs. For this synthetic stress world each row swaps
    # the same two positions inside competition 0. All memberships are already
    # 0, so this exercises the transition machinery without asserting any
    # original promotion/relegation result for this fake database.
    league_allocation_records = tuple(
        LeagueAllocation(allocation_id)
        for allocation_id in (0, 1, 2, 3, 4, 5, 6, 25)
    )


def _initial_scheduler_order(state):
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


def _publish_exact_synthetic_ranking(state):
    names = {
        int(club_id): str(state.clubs[int(club_id)].short_name).encode("cp1252")
        for club_id in state.premier_league.club_ids
    }
    ranking = state.premier_league.publish_exact_ranking(
        state.cup_results,
        names.get,
    )
    if ranking is None:
        raise AssertionError("complete synthetic league did not publish an exact ranking")
    return ranking


def _season_digest(state):
    payload = {
        "date": state.calendar.current_date.isoformat(),
        "results": [
            [
                int(fixture_id),
                int(result.home_goals),
                int(result.away_goals),
            ]
            for fixture_id, result in sorted(state.premier_league.results.items())
        ],
        "table": [
            [
                int(row.club_id),
                int(row.played),
                int(row.points),
                int(row.goals_for),
                int(row.goals_against),
            ]
            for row in state.premier_league_table()
        ],
        "players": [
            [
                int(player.index),
                int(player.club_id),
                int(player.condition),
                int(player.form_state),
                bool(player.injured),
                int(player.suspension_matches_remaining),
            ]
            for player in sorted(state.players.values(), key=lambda item: int(item.index))
        ],
    }
    return sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
    ).hexdigest()


def _complete_current_season(controller, *, max_days):
    state = controller.state
    attack = controller.attack_matrix
    defence = controller.defence_matrix
    start_results = len(state.premier_league.results)
    days = 0
    while len(state.premier_league.results) < len(state.premier_league.fixtures):
        days += 1
        if days > max_days:
            raise AssertionError(
                "consecutive-season stress exceeded day budget before season completion"
            )
        state.advance_one_day_with_premier_league_ai_fixtures(
            attack,
            defence,
            controller.match_rng,
        )
    if start_results != 0:
        raise AssertionError("new stress season unexpectedly started with results")
    return days


def _complete_remaining_season(controller, *, max_days):
    state = controller.state
    attack = controller.attack_matrix
    defence = controller.defence_matrix
    days = 0
    while len(state.premier_league.results) < len(state.premier_league.fixtures):
        days += 1
        if days > max_days:
            raise AssertionError(
                "save/reload consecutive-season stress exceeded day budget"
            )
        state.advance_one_day_with_premier_league_ai_fixtures(
            attack,
            defence,
            controller.match_rng,
        )
    return days


def _advance_to_result_count(controller, target, *, max_days=370):
    state = controller.state
    days = 0
    while len(state.premier_league.results) < int(target):
        days += 1
        if days > max_days:
            raise AssertionError(
                f"save/reload stress did not reach {target} results within day budget"
            )
        state.advance_one_day_with_premier_league_ai_fixtures(
            controller.attack_matrix,
            controller.defence_matrix,
            controller.match_rng,
        )
    if len(state.premier_league.results) != int(target):
        raise AssertionError(
            f"save/reload stress overshot target {target}: "
            f"{len(state.premier_league.results)}"
        )
    return days


def _roundtrip_controller(database, controller):
    before = snapshot_human_gameplay(controller)
    payload = dumps_human_gameplay(controller)
    restored = loads_human_gameplay(
        database,
        controller.attack_matrix,
        controller.defence_matrix,
        payload,
    )
    after = snapshot_human_gameplay(restored)
    if after != before:
        raise AssertionError("internal save/reload changed live controller state")
    return restored, len(payload)


class Gate16ConsecutiveSeasonTests(unittest.TestCase):
    def test_three_complete_seasons_run_in_one_live_world_across_two_rollovers(self):
        state = GameState.from_database(
            ConsecutiveSeasonDatabase(),
            date(2000, 8, 18),
            seed=0x13579BDF,
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(
            _initial_scheduler_order(state)
        )
        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x2468ACE0),
        )

        retained_runtimes = []
        season_digests = []
        rng_states = []
        completion_dates = []

        for season_index in range(3):
            retained_runtimes.append(state.premier_league)
            days = _complete_current_season(controller, max_days=370)
            self.assertLessEqual(days, 370)
            self.assertEqual(len(state.premier_league.results), 380)

            rows = state.premier_league_table()
            self.assertEqual(len(rows), 20)
            self.assertTrue(all(int(row.played) == 38 for row in rows))
            self.assertEqual(sum(int(row.played) for row in rows), 760)
            self.assertEqual(
                sum(int(row.goals_for) for row in rows),
                sum(int(row.goals_against) for row in rows),
            )
            self.assertEqual(
                sum(int(row.wins) for row in rows),
                sum(int(row.losses) for row in rows),
            )

            ranking = _publish_exact_synthetic_ranking(state)
            self.assertEqual(len(ranking), 20)
            self.assertEqual(set(ranking), set(range(1, 21)))

            for club_id in range(1, 21):
                roster = state.ordered_club_roster(club_id)
                self.assertGreaterEqual(
                    len(roster),
                    16,
                    f"season {season_index}: roster collapse at club {club_id}",
                )
                self.assertTrue(
                    all(int(player.club_id) == club_id for player in roster)
                )

            for player in state.players.values():
                self.assertGreaterEqual(int(player.condition), 0)
                self.assertLessEqual(int(player.condition), 100)
                self.assertGreaterEqual(int(player.form_state), 0)
                self.assertLessEqual(int(player.form_state), 4)
                self.assertGreaterEqual(
                    int(player.suspension_matches_remaining), 0
                )

            completion_dates.append(state.calendar.current_date)
            season_digests.append(_season_digest(state))
            rng_states.append(int(controller.match_rng.state) & 0xFFFFFFFF)

            if season_index == 2:
                break

            old_runtime = state.premier_league
            regeneration = controller.regenerate_annual_primary_season(
                season_year=2001 + season_index,
                procedural_league_ids=(),
            )
            self.assertIsNot(state.premier_league, old_runtime)
            self.assertEqual(len(state.premier_league.fixtures), 380)
            self.assertEqual(state.premier_league.results, {})
            self.assertEqual(
                int(controller.match_rng.state) & 0xFFFFFFFF,
                int(regeneration.state_after) & 0xFFFFFFFF,
            )
            self.assertEqual(
                state.club_competition_membership,
                {club_id: 0 for club_id in range(1, 21)},
            )
            self.assertTrue(state.primary_matchday_order)
            self.assertTrue(state.premier_league_scheduler_order)

        self.assertEqual(len({id(runtime) for runtime in retained_runtimes}), 3)
        self.assertEqual(len(season_digests), 3)
        self.assertEqual(len(completion_dates), 3)
        self.assertLess(completion_dates[0], completion_dates[1])
        self.assertLess(completion_dates[1], completion_dates[2])
        self.assertEqual(len(rng_states), 3)


    def test_three_seasons_survive_midseason_and_post_rollover_save_reload(self):
        database = ConsecutiveSeasonDatabase()
        state = GameState.from_database(
            database,
            date(2000, 8, 18),
            seed=0x0BADF00D,
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(
            _initial_scheduler_order(state)
        )
        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x10203040),
        )

        reload_payload_sizes = []
        monthly_update_counts = []
        season_digests = []
        midseason_targets = (120, 160, 200)

        for season_index, target in enumerate(midseason_targets):
            _advance_to_result_count(controller, target)
            controller, payload_size = _roundtrip_controller(database, controller)
            reload_payload_sizes.append(payload_size)

            remaining_days = _complete_remaining_season(
                controller,
                max_days=370,
            )
            self.assertLessEqual(remaining_days, 370)
            state = controller.state
            self.assertEqual(len(state.premier_league.results), 380)
            self.assertEqual(len(state.premier_league_table()), 20)
            self.assertTrue(
                all(int(row.played) == 38 for row in state.premier_league_table())
            )
            self.assertEqual(
                sum(int(row.goals_for) for row in state.premier_league_table()),
                sum(int(row.goals_against) for row in state.premier_league_table()),
            )
            self.assertEqual(
                sum(int(row.wins) for row in state.premier_league_table()),
                sum(int(row.losses) for row in state.premier_league_table()),
            )

            ranking = _publish_exact_synthetic_ranking(state)
            self.assertEqual(set(ranking), set(range(1, 21)))
            season_digests.append(_season_digest(state))
            monthly_update_counts.append(int(state.monthly_player_updates))

            for club_id in range(1, 21):
                roster = state.ordered_club_roster(club_id)
                self.assertGreaterEqual(
                    len(roster),
                    16,
                    f"season {season_index}: roster collapse after save/reload",
                )
                self.assertTrue(
                    all(int(player.club_id) == club_id for player in roster)
                )
            for player in state.players.values():
                self.assertGreaterEqual(int(player.condition), 0)
                self.assertLessEqual(int(player.condition), 100)
                self.assertGreaterEqual(int(player.form_state), 0)
                self.assertLessEqual(int(player.form_state), 4)
                self.assertGreaterEqual(
                    int(player.suspension_matches_remaining),
                    0,
                )

            if season_index == 2:
                break

            controller.regenerate_annual_primary_season(
                season_year=2001 + season_index,
                procedural_league_ids=(),
            )
            state = controller.state
            self.assertEqual(len(state.premier_league.fixtures), 380)
            self.assertEqual(state.premier_league.results, {})
            self.assertTrue(state.primary_matchday_order)
            self.assertTrue(state.premier_league_scheduler_order)

            controller, payload_size = _roundtrip_controller(database, controller)
            reload_payload_sizes.append(payload_size)
            self.assertEqual(controller.state.premier_league.results, {})
            self.assertEqual(len(controller.state.premier_league.fixtures), 380)

        self.assertEqual(len(reload_payload_sizes), 5)
        self.assertTrue(all(size > 0 for size in reload_payload_sizes))
        self.assertEqual(len(season_digests), 3)
        self.assertEqual(len(monthly_update_counts), 3)
        self.assertLess(monthly_update_counts[0], monthly_update_counts[1])
        self.assertLess(monthly_update_counts[1], monthly_update_counts[2])


if __name__ == "__main__":
    unittest.main()
