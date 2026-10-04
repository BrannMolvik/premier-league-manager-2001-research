"""Standalone Tk draw boundary for the resolved-only Gate-14 FastView surface.

This module is deliberately presentation-only. It accepts the already-built
resolved-only FastView composite, encodes its exact RGBA bytes as a lossless
RGBA8 PNG, and places that image on a caller-owned Tk canvas.

Pixels that are unresolved because cross-component z-order is unknown remain
transparent exactly as produced by the compositor. This module does not clear
or color the canvas beneath them, does not draw a background, does not rerun
simulation, and does not claim a complete FastView frame.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from hashlib import sha256
import struct
import zlib

from gate14_fastview_resolved_composite import (
    FastViewResolvedOnlyComposite,
    FastViewUnresolvedOverlapGroup,
)


class FastViewResolvedTkSurfaceError(ValueError):
    pass


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def encode_fastview_resolved_png(
    composite: FastViewResolvedOnlyComposite,
) -> bytes:
    """Encode the exact resolved-only RGBA plane without filling alpha holes."""
    if type(composite) is not FastViewResolvedOnlyComposite:
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires exact resolved-only composite"
        )

    width, height = composite.size
    row_bytes = width * 4
    scanlines = b"".join(
        b"\x00" + composite.rgba[y * row_bytes:(y + 1) * row_bytes]
        for y in range(height)
    )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        _PNG_SIGNATURE
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(scanlines, level=6))
        + _png_chunk(b"IEND", b"")
    )


@dataclass(frozen=True)
class FastViewResolvedTkDraw:
    """Keeps Tk image ownership plus the unresolved-fidelity audit boundary."""

    png: bytes
    png_sha256: str
    photo_image: object
    canvas_item_id: object
    resolved_pixel_count: int
    unresolved_overlap_pixel_count: int
    unresolved_overlap_groups: tuple[FastViewUnresolvedOverlapGroup, ...]
    unresolved_pixels_remain_transparent: bool = True
    cross_component_z_order_recovered: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.png, bytes) or not self.png.startswith(_PNG_SIGNATURE):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw requires encoded PNG bytes"
            )
        if (
            not isinstance(self.png_sha256, str)
            or len(self.png_sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.png_sha256)
            or sha256(self.png).hexdigest() != self.png_sha256
        ):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw PNG SHA-256 does not match bytes"
            )
        if (
            type(self.resolved_pixel_count) is not int
            or self.resolved_pixel_count < 0
            or type(self.unresolved_overlap_pixel_count) is not int
            or self.unresolved_overlap_pixel_count < 0
        ):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw pixel counts must be non-negative integers"
            )
        if (
            type(self.unresolved_overlap_groups) is not tuple
            or any(
                type(group) is not FastViewUnresolvedOverlapGroup
                for group in self.unresolved_overlap_groups
            )
        ):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw requires exact unresolved overlap groups"
            )
        if (
            not self.unresolved_pixels_remain_transparent
            or self.cross_component_z_order_recovered
            or self.complete_fastview_frame
        ):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw cannot promote unresolved frame fidelity"
            )


def draw_fastview_resolved_on_tk_canvas(
    composite: FastViewResolvedOnlyComposite,
    tk_module,
    canvas,
) -> FastViewResolvedTkDraw:
    """Draw one source-backed partial FastView image at native 800x600 origin.

    The caller owns the canvas/window lifecycle. No canvas clear, background
    color, scaling, fullscreen policy, event binding, or frame substitution is
    performed here.
    """
    if type(composite) is not FastViewResolvedOnlyComposite:
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires exact resolved-only composite"
        )
    if not hasattr(tk_module, "PhotoImage") or not hasattr(tk_module, "NW"):
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires PhotoImage and NW from the Tk module"
        )
    if not hasattr(canvas, "create_image"):
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires a canvas create_image boundary"
        )

    png = encode_fastview_resolved_png(composite)
    photo = tk_module.PhotoImage(
        data=b64encode(png).decode("ascii"),
        format="png",
    )
    item_id = canvas.create_image(
        0,
        0,
        image=photo,
        anchor=tk_module.NW,
    )
    return FastViewResolvedTkDraw(
        png=png,
        png_sha256=sha256(png).hexdigest(),
        photo_image=photo,
        canvas_item_id=item_id,
        resolved_pixel_count=composite.resolved_pixel_count,
        unresolved_overlap_pixel_count=composite.unresolved_overlap_pixel_count,
        unresolved_overlap_groups=composite.unresolved_overlap_groups,
    )
