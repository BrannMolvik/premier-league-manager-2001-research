"""Tests for the fail-closed resolved-only FastView composite."""
from dataclasses import replace
from hashlib import sha256
import unittest

from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
)
from gate14_fastview_resolved_composite import (
    FastViewResolvedCompositeError,
    compose_fastview_resolved_only_pixels,
)


SURFACE_PIXELS = 800 * 600


def plane(component, pixels, *, source_layers=1):
    rgba = bytearray(SURFACE_PIXELS * 4)
    for pixel_index, value in pixels.items():
        if not 0 <= pixel_index < SURFACE_PIXELS:
            raise AssertionError("test pixel outside surface")
        if len(value) != 4:
            raise AssertionError("test RGBA must have four channels")
        offset = pixel_index * 4
        rgba[offset:offset + 4] = bytes(value)
    raw = bytes(rgba)
    return FastViewComponentRasterPlane(
        component=component,
        size=(800, 600),
        rgba=raw,
        source_layer_count=source_layers,
        rgba_sha256=sha256(raw).hexdigest(),
    )


def pixel(composite, pixel_index):
    offset = pixel_index * 4
    return tuple(composite.rgba[offset:offset + 4])


def six_plane_set():
    return FastViewComponentRasterSet(
        chrome=plane(
            "direct_chrome",
            {
                0: (255, 0, 0, 255),
                10: (10, 10, 10, 255),
                # RGB data with alpha zero must not claim ownership.
                20: (99, 88, 77, 0),
            },
        ),
        possession_diagram=plane(
            "possession_diagram",
            {
                1: (0, 255, 0, 255),
                10: (20, 20, 20, 255),
            },
        ),
        possession_figures=plane(
            "possession_figures_text",
            {2: (0, 0, 255, 255)},
        ),
        team_table=plane(
            "team_table_static",
            {3: (40, 50, 60, 128)},
        ),
        league_scores=plane(
            "league_scores_static",
            {4: (70, 80, 90, 255)},
        ),
        league_table=plane(
            "league_table_static",
            {5: (100, 110, 120, 255)},
        ),
    )


class FastViewResolvedCompositeTests(unittest.TestCase):
    def test_copies_only_single_owner_pixels_and_masks_overlap(self):
        rasters = six_plane_set()
        composite = compose_fastview_resolved_only_pixels(rasters)

        self.assertEqual(composite.size, (800, 600))
        self.assertEqual(composite.resolved_pixel_count, 6)
        self.assertEqual(composite.unresolved_overlap_pixel_count, 1)
        self.assertEqual(pixel(composite, 0), (255, 0, 0, 255))
        self.assertEqual(pixel(composite, 1), (0, 255, 0, 255))
        self.assertEqual(pixel(composite, 2), (0, 0, 255, 255))
        # A singly owned partial-alpha pixel is copied exactly, not blended.
        self.assertEqual(pixel(composite, 3), (40, 50, 60, 128))
        self.assertEqual(pixel(composite, 4), (70, 80, 90, 255))
        self.assertEqual(pixel(composite, 5), (100, 110, 120, 255))

        # Cross-component overlap is never resolved by branch/order choice.
        self.assertEqual(pixel(composite, 10), (0, 0, 0, 0))
        self.assertEqual(composite.unresolved_overlap_mask[10], 1)

        # Alpha-zero RGB does not count as a component-owned visible pixel.
        self.assertEqual(pixel(composite, 20), (0, 0, 0, 0))
        self.assertEqual(composite.unresolved_overlap_mask[20], 0)

        self.assertEqual(
            composite.contributing_components,
            (
                "direct_chrome",
                "possession_diagram",
                "possession_figures_text",
                "team_table_static",
                "league_scores_static",
                "league_table_static",
            ),
        )
        self.assertEqual(
            composite.source_plane_sha256,
            tuple(
                (item.component, item.rgba_sha256)
                for item in (
                    rasters.chrome,
                    rasters.possession_diagram,
                    rasters.possession_figures,
                    rasters.team_table,
                    rasters.league_scores,
                    rasters.league_table,
                )
            ),
        )
        self.assertFalse(composite.cross_component_z_order_recovered)
        self.assertFalse(composite.flattened_frame_available)
        self.assertFalse(composite.complete_fastview_frame)

    def test_required_three_plane_set_is_supported_without_optional_art(self):
        rasters = FastViewComponentRasterSet(
            chrome=plane("direct_chrome", {100: (1, 2, 3, 255)}),
            possession_diagram=plane(
                "possession_diagram",
                {101: (4, 5, 6, 255)},
            ),
            possession_figures=plane(
                "possession_figures_text",
                {102: (7, 8, 9, 255)},
            ),
        )
        composite = compose_fastview_resolved_only_pixels(rasters)
        self.assertEqual(composite.resolved_pixel_count, 3)
        self.assertEqual(composite.unresolved_overlap_pixel_count, 0)
        self.assertEqual(
            composite.contributing_components,
            (
                "direct_chrome",
                "possession_diagram",
                "possession_figures_text",
            ),
        )

    def test_three_or_more_overlapping_components_still_produce_one_unresolved_pixel(self):
        rasters = FastViewComponentRasterSet(
            chrome=plane("direct_chrome", {7: (1, 1, 1, 255)}),
            possession_diagram=plane(
                "possession_diagram",
                {7: (2, 2, 2, 255)},
            ),
            possession_figures=plane(
                "possession_figures_text",
                {7: (3, 3, 3, 255)},
            ),
        )
        composite = compose_fastview_resolved_only_pixels(rasters)
        self.assertEqual(composite.resolved_pixel_count, 0)
        self.assertEqual(composite.unresolved_overlap_pixel_count, 1)
        self.assertEqual(composite.unresolved_overlap_mask[7], 1)
        self.assertEqual(pixel(composite, 7), (0, 0, 0, 0))

    def test_rejects_wrong_input_and_mutated_output_integrity(self):
        with self.assertRaisesRegex(
            FastViewResolvedCompositeError,
            "exact FastViewComponentRasterSet",
        ):
            compose_fastview_resolved_only_pixels(object())

        composite = compose_fastview_resolved_only_pixels(six_plane_set())
        with self.assertRaisesRegex(
            FastViewResolvedCompositeError,
            "RGBA SHA-256",
        ):
            replace(composite, rgba_sha256="0" * 64)
        with self.assertRaisesRegex(
            FastViewResolvedCompositeError,
            "overlap-mask SHA-256",
        ):
            replace(
                composite,
                unresolved_overlap_mask_sha256="0" * 64,
            )
        with self.assertRaisesRegex(
            FastViewResolvedCompositeError,
            "cannot promote",
        ):
            replace(composite, flattened_frame_available=True)


if __name__ == "__main__":
    unittest.main()
