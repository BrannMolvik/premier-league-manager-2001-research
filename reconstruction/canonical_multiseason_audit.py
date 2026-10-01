"""Canonical Gate-16 multi-season shipped-data audit.

This runner extends the proven one-season canonical annual rollover audit across
multiple consecutive seasons in one live controller. It never synthesizes
standings, qualification, cup outcomes, or RNG state. Each season must reach
the same fail-closed annual qualification boundary before regeneration.

The public controller-level helper is intentionally testable with a bounded
fake runtime. The canonical entrypoint always constructs the controller from
the user's authorized original FM2001 game directory.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Callable

from canonical_annual_rollover_audit import _qualification_if_complete
from human_gameplay import HumanGameplayController
from domestic_cup_state import (
    ANNUAL_QUALIFICATION_CUP_IDS,
    ENGLISH_DOMESTIC_CUP_IDS,
    EUROPEAN_CUP_IDS,
)
from season_regeneration import partition_annual_type3_league_sources


class CanonicalMultiSeasonAuditError(RuntimeError):
    """Repeated canonical season progression violated a long-duration invariant."""


@dataclass(frozen=True)
class CanonicalSeasonRolloverSnapshot:
    cycle: int
    qualification_captured_on: str
    days_advanced: int
    completed_premier_results: int
    membership_changes: int
    rng_before_rollover: int
    rng_after_rollover: int
    rollover_draw_count: int
    next_season_year: int
    next_premier_fixture_count: int
    next_primary_order_days: int
    next_primary_entry_count: int
    next_shadow_entry_count: int
    next_domestic_node_count: int
    next_european_node_count: int
    next_qualification_node_count: int
    next_procedural_league_count: int
    live_roster_reference_count: int


QualificationProbe = Callable[[object], tuple[object, object, int]]


def _scheduler_fixture_ids(state) -> tuple[int, ...]:
    order = state.premier_league_scheduler_order
    return tuple(
        int(fixture_id)
        for round_index in sorted(order)
        for fixture_id in order[round_index]
    )


def _fresh_primary_shape(state) -> tuple[int, ...]:
    primary_entries = sum(
        len(entries) for entries in state.primary_matchday_order.values()
    )
    shadow_entries = sum(
        len(entries) for entries in state.primary_schedule_shadow.days.values()
    )
    return (
        len(state.premier_league.fixtures),
        len(_scheduler_fixture_ids(state)),
        primary_entries,
        shadow_entries,
        len(state.domestic_cups.nodes),
        len(state.european_cups.nodes),
        len(state.qualification_cups.nodes),
        len(state.procedural_leagues),
    )


def _node_signature(node) -> tuple:
    return (
        str(node.node_kind),
        int(node.competition_id),
        int(node.competition_context),
        tuple(node.node_token),
    )


def _validate_fresh_regeneration_projection(state, regeneration, cycle: int) -> None:
    """Prove fresh season-owned state is exactly the current regeneration.

    Cup participant counts are legitimately qualification-dependent. A fresh
    season can therefore contain a different number of Cup nodes than the
    previous fresh season without representing accumulation. The corruption
    guard must compare each installed runtime against *that cycle's* materialized
    schedule instead of requiring cross-season count equality.
    """

    schedule_nodes = tuple(regeneration.competition.schedule_nodes)
    expected_shadow = Counter(_node_signature(node) for node in schedule_nodes)
    actual_shadow = Counter(
        _node_signature(entry)
        for on_date in sorted(state.primary_schedule_shadow.days)
        for entry in state.primary_schedule_shadow.days[on_date]
    )
    if actual_shadow != expected_shadow:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: fresh primary shadow differs from current "
            "regeneration projection"
        )

    cup_kinds = frozenset(("cup_match", "first_leg_match", "second_leg_match"))
    owners = (
        ("domestic", ENGLISH_DOMESTIC_CUP_IDS, state.domestic_cups),
        ("European", EUROPEAN_CUP_IDS, state.european_cups),
        ("qualification", ANNUAL_QUALIFICATION_CUP_IDS, state.qualification_cups),
    )
    for label, competition_ids, owner in owners:
        expected = Counter(
            _node_signature(node)
            for node in schedule_nodes
            if int(node.competition_id) in competition_ids
            and str(node.node_kind) in cup_kinds
        )
        actual = Counter(_node_signature(node) for node in owner.nodes)
        if actual != expected:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: fresh {label} Cup state differs from current "
                "regeneration projection"
            )

    live_procedural_keys = {
        (int(key[0]), int(key[1])) for key in state.procedural_leagues
    }
    current_procedural_keys = {
        (int(node.competition_id), int(node.competition_context))
        for node in schedule_nodes
        if str(node.node_kind) == "league_match"
        and int(node.competition_id) != 0
    }
    stale_procedural_keys = live_procedural_keys - current_procedural_keys
    if stale_procedural_keys:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: fresh procedural state retained non-current owners "
            f"{tuple(sorted(stale_procedural_keys))}"
        )

    expected_primary_entries: list[tuple] = []
    for node in schedule_nodes:
        competition_id = int(node.competition_id)
        competition_context = int(node.competition_context)
        node_kind = str(node.node_kind)
        node_token = tuple(node.node_token)
        if (
            node_kind in ("fixed_league_match", "league_match")
            and competition_id == 0
            and competition_context == 0
        ):
            expected_primary_entries.append(("premier_league", int(node_token[-1])))
        elif competition_id in ENGLISH_DOMESTIC_CUP_IDS and node_kind in cup_kinds:
            expected_primary_entries.append(("domestic_cup", node_token))
        elif competition_id in EUROPEAN_CUP_IDS and node_kind in cup_kinds:
            expected_primary_entries.append(("european_cup", node_token))
        elif competition_id in ANNUAL_QUALIFICATION_CUP_IDS and node_kind in cup_kinds:
            expected_primary_entries.append(("qualification_cup", node_token))
        elif (
            node_kind == "league_match"
            and (competition_id, competition_context) in live_procedural_keys
        ):
            expected_primary_entries.append(("procedural_league", node_token))

    actual_primary_entries = [
        tuple(entry)
        for on_date in sorted(state.primary_matchday_order)
        for entry in state.primary_matchday_order[on_date]
    ]
    if Counter(actual_primary_entries) != Counter(expected_primary_entries):
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: fresh shared-primary order differs from current "
            "regeneration projection"
        )


def _validate_live_references(state, cycle: int) -> int:
    seen_players: set[int] = set()
    roster_reference_count = 0

    for club_id, roster in state.club_roster_order.items():
        club_id = int(club_id)
        if club_id not in state.clubs:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: roster exists for unknown club {club_id}"
            )
        for player_id in roster:
            player_id = int(player_id)
            if player_id not in state.players:
                raise CanonicalMultiSeasonAuditError(
                    f"cycle {cycle}: roster references unknown player {player_id}"
                )
            if player_id in seen_players:
                raise CanonicalMultiSeasonAuditError(
                    f"cycle {cycle}: player {player_id} appears in multiple club rosters"
                )
            player = state.players[player_id]
            if int(player.club_id) != club_id:
                raise CanonicalMultiSeasonAuditError(
                    f"cycle {cycle}: player {player_id} roster/ownership mismatch "
                    f"{club_id} != {int(player.club_id)}"
                )
            seen_players.add(player_id)
            roster_reference_count += 1

    for club_id, competition_id in state.club_competition_membership.items():
        club_id = int(club_id)
        competition_id = int(competition_id)
        if club_id not in state.clubs:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: membership references unknown club {club_id}"
            )
        if competition_id not in state.competitions:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: membership references unknown competition "
                f"{competition_id}"
            )

    for player_id, player in state.players.items():
        condition = int(player.condition)
        form_state = int(player.form_state)
        suspension = int(player.suspension_matches_remaining)
        if not 0 <= condition <= 100:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: player {int(player_id)} invalid Condition {condition}"
            )
        if not 0 <= form_state <= 4:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: player {int(player_id)} invalid Form {form_state}"
            )
        if suspension < 0:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: player {int(player_id)} negative suspension {suspension}"
            )

    return roster_reference_count


def _validate_completed_premier(state, cycle: int) -> None:
    league = state.premier_league
    if league is None:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: Premier League runtime disappeared"
        )
    if len(league.fixtures) != 380:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: expected 380 Premier League fixtures, "
            f"found {len(league.fixtures)}"
        )
    if len(league.results) != 380:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: annual qualification became ready before all "
            f"380 Premier League fixtures completed"
        )

    rows = tuple(state.premier_league_table())
    if len(rows) != 20:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: expected 20 Premier League table rows, found {len(rows)}"
        )
    if any(int(row.played) != 38 for row in rows):
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: not every Premier League club played 38 matches"
        )
    if sum(int(row.played) for row in rows) != 760:
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: Premier League played totals do not reconcile"
        )
    if sum(int(row.goals_for) for row in rows) != sum(
        int(row.goals_against) for row in rows
    ):
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: Premier League goals for/against do not reconcile"
        )
    if sum(int(row.wins) for row in rows) != sum(
        int(row.losses) for row in rows
    ):
        raise CanonicalMultiSeasonAuditError(
            f"cycle {cycle}: Premier League wins/losses do not reconcile"
        )


def run_multiseason_controller_audit(
    controller,
    *,
    rollover_count: int = 3,
    max_days_per_season: int = 420,
    procedural_league_ids=None,
    qualification_probe: QualificationProbe | None = None,
) -> dict:
    """Run repeated completed-season -> annual-regeneration cycles.

    The caller supplies a live controller. Canonical callers should leave
    qualification_probe unset so the source-backed annual qualification helper
    is used. Tests may inject a deterministic fake probe to exercise the audit
    control flow without original source data.
    """

    rollover_count = int(rollover_count)
    max_days_per_season = int(max_days_per_season)
    if rollover_count < 2:
        raise ValueError("canonical multi-season audit requires at least two rollovers")
    if max_days_per_season < 1:
        raise ValueError("max_days_per_season must be positive")

    probe = _qualification_if_complete if qualification_probe is None else qualification_probe
    snapshots: list[CanonicalSeasonRolloverSnapshot] = []
    fresh_shapes: list[tuple[int, ...]] = []
    previous_capture_date: date | None = None
    retained_runtimes: list[object] = []

    for cycle in range(rollover_count):
        state = controller.state
        season_start_date = state.calendar.current_date
        qualification = None
        transition = None
        last_error: str | None = None

        for days_advanced in range(max_days_per_season + 1):
            try:
                qualification, transition, _preview_rng = probe(controller)
            except RuntimeError as exc:
                last_error = str(exc)
            else:
                break

            if days_advanced == max_days_per_season:
                raise CanonicalMultiSeasonAuditError(
                    f"cycle {cycle}: annual qualification did not complete within "
                    f"{max_days_per_season} days; last_error={last_error!r}"
                )

            state.advance_one_day_with_primary_ai_matches(
                controller.attack_matrix,
                controller.defence_matrix,
                controller.match_rng,
            )
        else:  # pragma: no cover
            raise AssertionError("unreachable multi-season audit loop")

        if qualification is None or transition is None:
            raise AssertionError("annual qualification readiness was not captured")

        captured_date = state.calendar.current_date
        if captured_date <= season_start_date:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: calendar did not advance during the season"
            )
        if previous_capture_date is not None and captured_date <= previous_capture_date:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: qualification capture date did not advance monotonically"
            )

        _validate_completed_premier(state, cycle)
        roster_reference_count = _validate_live_references(state, cycle)

        memberships_before = dict(state.club_competition_membership)
        old_runtime = state.premier_league
        if any(old_runtime is previous for previous in retained_runtimes):
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: Premier League runtime object was unexpectedly reused"
            )
        retained_runtimes.append(old_runtime)

        rng_before = int(controller.match_rng.state) & 0xFFFFFFFF
        regeneration = controller.regenerate_annual_primary_season(
            season_year=int(captured_date.year),
            procedural_league_ids=procedural_league_ids,
        )
        state = controller.state

        if state.premier_league is old_runtime:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: annual regeneration reused the prior Premier League runtime"
            )
        if len(state.premier_league.fixtures) != 380:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: regenerated Premier League does not contain 380 fixtures"
            )
        if state.premier_league.results:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: prior Premier League results survived regeneration"
            )
        if state.prepared_match_environments:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: prepared match environments survived regeneration"
            )
        if int(controller.match_rng.state) != int(regeneration.state_after):
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: controller RNG did not commit regeneration state atomically"
            )
        if dict(state.club_competition_membership) != dict(transition.memberships):
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: annual membership transition did not commit atomically"
            )

        scheduler_ids = _scheduler_fixture_ids(state)
        fixture_ids = tuple(int(value) for value in state.premier_league.fixtures)
        if len(scheduler_ids) != len(set(scheduler_ids)):
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: regenerated Premier League scheduler contains duplicates"
            )
        if set(scheduler_ids) != set(fixture_ids):
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: regenerated scheduler fixture set differs from league"
            )
        if not state.primary_matchday_order:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: regenerated shared primary schedule is empty"
            )

        competitions = tuple(state.competitions.values())
        allocations = tuple(state.cup_allocation_instructions)
        played_sources, _dummy_sources = partition_annual_type3_league_sources(
            competitions,
            allocations,
        )
        live_procedural_ids = {
            int(key[0]) for key in state.procedural_leagues
        }
        missing_played_sources = tuple(
            int(competition_id)
            for competition_id in played_sources
            if int(competition_id) != 0
            and int(competition_id) not in live_procedural_ids
        )
        if missing_played_sources:
            raise CanonicalMultiSeasonAuditError(
                f"cycle {cycle}: regenerated runtime dropped played annual "
                f"qualification sources {missing_played_sources}"
            )

        fresh_shape = _fresh_primary_shape(state)
        _validate_fresh_regeneration_projection(state, regeneration, cycle)
        fresh_shapes.append(fresh_shape)

        membership_changes = sum(
            1
            for club_id, previous_competition_id in memberships_before.items()
            if int(
                transition.memberships.get(club_id, previous_competition_id)
            )
            != int(previous_competition_id)
        )

        snapshots.append(
            CanonicalSeasonRolloverSnapshot(
                cycle=cycle,
                qualification_captured_on=captured_date.isoformat(),
                days_advanced=int(days_advanced),
                completed_premier_results=380,
                membership_changes=membership_changes,
                rng_before_rollover=rng_before,
                rng_after_rollover=int(controller.match_rng.state) & 0xFFFFFFFF,
                rollover_draw_count=int(regeneration.total_draw_count),
                next_season_year=int(regeneration.season_year),
                next_premier_fixture_count=len(state.premier_league.fixtures),
                next_primary_order_days=len(state.primary_matchday_order),
                next_primary_entry_count=fresh_shape[2],
                next_shadow_entry_count=fresh_shape[3],
                next_domestic_node_count=fresh_shape[4],
                next_european_node_count=fresh_shape[5],
                next_qualification_node_count=fresh_shape[6],
                next_procedural_league_count=fresh_shape[7],
                live_roster_reference_count=roster_reference_count,
            )
        )
        previous_capture_date = captured_date

    return {
        "rollover_count": rollover_count,
        "max_days_per_season": max_days_per_season,
        # Backward-compatible first-cycle shape plus the actual per-cycle shapes.
        "fresh_state_shape": list(fresh_shapes[0] if fresh_shapes else ()),
        "fresh_state_shapes": [list(shape) for shape in fresh_shapes],
        "snapshots": [asdict(item) for item in snapshots],
        "final_date": controller.state.calendar.current_date.isoformat(),
        "final_rng_state": int(controller.match_rng.state) & 0xFFFFFFFF,
    }


def run_canonical_multiseason_audit(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    rollover_count: int = 3,
    max_days_per_season: int = 420,
) -> dict:
    controller = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
    )
    report = run_multiseason_controller_audit(
        controller,
        rollover_count=rollover_count,
        max_days_per_season=max_days_per_season,
    )
    report["player_seed"] = int(player_seed)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the canonical Gate-16 multi-season shipped-data audit."
    )
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--rollovers", type=int, default=3)
    parser.add_argument("--max-days-per-season", type=int, default=420)
    args = parser.parse_args()
    report = run_canonical_multiseason_audit(
        args.game_dir,
        player_seed=args.player_seed,
        rollover_count=args.rollovers,
        max_days_per_season=args.max_days_per_season,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
