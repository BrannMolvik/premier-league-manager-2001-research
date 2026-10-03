"""Fail-closed layout contract for source-bound FastView visual fragments.

This module combines only screen rectangles that are already independently
source-closed:

- directly PictureControl-bound FastView top/ticker chrome;
- PossessionDiagram base/active art placements;
- PossessionFigures percentage text placements;
- explicitly selected TeamTable row/control geometry whose row indices are
  supplied by the caller rather than inferred.

It deliberately does not flatten those fragments into one RGBA frame. The
percentage controls overlap the possession diagram in the recovered 800x600
coordinate space, while a cross-component draw/z order has not yet been
promoted as source-backed. The loose FastView/background.444 path is also
explicitly unbound.

Therefore this is a layout/overlap contract for a future player-visible
renderer, not a complete original FastView frame.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_background import BACKGROUND_BINDING_STATUS
from gate14_fastview_team import (
    side_contract,
    team_row_name_resource,
    team_row_rects,
)
from original_fastview_chrome_art import OriginalFastViewChromeArt
from original_fastview_possession_art import OriginalFastViewPossessionArtFrame
from original_fastview_possession_figures_art import (
    OriginalFastViewPossessionFiguresArt,
)


FASTVIEW_SURFACE_SIZE = (800, 600)


class FastViewPartialSurfaceError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewPartialSurfaceLayer:
    component: str
    identity: str
    rect: tuple[int, int, int, int]
    raster_available: bool = True

    def __post_init__(self) -> None:
        if self.component not in {
            "direct_chrome",
            "possession_diagram",
            "possession_figures_text",
            "team_table_geometry",
        }:
            raise FastViewPartialSurfaceError("unknown FastView partial component")
        if not isinstance(self.identity, str) or not self.identity:
            raise FastViewPartialSurfaceError("FastView layer identity must be nonempty")
        if type(self.raster_available) is not bool:
            raise FastViewPartialSurfaceError(
                "FastView layer raster_available must be boolean"
            )
        if (
            type(self.rect) is not tuple
            or len(self.rect) != 4
            or any(type(value) is not int for value in self.rect)
        ):
            raise FastViewPartialSurfaceError("FastView layer rect must be four integers")
        left, top, right, bottom = self.rect
        width, height = FASTVIEW_SURFACE_SIZE
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise FastViewPartialSurfaceError(
                "FastView layer rect must stay inside the recovered 800x600 surface"
            )


@dataclass(frozen=True)
class FastViewTeamRowSelection:
    """One caller-explicit TeamTable row to expose in the partial surface."""

    side_index: int
    row_index: int

    def __post_init__(self) -> None:
        if type(self.side_index) is not int or self.side_index not in (0, 1):
            raise FastViewPartialSurfaceError(
                "FastView TeamTable side_index must be 0 or 1"
            )
        if type(self.row_index) is not int or self.row_index < 0:
            raise FastViewPartialSurfaceError(
                "FastView TeamTable row_index must be non-negative"
            )


@dataclass(frozen=True)
class FastViewPartialSurfaceOverlap:
    first_layer_index: int
    second_layer_index: int
    rect: tuple[int, int, int, int]


@dataclass(frozen=True)
class FastViewPartialSurfaceLayout:
    size: tuple[int, int]
    layers: tuple[FastViewPartialSurfaceLayer, ...]
    cross_component_overlaps: tuple[FastViewPartialSurfaceOverlap, ...]
    background_binding_status: str
    cross_component_z_order_recovered: bool = False
    raster_composition_available: bool = False
    complete_fastview_frame_available: bool = False

    def __post_init__(self) -> None:
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewPartialSurfaceError("FastView partial surface must be 800x600")
        if self.cross_component_z_order_recovered:
            raise FastViewPartialSurfaceError(
                "cross-component FastView z-order is not source-closed"
            )
        if self.raster_composition_available or self.complete_fastview_frame_available:
            raise FastViewPartialSurfaceError(
                "partial layout cannot claim flattened or complete FastView output"
            )


def _intersection(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> tuple[int, int, int, int] | None:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    if left >= right or top >= bottom:
        return None
    return (left, top, right, bottom)


def _cross_component_overlaps(
    layers: tuple[FastViewPartialSurfaceLayer, ...],
) -> tuple[FastViewPartialSurfaceOverlap, ...]:
    overlaps = []
    for first_index, first in enumerate(layers):
        for second_index in range(first_index + 1, len(layers)):
            second = layers[second_index]
            if first.component == second.component:
                continue
            rect = _intersection(first.rect, second.rect)
            if rect is not None:
                overlaps.append(
                    FastViewPartialSurfaceOverlap(
                        first_layer_index=first_index,
                        second_layer_index=second_index,
                        rect=rect,
                    )
                )
    return tuple(overlaps)


def build_fastview_partial_surface_layout(
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
    *,
    team_rows: tuple[FastViewTeamRowSelection, ...] = (),
) -> FastViewPartialSurfaceLayout:
    """Collect exact placements without inventing a cross-component draw order."""
    if type(chrome) is not OriginalFastViewChromeArt:
        raise FastViewPartialSurfaceError("chrome must be exact FastView chrome art")
    if type(possession) is not OriginalFastViewPossessionArtFrame:
        raise FastViewPartialSurfaceError(
            "possession must be exact FastView possession art"
        )
    if type(figures) is not OriginalFastViewPossessionFiguresArt:
        raise FastViewPartialSurfaceError(
            "figures must be exact FastView possession typography"
        )
    if type(team_rows) is not tuple:
        raise FastViewPartialSurfaceError(
            "team_rows must be an explicit tuple of FastViewTeamRowSelection"
        )
    if any(type(row) is not FastViewTeamRowSelection for row in team_rows):
        raise FastViewPartialSurfaceError(
            "team_rows must contain only FastViewTeamRowSelection values"
        )
    row_keys = tuple((row.side_index, row.row_index) for row in team_rows)
    if len(set(row_keys)) != len(row_keys):
        raise FastViewPartialSurfaceError(
            "duplicate FastView TeamTable row selections are not allowed"
        )

    layers: list[FastViewPartialSurfaceLayer] = []

    for placement in chrome.placements:
        layers.append(
            FastViewPartialSurfaceLayer(
                component="direct_chrome",
                identity=placement.resource_name,
                rect=placement.rect,
            )
        )

    for placement in possession.placements:
        layers.append(
            FastViewPartialSurfaceLayer(
                component="possession_diagram",
                identity=f"{placement.role}:{placement.resource_name}",
                rect=placement.rect,
            )
        )

    for row in figures.rows:
        if row.line_origin != row.source.rect[:2]:
            raise FastViewPartialSurfaceError(
                "PossessionFigures line origin drifted from source control origin"
            )
        if row.clip_rect != row.source.rect:
            raise FastViewPartialSurfaceError(
                "PossessionFigures clip rect drifted from source control"
            )
        identity = (
            "neutral"
            if row.source.side_index is None
            else f"side{row.source.side_index}"
        )
        layers.append(
            FastViewPartialSurfaceLayer(
                component="possession_figures_text",
                identity=identity,
                rect=row.clip_rect,
            )
        )

    for selection in team_rows:
        contract = side_contract(selection.side_index)
        name_resource = team_row_name_resource(
            selection.side_index,
            selection.row_index,
        )
        name_rect, bar_rect, text_rects = team_row_rects(
            selection.side_index,
            selection.row_index,
        )
        prefix = f"side{selection.side_index}:row{selection.row_index}"
        layers.append(
            FastViewPartialSurfaceLayer(
                component="team_table_geometry",
                identity=f"{prefix}:name_grid:{name_resource.name}",
                rect=name_rect,
                raster_available=name_resource.imported,
            )
        )
        layers.append(
            FastViewPartialSurfaceLayer(
                component="team_table_geometry",
                identity=(
                    f"{prefix}:energy_bar:"
                    f"{contract.static_energy_bar.name}+"
                    f"{contract.dynamic_energy_bar.name}"
                ),
                rect=bar_rect,
                raster_available=(
                    contract.static_energy_bar.imported
                    and contract.dynamic_energy_bar.imported
                ),
            )
        )
        for cell_index, rect in enumerate(text_rects, start=1):
            layers.append(
                FastViewPartialSurfaceLayer(
                    component="team_table_geometry",
                    identity=f"{prefix}:text_cell:{cell_index}",
                    rect=rect,
                    raster_available=False,
                )
            )

    layer_tuple = tuple(layers)
    return FastViewPartialSurfaceLayout(
        size=FASTVIEW_SURFACE_SIZE,
        layers=layer_tuple,
        cross_component_overlaps=_cross_component_overlaps(layer_tuple),
        background_binding_status=BACKGROUND_BINDING_STATUS,
    )
