"""Deterministic PNG export for the fail-closed FastView resolved-only composite.

The exporter never resolves cross-component overlap. The RGBA preview preserves
the composite's transparent unresolved pixels byte-for-byte, while the companion
mask PNG exposes those unresolved pixels as 255 and every other pixel as 0.

This is a player-visible/debuggable presentation boundary for already verified
pixels only. It is not a complete FastView frame and must not be used to claim
recovered z-order, background ownership, audio, or 3D choreography.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import struct
import zlib

from gate14_fastview_resolved_composite import (
    FastViewResolvedOnlyComposite,
    FastViewUnresolvedOverlapGroup,
)
from gate14_fastview_frame_plan import FastViewFramePlan


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class FastViewResolvedPreviewError(ValueError):
    pass


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    if len(kind) != 4:
        raise FastViewResolvedPreviewError("PNG chunk type must be four bytes")
    body = kind + payload
    return (
        struct.pack(">I", len(payload))
        + body
        + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    )


def _encode_png(
    *,
    width: int,
    height: int,
    color_type: int,
    bytes_per_pixel: int,
    pixels: bytes,
) -> bytes:
    if width <= 0 or height <= 0:
        raise FastViewResolvedPreviewError("PNG dimensions must be positive")
    expected = width * height * bytes_per_pixel
    if len(pixels) != expected:
        raise FastViewResolvedPreviewError("PNG pixel payload has wrong size")
    if color_type not in (0, 6):
        raise FastViewResolvedPreviewError("unsupported PNG color type")

    stride = width * bytes_per_pixel
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)  # deterministic filter type 0
        start = y * stride
        scanlines.extend(pixels[start:start + stride])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"".join(
        (
            PNG_SIGNATURE,
            _png_chunk(b"IHDR", ihdr),
            _png_chunk(b"IDAT", zlib.compress(bytes(scanlines), level=9)),
            _png_chunk(b"IEND", b""),
        )
    )


@dataclass(frozen=True)
class FastViewResolvedPreview:
    size: tuple[int, int]
    rgba_png: bytes
    overlap_mask_png: bytes
    rgba_png_sha256: str
    overlap_mask_png_sha256: str
    resolved_pixel_count: int
    unresolved_overlap_pixel_count: int
    overlap_groups: tuple[FastViewUnresolvedOverlapGroup, ...]
    source_composite_rgba_sha256: str
    source_overlap_mask_sha256: str
    cross_component_z_order_recovered: bool = False
    flattened_frame_available: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if self.size != (800, 600):
            raise FastViewResolvedPreviewError("FastView preview must remain 800x600")
        if not self.rgba_png.startswith(PNG_SIGNATURE):
            raise FastViewResolvedPreviewError("RGBA preview must be a PNG")
        if not self.overlap_mask_png.startswith(PNG_SIGNATURE):
            raise FastViewResolvedPreviewError("overlap mask preview must be a PNG")
        if sha256(self.rgba_png).hexdigest() != self.rgba_png_sha256:
            raise FastViewResolvedPreviewError("RGBA preview SHA-256 mismatch")
        if sha256(self.overlap_mask_png).hexdigest() != self.overlap_mask_png_sha256:
            raise FastViewResolvedPreviewError("overlap mask preview SHA-256 mismatch")
        for digest in (
            self.source_composite_rgba_sha256,
            self.source_overlap_mask_sha256,
        ):
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
            ):
                raise FastViewResolvedPreviewError(
                    "source composite hashes must be lowercase SHA-256"
                )
        if (
            type(self.overlap_groups) is not tuple
            or any(type(group) is not FastViewUnresolvedOverlapGroup for group in self.overlap_groups)
        ):
            raise FastViewResolvedPreviewError(
                "preview overlap groups must preserve exact composite records"
            )
        if (
            self.cross_component_z_order_recovered
            or self.flattened_frame_available
            or self.complete_fastview_frame
        ):
            raise FastViewResolvedPreviewError(
                "resolved preview cannot promote unresolved FastView fidelity"
            )


def build_fastview_resolved_preview(
    composite: FastViewResolvedOnlyComposite,
) -> FastViewResolvedPreview:
    """Encode the exact resolved-only RGBA and unresolved mask as PNGs."""
    if type(composite) is not FastViewResolvedOnlyComposite:
        raise FastViewResolvedPreviewError(
            "preview requires exact FastViewResolvedOnlyComposite"
        )
    width, height = composite.size
    rgba_png = _encode_png(
        width=width,
        height=height,
        color_type=6,
        bytes_per_pixel=4,
        pixels=composite.rgba,
    )
    mask_pixels = bytes(
        255 if value else 0
        for value in composite.unresolved_overlap_mask
    )
    mask_png = _encode_png(
        width=width,
        height=height,
        color_type=0,
        bytes_per_pixel=1,
        pixels=mask_pixels,
    )
    return FastViewResolvedPreview(
        size=composite.size,
        rgba_png=rgba_png,
        overlap_mask_png=mask_png,
        rgba_png_sha256=sha256(rgba_png).hexdigest(),
        overlap_mask_png_sha256=sha256(mask_png).hexdigest(),
        resolved_pixel_count=composite.resolved_pixel_count,
        unresolved_overlap_pixel_count=composite.unresolved_overlap_pixel_count,
        overlap_groups=composite.unresolved_overlap_groups,
        source_composite_rgba_sha256=composite.rgba_sha256,
        source_overlap_mask_sha256=composite.unresolved_overlap_mask_sha256,
    )


def build_fastview_frame_preview(frame: FastViewFramePlan) -> FastViewResolvedPreview:
    """Export only the resolved-only pixels retained by an exact frame plan."""
    if type(frame) is not FastViewFramePlan:
        raise FastViewResolvedPreviewError(
            "frame preview requires exact FastViewFramePlan"
        )
    return build_fastview_resolved_preview(frame.resolved_composite)
