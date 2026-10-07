"""Source-exact legacy RGB packing used by PPreMatch generic shirts.

0x653090 queries the active DirectDraw surface DDPIXELFORMAT and passes it to
0x6530D0. For each RGB mask, 0x653120 derives:
- the number of low zero bits (destination left shift);
- the number of high unused bits after normalization (source 8-bit right shift).

0x5E4980 applies those descriptors to palette RGB and stores a 16-bit word.
It also preserves the original quirk where a nonblack source color that
quantizes to zero is forced to packed value 1.
"""
from __future__ import annotations

from dataclasses import dataclass


class PrematchPixelFormatError(ValueError):
    pass


PREMATCH_PIXEL_FORMAT_QUERY_VA = 0x653090
PREMATCH_PIXEL_FORMAT_BUILD_VA = 0x6530D0
PREMATCH_PIXEL_CHANNEL_BUILD_VA = 0x653120
PREMATCH_GENERIC_SHIRT_COPY_VA = 0x5E4980

PREMATCH_PIXEL_FORMAT_GLOBAL_VA = 0x984820
PREMATCH_RED_CHANNEL_GLOBAL_VA = 0x984824
PREMATCH_GREEN_CHANNEL_GLOBAL_VA = 0x984830
PREMATCH_BLUE_CHANNEL_GLOBAL_VA = 0x98483C

PREMATCH_CHANNEL_MASK_OFFSET = 0x00
PREMATCH_CHANNEL_LEFT_SHIFT_OFFSET = 0x04
PREMATCH_CHANNEL_RIGHT_SHIFT_OFFSET = 0x08


@dataclass(frozen=True)
class PrematchPixelChannel:
    mask: int
    left_shift: int
    right_shift: int

    def __post_init__(self) -> None:
        if type(self.mask) is not int or self.mask <= 0:
            raise PrematchPixelFormatError("channel mask must be a positive integer")
        if type(self.left_shift) is not int or not 0 <= self.left_shift <= 31:
            raise PrematchPixelFormatError("channel left shift is invalid")
        if type(self.right_shift) is not int or not 0 <= self.right_shift <= 8:
            raise PrematchPixelFormatError("channel right shift is invalid")

    def pack(self, component: int) -> int:
        if type(component) is not int or not 0 <= component <= 255:
            raise PrematchPixelFormatError("RGB component must be in 0..255")
        return ((component >> self.right_shift) << self.left_shift) & self.mask


@dataclass(frozen=True)
class PrematchRGB16Format:
    bit_count: int
    red: PrematchPixelChannel
    green: PrematchPixelChannel
    blue: PrematchPixelChannel

    def __post_init__(self) -> None:
        if self.bit_count != 16:
            raise PrematchPixelFormatError(
                "PPreMatch generic shirt copy stores a 16-bit destination word"
            )
        masks = (self.red.mask, self.green.mask, self.blue.mask)
        if any(mask & ~0xFFFF for mask in masks):
            raise PrematchPixelFormatError("RGB16 channel mask exceeds destination word")
        if (masks[0] & masks[1]) or (masks[0] & masks[2]) or (masks[1] & masks[2]):
            raise PrematchPixelFormatError("RGB16 channel masks overlap")

    def pack_rgb(self, red: int, green: int, blue: int) -> int:
        packed = (
            self.red.pack(red)
            | self.green.pack(green)
            | self.blue.pack(blue)
        ) & 0xFFFF
        # 0x5E4980 reserves zero for no-write/color-key semantics. It tests
        # the original source RGB bytes, not the shifted components.
        if (red | green | blue) != 0 and packed == 0:
            packed = 1
        return packed


def source_channel_from_mask(mask: int) -> PrematchPixelChannel:
    """Mirror 0x653120's two shift-count loops for one DDPIXELFORMAT mask."""
    if type(mask) is not int or mask <= 0 or mask > 0xFFFFFFFF:
        raise PrematchPixelFormatError("pixel mask must be a nonzero uint32")

    normalized = mask
    left_shift = 0
    while (normalized & 1) == 0:
        normalized >>= 1
        left_shift += 1

    right_shift = 0
    # 0x653120 tests AL bit 7 while repeatedly shifting EAX left.
    while (normalized & 0x80) == 0:
        normalized = (normalized << 1) & 0xFFFFFFFF
        right_shift += 1
        if right_shift > 8:
            raise PrematchPixelFormatError(
                "channel mask cannot be normalized into an 8-bit source component"
            )

    return PrematchPixelChannel(
        mask=mask,
        left_shift=left_shift,
        right_shift=right_shift,
    )


def source_rgb16_format(
    *,
    red_mask: int,
    green_mask: int,
    blue_mask: int,
) -> PrematchRGB16Format:
    """Build the exact descriptor 0x6530D0 derives from a 16-bit surface."""
    return PrematchRGB16Format(
        bit_count=16,
        red=source_channel_from_mask(red_mask),
        green=source_channel_from_mask(green_mask),
        blue=source_channel_from_mask(blue_mask),
    )


def pack_rgba_to_source_rgb16(
    rgba: bytes,
    *,
    pixel_format: PrematchRGB16Format,
) -> bytes:
    """Apply 0x5E4980's RGB packing to an RGBA source plane.

    Alpha-zero pixels represent source index zero and therefore preserve the
    native no-write semantics as packed zero in this standalone plane.
    """
    if not isinstance(rgba, bytes) or len(rgba) % 4:
        raise PrematchPixelFormatError("RGBA source must contain whole pixels")
    if type(pixel_format) is not PrematchRGB16Format:
        raise PrematchPixelFormatError("exact PrematchRGB16Format is required")

    output = bytearray((len(rgba) // 4) * 2)
    for index in range(len(rgba) // 4):
        src = index * 4
        alpha = rgba[src + 3]
        if alpha == 0:
            packed = 0
        else:
            packed = pixel_format.pack_rgb(
                rgba[src],
                rgba[src + 1],
                rgba[src + 2],
            )
        dst = index * 2
        output[dst] = packed & 0xFF
        output[dst + 1] = (packed >> 8) & 0xFF
    return bytes(output)


def prematch_pixel_format_contract() -> dict:
    return {
        "pixel_format_query_va": PREMATCH_PIXEL_FORMAT_QUERY_VA,
        "pixel_format_build_va": PREMATCH_PIXEL_FORMAT_BUILD_VA,
        "channel_build_va": PREMATCH_PIXEL_CHANNEL_BUILD_VA,
        "shirt_copy_va": PREMATCH_GENERIC_SHIRT_COPY_VA,
        "pixel_format_global_va": PREMATCH_PIXEL_FORMAT_GLOBAL_VA,
        "red_channel_global_va": PREMATCH_RED_CHANNEL_GLOBAL_VA,
        "green_channel_global_va": PREMATCH_GREEN_CHANNEL_GLOBAL_VA,
        "blue_channel_global_va": PREMATCH_BLUE_CHANNEL_GLOBAL_VA,
        "channel_descriptor_layout": (
            PREMATCH_CHANNEL_MASK_OFFSET,
            PREMATCH_CHANNEL_LEFT_SHIFT_OFFSET,
            PREMATCH_CHANNEL_RIGHT_SHIFT_OFFSET,
        ),
        "packing_is_surface_mask_driven": True,
        "hardcoded_rgb565": False,
        "nonblack_zero_quantization_forced_to_one": True,
        "packing_algorithm_source_closed": True,
        "specific_runtime_surface_masks_required": True,
        "gate14_complete": False,
    }
