from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import tempfile
from typing import BinaryIO, Iterable
import zipfile


EXPECTED_BGROUND_PATH = "FM2001_Art/Generic/bground.444"
EXPECTED_BGROUND_SHA256 = (
    "9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9"
)
EXPECTED_BGROUND_SIZE = (800, 600)

KNOWN_GATE13_PATHS = {
    "fm2001_art/generic/bground.444",
    "fm2001_art/generic/license.png",
    "fmv/easp.tgq",
    "fmv/premintro.tgq",
    "fmv/credits2.txt",
}

GATE13_HINTS = (
    "background",
    "bground",
    "button",
    "continue",
    "cursor",
    "front",
    "league",
    "load",
    "logo",
    "main",
    "menu",
    "prem",
    "quit",
    "select",
    "start",
    "team",
    "user",
)

PRESENTATION_SUFFIXES = {
    ".444",
    ".bmp",
    ".gif",
    ".idx",
    ".jpg",
    ".jpeg",
    ".pcx",
    ".png",
    ".str",
    ".tga",
    ".tgq",
    ".txt",
}

DISC_IMAGE_SUFFIXES = {
    ".bin",
    ".ccd",
    ".img",
    ".iso",
    ".mdf",
    ".nrg",
}


@dataclass(frozen=True)
class AssetRecord:
    path: str
    size: int | None
    sha256: str | None
    source_layer: str
    candidate_reason: str
    width_u16le: int | None = None
    height_u16le: int | None = None
    expected_hash_match: bool | None = None


def normalize_member(path: str) -> str:
    text = path.replace("\\", "/").lstrip("/")
    parts = [part for part in text.split("/") if part not in ("", ".")]
    return "/".join(parts)


def _lower(path: str) -> str:
    return normalize_member(path).lower()


def candidate_reason(path: str) -> str | None:
    normalized = normalize_member(path)
    lowered = normalized.lower()
    suffix = PurePosixPath(normalized).suffix.lower()

    if lowered in KNOWN_GATE13_PATHS:
        return "known-gate13-path"

    if lowered.startswith("fm2001_art/generic/"):
        return "generic-front-end-directory"

    basename = PurePosixPath(lowered).name
    if suffix in PRESENTATION_SUFFIXES and any(hint in basename for hint in GATE13_HINTS):
        return "presentation-name-hint"

    return None


def is_disc_image(path: str) -> bool:
    return PurePosixPath(normalize_member(path)).suffix.lower() in DISC_IMAGE_SUFFIXES


