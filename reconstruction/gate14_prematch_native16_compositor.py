"""Native packed-16 compositor for one supplied PPreMatch child ledger.

This module deliberately stops one layer before modern display conversion.
Given an explicit valid runtime RGB mask triplet, it reproduces the source
PictureControl, TextControl, and Button@ease destination writes in native
0..181 child order and emits the exact 800x600 packed-16 framebuffer bytes.

The caller still has to prove that a mask triplet was observed from the
canonical original Windows runtime before claiming original-layout fidelity.
Packed-16 -> modern RGBA expansion also remains a separate boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_font_blend_source_trace import (
    Native16PixelMasks,
    blend_native_font_pixel16_with_color_key,
)
from gate14_native_rgb_pack import pack_native_rgb16
from gate14_prematch_child_rasters import (
    PrematchChildRaster,
    PrematchChildRasterLedger,
)
from gate14_prematch_compositor_source import (
    PREMATCH_PICTURE_CHILD_INDICES,
    PREMATCH_SELECTOR_CHILD_INDICES,
    PREMATCH_TEXT_CHILD_INDICES,
    prematch_picture_write_mode,
)


class PrematchNative16CompositorError(ValueError):
    pass


PREMATCH_NATIVE_SURFACE_SIZE = (800, 600)


@dataclass(frozen=True)
class PrematchNative16Frame:
    size: tuple[int, int]
    pixels_le: bytes
    pixels_sha256: str
    masks: Native16PixelMasks
    visible_child_count: int
    picture_child_count: int
    text_child_count: int
    selector_child_count: int
    native_child_order_preserved: bool = True
    supplied_runtime_masks_required: bool = True
    runtime_masks_observed_from_original: bool = False
    flattened_native16_frame_available: bool = True
    packed16_to_modern_rgba_recovered: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if self.size != PREMATCH_NATIVE_SURFACE_SIZE:
            raise PrematchNative16CompositorError(
                "PPreMatch native framebuffer must remain 800x600"
            )
        width, height = self.size
        if len(self.pixels_le) != width * height * 2:
            raise PrematchNative16CompositorError(
                "native packed-16 framebuffer byte count is wrong"
            )
        if sha256(self.pixels_le).hexdigest() != self.pixels_sha256:
            raise PrematchNative16CompositorError(
                "native packed-16 framebuffer checksum mismatch"
            )
        if type(self.masks) is not Native16PixelMasks:
            raise PrematchNative16CompositorError(
                "native framebuffer requires exact runtime masks"
            )
        for value in (
            self.visible_child_count,
            self.picture_child_count,
            self.text_child_count,
            self.selector_child_count,
        ):
            if type(value) is not int or value < 0:
                raise PrematchNative16CompositorError(
                    "native compositor child counts must be non-negative"
                )
        if self.picture_child_count + self.text_child_count + self.selector_child_count != (
            self.visible_child_count
        ):
            raise PrematchNative16CompositorError(
                "native compositor family counts do not cover visible children"
            )
        if not (
            self.native_child_order_preserved
            and self.supplied_runtime_masks_required
            and self.flattened_native16_frame_available
        ):
            raise PrematchNative16CompositorError(
                "native compositor cannot weaken proven ordering/frame state"
            )
        if (
            self.runtime_masks_observed_from_original
            or self.packed16_to_modern_rgba_recovered
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchNative16CompositorError(
                "mask provenance/modern display/Gate 14 remain separate contracts"
            )


def _pixel_offset(x: int, y: int) -> int:
    return (y * PREMATCH_NATIVE_SURFACE_SIZE[0] + x) * 2


def _read16(surface: bytearray, x: int, y: int) -> int:
    offset = _pixel_offset(x, y)
    return surface[offset] | (surface[offset + 1] << 8)


def _write16(surface: bytearray, x: int, y: int, value: int) -> None:
    offset = _pixel_offset(x, y)
    surface[offset] = value & 0xFF
    surface[offset + 1] = (value >> 8) & 0xFF


def _validate_visible_rect(child: PrematchChildRaster) -> None:
    if not child.visible or child.rect is None or child.rgba is None:
        raise PrematchNative16CompositorError(
            "native compositor requires a visible child with geometry/pixels"
        )
    rect = child.rect
    width, height = PREMATCH_NATIVE_SURFACE_SIZE
    if (
        rect.x < 0
        or rect.y < 0
        or rect.right > width
        or rect.bottom > height
    ):
        raise PrematchNative16CompositorError(
            f"child {child.child_index} exceeds native 800x600 surface"
        )


def _write_picture(
    surface: bytearray,
    child: PrematchChildRaster,
    masks: Native16PixelMasks,
    *,
    keyed: bool,
) -> None:
    _validate_visible_rect(child)
    rect = child.rect
    rgba = child.rgba
    for local_y in range(rect.height):
        for local_x in range(rect.width):
            source = (local_y * rect.width + local_x) * 4
            red, green, blue, alpha = rgba[source:source + 4]
            packed = pack_native_rgb16(red, green, blue, masks)
            if keyed and (alpha == 0 or packed == masks.color_key):
                continue
            _write16(
                surface,
                rect.x + local_x,
                rect.y + local_y,
                packed,
            )


def _blend_alpha_plane(
    surface: bytearray,
    *,
    origin: tuple[int, int],
    size: tuple[int, int],
    alpha: bytes,
    native_color_16: int,
    masks: Native16PixelMasks,
) -> None:
    width, height = size
    if len(alpha) != width * height:
        raise PrematchNative16CompositorError("glyph alpha geometry mismatch")
    origin_x, origin_y = origin
    surface_width, surface_height = PREMATCH_NATIVE_SURFACE_SIZE
    if (
        origin_x < 0
        or origin_y < 0
        or origin_x + width > surface_width
        or origin_y + height > surface_height
    ):
        raise PrematchNative16CompositorError(
            "glyph alpha plane exceeds native 800x600 surface"
        )
    for local_y in range(height):
        for local_x in range(width):
            glyph_alpha = alpha[local_y * width + local_x]
            if glyph_alpha == 0:
                continue
            x = origin_x + local_x
            y = origin_y + local_y
            destination = _read16(surface, x, y)
            blended = blend_native_font_pixel16_with_color_key(
                destination,
                native_color_16,
                glyph_alpha,
                masks,
            )
            _write16(surface, x, y, blended)


def _write_text(
    surface: bytearray,
    child: PrematchChildRaster,
    masks: Native16PixelMasks,
) -> None:
    _validate_visible_rect(child)
    rect = child.rect
    rgba = child.rgba
    alpha = bytearray(rect.width * rect.height)
    for pixel_index in range(rect.width * rect.height):
        source = pixel_index * 4
        red, green, blue, glyph_alpha = rgba[source:source + 4]
        if (red, green, blue) != (255, 255, 255):
            raise PrematchNative16CompositorError(
                "PPreMatch TextControl plane is not native 0xFFFF white"
            )
        alpha[pixel_index] = glyph_alpha
    _blend_alpha_plane(
        surface,
        origin=(rect.x, rect.y),
        size=(rect.width, rect.height),
        alpha=bytes(alpha),
        native_color_16=0xFFFF,
        masks=masks,
    )


def _write_selector(
    surface: bytearray,
    child: PrematchChildRaster,
    masks: Native16PixelMasks,
) -> None:
    _write_picture(surface, child, masks, keyed=False)
    if (
        child.caption_alpha is None
        or child.caption_size is None
        or child.caption_origin is None
        or child.caption_native_color_16 is None
    ):
        raise PrematchNative16CompositorError(
            "selector child lacks source-backed caption plane"
        )
    _blend_alpha_plane(
        surface,
        origin=child.caption_origin,
        size=child.caption_size,
        alpha=child.caption_alpha,
        native_color_16=child.caption_native_color_16,
        masks=masks,
    )


def compose_prematch_native16_frame(
    ledger: PrematchChildRasterLedger,
    *,
    masks: Native16PixelMasks,
) -> PrematchNative16Frame:
    """Flatten supplied child pixels into source-order native packed-16 bytes."""
    if type(ledger) is not PrematchChildRasterLedger:
        raise PrematchNative16CompositorError(
            "native compositor requires exact PrematchChildRasterLedger"
        )
    if type(masks) is not Native16PixelMasks:
        raise PrematchNative16CompositorError(
            "native compositor requires exact Native16PixelMasks"
        )

    surface = bytearray(PREMATCH_NATIVE_SURFACE_SIZE[0] * PREMATCH_NATIVE_SURFACE_SIZE[1] * 2)
    picture_count = 0
    text_count = 0
    selector_count = 0

    for child in ledger.children:
        if not child.visible:
            continue
        if child.child_index in PREMATCH_PICTURE_CHILD_INDICES:
            mode = prematch_picture_write_mode(child.child_index)
            _write_picture(
                surface,
                child,
                masks,
                keyed=(mode == "source_color_key"),
            )
            picture_count += 1
        elif child.child_index in PREMATCH_TEXT_CHILD_INDICES:
            _write_text(surface, child, masks)
            text_count += 1
        elif child.child_index in PREMATCH_SELECTOR_CHILD_INDICES:
            _write_selector(surface, child, masks)
            selector_count += 1
        else:
            raise PrematchNative16CompositorError(
                f"child {child.child_index} lacks a source-closed control family"
            )

    payload = bytes(surface)
    visible = picture_count + text_count + selector_count
    return PrematchNative16Frame(
        size=PREMATCH_NATIVE_SURFACE_SIZE,
        pixels_le=payload,
        pixels_sha256=sha256(payload).hexdigest(),
        masks=masks,
        visible_child_count=visible,
        picture_child_count=picture_count,
        text_child_count=text_count,
        selector_child_count=selector_count,
    )


def prematch_native16_compositor_contract() -> dict:
    return {
        "surface_size": PREMATCH_NATIVE_SURFACE_SIZE,
        "native_child_order": tuple(range(182)),
        "picture_write_modes_source_closed": True,
        "text_packed16_blend_reused": True,
        "selector_frame_then_caption_order_source_closed": True,
        "runtime_masks_must_be_supplied": True,
        "runtime_masks_observed_from_original": False,
        "flattened_native16_frame_available": True,
        "packed16_to_modern_rgba_recovered": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
