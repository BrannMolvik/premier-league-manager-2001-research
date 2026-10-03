"""Decoded original-art seam for source-closed FastViewTeam resources.

This module makes the seven exact TeamTable EA444 assets consumable by the
modern presentation layer without inventing the unresolved parts of PlayerRow
rasterization. It deliberately does not flatten text, assign cross-component
z-order, or guess how a resized dynamic PictureControl maps source pixels.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_fastview_team import FastViewTeamResource
from original_fastview_team_resources import (
    FASTVIEW_TEAM_TABLE_RESOURCES,
    OriginalFastViewTeamResourceError,
    source_resource_path,
    validate_source_fastview_team_resources,
)


class OriginalFastViewTeamArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewTeamDecodedResource:
    resource_name: str
    source_path: str
    width: int
    height: int
    rgba: bytes


@dataclass(frozen=True)
class OriginalFastViewTeamArt:
    resources: tuple[OriginalFastViewTeamDecodedResource, ...]
    generic_text_rasterization_available: bool = False
    dynamic_picture_crop_mapping_recovered: bool = False
    cross_component_z_order_recovered: bool = False
    complete_team_table_raster_available: bool = False

    def resource_named(self, name: str) -> OriginalFastViewTeamDecodedResource:
        matches = tuple(item for item in self.resources if item.resource_name == name)
        if len(matches) != 1:
            raise OriginalFastViewTeamArtError(
                f"Expected one decoded FastViewTeam resource named {name!r}"
            )
        return matches[0]


def _decoded_for(
    decoded: dict[str, EA444DecodedImage],
    resource: FastViewTeamResource,
) -> EA444DecodedImage:
    try:
        image = decoded[resource.name]
    except KeyError as exc:
        raise OriginalFastViewTeamArtError(
            f"Missing decoded FastViewTeam art: {resource.name}"
        ) from exc
    if not isinstance(image, EA444DecodedImage):
        raise OriginalFastViewTeamArtError(
            f"Decoded FastViewTeam art has wrong type: {resource.name}"
        )
    if (image.width, image.height) != resource.size:
        raise OriginalFastViewTeamArtError(
            f"Decoded FastViewTeam geometry mismatch: {resource.name}"
        )
    if len(image.rgba) != image.width * image.height * 4:
        raise OriginalFastViewTeamArtError(
            f"Decoded FastViewTeam RGBA payload incomplete: {resource.name}"
        )
    return image


def build_fastview_team_art(
    decoded: dict[str, EA444DecodedImage],
) -> OriginalFastViewTeamArt:
    """Expose exact decoded assets while keeping unresolved raster seams closed."""
    if not isinstance(decoded, dict):
        raise OriginalFastViewTeamArtError(
            "FastViewTeam decoded art must be keyed by source resource name"
        )
    resources = []
    for resource in FASTVIEW_TEAM_TABLE_RESOURCES:
        image = _decoded_for(decoded, resource)
        resources.append(
            OriginalFastViewTeamDecodedResource(
                resource_name=resource.name,
                source_path=resource.source_path,
                width=image.width,
                height=image.height,
                rgba=image.rgba,
            )
        )
    return OriginalFastViewTeamArt(tuple(resources))


def load_verified_fastview_team_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalFastViewTeamArt:
    """Validate and decode the exact original TeamTable assets from source_root."""
    try:
        validate_source_fastview_team_resources(source_root)
    except OriginalFastViewTeamResourceError as exc:
        raise OriginalFastViewTeamArtError(str(exc)) from exc
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewTeamArtError(
            f"Missing original executable: {original_executable}"
        ) from exc

    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    decoded = {}
    for resource in FASTVIEW_TEAM_TABLE_RESOURCES:
        decoded[resource.name] = decode_ea444(
            source_resource_path(source_root, resource).read_bytes(),
            tables=tables,
            quant=quant,
        )
    return build_fastview_team_art(decoded)
