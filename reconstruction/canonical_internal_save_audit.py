"""Canonical Gate-8 internal save/reload continuation audit.

Creates a real shipped-data human game and verifies deterministic save/reload
continuation. The legacy/default route saves in the middle of a Premier League
matchday. Gate 17 can additionally select a source-backed non-PL
procedural-primary TeamSelect club, save with its first procedural League match
pending, then require exact controller-policy/state/result/RNG equivalence.

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


def _json_primary_entry(entry: tuple | None):
    if entry is None:
        return None
    return [
        _json_primary_entry(value) if isinstance(value, tuple) else value
        for value in entry
    ]


def _live_procedural_primary_scope_targets(
    controller,
    *,
    require_all: bool = False,
) -> tuple[tuple[int, int], ...]:
    """Return one source-selected live club for each procedural-primary scope.

    Competition order follows the controller's source-derived playable-primary
    policy. Club choice follows source-backed TeamSelect/selectable-club order.
    The complete sweep fails closed when any expected competition lacks a live
    root owner or an eligible selectable club.
    """
    competition_ids = tuple(
        int(value) for value in controller.playable_primary_procedural_ids
    )
    if not competition_ids:
        raise RuntimeError("no playable procedural-primary competitions are available")
    allowed_clubs = {
        int(value) for value in controller.playable_primary_club_ids
    }
    selectable = tuple(int(value) for value in controller.selectable_club_ids())
    targets: list[tuple[int, int]] = []
    missing: list[int] = []

    for competition_id in competition_ids:
        owner = controller.state.procedural_leagues.get((competition_id, 0))
        if owner is None:
            missing.append(competition_id)
            continue
        owner_clubs = {int(value) for value in owner.club_ids}
        target = None
        for club_id in selectable:
            if club_id not in allowed_clubs or club_id not in owner_clubs:
                continue
            live_competition = controller.state.club_competition_membership.get(club_id)
            if live_competition is None or int(live_competition) != competition_id:
                continue
            target = (club_id, competition_id)
            break
        if target is None:
            missing.append(competition_id)
            continue
        targets.append(target)

    if require_all and missing:
        raise RuntimeError(
            "missing live TeamSelect procedural-primary scope targets: "
            + ",".join(str(value) for value in missing)
        )
    if not targets:
        raise RuntimeError("no live TeamSelect procedural-primary club is available")
    return tuple(targets)


def _first_live_procedural_primary_club(controller) -> tuple[int, int]:
    """Return the first source-backed TeamSelect club with a live primary owner."""
    return _live_procedural_primary_scope_targets(controller)[0]


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


def run_canonical_primary_scope_internal_save_audit(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    club_id: int | None = None,
    max_matches_before_save: int = 24,
    post_save_matches: int = 3,
    formation_id: int = 0,
) -> dict:
    """Verify save/reload continuation for a shipped non-PL primary career.

    The target club is source-selected from TeamSelect entries whose recovered
    runtime owner is procedural-primary. Earlier human Cup matches are played
    normally until the first procedural League match is pending. The save is
    taken at that pending-match boundary, then both the original and restored
    branches continue through the same shared primary route.
    """
    max_matches_before_save = int(max_matches_before_save)
    post_save_matches = int(post_save_matches)
    if max_matches_before_save <= 0:
        raise ValueError("max_matches_before_save must be positive")
    if post_save_matches <= 0:
        raise ValueError("post_save_matches must be positive")

    game_dir = Path(game_dir)
    original = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
    )

    if club_id is None:
        club_id, competition_id = _first_live_procedural_primary_club(original)
    else:
        club_id = int(club_id)
        competition_id = original.state.club_competition_membership.get(club_id)
        if competition_id is None:
            raise RuntimeError(f"club {club_id} has no live competition membership")
        competition_id = int(competition_id)
        if competition_id not in {
            int(value) for value in original.playable_primary_procedural_ids
        }:
            raise RuntimeError(
                f"club {club_id} is not in a playable procedural-primary League"
            )
        owner = original.state.procedural_leagues.get((competition_id, 0))
        if owner is None or club_id not in {
            int(value) for value in owner.club_ids
        }:
            raise RuntimeError(
                f"club {club_id} has no materialized procedural-primary owner"
            )

    original.select_club(club_id)
    pre_save_matches: list[dict] = []
    pending_entry = None
    for _ in range(max_matches_before_save):
        entry = original.advance_to_next_user_primary_match()
        _require(entry is not None, "ran out of primary matches before League save point")
        original.autofill_lineup(int(formation_id))
        if entry[0] == "procedural_league":
            pending_entry = tuple(entry)
            break
        outcome = original.play_user_primary_match()
        pre_save_matches.append(
            {
                "date": original.state.calendar.current_date.isoformat(),
                "entry": _json_primary_entry(tuple(outcome.match_entry)),
                "score": [int(value) for value in outcome.user_result.score],
            }
        )

    _require(
        pending_entry is not None,
        "no procedural League human match reached within audit bound",
    )
    _require(
        original.pending_primary_entry == pending_entry,
        "controller did not retain the procedural League save boundary",
    )

    save_text = dumps_human_gameplay(original)
    save_bytes = save_text.encode("utf-8")
    compressed = gzip.compress(save_bytes)
    pre_restore_snapshot = snapshot_human_gameplay(original)

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
        "restored non-PL primary snapshot differs immediately after load",
    )
    _require(
        restored.playable_primary_procedural_ids
        == original.playable_primary_procedural_ids,
        "playable primary competition policy changed across reload",
    )
    _require(
        restored.playable_primary_club_ids == original.playable_primary_club_ids,
        "playable primary club policy changed across reload",
    )
    _require(
        restored.playable_country_allocation_plan
        == original.playable_country_allocation_plan,
        "playable annual allocation plan changed across reload",
    )

    continued_matches: list[dict] = []
    for step in range(post_save_matches):
        if step > 0:
            left_entry = original.advance_to_next_user_primary_match()
            right_entry = restored.advance_to_next_user_primary_match()
            _require(
                left_entry is not None and right_entry is not None,
                "continued primary branch ran out of human matches",
            )
            _require(
                tuple(left_entry) == tuple(right_entry),
                "restored branch advanced to a different primary entry",
            )
            original.autofill_lineup(int(formation_id))
            restored.autofill_lineup(int(formation_id))
            _require(
                snapshot_human_gameplay(original)
                == snapshot_human_gameplay(restored),
                "branches diverged while preparing the next primary match",
            )

        left = original.play_user_primary_match()
        right = restored.play_user_primary_match()
        _require(
            left == right,
            "restored branch produced a different primary matchday outcome",
        )
        _require(
            snapshot_human_gameplay(original)
            == snapshot_human_gameplay(restored),
            "non-PL primary snapshots diverged after continued play",
        )
        continued_matches.append(
            {
                "date": original.state.calendar.current_date.isoformat(),
                "entry": _json_primary_entry(tuple(left.match_entry)),
                "score": [int(value) for value in left.user_result.score],
                "match_rng_state": f"0x{int(original.match_rng.state):08X}",
            }
        )

    _require(
        continued_matches
        and continued_matches[0]["entry"][0] == "procedural_league",
        "save continuation did not begin with the targeted procedural League match",
    )
    _require(
        int(original.match_rng.state) == int(restored.match_rng.state),
        "final non-PL primary match RNG states diverged",
    )

    live = original.state.procedural_leagues.get((competition_id, 0))
    _require(live is not None, "controlled procedural League owner disappeared")
    human_row = next(
        row for row in live.table()
        if int(row.club_id) == int(club_id)
    )
    audit = {
        "canonical_files_verified": True,
        "schema_version": int(pre_restore_snapshot["schema_version"]),
        "human_club_id": int(club_id),
        "competition_id": int(competition_id),
        "save_pending_entry": _json_primary_entry(pending_entry),
        "save_prior_primary_results": len(
            pre_restore_snapshot["controller"]["pending_prior_primary_results"]
        ),
        "save_after_primary_entries": list(
            pre_restore_snapshot["controller"]["pending_after_primary_entries"]
        ),
        "save_json_bytes": len(save_bytes),
        "save_gzip_bytes": len(compressed),
        "save_json_sha256": sha256(save_bytes).hexdigest(),
        "source_signature_sha256": pre_restore_snapshot["source"][
            "signature_sha256"
        ],
        "pre_save_matches": pre_save_matches,
        "continued_matches": continued_matches,
        "final_date": original.state.calendar.current_date.isoformat(),
        "human_played": int(human_row.played),
        "human_wins": int(human_row.wins),
        "human_draws": int(human_row.draws),
        "human_losses": int(human_row.losses),
        "human_points": int(human_row.points),
        "playable_primary_procedural_ids": [
            int(value) for value in original.playable_primary_procedural_ids
        ],
        "playable_annual_progression_country_ids": [
            int(value)
            for value in original.playable_annual_progression_country_ids()
        ],
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


def run_canonical_primary_scope_internal_save_sweep(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    max_matches_before_save: int = 24,
    post_save_matches: int = 3,
    formation_id: int = 0,
) -> dict:
    """Run the non-PL save-continuation audit across every live primary scope.

    This is audit tooling, not a claim that private canonical execution has
    occurred. Each competition gets a fresh canonical controller so one scope's
    simulation cannot influence another scope's save/reload proof.
    """
    max_matches_before_save = int(max_matches_before_save)
    post_save_matches = int(post_save_matches)
    if max_matches_before_save <= 0:
        raise ValueError("max_matches_before_save must be positive")
    if post_save_matches <= 0:
        raise ValueError("post_save_matches must be positive")

    game_dir = Path(game_dir)
    discovery = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
    )
    targets = _live_procedural_primary_scope_targets(
        discovery,
        require_all=True,
    )

    audits: list[dict] = []
    for club_id, competition_id in targets:
        result = run_canonical_primary_scope_internal_save_audit(
            game_dir,
            player_seed=int(player_seed),
            club_id=int(club_id),
            max_matches_before_save=max_matches_before_save,
            post_save_matches=post_save_matches,
            formation_id=int(formation_id),
        )
        _require(
            int(result["competition_id"]) == int(competition_id),
            "scope audit returned a different procedural-primary competition",
        )
        _require(
            int(result["human_club_id"]) == int(club_id),
            "scope audit returned a different TeamSelect club",
        )
        audits.append(result)

    expected_ids = [
        int(value) for value in discovery.playable_primary_procedural_ids
    ]
    verified_ids = [int(result["competition_id"]) for result in audits]
    _require(
        verified_ids == expected_ids,
        "procedural-primary save sweep did not preserve exact source scope order",
    )

    audit = {
        "canonical_files_verified": True,
        "player_seed": int(player_seed),
        "procedural_primary_scope_count": len(expected_ids),
        "verified_competition_ids": verified_ids,
        "target_club_ids": [int(result["human_club_id"]) for result in audits],
        "missing_competition_ids": [],
        "failed_competition_ids": [],
        "scope_audits": audits,
        "all_primary_scopes_save_reload_equal": True,
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--procedural-primary",
        action="store_true",
        help="audit one source-selected non-PL procedural-primary TeamSelect career",
    )
    mode.add_argument(
        "--procedural-primary-all",
        action="store_true",
        help="audit every live procedural-primary TeamSelect competition",
    )
    parser.add_argument("--max-before-save", type=int, default=24)
    args = parser.parse_args()
    if args.procedural_primary_all:
        if args.club_id != 0:
            parser.error("--club-id cannot be combined with --procedural-primary-all")
        audit = run_canonical_primary_scope_internal_save_sweep(
            args.game_dir,
            player_seed=args.player_seed,
            max_matches_before_save=args.max_before_save,
            post_save_matches=args.post_save_fixtures,
            formation_id=args.formation,
        )
    elif args.procedural_primary:
        audit = run_canonical_primary_scope_internal_save_audit(
            args.game_dir,
            player_seed=args.player_seed,
            club_id=None if args.club_id == 0 else args.club_id,
            max_matches_before_save=args.max_before_save,
            post_save_matches=args.post_save_fixtures,
            formation_id=args.formation,
        )
    else:
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
