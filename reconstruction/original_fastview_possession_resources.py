"""Byte-identical original FM2001 FastView possession resources and geometry.

Only the four PossessionDiagram resources are runtime-staged here. Their exact
source paths, hashes, dimensions and placement are source-closed from the
canonical executable and authorized disc. Scheduling and human-team side
orientation remain deliberately outside this module; source timing is modeled
separately from pixel placement.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct

from gate14_possession_diagram import (
    INITIAL_OVERLAY_STATE,
    OVERLAY_PATHS,
    PITCH_NORMAL_PATH,
    PITCH_RECT,
    active_overlay_rect,
)


class OriginalFastViewPossessionResourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewPossessionResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int


PITCH_LEFT = OriginalFastViewPossessionResource(
    "pitch_left", OVERLAY_PATHS[0],
    "bf1cf154f9742b39953771a248c7d1269d8d0394856ab1dc76dd81882b1b29d9",
    9736, (125, 78), 0x8298D4,
)
PITCH_MIDDLE = OriginalFastViewPossessionResource(
    "pitch_middle", OVERLAY_PATHS[1],
    "ad53294836bf1f489060e9339da79fa43f2fb70034c890ea93dbff14f5caee77",
    7896, (98, 78), 0x8298AC,
)
PITCH_RIGHT = OriginalFastViewPossessionResource(
    "pitch_right", OVERLAY_PATHS[2],
    "dedc194dc9410ddc6d606fdabd3fe779a0c1bf0bfdfe85752f9a56d57171e5fd",
    9408, (125, 78), 0x829888,
)
PITCH_NORMAL = OriginalFastViewPossessionResource(
    "pitch_normal", PITCH_NORMAL_PATH,
    "326f484f264630d656e47aee1eb8419970ddbf336fbbc4e47588ff841a346ced",
    18424, (294, 78), 0x8298F8,
)

FASTVIEW_POSSESSION_DIAGRAM_RESOURCES = (
    PITCH_LEFT,
    PITCH_MIDDLE,
    PITCH_RIGHT,
    PITCH_NORMAL,
)
FASTVIEW_POSSESSION_RESOURCE_BY_NAME = {
    resource.name: resource for resource in FASTVIEW_POSSESSION_DIAGRAM_RESOURCES
}
IMPORT_ROOT = Path("original_assets/source")


@dataclass(frozen=True)
class PossessionDiagramLayer:
    resource: OriginalFastViewPossessionResource
    rect: tuple[int, int, int, int]


def possession_diagram_layers(state: int) -> tuple[PossessionDiagramLayer, ...]:
    """Return the exact normal-pitch + active-overlay placement for a state.

    The caller must supply the state. Scheduling and event ordering remain
    separate from this exact pixel-placement primitive.
    """
    if type(state) is not int or state not in (0, 1, 2):
        raise OriginalFastViewPossessionResourceError(
            "PossessionDiagram state must be 0, 1, or 2"
        )
    return (
        PossessionDiagramLayer(PITCH_NORMAL, PITCH_RECT),
        PossessionDiagramLayer(
            (PITCH_LEFT, PITCH_MIDDLE, PITCH_RIGHT)[state],
            active_overlay_rect(state),
        ),
    )


def initial_possession_diagram_layers() -> tuple[PossessionDiagramLayer, ...]:
    return possession_diagram_layers(INITIAL_OVERLAY_STATE)


def imported_resource_path(
    repo_root: Path,
    resource: OriginalFastViewPossessionResource,
) -> Path:
    return Path(repo_root) / IMPORT_ROOT / resource.source_path


def validate_imported_possession_diagram_resources(
    repo_root: Path,
) -> tuple[OriginalFastViewPossessionResource, ...]:
    """Require every byte-identical source-closed diagram file staged in Git."""
    for resource in FASTVIEW_POSSESSION_DIAGRAM_RESOURCES:
        path = imported_resource_path(repo_root, resource)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalFastViewPossessionResourceError(
                f"Missing staged FastView possession resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalFastViewPossessionResourceError(
                f"FastView possession byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalFastViewPossessionResourceError(
                f"FastView possession checksum mismatch: {resource.source_path}"
            )
        if len(data) < 4:
            raise OriginalFastViewPossessionResourceError(
                f"FastView possession resource has no EA444 header: {resource.source_path}"
            )
        width, height = struct.unpack_from("<HH", data, 0)
        if (width, height) != resource.size:
            raise OriginalFastViewPossessionResourceError(
                f"FastView possession geometry mismatch: {resource.source_path}"
            )
    return FASTVIEW_POSSESSION_DIAGRAM_RESOURCES
