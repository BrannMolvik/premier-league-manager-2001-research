"""Native rectangle/arithmetic contracts; not pixel/timing/drag certification."""
import unittest
from original_pmatchinfo_scroll_geometry import (
    THUMB_BIAS, THUMB_BIAS_FLOAT32_BITS, native_vertical_thumb_rectangles,
)


class NativeThumbGeometryTests(unittest.TestCase):
    def test_bias_is_original_float32_not_half(self):
        self.assertEqual(THUMB_BIAS_FLOAT32_BITS, 0x3EFF7CEE)
        self.assertEqual(float(THUMB_BIAS), 0.49900001287460327)

    def test_eight_entry_list_has_122_pixel_thumb_and_half_rounds_down(self):
        for first, y in ((0, 291), (1, 311), (2, 332)):
            rects = native_vertical_thumb_rectangles(8, first, 1)
            self.assertEqual([r.source_rect for r in rects],
                             [(0, 0, 18, 3), (0, 3, 18, 19), (0, 22, 18, 3)])
            self.assertEqual([r.destination_rect for r in rects],
                             [(17, y, 18, 3), (17, y + 3, 18, 116), (17, y + 119, 18, 3)])
            self.assertTrue(all(r.clip_rect == (17, 291, 18, 163) for r in rects))

    def test_right_list_and_hover_frame(self):
        rects = native_vertical_thumb_rectangles(8, 1, 0, source_hover=True)
        self.assertEqual(rects[0].source_rect, (36, 0, 18, 3))
        self.assertEqual(rects[0].destination_rect, (389, 311, 18, 3))

    def test_no_range_requires_qualified_mask_and_uses_disabled_full_thumb(self):
        for count in range(7):
            with self.subTest(count=count):
                with self.assertRaisesRegex(ValueError, 'mask is not qualified'):
                    native_vertical_thumb_rectangles(count, 0, 1)
                rects = native_vertical_thumb_rectangles(count, 0, 1, masked_x87_invalid=True)
                self.assertEqual(rects[0].source_rect, (54, 0, 18, 3))
                self.assertEqual(rects[1].destination_rect, (17, 294, 18, 157))
                self.assertEqual(rects[2].destination_rect, (17, 451, 18, 3))

    def test_minimum_thumb_cap_clamp(self):
        rects = native_vertical_thumb_rectangles(2046, 2040, 1)
        self.assertEqual([r.destination_rect[3] for r in rects], [3, 0, 3])
        self.assertEqual(rects[-1].destination_rect, (17, 451, 18, 3))

    def test_invalid_range_and_boolean_ints_fail_closed(self):
        for args in ((True, 0, 1), (-1, 0, 1), (2047, 0, 1), (8, 3, 1),
                     (8, -1, 1), (8, 0, True), (8, 0, 2)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                native_vertical_thumb_rectangles(*args)


if __name__ == '__main__':
    unittest.main()
