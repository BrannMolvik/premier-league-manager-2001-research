"""Tests for source-closed FastView surfaced-control ownership."""
import unittest

from gate14_fastview_surfaced_picture_source import (
    AWAY_BADGE_RECT,
    BADGE_GENERIC_FALLBACK,
    BADGE_VARIANT,
    CLUB_GRAPHICS_BASENAME_OFFSET,
    COUNTRY_GRAPHICS_DIRECTORY_OFFSET,
    FULL_SURFACE_RECT,
    HOME_BADGE_RECT,
    MATCH_AWAY_SIDE_OFFSET,
    MATCH_HOME_SIDE_OFFSET,
    REAL_FIXTURE_AWAY_CLUB_OFFSET,
    REAL_FIXTURE_HOME_CLUB_OFFSET,
    SURFACED_CONTROLS,
    TEAM_BACKGROUND_GENERIC_FALLBACK,
    badge_source_path,
    surfaced_picture_source_contract,
)


class FastViewSurfacedPictureSourceTests(unittest.TestCase):
    def test_three_outer_controls_keep_exact_source_geometry_and_semantics(self):
        self.assertEqual(
            tuple((item.semantic, item.rect) for item in SURFACED_CONTROLS),
            (
                ("match_club_background_surface", FULL_SURFACE_RECT),
                ("home_club_badge", HOME_BADGE_RECT),
                ("away_club_badge", AWAY_BADGE_RECT),
            ),
        )
        self.assertEqual(FULL_SURFACE_RECT, (0, 0, 800, 600))
        self.assertEqual(HOME_BADGE_RECT, (38, 1, 173, 94))
        self.assertEqual(AWAY_BADGE_RECT, (627, 1, 762, 94))

    def test_home_away_orientation_is_source_dataflow_not_screen_guess(self):
        self.assertEqual(REAL_FIXTURE_HOME_CLUB_OFFSET, 0x0C)
        self.assertEqual(REAL_FIXTURE_AWAY_CLUB_OFFSET, 0x10)
        self.assertEqual(MATCH_HOME_SIDE_OFFSET, 0x14)
        self.assertEqual(MATCH_AWAY_SIDE_OFFSET, 0x28)
        self.assertEqual(SURFACED_CONTROLS[1].match_side_offset, 0x14)
        self.assertEqual(SURFACED_CONTROLS[2].match_side_offset, 0x28)

    def test_badge_path_uses_source_country_and_club_graphics_fields(self):
        self.assertEqual(CLUB_GRAPHICS_BASENAME_OFFSET, 0xE0)
        self.assertEqual(COUNTRY_GRAPHICS_DIRECTORY_OFFSET, 0x34)
        self.assertEqual(BADGE_VARIANT, "badge_2")
        self.assertEqual(
            badge_source_path("England", "arsenal"),
            r"FM2001_Art\Generic\Team_badge_stills\England\arsenal_badge_2.444",
        )
        self.assertTrue(BADGE_GENERIC_FALLBACK.endswith(r"team_badge_stills\generic.444"))
        with self.assertRaises(ValueError):
            badge_source_path("", "arsenal")
        with self.assertRaises(ValueError):
            badge_source_path("England", "bad/name")

    def test_background_ownership_is_closed_but_dynamic_variant_remains_open(self):
        contract = surfaced_picture_source_contract()
        self.assertTrue(contract["badge_variant_source_closed"])
        self.assertTrue(contract["badge_home_away_orientation_source_closed"])
        self.assertTrue(contract["full_surface_club_background_ownership_source_closed"])
        self.assertFalse(contract["full_surface_background_index_source_closed"])
        self.assertFalse(contract["surfaced_picture_pixels_staged"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])
        self.assertTrue(TEAM_BACKGROUND_GENERIC_FALLBACK.endswith(r"Team_backgrounds\generic.444"))


if __name__ == "__main__":
    unittest.main()
