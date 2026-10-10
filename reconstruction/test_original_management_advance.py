from datetime import date, timedelta
import unittest

from original_management_advance import (
    NATIVE_DEFAULT_TURN_LENGTH, NATIVE_TURN_LENGTH_CHOICES,
    original_management_advance_target, original_pitch_event_season_matches,
)


class NativeAdvanceTargetTests(unittest.TestCase):
    today = date(2000, 8, 1)
    end = date(2001, 7, 1)

    def target(self, delta, **kwargs):
        return original_management_advance_target(self.today,
            next_match_date=None if delta is None else self.today + timedelta(days=delta),
            selector_source_qualified=True, container_end_date=self.end, **kwargs)

    def test_constructor_and_original_option_choices(self):
        self.assertEqual(NATIVE_DEFAULT_TURN_LENGTH, 7)
        self.assertEqual(NATIVE_TURN_LENGTH_CHOICES, (1, 2, 3, 7, 14))

    def test_stops_before_distant_match_but_reaches_tomorrow(self):
        for delta, advance in ((0,0),(1,1),(2,1),(7,6),(8,7),(30,7)):
            with self.subTest(delta=delta):
                result = self.target(delta)
                self.assertEqual(result.target_date, self.today + timedelta(days=advance))
                self.assertEqual(result.processing_dates,
                    tuple(self.today + timedelta(days=i) for i in range(1, advance+1)))

    def test_qualified_null_is_capped_not_jump_to_season_end(self):
        self.assertEqual(self.target(None).target_date, self.today + timedelta(days=7))
        self.assertEqual(self.target(None, turn_length=0).processing_dates, ())
        result = original_management_advance_target(self.today, next_match_date=None,
            selector_source_qualified=True, container_end_date=self.today+timedelta(days=3))
        self.assertEqual(result.target_date, self.today+timedelta(days=2))

    def test_explicit_registry_length_preserved_not_rounded_to_ui_choice(self):
        self.assertEqual(self.target(30, turn_length=4).target_date,
                         self.today + timedelta(days=4))
        self.assertEqual(self.target(30, turn_length=0x7FFFFFFF).target_date,
                         self.today + timedelta(days=29))

    def test_unknown_is_not_native_null(self):
        for qualified in (False, None, 1):
            with self.subTest(qualified=qualified), self.assertRaisesRegex(RuntimeError, 'selector'):
                original_management_advance_target(self.today, next_match_date=None,
                    selector_source_qualified=qualified, container_end_date=self.end)

    def test_invalid_contexts_fail_closed(self):
        for value in (True, -1, 0x80000000, 7.0, '7'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.target(8, turn_length=value)
        for delta in (-1, 365):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                self.target(delta)
        with self.assertRaisesRegex(RuntimeError, 'annual'):
            original_management_advance_target(self.today, next_match_date=None,
                selector_source_qualified=True, container_end_date=self.today)


class NativePitchEventSeasonTests(unittest.TestCase):
    def test_exact_lower_inclusive_upper_exclusive_intervals(self):
        for month, day, selected in (
            (2,22,2), (5,21,2), (5,22,4), (8,21,4),
            (8,22,8), (11,21,8), (11,22,16), (12,31,16),
        ):
            for mask in range(256):
                with self.subTest(month=month, day=day, mask=mask):
                    self.assertEqual(
                        original_pitch_event_season_matches((100,month,day), mask),
                        bool(selected & mask))

    def test_early_year_retains_mask_not_synthetic_winter(self):
        for calendar in ((100,1,1), (100,1,31), (100,2,21)):
            for mask in range(256):
                with self.subTest(calendar=calendar, mask=mask):
                    self.assertEqual(original_pitch_event_season_matches(calendar, mask),
                                     bool(mask))
        # Source bit1/bit128 are accepted early, but not in the late-year16 arm.
        self.assertTrue(original_pitch_event_season_matches((100,2,21), 128))
        self.assertFalse(original_pitch_event_season_matches((100,12,31), 128))

    def test_native_leap_century_tuple_not_host_gregorian(self):
        self.assertTrue(original_pitch_event_season_matches((200,2,29), 2))
        self.assertFalse(original_pitch_event_season_matches((200,2,29), 16))
        for year in (0,1,2,3,101,201):
            with self.subTest(year=year), self.assertRaises(ValueError):
                original_pitch_event_season_matches((year,2,29), 255)

    def test_zero_mask_never_creates_an_event(self):
        for month in range(1,13):
            self.assertFalse(original_pitch_event_season_matches((100,month,1), 0))

    def test_missing_or_malformed_source_inputs_reject(self):
        for calendar in (None, date(2000,7,4), [100,7,4], (100,7),
                         (True,7,4), (-1,7,4), (8100,7,4), (100,0,4),
                         (100,13,4), (100,7,0), (100,4,31)):
            with self.subTest(calendar=calendar), self.assertRaises(ValueError):
                original_pitch_event_season_matches(calendar, 255)
        for mask in (None, True, -1, 256, '2', 2.0):
            with self.subTest(mask=mask), self.assertRaises(ValueError):
                original_pitch_event_season_matches((100,7,4), mask)


if __name__ == '__main__':
    unittest.main()
