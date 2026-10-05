"""Source-order LeagueScores raster phases.

The historical league_scores_static plane aggregates native children that sit
on both sides of LeagueTableComposite. This module exposes only source-backed
pixel layers that can be assigned to distinct native phases:

1. ScoreCompositeNormal grid-2 rows created by 0x522CD0 -> 0x523CC0;
2. the separately rasterized LeagueTableComposite block;
3. current_fix_grid_1 created later at 0x5239F3;
4. event-driven ScoreComposite phase icons appended at the current parent tail.

The paired phase text and other later LeagueScores controls remain omitted.
No flattened/global FastView z-order is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_scores import (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
    FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY,
    FASTVIEW_LEAGUE_SCORES_SCORE_FACTORY_VA,
    SCORE_COMPOSITE_PHASE_DISPLAY_CLEAR_VA,
    SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA,
    fastview_league_scores_grid_rects,
    fastview_league_scores_page_layout,
    score_composite_normal_page_slot_rects,
    score_composite_phase_rects,
    score_composite_phase_resource,
)
from original_fastview_score_table_art import OriginalFastViewScoreTableArt


class FastViewScoreDrawPhaseError(ValueError):
    pass


FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA = 0x5233C2
LEAGUE_TABLE_COMPOSITE_CALLSITE_VA = 0x523472
LEAGUE_SCORES_CURRENT_FIX_GRID_1_CALLSITE_VA = 0x5239F3

PHASE_EARLY_SCORE_ROWS = "league_scores_early_rows_static"
PHASE_LATE_GRID = "league_scores_late_grid_static"
PHASE_RUNTIME_ICONS = "league_scores_runtime_phase_icons"

SOURCE_CLOSED_STATIC_PHASE_ORDER = (
    PHASE_EARLY_SCORE_ROWS,
    "league_table_static",
    PHASE_LATE_GRID,
)


@dataclass(frozen=True)
class FastViewScoreDrawPhasePlane:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    rgba_sha256: str
    native_phase: str
    runtime_tail: bool = False
    complete_component: bool = False

    def __post_init__(self) -> None:
        if self.component not in {
            PHASE_EARLY_SCORE_ROWS,
            PHASE_LATE_GRID,
            PHASE_RUNTIME_ICONS,
        }:
            raise FastViewScoreDrawPhaseError("unknown LeagueScores draw phase")
        if self.native_phase != self.component:
            raise FastViewScoreDrawPhaseError("native phase identity drifted")
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewScoreDrawPhaseError("draw phase must retain 800x600")
        if len(self.rgba) != self.size[0] * self.size[1] * 4:
            raise FastViewScoreDrawPhaseError("draw phase RGBA payload has wrong size")
        if type(self.source_layer_count) is not int or self.source_layer_count < 0:
            raise FastViewScoreDrawPhaseError("source layer count must be non-negative")
        if self.component != PHASE_RUNTIME_ICONS and self.source_layer_count <= 0:
            raise FastViewScoreDrawPhaseError("static draw phase requires source pixels")
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewScoreDrawPhaseError("draw phase SHA-256 mismatch")
        if self.runtime_tail != (self.component == PHASE_RUNTIME_ICONS):
            raise FastViewScoreDrawPhaseError("runtime-tail classification drifted")
        if self.complete_component:
            raise FastViewScoreDrawPhaseError(
                "partial score draw phase cannot claim complete component"
            )


@dataclass(frozen=True)
class FastViewLeagueScoresDrawPhases:
    early_score_rows: FastViewScoreDrawPhasePlane
    late_grid: FastViewScoreDrawPhasePlane
    runtime_phase_icons: FastViewScoreDrawPhasePlane
    league_table_between_static_phases: bool = True
    runtime_phase_icons_append_at_current_tail: bool = True
    paired_phase_text_rasterized: bool = False
    aggregate_score_plane_has_single_z_position: bool = False
    global_fastview_z_order_recovered: bool = False
    complete_fastview_frame_recovered: bool = False

    def __post_init__(self) -> None:
        expected = (
            (self.early_score_rows, PHASE_EARLY_SCORE_ROWS),
            (self.late_grid, PHASE_LATE_GRID),
            (self.runtime_phase_icons, PHASE_RUNTIME_ICONS),
        )
        for plane, component in expected:
            if type(plane) is not FastViewScoreDrawPhasePlane:
                raise FastViewScoreDrawPhaseError("draw phases require exact planes")
            if plane.component != component:
                raise FastViewScoreDrawPhaseError("draw-phase component mismatch")
        if not self.league_table_between_static_phases:
            raise FastViewScoreDrawPhaseError(
                "source requires LeagueTable between early rows and late grid"
            )
        if not self.runtime_phase_icons_append_at_current_tail:
            raise FastViewScoreDrawPhaseError(
                "source phase helper appends controls at current parent tail"
            )
        if (
            self.paired_phase_text_rasterized
            or self.aggregate_score_plane_has_single_z_position
            or self.global_fastview_z_order_recovered
            or self.complete_fastview_frame_recovered
        ):
            raise FastViewScoreDrawPhaseError(
                "draw-phase split cannot promote unresolved FastView fidelity"
            )


def _blank_surface() -> bytearray:
    return bytearray(FASTVIEW_SURFACE_SIZE[0] * FASTVIEW_SURFACE_SIZE[1] * 4)


def _alpha_over(
    canvas: bytearray,
    source_rgba: bytes,
    rect: tuple[int, int, int, int],
) -> None:
    if type(rect) is not tuple or len(rect) != 4:
        raise FastViewScoreDrawPhaseError("placement rect must contain four values")
    left, top, right, bottom = rect
    if any(type(value) is not int for value in rect):
        raise FastViewScoreDrawPhaseError("placement rect must contain integers")
    width, height = right - left, bottom - top
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    if not (
        0 <= left < right <= surface_width
        and 0 <= top < bottom <= surface_height
    ):
        raise FastViewScoreDrawPhaseError("placement lies outside FastView surface")
    if len(source_rgba) != width * height * 4:
        raise FastViewScoreDrawPhaseError("source pixels do not match placement")

    for y in range(height):
        for x in range(width):
            src = (y * width + x) * 4
            alpha = source_rgba[src + 3]
            if alpha == 0:
                continue
            dst = ((top + y) * surface_width + left + x) * 4
            if alpha == 255:
                canvas[dst:dst + 4] = source_rgba[src:src + 4]
                continue
            inv = 255 - alpha
            dst_alpha = canvas[dst + 3]
            out_alpha = alpha + (dst_alpha * inv + 127) // 255
            if out_alpha == 0:
                continue
            for channel in range(3):
                src_premul = source_rgba[src + channel] * alpha
                dst_premul = (
                    canvas[dst + channel] * dst_alpha * inv + 127
                ) // 255
                canvas[dst + channel] = (
                    src_premul + dst_premul + out_alpha // 2
                ) // out_alpha
            canvas[dst + 3] = out_alpha


def _plane(
    component: str,
    canvas: bytearray,
    layers: int,
) -> FastViewScoreDrawPhasePlane:
    rgba = bytes(canvas)
    return FastViewScoreDrawPhasePlane(
        component=component,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        source_layer_count=layers,
        rgba_sha256=sha256(rgba).hexdigest(),
        native_phase=component,
        runtime_tail=(component == PHASE_RUNTIME_ICONS),
    )


def build_fastview_league_scores_draw_phases(
    art: OriginalFastViewScoreTableArt,
    source_count: int,
    *,
    phase_events_by_source_index: tuple[tuple[int, str], ...] = (),
) -> FastViewLeagueScoresDrawPhases:
    """Rasterize source-backed LeagueScores pixels at their native phase positions."""
    if type(art) is not OriginalFastViewScoreTableArt:
        raise FastViewScoreDrawPhaseError("draw phases require exact score/table art")
    if (
        type(source_count) is not int
        or not 1 <= source_count <= FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY
    ):
        raise FastViewScoreDrawPhaseError(
            "LeagueScores draw phases require one verified 1..12 visible page"
        )
    if type(phase_events_by_source_index) is not tuple:
        raise FastViewScoreDrawPhaseError("phase event placements must be a tuple")

    early = _blank_surface()
    grid2 = art.image_for(CURRENT_FIX_GRID_2)
    for source_index in range(source_count):
        grid_rect, _ = score_composite_normal_page_slot_rects(
            source_count, 0, source_index
        )
        _alpha_over(early, grid2.rgba, grid_rect)

    late = _blank_surface()
    grid1 = art.image_for(CURRENT_FIX_GRID_1)
    grid1_rects = fastview_league_scores_grid_rects(source_count)
    if len(grid1_rects) != 1:
        raise FastViewScoreDrawPhaseError(
            "LeagueScores late grid must retain one source strip"
        )
    _alpha_over(late, grid1.rgba, grid1_rects[0])

    runtime = _blank_surface()
    layout = fastview_league_scores_page_layout(source_count)
    seen: set[int] = set()
    runtime_layers = 0
    for source_index, event_name in phase_events_by_source_index:
        if type(source_index) is not int or not 0 <= source_index < source_count:
            raise FastViewScoreDrawPhaseError(
                "phase event source index lies outside visible LeagueScores page"
            )
        if source_index in seen:
            raise FastViewScoreDrawPhaseError(
                "only one retained phase icon may occupy one ScoreComposite"
            )
        seen.add(source_index)
        origin = layout.slot_origin(0, source_index)
        icon_rect, _paired_text_rect = score_composite_phase_rects(origin)
        resource = score_composite_phase_resource(event_name)
        _alpha_over(runtime, art.image_for(resource).rgba, icon_rect)
        runtime_layers += 1

    return FastViewLeagueScoresDrawPhases(
        early_score_rows=_plane(PHASE_EARLY_SCORE_ROWS, early, source_count),
        late_grid=_plane(PHASE_LATE_GRID, late, 1),
        runtime_phase_icons=_plane(
            PHASE_RUNTIME_ICONS,
            runtime,
            runtime_layers,
        ),
    )


def score_draw_phase_contract() -> dict:
    """Expose the source-order boundary without promoting global z-order."""
    return {
        "score_entry_build_callsite_va": FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA,
        "score_factory_va": FASTVIEW_LEAGUE_SCORES_SCORE_FACTORY_VA,
        "league_table_callsite_va": LEAGUE_TABLE_COMPOSITE_CALLSITE_VA,
        "late_grid_callsite_va": LEAGUE_SCORES_CURRENT_FIX_GRID_1_CALLSITE_VA,
        "phase_set_va": SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA,
        "phase_clear_va": SCORE_COMPOSITE_PHASE_DISPLAY_CLEAR_VA,
        "static_phase_order": SOURCE_CLOSED_STATIC_PHASE_ORDER,
        "runtime_phase_icons_append_at_current_tail": True,
        "paired_phase_text_rasterized": False,
        "aggregate_score_plane_has_single_z_position": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
    }
