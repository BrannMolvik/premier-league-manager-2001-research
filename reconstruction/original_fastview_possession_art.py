"""Exact decoded art seam for the source-closed FastView possession diagram.

This module deliberately renders only the four byte-identical PossessionDiagram
EA444 resources whose ownership and screen geometry are already source-closed.
It does not synthesize a FastView background, percentage typography, team-side
orientation, score chrome, commentary, audio, or 3D choreography.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_fastview_possession_resources import (
    FASTVIEW_POSSESSION_DIAGRAM_RESOURCES,
    OriginalFastViewPossessionResource,
    OriginalFastViewPossessionResourceError,
    imported_resource_path,
    possession_diagram_layers,
    validate_imported_possession_diagram_resources,
)


class OriginalFastViewPossessionArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewPossessionArtPlacement:
    role: str
    resource_name: str
    source_path: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass(frozen=True)
class OriginalFastViewPossessionArtFrame:
    state: int
    placements: tuple[OriginalFastViewPossessionArtPlacement, ...]
    surrounding_fastview_background_recovered: bool = False
    possession_text_typography_recovered: bool = False
    human_side_orientation_recovered: bool = False

    @property
    def complete_fastview_frame_available(self) -> bool:
        return (
            self.surrounding_fastview_background_recovered
            and self.possession_text_typography_recovered
            and self.human_side_orientation_recovered
        )


def _decoded_for(
    decoded_art: dict[str, EA444DecodedImage],
    resource: OriginalFastViewPossessionResource,
) -> EA444DecodedImage:
    try:
        image = decoded_art[resource.name]
    except KeyError as exc:
        raise OriginalFastViewPossessionArtError(
            f"Missing decoded FastView possession art: {resource.name}"
        ) from exc
    if not isinstance(image, EA444DecodedImage):
        raise OriginalFastViewPossessionArtError(
            f"Decoded FastView possession art has wrong type: {resource.name}"
        )
    if (image.width, image.height) != resource.size:
        raise OriginalFastViewPossessionArtError(
            f"Decoded FastView possession geometry mismatch: {resource.name}"
        )
    if len(image.rgba) != image.width * image.height * 4:
        raise OriginalFastViewPossessionArtError(
            f"Decoded FastView possession RGBA payload is incomplete: {resource.name}"
        )
    return image


def build_fastview_possession_art(
    decoded_art: dict[str, EA444DecodedImage],
    state: int,
) -> OriginalFastViewPossessionArtFrame:
    """Build only the exact base-pitch + active-overlay source placements."""
    if not isinstance(decoded_art, dict):
        raise OriginalFastViewPossessionArtError(
            "FastView possession decoded art must be keyed by resource name"
        )
    try:
        layers = possession_diagram_layers(state)
    except OriginalFastViewPossessionResourceError as exc:
        raise OriginalFastViewPossessionArtError(str(exc)) from exc

    placements = []
    for index, layer in enumerate(layers):
        image = _decoded_for(decoded_art, layer.resource)
        left, top, right, bottom = layer.rect
        width = right - left
        height = bottom - top
        if (width, height) != (image.width, image.height):
            raise OriginalFastViewPossessionArtError(
                f"FastView placement/image geometry drifted: {layer.resource.name}"
            )
        placements.append(
            OriginalFastViewPossessionArtPlacement(
                role="base_pitch" if index == 0 else "active_overlay",
                resource_name=layer.resource.name,
                source_path=layer.resource.source_path,
                x=left,
                y=top,
                width=width,
                height=height,
                rgba=image.rgba,
            )
        )
    return OriginalFastViewPossessionArtFrame(
        state=state,
        placements=tuple(placements),
    )


def load_verified_fastview_possession_art(
    repo_root: str | Path,
    original_executable: str | Path,
    state: int,
) -> OriginalFastViewPossessionArtFrame:
    """Decode staged originals with the canonical executable's EA444 tables."""
    root = Path(repo_root)
    validate_imported_possession_diagram_resources(root)
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewPossessionArtError(
            f"Missing original executable: {original_executable}"
        ) from exc

    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    decoded = {}
    for resource in FASTVIEW_POSSESSION_DIAGRAM_RESOURCES:
        decoded[resource.name] = decode_ea444(
            imported_resource_path(root, resource).read_bytes(),
            tables=tables,
            quant=quant,
        )
    return build_fastview_possession_art(decoded, state)
