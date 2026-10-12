"""Pure source-contract tests, not original GUI acceptance."""
import unittest

from original_supportstart_stars import (
    STAR_RESOURCE,
    STAR_SOURCE_SIZE,
    STAR_WRAPPERS,
    original_supportstart_star_frame,
    original_supportstart_star_local_rect,
)


class OriginalSupportStartStarTests(unittest.TestCase):
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
