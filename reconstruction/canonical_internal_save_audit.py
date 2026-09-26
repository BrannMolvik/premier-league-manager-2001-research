"""Canonical Gate-8 internal save/reload continuation audit.

Creates a real shipped-data human game, saves in the middle of a Premier League
matchday before the human fixture, restores into a fresh runtime, then advances
both branches through the remaining audited fixtures and requires exact
state/result/RNG equivalence.

Usage:
    PYTHONPATH=reconstruction python reconstruction/canonical_internal_save_audit.py /path/to/game
"""

from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path

from fm2001_data import FM2001Database
from human_gameplay import HumanGameplayController
from internal_save import dumps_human_gameplay, loads_human_gameplay, snapshot_human_gameplay
from match_coefficients import MatchCoefficientMatrices


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_canonical_internal_save_audit(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    club_id: int = 0,
    pre_save_fixtures: int = 2,
    post_save_fixtures: int = 4,
    formation_id: int = 0,
) -> dict:
    game_dir = Path(game_dir)
    original = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
    )
    original.select_club(int(club_id))

    pre_save_audit = []
    for _ in range(int(pre_save_fixtures)):
        original.autofill_lineup(int(formation_id))
        fixture = original.advance_to_next_user_fixture()
        _require(fixture is not None, "ran out of human fixtures before save")
        outcome = original.play_user_fixture()
        pre_save_audit.append(
            {
                "date": original.state.calendar.current_date.isoformat(),
                "fixture_id": int(outcome.fixture_id),
                "score": [int(v) for v in outcome.user_result.score],
            }
        )

    # Save at the harder boundary: earlier AI fixtures on the date have already
    # run but the human fixture and later same-day AI fixtures are still pending.
    original.autofill_lineup(int(formation_id))
    pending_fixture = original.advance_to_next_user_fixture()
    _require(pending_fixture is not None, "no pending human fixture at save point")
    _require(
        original.pending_fixture_id is not None,
        "controller did not stop before human fixture",
    )

    save_text = dumps_human_gameplay(original)
    save_bytes = save_text.encode("utf-8")
    compressed = gzip.compress(save_bytes)
    pre_restore_snapshot = snapshot_human_gameplay(original)

    # Restore from fresh source/database objects, not shared references from the
    # original controller.
    database = FM2001Database(game_dir)
    matrices = MatchCoefficientMatrices.from_executable(game_dir / "FOOTBAL.EXE")
    restored = loads_human_gameplay(
        database,
        matrices.attack,
        matrices.defence,
        save_text,
    )
    _require(
        snapshot_human_gameplay(restored) == pre_restore_snapshot,
        "restored snapshot differs immediately after load",
    )

    branch_audit = []
    for step in range(int(post_save_fixtures)):
        if step > 0:
            original.autofill_lineup(int(formation_id))
            restored.autofill_lineup(int(formation_id))
            left_fixture = original.advance_to_next_user_fixture()
            right_fixture = restored.advance_to_next_user_fixture()
            _require(
                left_fixture is not None and right_fixture is not None,
                "branch ran out of fixtures",
            )
            _require(
                int(left_fixture.id) == int(right_fixture.id),
                "restored branch advanced to a different fixture",
            )

        left = original.play_user_fixture()
        right = restored.play_user_fixture()
        _require(
            left == right,
            "restored branch produced a different matchday outcome",
        )
        _require(
            snapshot_human_gameplay(original)
            == snapshot_human_gameplay(restored),
            "runtime snapshots diverged after continued play",
        )
        branch_audit.append(
            {
                "date": original.state.calendar.current_date.isoformat(),
                "fixture_id": int(left.fixture_id),
                "score": [int(v) for v in left.user_result.score],
                "stored_results": len(original.state.premier_league.results),
                "match_rng_state": f"0x{int(original.match_rng.state):08X}",
            }
        )

    human_row = next(
        row
        for row in original.state.premier_league_table()
        if int(row.club_id) == int(club_id)
    )
    _require(
        len(original.state.premier_league.results)
        == len(restored.state.premier_league.results),
        "final stored-result counts diverged",
    )
    _require(
        int(original.match_rng.state) == int(restored.match_rng.state),
        "final match RNG states diverged",
    )

    audit = {
        "canonical_files_verified": True,
        "schema_version": int(pre_restore_snapshot["schema_version"]),
        "human_club_id": int(club_id),
        "pre_save_fixtures": int(pre_save_fixtures),
        "post_save_fixtures": int(post_save_fixtures),
        "save_date": original.state.premier_league.round_date(
            int(pending_fixture.round_index)
        ).isoformat(),
        "save_pending_fixture_id": int(pending_fixture.id),
        "save_prior_same_day_results": len(
            pre_restore_snapshot["controller"]["pending_prior_results"]
        ),
        "save_after_same_day_fixture_ids": [
            int(v)
            for v in pre_restore_snapshot["controller"]["pending_after_fixture_ids"]
        ],
        "save_json_bytes": len(save_bytes),
        "save_gzip_bytes": len(compressed),
        "save_json_sha256": sha256(save_bytes).hexdigest(),
        "source_signature_sha256": pre_restore_snapshot["source"][
            "signature_sha256"
        ],
        "pre_save_matches": pre_save_audit,
        "continued_matches": branch_audit,
        "final_date": original.state.calendar.current_date.isoformat(),
        "final_stored_results": len(original.state.premier_league.results),
        "human_played": int(human_row.played),
        "human_wins": int(human_row.wins),
        "human_draws": int(human_row.draws),
        "human_losses": int(human_row.losses),
        "human_points": int(human_row.points),
        "match_rng_final_state": f"0x{int(original.match_rng.state):08X}",
        "branches_equal": True,
    }
    payload = json.dumps(
        audit,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    audit["audit_sha256"] = sha256(payload).hexdigest()
    return audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--club-id", type=int, default=0)
    parser.add_argument("--pre-save-fixtures", type=int, default=2)
    parser.add_argument("--post-save-fixtures", type=int, default=4)
    parser.add_argument("--formation", type=int, default=0)
    args = parser.parse_args()
    audit = run_canonical_internal_save_audit(
        args.game_dir,
        player_seed=args.player_seed,
        club_id=args.club_id,
        pre_save_fixtures=args.pre_save_fixtures,
        post_save_fixtures=args.post_save_fixtures,
        formation_id=args.formation,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
