"""Fail-closed completed-human FastView presentation bundle.

This module composes only already-established Gate-14 boundaries:

completed human outcome
    -> HumanMatchPresentation / FastViewSemanticShell
    -> FastViewFramePlan
    -> resolved-only FastView PNG preview
    -> exact frame-coverage audit
    -> unresolved-overlap readiness audit
    -> optional caller-owned Tk canvas draw

It does not simulate a match, rerun RNG, invent background/z-order, assign
audio semantics, or synthesize 3D choreography.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from gate14_fastview_frame_coverage import (
    FastViewFrameCoverage,
    audit_fastview_frame_coverage,
)
from gate14_fastview_frame_plan import FastViewFramePlan
from gate14_fastview_human_frame_plan import (
    build_human_fastview_frame_plan,
    build_human_fastview_frame_plan_from_retained_histories,
)
from gate14_fastview_playerrow_from_result import FastViewRetainedPlayerRowIdentity
from gate14_fastview_overlap_readiness import (
    FastViewOverlapReadinessAudit,
    audit_fastview_overlap_readiness,
)
from gate14_fastview_resolved_preview import (
    FastViewResolvedPreview,
    build_fastview_frame_preview,
)
from gate14_fastview_score_table_static_raster import FastViewScoreTableStaticRasterSet
from gate14_fastview_score_draw_phases import FastViewLeagueScoresDrawPhases
from gate14_fastview_score_phase_text_raster import FastViewScorePhaseTextRaster
from gate14_fastview_clock_raster import FastViewClockRaster
from gate14_fastview_direct_header_raster import FastViewDirectHeaderRaster
from gate14_fastview_surfaced_resource_raster import FastViewSurfacedRasterSet
from gate14_fastview_tk_surface import (
    FastViewResolvedTkDraw,
    draw_fastview_preview_on_tk_canvas,
)
from human_match_presentation import HumanMatchOutcomeLike
from original_fastview_chrome_art import OriginalFastViewChromeArt
from original_fastview_possession_art import OriginalFastViewPossessionArtFrame
from original_fastview_possession_figures_art import OriginalFastViewPossessionFiguresArt
from original_fastview_team_art import OriginalFastViewTeamArt


class HumanFastViewResolvedPresentationError(ValueError):
    pass


@dataclass(frozen=True)
class HumanFastViewResolvedPresentation:
    """One integrity-bound partial presentation for a completed human match."""

    frame: FastViewFramePlan
    preview: FastViewResolvedPreview
    coverage: FastViewFrameCoverage
    overlap_readiness: FastViewOverlapReadinessAudit
    complete_fastview_frame: bool = False
    audio_ready: bool = False
    choreography_3d_ready: bool = False

    def __post_init__(self) -> None:
        if type(self.frame) is not FastViewFramePlan:
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation requires exact frame plan"
            )
        if type(self.preview) is not FastViewResolvedPreview:
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation requires exact resolved preview"
            )
        if type(self.coverage) is not FastViewFrameCoverage:
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation requires exact frame coverage"
            )
        if type(self.overlap_readiness) is not FastViewOverlapReadinessAudit:
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation requires exact overlap readiness"
            )

        composite = self.frame.resolved_composite
        expected_rgba_hash = composite.rgba_sha256
        expected_mask_hash = composite.unresolved_overlap_mask_sha256

        if (
            self.preview.source_composite_rgba_sha256 != expected_rgba_hash
            or self.coverage.source_composite_rgba_sha256 != expected_rgba_hash
            or self.overlap_readiness.source_composite_rgba_sha256 != expected_rgba_hash
        ):
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation RGBA source hashes drifted"
            )
        if (
            self.preview.source_overlap_mask_sha256 != expected_mask_hash
            or self.coverage.source_overlap_mask_sha256 != expected_mask_hash
            or self.overlap_readiness.source_overlap_mask_sha256 != expected_mask_hash
        ):
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation overlap-mask source hashes drifted"
            )
        if (
            self.preview.resolved_pixel_count != composite.resolved_pixel_count
            or self.coverage.resolved_pixel_count != composite.resolved_pixel_count
        ):
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation resolved-pixel counts drifted"
            )
        if (
            self.preview.unresolved_overlap_pixel_count
            != composite.unresolved_overlap_pixel_count
            or self.coverage.unresolved_overlap_pixel_count
            != composite.unresolved_overlap_pixel_count
            or self.overlap_readiness.unresolved_overlap_pixel_count
            != composite.unresolved_overlap_pixel_count
        ):
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation overlap counts drifted"
            )
        if (
            self.preview.overlap_groups != composite.unresolved_overlap_groups
            or self.coverage.unresolved_overlap_groups
            != composite.unresolved_overlap_groups
            or tuple(
                (group.components, group.pixel_count, group.bounding_rect)
                for group in self.overlap_readiness.groups
            )
            != tuple(
                (group.components, group.pixel_count, group.bounding_rect)
                for group in composite.unresolved_overlap_groups
            )
        ):
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation overlap topology drifted"
            )
        if (
            self.frame.complete_raster_frame
            or self.frame.audio_ready
            or self.frame.choreography_3d_ready
            or self.preview.cross_component_z_order_recovered
            or self.preview.flattened_frame_available
            or self.preview.complete_fastview_frame
            or self.coverage.cross_component_z_order_recovered
            or self.coverage.background_binding_recovered
            or self.coverage.complete_fastview_frame
            or self.overlap_readiness.cross_component_blend_rule_recovered
            or self.overlap_readiness.all_overlap_pixels_resolvable
            or self.overlap_readiness.complete_fastview_frame
            or self.complete_fastview_frame
            or self.audio_ready
            or self.choreography_3d_ready
        ):
            raise HumanFastViewResolvedPresentationError(
                "human FastView presentation cannot promote unresolved fidelity"
            )


def _presentation_from_frame(
    frame: FastViewFramePlan,
) -> HumanFastViewResolvedPresentation:
    if type(frame) is not FastViewFramePlan:
        raise HumanFastViewResolvedPresentationError(
            "human FastView presentation requires exact frame plan"
        )
    preview = build_fastview_frame_preview(frame)
    coverage = audit_fastview_frame_coverage(frame.resolved_composite)
    overlap_readiness = audit_fastview_overlap_readiness(frame.resolved_composite)
    return HumanFastViewResolvedPresentation(
        frame=frame,
        preview=preview,
        coverage=coverage,
        overlap_readiness=overlap_readiness,
    )


def build_human_fastview_resolved_presentation(
    outcome: HumanMatchOutcomeLike,
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
    team_art: OriginalFastViewTeamArt,
    score_table_static: FastViewScoreTableStaticRasterSet | None = None,
    *,
    score_draw_phases: FastViewLeagueScoresDrawPhases | None = None,
    score_phase_text: FastViewScorePhaseTextRaster | None = None,
    clock: FastViewClockRaster | None = None,
    direct_header: FastViewDirectHeaderRaster | None = None,
    surfaced: FastViewSurfacedRasterSet | None = None,
) -> HumanFastViewResolvedPresentation:
    """Build one source-bounded partial presentation from a completed outcome."""
    frame_kwargs = {"score_table_static": score_table_static}
    for name, value in (
        ("score_draw_phases", score_draw_phases),
        ("score_phase_text", score_phase_text),
        ("clock", clock),
        ("direct_header", direct_header),
        ("surfaced", surfaced),
    ):
        if value is not None:
            frame_kwargs[name] = value
    frame = build_human_fastview_frame_plan(
        outcome,
        chrome,
        possession,
        figures,
        team_art,
        **frame_kwargs,
    )
    return _presentation_from_frame(frame)


def build_human_fastview_resolved_presentation_from_retained_histories(
    outcome: HumanMatchOutcomeLike,
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
    team_art: OriginalFastViewTeamArt,
    *,
    row_identities: tuple[FastViewRetainedPlayerRowIdentity, ...],
    global_tick: int,
    energy_rng6_rolls: Mapping[tuple[int, int], int],
    score_table_static: FastViewScoreTableStaticRasterSet | None = None,
    score_draw_phases: FastViewLeagueScoresDrawPhases | None = None,
    score_phase_text: FastViewScorePhaseTextRaster | None = None,
    clock: FastViewClockRaster | None = None,
    direct_header: FastViewDirectHeaderRaster | None = None,
    surfaced: FastViewSurfacedRasterSet | None = None,
) -> HumanFastViewResolvedPresentation:
    """Use the existing retained-history row path, then bind preview/coverage."""
    frame_kwargs = {
        "row_identities": row_identities,
        "global_tick": global_tick,
        "energy_rng6_rolls": energy_rng6_rolls,
        "score_table_static": score_table_static,
    }
    for name, value in (
        ("score_draw_phases", score_draw_phases),
        ("score_phase_text", score_phase_text),
        ("clock", clock),
        ("direct_header", direct_header),
        ("surfaced", surfaced),
    ):
        if value is not None:
            frame_kwargs[name] = value
    frame = build_human_fastview_frame_plan_from_retained_histories(
        outcome,
        chrome,
        possession,
        figures,
        team_art,
        **frame_kwargs,
    )
    return _presentation_from_frame(frame)


def draw_human_fastview_resolved_presentation(
    presentation: HumanFastViewResolvedPresentation,
    tk_module,
    canvas,
) -> FastViewResolvedTkDraw:
    """Draw only the canonical resolved preview on a caller-owned Tk canvas."""
    if type(presentation) is not HumanFastViewResolvedPresentation:
        raise HumanFastViewResolvedPresentationError(
            "Tk draw requires exact human FastView resolved presentation"
        )
    return draw_fastview_preview_on_tk_canvas(
        presentation.preview,
        tk_module,
        canvas,
    )
