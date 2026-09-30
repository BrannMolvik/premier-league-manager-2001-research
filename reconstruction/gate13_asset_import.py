from __future__ import annotations

import argparse
import hashlib
import json
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


def validate_source_relative(
    source_relative: str, *, allow_verified_ui_bin: bool = False
) -> str:
    normalized = normalize_member(source_relative)
    pure = PurePosixPath(normalized)
    if not normalized or pure.is_absolute() or ".." in pure.parts:
        raise AssetImportError("Source asset path must stay inside the staging root.")
    if pure.suffix.lower() == ".bin" and not allow_verified_ui_bin:
        raise AssetImportError(
            "Opaque .bin UI resources require a verified extraction report."
        )
    if pure.suffix.lower() in FORBIDDEN_SUFFIXES and not (
        pure.suffix.lower() == ".bin" and allow_verified_ui_bin
    ):
        raise AssetImportError("Raw archive/disc-image containers must not be imported.")
    return normalized


def destination_relative(
    source_relative: str, *, allow_verified_ui_bin: bool = False
) -> Path:
    normalized = validate_source_relative(
        source_relative, allow_verified_ui_bin=allow_verified_ui_bin
    )
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


def verify_selection_inventory(
    inventory_report: Path,
    *,
    source_relative: str,
    staged_sha256: str,
    staged_size: int,
) -> dict:
    """Prove this staged file equals exactly one intentionally extracted original.

    A report may include several catalog entries, but the importer accepts
    only one hashed *extracted candidate* for the requested path. Disc-image
    containers themselves are never importable, including raw .bin archives.
    """
    report = json.loads(Path(inventory_report).read_text(encoding="utf-8"))
    if report.get("unresolved_explicit_paths"):
        raise AssetImportError(
            "Selected-source report has unresolved exact paths; do not import "
            "a partial source selection."
        )
    key = normalize_member(source_relative).casefold()
    candidates = [
        item for item in report.get("candidates", [])
        if isinstance(item.get("path"), str)
        and normalize_member(item["path"]).casefold() == key
    ]
    if len(candidates) != 1:
        raise AssetImportError(
            "Selection inventory must identify exactly one source-layer "
            f"candidate for {source_relative}."
        )
    record = candidates[0]
    if record.get("source_layer") not in {
        "zip-extracted", "iso9660-extracted", "disc-image-extracted"
    }:
        raise AssetImportError(
            "Source report lists this asset but does not verify extracted bytes."
        )
    if record.get("sha256") != staged_sha256 or record.get("size") != staged_size:
        raise AssetImportError(
            "Staged asset bytes differ from the selected source report."
        )
    if PurePosixPath(source_relative).suffix.lower() == ".bin":
        # Loose .bin UI data is possible, but its container identity must be
        # distinguishable from a nested raw BIN disc image.
        if record["source_layer"] == "zip-extracted":
            entries = [
                item for item in report.get("zip_files", [])
                if isinstance(item.get("path"), str)
                and normalize_member(item["path"]).casefold() == key
            ]
            if len(entries) != 1 or entries[0].get("is_disc_image") is not False:
                raise AssetImportError(
                    "Cannot establish that the loose .bin is UI data, not a disc image."
                )
    return report


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
    inventory_report: Path | None = None,
) -> tuple[Path, str]:
    normalized = validate_source_relative(
        source_relative,
        allow_verified_ui_bin=inventory_report is not None,
    )
    staging_root = staging_root.resolve()
    source = (staging_root / Path(*PurePosixPath(normalized).parts)).resolve()

    try:
        source.relative_to(staging_root)
    except ValueError as exc:
        raise AssetImportError("Resolved source escapes the staging root.") from exc

    digest = validate_asset_bytes(normalized, source)
    if inventory_report is not None:
        report = verify_selection_inventory(
            inventory_report,
            source_relative=normalized,
            staged_sha256=digest,
            staged_size=source.stat().st_size,
        )
        source_digest = report.get("source_sha256")
        if isinstance(source_digest, str) and len(source_digest) == 64:
            notes += f" Source archive SHA-256: {source_digest}."
        else:
            notes += " Hash-verified against selected source-inventory report."
    destination_rel = destination_relative(
        normalized,
        allow_verified_ui_bin=inventory_report is not None,
    )
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
        "--inventory-report",
        type=Path,
        help=(
            "Verify staged bytes, source layer and complete exact-path "
            "selection against the JSON extraction report; required for "
            "opaque .bin UI assets and recommended for all imported originals."
        ),
    )
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
        inventory_report=args.inventory_report,
    )
    print(f"Imported {destination.as_posix()} SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
