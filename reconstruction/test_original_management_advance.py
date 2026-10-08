from datetime import date, timedelta
import unittest

from original_management_advance import (
    NATIVE_DEFAULT_TURN_LENGTH, NATIVE_TURN_LENGTH_CHOICES,
    original_management_advance_target,
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


if __name__ == '__main__':
    unittest.main()
