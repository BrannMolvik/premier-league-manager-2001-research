"""Create fail-closed Gate-17 gameplay receipts on the Windows release candidate.

This runner deliberately creates only the three gameplay receipts that can be
proved by the reconstructed runtime itself:

- new_game_management_loop
- save_reload
- season_progression

The clean_windows_install receipt is intentionally not created here. That fact
must come from the separate installed-release procedure, outside the
development/source environment.

Every receipt is bound to one repository commit, release version and exact
release-archive SHA-256 so final Gate-17 evidence cannot mix source-tree tests
with a different shipped artifact.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile

from canonical_annual_rollover_audit import run_canonical_annual_rollover_audit
from fm2001_data import FM2001Database
from human_gameplay import HumanGameplayController
from gate17_release_readiness import require_windows_11
from internal_save import (
    load_human_gameplay,
    save_human_gameplay,
    snapshot_human_gameplay,
)


class WindowsGameplayReceiptError(RuntimeError):
    """Release gameplay evidence could not be produced faithfully."""


@dataclass(frozen=True)
class ReleaseArtifactIdentity:
    release_version: str
    repository_commit: str
    release_archive_sha256: str
    release_archive_size: int


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_release_artifact_identity(
    *,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
) -> ReleaseArtifactIdentity:
    release_version = str(release_version).strip()
    if not release_version:
        raise WindowsGameplayReceiptError("release_version must be non-empty")
    repository_commit = str(repository_commit)
    if re.fullmatch(r"[0-9a-f]{40}", repository_commit) is None:
        raise WindowsGameplayReceiptError(
            "repository_commit must be a lowercase 40-character Git SHA"
        )
    archive = Path(release_archive).resolve()
    if not archive.is_file():
        raise WindowsGameplayReceiptError(
            f"release archive does not exist: {archive}"
        )
    size = archive.stat().st_size
    if size <= 0:
        raise WindowsGameplayReceiptError("release archive is empty")
    return ReleaseArtifactIdentity(
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive_sha256=_sha256_file(archive),
        release_archive_size=int(size),
    )


def _first_premier_club_id(controller) -> int:
    league = controller.state.premier_league
    if league is None or not league.club_ids:
        raise WindowsGameplayReceiptError(
            "canonical runtime has no Premier League clubs"
        )
    return int(league.club_ids[0])


def audit_new_game_management_loop(controller) -> dict:
    club_id = _first_premier_club_id(controller)
    controller.select_club(club_id)
    selection = controller.autofill_lineup(0)
    if len(selection.lineup.starters) != 11:
        raise WindowsGameplayReceiptError("autofill did not produce an XI")
    if len(selection.lineup.substitutes) != 5:
        raise WindowsGameplayReceiptError(
            "autofill did not produce five substitutes"
        )

    fixture = controller.advance_to_next_user_fixture()
    if fixture is None:
        raise WindowsGameplayReceiptError(
            "new game has no reachable Premier League user fixture"
        )
    fixture_id = int(fixture.id)
    outcome = controller.play_user_fixture()
    if int(outcome.fixture_id) != fixture_id:
        raise WindowsGameplayReceiptError(
            "played fixture differs from the pending user fixture"
        )
    if controller.pending_fixture_id is not None:
        raise WindowsGameplayReceiptError(
            "management loop left the played fixture pending"
        )
    if fixture_id not in controller.state.premier_league.results:
        raise WindowsGameplayReceiptError(
            "played user fixture was not persisted to the league"
        )

    return {
        "new_game": True,
        "management_loop": True,
        "selected_club_id": club_id,
        "formation_id": 0,
        "starter_count": len(selection.lineup.starters),
        "substitute_count": len(selection.lineup.substitutes),
        "played_fixture_id": fixture_id,
        "matchday_result_count": len(outcome.matchday_results),
        "current_date": controller.state.calendar.current_date.isoformat(),
    }


def audit_save_reload(game_dir: str | Path, controller) -> dict:
    club_id = _first_premier_club_id(controller)
    controller.select_club(club_id)
    controller.autofill_lineup(0)
    fixture = controller.advance_to_next_user_fixture()
    if fixture is None:
        raise WindowsGameplayReceiptError(
            "save/reload audit could not reach a user fixture"
        )
    controller.play_user_fixture()
    expected = snapshot_human_gameplay(controller)

    database = FM2001Database(game_dir)
    with tempfile.TemporaryDirectory(prefix="fm2001-gate17-save-") as temp:
        save_path = Path(temp) / "gate17-smoke.fm2k"
        save_human_gameplay(controller, save_path)
        if not save_path.is_file() or save_path.stat().st_size <= 0:
            raise WindowsGameplayReceiptError(
                "save/reload audit did not create a non-empty save"
            )
        restored = load_human_gameplay(
            database,
            controller.attack_matrix,
            controller.defence_matrix,
            save_path,
        )
    actual = snapshot_human_gameplay(restored)
    if actual != expected:
        raise WindowsGameplayReceiptError(
            "save/reload audit did not restore the exact gameplay snapshot"
        )
    return {
        "save_reload": True,
        "selected_club_id": club_id,
        "schema_version": int(expected["schema_version"]),
        "restored_date": restored.state.calendar.current_date.isoformat(),
        "restored_result_count": len(restored.state.premier_league.results),
    }


def audit_season_progression(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    max_days: int = 420,
) -> dict:
    report = run_canonical_annual_rollover_audit(
        game_dir,
        player_seed=int(player_seed),
        max_days=int(max_days),
    )
    if int(report.get("year_two_premier_fixture_count", 0)) != 380:
        raise WindowsGameplayReceiptError(
            "annual rollover did not install a complete year-two Premier League"
        )
    if int(report.get("days_advanced", 0)) <= 0:
        raise WindowsGameplayReceiptError(
            "annual rollover did not advance a live season"
        )
    return {
        "season_progression": True,
        "player_seed": int(report["player_seed"]),
        "days_advanced": int(report["days_advanced"]),
        "qualification_captured_on": str(report["qualification_captured_on"]),
        "rollover_season_year": int(report["rollover_season_year"]),
        "year_two_premier_fixture_count": int(
            report["year_two_premier_fixture_count"]
        ),
        "year_two_primary_order_days": int(
            report["year_two_primary_order_days"]
        ),
        "rollover_total_draw_count": int(report["rollover_total_draw_count"]),
    }


def _receipt_payload(
    *,
    audit_kind: str,
    identity: ReleaseArtifactIdentity,
    windows: dict[str, str],
    result: dict,
) -> dict:
    return {
        "passed": True,
        "audit_kind": str(audit_kind),
        "repository_commit": identity.repository_commit,
        "release_version": identity.release_version,
        "release_archive_sha256": identity.release_archive_sha256,
        "release_archive_size": identity.release_archive_size,
        **windows,
        **result,
    }


def require_output_directory_outside_repo(
    output_dir: str | Path,
    *,
    repo_root: str | Path,
) -> Path:
    root = Path(repo_root).resolve()
    output = Path(output_dir).resolve()
    if output.is_relative_to(root):
        raise WindowsGameplayReceiptError(
            "Gate-17 Windows gameplay receipts must remain outside Git"
        )
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_new_receipt(path: str | Path, payload: dict) -> Path:
    path = Path(path)
    if path.exists():
        raise WindowsGameplayReceiptError(
            f"receipt already exists; do not overwrite evidence: {path}"
        )
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def run_windows_gameplay_receipts(
    *,
    game_dir: str | Path,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    output_dir: str | Path,
    repo_root: str | Path,
    player_seed: int = 1,
    max_days: int = 420,
) -> dict[str, Path]:
    windows = require_windows_11()
    identity = resolve_release_artifact_identity(
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive=release_archive,
    )
    output = require_output_directory_outside_repo(
        output_dir,
        repo_root=repo_root,
    )

    management = audit_new_game_management_loop(
        HumanGameplayController.from_canonical_game_dir(
            game_dir,
            player_seed=int(player_seed),
        )
    )
    management_path = write_new_receipt(
        output / "new_game_management_loop.json",
        _receipt_payload(
            audit_kind="gate17_new_game_management_loop",
            identity=identity,
            windows=windows,
            result=management,
        ),
    )

    save_reload = audit_save_reload(
        game_dir,
        HumanGameplayController.from_canonical_game_dir(
            game_dir,
            player_seed=int(player_seed),
        ),
    )
    save_path = write_new_receipt(
        output / "save_reload.json",
        _receipt_payload(
            audit_kind="gate17_save_reload",
            identity=identity,
            windows=windows,
            result=save_reload,
        ),
    )

    season = audit_season_progression(
        game_dir,
        player_seed=int(player_seed),
        max_days=int(max_days),
    )
    season_path = write_new_receipt(
        output / "season_progression.json",
        _receipt_payload(
            audit_kind="gate17_season_progression",
            identity=identity,
            windows=windows,
            result=season,
        ),
    )
    return {
        "new_game_management_loop": management_path,
        "save_reload": save_path,
        "season_progression": season_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--max-days", type=int, default=420)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    receipts = run_windows_gameplay_receipts(
        game_dir=args.game_dir,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        release_archive=args.release_archive,
        output_dir=args.output_dir,
        repo_root=repo_root,
        player_seed=args.player_seed,
        max_days=args.max_days,
    )
    for name, path in receipts.items():
        print(f"{name}: {path}")
    print(
        "Gameplay receipts passed. clean_windows_install remains a separate "
        "installed-release receipt and was not inferred here."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
