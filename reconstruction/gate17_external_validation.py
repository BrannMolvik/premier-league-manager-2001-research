"""Run the complete external Gate-17 validation as one fail-closed transaction.

This coordinator is intended for the final real Windows 11 client workstation.
It does not weaken any prerequisite. Before creating an install directory or an
external receipt it requires:

- a Windows 11 client workstation, never GitHub Actions / Windows Server;
- a clean repository at the exact release commit;
- every Gate 1-16 ROADMAP completion criterion checked;
- the final limitations document to have left its pre-release state;
- the exact release archive and canonical user-owned game directory outside Git;
- a green canonical full-scope implementation preflight over that game directory;
- a fresh external work root.

Only after those checks pass does it require a separately produced full-original-
scope receipt, run the clean-install receipt and the three canonical gameplay
receipts, assemble one release-evidence manifest and execute
the final release-readiness audit. If any later step fails, the newly created
work root is removed so a partial receipt set cannot be mistaken for final
release evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from gate17_clean_windows_install import run_clean_windows_install_receipt
from gate17_full_scope_preflight import run_canonical_full_scope_preflight
from gate17_release_evidence import assemble_release_evidence
from gate17_release_readiness import (
    ReleaseReadinessError,
    require_external_windows_11_workstation,
    require_path_outside_repo,
    run_final_release_audit,
    validate_clean_repository,
    validate_limitations_document,
    validate_roadmap_prerequisites,
)
from gate17_windows_gameplay_receipts import (
    resolve_release_artifact_identity,
    run_windows_gameplay_receipts,
)


class ExternalReleaseValidationError(RuntimeError):
    """The transactional external Gate-17 validation could not complete."""


def _external_existing_dir(
    path: str | Path,
    *,
    repo_root: Path,
    label: str,
) -> Path:
    try:
        target = require_path_outside_repo(Path(path), repo_root, label=label)
    except ReleaseReadinessError as exc:
        raise ExternalReleaseValidationError(str(exc)) from exc
    if not target.is_dir():
        raise ExternalReleaseValidationError(f"{label} does not exist: {target}")
    return target


def _external_existing_file(
    path: str | Path,
    *,
    repo_root: Path,
    label: str,
) -> Path:
    try:
        target = require_path_outside_repo(Path(path), repo_root, label=label)
    except ReleaseReadinessError as exc:
        raise ExternalReleaseValidationError(str(exc)) from exc
    if not target.is_file():
        raise ExternalReleaseValidationError(f"{label} does not exist: {target}")
    return target


def _fresh_external_root(
    path: str | Path,
    *,
    repo_root: Path,
) -> Path:
    try:
        target = require_path_outside_repo(
            Path(path),
            repo_root,
            label="external Gate-17 work root",
        )
    except ReleaseReadinessError as exc:
        raise ExternalReleaseValidationError(str(exc)) from exc
    if target.exists():
        raise ExternalReleaseValidationError(
            f"external Gate-17 work root must not already exist: {target}"
        )
    return target


def preflight_external_release_validation(
    *,
    repo_root: str | Path,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    canonical_game_dir: str | Path,
    full_original_scope_receipt: str | Path,
    work_root: str | Path,
    player_seed: int = 1,
    max_days: int = 420,
) -> dict:
    """Validate all immutable-evidence prerequisites before writing anything."""
    root = Path(repo_root).resolve()
    windows = require_external_windows_11_workstation()
    repository = validate_clean_repository(root, repository_commit)
    roadmap = validate_roadmap_prerequisites(root)
    limitations = validate_limitations_document(
        root,
        "research/RELEASE_LIMITATIONS.md",
    )

    try:
        archive = require_path_outside_repo(
            Path(release_archive),
            root,
            label="release archive",
        )
    except ReleaseReadinessError as exc:
        raise ExternalReleaseValidationError(str(exc)) from exc
    identity = resolve_release_artifact_identity(
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive=archive,
    )
    game_dir = _external_existing_dir(
        canonical_game_dir,
        repo_root=root,
        label="canonical FM2001 game directory",
    )
    scope_receipt = _external_existing_file(
        full_original_scope_receipt,
        repo_root=root,
        label="full original scope receipt",
    )
    implementation_preflight = run_canonical_full_scope_preflight(
        game_dir,
        player_seed=int(player_seed),
        max_days=int(max_days),
    )
    if not implementation_preflight.ready_for_full_runtime_validation:
        raise ExternalReleaseValidationError(
            "canonical full-scope implementation preflight is not ready: "
            + ",".join(implementation_preflight.blocker_codes)
        )
    output_root = _fresh_external_root(work_root, repo_root=root)

    return {
        "windows": windows,
        "repository": repository,
        "roadmap": roadmap,
        "limitations": limitations,
        "identity": identity,
        "release_archive": archive,
        "canonical_game_dir": game_dir,
        "full_original_scope_receipt": scope_receipt,
        "implementation_preflight": implementation_preflight,
        "work_root": output_root,
    }


def _write_new_json(path: Path, payload: dict) -> Path:
    if path.exists():
        raise ExternalReleaseValidationError(
            f"final validation output already exists; do not overwrite: {path}"
        )
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def run_external_release_validation(
    *,
    repo_root: str | Path,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    canonical_game_dir: str | Path,
    full_original_scope_receipt: str | Path,
    work_root: str | Path,
    player_seed: int = 1,
    max_days: int = 420,
) -> dict[str, Path]:
    """Execute the complete external release validation transaction."""
    preflight = preflight_external_release_validation(
        repo_root=repo_root,
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive=release_archive,
        canonical_game_dir=canonical_game_dir,
        full_original_scope_receipt=full_original_scope_receipt,
        work_root=work_root,
        player_seed=int(player_seed),
        max_days=int(max_days),
    )

    root = Path(repo_root).resolve()
    output_root = Path(preflight["work_root"])
    receipts_dir = output_root / "receipts"
    install_root = output_root / "install"
    evidence_path = output_root / "release-evidence.json"
    final_receipt_path = output_root / "gate17-final-release.json"

    output_root.mkdir(parents=True)
    try:
        clean_receipt = run_clean_windows_install_receipt(
            release_version=release_version,
            repository_commit=repository_commit,
            release_archive=preflight["release_archive"],
            install_root=install_root,
            output_dir=receipts_dir,
            repo_root=root,
        )
        gameplay = run_windows_gameplay_receipts(
            game_dir=preflight["canonical_game_dir"],
            release_version=release_version,
            repository_commit=repository_commit,
            release_archive=preflight["release_archive"],
            output_dir=receipts_dir,
            repo_root=root,
            player_seed=int(player_seed),
            max_days=int(max_days),
        )
        evidence = assemble_release_evidence(
            release_version=release_version,
            repository_commit=repository_commit,
            release_archive=preflight["release_archive"],
            receipt_paths={
                "clean_windows_install": clean_receipt,
                "new_game_management_loop": gameplay["new_game_management_loop"],
                "season_progression": gameplay["season_progression"],
                "save_reload": gameplay["save_reload"],
                "full_original_scope": preflight["full_original_scope_receipt"],
            },
            output_path=evidence_path,
            repo_root=root,
        )
        final_receipt = run_final_release_audit(
            repo_root=root,
            evidence_path=evidence,
            release_archive=preflight["release_archive"],
            canonical_game_dir=preflight["canonical_game_dir"],
        )
        _write_new_json(final_receipt_path, final_receipt)
    except Exception:
        shutil.rmtree(output_root, ignore_errors=True)
        raise

    return {
        "work_root": output_root,
        "clean_windows_install": clean_receipt,
        "new_game_management_loop": gameplay["new_game_management_loop"],
        "season_progression": gameplay["season_progression"],
        "save_reload": gameplay["save_reload"],
        "full_original_scope": preflight["full_original_scope_receipt"],
        "release_evidence": evidence,
        "final_release_receipt": final_receipt_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--canonical-game-dir", type=Path, required=True)
    parser.add_argument("--full-original-scope-receipt", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--max-days", type=int, default=420)
    args = parser.parse_args()

    result = run_external_release_validation(
        repo_root=args.repo_root,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        release_archive=args.release_archive,
        canonical_game_dir=args.canonical_game_dir,
        full_original_scope_receipt=args.full_original_scope_receipt,
        work_root=args.work_root,
        player_seed=args.player_seed,
        max_days=args.max_days,
    )
    print(json.dumps({key: str(value) for key, value in result.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
