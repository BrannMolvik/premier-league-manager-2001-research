"""Original-PE-based PLeagueFixtures country/League radio rectangle regressions."""
import unittest

from original_league_fixtures_radio_layout import (
    original_league_fixtures_radio_rects,
    original_league_fixtures_radio_candidate_at_point,
)


class SourceRadioLayoutTests(unittest.TestCase):
    def test_all_country_radios_and_full_six_leagues(self):
        rows = original_league_fixtures_radio_rects(league_option_count=6)
        self.assertEqual(len(rows), 14)
        self.assertEqual([(v.family, v.index, v.event_id) for v in rows[:8]],
                         [("country", i, i + 1) for i in range(8)])
        self.assertEqual([(v.family, v.index, v.event_id) for v in rows[8:]],
                         [("league", i, i + 9) for i in range(6)])
        self.assertEqual([v.rect for v in rows[:8]],
                         [(27, 256 + 20*i, 182, 18) for i in range(8)])
        self.assertEqual([v.rect for v in rows[8:]],
                         [(27, 445 + 20*i, 182, 18) for i in range(6)])

    def test_english_source_five_leagues_suppress_hidden_sixth(self):
        rows = original_league_fixtures_radio_rects(league_option_count=5)
        self.assertEqual([row.event_id for row in rows[-5:]], [9, 10, 11, 12, 13])
        self.assertEqual(len(rows), 13)
        self.assertIsNone(original_league_fixtures_radio_candidate_at_point(
            40, 550, league_option_count=5))
        self.assertEqual(original_league_fixtures_radio_candidate_at_point(
            40, 540, league_option_count=5).event_id, 13)

    def test_exact_rectangle_edges_and_two_pixel_gaps(self):
        for count in (1, 5, 6):
            for radio in original_league_fixtures_radio_rects(league_option_count=count):
                x, y, width, height = radio.rect
                for px, py in ((x, y), (x+width-1, y), (x, y+height-1),
                               (x+width-1, y+height-1)):
                    self.assertEqual(original_league_fixtures_radio_candidate_at_point(
                        px, py, league_option_count=count), radio)
                for px, py in ((x-1, y), (x+width, y), (x, y+height)):
                    self.assertNotEqual(original_league_fixtures_radio_candidate_at_point(
                        px, py, league_option_count=count), radio)

    def test_country_to_league_gap_never_attributed_to_radio(self):
        for y in (414, 415, 423, 424, 443, 444):
            self.assertIsNone(original_league_fixtures_radio_candidate_at_point(
                27, y, league_option_count=6))

    def test_native_canvas_and_cross_panel_coordinates_fail_closed(self):
        for px, py in ((0, 260), (209, 260), (20, 450), (241, 450),
                       (70, 235), (70, 599), (70, 0), (-1, 256)):
            self.assertIsNone(original_league_fixtures_radio_candidate_at_point(
                px, py, league_option_count=6))

    def test_bad_source_counts_and_pointer_types_rejected(self):
        for n in (0, 7, -1, None, True, 5.0, "5"):
            with self.assertRaises(ValueError):
                original_league_fixtures_radio_rects(league_option_count=n)
        for x, y in ((True, 257), (28, False), (28.0, 257), (28, "257")):
            with self.assertRaises(ValueError):
                original_league_fixtures_radio_candidate_at_point(
                    x, y, league_option_count=5)


if __name__ == "__main__":
    unittest.main()
