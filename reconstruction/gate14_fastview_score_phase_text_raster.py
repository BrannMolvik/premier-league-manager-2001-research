"""Source-backed transparent raster for ScoreComposite phase labels.

This module turns the exact HT/FT/ET/PEN label contract into a separate
800x600 transparent plane. It deliberately does not merge the labels with the
runtime phase-icon plane: the original helper appends icon then text per
ScoreComposite callback, while cross-row callback order is not yet source-
closed. Keeping the planes separate preserves exact glyph pixels without
inventing a global icon/text z-order.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_phase_text import (
    PHASE_TEXT_NATIVE_COLOR_16,
    FastViewScorePhaseText,
    score_phase_text,
)
from gate14_fastview_scores import (
    FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY,
    fastview_league_scores_page_layout,
    score_composite_phase_rects,
)
from gate14_possession_figures import (
    SOURCE_TEXT_FONT_ATLAS_SIZE,
    SOURCE_TEXT_FONT_BYTE_SIZE,
    SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
    SOURCE_TEXT_FONT_PATH,
    SOURCE_TEXT_FONT_SHA256,
)
from original_live_debug_view import endpoint_text_rgba


class FastViewScorePhaseTextRasterError(ValueError):
    pass


PHASE_RUNTIME_TEXT_COMPONENT = "league_scores_runtime_phase_text"


@dataclass(frozen=True)
class FastViewScorePhaseTextPlacement:
    source_index: int
    source: FastViewScorePhaseText
    control_rect: tuple[int, int, int, int]
    line_origin: tuple[int, int]
    glyph_size: tuple[int, int]

    def __post_init__(self) -> None:
        if type(self.source_index) is not int or self.source_index < 0:
            raise FastViewScorePhaseTextRasterError(
                "phase-text source index must be non-negative"
            )
        if type(self.source) is not FastViewScorePhaseText:
            raise FastViewScorePhaseTextRasterError(
                "phase-text placement requires exact source label evidence"
            )
        if (
            type(self.control_rect) is not tuple
            or len(self.control_rect) != 4
            or any(type(value) is not int for value in self.control_rect)
        ):
            raise FastViewScorePhaseTextRasterError(
                "phase-text control rect must contain four integers"
            )
        if (
            type(self.line_origin) is not tuple
            or len(self.line_origin) != 2
            or any(type(value) is not int for value in self.line_origin)
        ):
            raise FastViewScorePhaseTextRasterError(
                "phase-text line origin must be an integer pair"
            )
        if (
            type(self.glyph_size) is not tuple
            or len(self.glyph_size) != 2
            or any(type(value) is not int or value <= 0 for value in self.glyph_size)
        ):
            raise FastViewScorePhaseTextRasterError(
                "phase-text glyph size must be a positive integer pair"
            )


@dataclass(frozen=True)
class FastViewScorePhaseTextRaster:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    placements: tuple[FastViewScorePhaseTextPlacement, ...]
    rgba_sha256: str
    native_line_height: int = SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT
    native_color_16: int = PHASE_TEXT_NATIVE_COLOR_16
    aggregate_icon_text_order_recovered: bool = False
    flattened_with_runtime_icons: bool = False
    global_fastview_z_order_recovered: bool = False
    complete_fastview_frame_recovered: bool = False

    def __post_init__(self) -> None:
        if self.component != PHASE_RUNTIME_TEXT_COMPONENT:
            raise FastViewScorePhaseTextRasterError(
                "phase-text component identity drifted"
            )
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewScorePhaseTextRasterError(
                "phase-text raster must retain 800x600"
            )
        if len(self.rgba) != self.size[0] * self.size[1] * 4:
            raise FastViewScorePhaseTextRasterError(
                "phase-text RGBA payload has wrong size"
            )
        if (
            type(self.source_layer_count) is not int
            or self.source_layer_count < 0
            or self.source_layer_count != len(self.placements)
        ):
            raise FastViewScorePhaseTextRasterError(
                "phase-text source layer count must match placements"
            )
        if type(self.placements) is not tuple or any(
            type(item) is not FastViewScorePhaseTextPlacement
            for item in self.placements
        ):
            raise FastViewScorePhaseTextRasterError(
                "phase-text placements must use exact records"
            )
        if len({item.source_index for item in self.placements}) != len(
            self.placements
        ):
            raise FastViewScorePhaseTextRasterError(
                "one ScoreComposite row may retain at most one phase label"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewScorePhaseTextRasterError(
                "phase-text RGBA SHA-256 mismatch"
            )
        if self.native_line_height != 20:
            raise FastViewScorePhaseTextRasterError(
                "phase-text native line height drifted"
            )
        if self.native_color_16 != 0xFFFF:
            raise FastViewScorePhaseTextRasterError(
                "phase-text native color drifted"
            )
        if (
            self.aggregate_icon_text_order_recovered
            or self.flattened_with_runtime_icons
            or self.global_fastview_z_order_recovered
            or self.complete_fastview_frame_recovered
        ):
            raise FastViewScorePhaseTextRasterError(
                "phase-text raster cannot promote unresolved ordering/frame fidelity"
            )


def load_verified_phase_text_font(repo_root: str | Path) -> EAFont:
    """Load only the provenance-tracked source font used by style index 1."""
    path = Path(repo_root) / "original_assets" / "source" / SOURCE_TEXT_FONT_PATH
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise FastViewScorePhaseTextRasterError(
            f"missing staged phase-text font: {SOURCE_TEXT_FONT_PATH}"
        ) from exc
    if len(data) != SOURCE_TEXT_FONT_BYTE_SIZE:
        raise FastViewScorePhaseTextRasterError(
            "phase-text font byte-size mismatch"
        )
    if sha256(data).hexdigest() != SOURCE_TEXT_FONT_SHA256:
        raise FastViewScorePhaseTextRasterError(
            "phase-text font checksum mismatch"
        )
    font = EAFont.from_bytes(data)
    if (font.atlas_width, font.atlas_height) != SOURCE_TEXT_FONT_ATLAS_SIZE:
        raise FastViewScorePhaseTextRasterError(
            "phase-text font atlas geometry mismatch"
        )
    if font.native_line_height() != SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT:
        raise FastViewScorePhaseTextRasterError(
            "phase-text font native line-height mismatch"
        )
    return font


def _trunc_half(value: int) -> int:
    """Mirror x86 signed divide-by-two rounding toward zero."""
    if type(value) is not int:
        raise FastViewScorePhaseTextRasterError(
            "centering delta must be integer"
        )
    return value // 2 if value >= 0 else -((-value) // 2)


def phase_text_line_origin(
    font: EAFont,
    source: FastViewScorePhaseText,
    control_rect: tuple[int, int, int, int],
) -> tuple[int, int]:
    """Mirror generic centered-text origin arithmetic for one phase control."""
    if type(font) is not EAFont:
        raise FastViewScorePhaseTextRasterError(
            "phase-text raster requires exact EAFont"
        )
    if type(source) is not FastViewScorePhaseText:
        raise FastViewScorePhaseTextRasterError(
            "phase-text source must be exact source evidence"
        )
    left, top, right, bottom = control_rect
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        raise FastViewScorePhaseTextRasterError(
            "phase-text control rectangle must be positive"
        )
    text_width = font.measure_text(source.text)
    line_height = font.native_line_height()
    return (
        left + _trunc_half(width - text_width),
        top + _trunc_half(height - line_height),
    )


def _draw_clipped_endpoint_text(
    canvas: bytearray,
    *,
    mask_width: int,
    mask_height: int,
    mask_rgba: bytes,
    line_origin: tuple[int, int],
    clip_rect: tuple[int, int, int, int],
) -> None:
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    if len(mask_rgba) != mask_width * mask_height * 4:
        raise FastViewScorePhaseTextRasterError(
            "phase-text mask RGBA geometry mismatch"
        )
    left, top, right, bottom = clip_rect
    origin_x, origin_y = line_origin
    for y in range(mask_height):
        screen_y = origin_y + y
        if screen_y < top or screen_y >= bottom:
            continue
        if not 0 <= screen_y < surface_height:
            continue
        for x in range(mask_width):
            screen_x = origin_x + x
            if screen_x < left or screen_x >= right:
                continue
            if not 0 <= screen_x < surface_width:
                continue
            src = (y * mask_width + x) * 4
            alpha = mask_rgba[src + 3]
            if alpha == 0:
                continue
            dst = (screen_y * surface_width + screen_x) * 4
            # Phase labels for distinct LeagueScores rows cannot overlap
            # because row step 19 exceeds the 16-pixel control height. Max
            # alpha remains fail-closed if a future synthetic input violates
            # that invariant without inventing native blend behavior.
            if alpha > canvas[dst + 3]:
                canvas[dst:dst + 4] = mask_rgba[src:src + 4]


def build_fastview_score_phase_text_raster(
    font: EAFont,
    source_count: int,
    *,
    phase_events_by_source_index: tuple[tuple[int, str], ...] = (),
) -> FastViewScorePhaseTextRaster:
    """Raster exact phase labels on their source ScoreComposite rows."""
    if type(font) is not EAFont:
        raise FastViewScorePhaseTextRasterError(
            "phase-text raster requires exact EAFont"
        )
    if font.native_line_height() != SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT:
        raise FastViewScorePhaseTextRasterError(
            "phase-text font line-height does not match source style"
        )
    if (
        type(source_count) is not int
        or not 1 <= source_count <= FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY
    ):
        raise FastViewScorePhaseTextRasterError(
            "phase-text raster requires one verified 1..12 LeagueScores page"
        )
    if type(phase_events_by_source_index) is not tuple:
        raise FastViewScorePhaseTextRasterError(
            "phase-text event placements must be a tuple"
        )

    canvas = bytearray(FASTVIEW_SURFACE_SIZE[0] * FASTVIEW_SURFACE_SIZE[1] * 4)
    layout = fastview_league_scores_page_layout(source_count)
    placements = []
    seen: set[int] = set()

    for source_index, event_name in phase_events_by_source_index:
        if type(source_index) is not int or not 0 <= source_index < source_count:
            raise FastViewScorePhaseTextRasterError(
                "phase-text source index lies outside visible LeagueScores page"
            )
        if source_index in seen:
            raise FastViewScorePhaseTextRasterError(
                "only one retained phase label may occupy one ScoreComposite"
            )
        seen.add(source_index)

        source = score_phase_text(event_name)
        origin = layout.slot_origin(0, source_index)
        _icon_rect, control_rect = score_composite_phase_rects(origin)
        line_origin = phase_text_line_origin(font, source, control_rect)
        mask = font.render_text_alpha(source.text)
        rgba = endpoint_text_rgba(mask.alpha, source.native_color_16)
        _draw_clipped_endpoint_text(
            canvas,
            mask_width=mask.width,
            mask_height=mask.height,
            mask_rgba=rgba,
            line_origin=line_origin,
            clip_rect=control_rect,
        )
        placements.append(
            FastViewScorePhaseTextPlacement(
                source_index=source_index,
                source=source,
                control_rect=control_rect,
                line_origin=line_origin,
                glyph_size=(mask.width, mask.height),
            )
        )

    payload = bytes(canvas)
    return FastViewScorePhaseTextRaster(
        component=PHASE_RUNTIME_TEXT_COMPONENT,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=payload,
        source_layer_count=len(placements),
        placements=tuple(placements),
        rgba_sha256=sha256(payload).hexdigest(),
    )


def score_phase_text_raster_contract() -> dict:
    return {
        "component": PHASE_RUNTIME_TEXT_COMPONENT,
        "source_font_path": SOURCE_TEXT_FONT_PATH,
        "source_font_sha256": SOURCE_TEXT_FONT_SHA256,
        "source_font_native_line_height": SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
        "native_color_16": PHASE_TEXT_NATIVE_COLOR_16,
        "source_control_size": (28, 16),
        "source_row_step": 19,
        "center_rounding": "signed_truncation_toward_zero",
        "control_clipping_applied": True,
        "exact_phase_text_pixels_recovered": True,
        "aggregate_icon_text_order_recovered": False,
        "flattened_with_runtime_icons": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
    }
