"""Tests for surfaced FastView background and badge raster planes."""
from datetime import date
from types import SimpleNamespace
import unittest

from gate14_fastview_surfaced_picture_selection import (
    build_fastview_surfaced_resource_selection,
)
from gate14_fastview_surfaced_picture_source import (
    AWAY_BADGE_RECT,
    HOME_BADGE_RECT,
)
from gate14_fastview_surfaced_resource_loader import (
    VerifiedFastViewSurfacedResource,
    VerifiedFastViewSurfacedResourceSet,
)
from gate14_fastview_surfaced_resource_raster import (
    BACKGROUND_COMPONENT,
    BADGES_COMPONENT,
    FastViewSurfacedRasterError,
    build_fastview_surfaced_rasters,
    surfaced_raster_contract,
)


def club(country_id, basename, fan_base_index):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
    )


def resource(role, path, geometry, pixel):
    rgba = bytearray(geometry[0] * geometry[1] * 4)
    rgba[0:4] = bytes(pixel)
    payload = bytes(rgba)
    import hashlib
    return VerifiedFastViewSurfacedResource(
        role=role,
        source_path=path,
        byte_size=17,
        sha256=hashlib.sha256(b"source-" + role.encode("ascii")).hexdigest(),
        geometry=geometry,
        rgba=payload,
        transparent_pixels=0,
    )


class FastViewSurfacedResourceRasterTests(unittest.TestCase):
    def resources(self):
        clubs = {
            10: club(26, "arsenal", 25),
            11: club(26, "chelsea", 14),
        }
        countries = {26: SimpleNamespace(graphics_directory="England")}
        selection = build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=clubs,
            countries=countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )
        return VerifiedFastViewSurfacedResourceSet(
            selection=selection,
            background=resource(
                "background", "background.444", (800, 600), (1, 2, 3, 255)
            ),
            home_badge=resource(
                "home_badge", "home.444", (135, 93), (4, 5, 6, 255)
            ),
            away_badge=resource(
                "away_badge", "away.444", (135, 93), (7, 8, 9, 255)
            ),
        )

    def test_keeps_background_and_badges_as_distinct_native_order_planes(self):
        rasters = build_fastview_surfaced_rasters(self.resources())
        self.assertEqual(rasters.background.component, BACKGROUND_COMPONENT)
        self.assertEqual(rasters.background.source_layer_count, 1)
        self.assertEqual(rasters.background.source_paths, ("background.444",))
        self.assertEqual(rasters.badges.component, BADGES_COMPONENT)
        self.assertEqual(rasters.badges.source_layer_count, 2)
        self.assertEqual(
            rasters.badges.source_paths, ("home.444", "away.444")
        )
        self.assertTrue(rasters.outer_draw_positions_preserved)
        self.assertFalse(rasters.cross_component_blend_recovered)
        self.assertFalse(rasters.complete_fastview_frame_recovered)

    def test_badges_are_placed_at_exact_source_rectangles(self):
        rasters = build_fastview_surfaced_rasters(self.resources())

        def pixel(rgba, x, y):
            offset = (y * 800 + x) * 4
            return tuple(rgba[offset:offset + 4])

        self.assertEqual(
            pixel(rasters.badges.rgba, HOME_BADGE_RECT[0], HOME_BADGE_RECT[1]),
            (4, 5, 6, 255),
        )
        self.assertEqual(
            pixel(rasters.badges.rgba, AWAY_BADGE_RECT[0], AWAY_BADGE_RECT[1]),
            (7, 8, 9, 255),
        )
        self.assertEqual(pixel(rasters.badges.rgba, 0, 0), (0, 0, 0, 0))
        self.assertEqual(
            pixel(rasters.background.rgba, 0, 0),
            (1, 2, 3, 255),
        )

    def test_wrong_badge_geometry_fails_before_component_promotion(self):
        resources = self.resources()
        bad_home = resource(
            "home_badge", "home.444", (134, 93), (4, 5, 6, 255)
        )
        bad_set = VerifiedFastViewSurfacedResourceSet(
            selection=resources.selection,
            background=resources.background,
            home_badge=bad_home,
            away_badge=resources.away_badge,
        )
        with self.assertRaisesRegex(
            FastViewSurfacedRasterError,
            "home_badge geometry",
        ):
            build_fastview_surfaced_rasters(bad_set)

    def test_contract_preserves_two_native_draw_positions_and_fail_closed_frame(self):
        contract = surfaced_raster_contract()
        self.assertEqual(contract["background_component"], BACKGROUND_COMPONENT)
        self.assertEqual(contract["badges_component"], BADGES_COMPONENT)
        self.assertTrue(contract["background_and_badges_kept_separate"])
        self.assertTrue(contract["source_bytes_loaded"])
        self.assertTrue(contract["ea444_decoded"])
        self.assertFalse(contract["cross_component_blend_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
