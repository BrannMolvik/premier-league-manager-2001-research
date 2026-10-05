"""Integration tests for surfaced FastView component planes."""
from hashlib import sha256
from unittest.mock import patch
import unittest

from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
    build_fastview_component_rasters,
)
from gate14_fastview_draw_order import source_closed_pairwise_order
from gate14_fastview_resolved_composite import (
    FastViewUnresolvedOverlapGroup,
    compose_fastview_resolved_only_pixels,
)
from gate14_fastview_surfaced_resource_raster import (
    BACKGROUND_COMPONENT,
    BADGES_COMPONENT,
    FastViewSurfacedRasterPlane,
    FastViewSurfacedRasterSet,
)


PIXELS = 800 * 600


def plane(component, pixel_index, rgba_value, *, layers=1):
    rgba = bytearray(PIXELS * 4)
    off = pixel_index * 4
    rgba[off:off + 4] = bytes(rgba_value)
    raw = bytes(rgba)
    return FastViewComponentRasterPlane(
        component=component,
        size=(800, 600),
        rgba=raw,
        source_layer_count=layers,
        rgba_sha256=sha256(raw).hexdigest(),
    )


def surfaced_plane(component, pixel_index, rgba_value, *, layers, paths):
    rgba = bytearray(PIXELS * 4)
    off = pixel_index * 4
    rgba[off:off + 4] = bytes(rgba_value)
    raw = bytes(rgba)
    return FastViewSurfacedRasterPlane(
        component=component,
        size=(800, 600),
        rgba=raw,
        source_layer_count=layers,
        rgba_sha256=sha256(raw).hexdigest(),
        source_paths=paths,
    )


def surfaced():
    return FastViewSurfacedRasterSet(
        background=surfaced_plane(
            BACKGROUND_COMPONENT,
            5,
            (10, 20, 30, 255),
            layers=1,
            paths=("background.444",),
        ),
        badges=surfaced_plane(
            BADGES_COMPONENT,
            7,
            (40, 50, 60, 255),
            layers=2,
            paths=("home.444", "away.444"),
        ),
    )


class FastViewSurfacedComponentIntegrationTests(unittest.TestCase):
    def test_builder_lifts_both_surfaced_planes_without_flattening(self):
        chrome = plane("direct_chrome", 6, (1, 1, 1, 255))
        possession = plane("possession_diagram", 8, (2, 2, 2, 255))
        figures = plane("possession_figures_text", 9, (3, 3, 3, 255))
        source = surfaced()

        with (
            patch(
                "gate14_fastview_component_rasters.rasterize_fastview_chrome_plane",
                return_value=chrome,
            ),
            patch(
                "gate14_fastview_component_rasters.rasterize_fastview_possession_plane",
                return_value=possession,
            ),
            patch(
                "gate14_fastview_component_rasters.rasterize_fastview_possession_figures_plane",
                return_value=figures,
            ),
        ):
            rasters = build_fastview_component_rasters(
                object(),
                object(),
                object(),
                surfaced=source,
            )

        self.assertEqual(rasters.match_background.component, BACKGROUND_COMPONENT)
        self.assertEqual(rasters.club_badges.component, BADGES_COMPONENT)
        self.assertEqual(
            rasters.match_background.rgba_sha256,
            source.background.rgba_sha256,
        )
        self.assertEqual(rasters.club_badges.rgba_sha256, source.badges.rgba_sha256)
        self.assertFalse(rasters.cross_component_z_order_recovered)
        self.assertFalse(rasters.flattened_frame_available)

    def test_resolved_composite_keeps_source_plane_order_and_masks_overlap(self):
        rasters = FastViewComponentRasterSet(
            match_background=plane(
                BACKGROUND_COMPONENT,
                10,
                (9, 9, 9, 255),
            ),
            chrome=plane(
                "direct_chrome",
                10,
                (1, 1, 1, 255),
            ),
            clock=plane(
                "clock_text",
                11,
                (2, 2, 2, 255),
            ),
            club_badges=plane(
                BADGES_COMPONENT,
                12,
                (3, 3, 3, 255),
                layers=2,
            ),
            possession_diagram=plane(
                "possession_diagram",
                13,
                (4, 4, 4, 255),
            ),
            possession_figures=plane(
                "possession_figures_text",
                14,
                (5, 5, 5, 255),
            ),
        )
        composite = compose_fastview_resolved_only_pixels(rasters)

        self.assertEqual(
            composite.contributing_components,
            (
                BACKGROUND_COMPONENT,
                "direct_chrome",
                "clock_text",
                BADGES_COMPONENT,
                "possession_diagram",
                "possession_figures_text",
            ),
        )
        self.assertEqual(composite.unresolved_overlap_mask[10], 1)
        self.assertEqual(
            composite.unresolved_overlap_groups,
            (
                FastViewUnresolvedOverlapGroup(
                    components=(BACKGROUND_COMPONENT, "direct_chrome"),
                    pixel_count=1,
                    bounding_rect=(10, 0, 11, 1),
                ),
            ),
        )
        self.assertFalse(composite.cross_component_z_order_recovered)
        self.assertFalse(composite.flattened_frame_available)

    def test_pairwise_order_is_source_closed_for_both_surfaced_positions(self):
        first = source_closed_pairwise_order(
            BACKGROUND_COMPONENT,
            "direct_chrome",
        )
        self.assertEqual(first.earlier_component, BACKGROUND_COMPONENT)
        self.assertEqual(first.later_component, "direct_chrome")
        self.assertTrue(first.same_parent_draw_array)

        second = source_closed_pairwise_order(
            "clock_text",
            BADGES_COMPONENT,
        )
        self.assertEqual(second.earlier_component, "clock_text")
        self.assertEqual(second.later_component, BADGES_COMPONENT)

        third = source_closed_pairwise_order(
            BADGES_COMPONENT,
            "possession_diagram",
        )
        self.assertEqual(third.earlier_component, BADGES_COMPONENT)
        self.assertEqual(third.later_component, "possession_diagram")

        # Source order is not permission to infer native cross-component blend.
        self.assertFalse(first.pixel_blend_rule_recovered)
        self.assertFalse(first.global_z_order_recovered)


if __name__ == "__main__":
    unittest.main()
