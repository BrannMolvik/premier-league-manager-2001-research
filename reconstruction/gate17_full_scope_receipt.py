"""Produce the Gate-17 full-original-scope receipt from per-scope results.

This producer is intentionally unusable while the repository scope catalog is
still unrecovered. It runs on a real Windows 11 client, binds one exact release
archive and repository commit, validates a separately supplied per-scope result
set against the source-backed catalog, and only then writes the immutable
full_original_scope.json receipt outside Git.

It does not discover leagues/countries and does not run gameplay by itself.
Those facts must come from the future source-backed full-scope runtime audit.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from gate17_release_readiness import (
    ReleaseReadinessError,
    require_external_windows_11_workstation,
    require_path_outside_repo,
    validate_full_scope_catalog,
)
from gate17_windows_gameplay_receipts import (
    ReleaseArtifactIdentity,
    WindowsGameplayReceiptError,
    resolve_release_artifact_identity,
    write_new_receipt,
)


class FullScopeReceiptError(RuntimeError):
    """The full-original-scope evidence is incomplete or inconsistent."""


REQUIRED_SCOPE_RESULT_FLAGS = (
    "human_career_flow",
    "competition_progression",
    "original_management_gameplay_subsystems",
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


def validate_scope_results(
    *,
    results_path: str | Path,
    repo_root: str | Path,
) -> dict:
    """Validate every result against the exact source-backed scope catalog."""
    root = Path(repo_root).resolve()
    catalog = validate_full_scope_catalog(root)
    path = _external_existing_file(
        results_path,
        repo_root=root,
        label="full-scope results",
    )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FullScopeReceiptError("full-scope results are not readable JSON") from exc
    if not isinstance(payload, Mapping):
        raise FullScopeReceiptError("full-scope results root must be an object")
    if int(payload.get("schema_version", 0)) != 1:
        raise FullScopeReceiptError("full-scope results schema_version must be 1")
    if payload.get("scope_catalog_sha256") != catalog["sha256"]:
        raise FullScopeReceiptError(
            "full-scope results were produced for a different scope catalog"
        )

    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raise FullScopeReceiptError("full-scope results must contain a results list")
    expected_ids = catalog["scope_ids"]
    actual_ids = []
    failed_ids = []
    for index, raw in enumerate(raw_results):
        if not isinstance(raw, Mapping):
            raise FullScopeReceiptError(
                f"full-scope result {index} must be an object"
            )
        scope_id = raw.get("scope_id")
        if not isinstance(scope_id, str) or not scope_id:
            raise FullScopeReceiptError(
                f"full-scope result {index} requires scope_id"
            )
        actual_ids.append(scope_id)
        if raw.get("passed") is not True:
            failed_ids.append(scope_id)
        for flag in REQUIRED_SCOPE_RESULT_FLAGS:
            if raw.get(flag) is not True:
                failed_ids.append(scope_id)
                break

    if tuple(actual_ids) != expected_ids:
        raise FullScopeReceiptError(
            "full-scope result IDs do not exactly match the source-backed catalog"
        )
    if failed_ids:
        unique_failed = tuple(dict.fromkeys(failed_ids))
        raise FullScopeReceiptError(
            "full-scope results contain failed scope IDs: "
            + ", ".join(unique_failed)
        )

    return {
        "path": str(path),
        "sha256": _sha256_file(path),
        "scope_catalog_sha256": catalog["sha256"],
        "scope_entry_count": catalog["entry_count"],
        "verified_scope_ids": expected_ids,
    }


def _receipt_payload(
    *,
    identity: ReleaseArtifactIdentity,
    windows: dict,
    scope_results: dict,
) -> dict:
    ids = list(scope_results["verified_scope_ids"])
    count = int(scope_results["scope_entry_count"])
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
        "scope_catalog_sha256": scope_results["scope_catalog_sha256"],
        "scope_results_sha256": scope_results["sha256"],
        "scope_entry_count": count,
        "verified_scope_entry_count": count,
        "verified_scope_ids": ids,
        "missing_scope_ids": [],
        "failed_scope_ids": [],
    }


def run_full_scope_receipt(
    *,
    repo_root: str | Path,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    scope_results: str | Path,
    output_path: str | Path,
) -> Path:
    """Write full_original_scope.json only after all fail-closed checks pass."""
    root = Path(repo_root).resolve()
    windows = require_external_windows_11_workstation()
    identity = resolve_release_artifact_identity(
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive=release_archive,
    )
    checked = validate_scope_results(
        results_path=scope_results,
        repo_root=root,
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
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--scope-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = run_full_scope_receipt(
        repo_root=args.repo_root,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        release_archive=args.release_archive,
        scope_results=args.scope_results,
        output_path=args.output,
    )
    print(f"full original scope receipt: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
