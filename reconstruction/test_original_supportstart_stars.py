"""Pure source-contract tests, not original GUI acceptance."""
import unittest
import hashlib
from pathlib import Path

from ea444_header import parse_ea444_header

from original_supportstart_stars import (
    STAR_RESOURCE,
    STAR_SOURCE_SIZE,
    STAR_WRAPPERS,
    original_supportstart_star_frame,
    original_supportstart_star_local_rect,
)


class OriginalSupportStartStarTests(unittest.TestCase):
    def test_staged_original_star_asset_is_byte_identical_and_real_ea444(self):
        # Source file exists intentionally in original_assets with provenance
        # and must match the owner's authenticated original, not replacement art.
        original = (Path(__file__).resolve().parents[1] / "original_assets"
                    / "source" / STAR_RESOURCE)
        data = original.read_bytes()
        self.assertEqual(len(data), 2776)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "16c619e305ebad013e7404ea9e5d4414a9f9a8bd0d6ad26f269ee82a49849633")
        dimensions = parse_ea444_header(data)
        self.assertEqual((dimensions.width, dimensions.height), STAR_SOURCE_SIZE)
        self.assertEqual(dimensions.payload_size, 2768)

    def test_all_five_native_cases_use_same_stars_strip(self):
        self.assertEqual(STAR_SOURCE_SIZE, (75, 10))
        self.assertEqual(len(STAR_WRAPPERS), 5)
        for n in range(1, 6):
            with self.subTest(state=n):
                frame = original_supportstart_star_frame(n)
                self.assertEqual(frame.wrapper_va, STAR_WRAPPERS[n - 1])
                self.assertEqual(frame.source_path, STAR_RESOURCE)
                self.assertEqual(frame.crop_left_top_right_bottom, (0, 0, 15*n, 10))

    def test_seven_native_row_star_child_rectangles_not_screen_hit_areas(self):
        self.assertEqual(original_supportstart_star_local_rect(0, 1), (621, 185, 15, 10))
        self.assertEqual(original_supportstart_star_local_rect(6, 5), (621, 425, 75, 10))
        self.assertEqual(original_supportstart_star_local_rect(3, 0), (621, 305, 0, 0))
        for bad_row in (-1, 7, False, 2.0, None):
            with self.subTest(row=bad_row):
                with self.assertRaises(ValueError):
                    original_supportstart_star_local_rect(bad_row, 3)

    def test_native_out_of_range_is_null_not_clamped(self):
        for n in (-100, -1, 0, 6, 7, 100):
            with self.subTest(state=n):
                self.assertIsNone(original_supportstart_star_frame(n))

    def test_port_rejects_noninteger_states_explicitly(self):
        for bad in (True, 3.0, None, "3"):
            with self.subTest(value=bad):
                with self.assertRaises(TypeError):
                    original_supportstart_star_frame(bad)


if __name__ == "__main__":
    unittest.main()
