"""Decode and place only the source-proven PLeagueFixtures grid art.

Recovery 150 proves that PLeagueFixtures setup binds fixtures_vert_grid.444
twelve times at exact screen-space origins and fixtures_hori_grid.444 twenty-
four times at exact screen-space origins.  The source images overlap by design.

This module stops at that evidence boundary.  It does not place the four
24x13 fixture-box resources, render fixture/date text, synthesize surrounding
panel pixels, or infer any additional clipping/layering beyond the recovered
bitmap setup calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_header import parse_ea444_header
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_league_fixtures_resources import (
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
    LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
    LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
    OriginalLeagueFixturesResource,
)


class OriginalLeagueFixturesArtError(ValueError):
    """The original League Fixtures grid art cannot be used safely."""


@dataclass(frozen=True)
class OriginalLeagueFixturesGridArtPlacement:
    resource_name: str
    source_path: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


@dataclass(frozen=True)
class OriginalLeagueFixturesGridArt:
    vertical: tuple[OriginalLeagueFixturesGridArtPlacement, ...]
    horizontal: tuple[OriginalLeagueFixturesGridArtPlacement, ...]

    @property
    def placements(self) -> tuple[OriginalLeagueFixturesGridArtPlacement, ...]:
        return self.vertical + self.horizontal

    @property
    def resource_names(self) -> tuple[str, ...]:
        return (FIXTURES_VERTICAL_GRID.name, FIXTURES_HORIZONTAL_GRID.name)


def _decoded_for(
    decoded_art: dict[str, EA444DecodedImage],
    resource: OriginalLeagueFixturesResource,
) -> EA444DecodedImage:
    try:
        image = decoded_art[resource.name]
    except KeyError as exc:
        raise OriginalLeagueFixturesArtError(
            f"Missing decoded League Fixtures grid art: {resource.name}"
        ) from exc
    if not isinstance(image, EA444DecodedImage):
        raise OriginalLeagueFixturesArtError(
            f"Decoded League Fixtures grid art has wrong type: {resource.name}"
        )
    if (image.width, image.height) != resource.size:
        raise OriginalLeagueFixturesArtError(
            f"Decoded League Fixtures grid geometry mismatch: {resource.name}"
        )
    expected = image.width * image.height * 4
    if len(image.rgba) != expected:
        raise OriginalLeagueFixturesArtError(
            f"Decoded League Fixtures RGBA payload is incomplete: {resource.name}"
        )
    return image


def _placements(
    resource: OriginalLeagueFixturesResource,
    image: EA444DecodedImage,
    positions: tuple[tuple[int, int], ...],
) -> tuple[OriginalLeagueFixturesGridArtPlacement, ...]:
    return tuple(
        OriginalLeagueFixturesGridArtPlacement(
            resource_name=resource.name,
            source_path=resource.source_path,
            x=x,
            y=y,
            width=image.width,
            height=image.height,
            rgba=image.rgba,
        )
        for x, y in positions
    )


def build_league_fixtures_grid_art(
    decoded_art: dict[str, EA444DecodedImage],
) -> OriginalLeagueFixturesGridArt:
    """Project exactly the 36 source bitmap setup calls recovered at 0x46AA70."""
    if not isinstance(decoded_art, dict):
        raise OriginalLeagueFixturesArtError(
            "League Fixtures decoded art must be keyed by source resource name"
        )

    vertical = _decoded_for(decoded_art, FIXTURES_VERTICAL_GRID)
    horizontal = _decoded_for(decoded_art, FIXTURES_HORIZONTAL_GRID)
    return OriginalLeagueFixturesGridArt(
        vertical=_placements(
            FIXTURES_VERTICAL_GRID,
            vertical,
            LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
        ),
        horizontal=_placements(
            FIXTURES_HORIZONTAL_GRID,
            horizontal,
            LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
        ),
    )


def _read_verified_resource(
    source_root: Path,
    resource: OriginalLeagueFixturesResource,
) -> bytes:
    path = Path(source_root).joinpath(*resource.source_path.split("/"))
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalLeagueFixturesArtError(
            f"Missing original League Fixtures resource: {resource.source_path}"
        ) from exc
    if len(data) != resource.byte_size:
        raise OriginalLeagueFixturesArtError(
            f"League Fixtures byte-size mismatch: {resource.source_path}"
        )
    if sha256(data).hexdigest() != resource.sha256:
        raise OriginalLeagueFixturesArtError(
            f"League Fixtures checksum mismatch: {resource.source_path}"
        )
    header = parse_ea444_header(data)
    if (header.width, header.height) != resource.size:
        raise OriginalLeagueFixturesArtError(
            f"League Fixtures source geometry mismatch: {resource.source_path}"
        )
    return data


def load_verified_league_fixtures_grid_art(
    source_root: Path,
    original_executable: Path,
) -> OriginalLeagueFixturesGridArt:
    """Decode the two exact grid resources using the verified original codec tables.

    This loader deliberately requires the source-owned .444 files.  It never
    substitutes generated placeholders when those assets have not yet been
    provenance-imported into the repository.
    """
    try:
        exe = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalLeagueFixturesArtError(
            f"Missing original executable: {original_executable}"
        ) from exc

    tables = tables_from_original_executable(exe)
    quant = quantization_from_verified_executable(exe)
    decoded = {}
    for resource in (FIXTURES_VERTICAL_GRID, FIXTURES_HORIZONTAL_GRID):
        decoded[resource.name] = decode_ea444(
            _read_verified_resource(Path(source_root), resource),
            tables=tables,
            quant=quant,
        )
    return build_league_fixtures_grid_art(decoded)
