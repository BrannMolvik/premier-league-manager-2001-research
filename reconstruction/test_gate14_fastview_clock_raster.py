"""Tests for fail-closed white-endpoint FastView clock raster."""
from pathlib import Path
import unittest

from gate14_fastview_clock import (
    CLOCK_ALERT,
    CLOCK_WHITE,
    SOURCE_CLOCK_TEXT_RECT,
    apply_clock_extra_time,
    apply_clock_full_time,
    apply_clock_global_tick,
    apply_clock_half_time,
    apply_clock_second_half,
    initial_fastview_clock_state,
)
from gate14_fastview_clock_raster import (
    CLOCK_TEXT_COMPONENT,
    FastViewClockRasterError,
    build_white_endpoint_clock_raster,
    clock_white_raster_contract,
    load_verified_clock_font,
)
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE


class FastViewClockRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.font = load_verified_clock_font(cls.repo_root)

    def _alpha_bounds(self, rgba: bytes):
        width, height = FASTVIEW_SURFACE_SIZE
        points = []
        for index in range(width * height):
            if rgba[index * 4 + 3]:
                points.append((index % width, index // width))
        if not points:
            return None
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        return min(xs), min(ys), max(xs) + 1, max(ys) + 1

    def test_initial_empty_clock_is_transparent_zero_layer(self):
        raster = build_white_endpoint_clock_raster(
            self.font,
            initial_fastview_clock_state(),
        )
        self.assertEqual(raster.component, CLOCK_TEXT_COMPONENT)
        self.assertEqual(raster.size, (800, 600))
        self.assertEqual(raster.source_layer_count, 0)
        self.assertEqual(raster.text, "")
        self.assertIsNone(raster.line_origin)
        self.assertIsNone(raster.native_color_16)
        self.assertIsNone(self._alpha_bounds(raster.rgba))
        self.assertTrue(raster.white_endpoint_only)
        self.assertTrue(raster.alert_color_withheld)

    def test_first_half_numeric_white_raster_uses_exact_left_top_origin(self):
        state = apply_clock_global_tick(initial_fastview_clock_state(), 45)
        self.assertIs(state.color, CLOCK_WHITE)
        raster = build_white_endpoint_clock_raster(self.font, state)

        self.assertEqual(raster.source_layer_count, 1)
        self.assertEqual(raster.text, "45 mins")
        self.assertEqual(raster.line_origin, SOURCE_CLOCK_TEXT_RECT[:2])
        self.assertEqual(raster.native_color_16, 0xFFFF)
        bounds = self._alpha_bounds(raster.rgba)
        self.assertIsNotNone(bounds)
        left, top, right, bottom = bounds
        clip_left, clip_top, clip_right, clip_bottom = SOURCE_CLOCK_TEXT_RECT
        self.assertGreaterEqual(left, clip_left)
        self.assertGreaterEqual(top, clip_top)
        self.assertLessEqual(right, clip_right)
        self.assertLessEqual(bottom, clip_bottom)

    def test_half_time_second_half_and_full_time_white_states_rasterize(self):
        state = apply_clock_global_tick(initial_fastview_clock_state(), 46)
        self.assertIs(state.color, CLOCK_ALERT)

        half = apply_clock_half_time(state)
        self.assertEqual(half.text, "Half time")
        self.assertIs(half.color, CLOCK_WHITE)
        half_raster = build_white_endpoint_clock_raster(self.font, half)
        self.assertEqual(half_raster.text, "Half time")
        self.assertEqual(half_raster.source_layer_count, 1)

        second = apply_clock_second_half(half)
        self.assertEqual(second.text, "46 mins")
        self.assertIs(second.color, CLOCK_WHITE)
        second_raster = build_white_endpoint_clock_raster(self.font, second)
        self.assertEqual(second_raster.text, "46 mins")

        full = apply_clock_full_time(
            apply_clock_global_tick(second, 91)
        )
        self.assertEqual(full.text, "Full time")
        self.assertIs(full.color, CLOCK_WHITE)
        full_raster = build_white_endpoint_clock_raster(self.font, full)
        self.assertEqual(full_raster.text, "Full time")

    def test_alert_numeric_extra_time_and_penalties_fail_closed(self):
        alert_tick = apply_clock_global_tick(initial_fastview_clock_state(), 46)
        extra = apply_clock_extra_time(initial_fastview_clock_state())
        from gate14_fastview_clock import apply_clock_penalties
        penalties = apply_clock_penalties(initial_fastview_clock_state())

        for state in (alert_tick, extra, penalties):
            with self.subTest(text=state.text):
                self.assertIs(state.color, CLOCK_ALERT)
                with self.assertRaisesRegex(
                    FastViewClockRasterError,
                    "modern RGBA remains unresolved",
                ):
                    build_white_endpoint_clock_raster(self.font, state)

    def test_clock_text_pixels_are_exact_white_endpoint_with_source_alpha(self):
        state = apply_clock_global_tick(initial_fastview_clock_state(), 1)
        raster = build_white_endpoint_clock_raster(self.font, state)
        nonzero = [
            raster.rgba[index:index + 4]
            for index in range(0, len(raster.rgba), 4)
            if raster.rgba[index + 3]
        ]
        self.assertTrue(nonzero)
        self.assertTrue(
            all(pixel[0:3] == b"\xff\xff\xff" for pixel in nonzero)
        )
        self.assertTrue(any(pixel[3] < 255 for pixel in nonzero))

    def test_wrong_font_or_state_type_fails_closed(self):
        with self.assertRaisesRegex(FastViewClockRasterError, "exact EAFont"):
            build_white_endpoint_clock_raster(
                object(),
                initial_fastview_clock_state(),
            )
        with self.assertRaisesRegex(
            FastViewClockRasterError,
            "exact FastViewClockState",
        ):
            build_white_endpoint_clock_raster(self.font, object())

    def test_contract_keeps_alert_integration_and_global_frame_false(self):
        contract = clock_white_raster_contract()
        self.assertEqual(contract["component"], CLOCK_TEXT_COMPONENT)
        self.assertEqual(contract["source_rect"], SOURCE_CLOCK_TEXT_RECT)
        self.assertEqual(contract["line_origin"], SOURCE_CLOCK_TEXT_RECT[:2])
        self.assertTrue(contract["white_endpoint_raster_recovered"])
        self.assertTrue(contract["alert_color_withheld"])
        self.assertFalse(contract["alert_modern_rgba_recovered"])
        self.assertFalse(contract["integrated_component_plane"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
