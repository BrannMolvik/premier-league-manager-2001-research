"""Fail-closed white-endpoint raster for the source-closed FastView clock.

ClockControl can display both the native all-bits-on white endpoint (0xFFFF)
and a runtime-packed RGB(255,45,45) alert color. Only the white endpoint has an
exact modern RGBA interpretation independent of the active 16-bit channel
layout.

This module therefore rasterizes only ClockControl states whose source color is
already exact at the white endpoint. Alert-colored states are rejected rather
than approximated.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from gate14_fastview_clock import (
    SOURCE_CLOCK_NATIVE_WHITE_16,
    SOURCE_CLOCK_TEXT_RECT,
    FastViewClockState,
)
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_possession_figures import (
    SOURCE_TEXT_FONT_ATLAS_SIZE,
    SOURCE_TEXT_FONT_BYTE_SIZE,
    SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
    SOURCE_TEXT_FONT_PATH,
    SOURCE_TEXT_FONT_SHA256,
)
from original_live_debug_view import endpoint_text_rgba


class FastViewClockRasterError(ValueError):
    pass


CLOCK_TEXT_COMPONENT = "clock_text"


@dataclass(frozen=True)
class FastViewClockRaster:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    text: str
    line_origin: tuple[int, int] | None
    clip_rect: tuple[int, int, int, int]
    native_color_16: int | None
    rgba_sha256: str
    white_endpoint_only: bool = True
    alert_color_withheld: bool = True
    alert_modern_rgba_recovered: bool = False
    global_fastview_z_order_recovered: bool = False
    complete_fastview_frame_recovered: bool = False

    def __post_init__(self) -> None:
        if self.component != CLOCK_TEXT_COMPONENT:
            raise FastViewClockRasterError("clock raster component identity drifted")
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewClockRasterError("clock raster must retain 800x600")
        if len(self.rgba) != self.size[0] * self.size[1] * 4:
            raise FastViewClockRasterError("clock raster RGBA payload has wrong size")
        if self.source_layer_count not in (0, 1):
            raise FastViewClockRasterError("clock raster has zero or one visible text layer")
        if self.clip_rect != SOURCE_CLOCK_TEXT_RECT:
            raise FastViewClockRasterError("clock raster clip rectangle drifted")
        if self.source_layer_count == 0:
            if self.text or self.line_origin is not None or self.native_color_16 is not None:
                raise FastViewClockRasterError(
                    "empty clock raster must not retain a visible source layer"
                )
        else:
            if not self.text:
                raise FastViewClockRasterError("visible clock raster requires text")
            if self.line_origin != SOURCE_CLOCK_TEXT_RECT[:2]:
                raise FastViewClockRasterError(
                    "source left/top ClockControl line origin drifted"
                )
            if self.native_color_16 != SOURCE_CLOCK_NATIVE_WHITE_16:
                raise FastViewClockRasterError(
                    "white-endpoint clock raster requires native 0xFFFF"
                )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewClockRasterError("clock raster SHA-256 mismatch")
        if not self.white_endpoint_only or not self.alert_color_withheld:
            raise FastViewClockRasterError(
                "partial clock raster must remain white-only with alerts withheld"
            )
        if (
            self.alert_modern_rgba_recovered
            or self.global_fastview_z_order_recovered
            or self.complete_fastview_frame_recovered
        ):
            raise FastViewClockRasterError(
                "clock raster cannot promote unresolved output/order/frame fidelity"
            )


def load_verified_clock_font(repo_root: str | Path) -> EAFont:
    """Load the exact staged style-1 Zurich font used by ClockControl."""
    path = Path(repo_root) / "original_assets" / "source" / SOURCE_TEXT_FONT_PATH
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise FastViewClockRasterError(
            f"missing staged clock font: {SOURCE_TEXT_FONT_PATH}"
        ) from exc
    if len(data) != SOURCE_TEXT_FONT_BYTE_SIZE:
        raise FastViewClockRasterError("clock font byte-size mismatch")
    if sha256(data).hexdigest() != SOURCE_TEXT_FONT_SHA256:
        raise FastViewClockRasterError("clock font checksum mismatch")
    font = EAFont.from_bytes(data)
    if (font.atlas_width, font.atlas_height) != SOURCE_TEXT_FONT_ATLAS_SIZE:
        raise FastViewClockRasterError("clock font atlas geometry mismatch")
    if font.native_line_height() != SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT:
        raise FastViewClockRasterError("clock font native line-height mismatch")
    return font


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
        raise FastViewClockRasterError("clock glyph RGBA geometry mismatch")
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


def build_white_endpoint_clock_raster(
    font: EAFont,
    state: FastViewClockState,
) -> FastViewClockRaster:
    """Raster one source ClockControl state only when its RGBA color is exact."""
    if type(font) is not EAFont:
        raise FastViewClockRasterError("clock raster requires exact EAFont")
    if type(state) is not FastViewClockState:
        raise FastViewClockRasterError("clock raster requires exact FastViewClockState")
    if font.native_line_height() != SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT:
        raise FastViewClockRasterError("clock font line-height does not match source")
    if not state.color.exact_modern_rgba_recovered:
        raise FastViewClockRasterError(
            "clock alert color is source-backed RGB8 but modern RGBA remains unresolved"
        )

    canvas = bytearray(FASTVIEW_SURFACE_SIZE[0] * FASTVIEW_SURFACE_SIZE[1] * 4)
    if not state.text:
        payload = bytes(canvas)
        return FastViewClockRaster(
            component=CLOCK_TEXT_COMPONENT,
            size=FASTVIEW_SURFACE_SIZE,
            rgba=payload,
            source_layer_count=0,
            text="",
            line_origin=None,
            clip_rect=SOURCE_CLOCK_TEXT_RECT,
            native_color_16=None,
            rgba_sha256=sha256(payload).hexdigest(),
        )

    if state.color.native_color_16 != SOURCE_CLOCK_NATIVE_WHITE_16:
        raise FastViewClockRasterError(
            "exact ClockControl raster currently supports only native white"
        )

    mask = font.render_text_alpha(state.text)
    origin = SOURCE_CLOCK_TEXT_RECT[:2]
    rgba = endpoint_text_rgba(mask.alpha, SOURCE_CLOCK_NATIVE_WHITE_16)
    _draw_clipped(
        canvas,
        source_rgba=rgba,
        width=mask.width,
        height=mask.height,
        origin=origin,
        clip_rect=SOURCE_CLOCK_TEXT_RECT,
    )
    payload = bytes(canvas)
    return FastViewClockRaster(
        component=CLOCK_TEXT_COMPONENT,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=payload,
        source_layer_count=1,
        text=state.text,
        line_origin=origin,
        clip_rect=SOURCE_CLOCK_TEXT_RECT,
        native_color_16=SOURCE_CLOCK_NATIVE_WHITE_16,
        rgba_sha256=sha256(payload).hexdigest(),
    )


def clock_white_raster_contract() -> dict:
    return {
        "component": CLOCK_TEXT_COMPONENT,
        "source_font_path": SOURCE_TEXT_FONT_PATH,
        "source_font_sha256": SOURCE_TEXT_FONT_SHA256,
        "source_font_native_line_height": SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
        "source_rect": SOURCE_CLOCK_TEXT_RECT,
        "line_origin": SOURCE_CLOCK_TEXT_RECT[:2],
        "native_white_16": SOURCE_CLOCK_NATIVE_WHITE_16,
        "white_endpoint_raster_recovered": True,
        "alert_color_withheld": True,
        "alert_modern_rgba_recovered": False,
        "integrated_component_plane": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
