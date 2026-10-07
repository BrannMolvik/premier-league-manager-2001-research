"""Regression coverage for the source RGB stage of generic PPreMatch shirts."""
import struct
import unittest
from unittest.mock import patch

from gate14_prematch_generic_shirt import (
    PREMATCH_GENERIC_SHIRT_COLOR_TABLE_BYTES,
    PREMATCH_GENERIC_SHIRT_COLOR_TABLE_VA,
    PREMATCH_GENERIC_SHIRT_COPY_VA,
    PREMATCH_GENERIC_SHIRT_GRADIENT_VA,
    PREMATCH_GENERIC_SHIRT_RECOLOR_VA,
    PrematchGenericShirtError,
    _native_gradient,
    parse_prematch_generic_bmp,
    prematch_generic_shirt_contract,
    recolor_prematch_generic_shirt,
)
from gate14_prematch_shirt_selection import (
    PrematchClubShirtState,
    select_prematch_team_kits,
)


def bmp_with_rows(rows):
    width, height = 36, 1280
    stride = 36
    palette = bytearray(256 * 4)
    # Preserve a source palette value beyond the rewritten 1..79 ranges.
    palette[80 * 4:80 * 4 + 4] = bytes((9, 8, 7, 0))  # B,G,R,0 -> RGB 7,8,9
    pixel_offset = 14 + 40 + len(palette)
    pixels = bytearray(stride * height)
    for output_y, values in rows.items():
        source_y = height - 1 - output_y
        start = source_y * stride
        pixels[start:start + len(values)] = bytes(values)
    total = pixel_offset + len(pixels)
    header = bytearray(14 + 40)
    header[:2] = b"BM"
    struct.pack_into("<I", header, 2, total)
    struct.pack_into("<I", header, 10, pixel_offset)
    struct.pack_into("<I", header, 14, 40)
    struct.pack_into("<ii", header, 18, width, height)
    struct.pack_into("<HH", header, 26, 1, 8)
    struct.pack_into("<I", header, 30, 0)
    struct.pack_into("<I", header, 34, len(pixels))
    struct.pack_into("<I", header, 46, 256)
    return bytes(header + palette + pixels)


def color_table():
    table = bytearray(PREMATCH_GENERIC_SHIRT_COLOR_TABLE_BYTES)
    # Source records are two RGB endpoints separated by one unused byte each.
    table[1 * 8:1 * 8 + 8] = bytes((10, 20, 30, 0, 40, 50, 60, 0))
    table[2 * 8:2 * 8 + 8] = bytes((100, 110, 120, 0, 160, 170, 180, 0))
    table[3 * 8:3 * 8 + 8] = bytes((1, 2, 3, 0, 4, 5, 6, 0))
    table[4 * 8:4 * 8 + 8] = bytes((11, 12, 13, 0, 14, 15, 16, 0))
    return bytes(table)


def no_clash_table():
    return bytes([23] * (23 * 6))


