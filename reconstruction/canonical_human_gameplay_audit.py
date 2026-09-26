"""Canonical shipped-data human-manager gameplay audit.

This runner exercises Gate 7 without committing original FM2001 assets. It
creates the same canonical scheduler/match backend used by Gates 5/6, takes
control of one Premier League club, auto-fills a legal human XI/bench through
the proven selection core, advances in exact scheduler order, and plays several
human fixtures through the shared human-vs-AI backend.

Usage:
    PYTHONPATH=reconstruction python reconstruction/canonical_human_gameplay_audit.py /path/to/game
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from human_gameplay import HumanGameplayController


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_canonical_human_gameplay_audit(
    game_dir: str | Path,
    *,
    fixtures_to_play: int = 3,
    player_seed: int = 1,
    club_id: int | None = None,
    formation_id: int = 0,
) -> dict:
    fixtures_to_play = int(fixtures_to_play)
    if fixtures_to_play <= 0:
        raise ValueError("fixtures_to_play must be positive")

    controller = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
    )
    league = controller.state.premier_league

    if club_id is None:
        club_id = int(league.club_ids[0])
    club_id = int(club_id)
    controller.select_club(club_id)

    fixture_audits: list[dict] = []
    previous_result_count = len(league.results)

    for _ in range(fixtures_to_play):
        selection = controller.autofill_lineup(int(formation_id))
        _require(
            len(selection.lineup.starters) == 11,
            "canonical human autofill did not produce 11 starters",
        )
        _require(
            len(selection.lineup.substitutes) == 5,
            "canonical human autofill did not produce five substitutes",
        )
        _require(
            all(
                not player.base_match_unavailable
                for player in selection.participants
            ),
            "canonical human selection contains an unavailable player",
        )

        results_before_matchday = len(league.results)
        fixture = controller.advance_to_next_user_fixture()
        _require(fixture is not None, "no remaining human Premier League fixture")
        _require(
            club_id in (
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            ),
            "pending fixture does not contain the human club",
        )

        fixture_date = controller.state.calendar.current_date
        pending_id = int(fixture.id)
        outcome = controller.play_user_fixture()
        after_matchday = len(league.results)

        _require(
            int(outcome.fixture_id) == pending_id,
            "human outcome fixture ID changed",
        )
        _require(
            len(outcome.matchday_results) == 10,
            "canonical Premier League matchday did not contain 10 matches",
        )
        _require(
            after_matchday - results_before_matchday == 10,
            "stored result count did not advance by one complete matchday",
        )

        matchday_fixtures = tuple(
            league.fixtures[int(fixture_id)]
            for fixture_id, _ in outcome.matchday_results
        )
        clubs = [
            int(team_id)
            for match_fixture in matchday_fixtures
            for team_id in (
                match_fixture.home_club_id,
                match_fixture.away_club_id,
            )
        ]
        counts = Counter(clubs)
        _require(
            len(clubs) == 20
            and len(counts) == 20
            and all(value == 1 for value in counts.values()),
            "canonical human matchday does not contain all 20 PL clubs once",
        )

        table_row = next(
            row for row in outcome.table
            if int(row.club_id) == club_id
        )
        score = outcome.user_result.score
        fixture_audits.append(
            {
                "date": fixture_date.isoformat(),
                "fixture_id": pending_id,
                "home_club_id": int(fixture.home_club_id),
                "away_club_id": int(fixture.away_club_id),
                "score": [int(score[0]), int(score[1])],
                "matchday_order": [
                    int(fixture_id)
                    for fixture_id, _ in outcome.matchday_results
                ],
                "human_played": int(table_row.played),
                "human_points": int(table_row.points),
                "rng_state_after": int(controller.match_rng.state),
            }
        )

    _require(
        len(league.results) - previous_result_count == fixtures_to_play * 10,
        "canonical human run did not complete exactly one full PL matchday per fixture",
    )
    _require(
        all(
            0 <= int(player.condition) <= 100
            for player in controller.squad()
        ),
        "human squad Condition escaped 0..100",
    )
    _require(
        all(
            0 <= int(player.form_state) <= 4
            for player in controller.squad()
        ),
        "human squad Form escaped 0..4",
    )

    table = controller.state.premier_league_table()
    human_row = next(row for row in table if int(row.club_id) == club_id)
    audit = {
        "canonical_files_verified": True,
        "human_club_id": club_id,
        "fixtures_played": fixtures_to_play,
        "formation_id": int(formation_id),
        "fixtures": fixture_audits,
        "stored_result_count": len(league.results),
        "human_played": int(human_row.played),
        "human_wins": int(human_row.wins),
        "human_draws": int(human_row.draws),
        "human_losses": int(human_row.losses),
        "human_points": int(human_row.points),
        "human_goal_difference": int(human_row.goal_difference),
        "human_condition_min": min(
            int(player.condition)
            for player in controller.squad()
        ),
        "human_condition_max": max(
            int(player.condition)
            for player in controller.squad()
        ),
        "human_injured_count": sum(
            bool(player.injured)
            for player in controller.squad()
        ),
        "human_suspended_count": sum(
            bool(player.suspended)
            for player in controller.squad()
        ),
        "match_rng_final_state": f"0x{int(controller.match_rng.state):08X}",
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
    parser.add_argument("--fixtures", type=int, default=3)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--club-id", type=int)
    parser.add_argument("--formation", type=int, default=0)
    args = parser.parse_args()

    audit = run_canonical_human_gameplay_audit(
        args.game_dir,
        fixtures_to_play=args.fixtures,
        player_seed=args.player_seed,
        club_id=args.club_id,
        formation_id=args.formation,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
