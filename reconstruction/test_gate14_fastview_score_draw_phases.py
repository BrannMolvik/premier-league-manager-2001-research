"""Tests for source-order LeagueScores raster phases."""
from dataclasses import replace
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_score_draw_phases import (
    FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA,
    LEAGUE_SCORES_CURRENT_FIX_GRID_1_CALLSITE_VA,
    LEAGUE_TABLE_COMPOSITE_CALLSITE_VA,
    PHASE_EARLY_SCORE_ROWS,
    PHASE_LATE_GRID,
    PHASE_RUNTIME_ICONS,
    SOURCE_CLOSED_STATIC_PHASE_ORDER,
    FastViewScoreDrawPhaseError,
    build_fastview_league_scores_draw_phases,
    score_draw_phase_contract,
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


class FastViewScoreDrawPhaseTests(unittest.TestCase):
    def test_static_source_order_is_early_rows_table_late_grid(self):
        self.assertEqual(FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA, 0x5233C2)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_CALLSITE_VA, 0x523472)
        self.assertEqual(LEAGUE_SCORES_CURRENT_FIX_GRID_1_CALLSITE_VA, 0x5239F3)
        self.assertLess(
            FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA,
            LEAGUE_TABLE_COMPOSITE_CALLSITE_VA,
        )
        self.assertLess(
            LEAGUE_TABLE_COMPOSITE_CALLSITE_VA,
            LEAGUE_SCORES_CURRENT_FIX_GRID_1_CALLSITE_VA,
        )
        self.assertEqual(
            SOURCE_CLOSED_STATIC_PHASE_ORDER,
            (
                PHASE_EARLY_SCORE_ROWS,
                "league_table_static",
                PHASE_LATE_GRID,
            ),
        )

    def test_raster_split_places_early_rows_and_late_grid_separately(self):
        phases = build_fastview_league_scores_draw_phases(exact_art(), 2)
        self.assertEqual(phases.early_score_rows.source_layer_count, 2)
        self.assertEqual(phases.late_grid.source_layer_count, 1)
        self.assertEqual(phases.runtime_phase_icons.source_layer_count, 0)

        self.assertEqual(pixel(phases.early_score_rows, 38, 55), (20, 21, 22, 255))
        self.assertEqual(pixel(phases.early_score_rows, 38, 74), (20, 21, 22, 255))
        self.assertEqual(pixel(phases.early_score_rows, 38, 32), (0, 0, 0, 0))

        self.assertEqual(pixel(phases.late_grid, 38, 32), (10, 11, 12, 255))
        self.assertEqual(pixel(phases.late_grid, 38, 55), (0, 0, 0, 0))

    def test_runtime_phase_icons_are_retained_as_tail_plane_only(self):
        phases = build_fastview_league_scores_draw_phases(
            exact_art(),
            12,
            phase_events_by_source_index=((0, "EventHalfTime"), (11, "EventFullTime")),
        )
        self.assertEqual(phases.runtime_phase_icons.source_layer_count, 2)
        self.assertTrue(phases.runtime_phase_icons.runtime_tail)
        self.assertEqual(
            pixel(phases.runtime_phase_icons, 354, 55),
            (30, 31, 32, 255),
        )
        self.assertEqual(
            pixel(phases.runtime_phase_icons, 354, 264),
            (60, 61, 62, 255),
        )
        self.assertFalse(phases.paired_phase_text_rasterized)
        self.assertFalse(phases.aggregate_score_plane_has_single_z_position)

    def test_duplicate_off_page_or_unproved_phase_input_fails_closed(self):
        art = exact_art()
        for bad_count in (0, 13, True, 1.5):
            with self.subTest(count=bad_count):
                with self.assertRaises(FastViewScoreDrawPhaseError):
                    build_fastview_league_scores_draw_phases(art, bad_count)
        with self.assertRaisesRegex(FastViewScoreDrawPhaseError, "outside"):
            build_fastview_league_scores_draw_phases(
                art,
                2,
                phase_events_by_source_index=((2, "EventHalfTime"),),
            )
        with self.assertRaisesRegex(FastViewScoreDrawPhaseError, "only one"):
            build_fastview_league_scores_draw_phases(
                art,
                2,
                phase_events_by_source_index=(
                    (0, "EventHalfTime"),
                    (0, "EventFullTime"),
                ),
            )

    def test_contract_keeps_global_and_complete_claims_false(self):
        contract = score_draw_phase_contract()
        self.assertFalse(contract["paired_phase_text_rasterized"])
        self.assertFalse(contract["aggregate_score_plane_has_single_z_position"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])

        phases = build_fastview_league_scores_draw_phases(exact_art(), 1)
        with self.assertRaisesRegex(FastViewScoreDrawPhaseError, "cannot promote"):
            replace(phases, global_fastview_z_order_recovered=True)


if __name__ == "__main__":
    unittest.main()
