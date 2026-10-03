import unittest

from gate14_fastview_clock import (
    SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE,
    SOURCE_CLOCK_FORMAT,
    SOURCE_CLOCK_RECEIVER_VA,
    SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE,
    SOURCE_CLOCK_TEXT_RECT,
    SOURCE_POSSESSION_ARRAY_LOOKUP_VA,
    FastViewClockError,
    fastview_clock_numeric_value,
    possession_array_index_for_global_tick,
)


class FastViewClockTests(unittest.TestCase):
    def test_clock_uses_same_global_tick_numeric_value(self):
        self.assertEqual(SOURCE_CLOCK_RECEIVER_VA, 0x51EDB0)
        self.assertEqual(SOURCE_CLOCK_FORMAT, "%u %s")
        self.assertEqual(SOURCE_CLOCK_TEXT_RECT, (439, 44, 621, 64))
        self.assertEqual(SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE, 46)
        self.assertEqual(SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE, 91)
        for value in (0, 1, 5, 45, 46, 90, 91, 120):
            with self.subTest(value=value):
                self.assertEqual(fastview_clock_numeric_value(value), value)

    def test_possession_lookup_uses_global_tick_divided_by_five(self):
        self.assertEqual(SOURCE_POSSESSION_ARRAY_LOOKUP_VA, 0x631240)
        self.assertEqual(possession_array_index_for_global_tick(0), 0)
        self.assertEqual(possession_array_index_for_global_tick(5), 1)
        self.assertEqual(possession_array_index_for_global_tick(40), 8)
        self.assertEqual(possession_array_index_for_global_tick(90), 18)

    def test_non_boundary_or_invalid_values_fail_closed(self):
        with self.assertRaises(FastViewClockError):
            fastview_clock_numeric_value(-1)
        with self.assertRaises(FastViewClockError):
            possession_array_index_for_global_tick(7)
        with self.assertRaises(FastViewClockError):
            possession_array_index_for_global_tick(True)


if __name__ == "__main__":
    unittest.main()
