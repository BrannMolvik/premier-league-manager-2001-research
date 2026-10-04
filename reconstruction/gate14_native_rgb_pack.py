"""Source-closed FM2001 RGB8 -> native packed-16 conversion.

The canonical executable derives one small metadata record per runtime channel
mask at 0x653120. It then uses 0x443E00 to quantize one 8-bit channel into that
mask and 0x443E20 to combine red, green, and blue.

This module mirrors only that source direction. It does not choose the runtime
mask values, which remain a strict Windows receipt, and it does not invent the
inverse packed-16 -> modern-RGBA expansion performed by the display path.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_font_blend_source_trace import (
    NATIVE_CHANNEL_MASK_METADATA_VA,
    Native16PixelMasks,
)


class Gate14NativeRgbPackError(ValueError):
    pass


NATIVE_CHANNEL_PACK_VA = 0x443E00
NATIVE_RGB_PACK_VA = 0x443E20


@dataclass(frozen=True)
class Native16ChannelPacking:
    """Source-equivalent metadata retained for one contiguous RGB mask."""

    mask: int
    placement_shift: int
    quantization_shift: int
    channel_bits: int

    def __post_init__(self) -> None:
        if type(self.mask) is not int or not 0 < self.mask <= 0xFFFF:
            raise Gate14NativeRgbPackError("channel mask must be a non-zero uint16")
        if any(
            type(value) is not int
            for value in (
                self.placement_shift,
                self.quantization_shift,
                self.channel_bits,
            )
        ):
            raise Gate14NativeRgbPackError("channel packing metadata must be integers")
        if not 0 <= self.placement_shift <= 15:
            raise Gate14NativeRgbPackError("placement_shift is outside uint16")
        if not 0 <= self.quantization_shift <= 7:
            raise Gate14NativeRgbPackError("quantization_shift must be 0..7")
        if not 1 <= self.channel_bits <= 8:
            raise Gate14NativeRgbPackError("channel_bits must be 1..8")
        expected = ((1 << self.channel_bits) - 1) << self.placement_shift
        if expected != self.mask:
            raise Gate14NativeRgbPackError(
                "channel metadata does not describe one contiguous source mask"
            )
        if self.quantization_shift != 8 - self.channel_bits:
            raise Gate14NativeRgbPackError(
                "quantization_shift must match the source 8-bit truncation width"
            )


def native_channel_packing(mask: int) -> Native16ChannelPacking:
    """Mirror 0x653120's metadata for one contiguous <=8-bit channel mask."""
    if type(mask) is not int or not 0 < mask <= 0xFFFF:
        raise Gate14NativeRgbPackError("channel mask must be a non-zero uint16")

    low_bit = mask & -mask
    placement_shift = low_bit.bit_length() - 1
    normalized = mask >> placement_shift
    if normalized & (normalized + 1):
        raise Gate14NativeRgbPackError(
            "channel mask must be contiguous for source packing"
        )
    channel_bits = normalized.bit_length()
    if channel_bits > 8:
        raise Gate14NativeRgbPackError(
            "source RGB8 packing does not accept channels wider than 8 bits"
        )
    return Native16ChannelPacking(
        mask=mask,
        placement_shift=placement_shift,
        quantization_shift=8 - channel_bits,
        channel_bits=channel_bits,
    )


def pack_native_channel8(value: int, packing: Native16ChannelPacking) -> int:
    """Mirror 0x443E00 for one source 8-bit channel."""
    if type(value) is not int or not 0 <= value <= 0xFF:
        raise Gate14NativeRgbPackError("channel value must be a uint8")
    if type(packing) is not Native16ChannelPacking:
        raise Gate14NativeRgbPackError(
            "packing must be an exact Native16ChannelPacking"
        )
    return (
        ((value & 0xFF) >> packing.quantization_shift)
        << packing.placement_shift
    ) & packing.mask


def pack_native_rgb16(
    red: int,
    green: int,
    blue: int,
    masks: Native16PixelMasks,
) -> int:
    """Mirror 0x443E20 using the active runtime RGB mask triplet."""
    if type(masks) is not Native16PixelMasks:
        raise Gate14NativeRgbPackError("masks must be exact Native16PixelMasks")
    red_packing = native_channel_packing(masks.red)
    green_packing = native_channel_packing(masks.green)
    blue_packing = native_channel_packing(masks.blue)
    return (
        pack_native_channel8(red, red_packing)
        | pack_native_channel8(green, green_packing)
        | pack_native_channel8(blue, blue_packing)
    ) & 0xFFFF


def native_rgb_pack_contract() -> dict:
    """Expose the exact recovered conversion boundary without mask guessing."""
    return {
        "channel_mask_metadata_va": NATIVE_CHANNEL_MASK_METADATA_VA,
        "channel_pack_va": NATIVE_CHANNEL_PACK_VA,
        "rgb_pack_va": NATIVE_RGB_PACK_VA,
        "input_channel_bits": 8,
        "runtime_mask_values_recovered": False,
        "rgb8_to_packed16_recovered": True,
        "packed16_to_modern_rgba_recovered": False,
        "cross_component_pixels_resolvable": False,
        "complete_fastview_frame_recovered": False,
        "evidence_limit": (
            "The executable proves how each 8-bit channel is truncated and "
            "shifted into an already-observed runtime mask. This contract does "
            "not choose RGB565/RGB555, recover the display-side packed16-to-RGBA "
            "expansion, resolve overlap pixels, or complete FastView."
        ),
    }
