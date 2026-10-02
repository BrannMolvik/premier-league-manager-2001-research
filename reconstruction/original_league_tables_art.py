"""Decode only the source-proven PLeagueTables header band for live composition.

The full League Tables row-art selector still depends on source position thresholds
and a neutral helper byte whose runtime identity is not yet exposed through the
presentation bridge.  This module therefore renders only the exact league_bar.444
control at its recovered PLeagueTables rectangle and keeps every row background
fail-closed until that selector can be projected without guessing.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_league_tables_resources import (
    LEAGUE_TABLES_BAR_RECT,
    LEAGUE_TABLES_RESOURCE_BY_NAME,
    LEAGUE_TABLES_RESOURCES,
    validate_original_league_tables_resources,
)


class OriginalLeagueTablesArtError(ValueError):
    """The League Tables header cannot be rendered from verified source art."""


@dataclass(frozen=True)
class OriginalLeagueTablesHeaderArt:
    resource_name: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes
    staged_resource_names: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.resource_name != "league_bar":
            raise OriginalLeagueTablesArtError(
                "League Tables header art must be the source-bound league_bar resource"
            )
        if (self.x, self.y, self.width, self.height) != LEAGUE_TABLES_BAR_RECT:
            raise OriginalLeagueTablesArtError(
                "League Tables header placement drifted from the recovered rectangle"
            )
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalLeagueTablesArtError(
                "League Tables header RGBA payload does not match source geometry"
            )
        required = tuple(resource.name for resource in LEAGUE_TABLES_RESOURCES)
        if tuple(self.staged_resource_names) != required:
            raise OriginalLeagueTablesArtError(
                "League Tables live art requires the exact staged resource family"
            )


def build_league_tables_header_art(
    image: EA444DecodedImage,
    *,
    staged_resource_names: tuple[str, ...],
) -> OriginalLeagueTablesHeaderArt:
    """Bind a decoded exact league_bar image to its source-proven control rect."""
    resource = LEAGUE_TABLES_RESOURCE_BY_NAME["league_bar"]
    if not isinstance(image, EA444DecodedImage):
        raise OriginalLeagueTablesArtError(
            "League Tables header requires a decoded EA444 source image"
        )
    if (image.width, image.height) != resource.size:
        raise OriginalLeagueTablesArtError(
            "Decoded league_bar geometry differs from the verified source resource"
        )
    x, y, width, height = LEAGUE_TABLES_BAR_RECT
    return OriginalLeagueTablesHeaderArt(
        resource_name=resource.name,
        x=x,
        y=y,
        width=width,
        height=height,
        rgba=image.rgba,
        staged_resource_names=tuple(staged_resource_names),
    )


def load_verified_league_tables_header_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalLeagueTablesHeaderArt:
    """Validate all staged table art, then decode only the proven header band."""
    root = Path(source_root)
    validated = validate_original_league_tables_resources(root)
    resource = LEAGUE_TABLES_RESOURCE_BY_NAME["league_bar"]

    executable = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    image = decode_ea444(
        (root / resource.source_path).read_bytes(),
        tables=tables,
        quant=quant,
    )
    return build_league_tables_header_art(
        image,
        staged_resource_names=tuple(item.name for item in validated),
    )
