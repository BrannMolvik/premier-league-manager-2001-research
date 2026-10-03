"""Static source-backed FastView score and LeagueTable raster planes.

This module consumes only checksum-gated original score/table art plus exact
layout contracts already recovered from the canonical executable. It deliberately
renders no unresolved text and does not flatten these planes with other FastView
components.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_league_table import (
    CURRENT_TABLE_GRID_1,
    CURRENT_TABLE_GRID_2,
    league_table_heading_rects,
    league_table_row_rects,
    league_table_visible_row_count,
)
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_scores import (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
    FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY,
    fastview_league_scores_grid_rects,
    fastview_league_scores_page_layout,
    score_composite_normal_page_slot_rects,
    score_composite_phase_rects,
    score_composite_phase_resource,
)
from original_fastview_score_table_art import OriginalFastViewScoreTableArt


class FastViewScoreTableStaticRasterError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewScoreTableStaticPlane:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    rgba_sha256: str
    text_rasterized: bool = False
    complete_component: bool = False

    def __post_init__(self) -> None:
        if self.component not in {"league_scores_static", "league_table_static"}:
            raise FastViewScoreTableStaticRasterError("unknown score/table raster component")
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewScoreTableStaticRasterError(
                "score/table static plane must retain the 800x600 FastView surface"
            )
        if len(self.rgba) != self.size[0] * self.size[1] * 4:
            raise FastViewScoreTableStaticRasterError(
                "score/table static plane RGBA payload has wrong size"
            )
        if type(self.source_layer_count) is not int or self.source_layer_count <= 0:
            raise FastViewScoreTableStaticRasterError(
                "score/table static plane requires at least one source layer"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewScoreTableStaticRasterError(
                "score/table static plane SHA-256 does not match RGBA payload"
            )
        if self.text_rasterized or self.complete_component:
            raise FastViewScoreTableStaticRasterError(
                "static score/table plane cannot promote unresolved text/completeness"
            )


@dataclass(frozen=True)
class FastViewScoreTableStaticRasterSet:
    league_scores: FastViewScoreTableStaticPlane
    league_table: FastViewScoreTableStaticPlane
    cross_component_z_order_recovered: bool = False
    flattened_frame_available: bool = False

    def __post_init__(self) -> None:
        if self.league_scores.component != "league_scores_static":
            raise FastViewScoreTableStaticRasterError(
                "league-scores plane identity mismatch"
            )
        if self.league_table.component != "league_table_static":
            raise FastViewScoreTableStaticRasterError(
                "league-table plane identity mismatch"
            )
        if self.cross_component_z_order_recovered or self.flattened_frame_available:
            raise FastViewScoreTableStaticRasterError(
                "score/table cross-component composition remains unresolved"
            )


def _blank_surface() -> bytearray:
    return bytearray(FASTVIEW_SURFACE_SIZE[0] * FASTVIEW_SURFACE_SIZE[1] * 4)


def _alpha_over(
    canvas: bytearray,
    source_rgba: bytes,
    rect: tuple[int, int, int, int],
) -> None:
    if (
        type(rect) is not tuple
        or len(rect) != 4
        or any(type(value) is not int for value in rect)
    ):
        raise FastViewScoreTableStaticRasterError("source rect must contain four integers")
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    if not (
        0 <= left < right <= surface_width
        and 0 <= top < bottom <= surface_height
    ):
        raise FastViewScoreTableStaticRasterError(
            "source rect lies outside the 800x600 FastView surface"
        )
    if len(source_rgba) != width * height * 4:
        raise FastViewScoreTableStaticRasterError(
            "source RGBA does not match placement geometry"
        )

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


def _plane(component: str, canvas: bytearray, layer_count: int) -> FastViewScoreTableStaticPlane:
    rgba = bytes(canvas)
    return FastViewScoreTableStaticPlane(
        component=component,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        source_layer_count=layer_count,
        rgba_sha256=sha256(rgba).hexdigest(),
    )


def rasterize_fastview_league_scores_static(
    art: OriginalFastViewScoreTableArt,
    source_count: int,
    *,
    phase_events_by_source_index: tuple[tuple[int, str], ...] = (),
) -> FastViewScoreTableStaticPlane:
    """Rasterize source-proven fixture grids and optional typed phase icons.

    Paging above 24 source entries remains outside this static slice because the
    recovered contract describes one visible page only. Phase labels are not
    rasterized.
    """
    if type(art) is not OriginalFastViewScoreTableArt:
        raise FastViewScoreTableStaticRasterError(
            "league-scores raster requires exact source-art bundle"
        )
    if type(source_count) is not int or not 1 <= source_count <= FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY:
        raise FastViewScoreTableStaticRasterError(
            "league-scores source_count must be within the recovered visible page"
        )
    if type(phase_events_by_source_index) is not tuple:
        raise FastViewScoreTableStaticRasterError("phase event placements must be a tuple")

    canvas = _blank_surface()
    layers = 0

    grid1 = art.image_for(CURRENT_FIX_GRID_1)
    for rect in fastview_league_scores_grid_rects(source_count):
        _alpha_over(canvas, grid1.rgba, rect)
        layers += 1

    grid2 = art.image_for(CURRENT_FIX_GRID_2)
    layout = fastview_league_scores_page_layout(source_count)
    for source_index in range(source_count):
        if layout.columns == 1:
            column, row = 0, source_index
        else:
            column, row = divmod(source_index, layout.rows_per_column)
        grid_rect, _text_rects = score_composite_normal_page_slot_rects(
            source_count,
            column,
            row,
        )
        _alpha_over(canvas, grid2.rgba, grid_rect)
        layers += 1

    seen_indices: set[int] = set()
    for source_index, event_name in phase_events_by_source_index:
        if type(source_index) is not int or not 0 <= source_index < source_count:
            raise FastViewScoreTableStaticRasterError(
                "phase event source index is outside the visible score page"
            )
        if source_index in seen_indices:
            raise FastViewScoreTableStaticRasterError(
                "only one retained phase icon may occupy a score composite"
            )
        seen_indices.add(source_index)
        if layout.columns == 1:
            column, row = 0, source_index
        else:
            column, row = divmod(source_index, layout.rows_per_column)
        origin = layout.slot_origin(column, row)
        icon_rect, _text_rect = score_composite_phase_rects(origin)
        resource = score_composite_phase_resource(event_name)
        icon = art.image_for(resource)
        _alpha_over(canvas, icon.rgba, icon_rect)
        layers += 1

    return _plane("league_scores_static", canvas, layers)


def rasterize_fastview_league_table_static(
    art: OriginalFastViewScoreTableArt,
    source_count: int,
) -> FastViewScoreTableStaticPlane:
    """Rasterize heading and exact visible row-grid count; no table text."""
    if type(art) is not OriginalFastViewScoreTableArt:
        raise FastViewScoreTableStaticRasterError(
            "league-table raster requires exact source-art bundle"
        )
    visible_rows = league_table_visible_row_count(source_count)

    canvas = _blank_surface()
    heading_image = art.image_for(CURRENT_TABLE_GRID_1)
    heading_rect, _heading_text = league_table_heading_rects()
    _alpha_over(canvas, heading_image.rgba, heading_rect)
    layers = 1

    row_image = art.image_for(CURRENT_TABLE_GRID_2)
    for row_index in range(visible_rows):
        row_rect, _row_text = league_table_row_rects(row_index)
        _alpha_over(canvas, row_image.rgba, row_rect)
        layers += 1

    return _plane("league_table_static", canvas, layers)


def build_fastview_score_table_static_rasters(
    art: OriginalFastViewScoreTableArt,
    *,
    league_scores_source_count: int,
    league_table_source_count: int,
    phase_events_by_source_index: tuple[tuple[int, str], ...] = (),
) -> FastViewScoreTableStaticRasterSet:
    return FastViewScoreTableStaticRasterSet(
        league_scores=rasterize_fastview_league_scores_static(
            art,
            league_scores_source_count,
            phase_events_by_source_index=phase_events_by_source_index,
        ),
        league_table=rasterize_fastview_league_table_static(
            art,
            league_table_source_count,
        ),
    )
