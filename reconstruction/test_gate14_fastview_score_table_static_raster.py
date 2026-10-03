"""Tests for static source-backed FastView score/table raster planes."""
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_score_table_static_raster import (
    FastViewScoreTableStaticRasterError,
    build_fastview_score_table_static_rasters,
    rasterize_fastview_league_scores_static,
    rasterize_fastview_league_table_static,
)
from original_fastview_score_table_art import (
    FASTVIEW_SCORE_TABLE_ART_RESOURCES,
    build_fastview_score_table_art,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes((value, value + 1, value + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


def exact_art():
    return build_fastview_score_table_art(
        {
            resource.name: image(*resource.size, 10 + index * 10)
            for index, resource in enumerate(FASTVIEW_SCORE_TABLE_ART_RESOURCES)
        }
    )


def pixel(plane, x, y):
    offset = (y * 800 + x) * 4
    return tuple(plane.rgba[offset:offset + 4])


class FastViewScoreTableStaticRasterTests(unittest.TestCase):
    def test_single_column_scores_draws_grid1_and_exact_grid2_rows(self):
        plane = rasterize_fastview_league_scores_static(exact_art(), 2)
        self.assertEqual(plane.component, "league_scores_static")
        self.assertEqual(plane.size, (800, 600))
        self.assertEqual(plane.source_layer_count, 3)
        # resource order: current_fix_grid_1=10, grid_2=20
        self.assertEqual(pixel(plane, 246, 32), (10, 11, 12, 255))
        self.assertEqual(pixel(plane, 246, 55), (20, 21, 22, 255))
        self.assertEqual(pixel(plane, 246, 74), (20, 21, 22, 255))
        self.assertEqual(pixel(plane, 246, 93), (0, 0, 0, 0))
        self.assertFalse(plane.text_rasterized)
        self.assertFalse(plane.complete_component)

    def test_two_column_scores_and_typed_phase_icon_use_exact_positions(self):
        plane = rasterize_fastview_league_scores_static(
            exact_art(),
            13,
            phase_events_by_source_index=((0, "EventHalfTime"), (12, "EventFullTime")),
        )
        # two grid-1 strips + 13 grid-2 rows + 2 phase icons
        self.assertEqual(plane.source_layer_count, 17)
        self.assertEqual(pixel(plane, 38, 32), (10, 11, 12, 255))
        self.assertEqual(pixel(plane, 454, 32), (10, 11, 12, 255))
        self.assertEqual(pixel(plane, 38, 55), (20, 21, 22, 255))
        self.assertEqual(pixel(plane, 454, 55), (20, 21, 22, 255))
        # phase resource order: half=30, extra=40, penalties=50, full=60
        self.assertEqual(pixel(plane, 354, 55), (30, 31, 32, 255))
        self.assertEqual(pixel(plane, 770, 55), (60, 61, 62, 255))

    def test_league_table_draws_heading_and_source_visible_row_count(self):
        plane = rasterize_fastview_league_table_static(exact_art(), 20)
        self.assertEqual(plane.component, "league_table_static")
        # count 20 -> exact visible-row transform gives 10, plus heading.
        self.assertEqual(plane.source_layer_count, 11)
        # resource order current_table_grid_1=70, current_table_grid_2=80
        self.assertEqual(pixel(plane, 382, 32), (70, 71, 72, 255))
        self.assertEqual(pixel(plane, 382, 55), (80, 81, 82, 255))
        self.assertEqual(pixel(plane, 382, 55 + 9 * 19), (80, 81, 82, 255))
        self.assertEqual(pixel(plane, 382, 55 + 10 * 19), (0, 0, 0, 0))

    def test_build_set_remains_unflattened(self):
        rasters = build_fastview_score_table_static_rasters(
            exact_art(),
            league_scores_source_count=1,
            league_table_source_count=12,
        )
        self.assertFalse(rasters.cross_component_z_order_recovered)
        self.assertFalse(rasters.flattened_frame_available)
        self.assertEqual(rasters.league_scores.component, "league_scores_static")
        self.assertEqual(rasters.league_table.component, "league_table_static")

    def test_rejects_off_page_duplicate_or_unproved_phase_inputs(self):
        art = exact_art()
        for bad_count in (0, 25, True, 1.5):
            with self.subTest(bad_count=bad_count):
                with self.assertRaises(FastViewScoreTableStaticRasterError):
                    rasterize_fastview_league_scores_static(art, bad_count)

        with self.assertRaisesRegex(
            FastViewScoreTableStaticRasterError,
            "outside the visible score page",
        ):
            rasterize_fastview_league_scores_static(
                art, 2, phase_events_by_source_index=((2, "EventHalfTime"),)
            )

        with self.assertRaisesRegex(
            FastViewScoreTableStaticRasterError,
            "only one retained phase icon",
        ):
            rasterize_fastview_league_scores_static(
                art,
                2,
                phase_events_by_source_index=(
                    (0, "EventHalfTime"),
                    (0, "EventFullTime"),
                ),
            )

        with self.assertRaises(Exception):
            rasterize_fastview_league_scores_static(
                art, 1, phase_events_by_source_index=((0, "EventGlobalSecondHalf"),)
            )


if __name__ == "__main__":
    unittest.main()
