from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import unittest

from ea_language_strings import parse_language_pair
from gate14_fastview_clock import (
    CLOCK_ALERT,
    CLOCK_WHITE,
    SOURCE_CLOCK_ALERT_RGB8,
    SOURCE_CLOCK_CALLBACK_EXTRA_TIME,
    SOURCE_CLOCK_CALLBACK_FULL_TIME,
    SOURCE_CLOCK_CALLBACK_GLOBAL_TICK,
    SOURCE_CLOCK_CALLBACK_HALF_TIME,
    SOURCE_CLOCK_CALLBACK_PENALTIES,
    SOURCE_CLOCK_CALLBACK_SECOND_HALF,
    SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE,
    SOURCE_CLOCK_FORMAT,
    SOURCE_CLOCK_LOCALIZED_TEXT,
    SOURCE_CLOCK_NATIVE_WHITE_16,
    SOURCE_CLOCK_PENALTIES_LATCH_OFFSET,
    SOURCE_CLOCK_POST_90_LATCH_OFFSET,
    SOURCE_CLOCK_RECEIVER_OFFSETS,
    SOURCE_CLOCK_RECEIVER_VTABLES,
    SOURCE_CLOCK_SECOND_HALF_LATCH_OFFSET,
    SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE,
    SOURCE_CLOCK_TEXT_RAW_FLAGS,
    SOURCE_CLOCK_TEXT_RECT,
    SOURCE_CLOCK_TEXT_RENDER_FLAGS,
    SOURCE_CLOCK_TEXT_STYLE_INDEX,
    SOURCE_CLOCK_TEXTCONTROL_OFFSET,
    SOURCE_POSSESSION_ARRAY_LOOKUP_VA,
    FastViewClockError,
    apply_clock_extra_time,
    apply_clock_full_time,
    apply_clock_global_tick,
    apply_clock_half_time,
    apply_clock_penalties,
    apply_clock_second_half,
    fastview_clock_contract,
    fastview_clock_numeric_value,
    initial_fastview_clock_state,
    possession_array_index_for_global_tick,
)


