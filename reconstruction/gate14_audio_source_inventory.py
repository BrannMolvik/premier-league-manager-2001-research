"""Deterministic Gate-14 inventory of source-disc audio/media candidates.

This tool classifies only source paths that are already visible in the Joliet
catalog. A .bnk suffix is recorded neutrally as a bank candidate; no sound,
music, commentary, or cue semantics are inferred from its filename.

The two startup TGQs are stronger: their ownership, hashes, embedded audio and
startup callsites are already source-backed in research/STARTUP_PRESENTATION.md.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
from typing import Iterable, Protocol

from gate13_source_inventory import (
    DiscFileRecord,
    catalog_iso_image,
    is_mode1_2352_image,
    normalize_member,
)
from iso9660_reader import IsoImage, RawMode1IsoImage


STARTUP_TGQ_PATHS = (
    "FMV/easp.tgq",
    "FMV/premintro.tgq",
)


class DiscFileLike(Protocol):
    path: str
    size: int


@dataclass(frozen=True)
class Gate14AudioSourceRecord:
    path: str
    size: int
    source_kind: str

    def __post_init__(self) -> None:
        if int(self.size) < 0:
            raise ValueError("source file size cannot be negative")
        if self.source_kind not in {
            "bank_candidate",
            "startup_tgq",
            "other_tgq",
        }:
            raise ValueError("unsupported Gate-14 audio source kind")


@dataclass(frozen=True)
class Gate14AudioSourceInventory:
    records: tuple[Gate14AudioSourceRecord, ...]

    @property
    def bank_candidates(self) -> tuple[Gate14AudioSourceRecord, ...]:
        return tuple(item for item in self.records if item.source_kind == "bank_candidate")

    @property
    def startup_tgqs(self) -> tuple[Gate14AudioSourceRecord, ...]:
        return tuple(item for item in self.records if item.source_kind == "startup_tgq")

    @property
    def other_tgqs(self) -> tuple[Gate14AudioSourceRecord, ...]:
        return tuple(item for item in self.records if item.source_kind == "other_tgq")


def _classify(path: str) -> str | None:
    normalized = normalize_member(path)
    lowered = normalized.casefold()
    startup = {item.casefold() for item in STARTUP_TGQ_PATHS}
    if lowered in startup:
        return "startup_tgq"
    suffix = PurePosixPath(normalized).suffix.casefold()
    if suffix == ".bnk":
        return "bank_candidate"
    if suffix == ".tgq":
        return "other_tgq"
    return None


def build_gate14_audio_source_inventory(
    files: Iterable[DiscFileLike],
) -> Gate14AudioSourceInventory:
    """Select only deterministic bank/TGQ candidates from a source catalog."""
    selected: list[Gate14AudioSourceRecord] = []
    seen: set[str] = set()
    for item in files:
        normalized = normalize_member(item.path)
        key = normalized.casefold()
        if key in seen:
            raise ValueError(f"duplicate source path in Gate-14 catalog: {normalized}")
        seen.add(key)
        kind = _classify(normalized)
        if kind is None:
            continue
        selected.append(
            Gate14AudioSourceRecord(
                path=normalized,
                size=int(item.size),
                source_kind=kind,
            )
        )
    selected.sort(key=lambda item: item.path.casefold())
    return Gate14AudioSourceInventory(tuple(selected))


def inventory_disc_image(path: Path) -> Gate14AudioSourceInventory:
    """Read an ISO/Joliet or raw MODE1/2352 source image without extraction."""
    source = Path(path)
    image = RawMode1IsoImage(source) if is_mode1_2352_image(source) else IsoImage(source)
    return build_gate14_audio_source_inventory(catalog_iso_image(image))


def render_inventory(inventory: Gate14AudioSourceInventory, source: Path) -> dict:
    return {
        "schema_version": 1,
        "source": str(Path(source).resolve()),
        "bank_candidate_count": len(inventory.bank_candidates),
        "startup_tgq_count": len(inventory.startup_tgqs),
        "other_tgq_count": len(inventory.other_tgqs),
        "records": [asdict(item) for item in inventory.records],
        "semantic_boundary": {
            "bank_suffix_semantics_recovered": False,
            "bank_entry_semantics_recovered": False,
            "startup_tgq_ownership_recovered": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disc_image", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    inventory = inventory_disc_image(args.disc_image)
    rendered = json.dumps(
        render_inventory(inventory, args.disc_image),
        indent=2,
        sort_keys=True,
    ) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
