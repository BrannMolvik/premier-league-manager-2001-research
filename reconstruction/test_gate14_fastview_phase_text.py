"""Tests for source-closed ScoreComposite phase labels."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import unittest

from ea_language_strings import parse_language_pair
from gate14_fastview_phase_text import (
    CANONICAL_ENGLISH_IDX_ENTRY_COUNT,
    CANONICAL_ENGLISH_IDX_SHA256,
    CANONICAL_ENGLISH_IDX_SIZE,
    CANONICAL_ENGLISH_STR_SHA256,
    CANONICAL_ENGLISH_STR_SIZE,
    GENERIC_TEXT_CONSTRUCTOR_VA,
    GENERIC_TEXT_DRAW_VA,
    LANGUAGE_GLOBAL_FIRST_VA,
    LANGUAGE_GLOBAL_LAST_VA,
    LANGUAGE_GLOBAL_STRIDE,
    LANGUAGE_INDEX_READ_VA,
    LANGUAGE_INITIALIZER_FIRST_READ_CALLSITE_VA,
    LANGUAGE_INITIALIZER_LAST_READ_CALLSITE_VA,
    LANGUAGE_POINTER_RESOLVE_VA,
    PHASE_ICON_CONSTRUCTOR_CALLSITE_VA,
    PHASE_TEXT_BY_EVENT,
    PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA,
    PHASE_TEXT_NATIVE_COLOR_16,
    PHASE_TEXT_RENDER_FLAGS,
    PHASE_TEXT_STYLE_WRAPPER_VA,
    FastViewScorePhaseTextError,
    language_entry_for_global,
    score_phase_text,
    score_phase_text_contract,
)


class FastViewScorePhaseTextTests(unittest.TestCase):
    def test_localization_initializer_is_exactly_the_2714_entry_idx_table(self):
        self.assertEqual(LANGUAGE_INDEX_READ_VA, 0x667E90)
        self.assertEqual(LANGUAGE_POINTER_RESOLVE_VA, 0x64E320)
        self.assertEqual(LANGUAGE_INITIALIZER_FIRST_READ_CALLSITE_VA, 0x635F56)
        self.assertEqual(LANGUAGE_INITIALIZER_LAST_READ_CALLSITE_VA, 0x64C7AC)
        self.assertEqual(CANONICAL_ENGLISH_IDX_ENTRY_COUNT, 2714)
        self.assertEqual(LANGUAGE_GLOBAL_FIRST_VA, 0x9847F8)
        self.assertEqual(LANGUAGE_GLOBAL_LAST_VA, 0x981D94)
        self.assertEqual(LANGUAGE_GLOBAL_STRIDE, -4)
        self.assertEqual(
            language_entry_for_global(LANGUAGE_GLOBAL_LAST_VA),
            CANONICAL_ENGLISH_IDX_ENTRY_COUNT - 1,
        )

    def test_phase_globals_map_to_exact_english_entries_and_strings(self):
        expected = {
            "EventHalfTime": (0x982380, 2334, 21533, "HT"),
            "EventFullTime": (0x98237C, 2335, 21534, "FT"),
            "EventExtraTime": (0x982378, 2336, 21535, "ET"),
            "EventPenalties": (0x982374, 2337, 21536, "PEN"),
        }
        self.assertEqual(set(PHASE_TEXT_BY_EVENT), set(expected))
        for event_name, values in expected.items():
            with self.subTest(event_name=event_name):
                item = score_phase_text(event_name)
                self.assertEqual(
                    (
                        item.label_global_va,
                        item.english_idx_entry,
                        item.english_string_id,
                        item.text,
                    ),
                    values,
                )
                self.assertEqual(
                    language_entry_for_global(item.label_global_va),
                    item.english_idx_entry,
                )

    def test_checked_in_original_english_pair_replays_exact_phase_labels(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        idx_bytes = (root / "English.idx").read_bytes()
        str_bytes = (root / "English.str").read_bytes()
        self.assertEqual(len(idx_bytes), CANONICAL_ENGLISH_IDX_SIZE)
        self.assertEqual(len(str_bytes), CANONICAL_ENGLISH_STR_SIZE)
        self.assertEqual(sha256(idx_bytes).hexdigest(), CANONICAL_ENGLISH_IDX_SHA256)
        self.assertEqual(sha256(str_bytes).hexdigest(), CANONICAL_ENGLISH_STR_SHA256)

        strings, index = parse_language_pair(str_bytes, idx_bytes)
        self.assertEqual(len(index.string_ids), CANONICAL_ENGLISH_IDX_ENTRY_COUNT)
        for item in PHASE_TEXT_BY_EVENT.values():
            with self.subTest(event_name=item.event_name):
                self.assertEqual(index.string_ids[item.english_idx_entry], item.english_string_id)
                self.assertEqual(
                    index.resolve(strings, item.english_idx_entry),
                    item.text,
                )

    def test_generic_text_contract_is_centered_white_style_one(self):
        contract = score_phase_text_contract()
        self.assertEqual(GENERIC_TEXT_CONSTRUCTOR_VA, 0x527960)
        self.assertEqual(GENERIC_TEXT_DRAW_VA, 0x64F090)
        self.assertEqual(PHASE_TEXT_STYLE_WRAPPER_VA, 0x87BE90)
        self.assertEqual(PHASE_TEXT_NATIVE_COLOR_16, 0xFFFF)
        self.assertEqual(PHASE_TEXT_RENDER_FLAGS, 0x2C)
        self.assertEqual(contract["raw_flags"], 0x24)
        self.assertEqual(contract["render_flags"], 0x2C)
        self.assertEqual(contract["horizontal_alignment"], "center")
        self.assertEqual(contract["vertical_alignment"], "center")
        self.assertEqual(contract["native_color_16"], 0xFFFF)

    def test_runtime_append_contract_keeps_interleaving_fail_closed(self):
        contract = score_phase_text_contract()
        self.assertEqual(PHASE_ICON_CONSTRUCTOR_CALLSITE_VA, 0x51BB05)
        self.assertEqual(PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA, 0x51BB9A)
        self.assertLess(
            PHASE_ICON_CONSTRUCTOR_CALLSITE_VA,
            PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA,
        )
        self.assertTrue(contract["per_callback_icon_before_text"])
        self.assertFalse(contract["global_all_icons_before_all_text"])
        self.assertTrue(contract["paired_phase_text_identity_recovered"])
        self.assertFalse(contract["paired_phase_text_rasterized"])
        self.assertFalse(contract["runtime_icon_text_interleaving_flattened"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])

    def test_contract_rejects_bad_global_and_false_record_mutation(self):
        for value in (0x9847FA, 0x9847FC, 0x981D90, "0x982380"):
            with self.subTest(value=value):
                with self.assertRaises(FastViewScorePhaseTextError):
                    language_entry_for_global(value)

        item = score_phase_text("EventHalfTime")
        with self.assertRaisesRegex(
            FastViewScorePhaseTextError,
            "mapping drifted",
        ):
            replace(item, english_idx_entry=2335)
        with self.assertRaisesRegex(
            FastViewScorePhaseTextError,
            "alignment",
        ):
            replace(item, horizontal_alignment="left")
        with self.assertRaisesRegex(
            FastViewScorePhaseTextError,
            "native color",
        ):
            replace(item, native_color_16=0)

        with self.assertRaisesRegex(
            FastViewScorePhaseTextError,
            "no source-closed",
        ):
            score_phase_text("EventGlobalSecondHalf")


if __name__ == "__main__":
    unittest.main()
