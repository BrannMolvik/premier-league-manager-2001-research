import unittest
from original_fixture_match_info_link import (
    fixture_cell_at_screen_point, resolve_source_match_info_link,
    source_report_capture_eligible, source_fixture_report_control_accepts,
    source_fixture_report_hover_accepts,
)


class FixtureMatchInfoLinkTests(unittest.TestCase):
    def test_capture_counts_and_developer_bypass_are_independent_of_results(self):
        for home, away in ((1, 1), (18, 18), (0xFFFFFFFF, 1)):
            self.assertTrue(source_report_capture_eligible(
                home, away, skip_match_calculation=False))
            self.assertFalse(source_report_capture_eligible(
                home, away, skip_match_calculation=True))
        for home, away in ((0, 0), (0, 18), (18, 0)):
            self.assertFalse(source_report_capture_eligible(
                home, away, skip_match_calculation=False))

    def test_native_event_guards_do_not_promote_completed_match_to_context(self):
        for flags in (2, 3, 0x12, 0xFFFFFFFF & ~0x20):
            self.assertTrue(source_fixture_report_control_accepts(flags))
        for flags in (0, 1, 0x20, 0x22, 0x23):
            self.assertFalse(source_fixture_report_control_accepts(flags))
        self.assertFalse(source_fixture_report_hover_accepts(None))
        self.assertFalse(source_fixture_report_hover_accepts(0x20))
        self.assertTrue(source_fixture_report_hover_accepts(0x21))
        self.assertIsNone(resolve_source_match_info_link(0xFFFF, ()))

    def test_native_inputs_are_not_coerced(self):
        for value in (-1, True, '18', 0x100000000):
            with self.assertRaises(ValueError):
                source_report_capture_eligible(value, 18, skip_match_calculation=False)
            with self.assertRaises(ValueError):
                source_fixture_report_control_accepts(value)
            with self.assertRaises(ValueError):
                source_fixture_report_hover_accepts(value)
        with self.assertRaises(ValueError):
            source_report_capture_eligible(18, 18, skip_match_calculation=0)

    def test_source_grid_extent_and_gaps(self):
        self.assertEqual(fixture_cell_at_screen_point(378, 235), (0, 0))
        self.assertEqual(fixture_cell_at_screen_point(406, 248), (0, 0))
        self.assertEqual(fixture_cell_at_screen_point(407, 249), (1, 1))
        self.assertEqual(fixture_cell_at_screen_point(725, 570), (11, 23))
        for point in ((377, 235), (378, 234), (726, 570), (725, 571)):
            self.assertIsNone(fixture_cell_at_screen_point(*point))

    def test_signed_word_sentinel_and_missing_nodes(self):
        first, second = object(), object()
        reports = (first, second, None)
        self.assertIs(resolve_source_match_info_link(0, reports), first)
        self.assertIs(resolve_source_match_info_link(1, reports), second)
        for word in (2, 3, 0x7FFF, 0x8000, 0xFFFE, 0xFFFF):
            self.assertIsNone(resolve_source_match_info_link(word, reports))
        self.assertIsNone(resolve_source_match_info_link(0, ()))

    def test_no_coercion_or_score_derived_context(self):
        for word in (-1, 0x10000, True, '0'):
            with self.assertRaises(ValueError):
                resolve_source_match_info_link(word, ())
        with self.assertRaises(ValueError):
            resolve_source_match_info_link(0, [])
        with self.assertRaises(ValueError):
            fixture_cell_at_screen_point(True, 235)
