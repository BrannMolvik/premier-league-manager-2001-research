"""Exact white-endpoint raster for the two direct FastView header TextControls.

The source closes both direct header controls as centered style-3 TextControls
using the exact Zurich_XCn_BT_18pixel.fnt font and native color 0xFFFF. This
module rasterizes already source-backed final strings only. It does not invent
match type, referee identity, stadium, attendance, or bind missing runtime
metadata.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from gate14_fastview_direct_header_text import (
    FIRST_TEXT_RECT,
    SECOND_TEXT_RECT,
    TEXT_FONT_PATH,
    TEXT_FONT_SOURCE_SHA256,
    TEXT_FONT_SOURCE_SIZE,
    TEXT_NATIVE_COLOR_16,
)
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from original_live_debug_view import endpoint_text_rgba


class FastViewDirectHeaderRasterError(ValueError):
    pass


DIRECT_HEADER_TEXT_COMPONENT = "direct_header_text"
DIRECT_HEADER_FONT_ATLAS_SIZE = (1366, 19)
DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT = 20


@dataclass(frozen=True)
class FastViewDirectHeaderPlacement:
    text: str
    control_rect: tuple[int, int, int, int]
    line_origin: tuple[int, int]
    glyph_size: tuple[int, int]

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text:
            raise FastViewDirectHeaderRasterError(
                "direct header placement requires non-empty source text"
            )
        if self.control_rect not in (FIRST_TEXT_RECT, SECOND_TEXT_RECT):
            raise FastViewDirectHeaderRasterError(
                "direct header placement uses an unknown source rectangle"
            )
        if (
            type(self.line_origin) is not tuple
            or len(self.line_origin) != 2
            or any(type(value) is not int for value in self.line_origin)
        ):
            raise FastViewDirectHeaderRasterError(
                "direct header line origin must be an integer pair"
            )
        if (
            type(self.glyph_size) is not tuple
            or len(self.glyph_size) != 2
            or any(type(value) is not int or value <= 0 for value in self.glyph_size)
        ):
            raise FastViewDirectHeaderRasterError(
                "direct header glyph size must be a positive integer pair"
            )


@dataclass(frozen=True)
class FastViewDirectHeaderRaster:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    placements: tuple[FastViewDirectHeaderPlacement, ...]
    rgba_sha256: str
    native_line_height: int = DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT
    native_color_16: int = TEXT_NATIVE_COLOR_16
    final_strings_source_backed: bool = True
    runtime_metadata_bound: bool = False
    global_fastview_z_order_recovered: bool = False
    complete_fastview_frame_recovered: bool = False

    def __post_init__(self) -> None:
        if self.component != DIRECT_HEADER_TEXT_COMPONENT:
            raise FastViewDirectHeaderRasterError(
                "direct header raster component identity drifted"
            )
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewDirectHeaderRasterError(
                "direct header raster must retain 800x600"
            )
        if len(self.rgba) != self.size[0] * self.size[1] * 4:
            raise FastViewDirectHeaderRasterError(
                "direct header RGBA payload has wrong size"
            )
        if self.source_layer_count != 2 or len(self.placements) != 2:
            raise FastViewDirectHeaderRasterError(
                "direct header raster requires exactly two source text layers"
            )
        if tuple(item.control_rect for item in self.placements) != (
            FIRST_TEXT_RECT,
            SECOND_TEXT_RECT,
        ):
            raise FastViewDirectHeaderRasterError(
                "direct header placement order/rectangles drifted"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewDirectHeaderRasterError(
                "direct header RGBA SHA-256 mismatch"
            )
        if self.native_line_height != DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT:
            raise FastViewDirectHeaderRasterError(
                "direct header native line height drifted"
            )
        if self.native_color_16 != TEXT_NATIVE_COLOR_16:
            raise FastViewDirectHeaderRasterError(
                "direct header native color drifted"
            )
        if not self.final_strings_source_backed:
            raise FastViewDirectHeaderRasterError(
                "direct header raster cannot accept inferred final strings"
            )
        if (
            self.runtime_metadata_bound
            or self.global_fastview_z_order_recovered
            or self.complete_fastview_frame_recovered
        ):
            raise FastViewDirectHeaderRasterError(
                "direct header raster cannot promote unresolved runtime/frame fidelity"
            )


def load_verified_direct_header_font(repo_root: str | Path) -> EAFont:
    """Load only the provenance-tracked source font used by these controls."""
    path = Path(repo_root) / "original_assets" / "source" / Path(*TEXT_FONT_PATH.split("\\"))
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise FastViewDirectHeaderRasterError(
            f"missing staged direct-header font: {TEXT_FONT_PATH}"
        ) from exc
    if len(data) != TEXT_FONT_SOURCE_SIZE:
        raise FastViewDirectHeaderRasterError(
            "direct-header font byte-size mismatch"
        )
    if sha256(data).hexdigest() != TEXT_FONT_SOURCE_SHA256:
        raise FastViewDirectHeaderRasterError(
            "direct-header font checksum mismatch"
        )
    font = EAFont.from_bytes(data)
    if (font.atlas_width, font.atlas_height) != DIRECT_HEADER_FONT_ATLAS_SIZE:
        raise FastViewDirectHeaderRasterError(
            "direct-header font atlas geometry mismatch"
        )
    if font.native_line_height() != DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT:
        raise FastViewDirectHeaderRasterError(
            "direct-header font native line-height mismatch"
        )
    return font


def _trunc_half(value: int) -> int:
    """Mirror x86 signed divide-by-two rounding toward zero."""
    if type(value) is not int:
        raise FastViewDirectHeaderRasterError(
            "centering delta must be integer"
        )
    return value // 2 if value >= 0 else -((-value) // 2)


def direct_header_line_origin(
    font: EAFont,
    text: str,
    control_rect: tuple[int, int, int, int],
) -> tuple[int, int]:
    """Mirror generic centered TextControl line-origin arithmetic."""
    if type(font) is not EAFont:
        raise FastViewDirectHeaderRasterError(
            "direct header raster requires exact EAFont"
        )
    if not isinstance(text, str) or not text:
        raise FastViewDirectHeaderRasterError(
            "direct header text must be non-empty"
        )
    if control_rect not in (FIRST_TEXT_RECT, SECOND_TEXT_RECT):
        raise FastViewDirectHeaderRasterError(
            "direct header control rectangle is not source-backed"
        )
    left, top, right, bottom = control_rect
    return (
        left + _trunc_half((right - left) - font.measure_text(text)),
        top + _trunc_half((bottom - top) - font.native_line_height()),
    )


def _draw_clipped(
    canvas: bytearray,
    *,
    source_rgba: bytes,
    width: int,
    height: int,
    origin: tuple[int, int],
    clip_rect: tuple[int, int, int, int],
) -> None:
    if len(source_rgba) != width * height * 4:
        raise FastViewDirectHeaderRasterError(
            "direct header glyph RGBA geometry mismatch"
        )
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    left, top, right, bottom = clip_rect
    origin_x, origin_y = origin
    for y in range(height):
        screen_y = origin_y + y
        if not top <= screen_y < bottom or not 0 <= screen_y < surface_height:
            continue
        for x in range(width):
            screen_x = origin_x + x
            if not left <= screen_x < right or not 0 <= screen_x < surface_width:
                continue
            src = (y * width + x) * 4
            if source_rgba[src + 3] == 0:
                continue
            dst = (screen_y * surface_width + screen_x) * 4
            canvas[dst:dst + 4] = source_rgba[src:src + 4]


def build_fastview_direct_header_raster(
    font: EAFont,
    first_text: str,
    second_text: str,
) -> FastViewDirectHeaderRaster:
    """Raster two already source-backed final strings with exact source clips."""
    if type(font) is not EAFont:
        raise FastViewDirectHeaderRasterError(
            "direct header raster requires exact EAFont"
        )
    if font.native_line_height() != DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT:
        raise FastViewDirectHeaderRasterError(
            "direct header font line-height does not match source style"
        )

    canvas = bytearray(FASTVIEW_SURFACE_SIZE[0] * FASTVIEW_SURFACE_SIZE[1] * 4)
    placements = []
    for text, rect in (
        (first_text, FIRST_TEXT_RECT),
        (second_text, SECOND_TEXT_RECT),
    ):
        origin = direct_header_line_origin(font, text, rect)
        mask = font.render_text_alpha(text)
        rgba = endpoint_text_rgba(mask.alpha, TEXT_NATIVE_COLOR_16)
        _draw_clipped(
            canvas,
            source_rgba=rgba,
            width=mask.width,
            height=mask.height,
            origin=origin,
            clip_rect=rect,
        )
        placements.append(
            FastViewDirectHeaderPlacement(
                text=text,
                control_rect=rect,
                line_origin=origin,
                glyph_size=(mask.width, mask.height),
            )
        )

    payload = bytes(canvas)
    return FastViewDirectHeaderRaster(
        component=DIRECT_HEADER_TEXT_COMPONENT,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=payload,
        source_layer_count=2,
        placements=tuple(placements),
        rgba_sha256=sha256(payload).hexdigest(),
    )


def direct_header_raster_contract() -> dict:
    return {
        "component": DIRECT_HEADER_TEXT_COMPONENT,
        "source_font_path": TEXT_FONT_PATH,
        "source_font_size": TEXT_FONT_SOURCE_SIZE,
        "source_font_sha256": TEXT_FONT_SOURCE_SHA256,
        "source_font_atlas_size": DIRECT_HEADER_FONT_ATLAS_SIZE,
        "source_font_native_line_height": DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT,
        "native_color_16": TEXT_NATIVE_COLOR_16,
        "control_rects": (FIRST_TEXT_RECT, SECOND_TEXT_RECT),
        "center_rounding": "signed_truncation_toward_zero",
        "control_clipping_applied": True,
        "exact_header_text_pixels_recovered": True,
        "runtime_metadata_bound": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
