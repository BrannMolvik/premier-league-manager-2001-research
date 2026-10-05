"""Immutable Gate-14 frame plan built only from retained presentation state.

This is a composition boundary, not a rasterizer. It combines the semantic
FastView shell with its already validated PlayerRow render plans and the
fail-closed 800x600 partial-surface layout. It never reruns simulation or RNG,
resolves localization, invents cross-component z-order, or claims audio/3D
presentation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastview_semantic_shell import FastViewSemanticShell
from gate14_fastview_component_rasters import (
    FastViewComponentRasterSet,
    build_fastview_component_rasters,
)
from gate14_fastview_resolved_composite import (
    FastViewResolvedOnlyComposite,
    compose_fastview_resolved_only_pixels,
    ordered_fastview_component_planes,
)
from gate14_fastview_partial_surface import (
    FastViewPartialSurfaceLayout,
    build_fastview_partial_surface_from_render_plans,
)
from gate14_fastview_team_energy_raster import rasterize_fastview_team_energy_rows
from gate14_fastview_team_text_raster import rasterize_fastview_playerrow_text
from gate14_fastview_playerrows_raster import compose_fastview_player_rows_raster
from gate14_fastview_score_table_static_raster import FastViewScoreTableStaticRasterSet
from gate14_fastview_score_draw_phases import FastViewLeagueScoresDrawPhases
from gate14_fastview_score_phase_text_raster import FastViewScorePhaseTextRaster
from gate14_fastview_clock_raster import FastViewClockRaster
from gate14_fastview_direct_header_raster import FastViewDirectHeaderRaster
from gate14_fastview_surfaced_resource_raster import FastViewSurfacedRasterSet
from gate14_fastview_playerrow_snapshot import (
    FastViewPlayerRowRenderPlan,
    build_fastview_player_row_render_plan,
)
from original_fastview_chrome_art import OriginalFastViewChromeArt
from original_fastview_team_art import OriginalFastViewTeamArt
from original_fastview_possession_art import OriginalFastViewPossessionArtFrame
from original_fastview_possession_figures_art import (
    OriginalFastViewPossessionFiguresArt,
)
from runtime_layout import application_root


class FastViewFramePlanError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewFramePlan:
    match_reference: object
    semantic_shell: FastViewSemanticShell
    surface_layout: FastViewPartialSurfaceLayout
    component_rasters: FastViewComponentRasterSet
    resolved_composite: FastViewResolvedOnlyComposite
    player_row_render_plans: tuple[FastViewPlayerRowRenderPlan, ...]
    complete_raster_frame: bool = False
    audio_ready: bool = False
    choreography_3d_ready: bool = False

    def __post_init__(self) -> None:
        if self.player_row_render_plans != self.semantic_shell.player_row_render_plans:
            raise FastViewFramePlanError(
                "frame plan PlayerRow instructions must match semantic shell"
            )
        if type(self.component_rasters) is not FastViewComponentRasterSet:
            raise FastViewFramePlanError(
                "frame plan requires exact source-backed component rasters"
            )
        if type(self.resolved_composite) is not FastViewResolvedOnlyComposite:
            raise FastViewFramePlanError(
                "frame plan requires exact resolved-only FastView composite"
            )
        planes = ordered_fastview_component_planes(self.component_rasters)
        expected_source_hashes = tuple(
            (plane.component, plane.rgba_sha256)
            for plane in planes
        )
        if self.resolved_composite.source_plane_sha256 != expected_source_hashes:
            raise FastViewFramePlanError(
                "resolved-only composite does not match frame component rasters"
            )
        if (
            self.component_rasters.cross_component_z_order_recovered
            or self.component_rasters.flattened_frame_available
        ):
            raise FastViewFramePlanError(
                "frame plan cannot promote unresolved cross-component raster order"
            )
        if (
            self.complete_raster_frame
            or self.audio_ready
            or self.choreography_3d_ready
        ):
            raise FastViewFramePlanError(
                "Gate-14 frame plan cannot promote unresolved fidelity boundaries"
            )
        if (
            self.surface_layout.raster_composition_available
            or self.surface_layout.complete_fastview_frame_available
        ):
            raise FastViewFramePlanError(
                "frame plan requires the fail-closed partial FastView surface"
            )


def build_fastview_frame_plan(
    shell: FastViewSemanticShell,
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
    team_art: OriginalFastViewTeamArt,
    score_table_static: FastViewScoreTableStaticRasterSet | None = None,
    *,
    asset_root: str | Path | None = None,
    score_draw_phases: FastViewLeagueScoresDrawPhases | None = None,
    score_phase_text: FastViewScorePhaseTextRaster | None = None,
    clock: FastViewClockRaster | None = None,
    direct_header: FastViewDirectHeaderRaster | None = None,
    surfaced: FastViewSurfacedRasterSet | None = None,
) -> FastViewFramePlan:
    """Compose one renderer input from already retained/source-closed state.

    Every optional presentation value is accepted only as an already-built,
    source-verified artifact. asset_root defaults to the runtime application
    root so the same provenance-tracked PlayerRow font path works in
    development and frozen packages. This layer never derives fixture/table
    counts, phase state, clock/header text, or surfaced selections.
    """
    if type(shell) is not FastViewSemanticShell:
        raise FastViewFramePlanError("shell must be an exact FastViewSemanticShell")

    if len(shell.player_rows) != len(shell.player_row_render_plans):
        raise FastViewFramePlanError(
            "semantic shell PlayerRow snapshot/render-plan counts differ"
        )

    for row, retained_plan in zip(
        shell.player_rows,
        shell.player_row_render_plans,
        strict=True,
    ):
        expected_plan = build_fastview_player_row_render_plan(row)
        if retained_plan != expected_plan:
            raise FastViewFramePlanError(
                "semantic shell contains a drifted PlayerRow render plan"
            )

    surface = build_fastview_partial_surface_from_render_plans(
        chrome,
        possession,
        figures,
        render_plans=shell.player_row_render_plans,
    )
    team_energy = rasterize_fastview_team_energy_rows(
        team_art,
        shell.player_row_render_plans,
    )
    root = application_root() if asset_root is None else Path(asset_root).resolve()
    team_text = rasterize_fastview_playerrow_text(
        root,
        shell.player_row_render_plans,
    )
    player_rows = compose_fastview_player_rows_raster(
        team_energy,
        team_text,
        shell.player_row_render_plans,
    )
    component_kwargs = {"score_table": score_table_static}
    for name, value in (
        ("score_draw_phases", score_draw_phases),
        ("score_phase_text", score_phase_text),
        ("clock", clock),
        ("direct_header", direct_header),
        ("surfaced", surfaced),
    ):
        if value is not None:
            component_kwargs[name] = value
    component_rasters = build_fastview_component_rasters(
        chrome,
        possession,
        figures,
        player_rows,
        **component_kwargs,
    )

    resolved_composite = compose_fastview_resolved_only_pixels(component_rasters)

    return FastViewFramePlan(
        match_reference=shell.match_reference,
        semantic_shell=shell,
        surface_layout=surface,
        component_rasters=component_rasters,
        resolved_composite=resolved_composite,
        player_row_render_plans=shell.player_row_render_plans,
    )
