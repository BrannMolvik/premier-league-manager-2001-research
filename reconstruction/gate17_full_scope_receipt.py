"""Produce the final Gate-17 full_original_scope receipt fail-closed.

This module does not create gameplay capability. It can only turn an external
per-scope audit result into a release receipt when all of the following are true:

- the current canonical TeamSelect catalog is loaded from verified game data;
- the canonical repository-side full-scope implementation preflight is green;
- every exact catalog scope appears once, in canonical order;
- every scope proves human career flow, competition progression, required
  management/gameplay subsystems, and save/reload continuation;
- the external audit proves the source-backed six-simultaneous-human contract;
- the receipt is produced on a real Windows 11 client and bound to one exact
  release archive, version, and repository commit.

The external per-scope audit is intentionally separate from this producer.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from gate17_full_scope_catalog import load_canonical_original_playable_scope
from gate17_full_scope_preflight import run_canonical_full_scope_preflight
from gate17_multi_human_capability import ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS
from gate17_release_readiness import (
    ReleaseReadinessError,
    build_full_scope_receipt_binding,
    require_external_windows_11_workstation,
    require_path_outside_repo,
)
from gate17_windows_gameplay_receipts import (
    ReleaseArtifactIdentity,
    WindowsGameplayReceiptError,
    resolve_release_artifact_identity,
    write_new_receipt,
)


class FullScopeReceiptError(RuntimeError):
    """The full-original-scope evidence is incomplete or inconsistent."""


RESULT_SCHEMA_VERSION = 2
REQUIRED_PER_SCOPE_FLAGS = (
    "human_career_flow",
    "competition_progression",
    "original_management_gameplay_subsystems",
    "save_reload",
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _external_existing_file(
    path: str | Path,
    *,
    repo_root: Path,
    label: str,
) -> Path:
    try:
        target = require_path_outside_repo(Path(path), repo_root, label=label)
    except ReleaseReadinessError as exc:
        raise FullScopeReceiptError(str(exc)) from exc
    if not target.is_file():
        raise FullScopeReceiptError(f"{label} does not exist: {target}")
    return target


def _read_result_payload(path: Path) -> Mapping[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FullScopeReceiptError(
            "full-scope result file is not readable JSON"
        ) from exc
    if not isinstance(payload, Mapping):
        raise FullScopeReceiptError("full-scope result root must be an object")
    return payload


def validate_full_scope_results(
    *,
    results_path: str | Path,
    repo_root: str | Path,
    canonical_game_dir: str | Path,
    identity: ReleaseArtifactIdentity,
) -> dict:
    """Bind external per-scope results to the current canonical TeamSelect catalog."""
    root = Path(repo_root).resolve()
    path = _external_existing_file(
        results_path,
        repo_root=root,
        label="full-scope results",
    )
    payload = _read_result_payload(path)
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        raise FullScopeReceiptError(
            f"full-scope results schema_version must be {RESULT_SCHEMA_VERSION}"
        )
    if type(identity) is not ReleaseArtifactIdentity:
        raise FullScopeReceiptError(
            "full-scope results require exact ReleaseArtifactIdentity"
        )
    expected_identity = {
        "release_version": identity.release_version,
        "repository_commit": identity.repository_commit,
        "release_archive_sha256": identity.release_archive_sha256,
        "release_archive_size": identity.release_archive_size,
    }
    for key, expected in expected_identity.items():
        if payload.get(key) != expected:
            raise FullScopeReceiptError(
                f"full-scope results {key} does not match release candidate"
            )
    if payload.get("windows_11") is not True:
        raise FullScopeReceiptError(
            "full-scope results must prove windows_11"
        )
    windows_build = payload.get("windows_build")
    if type(windows_build) is not int or windows_build < 22000:
        raise FullScopeReceiptError(
            "full-scope results windows_build is not Windows 11"
        )
    if payload.get("windows_product_type") != 1:
        raise FullScopeReceiptError(
            "full-scope results must come from a Windows client workstation"
        )

    scope = load_canonical_original_playable_scope(Path(canonical_game_dir).resolve())
    binding = build_full_scope_receipt_binding(scope)

    if payload.get("scope_catalog_sha256") != binding["scope_catalog_sha256"]:
        raise FullScopeReceiptError(
            "full-scope results were produced for a different TeamSelect catalog"
        )

    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raise FullScopeReceiptError("full-scope results must contain a results list")

    actual_ids: list[str] = []
    failed_ids: list[str] = []
    save_reload_failed_ids: list[str] = []
    for index, raw in enumerate(raw_results):
        if not isinstance(raw, Mapping):
            raise FullScopeReceiptError(
                f"full-scope result {index} must be an object"
            )
        scope_id = raw.get("scope_id")
        if not isinstance(scope_id, str) or not scope_id:
            raise FullScopeReceiptError(
                f"full-scope result {index} requires non-empty scope_id"
            )
        actual_ids.append(scope_id)
        if raw.get("passed") is not True:
            failed_ids.append(scope_id)
        for flag in REQUIRED_PER_SCOPE_FLAGS:
            if raw.get(flag) is not True:
                failed_ids.append(scope_id)
                if flag == "save_reload":
                    save_reload_failed_ids.append(scope_id)

    expected_ids = tuple(binding["scope_ids"])
    if tuple(actual_ids) != expected_ids:
        raise FullScopeReceiptError(
            "full-scope result IDs do not exactly match canonical TeamSelect order"
        )
    if len(set(actual_ids)) != len(actual_ids):
        raise FullScopeReceiptError("full-scope results contain duplicate scope IDs")

    multi_human = payload.get("multi_human_management")
    simultaneous = payload.get("simultaneous_human_users_verified")
    if multi_human is not True:
        raise FullScopeReceiptError(
            "full-scope results must prove multi_human_management"
        )
    if (
        type(simultaneous) is not int
        or simultaneous != ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS
    ):
        raise FullScopeReceiptError(
            "full-scope results simultaneous_human_users_verified must equal "
            f"{ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS}"
        )

    unique_failed = tuple(dict.fromkeys(failed_ids))
    if unique_failed:
        raise FullScopeReceiptError(
            "full-scope results contain failed scope IDs: "
            + ", ".join(unique_failed)
        )

    if save_reload_failed_ids:
        raise FullScopeReceiptError(
            "full-scope results contain save/reload failures: "
            + ", ".join(tuple(dict.fromkeys(save_reload_failed_ids)))
        )

    return {
        "path": str(path),
        "sha256": _sha256_file(path),
        **binding,
        "verified_scope_ids": expected_ids,
        "verified_scope_entry_count": len(expected_ids),
        "save_reload_verified_scope_ids": expected_ids,
        "save_reload_verified_scope_entry_count": len(expected_ids),
        "simultaneous_human_users_verified": simultaneous,
        "windows_build": windows_build,
        "windows_product_type": 1,
    }


def _receipt_payload(
    *,
    identity: ReleaseArtifactIdentity,
    windows: dict,
    scope_results: dict,
) -> dict:
    ids = list(scope_results["verified_scope_ids"])
    save_ids = list(scope_results["save_reload_verified_scope_ids"])
    return {
        "passed": True,
        "audit_kind": "gate17_full_original_scope",
        "repository_commit": identity.repository_commit,
        "release_version": identity.release_version,
        "release_archive_sha256": identity.release_archive_sha256,
        "release_archive_size": identity.release_archive_size,
        **windows,
        "full_original_scope": True,
        "all_original_playable_leagues": True,
        "all_original_playable_countries": True,
        "human_career_flow": True,
        "competition_progression": True,
        "original_management_gameplay_subsystems": True,
        "all_original_scope_save_reload": True,
        "multi_human_management": True,
        "simultaneous_human_users_verified": int(
            scope_results["simultaneous_human_users_verified"]
        ),
        "scope_catalog_sha256": scope_results["scope_catalog_sha256"],
        "scope_country_count": int(scope_results["scope_country_count"]),
        "scope_entry_count": int(scope_results["scope_entry_count"]),
        "scope_selectable_club_row_count": int(
            scope_results["scope_selectable_club_row_count"]
        ),
        "scope_results_sha256": scope_results["sha256"],
        "verified_scope_entry_count": int(
            scope_results["verified_scope_entry_count"]
        ),
        "verified_scope_ids": ids,
        "missing_scope_ids": [],
        "failed_scope_ids": [],
        "save_reload_verified_scope_entry_count": int(
            scope_results["save_reload_verified_scope_entry_count"]
        ),
        "save_reload_verified_scope_ids": save_ids,
        "save_reload_missing_scope_ids": [],
        "save_reload_failed_scope_ids": [],
    }


def run_full_scope_receipt(
    *,
    repo_root: str | Path,
    canonical_game_dir: str | Path,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    scope_results: str | Path,
    output_path: str | Path,
    player_seed: int = 1,
    max_days: int = 420,
) -> Path:
    """Write full_original_scope.json only after all current gates are proven."""
    root = Path(repo_root).resolve()
    windows = require_external_windows_11_workstation()

    identity = resolve_release_artifact_identity(
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive=release_archive,
    )

    implementation = run_canonical_full_scope_preflight(
        Path(canonical_game_dir).resolve(),
        player_seed=int(player_seed),
        max_days=int(max_days),
    )
    if not implementation.ready_for_full_runtime_validation:
        raise FullScopeReceiptError(
            "canonical full-scope implementation preflight is not ready: "
            + ",".join(implementation.blocker_codes)
        )

    checked = validate_full_scope_results(
        results_path=scope_results,
        repo_root=root,
        canonical_game_dir=canonical_game_dir,
        identity=identity,
    )

    if windows.get("windows_build") != checked["windows_build"]:
        raise FullScopeReceiptError(
            "full-scope results Windows build differs from receipt workstation"
        )
    if windows.get("windows_product_type") != checked["windows_product_type"]:
        raise FullScopeReceiptError(
            "full-scope results Windows product type differs from receipt workstation"
        )

    try:
        output = require_path_outside_repo(
            Path(output_path),
            root,
            label="full original scope receipt",
        )
    except ReleaseReadinessError as exc:
        raise FullScopeReceiptError(str(exc)) from exc
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        return write_new_receipt(
            output,
            _receipt_payload(
                identity=identity,
                windows=windows,
                scope_results=checked,
            ),
        )
    except WindowsGameplayReceiptError as exc:
        raise FullScopeReceiptError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--canonical-game-dir", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--scope-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--max-days", type=int, default=420)
    args = parser.parse_args()

    result = run_full_scope_receipt(
        repo_root=args.repo_root,
        canonical_game_dir=args.canonical_game_dir,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        release_archive=args.release_archive,
        scope_results=args.scope_results,
        output_path=args.output,
        player_seed=args.player_seed,
        max_days=args.max_days,
    )
    print(f"full original scope receipt: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
