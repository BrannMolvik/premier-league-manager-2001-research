"""Regression coverage for source-exact PPreMatch legacy RGB packing."""
import unittest

from gate14_prematch_pixel_format import (
    PREMATCH_BLUE_CHANNEL_GLOBAL_VA,
    PREMATCH_GENERIC_SHIRT_COPY_VA,
    PREMATCH_GREEN_CHANNEL_GLOBAL_VA,
    PREMATCH_PIXEL_CHANNEL_BUILD_VA,
    PREMATCH_PIXEL_FORMAT_BUILD_VA,
    PREMATCH_PIXEL_FORMAT_GLOBAL_VA,
    PREMATCH_PIXEL_FORMAT_QUERY_VA,
    PREMATCH_RED_CHANNEL_GLOBAL_VA,
    PrematchPixelFormatError,
    pack_rgba_to_source_rgb16,
    prematch_pixel_format_contract,
    source_channel_from_mask,
    source_rgb16_format,
)


class PrematchPixelFormatTests(unittest.TestCase):
    def test_source_addresses_and_contract_are_exact(self):
        self.assertEqual(PREMATCH_PIXEL_FORMAT_QUERY_VA, 0x653090)
        self.assertEqual(PREMATCH_PIXEL_FORMAT_BUILD_VA, 0x6530D0)
        self.assertEqual(PREMATCH_PIXEL_CHANNEL_BUILD_VA, 0x653120)
        self.assertEqual(PREMATCH_GENERIC_SHIRT_COPY_VA, 0x5E4980)
        self.assertEqual(PREMATCH_PIXEL_FORMAT_GLOBAL_VA, 0x984820)
        self.assertEqual(PREMATCH_RED_CHANNEL_GLOBAL_VA, 0x984824)
        self.assertEqual(PREMATCH_GREEN_CHANNEL_GLOBAL_VA, 0x984830)
        self.assertEqual(PREMATCH_BLUE_CHANNEL_GLOBAL_VA, 0x98483C)

        contract = prematch_pixel_format_contract()
        self.assertTrue(contract["packing_is_surface_mask_driven"])
        self.assertFalse(contract["hardcoded_rgb565"])
        self.assertTrue(contract["nonblack_zero_quantization_forced_to_one"])
        self.assertTrue(contract["packing_algorithm_source_closed"])
        self.assertTrue(contract["specific_runtime_surface_masks_required"])
        self.assertFalse(contract["gate14_complete"])

    def test_653120_descriptor_for_rgb565(self):
        red = source_channel_from_mask(0xF800)
        green = source_channel_from_mask(0x07E0)
        blue = source_channel_from_mask(0x001F)
        self.assertEqual((red.left_shift, red.right_shift), (11, 3))
        self.assertEqual((green.left_shift, green.right_shift), (5, 2))
        self.assertEqual((blue.left_shift, blue.right_shift), (0, 3))

    def test_653120_descriptor_for_rgb555(self):
        red = source_channel_from_mask(0x7C00)
        green = source_channel_from_mask(0x03E0)
        blue = source_channel_from_mask(0x001F)
        self.assertEqual((red.left_shift, red.right_shift), (10, 3))
        self.assertEqual((green.left_shift, green.right_shift), (5, 3))
        self.assertEqual((blue.left_shift, blue.right_shift), (0, 3))

    def test_pack_matches_native_shift_or_rule_for_rgb565(self):
        fmt = source_rgb16_format(
            red_mask=0xF800,
            green_mask=0x07E0,
            blue_mask=0x001F,
        )
        self.assertEqual(fmt.pack_rgb(255, 255, 255), 0xFFFF)
        self.assertEqual(fmt.pack_rgb(255, 0, 0), 0xF800)
        self.assertEqual(fmt.pack_rgb(0, 255, 0), 0x07E0)
        self.assertEqual(fmt.pack_rgb(0, 0, 255), 0x001F)
        self.assertEqual(fmt.pack_rgb(0, 0, 0), 0x0000)

        # Native 0x5E4980 prevents a nonblack source from quantizing to zero.
        self.assertEqual(fmt.pack_rgb(1, 1, 1), 0x0001)

    def test_rgba_plane_preserves_index_zero_no_write_as_zero_word(self):
        fmt = source_rgb16_format(
            red_mask=0xF800,
            green_mask=0x07E0,
            blue_mask=0x001F,
        )
        packed = pack_rgba_to_source_rgb16(
            bytes(
                (
                    255, 0, 0, 255,
                    0, 255, 0, 255,
                    1, 1, 1, 255,
                    255, 255, 255, 0,
                )
            ),
            pixel_format=fmt,
        )
        self.assertEqual(
            packed,
            bytes(
                (
                    0x00, 0xF8,
                    0xE0, 0x07,
                    0x01, 0x00,
                    0x00, 0x00,
                )
            ),
        )

    def test_invalid_masks_fail_closed(self):
        with self.assertRaises(PrematchPixelFormatError):
            source_channel_from_mask(0)
        with self.assertRaisesRegex(PrematchPixelFormatError, "overlap"):
            source_rgb16_format(
                red_mask=0xF800,
                green_mask=0xF800,
                blue_mask=0x001F,
            )


if __name__ == "__main__":
    unittest.main()
