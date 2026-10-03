"""Checksum-gated original FastView score/table art loader.

This module combines only source resources whose exact FM2001 paths, byte sizes,
SHA-256 identities, decoded geometry, owners and placements are already
persisted in the Gate-14 score and LeagueTable contracts.

No original bytes are embedded in Git. A caller supplies an extracted authorized
source root plus the canonical FOOTBAL.EXE, whose EA444 tables/quantization are
independently hash-gated before resource decode.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import TypeAlias

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_fastview_league_table import (
    CURRENT_TABLE_GRID_1,
    CURRENT_TABLE_GRID_2,
    FastViewLeagueTableGridResource,
)
from gate14_fastview_scores import (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
    SCORE_COMPOSITE_PHASE_RESOURCES,
    FastViewScoreGridResource,
    FastViewScorePhaseResource,
)


FastViewScoreTableSource: TypeAlias = (
    FastViewScoreGridResource
    | FastViewScorePhaseResource
    | FastViewLeagueTableGridResource
)

FASTVIEW_SCORE_TABLE_ART_RESOURCES: tuple[FastViewScoreTableSource, ...] = (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
    *SCORE_COMPOSITE_PHASE_RESOURCES,
    CURRENT_TABLE_GRID_1,
    CURRENT_TABLE_GRID_2,
)


class OriginalFastViewScoreTableArtError(ValueError):
    pass


def _is_exact_source_type(value: object) -> bool:
    return type(value) in {
        FastViewScoreGridResource,
        FastViewScorePhaseResource,
        FastViewLeagueTableGridResource,
    }


@dataclass(frozen=True)
class OriginalFastViewScoreTableDecodedResource:
    source: FastViewScoreTableSource
    image: EA444DecodedImage

    def __post_init__(self) -> None:
        if not _is_exact_source_type(self.source):
            raise OriginalFastViewScoreTableArtError(
                "score/table decoded resource requires exact source metadata"
            )
        if not isinstance(self.image, EA444DecodedImage):
            raise OriginalFastViewScoreTableArtError(
                f"decoded score/table art has wrong type: {self.source.name}"
            )
        if (self.image.width, self.image.height) != self.source.size:
            raise OriginalFastViewScoreTableArtError(
                f"decoded score/table geometry mismatch: {self.source.name}"
            )
        if len(self.image.rgba) != self.image.width * self.image.height * 4:
            raise OriginalFastViewScoreTableArtError(
                f"decoded score/table RGBA payload incomplete: {self.source.name}"
            )


@dataclass(frozen=True)
class OriginalFastViewScoreTableArt:
    resources: tuple[OriginalFastViewScoreTableDecodedResource, ...]

    def __post_init__(self) -> None:
        if tuple(item.source for item in self.resources) != FASTVIEW_SCORE_TABLE_ART_RESOURCES:
            raise OriginalFastViewScoreTableArtError(
                "score/table art must preserve exact source resource order"
            )
        names = tuple(item.source.name for item in self.resources)
        if len(set(names)) != len(names):
            raise OriginalFastViewScoreTableArtError(
                "score/table art contains duplicate resource identities"
            )

    def image_for(self, resource: FastViewScoreTableSource) -> EA444DecodedImage:
        if not _is_exact_source_type(resource):
            raise OriginalFastViewScoreTableArtError(
                "score/table lookup requires exact source metadata"
            )
        for item in self.resources:
            if item.source is resource:
                return item.image
        raise OriginalFastViewScoreTableArtError(
            f"score/table source resource is not loaded: {resource.name}"
        )


def build_fastview_score_table_art(
    decoded: dict[str, EA444DecodedImage],
) -> OriginalFastViewScoreTableArt:
    if not isinstance(decoded, dict):
        raise OriginalFastViewScoreTableArtError(
            "score/table decoded art must be keyed by source resource name"
        )

    expected_names = tuple(
        resource.name for resource in FASTVIEW_SCORE_TABLE_ART_RESOURCES
    )
    if set(decoded) != set(expected_names):
        missing = tuple(name for name in expected_names if name not in decoded)
        unexpected = tuple(name for name in decoded if name not in expected_names)
        raise OriginalFastViewScoreTableArtError(
            "score/table decoded resource set differs from exact source family: "
            f"missing={missing}, unexpected={unexpected}"
        )

    return OriginalFastViewScoreTableArt(
        tuple(
            OriginalFastViewScoreTableDecodedResource(
                resource,
                decoded[resource.name],
            )
            for resource in FASTVIEW_SCORE_TABLE_ART_RESOURCES
        )
    )


def _read_verified_score_table_resource(
    source_root: Path,
    resource: FastViewScoreTableSource,
) -> bytes:
    if not _is_exact_source_type(resource):
        raise OriginalFastViewScoreTableArtError(
            "score/table source reader requires exact source metadata"
        )
    path = source_root / Path(resource.source_path)
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewScoreTableArtError(
            f"missing original score/table resource: {resource.source_path}"
        ) from exc

    if len(data) != resource.byte_size:
        raise OriginalFastViewScoreTableArtError(
            f"score/table resource byte-size mismatch: {resource.source_path}"
        )
    if sha256(data).hexdigest() != resource.sha256:
        raise OriginalFastViewScoreTableArtError(
            f"score/table resource checksum mismatch: {resource.source_path}"
        )
    return data


def load_verified_fastview_score_table_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalFastViewScoreTableArt:
    root = Path(source_root)
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewScoreTableArtError(
            f"missing canonical original executable: {original_executable}"
        ) from exc

    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)

    decoded: dict[str, EA444DecodedImage] = {}
    for resource in FASTVIEW_SCORE_TABLE_ART_RESOURCES:
        raw = _read_verified_score_table_resource(root, resource)
        image = decode_ea444(raw, tables=tables, quant=quant)
        if (image.width, image.height) != resource.size:
            raise OriginalFastViewScoreTableArtError(
                f"decoded score/table geometry mismatch: {resource.source_path}"
            )
        decoded[resource.name] = image

    return build_fastview_score_table_art(decoded)
