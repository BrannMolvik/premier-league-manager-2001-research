"""Source-backed panel-owned pixels for the normal management canvas.

This module deliberately composes only graphics whose concrete management-panel
owner and screen placement are already recovered.  It is separate from the
PMenu compositor because the application-wide surrounding background remains an
independent unresolved ownership boundary.

Recovery 179 integrates the exact PLeagueFixtures grid setup:
- 12 full fixtures_vert_grid.444 placements at (378 + 29*n, 98);
- 24 full fixtures_hori_grid.444 placements at (241, 235 + 14*n).

The four 24x13 fixture-cell wrappers are intentionally not placed here.  Their
state-selection semantics are recovered, but their final screen-pixel placement
has not yet been source-closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from gate13_original_pixel_preview import encode_rgba_png
from original_league_fixtures_art import (
    OriginalLeagueFixturesGridArt,
    load_verified_league_fixtures_grid_art,
)
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_RESOURCES,
    validate_original_league_fixtures_resources,
)
from original_management_canvas import OriginalManagementCanvasFrame
from original_management_navigation import LEAGUE_FIXTURES_PANEL


class OriginalManagementPanelCanvasError(ValueError):
    """A management panel cannot be rendered from the recovered source boundary."""


@dataclass(frozen=True)
class OriginalManagementPanelResources:
    league_fixtures_grid_art: OriginalLeagueFixturesGridArt
    league_fixtures_resource_names: tuple[str, ...]

    def __post_init__(self) -> None:
        expected = tuple(resource.name for resource in LEAGUE_FIXTURES_RESOURCES)
        if self.league_fixtures_resource_names != expected:
            raise OriginalManagementPanelCanvasError(
                "League Fixtures staged resource identity differs from source contract"
            )


@dataclass(frozen=True)
class OriginalManagementPanelOverlay:
    role: str
    panel_class: str
    x: int
    y: int
    width: int
    height: int
    png: bytes
    source_path: str


@dataclass(frozen=True)
class OriginalManagementPanelRender:
    panel_class: str
    overlays: tuple[OriginalManagementPanelOverlay, ...]
    unresolved_pixel_boundaries: tuple[str, ...]


def load_verified_management_panel_resources(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalManagementPanelResources:
    """Validate all imported fixture art and decode only placement-proven grids."""
    root = Path(source_root)
    validated = validate_original_league_fixtures_resources(root)
    grid = load_verified_league_fixtures_grid_art(
        root,
        Path(original_executable),
    )
    return OriginalManagementPanelResources(
        league_fixtures_grid_art=grid,
        league_fixtures_resource_names=tuple(resource.name for resource in validated),
    )


def build_management_panel_render(
    frame: OriginalManagementCanvasFrame,
    resources: OriginalManagementPanelResources,
) -> OriginalManagementPanelRender:
    """Project only source-owned panel pixels for the currently selected panel."""
    if not isinstance(frame, OriginalManagementCanvasFrame):
        raise OriginalManagementPanelCanvasError(
            "Panel rendering requires an OriginalManagementCanvasFrame"
        )
    if not isinstance(resources, OriginalManagementPanelResources):
        raise OriginalManagementPanelCanvasError(
            "Panel rendering requires verified original management resources"
        )

    presentation = frame.presentation
    if presentation.panel_class != LEAGUE_FIXTURES_PANEL.panel_class:
        return OriginalManagementPanelRender(
            panel_class=presentation.panel_class,
            overlays=(),
            unresolved_pixel_boundaries=(
                "panel-specific pixel composition is not yet integrated",
            ),
        )
    if presentation.league_fixtures is None:
        raise OriginalManagementPanelCanvasError(
            "PLeagueFixtures render requires its source-backed matrix snapshot"
        )
    if not presentation.league_fixtures.exact_art_staged:
        raise OriginalManagementPanelCanvasError(
            "PLeagueFixtures render requires all six exact imported resources staged"
        )

    overlays = tuple(
        OriginalManagementPanelOverlay(
            role="league_fixtures_grid",
            panel_class=LEAGUE_FIXTURES_PANEL.panel_class,
            x=item.x,
            y=item.y,
            width=item.width,
            height=item.height,
            png=encode_rgba_png(item.width, item.height, item.rgba),
            source_path=item.source_path,
        )
        for item in resources.league_fixtures_grid_art.placements
    )
    return OriginalManagementPanelRender(
        panel_class=presentation.panel_class,
        overlays=overlays,
        unresolved_pixel_boundaries=(
            "fixture-cell 24x13 final placement/text composition",
            "League Fixtures selector/header/footer pixels outside recovered grid art",
            "application-owned surrounding management background",
        ),
    )
