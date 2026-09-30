"""Canonical Gate-12 annual qualification and rollover audit.

This command requires the user's authorized original FM2001 game directory.
It never substitutes historical qualification state. The season is advanced
only through GameState's shared primary AI scheduler. If a dynamic FA Cup
Replay reaches its due date before the exact 0x615A60 primary insertion order
has been recovered, the scheduler raises the explicit fidelity blocker rather
than silently skipping that match.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from human_gameplay import HumanGameplayController
from match_schedule import MsvcCrtRng
from season_regeneration import (
    capture_annual_type3_qualification_snapshot,
    finalize_annual_dummy_league_rankings,
    partition_annual_type3_league_sources,
    required_annual_type3_sources,
)


def _ordered_live_players(state) -> tuple[object, ...]:
    ordered: list[object] = []
    seen: set[int] = set()
    for club_id in state.clubs:
        for player_id in state.club_roster_order.get(int(club_id), ()):
            player_id = int(player_id)
            player = state.players.get(player_id)
            if player is None or player_id in seen:
                continue
            ordered.append(player)
            seen.add(player_id)
    for player_id, player in state.players.items():
        player_id = int(player_id)
        if player_id not in seen:
            ordered.append(player)
            seen.add(player_id)
    return tuple(ordered)


def _qualification_if_complete(controller: HumanGameplayController):
    state = controller.state
    competitions = tuple(state.competitions.values())
    allocations = tuple(state.cup_allocation_instructions)
    played_sources, _dummy_sources = partition_annual_type3_league_sources(
        competitions,
        allocations,
    )
    missing_played = tuple(
        int(competition_id)
        for competition_id in played_sources
        if (int(competition_id), 0) not in state.cup_results.competition_rankings
    )
    if missing_played:
        raise RuntimeError(
            "annual type-3 live played-League qualification rankings are "
            f"unresolved for {missing_played}"
        )

    trial_rng = MsvcCrtRng(int(controller.match_rng.state))
    dummy_rankings = finalize_annual_dummy_league_rankings(
        trial_rng,
        competitions,
        tuple(state.countries.values()),
        tuple(state.clubs.values()),
        _ordered_live_players(state),
        state.club_competition_membership,
    )
    qualification = capture_annual_type3_qualification_snapshot(
        state,
        competitions,
        allocations,
        ranking_overrides=dummy_rankings,
    )
    transition = state.preview_english_season_transition(
        ranking_overrides=dummy_rankings,
    )
    return qualification, transition, int(trial_rng.state)


def run_canonical_annual_rollover_audit(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    max_days: int = 420,
) -> dict:
    """Finish the canonical live season and atomically install the next one."""

    controller = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
    )
    state = controller.state
    competitions = tuple(state.competitions.values())
    allocations = tuple(state.cup_allocation_instructions)
    required_leagues, required_cups = required_annual_type3_sources(
        competitions,
        allocations,
    )
    played_sources, dummy_sources = partition_annual_type3_league_sources(
        competitions,
        allocations,
    )

    qualification = None
    transition = None
    last_qualification_error = None
    last_transition_error = None
    days_advanced = 0

    for days_advanced in range(int(max_days) + 1):
        try:
            qualification, transition, _preview_finalized_rng = (
                _qualification_if_complete(controller)
            )
        except RuntimeError as exc:
            message = str(exc)
            if "season transition ranking is unresolved" in message:
                last_transition_error = message
            else:
                last_qualification_error = message
        else:
            last_qualification_error = None
            last_transition_error = None
            break

        if days_advanced == int(max_days):
            raise RuntimeError(
                "canonical annual qualification did not complete within "
                f"{int(max_days)} days; qualification={last_qualification_error!r}; "
                f"transition={last_transition_error!r}"
            )

        state.advance_one_day_with_primary_ai_matches(
            controller.attack_matrix,
            controller.defence_matrix,
            controller.match_rng,
        )
    else:  # pragma: no cover - loop exits by break or explicit error
        raise AssertionError("unreachable annual audit loop state")

    if qualification is None or transition is None:
        raise AssertionError("annual qualification readiness was not captured")

    captured_date = state.calendar.current_date
    rng_before_rollover = int(controller.match_rng.state)
    memberships_before = dict(state.club_competition_membership)
    old_premier = state.premier_league
    if old_premier is None:
        raise RuntimeError("canonical Premier League runtime disappeared before rollover")

    regeneration = controller.regenerate_annual_primary_season(
        season_year=int(captured_date.year),
    )

    if controller.state.premier_league is old_premier:
        raise AssertionError("annual rollover did not replace Premier League state")
    if controller.state.premier_league.results:
        raise AssertionError("new Premier League already contains results")
    if not controller.state.primary_matchday_order:
        raise AssertionError("new primary scheduler order is empty")
    if int(controller.match_rng.state) != int(regeneration.state_after):
        raise AssertionError("controller CRT state did not commit with regeneration")
    if dict(controller.state.club_competition_membership) != dict(
        transition.memberships
    ):
        raise AssertionError("annual membership transition did not commit atomically")

    live_procedural_ids = {
        int(competition_id)
        for competition_id, _context in controller.state.procedural_leagues
    }
    missing_played_sources = tuple(
        int(competition_id)
        for competition_id in played_sources
        if int(competition_id) != 0
        and int(competition_id) not in live_procedural_ids
    )
    if missing_played_sources:
        raise AssertionError(
            "year-two runtime dropped played annual qualification sources "
            f"{missing_played_sources}"
        )

    return {
        "player_seed": int(player_seed),
        "days_advanced": int(days_advanced),
        "qualification_captured_on": captured_date.isoformat(),
        "required_league_sources": [int(value) for value in required_leagues],
        "played_league_sources": [int(value) for value in played_sources],
        "dummy_league_sources": [int(value) for value in dummy_sources],
        "required_cup_sources": [int(value) for value in required_cups],
        "captured_ranking_sources": sorted(
            int(value)
            for value in qualification.qualification_rankings_by_competition
        ),
        "captured_cup_sources": sorted(
            int(value)
            for value in qualification.cup_enumerated_club_ids_by_source
        ),
        "membership_changes": sum(
            1
            for club_id, old_competition_id in memberships_before.items()
            if int(transition.memberships.get(club_id, old_competition_id))
            != int(old_competition_id)
        ),
        "rollover_season_year": int(regeneration.season_year),
        "rollover_rng_before": rng_before_rollover,
        "rollover_rng_after": int(controller.match_rng.state),
        "rollover_total_draw_count": int(regeneration.total_draw_count),
        "year_two_primary_order_days": len(controller.state.primary_matchday_order),
        "year_two_premier_fixture_count": len(
            controller.state.premier_league.fixtures
        ),
        "year_two_live_procedural_ids": sorted(live_procedural_ids),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the canonical Gate-12 annual rollover audit."
    )
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--max-days", type=int, default=420)
    args = parser.parse_args()
    report = run_canonical_annual_rollover_audit(
        args.game_dir,
        player_seed=args.player_seed,
        max_days=args.max_days,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