def sha256_stream(stream: BinaryIO, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return sha256_stream(handle)


def _dimensions_from_prefix(prefix: bytes) -> tuple[int | None, int | None]:
    if len(prefix) < 4:
        return None, None
    return struct.unpack("<HH", prefix[:4])


def _record_from_bytes(
    *,
    path: str,
    data: bytes,
    source_layer: str,
    reason: str,
) -> AssetRecord:
    digest = hashlib.sha256(data).hexdigest()
    width, height = _dimensions_from_prefix(data)
    lowered = _lower(path)
    expected = None
    if lowered == EXPECTED_BGROUND_PATH.lower():
        expected = digest == EXPECTED_BGROUND_SHA256
    return AssetRecord(
        path=normalize_member(path),
        size=len(data),
        sha256=digest,
        source_layer=source_layer,
        candidate_reason=reason,
        width_u16le=width if lowered.endswith(".444") else None,
        height_u16le=height if lowered.endswith(".444") else None,
        expected_hash_match=expected,
    )


def inventory_directory(root: Path) -> tuple[list[AssetRecord], list[str]]:
    records: list[AssetRecord] = []
    warnings: list[str] = []
    root = root.resolve()

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = normalize_member(path.relative_to(root).as_posix())
        reason = candidate_reason(relative)
        if reason is None:
            continue
        digest = sha256_file(path)
        prefix = path.read_bytes()[:4]
        width, height = _dimensions_from_prefix(prefix)
        lowered = relative.lower()
        expected = None
        if lowered == EXPECTED_BGROUND_PATH.lower():
            expected = digest == EXPECTED_BGROUND_SHA256
            if expected and (width, height) != EXPECTED_BGROUND_SIZE:
                warnings.append(
                    "bground.444 hash matches but first uint16 dimensions are "
                    f"{width}x{height}, expected 800x600"
                )
        records.append(
            AssetRecord(
                path=relative,
                size=path.stat().st_size,
                sha256=digest,
                source_layer="directory",
                candidate_reason=reason,
                width_u16le=width if lowered.endswith(".444") else None,
                height_u16le=height if lowered.endswith(".444") else None,
                expected_hash_match=expected,
            )
        )

    return records, warnings


def inventory_zip(path: Path) -> tuple[list[AssetRecord], list[str], list[str]]:
    records: list[AssetRecord] = []
    nested_images: list[str] = []
    warnings: list[str] = []

    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            member = normalize_member(info.filename)
            if is_disc_image(member):
                nested_images.append(member)

            reason = candidate_reason(member)
            if reason is None:
                continue

            with archive.open(info) as stream:
                data = stream.read()
            record = _record_from_bytes(
                path=member,
                data=data,
                source_layer="zip",
                reason=reason,
            )
            records.append(record)

    if not records and nested_images:
        warnings.append(
            "No Gate-13 resources are direct ZIP members; nested disc image "
            "inspection is required."
        )
    return records, nested_images, warnings


def parse_7z_slt(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_entries = False

    for raw in text.splitlines():
        line = raw.rstrip()
        if line == "----------":
            if current.get("Path"):
                entries.append(current)
            current = {}
            in_entries = True
            continue
        if not in_entries:
            continue
        if not line:
            if current.get("Path"):
                entries.append(current)
            current = {}
            continue
        if " = " in line:
            key, value = line.split(" = ", 1)
            current[key] = value

    if current.get("Path"):
        entries.append(current)
    return entries


def _seven_zip_command(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for command in ("7z", "7zz", "7za"):
        resolved = shutil.which(command)
        if resolved:
            return resolved
    return None


def list_with_7z(container: Path, seven_zip: str) -> list[dict[str, str]]:
    process = subprocess.run(
        [seven_zip, "l", "-slt", str(container)],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"7-Zip could not list {container}: {process.stderr.strip()}"
        )
    return parse_7z_slt(process.stdout)


def _extract_member(
    container: Path,
    member: str,
    destination: Path,
    seven_zip: str,
) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    process = subprocess.run(
        [
            seven_zip,
            "x",
            "-y",
            f"-o{destination}",
            str(container),
            member,
        ],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"7-Zip could not extract {member} from {container}: "
            f"{process.stderr.strip()}"
        )
    expected = destination / Path(*PurePosixPath(normalize_member(member)).parts)
    if expected.exists():
        return expected
    matches = list(destination.rglob(PurePosixPath(member).name))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError(
        f"7-Zip reported success but extracted member was not found: {member}"
    )


def inventory_disc_image(
    image: Path,
    seven_zip: str,
    extract_candidates_to: Path | None = None,
) -> tuple[list[AssetRecord], list[str]]:
    records: list[AssetRecord] = []
    warnings: list[str] = []
    entries = list_with_7z(image, seven_zip)

    for entry in entries:
        member = normalize_member(entry.get("Path", ""))
        reason = candidate_reason(member)
        if reason is None:
            continue

        size = None
        raw_size = entry.get("Size")
        if raw_size and raw_size.isdigit():
            size = int(raw_size)

        record = AssetRecord(
            path=member,
            size=size,
            sha256=None,
            source_layer="disc-image-listing",
            candidate_reason=reason,
        )

        if extract_candidates_to is not None:
            extracted = _extract_member(
                image,
                member,
                extract_candidates_to,
                seven_zip,
            )
            data = extracted.read_bytes()
            record = _record_from_bytes(
                path=member,
                data=data,
                source_layer="disc-image-extracted",
                reason=reason,
            )
        records.append(record)

    if not records:
        warnings.append(
            f"No Gate-13 candidate resources were found in disc image {image.name}."
        )
    return records, warnings


def deep_inventory_zip(
    archive: Path,
    seven_zip: str,
    extract_candidates_to: Path | None = None,
) -> tuple[list[AssetRecord], list[str]]:
    direct, nested_images, warnings = inventory_zip(archive)
    records = list(direct)
    if not nested_images:
        return records, warnings

    with tempfile.TemporaryDirectory(prefix="fm2001-gate13-") as temp_name:
        temp = Path(temp_name)
        for member in nested_images:
            extracted_image = _extract_member(
                archive,
                member,
                temp,
                seven_zip,
            )
            try:
                image_records, image_warnings = inventory_disc_image(
                    extracted_image,
                    seven_zip,
                    extract_candidates_to,
                )
            except RuntimeError as exc:
                warnings.append(str(exc))
                continue
            records.extend(image_records)
            warnings.extend(image_warnings)

    return records, warnings


def report_for_source(
    source: Path,
    *,
    deep: bool = False,
    seven_zip: str | None = None,
    extract_candidates_to: Path | None = None,
    hash_source: bool = False,
) -> dict:
    source = source.resolve()
    warnings: list[str] = []
    nested_images: list[str] = []

    if source.is_dir():
        records, warnings = inventory_directory(source)
        kind = "directory"
    elif zipfile.is_zipfile(source):
        kind = "zip"
        if deep:
            command = _seven_zip_command(seven_zip)
            if command is None:
                records, nested_images, warnings = inventory_zip(source)
                warnings.append(
                    "Deep inspection requested but 7-Zip was not found. "
                    "Install 7-Zip or pass --seven-zip."
                )
            else:
                records, warnings = deep_inventory_zip(
                    source,
                    command,
                    extract_candidates_to,
                )
                _, nested_images, _ = inventory_zip(source)
        else:
            records, nested_images, warnings = inventory_zip(source)
    elif source.suffix.lower() in DISC_IMAGE_SUFFIXES:
        kind = "disc-image"
        command = _seven_zip_command(seven_zip)
        if command is None:
            records = []
            warnings = [
                "Disc image inspection requires 7-Zip. Install it or pass "
                "--seven-zip."
            ]
        else:
            records, warnings = inventory_disc_image(
                source,
                command,
                extract_candidates_to,
            )
    else:
        raise ValueError(
            "Source must be an extracted directory, ZIP archive, or supported "
            "disc image."
        )

    bground = [
        record
        for record in records
        if _lower(record.path) == EXPECTED_BGROUND_PATH.lower()
    ]
    if bground:
        record = bground[0]
        if record.sha256 is not None and record.sha256 != EXPECTED_BGROUND_SHA256:
            warnings.append(
                "Recovered bground.444 does not match the canonical source-disc "
                "SHA-256 recorded by the project."
            )
        if (
            record.width_u16le is not None
            and (record.width_u16le, record.height_u16le) != EXPECTED_BGROUND_SIZE
        ):
            warnings.append(
                "Recovered bground.444 dimensions do not match the recorded "
                "800x600 header."
            )

    return {
        "schema_version": 1,
        "source": str(source),
        "source_kind": kind,
        "source_size": source.stat().st_size if source.is_file() else None,
        "source_sha256": sha256_file(source) if hash_source and source.is_file() else None,
        "expected_bground": {
            "path": EXPECTED_BGROUND_PATH,
            "sha256": EXPECTED_BGROUND_SHA256,
            "width": EXPECTED_BGROUND_SIZE[0],
            "height": EXPECTED_BGROUND_SIZE[1],
        },
        "nested_disc_images": nested_images,
        "candidates": [asdict(record) for record in records],
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory authorized FM2001 source material for Gate 13 without "
            "adding raw disc images to Git."
        )
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--seven-zip")
    parser.add_argument("--extract-candidates-to", type=Path)
    parser.add_argument("--hash-source", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = report_for_source(
        args.source,
        deep=args.deep,
        seven_zip=args.seven_zip,
        extract_candidates_to=args.extract_candidates_to,
        hash_source=args.hash_source,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
