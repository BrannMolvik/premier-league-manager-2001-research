"""Tests for exact fail-closed FastView frame coverage accounting."""
from dataclasses import replace
from hashlib import sha256
import unittest

from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
)
from gate14_fastview_frame_coverage import (
    FastViewFrameCoverageError,
    audit_fastview_frame_coverage,
)
from gate14_fastview_resolved_composite import compose_fastview_resolved_only_pixels


WIDTH = 800
HEIGHT = 600
TOTAL = WIDTH * HEIGHT


def plane(component, pixels):
    rgba = bytearray(TOTAL * 4)
    for index, value in pixels.items():
        offset = index * 4
        rgba[offset:offset + 4] = bytes(value)
    payload = bytes(rgba)
    return FastViewComponentRasterPlane(
        component=component,
        size=(WIDTH, HEIGHT),
        rgba=payload,
        source_layer_count=1,
        rgba_sha256=sha256(payload).hexdigest(),
    )


def source_composite():
    return compose_fastview_resolved_only_pixels(
        FastViewComponentRasterSet(
            chrome=plane(
                "direct_chrome",
                {
                    0: (10, 20, 30, 255),
                    1: (11, 21, 31, 255),
                },
            ),
            possession_diagram=plane(
                "possession_diagram",
                {
                    1: (40, 50, 60, 255),
                    2: (41, 51, 61, 255),
                },
            ),
            possession_figures=plane(
                "possession_figures_text",
                {
                    3: (70, 80, 90, 128),
                },
            ),
        )
    )


class FastViewFrameCoverageTests(unittest.TestCase):
    def test_partitions_entire_surface_without_calling_unowned_pixels_missing(self):
        composite = source_composite()
        coverage = audit_fastview_frame_coverage(composite)

        self.assertEqual(coverage.total_pixel_count, TOTAL)
        self.assertEqual(coverage.resolved_pixel_count, 3)
        self.assertEqual(coverage.unresolved_overlap_pixel_count, 1)
        self.assertEqual(
            coverage.no_verified_visible_contributor_pixel_count,
            TOTAL - 4,
        )
        self.assertEqual(
            coverage.resolved_pixel_count
            + coverage.unresolved_overlap_pixel_count
            + coverage.no_verified_visible_contributor_pixel_count,
            TOTAL,
        )
        self.assertEqual(
            coverage.unresolved_overlap_groups,
            composite.unresolved_overlap_groups,
        )
        self.assertEqual(
            coverage.contributing_components,
            composite.contributing_components,
        )
        self.assertEqual(
            coverage.source_composite_rgba_sha256,
            composite.rgba_sha256,
        )
        self.assertEqual(
            coverage.source_overlap_mask_sha256,
            composite.unresolved_overlap_mask_sha256,
        )
        self.assertTrue(coverage.exhaustive_partition_verified)
        self.assertFalse(coverage.cross_component_z_order_recovered)
        self.assertFalse(coverage.background_binding_recovered)
        self.assertFalse(coverage.complete_fastview_frame)

    def test_basis_points_are_deterministic_integer_floors(self):
        coverage = audit_fastview_frame_coverage(source_composite())
        self.assertEqual(
            coverage.resolved_basis_points,
            (3 * 10000) // TOTAL,
        )
        self.assertEqual(
            coverage.unresolved_overlap_basis_points,
            (1 * 10000) // TOTAL,
        )
        self.assertEqual(
            coverage.no_verified_visible_contributor_basis_points,
            ((TOTAL - 4) * 10000) // TOTAL,
        )

    def test_rejects_partition_drift_or_false_fidelity_promotion(self):
        coverage = audit_fastview_frame_coverage(source_composite())

        with self.assertRaisesRegex(
            FastViewFrameCoverageError,
            "partition",
        ):
            replace(
                coverage,
                no_verified_visible_contributor_pixel_count=(
                    coverage.no_verified_visible_contributor_pixel_count - 1
                ),
            )

        for field in (
            "cross_component_z_order_recovered",
            "background_binding_recovered",
            "complete_fastview_frame",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    FastViewFrameCoverageError,
                    "cannot promote",
                ):
                    replace(coverage, **{field: True})

    def test_requires_exact_resolved_composite(self):
        with self.assertRaisesRegex(
            FastViewFrameCoverageError,
            "exact FastViewResolvedOnlyComposite",
        ):
            audit_fastview_frame_coverage(object())


if __name__ == "__main__":
    unittest.main()
