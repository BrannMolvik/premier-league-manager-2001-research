"""Tests for source-closed FastView surfaced-control ownership."""
import unittest

from gate14_fastview_surfaced_picture_source import (
    AWAY_BADGE_RECT,
    BACKGROUND_CLIENT_CACHE_BASE_VA,
    BACKGROUND_CLIENT_CACHE_COUNT,
    BACKGROUND_CLIENT_CACHE_STRIDE,
    BACKGROUND_MONTH_TABLE_VA,
    BACKGROUND_RESOURCE_POOL_CAPACITY,
    BACKGROUND_RESOURCE_POOL_VA,
    BACKGROUND_VARIANT_BY_MONTH,
    BADGE_GENERIC_FALLBACK,
    BADGE_VARIANT,
    CLUB_GRAPHICS_BASENAME_OFFSET,
    COUNTRY_GRAPHICS_DIRECTORY_OFFSET,
    DATE_SPLIT_HELPER_VA,
    DBRCLUB_BACKGROUND_TIER_SOURCE_OFFSET,
    FASTVIEW_BACKGROUND_CLIENT_CACHE_INDEX,
    FULL_SURFACE_RECT,
    HOME_BADGE_RECT,
    MATCH_AWAY_SIDE_OFFSET,
    MATCH_BACKGROUND_CLUB_HELPER_VA,
    MATCH_BACKGROUND_CLUB_OVERRIDE_OFFSET,
    MATCH_HOME_SIDE_OFFSET,
    REAL_FIXTURE_AWAY_CLUB_OFFSET,
    REAL_FIXTURE_HOME_CLUB_OFFSET,
    SURFACED_CONTROLS,
    TEAM_BACKGROUND_GENERIC_FALLBACK,
    background_client_cache_address,
    background_source_candidates,
    background_variant_for_month,
    badge_source_path,
    generic_background_tier,
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

    def test_background_month_table_matches_literal_source_lookup(self):
        self.assertEqual(DATE_SPLIT_HELPER_VA, 0x64CCD0)
        self.assertEqual(BACKGROUND_MONTH_TABLE_VA, 0x83339C)
        self.assertEqual(
            BACKGROUND_VARIANT_BY_MONTH,
            (None, 2, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, 2),
        )
        self.assertEqual(
            tuple(background_variant_for_month(month) for month in range(1, 13)),
            (2, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, 2),
        )
        for bad in (0, 13, True, 1.0):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    background_variant_for_month(bad)

    def test_background_fallback_tier_preserves_raw_club_thresholds(self):
        self.assertEqual(DBRCLUB_BACKGROUND_TIER_SOURCE_OFFSET, 0x70)
        self.assertEqual(generic_background_tier(21), 0)
        self.assertEqual(generic_background_tier(20), 1)
        self.assertEqual(generic_background_tier(9), 1)
        self.assertEqual(generic_background_tier(8), 2)
        self.assertEqual(generic_background_tier(-1), 2)
        with self.assertRaises(ValueError):
            generic_background_tier("8")

    def test_background_candidates_preserve_exact_attempt_order(self):
        self.assertEqual(
            background_source_candidates("England", "arsenal", 1, 25),
            (
                r"FM2001_Art\Generic\Team_backgrounds\England\arsenal_background2.444",
                r"FM2001_Art\Generic\Team_backgrounds\England\arsenal_background.444",
                r"FM2001_Art\Generic\Team_backgrounds\generic0_background2.444",
            ),
        )
        self.assertEqual(
            background_source_candidates("England", "arsenal", 6, 8)[-1],
            r"FM2001_Art\Generic\Team_backgrounds\generic2_background0.444",
        )

    def test_fastview_uses_second_client_cache_and_shared_two_slot_pool(self):
        self.assertEqual(BACKGROUND_CLIENT_CACHE_BASE_VA, 0x87AC68)
        self.assertEqual(BACKGROUND_CLIENT_CACHE_COUNT, 2)
        self.assertEqual(BACKGROUND_CLIENT_CACHE_STRIDE, 0x0C)
        self.assertEqual(FASTVIEW_BACKGROUND_CLIENT_CACHE_INDEX, 1)
        self.assertEqual(background_client_cache_address(0), 0x87AC68)
        self.assertEqual(background_client_cache_address(1), 0x87AC74)
        self.assertEqual(BACKGROUND_RESOURCE_POOL_VA, 0x87AC30)
        self.assertEqual(BACKGROUND_RESOURCE_POOL_CAPACITY, 2)
        with self.assertRaises(ValueError):
            background_client_cache_address(2)

    def test_background_ownership_and_selector_are_closed_but_pixels_remain_open(self):
        contract = surfaced_picture_source_contract()
        self.assertTrue(contract["badge_variant_source_closed"])
        self.assertTrue(contract["badge_home_away_orientation_source_closed"])
        self.assertTrue(contract["full_surface_club_background_ownership_source_closed"])
        self.assertEqual(
            contract["full_surface_background_club_rule"],
            "match_plus_0x48_override_else_home_side",
        )
        self.assertEqual(MATCH_BACKGROUND_CLUB_HELPER_VA, 0x514220)
        self.assertEqual(MATCH_BACKGROUND_CLUB_OVERRIDE_OFFSET, 0x48)
        self.assertTrue(contract["full_surface_background_index_source_closed"])
        self.assertEqual(contract["background_client_cache_index"], 1)
        self.assertEqual(contract["background_resource_pool_capacity"], 2)
        self.assertTrue(contract["background_cache_reuses_matching_pool_entry"])
        self.assertTrue(contract["background_cache_reference_counted"])
        self.assertEqual(
            contract["background_club_attempt_order"],
            ("backgroundN", "background", "genericTier_backgroundN"),
        )
        self.assertFalse(contract["surfaced_picture_pixels_staged"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])
        self.assertTrue(
            TEAM_BACKGROUND_GENERIC_FALLBACK.endswith(
                r"Team_backgrounds\generic.444"
            )
        )


if __name__ == "__main__":
    unittest.main()
