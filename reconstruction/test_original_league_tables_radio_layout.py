"""Native original PE source geometry regressions for Tables radio candidates."""
import unittest

from original_league_tables_radio_layout import (
    original_league_tables_radio_candidate_at_point,
    original_league_tables_radio_rects,
)


class OriginalLeagueTablesRadioGeometryTests(unittest.TestCase):
    def test_source_control_census_events_and_three_distinct_families(self):
        rows = original_league_tables_radio_rects(division_option_count=5)
        self.assertEqual(len(rows), 15)
        self.assertEqual([(r.family, r.index, r.event_id) for r in rows],
                         [("country", i, i + 1) for i in range(8)] +
                         [("division", i, i + 9) for i in range(5)] +
                         [("sort", i, i + 14) for i in range(2)])
        self.assertEqual([r.rect for r in rows[:8]],
                         [(27, 172 + 20*i, 182, 18) for i in range(8)])
        self.assertEqual([r.rect for r in rows[8:13]],
                         [(27, 361 + 20*i, 182, 18) for i in range(5)])
        self.assertEqual([r.rect for r in rows[13:]],
                         [(27, 490 + 20*i, 182, 18) for i in range(2)])

    def test_hidden_divisions_do_not_become_clickable_candidates(self):
        rows = original_league_tables_radio_rects(division_option_count=1)
        self.assertEqual([r.event_id for r in rows], list(range(1, 10)) + [14, 15])
        self.assertIsNone(original_league_tables_radio_candidate_at_point(
            40, 382, division_option_count=1))
        self.assertEqual(original_league_tables_radio_candidate_at_point(
            40, 492, division_option_count=1).event_id, 14)

    def test_edges_are_half_open_and_2px_gutters_unclaimed(self):
        for count in (1, 3, 5):
            for r in original_league_tables_radio_rects(division_option_count=count):
                x, y, w, h = r.rect
                for px, py in ((x, y), (x+w-1, y), (x, y+h-1), (x+w-1, y+h-1)):
                    self.assertEqual(original_league_tables_radio_candidate_at_point(
                        px, py, division_option_count=count), r)
                for px, py in ((x-1, y), (x+w, y), (x, y+h)):
                    self.assertNotEqual(original_league_tables_radio_candidate_at_point(
                        px, py, division_option_count=count), r)

    def test_headers_and_gaps_not_registered_as_radio(self):
        for y in (150, 170, 171, 190, 330, 339, 340, 359, 360,
                  459, 468, 469, 488, 489, 508, 509, 530):
            self.assertIsNone(original_league_tables_radio_candidate_at_point(
                40, y, division_option_count=5), y)

    def test_invalid_count_types_coordinates_and_cross_panel_fail_closed(self):
        for x, y in ((0, 176), (26, 176), (209, 176), (240, 361),
                     (27, 600), (-1, 180), (70, 5)):
            self.assertIsNone(original_league_tables_radio_candidate_at_point(
                x, y, division_option_count=5))
        for count in (0, 6, -1, None, True, 2.0, "2"):
            with self.subTest(count=count), self.assertRaises(ValueError):
                original_league_tables_radio_rects(division_option_count=count)
        for x, y in ((True, 173), (40, False), (40.0, 173), (40, "173")):
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                original_league_tables_radio_candidate_at_point(
                    x, y, division_option_count=5)


if __name__ == "__main__":
    unittest.main()
