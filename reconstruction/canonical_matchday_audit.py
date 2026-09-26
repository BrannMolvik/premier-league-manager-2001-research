"""Canonical real-data Premier League matchday integration audit.

This tool intentionally requires the authorized FM2001 shipped files outside
Git. It verifies those files, reconstructs the exact Gate-3/4 scheduler order,
installs that order into GameState, then executes consecutive real Premier
League matchdays through the autonomous AI match path.

Usage:
    PYTHONPATH=reconstruction python reconstruction/canonical_matchday_audit.py /path/to/game
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from competition_materializer import materialize_primary_rng_driven_schedule
from fm2001_data import FM2001Database
from game_state import GameState
from match_coefficients import MatchCoefficientMatrices
from match_schedule import MsvcCrtRng
from primary_schedule import (
    fixed_league_fixture_order_by_round,
    place_primary_schedule_nodes,
    shuffle_primary_schedule_buckets,
)
from verify import verify_canonical_files


COMPETITION_START_STATE = 0x2797444C
EXPECTED_PRE_SHUFFLE_STATE = 0x0E556598
EXPECTED_PRIMARY_SCHEDULE_SHA256 = (
    "0a22c9f0c1fa20de770a7d679583b6b4e4bdbd9363a5bda07194bfe8919cc35a"
)
EXPECTED_PRIMARY_SHUFFLE_DRAWS = 9178
EXPECTED_PRIMARY_SHUFFLE_FINAL_STATE = 0x839953AA
EXPECTED_BUCKET_COUNT_SHA256 = (
    "fce6003d6a415813c08d3b55152ae6bf3da3fb9f68eef3bf4c0666e1df67718b"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def reconstruct_canonical_pl_scheduler_order(database: FM2001Database):
    """Return exact PL fixture order by round plus the final shuffle state."""

    competition = materialize_primary_rng_driven_schedule(
        MsvcCrtRng(COMPETITION_START_STATE),
        database.competitions,
        database.rounds,
        database.clubs,
        database.countries,
        database.cup_allocation_instructions,
        database.players,
        real_fixtures=database.real_fixtures,
    )
    _require(
        competition.schedule_node_count == 9346,
        f"expected 9346 primary nodes, got {competition.schedule_node_count}",
    )
    _require(
        competition.schedule_sha256 == EXPECTED_PRIMARY_SCHEDULE_SHA256,
        "primary schedule-node digest does not match Gate 3",
    )
    _require(
        competition.state_entering_primary_shuffle == EXPECTED_PRE_SHUFFLE_STATE,
        "primary schedule-shuffle input state does not match Gate 3",
    )

    placement = place_primary_schedule_nodes(competition.schedule_nodes)
    counts = [len(bucket) for bucket in placement.buckets]
    count_digest = sha256(
        json.dumps(counts, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    _require(
        count_digest == EXPECTED_BUCKET_COUNT_SHA256,
        f"primary bucket-count digest mismatch: {count_digest}",
    )

    shuffle_rng = MsvcCrtRng(competition.state_entering_primary_shuffle)
    shuffled = shuffle_primary_schedule_buckets(
        placement.buckets,
        shuffle_rng,
    )
    _require(
        shuffled.draw_count == EXPECTED_PRIMARY_SHUFFLE_DRAWS,
        f"expected {EXPECTED_PRIMARY_SHUFFLE_DRAWS} bucket draws, got {shuffled.draw_count}",
    )
    _require(
        shuffled.state_after == EXPECTED_PRIMARY_SHUFFLE_FINAL_STATE,
        (
            "primary schedule final state mismatch: "
            f"0x{int(shuffled.state_after or 0):08X}"
        ),
    )

    order = fixed_league_fixture_order_by_round(
        shuffled.buckets,
        competition_id=0,
    )
    _require(len(order) == 38, f"expected 38 PL round orders, got {len(order)}")
    return order, int(shuffled.state_after)


def run_canonical_matchday_audit(
    game_dir: str | Path,
    *,
    rounds_to_run: int = 3,
    player_seed: int = 1,
) -> dict:
    """Run consecutive real PL rounds and return a deterministic audit."""

    game_dir = Path(game_dir)
    rounds_to_run = int(rounds_to_run)
    if rounds_to_run <= 0:
        raise ValueError("rounds_to_run must be positive")

    verify_canonical_files(game_dir)
    database = FM2001Database(game_dir)
    matrices = MatchCoefficientMatrices.from_executable(game_dir / "FOOTBAL.EXE")

    scheduler_order, post_schedule_state = reconstruct_canonical_pl_scheduler_order(
        database
    )
    scheduler_by_round = dict(scheduler_order)

    state = GameState.from_database(
        database,
        date(2000, 8, 18),
        seed=int(player_seed),
        season_year=2000,
    )
    state.install_premier_league_scheduler_order(scheduler_order)

    # This audit deliberately starts autonomous match RNG at the exact Gate-4
    # primary-schedule completion checkpoint. Runtime-player initialization is
    # independently deterministic under player_seed; the purpose here is
    # cross-system integration, not claiming one historical user-save seed.
    match_rng = MsvcCrtRng(post_schedule_state)

    round_audits: list[dict] = []
    days_advanced = 0
    while len(round_audits) < rounds_to_run:
        days_advanced += 1
        if days_advanced > 366:
            raise RuntimeError("failed to reach requested PL rounds within one year")

        results = state.advance_one_day_with_premier_league_ai_fixtures(
            matrices.attack,
            matrices.defence,
            match_rng,
        )
        if not results:
            continue

        fixture_ids = tuple(int(fixture_id) for fixture_id, _ in results)
        fixtures = tuple(
            state.premier_league.fixtures[fixture_id]
            for fixture_id in fixture_ids
        )
        round_ids = {int(fixture.round_index) for fixture in fixtures}
        _require(
            len(round_ids) == 1,
            f"one matchday unexpectedly contained PL rounds {sorted(round_ids)}",
        )
        round_id = next(iter(round_ids))
        _require(
            len(results) == 10,
            f"PL round {round_id} produced {len(results)} matches, expected 10",
        )
        _require(
            fixture_ids == scheduler_by_round[round_id],
            (
                f"PL round {round_id} execution order diverged: "
                f"{fixture_ids} != {scheduler_by_round[round_id]}"
            ),
        )

        club_ids = [
            club_id
            for fixture in fixtures
            for club_id in (
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            )
        ]
        counts = Counter(club_ids)
        _require(
            len(club_ids) == 20
            and len(counts) == 20
            and all(value == 1 for value in counts.values()),
            f"PL round {round_id} does not contain all 20 clubs exactly once",
        )

        round_audits.append(
            {
                "date": state.calendar.current_date.isoformat(),
                "round_index": round_id,
                "fixture_order": list(fixture_ids),
                "scores": [
                    [int(fixture_id), int(result.score[0]), int(result.score[1])]
                    for fixture_id, result in results
                ],
                "stored_result_count": len(state.premier_league.results),
                "injured_player_count": sum(
                    bool(player.injured)
                    for player in state.players.values()
                ),
                "suspended_player_count": sum(
                    bool(player.suspended)
                    for player in state.players.values()
                ),
                "rng_state_after": int(match_rng.state),
            }
        )

    table = state.premier_league_table()
    _require(len(table) == 20, f"expected 20 PL table rows, got {len(table)}")
    _require(
        len(state.premier_league.results) == rounds_to_run * 10,
        "stored PL result count does not match completed rounds",
    )
    _require(
        sum(row.played for row in table) == rounds_to_run * 20,
        "league-table played total does not reconcile",
    )
    _require(
        all(row.played == rounds_to_run for row in table),
        "not every PL club has the expected played count",
    )
    _require(
        sum(row.goals_for for row in table)
        == sum(row.goals_against for row in table),
        "league-table goals for/against do not reconcile",
    )

    pl_club_ids = set(state.premier_league.club_ids)
    pl_players = [
        player
        for club_id in pl_club_ids
        for player in state.ordered_club_roster(club_id)
    ]
    _require(
        len({player.index for player in pl_players}) == len(pl_players),
        "a PL runtime player appears in more than one club roster",
    )

    selection_issues = []
    for club_id in sorted(pl_club_ids):
        roster = state.ordered_club_roster(club_id)
        active = {player.index for player in roster if player.match_active}
        substitutes = {
            player.index
            for player in roster
            if player.match_substitute_available
        }
        if len(active) != 11 or len(substitutes) != 5 or active & substitutes:
            selection_issues.append(
                [club_id, len(active), len(substitutes), sorted(active & substitutes)]
            )
    _require(not selection_issues, f"invalid persisted PL selections: {selection_issues}")

    _require(
        all(0 <= int(player.condition) <= 100 for player in pl_players),
        "PL player Condition escaped 0..100",
    )
    _require(
        all(0 <= int(player.form_state) <= 4 for player in pl_players),
        "PL player Form state escaped 0..4",
    )
    _require(
        all(
            not player.injured or player.injury_return_date is not None
            for player in pl_players
        ),
        "an injured PL player has no return date",
    )
    _require(
        all(
            int(player.suspension_matches_remaining) >= 0
            for player in pl_players
        ),
        "a PL player has negative suspension matches remaining",
    )

    score_goal_total = sum(
        result.home_goals + result.away_goals
        for result in state.premier_league.results.values()
    )
    table_goal_total = sum(row.goals_for for row in table)
    _require(
        score_goal_total == table_goal_total,
        "stored result goals do not match league table",
    )

    audit = {
        "canonical_files_verified": True,
        "rounds_completed": rounds_to_run,
        "days_advanced": days_advanced,
        "scheduler_final_state": f"0x{post_schedule_state:08X}",
        "match_rng_final_state": f"0x{int(match_rng.state):08X}",
        "rounds": round_audits,
        "stored_result_count": len(state.premier_league.results),
        "table_played_total": sum(row.played for row in table),
        "table_goal_total": table_goal_total,
        "prepared_environment_count": len(state.prepared_match_environments),
        "pitch_wear_nonzero_club_count": sum(
            int(value) != 0
            for value in state.pitch_wear.values()
        ),
        "pl_player_count": len(pl_players),
        "condition_min": min(player.condition for player in pl_players),
        "condition_max": max(player.condition for player in pl_players),
        "injured_player_count": sum(
            bool(player.injured)
            for player in pl_players
        ),
        "suspended_player_count": sum(
            bool(player.suspended)
            for player in pl_players
        ),
        "yellow_total": sum(
            int(player.discipline_yellow_total)
            for player in pl_players
        ),
    }

    digest_payload = json.dumps(
        audit,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    audit["audit_sha256"] = sha256(digest_payload).hexdigest()
    return audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--player-seed", type=int, default=1)
    args = parser.parse_args()

    audit = run_canonical_matchday_audit(
        args.game_dir,
        rounds_to_run=args.rounds,
        player_seed=args.player_seed,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
