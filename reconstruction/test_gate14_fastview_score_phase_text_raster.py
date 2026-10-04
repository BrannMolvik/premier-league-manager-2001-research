"""Tests for the source-backed ScoreComposite phase-text raster."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import unittest

from gate14_fastview_phase_text import score_phase_text
from gate14_fastview_score_phase_text_raster import (
    PHASE_RUNTIME_TEXT_COMPONENT,
    FastViewScorePhaseTextRasterError,
    build_fastview_score_phase_text_raster,
    load_verified_phase_text_font,
    phase_text_line_origin,
    score_phase_text_raster_contract,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def alpha_bounds(raster):
    width, height = raster.size
    xs = []
    ys = []
    for index in range(width * height):
        if raster.rgba[index * 4 + 3]:
            xs.append(index % width)
            ys.append(index // width)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


class FastViewScorePhaseTextRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.font = load_verified_phase_text_font(REPO_ROOT)

    def test_verified_source_font_and_exact_label_metrics(self):
        self.assertEqual(self.font.native_line_height(), 20)
        expected = {
            "EventHalfTime": ("HT", 16, 17),
            "EventFullTime": ("FT", 14, 17),
            "EventExtraTime": ("ET", 14, 17),
            "EventPenalties": ("PEN", 23, 17),
        }
        for event_name, (text, width, height) in expected.items():
            with self.subTest(event_name=event_name):
                source = score_phase_text(event_name)
                mask = self.font.render_text_alpha(source.text)
                self.assertEqual(source.text, text)
                self.assertEqual((mask.width, mask.height), (width, height))

    def test_centered_origin_matches_native_signed_half_arithmetic(self):
        origin = (38, 55)
        expected = {
            "EventHalfTime": (355, 53),
            "EventFullTime": (356, 53),
            "EventExtraTime": (356, 53),
            "EventPenalties": (351, 53),
        }
        control = (349, 55, 377, 71)
        for event_name, expected_origin in expected.items():
            with self.subTest(event_name=event_name):
                self.assertEqual(
                    phase_text_line_origin(
                        self.font,
                        score_phase_text(event_name),
                        control,
                    ),
                    expected_origin,
                )

    def test_single_half_time_label_is_clipped_inside_exact_row_control(self):
        raster = build_fastview_score_phase_text_raster(
            self.font,
            1,
            phase_events_by_source_index=((0, "EventHalfTime"),),
        )
        self.assertEqual(raster.component, PHASE_RUNTIME_TEXT_COMPONENT)
        self.assertEqual(raster.source_layer_count, 1)
        placement = raster.placements[0]
        self.assertEqual(placement.control_rect, (349, 55, 377, 71))
        self.assertEqual(placement.line_origin, (355, 53))
        self.assertEqual(placement.glyph_size, (16, 17))
        bounds = alpha_bounds(raster)
        self.assertIsNotNone(bounds)
        self.assertGreaterEqual(bounds[0], placement.control_rect[0])
        self.assertGreaterEqual(bounds[1], placement.control_rect[1])
        self.assertLessEqual(bounds[2], placement.control_rect[2])
        self.assertLessEqual(bounds[3], placement.control_rect[3])
        self.assertEqual(bounds[1], 56)
        self.assertEqual(bounds[3], 70)
        self.assertFalse(raster.aggregate_icon_text_order_recovered)
        self.assertFalse(raster.flattened_with_runtime_icons)
        self.assertFalse(raster.global_fastview_z_order_recovered)

    def test_multiple_rows_preserve_input_event_row_identity_without_flattening(self):
        raster = build_fastview_score_phase_text_raster(
            self.font,
            4,
            phase_events_by_source_index=(
                (0, "EventHalfTime"),
                (1, "EventFullTime"),
                (2, "EventExtraTime"),
                (3, "EventPenalties"),
            ),
        )
        self.assertEqual(raster.source_layer_count, 4)
        self.assertEqual(
            tuple(
                (
                    item.source_index,
                    item.source.event_name,
                    item.source.text,
                    item.control_rect,
                )
                for item in raster.placements
            ),
            (
                (0, "EventHalfTime", "HT", (349, 55, 377, 71)),
                (1, "EventFullTime", "FT", (349, 74, 377, 90)),
                (2, "EventExtraTime", "ET", (349, 93, 377, 109)),
                (3, "EventPenalties", "PEN", (349, 112, 377, 128)),
            ),
        )
        self.assertEqual(
            sha256(raster.rgba).hexdigest(),
            raster.rgba_sha256,
        )

    def test_zero_runtime_labels_is_valid_transparent_plane(self):
        raster = build_fastview_score_phase_text_raster(
            self.font,
            12,
            phase_events_by_source_index=(),
        )
        self.assertEqual(raster.source_layer_count, 0)
        self.assertEqual(raster.placements, ())
        self.assertEqual(set(raster.rgba), {0})

    def test_duplicate_row_unknown_event_and_out_of_page_fail_closed(self):
        with self.assertRaisesRegex(
            FastViewScorePhaseTextRasterError,
            "only one retained phase label",
        ):
            build_fastview_score_phase_text_raster(
                self.font,
                2,
                phase_events_by_source_index=(
                    (0, "EventHalfTime"),
                    (0, "EventFullTime"),
                ),
            )
        with self.assertRaisesRegex(Exception, "no source-closed"):
            build_fastview_score_phase_text_raster(
                self.font,
                1,
                phase_events_by_source_index=((0, "EventGlobalSecondHalf"),),
            )
        with self.assertRaisesRegex(
            FastViewScorePhaseTextRasterError,
            "outside visible",
        ):
            build_fastview_score_phase_text_raster(
                self.font,
                1,
                phase_events_by_source_index=((1, "EventHalfTime"),),
            )

    def test_raster_record_rejects_false_fidelity_promotion(self):
        raster = build_fastview_score_phase_text_raster(
            self.font,
            1,
            phase_events_by_source_index=((0, "EventHalfTime"),),
        )
        for field in (
            "aggregate_icon_text_order_recovered",
            "flattened_with_runtime_icons",
            "global_fastview_z_order_recovered",
            "complete_fastview_frame_recovered",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    FastViewScorePhaseTextRasterError,
                    "cannot promote",
                ):
                    replace(raster, **{field: True})

    def test_contract_keeps_icon_text_and_frame_boundaries_false(self):
        contract = score_phase_text_raster_contract()
        self.assertEqual(contract["component"], PHASE_RUNTIME_TEXT_COMPONENT)
        self.assertEqual(contract["source_font_native_line_height"], 20)
        self.assertEqual(contract["native_color_16"], 0xFFFF)
        self.assertEqual(contract["source_control_size"], (28, 16))
        self.assertEqual(contract["source_row_step"], 19)
        self.assertTrue(contract["control_clipping_applied"])
        self.assertTrue(contract["exact_phase_text_pixels_recovered"])
        self.assertFalse(contract["aggregate_icon_text_order_recovered"])
        self.assertFalse(contract["flattened_with_runtime_icons"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])


if __name__ == "__main__":
    unittest.main()
