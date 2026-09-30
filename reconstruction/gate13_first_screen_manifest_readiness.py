"""Fail-closed readiness audit for the pinned Gate-13 first-screen originals.

This is an end-state repository audit, not a source-extraction validator. The
source inventory/selection stage proves staged licensed bytes before import.
This module proves that every pinned source asset was subsequently imported at
its canonical repository path, recorded in the provenance manifest with the
same source SHA-256, and still has byte-identical tracked contents.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from gate13_asset_import import destination_relative
from gate13_first_screen_selection import (
    FIRST_SCREEN_ORIGINALS,
    ExpectedSource,
    assert_canonical_selection_file,
    source_selection_file,
)
from gate13_source_inventory import normalize_member


MANIFEST_RELATIVE = Path("original_assets") / "MANIFEST.md"


class FirstScreenManifestReadinessError(ValueError):
    pass


@dataclass(frozen=True)
class ManifestAssetRow:
    repository_path: str
    source_path: str
    source_sha256: str
    form: str


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest_asset_rows(text: str) -> tuple[ManifestAssetRow, ...]:
    """Parse provenance rows without treating surrounding Markdown as data."""
    rows: list[ManifestAssetRow] = []
    seen_repository: set[str] = set()
    seen_source: set[str] = set()

    for raw_line in text.splitlines():
        if not raw_line.startswith("| original_assets/"):
            continue
        cells = [cell.strip() for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) != 5:
            raise FirstScreenManifestReadinessError(
                "Malformed original_assets manifest row"
            )
        repository_path, source_path, source_sha256, form, _notes = cells
        normalized_source = normalize_member(source_path)
        repository_key = repository_path.casefold()
        source_key = normalized_source.casefold()
        if repository_key in seen_repository:
            raise FirstScreenManifestReadinessError(
                f"Duplicate manifest repository path: {repository_path}"
            )
        if source_key in seen_source:
            raise FirstScreenManifestReadinessError(
                f"Duplicate manifest source path: {source_path}"
            )
        seen_repository.add(repository_key)
        seen_source.add(source_key)
        rows.append(
            ManifestAssetRow(
                repository_path=repository_path,
                source_path=normalized_source,
                source_sha256=source_sha256.lower(),
                form=form.lower(),
            )
        )
    return tuple(rows)


def assert_first_screen_manifest_ready(
    repo_root: Path,
    *,
    expected_assets: tuple[ExpectedSource, ...] = FIRST_SCREEN_ORIGINALS,
) -> tuple[str, ...]:
    """Return canonical repository paths only when the full first slice is ready."""
    root = Path(repo_root).resolve()
    manifest = root / MANIFEST_RELATIVE
    if not manifest.is_file():
        raise FirstScreenManifestReadinessError(
            "Original asset manifest is missing"
        )

    rows = parse_manifest_asset_rows(manifest.read_text(encoding="utf-8"))
    by_source = {row.source_path.casefold(): row for row in rows}
    verified: list[str] = []

    for asset in expected_assets:
        source_key = normalize_member(asset.path).casefold()
        row = by_source.get(source_key)
        if row is None:
            raise FirstScreenManifestReadinessError(
                f"Pinned first-screen original is not imported: {asset.path}"
            )

        expected_repository = destination_relative(asset.path).as_posix()
        if row.repository_path != expected_repository:
            raise FirstScreenManifestReadinessError(
                f"Manifest repository path disagrees for {asset.path}: "
                f"{row.repository_path} != {expected_repository}"
            )
        if row.form != "original":
            raise FirstScreenManifestReadinessError(
                f"Pinned source copy must remain byte-identical original: {asset.path}"
            )
        if row.source_sha256 != asset.sha256:
            raise FirstScreenManifestReadinessError(
                f"Manifest source SHA-256 disagrees for {asset.path}"
            )

        tracked = root / Path(*Path(expected_repository).parts)
        if not tracked.is_file():
            raise FirstScreenManifestReadinessError(
                f"Manifest-listed first-screen original is absent: {expected_repository}"
            )
        actual_hash = _sha256(tracked)
        if actual_hash != asset.sha256:
            raise FirstScreenManifestReadinessError(
                f"Tracked bytes disagree with pinned source SHA-256: {asset.path}"
            )
        verified.append(expected_repository)

    return tuple(verified)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail unless all ten pinned FM2001 first-screen originals are "
            "provenance-imported and byte-identical to their source receipts."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()

    # Keep the durable extraction plan and the import-readiness contract locked
    # to the same independently recovered source set.
    assert_canonical_selection_file(source_selection_file())
    verified = assert_first_screen_manifest_ready(args.repo_root)
    print(
        f"Gate 13 first-screen provenance ready: {len(verified)} pinned "
        "original resources are present with exact source hashes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
