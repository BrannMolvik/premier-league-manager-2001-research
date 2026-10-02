from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
from typing import Iterable


CANONICAL_SOUND_BANK_COUNT = 64
CANONICAL_STARTUP_MEDIA_PATHS = (
    "FMV/easp.tgq",
    "FMV/premintro.tgq",
)


@dataclass(frozen=True)
class Gate14AudioCatalogEntry:
    path: str
    size: int | None
    extent: int | None
    category: str
    binding_status: str
    sha256: str | None = None


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _key(path: str) -> str:
    return _normalize(path).casefold()


def _candidate_hashes(report: dict) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for item in report.get("candidates", []):
        path = item.get("path")
        digest = item.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            continue
        key = _key(path)
        previous = hashes.get(key)
        if previous is not None and previous != digest:
            raise ValueError(
                f"Conflicting source hashes for catalog path: {_normalize(path)}"
            )
        hashes[key] = digest
    return hashes


def build_audio_catalog(report: dict) -> dict:
    """Reduce a full source report to evidence-backed Gate-14 audio candidates.

    Only two source families are promoted here:

    * .bnk files, because the canonical raw-disc census already proves that the
      shipped source contains an EA sound-bank family;
    * the two exact startup TGQ paths whose executable startup callsites and
      embedded audio have already been verified separately.

    The reducer deliberately does not infer a .bnk bank role, sample index,
    menu-music identity, or event mapping from a filename.
    """

    candidate_hashes = _candidate_hashes(report)
    seen: set[str] = set()
    sound_banks: list[Gate14AudioCatalogEntry] = []
    startup_media: list[Gate14AudioCatalogEntry] = []
    startup_keys = {_key(path) for path in CANONICAL_STARTUP_MEDIA_PATHS}

    for item in report.get("disc_files", []):
        path = item.get("path")
        if not isinstance(path, str):
            continue
        normalized = _normalize(path)
        key = normalized.casefold()
        if key in seen:
            raise ValueError(f"Duplicate case-insensitive disc path: {normalized}")
        seen.add(key)

        suffix = PurePosixPath(normalized).suffix.casefold()
        if suffix == ".bnk":
            sound_banks.append(
                Gate14AudioCatalogEntry(
                    path=normalized,
                    size=item.get("size") if isinstance(item.get("size"), int) else None,
                    extent=(
                        item.get("extent")
                        if isinstance(item.get("extent"), int)
                        else None
                    ),
                    category="sound-bank",
                    binding_status="unmapped",
                    sha256=candidate_hashes.get(key),
                )
            )
        elif key in startup_keys:
            startup_media.append(
                Gate14AudioCatalogEntry(
                    path=normalized,
                    size=item.get("size") if isinstance(item.get("size"), int) else None,
                    extent=(
                        item.get("extent")
                        if isinstance(item.get("extent"), int)
                        else None
                    ),
                    category="startup-media",
                    binding_status="startup-sequence-source-proven",
                    sha256=candidate_hashes.get(key),
                )
            )

    sound_banks.sort(key=lambda entry: entry.path.casefold())
    startup_media.sort(
        key=lambda entry: CANONICAL_STARTUP_MEDIA_PATHS.index(
            next(
                canonical
                for canonical in CANONICAL_STARTUP_MEDIA_PATHS
                if _key(canonical) == _key(entry.path)
            )
        )
    )

    return {
        "schema_version": 1,
        "source_sha256": report.get("source_sha256"),
        "disc_file_count": report.get(
            "disc_file_count", len(report.get("disc_files", []))
        ),
        "sound_bank_count": len(sound_banks),
        "startup_media_count": len(startup_media),
        "sound_banks": [asdict(entry) for entry in sound_banks],
        "startup_media": [asdict(entry) for entry in startup_media],
        "bank_semantics_recovered": False,
        "bank_event_bindings_recovered": False,
    }


def validate_canonical_audio_catalog(catalog: dict) -> None:
    if catalog.get("sound_bank_count") != CANONICAL_SOUND_BANK_COUNT:
        raise ValueError(
            "Canonical FM2001 audio catalog must contain exactly "
            f"{CANONICAL_SOUND_BANK_COUNT} .bnk files; found "
            f"{catalog.get('sound_bank_count')}."
        )

    paths = tuple(item.get("path") for item in catalog.get("startup_media", []))
    if tuple(_key(path) for path in paths if isinstance(path, str)) != tuple(
        _key(path) for path in CANONICAL_STARTUP_MEDIA_PATHS
    ):
        raise ValueError(
            "Canonical FM2001 startup media catalog must contain exactly "
            "FMV/easp.tgq then FMV/premintro.tgq."
        )


def selected_paths(catalog: dict, kind: str) -> list[str]:
    if kind not in {"all", "banks", "startup"}:
        raise ValueError(f"Unsupported audio catalog kind: {kind}")
    paths: list[str] = []
    if kind in {"all", "banks"}:
        paths.extend(
            item["path"]
            for item in catalog.get("sound_banks", [])
            if isinstance(item.get("path"), str)
        )
    if kind in {"all", "startup"}:
        paths.extend(
            item["path"]
            for item in catalog.get("startup_media", [])
            if isinstance(item.get("path"), str)
        )
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reduce a saved FM2001 full-disc source report to the exact "
            "Gate-14 .bnk and startup-TGQ catalog without assigning unproven "
            "sound-bank semantics."
        )
    )
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--kind",
        choices=("all", "banks", "startup"),
        default="all",
    )
    parser.add_argument(
        "--paths-only",
        action="store_true",
        help=(
            "Print selected exact source-relative paths, one per line. "
            "This is suitable for a later explicit-path extraction pass."
        ),
    )
    parser.add_argument(
        "--require-canonical",
        action="store_true",
        help=(
            "Require the persisted canonical 64-bank count and exact two-item "
            "startup-media path sequence."
        ),
    )
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    catalog = build_audio_catalog(report)
    if args.require_canonical:
        validate_canonical_audio_catalog(catalog)

    if args.paths_only:
        for path in selected_paths(catalog, args.kind):
            print(path)
    elif args.kind == "all":
        print(json.dumps(catalog, indent=2, sort_keys=True))
    else:
        key = "sound_banks" if args.kind == "banks" else "startup_media"
        print(
            json.dumps(
                {
                    "schema_version": catalog["schema_version"],
                    "source_sha256": catalog["source_sha256"],
                    key: catalog[key],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
