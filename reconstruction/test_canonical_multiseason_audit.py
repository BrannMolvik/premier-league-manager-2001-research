"""Repository-side tests for the canonical Gate-16 multi-season audit runner."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from types import SimpleNamespace
import unittest

from canonical_multiseason_audit import (
    CanonicalMultiSeasonAuditError,
    _validate_fresh_regeneration_projection,
    run_multiseason_controller_audit,
)


@dataclass
class FakePlayer:
    index: int
    club_id: int
    condition: int = 100
    form_state: int = 2
    suspension_matches_remaining: int = 0


@dataclass(frozen=True)
class FakeTableRow:
    club_id: int
    played: int = 38
    points: int = 50
    goals_for: int = 40
    goals_against: int = 40
    wins: int = 10
    losses: int = 10


@dataclass(frozen=True)
class FakeScheduleNode:
    node_kind: str
    competition_id: int
    competition_context: int
    node_token: tuple


class FakePremierLeague:
    def __init__(self, generation: int, complete: bool):
        start = generation * 1000
        self.fixtures = {start + value: object() for value in range(380)}
        self.results = (
            {fixture_id: object() for fixture_id in self.fixtures}
            if complete
            else {}
        )
        self.club_ids = tuple(range(1, 21))


class FakeCalendar:
    def __init__(self):
        self.current_date = date(2000, 8, 18)


class FakeState:
    def __init__(self):
        self.calendar = FakeCalendar()
        self.generation = 0
        self.premier_league = FakePremierLeague(0, complete=False)
        self.clubs = {club_id: object() for club_id in range(1, 21)}
        self.competitions = {0: SimpleNamespace(id=0)}
        self.cup_allocation_instructions = ()
        self.club_competition_membership = {
            club_id: 0 for club_id in range(1, 21)
        }
        self.players = {
            club_id: FakePlayer(club_id, club_id) for club_id in range(1, 21)
        }
        self.club_roster_order = {
            club_id: (club_id,) for club_id in range(1, 21)
        }
        self.prepared_match_environments = {}
        self.procedural_leagues = {}
        self._refresh_projection(europe_node_count=2)

    def _refresh_projection(self, *, europe_node_count: int):
        fixture_ids = list(self.premier_league.fixtures)
        self.premier_league_scheduler_order = {
            round_index: tuple(
                fixture_ids[round_index * 10:(round_index + 1) * 10]
            )
            for round_index in range(38)
        }
        premier_nodes = tuple(
            FakeScheduleNode(
                "league_match",
                0,
                0,
                ("league_match", 0, 0, fixture_id),
            )
            for fixture_id in fixture_ids
        )
        domestic_nodes = tuple(
            FakeScheduleNode(
                "cup_match",
                1,
                0,
                ("cup_result", 1, 100, pair_index),
            )
            for pair_index in range(3)
        )
        european_nodes = tuple(
            FakeScheduleNode(
                "first_leg_match" if pair_index % 2 == 0 else "second_leg_match",
                10,
                0,
                (
                    "cup_first_leg" if pair_index % 2 == 0 else "cup_result",
                    10,
                    210,
                    pair_index // 2,
                ),
            )
            for pair_index in range(europe_node_count)
        )
        qualification_nodes = (
            FakeScheduleNode(
                "cup_match",
                19,
                0,
                ("cup_result", 19, 300, 0),
            ),
        )
        schedule_nodes = premier_nodes + domestic_nodes + european_nodes + qualification_nodes
        self.domestic_cups = SimpleNamespace(nodes=domestic_nodes)
        self.european_cups = SimpleNamespace(nodes=european_nodes)
        self.qualification_cups = SimpleNamespace(nodes=qualification_nodes)
        self.primary_schedule_shadow = SimpleNamespace(
            days={self.calendar.current_date + timedelta(days=1): schedule_nodes}
        )
        primary_entries = tuple(
            [("premier_league", int(node.node_token[-1])) for node in premier_nodes]
            + [("domestic_cup", node.node_token) for node in domestic_nodes]
            + [("european_cup", node.node_token) for node in european_nodes]
            + [("qualification_cup", node.node_token) for node in qualification_nodes]
        )
        self.primary_matchday_order = {
            self.calendar.current_date + timedelta(days=1): primary_entries
        }
        return schedule_nodes

    def advance_one_day_with_primary_ai_matches(self, *_args):
        self.calendar.current_date += timedelta(days=1)
        self.premier_league.results = {
            fixture_id: object() for fixture_id in self.premier_league.fixtures
        }
        return ()

    def premier_league_table(self):
        return tuple(FakeTableRow(club_id) for club_id in range(1, 21))


class FakeRng:
    def __init__(self):
        self.state = 0x12345678


class FakeController:
    attack_matrix = None
    defence_matrix = None

    def __init__(
        self,
        *,
        drift_on_cycle: int | None = None,
        variable_europe_on_cycle: int | None = None,
    ):
        self.state = FakeState()
        self.match_rng = FakeRng()
        self.rollovers = 0
        self.drift_on_cycle = drift_on_cycle
        self.variable_europe_on_cycle = variable_europe_on_cycle

    def regenerate_annual_primary_season(
        self,
        *,
        season_year,
        procedural_league_ids=None,
    ):
        del procedural_league_ids
        self.rollovers += 1
        self.state.generation += 1
        self.state.premier_league = FakePremierLeague(
            self.state.generation,
            complete=False,
        )
        self.state.prepared_match_environments = {}
        europe_node_count = 4 if self.variable_europe_on_cycle == self.rollovers else 2
        schedule_nodes = self.state._refresh_projection(
            europe_node_count=europe_node_count,
        )
        if self.drift_on_cycle == self.rollovers:
            stale = FakeScheduleNode(
                "cup_match",
                1,
                0,
                ("stale_prior_season", self.rollovers),
            )
            self.state.domestic_cups = SimpleNamespace(
                nodes=self.state.domestic_cups.nodes + (stale,)
            )
        self.match_rng.state = (self.match_rng.state + 0x10101) & 0xFFFFFFFF
        return SimpleNamespace(
            state_after=self.match_rng.state,
            total_draw_count=1234,
            season_year=int(season_year),
            competition=SimpleNamespace(schedule_nodes=schedule_nodes),
        )


def fake_qualification_probe(controller):
    if len(controller.state.premier_league.results) != 380:
        raise RuntimeError("season still incomplete")
    membership = dict(controller.state.club_competition_membership)
    qualification = SimpleNamespace(
        qualification_rankings_by_competition={0: tuple(range(1, 21))},
        cup_enumerated_club_ids_by_source={},
    )
    transition = SimpleNamespace(memberships=membership)
    return qualification, transition, controller.match_rng.state


class CanonicalMultiSeasonAuditRunnerTests(unittest.TestCase):
    def test_three_rollovers_require_monotonic_complete_seasons(self):
        controller = FakeController()
        report = run_multiseason_controller_audit(
            controller,
            rollover_count=3,
            max_days_per_season=2,
            procedural_league_ids=(),
            qualification_probe=fake_qualification_probe,
        )

        self.assertEqual(report["rollover_count"], 3)
        self.assertEqual(len(report["snapshots"]), 3)
        self.assertEqual(controller.rollovers, 3)
        self.assertEqual(
            [item["completed_premier_results"] for item in report["snapshots"]],
            [380, 380, 380],
        )
        self.assertEqual(
            [item["days_advanced"] for item in report["snapshots"]],
            [1, 1, 1],
        )
        self.assertEqual(
            [item["next_premier_fixture_count"] for item in report["snapshots"]],
            [380, 380, 380],
        )
        self.assertEqual(len(report["fresh_state_shapes"]), 3)
        self.assertEqual(controller.state.premier_league.results, {})

    def test_participant_dependent_fresh_cup_shape_is_allowed_when_projection_matches(self):
        controller = FakeController(variable_europe_on_cycle=3)
        report = run_multiseason_controller_audit(
            controller,
            rollover_count=3,
            max_days_per_season=2,
            procedural_league_ids=(),
            qualification_probe=fake_qualification_probe,
        )

        shapes = report["fresh_state_shapes"]
        self.assertEqual([shape[5] for shape in shapes], [2, 2, 4])
        self.assertEqual(shapes[2][2] - shapes[1][2], 2)
        self.assertEqual(shapes[2][3] - shapes[1][3], 2)

    def test_primary_projection_keeps_allowed_procedural_context_without_live_owner(self):
        node = FakeScheduleNode(
            "league_match",
            14,
            3,
            ("league_match", 14, 3, 0),
        )
        state = SimpleNamespace(
            primary_schedule_shadow=SimpleNamespace(days={date(2001, 1, 1): (node,)}),
            domestic_cups=SimpleNamespace(nodes=()),
            european_cups=SimpleNamespace(nodes=()),
            qualification_cups=SimpleNamespace(nodes=()),
            procedural_leagues={},
            primary_matchday_order={
                date(2001, 1, 1): (("procedural_league", node.node_token),)
            },
        )
        regeneration = SimpleNamespace(
            competition=SimpleNamespace(schedule_nodes=(node,))
        )

        # Gate-12 primary order is keyed by the source-authorized competition
        # ID, not by whether this particular context resolves to a live owner.
        _validate_fresh_regeneration_projection(
            state,
            regeneration,
            0,
            procedural_league_ids=(14,),
        )

    def test_current_regeneration_projection_mismatch_fails_closed(self):
        controller = FakeController(drift_on_cycle=2)
        with self.assertRaisesRegex(
            CanonicalMultiSeasonAuditError,
            "fresh domestic Cup state differs from current regeneration projection",
        ):
            run_multiseason_controller_audit(
                controller,
                rollover_count=3,
                max_days_per_season=2,
                procedural_league_ids=(),
                qualification_probe=fake_qualification_probe,
            )

    def test_day_budget_failure_does_not_regenerate(self):
        controller = FakeController()

        def never_ready(_controller):
            raise RuntimeError("still waiting")

        with self.assertRaisesRegex(
            CanonicalMultiSeasonAuditError,
            "did not complete within 1 days",
        ):
            run_multiseason_controller_audit(
                controller,
                rollover_count=2,
                max_days_per_season=1,
                procedural_league_ids=(),
                qualification_probe=never_ready,
            )
        self.assertEqual(controller.rollovers, 0)

    def test_rejects_single_rollover_as_not_multiseason(self):
        with self.assertRaisesRegex(ValueError, "at least two rollovers"):
            run_multiseason_controller_audit(
                FakeController(),
                rollover_count=1,
                qualification_probe=fake_qualification_probe,
            )


if __name__ == "__main__":
    unittest.main()
