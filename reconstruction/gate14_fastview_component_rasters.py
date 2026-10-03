"""Source-backed FastView component RGBA planes.

This module rasterizes only components whose own pixel ownership and internal
draw order are already recovered:

* directly PictureControl-bound FastView chrome;
* PossessionDiagram base pitch followed by its active overlay;
* PossessionFigures source-font glyphs.

Each component is emitted as a separate transparent 800x600 RGBA plane.
Cross-component z-order remains deliberately unresolved, so this module cannot
flatten the planes into one FastView frame or claim complete raster fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from original_fastview_chrome_art import OriginalFastViewChromeArt
from original_fastview_possession_art import OriginalFastViewPossessionArtFrame
from original_fastview_possession_figures_art import (
    OriginalFastViewPossessionFiguresArt,
)


class FastViewComponentRasterError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewComponentRasterPlane:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    rgba_sha256: str
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if self.component not in {
            "direct_chrome",
            "possession_diagram",
            "possession_figures_text",
        }:
            raise FastViewComponentRasterError("unknown FastView raster component")
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewComponentRasterError("FastView raster plane must be 800x600")
        width, height = self.size
        if len(self.rgba) != width * height * 4:
            raise FastViewComponentRasterError(
                "FastView raster plane RGBA payload has wrong size"
            )
        if type(self.source_layer_count) is not int or self.source_layer_count <= 0:
            raise FastViewComponentRasterError(
                "FastView raster plane source_layer_count must be positive"
            )
        if (
            not isinstance(self.rgba_sha256, str)
            or len(self.rgba_sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.rgba_sha256)
        ):
            raise FastViewComponentRasterError(
                "FastView raster plane SHA-256 must be lowercase hexadecimal"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewComponentRasterError(
                "FastView raster plane SHA-256 does not match RGBA payload"
            )
        if self.complete_fastview_frame:
            raise FastViewComponentRasterError(
                "component plane cannot claim a complete FastView frame"
            )


@dataclass(frozen=True)
class FastViewComponentRasterSet:
    chrome: FastViewComponentRasterPlane
    possession_diagram: FastViewComponentRasterPlane
    possession_figures: FastViewComponentRasterPlane
    cross_component_z_order_recovered: bool = False
    flattened_frame_available: bool = False

    def __post_init__(self) -> None:
        expected = (
            (self.chrome, "direct_chrome"),
            (self.possession_diagram, "possession_diagram"),
            (self.possession_figures, "possession_figures_text"),
        )
        for plane, component in expected:
            if type(plane) is not FastViewComponentRasterPlane:
                raise FastViewComponentRasterError(
                    "FastView raster set requires exact component planes"
                )
            if plane.component != component:
                raise FastViewComponentRasterError(
                    "FastView raster set component identity mismatch"
                )
        if self.cross_component_z_order_recovered or self.flattened_frame_available:
            raise FastViewComponentRasterError(
                "cross-component FastView composition remains unresolved"
            )


def _blank_surface() -> bytearray:
    width, height = FASTVIEW_SURFACE_SIZE
    return bytearray(width * height * 4)


def _validate_rect(
    rect: tuple[int, int, int, int],
    *,
    payload_width: int,
    payload_height: int,
) -> None:
    if (
        type(rect) is not tuple
        or len(rect) != 4
        or any(type(value) is not int for value in rect)
    ):
        raise FastViewComponentRasterError("source raster rect must be four integers")
    left, top, right, bottom = rect
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    if not (0 <= left < right <= surface_width and 0 <= top < bottom <= surface_height):
        raise FastViewComponentRasterError(
            "source raster rect must stay inside the recovered 800x600 surface"
        )
    if (right - left, bottom - top) != (payload_width, payload_height):
        raise FastViewComponentRasterError(
            "source raster rect does not match RGBA payload geometry"
        )


def _alpha_over(
    canvas: bytearray,
    source_rgba: bytes,
    rect: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if len(source_rgba) != width * height * 4:
        raise FastViewComponentRasterError(
            "source RGBA payload does not match placement geometry"
        )
    surface_width, _ = FASTVIEW_SURFACE_SIZE

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

            # Straight-alpha source-over. Compute premultiplied color terms,
            # then convert back to straight RGBA for the stored plane.
            for channel in range(3):
                src_premul = source_rgba[src + channel] * alpha
                dst_premul = (
                    canvas[dst + channel] * dst_alpha * inv + 127
                ) // 255
                canvas[dst + channel] = (
                    src_premul + dst_premul + out_alpha // 2
                ) // out_alpha
            canvas[dst + 3] = out_alpha


def _plane(component: str, canvas: bytearray, layer_count: int):
    rgba = bytes(canvas)
    return FastViewComponentRasterPlane(
        component=component,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        source_layer_count=int(layer_count),
        rgba_sha256=sha256(rgba).hexdigest(),
    )


def rasterize_fastview_chrome_plane(
    chrome: OriginalFastViewChromeArt,
) -> FastViewComponentRasterPlane:
    """Rasterize directly owned chrome in retained source placement order."""
    if type(chrome) is not OriginalFastViewChromeArt:
        raise FastViewComponentRasterError(
            "chrome must be exact OriginalFastViewChromeArt"
        )
    if not chrome.placements:
        raise FastViewComponentRasterError("FastView chrome has no source placements")

    canvas = _blank_surface()
    for placement in chrome.placements:
        left, top, right, bottom = placement.rect
        _validate_rect(
            placement.rect,
            payload_width=right - left,
            payload_height=bottom - top,
        )
        _alpha_over(canvas, placement.rgba, placement.rect)
    return _plane("direct_chrome", canvas, len(chrome.placements))


def rasterize_fastview_possession_plane(
    possession: OriginalFastViewPossessionArtFrame,
) -> FastViewComponentRasterPlane:
    """Rasterize base pitch then active overlay exactly as retained."""
    if type(possession) is not OriginalFastViewPossessionArtFrame:
        raise FastViewComponentRasterError(
            "possession must be exact OriginalFastViewPossessionArtFrame"
        )
    if not possession.placements:
        raise FastViewComponentRasterError(
            "FastView possession diagram has no source placements"
        )
    if possession.placements[0].role != "base_pitch":
        raise FastViewComponentRasterError(
            "FastView possession diagram must begin with base_pitch"
        )
    if any(
        placement.role not in {"base_pitch", "active_overlay"}
        for placement in possession.placements
    ):
        raise FastViewComponentRasterError(
            "FastView possession diagram contains an unknown source role"
        )

    canvas = _blank_surface()
    for placement in possession.placements:
        _validate_rect(
            placement.rect,
            payload_width=placement.width,
            payload_height=placement.height,
        )
        _alpha_over(canvas, placement.rgba, placement.rect)
    return _plane("possession_diagram", canvas, len(possession.placements))


def rasterize_fastview_possession_figures_plane(
    figures: OriginalFastViewPossessionFiguresArt,
) -> FastViewComponentRasterPlane:
    """Rasterize only the source-font glyph bounds at each exact line origin."""
    if type(figures) is not OriginalFastViewPossessionFiguresArt:
        raise FastViewComponentRasterError(
            "figures must be exact OriginalFastViewPossessionFiguresArt"
        )
    if len(figures.rows) != 3:
        raise FastViewComponentRasterError(
            "PossessionFigures must retain exactly three source controls"
        )

    canvas = _blank_surface()
    for row in figures.rows:
        left, top = row.line_origin
        rect = (
            left,
            top,
            left + row.glyph_width,
            top + row.glyph_height,
        )
        clip_left, clip_top, clip_right, clip_bottom = row.clip_rect
        if not (
            clip_left <= rect[0] <= rect[2] <= clip_right
            and clip_top <= rect[1] <= rect[3] <= clip_bottom
        ):
            raise FastViewComponentRasterError(
                "PossessionFigures glyph exceeds its recovered source clip"
            )
        _validate_rect(
            rect,
            payload_width=row.glyph_width,
            payload_height=row.glyph_height,
        )
        _alpha_over(canvas, row.glyph_rgba, rect)
    return _plane("possession_figures_text", canvas, len(figures.rows))


def build_fastview_component_rasters(
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
) -> FastViewComponentRasterSet:
    """Build all currently source-rasterizable planes without flattening them."""
    return FastViewComponentRasterSet(
        chrome=rasterize_fastview_chrome_plane(chrome),
        possession_diagram=rasterize_fastview_possession_plane(possession),
        possession_figures=rasterize_fastview_possession_figures_plane(figures),
    )