class FastViewClockTests(unittest.TestCase):
    def test_clock_uses_same_global_tick_numeric_value(self):
        self.assertEqual(SOURCE_CLOCK_FORMAT, "%u %s")
        self.assertEqual(SOURCE_CLOCK_TEXT_RECT, (439, 44, 621, 64))
        self.assertEqual(SOURCE_CLOCK_TEXTCONTROL_OFFSET, 0x18)
        self.assertEqual(SOURCE_CLOCK_TEXT_STYLE_INDEX, 1)
        self.assertEqual(SOURCE_CLOCK_TEXT_RAW_FLAGS, 0x02)
        self.assertEqual(SOURCE_CLOCK_TEXT_RENDER_FLAGS, 0x0A)
        self.assertEqual(SOURCE_CLOCK_NATIVE_WHITE_16, 0xFFFF)
        self.assertEqual(SOURCE_CLOCK_ALERT_RGB8, (255, 45, 45))
        self.assertEqual(SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE, 46)
        self.assertEqual(SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE, 91)
        for value in (0, 1, 5, 45, 46, 90, 91, 120):
            with self.subTest(value=value):
                self.assertEqual(fastview_clock_numeric_value(value), value)

    def test_rtti_receiver_offsets_vtables_and_callbacks_are_exact(self):
        self.assertEqual(
            SOURCE_CLOCK_RECEIVER_OFFSETS,
            {
                "EventGlobalTick": 0x00,
                "EventGlobalHalfTime": 0x04,
                "EventGlobalSecondHalf": 0x08,
                "EventGlobalFullTime": 0x0C,
                "EventGlobalExtraTime": 0x10,
                "EventGlobalPenalties": 0x14,
            },
        )
        self.assertEqual(
            SOURCE_CLOCK_RECEIVER_VTABLES,
            {
                "EventGlobalTick": 0x7CA468,
                "EventGlobalHalfTime": 0x7CA45C,
                "EventGlobalSecondHalf": 0x7CA450,
                "EventGlobalFullTime": 0x7CA444,
                "EventGlobalExtraTime": 0x7CA438,
                "EventGlobalPenalties": 0x7CA42C,
            },
        )
        self.assertEqual(SOURCE_CLOCK_CALLBACK_GLOBAL_TICK, 0x51EDB0)
        self.assertEqual(SOURCE_CLOCK_CALLBACK_HALF_TIME, 0x51EEE0)
        self.assertEqual(SOURCE_CLOCK_CALLBACK_SECOND_HALF, 0x51EFB0)
        self.assertEqual(SOURCE_CLOCK_CALLBACK_FULL_TIME, 0x51EFD0)
        self.assertEqual(SOURCE_CLOCK_CALLBACK_EXTRA_TIME, 0x51F0A0)
        self.assertEqual(SOURCE_CLOCK_CALLBACK_PENALTIES, 0x51F170)
        self.assertEqual(SOURCE_CLOCK_SECOND_HALF_LATCH_OFFSET, 0x6C)
        self.assertEqual(SOURCE_CLOCK_POST_90_LATCH_OFFSET, 0x6D)
        self.assertEqual(SOURCE_CLOCK_PENALTIES_LATCH_OFFSET, 0x6E)

    def test_localization_globals_map_to_exact_english_strings(self):
        expected = {
            "mins": (0x982384, 2333, 21532, "mins"),
            "half_time": (0x98238C, 2331, 21530, "Half time"),
            "full_time": (0x982388, 2332, 21531, "Full time"),
            "extra_time": (0x9821F4, 2433, 21617, "Extra time"),
            "penalties": (0x9822D0, 2378, 20014, "Penalties"),
        }
        self.assertEqual(SOURCE_CLOCK_LOCALIZED_TEXT, expected)

        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        idx_bytes = (root / "English.idx").read_bytes()
        str_bytes = (root / "English.str").read_bytes()
        self.assertEqual(
            sha256(idx_bytes).hexdigest(),
            "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1",
        )
        self.assertEqual(
            sha256(str_bytes).hexdigest(),
            "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601",
        )
        strings, index = parse_language_pair(str_bytes, idx_bytes)
        for _label, (_global, entry, string_id, text) in expected.items():
            with self.subTest(entry=entry):
                self.assertEqual(index.string_ids[entry], string_id)
                self.assertEqual(index.resolve(strings, entry), text)

    def test_initial_and_first_half_numeric_state_is_white(self):
        state = initial_fastview_clock_state()
        self.assertEqual(state.text, "")
        self.assertIs(state.color, CLOCK_WHITE)
        self.assertIs(apply_clock_global_tick(state, 0), state)

        state = apply_clock_global_tick(state, 1)
        self.assertEqual(state.text, "1 mins")
        self.assertIs(state.color, CLOCK_WHITE)
        self.assertEqual(state.last_numeric_tick, 1)

        state = apply_clock_global_tick(state, 45)
        self.assertEqual(state.text, "45 mins")
        self.assertIs(state.color, CLOCK_WHITE)

    def test_46_threshold_alerts_until_half_time_then_second_half_latches(self):
        state = apply_clock_global_tick(initial_fastview_clock_state(), 46)
        self.assertEqual(state.text, "46 mins")
        self.assertIs(state.color, CLOCK_ALERT)
        self.assertFalse(state.second_half_latched)

        state = apply_clock_half_time(state)
        self.assertEqual(state.text, "Half time")
        self.assertIs(state.color, CLOCK_WHITE)

        state = apply_clock_second_half(state)
        self.assertTrue(state.second_half_latched)
        self.assertEqual(state.text, "46 mins")
        self.assertIs(state.color, CLOCK_WHITE)

        state = apply_clock_global_tick(state, 90)
        self.assertEqual(state.text, "90 mins")
        self.assertIs(state.color, CLOCK_WHITE)

        state = apply_clock_global_tick(state, 91)
        self.assertEqual(state.text, "91 mins")
        self.assertIs(state.color, CLOCK_ALERT)

    def test_full_extra_and_penalties_callbacks_match_source_text_color_latches(self):
        state = apply_clock_second_half(
            apply_clock_half_time(
                apply_clock_global_tick(initial_fastview_clock_state(), 46)
            )
        )

        full = apply_clock_full_time(apply_clock_global_tick(state, 91))
        self.assertEqual(full.text, "Full time")
        self.assertIs(full.color, CLOCK_WHITE)
        self.assertTrue(full.post_90_latched)

        extra = apply_clock_extra_time(state)
        self.assertEqual(extra.text, "Extra time")
        self.assertIs(extra.color, CLOCK_ALERT)
        self.assertTrue(extra.post_90_latched)

        penalties = apply_clock_penalties(extra)
        self.assertEqual(penalties.text, "Penalties")
        self.assertIs(penalties.color, CLOCK_ALERT)
        self.assertTrue(penalties.penalties_latched)
        self.assertIs(apply_clock_global_tick(penalties, 120), penalties)

    def test_alert_color_stays_fail_closed_for_modern_rgba(self):
        self.assertIsNone(CLOCK_ALERT.native_color_16)
        self.assertEqual(CLOCK_ALERT.source_rgb8, (255, 45, 45))
        self.assertFalse(CLOCK_ALERT.exact_modern_rgba_recovered)
        self.assertEqual(CLOCK_WHITE.native_color_16, 0xFFFF)
        self.assertIsNone(CLOCK_WHITE.source_rgb8)
        self.assertTrue(CLOCK_WHITE.exact_modern_rgba_recovered)

        with self.assertRaisesRegex(FastViewClockError, "exact modern RGBA"):
            replace(CLOCK_ALERT, exact_modern_rgba_recovered=True)

    def test_possession_lookup_uses_global_tick_divided_by_five(self):
        self.assertEqual(SOURCE_POSSESSION_ARRAY_LOOKUP_VA, 0x631240)
        self.assertEqual(possession_array_index_for_global_tick(0), 0)
        self.assertEqual(possession_array_index_for_global_tick(5), 1)
        self.assertEqual(possession_array_index_for_global_tick(40), 8)
        self.assertEqual(possession_array_index_for_global_tick(90), 18)

    def test_contract_retains_raster_and_global_order_boundaries(self):
        contract = fastview_clock_contract()
        self.assertTrue(contract["clock_text_state_machine_recovered"])
        self.assertFalse(contract["alert_packed16_value_recovered"])
        self.assertFalse(contract["alert_modern_rgba_recovered"])
        self.assertFalse(contract["clock_raster_integrated"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])

    def test_invalid_values_fail_closed(self):
        with self.assertRaises(FastViewClockError):
            fastview_clock_numeric_value(-1)
        with self.assertRaises(FastViewClockError):
            possession_array_index_for_global_tick(7)
        with self.assertRaises(FastViewClockError):
            possession_array_index_for_global_tick(True)
        with self.assertRaises(FastViewClockError):
            apply_clock_global_tick(object(), 1)


if __name__ == "__main__":
    unittest.main()
