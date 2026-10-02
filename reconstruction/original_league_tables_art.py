"""Decode the exact source-proven PLeagueTables header background.

Recovery 162 proves that league_bar.444 is owned by PLeagueTables through
panel object +0x788 and is placed at the exact screen rectangle
(270, 152, 475, 19).  This module intentionally exposes only that bounded
pixel layer.  It does not select per-row grid/icon states or render text.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_header import parse_ea444_header
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_league_tables_resources import (
    LEAGUE_TABLES_BAR_RECT,
    LEAGUE_TABLES_RESOURCE_BY_NAME,
    OriginalLeagueTablesResource,
)


class OriginalLeagueTablesArtError(ValueError):
    """The exact League Tables header art cannot be used safely."""


LEAGUE_TABLES_HEADER_RESOURCE = LEAGUE_TABLES_RESOURCE_BY_NAME["league_bar"]


@dataclass(frozen=True)
class OriginalLeagueTablesHeaderArt:
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


def build_league_tables_header_art(
    decoded: EA444DecodedImage,
) -> OriginalLeagueTablesHeaderArt:
    """Bind one decoded original league_bar image to its exact source rectangle."""
    if not isinstance(decoded, EA444DecodedImage):
        raise OriginalLeagueTablesArtError(
            "League Tables header art must be a decoded EA444 image"
        )

    x, y, width, height = LEAGUE_TABLES_BAR_RECT
    if (decoded.width, decoded.height) != (width, height):
        raise OriginalLeagueTablesArtError(
            "Decoded League Tables header geometry does not match the source rectangle"
        )
    expected_rgba = width * height * 4
    if len(decoded.rgba) != expected_rgba:
        raise OriginalLeagueTablesArtError(
            "Decoded League Tables header RGBA payload is incomplete"
        )

    return OriginalLeagueTablesHeaderArt(
        resource_name=LEAGUE_TABLES_HEADER_RESOURCE.name,
        source_path=LEAGUE_TABLES_HEADER_RESOURCE.source_path,
        x=x,
        y=y,
        width=width,
        height=height,
        rgba=decoded.rgba,
    )


def _read_verified_header_resource(
    source_root: Path,
    resource: OriginalLeagueTablesResource = LEAGUE_TABLES_HEADER_RESOURCE,
) -> bytes:
    path = Path(source_root).joinpath(*resource.source_path.split("/"))
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalLeagueTablesArtError(
            f"Missing original League Tables header resource: {resource.source_path}"
        ) from exc

    if len(data) != resource.byte_size:
        raise OriginalLeagueTablesArtError(
            f"League Tables header byte-size mismatch: {resource.source_path}"
        )
    if sha256(data).hexdigest() != resource.sha256:
        raise OriginalLeagueTablesArtError(
            f"League Tables header checksum mismatch: {resource.source_path}"
        )
    header = parse_ea444_header(data)
    if (header.width, header.height) != resource.size:
        raise OriginalLeagueTablesArtError(
            f"League Tables header source geometry mismatch: {resource.source_path}"
        )
    return data


def load_verified_league_tables_header_art(
    source_root: Path,
    original_executable: Path,
) -> OriginalLeagueTablesHeaderArt:
    """Decode the imported original header with the verified executable codec."""
    try:
        exe = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalLeagueTablesArtError(
            f"Missing original executable: {original_executable}"
        ) from exc

    tables = tables_from_original_executable(exe)
    quant = quantization_from_verified_executable(exe)
    decoded = decode_ea444(
        _read_verified_header_resource(Path(source_root)),
        tables=tables,
        quant=quant,
    )
    return build_league_tables_header_art(decoded)
