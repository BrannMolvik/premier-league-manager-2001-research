import unittest

from ea444_decoder import EA444DecodedImage
from original_fastview_league_scores_art import (
    OriginalFastViewLeagueScoresArtError,
    build_current_fixture_grid_art,
)


class OriginalFastViewLeagueScoresArtTests(unittest.TestCase):
    def test_exact_owner_local_grid_placement_only(self):
        decoded = EA444DecodedImage(
            width=309,
            height=19,
            rgba=bytes([7]) * (309 * 19 * 4),
            consumed_bits=0,
            transparent_pixels=0,
        )
        art = build_current_fixture_grid_art(decoded)
        self.assertEqual(
            art.current_fixture_grid.owner_local_rect,
            (38, 32, 347, 51),
        )
        self.assertFalse(art.screen_absolute_rect_recovered)
        self.assertFalse(art.score_composite_grid2_geometry_recovered)

    def test_wrong_geometry_fails_closed(self):
        decoded = EA444DecodedImage(
            width=309,
            height=18,
            rgba=bytes([1]) * (309 * 18 * 4),
            consumed_bits=0,
            transparent_pixels=0,
        )
        with self.assertRaisesRegex(
            OriginalFastViewLeagueScoresArtError,
            "geometry mismatch",
        ):
            build_current_fixture_grid_art(decoded)


if __name__ == "__main__":
    unittest.main()