class PrematchGenericShirtTests(unittest.TestCase):
    def setUp(self):
        self.club = PrematchClubShirtState(
            club_id=10,
            graphics_basename="Arsenal",
            primary_template_index=1,
            alternate_template_index=7,
            primary_color_id=1,
            primary_secondary_color_id=2,
            alternate_color_id=3,
            alternate_secondary_color_id=4,
        )
        other = PrematchClubShirtState(
            club_id=11,
            graphics_basename="Chelsea",
            primary_template_index=2,
            alternate_template_index=8,
            primary_color_id=5,
            primary_secondary_color_id=6,
            alternate_color_id=7,
            alternate_secondary_color_id=8,
        )
        self.context = select_prematch_team_kits(
            self.club,
            other,
            clash_table=no_clash_table(),
        ).home

    def test_contract_keeps_legacy_display_packing_fail_closed(self):
        contract = prematch_generic_shirt_contract()
        self.assertEqual(PREMATCH_GENERIC_SHIRT_RECOLOR_VA, 0x5E4C60)
        self.assertEqual(PREMATCH_GENERIC_SHIRT_COPY_VA, 0x5E4980)
        self.assertEqual(PREMATCH_GENERIC_SHIRT_GRADIENT_VA, 0x5E4B10)
        self.assertEqual(PREMATCH_GENERIC_SHIRT_COLOR_TABLE_VA, 0x834190)
        self.assertEqual(contract["source_geometry"], (36, 1280))
        self.assertEqual(contract["frame_geometry"], (36, 32))
        self.assertEqual(contract["frame_count"], 40)
        self.assertTrue(contract["palette_index_zero_transparent"])
        self.assertTrue(contract["source_rgb_recolor_recovered"])
        self.assertFalse(contract["legacy_display_packing_recovered"])
        self.assertFalse(contract["complete_marker_pixels_recovered"])
        self.assertFalse(contract["gate14_complete"])

    def test_bmp_parser_preserves_top_down_index_order_and_source_palette(self):
        raw = bmp_with_rows({0: [1, 80], 1: [32, 64]})
        parsed = parse_prematch_generic_bmp(raw)
        self.assertEqual((parsed.width, parsed.height), (36, 1280))
        self.assertEqual(tuple(parsed.indices[:2]), (1, 80))
        self.assertEqual(tuple(parsed.indices[36:38]), (32, 64))
        self.assertEqual(parsed.palette_rgb[80], (7, 8, 9))

    def test_native_gradient_uses_signed_integer_step_then_exact_endpoint(self):
        gradient = dict(_native_gradient((100, 0, 0), (40, 30, 60), 1, 31))
        # Native idiv truncates -60/30 toward zero to -2 exactly.
        self.assertEqual(gradient[2], (98, 1, 2))
        self.assertEqual(gradient[30], (42, 29, 58))
        self.assertEqual(gradient[31], (40, 30, 60))

        # Non-divisible negative delta is also truncation toward zero, not floor.
        gradient = dict(_native_gradient((10, 10, 10), (0, 0, 0), 1, 4))
        self.assertEqual(gradient[2], (7, 7, 7))
        self.assertEqual(gradient[3], (4, 4, 4))
        self.assertEqual(gradient[4], (0, 0, 0))

    def test_recolor_rewrites_three_native_ranges_preserves_rest_and_transparency(self):
        raw = bmp_with_rows(
            {
                0: [1, 2, 31, 32, 33, 63, 64, 65, 79, 80, 0],
            }
        )
        with patch(
            "gate14_prematch_generic_shirt.prematch_generic_color_table_from_executable",
            return_value=color_table(),
        ):
            atlas = recolor_prematch_generic_shirt(
                raw,
                executable=b"canonical-test-double",
                club=self.club,
                context=self.context,
            )

        def pixel(index):
            start = index * 4
            return tuple(atlas.rgba[start:start + 4])

        self.assertEqual(pixel(0), (10, 20, 30, 255))
        self.assertEqual(pixel(1), (11, 21, 31, 255))
        self.assertEqual(pixel(2), (40, 50, 60, 255))
        self.assertEqual(pixel(3), (100, 110, 120, 255))
        # 60/31 truncates to one per channel until the exact endpoint.
        self.assertEqual(pixel(4), (101, 111, 121, 255))
        self.assertEqual(pixel(5), (160, 170, 180, 255))
        self.assertEqual(pixel(6), (255, 255, 255, 255))
        self.assertEqual(pixel(7), (238, 238, 238, 255))
        self.assertEqual(pixel(8), (0, 0, 0, 255))
        self.assertEqual(pixel(9), (7, 8, 9, 255))
        self.assertEqual(pixel(10), (0, 0, 0, 0))
        self.assertTrue(atlas.source_rgb_recolor_recovered)
        self.assertFalse(atlas.legacy_display_packing_recovered)

    def test_alternate_context_uses_alternate_two_color_ids(self):
        alternate_context = type(self.context)(
            use_alternate=True,
            selected_template_index=self.club.alternate_template_index,
            custom_source_path=None,
            generic_template_index=self.club.alternate_template_index,
            generic_source_path=r"fm2001_art\Generic\front-end-shirts\generic\Team07.bmp",
        )
        raw = bmp_with_rows({0: [1, 32]})
        with patch(
            "gate14_prematch_generic_shirt.prematch_generic_color_table_from_executable",
            return_value=color_table(),
        ):
            atlas = recolor_prematch_generic_shirt(
                raw,
                executable=b"canonical-test-double",
                club=self.club,
                context=alternate_context,
            )
        self.assertEqual(tuple(atlas.rgba[:4]), (1, 2, 3, 255))
        self.assertEqual(tuple(atlas.rgba[4:8]), (11, 12, 13, 255))
        self.assertEqual((atlas.primary_color_id, atlas.secondary_color_id), (3, 4))

    def test_invalid_bmp_fails_closed(self):
        with self.assertRaises(PrematchGenericShirtError):
            parse_prematch_generic_bmp(b"not-a-bmp")


if __name__ == "__main__":
    unittest.main()
