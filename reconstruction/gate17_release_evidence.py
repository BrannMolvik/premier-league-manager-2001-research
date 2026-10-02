"""Assemble one fail-closed Gate-17 release evidence manifest.

The final release audit deliberately consumes an external evidence JSON rather
than inventing receipt state from the source tree. This helper removes manual
hash-copying from that process. It validates the exact release archive and all
four distinct external receipts against one release version and repository
commit before writing a new evidence file outside Git.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from gate17_release_readiness import (
    REQUIRED_EXTERNAL_RECEIPTS,
    parse_release_evidence,
    require_path_outside_repo,
    validate_external_receipts,
    validate_release_archive,
)


class ReleaseEvidenceAssemblerError(RuntimeError):
    """The external Gate-17 evidence set is inconsistent or incomplete."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_external_path(
    path: str | Path,
    repo_root: str | Path,
    *,
    label: str,
) -> Path:
    try:
        return require_path_outside_repo(Path(path), Path(repo_root), label=label)
    except Exception as exc:
        raise ReleaseEvidenceAssemblerError(str(exc)) from exc


def _require_commit(value: str) -> str:
    value = str(value)
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ReleaseEvidenceAssemblerError(
            "repository_commit must be a lowercase 40-character Git SHA"
        )
    return value


def _require_release_version(value: str) -> str:
    value = str(value).strip()
    if not value:
        raise ReleaseEvidenceAssemblerError("release_version must be non-empty")
    return value


def assemble_release_evidence(
    *,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    receipt_paths: dict[str, str | Path],
    output_path: str | Path,
    repo_root: str | Path,
) -> Path:
    version = _require_release_version(release_version)
    commit = _require_commit(repository_commit)
    root = Path(repo_root).resolve()

    if set(receipt_paths) != set(REQUIRED_EXTERNAL_RECEIPTS):
        missing = sorted(set(REQUIRED_EXTERNAL_RECEIPTS) - set(receipt_paths))
        extra = sorted(set(receipt_paths) - set(REQUIRED_EXTERNAL_RECEIPTS))
        raise ReleaseEvidenceAssemblerError(
            f"receipt set mismatch: missing={missing}, extra={extra}"
        )

    archive = _require_external_path(
        release_archive,
        root,
        label="release archive",
    )
    if not archive.is_file() or archive.stat().st_size <= 0:
        raise ReleaseEvidenceAssemblerError(
            f"release archive is missing or empty: {archive}"
        )

    normalized_receipts: dict[str, Path] = {}
    seen: dict[Path, str] = {}
    for name in REQUIRED_EXTERNAL_RECEIPTS:
        path = _require_external_path(
            receipt_paths[name],
            root,
            label=f"{name} receipt",
        )
        previous = seen.get(path)
        if previous is not None:
            raise ReleaseEvidenceAssemblerError(
                f"{name} receipt reuses the same file as {previous}"
            )
        seen[path] = name
        if not path.is_file():
            raise ReleaseEvidenceAssemblerError(
                f"{name} receipt does not exist: {path}"
            )
        normalized_receipts[name] = path

    output = _require_external_path(
        output_path,
        root,
        label="release evidence output",
    )
    if output.exists():
        raise ReleaseEvidenceAssemblerError(
            f"release evidence already exists; do not overwrite: {output}"
        )
    if output == archive or output in seen:
        raise ReleaseEvidenceAssemblerError(
            "release evidence output must be distinct from archive and receipt files"
        )

    payload = {
        "schema_version": 1,
        "release_version": version,
        "repository_commit": commit,
        "limitations_path": "research/RELEASE_LIMITATIONS.md",
        "external_receipts": {
            name: {
                "path": str(path),
                "sha256": _sha256_file(path),
            }
            for name, path in normalized_receipts.items()
        },
        "archive": {
            "sha256": _sha256_file(archive),
            "size_bytes": int(archive.stat().st_size),
        },
    }

    # Reuse the final audit's own parser/validators before writing anything.
    # This proves every receipt has passed=true, the required criterion flags,
    # and the same commit/version/archive identity as the evidence manifest.
    try:
        evidence = parse_release_evidence(payload)
        validate_external_receipts(evidence, root)
        validate_release_archive(archive, evidence.archive, root)
    except Exception as exc:
        raise ReleaseEvidenceAssemblerError(
            f"release evidence prevalidation failed: {exc}"
        ) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--clean-windows-install", type=Path, required=True)
    parser.add_argument("--new-game-management-loop", type=Path, required=True)
    parser.add_argument("--season-progression", type=Path, required=True)
    parser.add_argument("--save-reload", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    result = assemble_release_evidence(
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        release_archive=args.release_archive,
        receipt_paths={
            "clean_windows_install": args.clean_windows_install,
            "new_game_management_loop": args.new_game_management_loop,
            "season_progression": args.season_progression,
            "save_reload": args.save_reload,
        },
        output_path=args.output,
        repo_root=repo_root,
    )
    print(f"release evidence: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
