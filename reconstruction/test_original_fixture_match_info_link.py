import unittest
from original_fixture_match_info_link import (
    fixture_cell_at_screen_point, resolve_source_match_info_link,
)


class FixtureMatchInfoLinkTests(unittest.TestCase):
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
