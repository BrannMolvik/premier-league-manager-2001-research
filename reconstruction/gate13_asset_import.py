from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import struct

from gate13_source_inventory import (
    EXPECTED_BGROUND_PATH,
    EXPECTED_BGROUND_SHA256,
    EXPECTED_BGROUND_SIZE,
    normalize_member,
)


ORIGINAL_ASSET_PREFIX = Path("original_assets") / "source"
MANIFEST_RELATIVE = Path("original_assets") / "MANIFEST.md"

FORBIDDEN_SUFFIXES = {
    ".7z",
    ".bin",
    ".ccd",
    ".cue",
    ".iso",
    ".mdf",
    ".mds",
    ".nrg",
    ".rar",
    ".sub",
    ".zip",
}

MAX_IMPORT_BYTES = 95 * 1024 * 1024


class AssetImportError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_relative(source_relative: str) -> str:
    normalized = normalize_member(source_relative)
    pure = PurePosixPath(normalized)
    if not normalized or pure.is_absolute() or ".." in pure.parts:
        raise AssetImportError("Source asset path must stay inside the staging root.")
    if pure.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise AssetImportError("Raw archive/disc-image containers must not be imported.")
    return normalized


def destination_relative(source_relative: str) -> Path:
    normalized = validate_source_relative(source_relative)
    return ORIGINAL_ASSET_PREFIX.joinpath(*PurePosixPath(normalized).parts)


def validate_asset_bytes(source_relative: str, source_path: Path) -> str:
    if not source_path.is_file():
        raise AssetImportError(f"Source asset does not exist: {source_path}")
    size = source_path.stat().st_size
    if size > MAX_IMPORT_BYTES:
        raise AssetImportError(
            f"Source asset is {size} bytes; tracked originals must stay below 95 MiB."
        )

    digest = _sha256(source_path)
    if normalize_member(source_relative).lower() == EXPECTED_BGROUND_PATH.lower():
        if digest != EXPECTED_BGROUND_SHA256:
            raise AssetImportError(
                "bground.444 does not match the canonical source-disc SHA-256."
            )
        prefix = source_path.read_bytes()[:4]
        if len(prefix) < 4:
            raise AssetImportError("bground.444 is too short to contain its header.")
        dimensions = struct.unpack("<HH", prefix)
        if dimensions != EXPECTED_BGROUND_SIZE:
            raise AssetImportError(
                f"bground.444 header is {dimensions[0]}x{dimensions[1]}, "
                "expected 800x600."
            )
    return digest


def _manifest_header_and_rows(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    rows = [
        line
        for line in lines
        if line.startswith("| original_assets/") and "| --- |" not in line
    ]
    return lines, rows


def add_manifest_row(
    manifest_text: str,
    *,
    repository_path: str,
    source_path: str,
    sha256: str,
    notes: str,
) -> str:
    row = (
        f"| {repository_path} | {source_path} | {sha256} | original | {notes} |"
    )
    lines = manifest_text.splitlines()
    if any(line.startswith(f"| {repository_path} |") for line in lines):
        raise AssetImportError(f"Manifest already contains {repository_path}.")

    none_row = "| _None imported yet_ |  |  |  |  |"
    if none_row in lines:
        index = lines.index(none_row)
        lines[index] = row
    else:
        separator = "| --- | --- | --- | --- | --- |"
        try:
            start = lines.index(separator) + 1
        except ValueError as exc:
            raise AssetImportError("Manifest table header was not found.") from exc

        while start < len(lines) and lines[start].startswith("| "):
            start += 1
        lines.insert(start, row)

    return "\n".join(lines) + "\n"


def import_original_asset(
    *,
    staging_root: Path,
    source_relative: str,
    repo_root: Path,
    notes: str,
) -> tuple[Path, str]:
    normalized = validate_source_relative(source_relative)
    staging_root = staging_root.resolve()
    source = (staging_root / Path(*PurePosixPath(normalized).parts)).resolve()

    try:
        source.relative_to(staging_root)
    except ValueError as exc:
        raise AssetImportError("Resolved source escapes the staging root.") from exc

    digest = validate_asset_bytes(normalized, source)
    destination_rel = destination_relative(normalized)
    destination = (repo_root.resolve() / destination_rel).resolve()
    manifest = repo_root.resolve() / MANIFEST_RELATIVE

    if destination.exists():
        if _sha256(destination) != digest:
            raise AssetImportError(
                f"Destination already exists with different bytes: {destination_rel}"
            )
        raise AssetImportError(f"Destination is already imported: {destination_rel}")

    manifest_text = manifest.read_text(encoding="utf-8")
    updated_manifest = add_manifest_row(
        manifest_text,
        repository_path=destination_rel.as_posix(),
        source_path=normalized,
        sha256=digest,
        notes=notes,
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    manifest.write_text(updated_manifest, encoding="utf-8")
    return destination_rel, digest


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import one intentionally selected authorized FM2001 asset from a "
            "staging extraction into original_assets/ with manifest provenance."
        )
    )
    parser.add_argument("staging_root", type=Path)
    parser.add_argument("source_relative")
    parser.add_argument("--repo-root", type=Path, default=Path(".."))
    parser.add_argument(
        "--notes",
        default="Byte-identical authorized source asset imported for Gate 13.",
    )
    args = parser.parse_args()

    destination, digest = import_original_asset(
        staging_root=args.staging_root,
        source_relative=args.source_relative,
        repo_root=args.repo_root,
        notes=args.notes,
    )
    print(f"Imported {destination.as_posix()} SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
