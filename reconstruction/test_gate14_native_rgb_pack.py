"""Tests for source-closed FM2001 RGB8 -> packed-16 conversion."""
from dataclasses import replace
import unittest

from gate14_font_blend_source_trace import Native16PixelMasks
from gate14_native_rgb_pack import (
    NATIVE_CHANNEL_PACK_VA,
    NATIVE_RGB_PACK_VA,
    Gate14NativeRgbPackError,
    Native16ChannelPacking,
    native_channel_packing,
    native_rgb_pack_contract,
    pack_native_channel8,
    pack_native_rgb16,
)


class Gate14NativeRgbPackTests(unittest.TestCase):
    def test_rgb565_metadata_matches_source_shift_algorithm(self):
        red = native_channel_packing(0xF800)
        green = native_channel_packing(0x07E0)
        blue = native_channel_packing(0x001F)

        self.assertEqual(
            red,
            Native16ChannelPacking(
                mask=0xF800,
                placement_shift=11,
                quantization_shift=3,
                channel_bits=5,
            ),
        )
        self.assertEqual(
            green,
            Native16ChannelPacking(
                mask=0x07E0,
                placement_shift=5,
                quantization_shift=2,
                channel_bits=6,
            ),
        )
        self.assertEqual(
            blue,
            Native16ChannelPacking(
                mask=0x001F,
                placement_shift=0,
                quantization_shift=3,
                channel_bits=5,
            ),
        )

    def test_rgb565_and_rgb555_pack_exact_channel_endpoints(self):
        rgb565 = Native16PixelMasks(red=0xF800, green=0x07E0, blue=0x001F)
        self.assertEqual(pack_native_rgb16(255, 255, 255, rgb565), 0xFFFF)
        self.assertEqual(pack_native_rgb16(255, 0, 0, rgb565), 0xF800)
        self.assertEqual(pack_native_rgb16(0, 255, 0, rgb565), 0x07E0)
        self.assertEqual(pack_native_rgb16(0, 0, 255, rgb565), 0x001F)
        self.assertEqual(pack_native_rgb16(128, 0, 0, rgb565), 0x8000)

        rgb555 = Native16PixelMasks(red=0x7C00, green=0x03E0, blue=0x001F)
        self.assertEqual(pack_native_rgb16(255, 255, 255, rgb555), 0x7FFF)
        self.assertEqual(pack_native_rgb16(255, 0, 0, rgb555), 0x7C00)
        self.assertEqual(pack_native_rgb16(0, 255, 0, rgb555), 0x03E0)
        self.assertEqual(pack_native_rgb16(0, 0, 255, rgb555), 0x001F)

    def test_single_channel_pack_uses_truncation_not_rounding(self):
        packing = native_channel_packing(0x001F)
        self.assertEqual(pack_native_channel8(0, packing), 0)
        self.assertEqual(pack_native_channel8(7, packing), 0)
        self.assertEqual(pack_native_channel8(8, packing), 1)
        self.assertEqual(pack_native_channel8(254, packing), 31)
        self.assertEqual(pack_native_channel8(255, packing), 31)

    def test_rejects_noncontiguous_too_wide_or_invalid_values(self):
        with self.assertRaisesRegex(
            Gate14NativeRgbPackError,
            "contiguous",
        ):
            native_channel_packing(0x0520)
        with self.assertRaisesRegex(
            Gate14NativeRgbPackError,
            "wider than 8",
        ):
            native_channel_packing(0x01FF)
        with self.assertRaisesRegex(
            Gate14NativeRgbPackError,
            "uint8",
        ):
            pack_native_channel8(256, native_channel_packing(0x001F))
        with self.assertRaisesRegex(
            Gate14NativeRgbPackError,
            "exact Native16PixelMasks",
        ):
            pack_native_rgb16(1, 2, 3, object())

    def test_metadata_record_rejects_false_source_semantics(self):
        packing = native_channel_packing(0xF800)
        with self.assertRaisesRegex(
            Gate14NativeRgbPackError,
            "does not describe",
        ):
            replace(packing, placement_shift=10)
        with self.assertRaisesRegex(
            Gate14NativeRgbPackError,
            "quantization_shift",
        ):
            replace(packing, quantization_shift=2)

    def test_contract_keeps_runtime_values_and_modern_expansion_fail_closed(self):
        contract = native_rgb_pack_contract()
        self.assertEqual(contract["channel_pack_va"], NATIVE_CHANNEL_PACK_VA)
        self.assertEqual(contract["rgb_pack_va"], NATIVE_RGB_PACK_VA)
        self.assertEqual(NATIVE_CHANNEL_PACK_VA, 0x443E00)
        self.assertEqual(NATIVE_RGB_PACK_VA, 0x443E20)
        self.assertEqual(contract["input_channel_bits"], 8)
        self.assertTrue(contract["rgb8_to_packed16_recovered"])
        self.assertFalse(contract["runtime_mask_values_recovered"])
        self.assertFalse(contract["packed16_to_modern_rgba_recovered"])
        self.assertFalse(contract["cross_component_pixels_resolvable"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])


if __name__ == "__main__":
    unittest.main()
