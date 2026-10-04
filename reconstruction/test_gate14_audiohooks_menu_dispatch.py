"""Tests for source-closed numeric AudioHooks -> menus.bnk routing."""
from dataclasses import replace
import unittest

from gate14_audiohooks_menu_dispatch import (
    SOURCE_BOUNDARY,
    Gate14AudioHooksDispatchError,
    directly_reachable_menu_sample_slots,
    menus_sample_for_audiohooks_event,
)


class AudioHooksMenuDispatchTests(unittest.TestCase):
    def test_unconditional_event_ids_keep_literal_sample_slots(self):
        expected = {
            17: 6,
            18: 7,
            19: 1,
            23: 16,
            24: 17,
            25: 16,
            26: 17,
            31: 20,
            32: 20,
        }
        for event_id, sample in expected.items():
            with self.subTest(event_id=event_id):
                self.assertEqual(
                    menus_sample_for_audiohooks_event(event_id, 999).sample_slot,
                    sample,
                )

    def test_zero_state_and_special_predicates_match_source_switch(self):
        zero_state = {
            5: 11,
            6: 12,
            20: 13,
            21: 15,
            22: 14,
            27: 8,
            28: 9,
            29: 4,
            30: 5,
            33: 22,
            34: 21,
        }
        for event_id, sample in zero_state.items():
            with self.subTest(event_id=event_id):
                self.assertEqual(
                    menus_sample_for_audiohooks_event(event_id, 0).sample_slot,
                    sample,
                )
                self.assertIsNone(
                    menus_sample_for_audiohooks_event(event_id, 1).sample_slot
                )

        for event_id in (2, 3, 4):
            self.assertEqual(
                menus_sample_for_audiohooks_event(event_id, 0).sample_slot, 2
            )
            self.assertEqual(
                menus_sample_for_audiohooks_event(event_id, 3).sample_slot, 2
            )
            self.assertIsNone(
                menus_sample_for_audiohooks_event(event_id, 1).sample_slot
            )

        self.assertEqual(menus_sample_for_audiohooks_event(8, 8).sample_slot, 10)
        self.assertIsNone(menus_sample_for_audiohooks_event(8, 0).sample_slot)

        self.assertEqual(menus_sample_for_audiohooks_event(10, 0).sample_slot, 2)
        self.assertEqual(menus_sample_for_audiohooks_event(10, 3).sample_slot, 2)
        self.assertEqual(menus_sample_for_audiohooks_event(10, 6).sample_slot, 3)
        self.assertIsNone(menus_sample_for_audiohooks_event(10, 1).sample_slot)

        self.assertEqual(menus_sample_for_audiohooks_event(35, 0).sample_slot, 18)
        self.assertEqual(menus_sample_for_audiohooks_event(35, 1).sample_slot, 19)
        self.assertIsNone(menus_sample_for_audiohooks_event(35, 2).sample_slot)

    def test_known_no_sound_switch_entries_remain_silent(self):
        for event_id in (7, 9, 11, 12, 13, 14, 15, 16):
            with self.subTest(event_id=event_id):
                self.assertIsNone(
                    menus_sample_for_audiohooks_event(event_id, 0).sample_slot
                )

    def test_direct_dispatch_reaches_every_nonzero_menu_slot_exactly_as_set(self):
        self.assertEqual(
            directly_reachable_menu_sample_slots(),
            tuple(range(1, 23)),
        )

    def test_numeric_contract_does_not_promote_event_or_sample_meaning(self):
        row = menus_sample_for_audiohooks_event(17, 0)
        self.assertFalse(row.event_semantics_recovered)
        self.assertFalse(row.sample_semantics_recovered)
        self.assertTrue(SOURCE_BOUNDARY.numeric_switch_recovered)
        self.assertTrue(SOURCE_BOUNDARY.literal_sample_slots_recovered)
        self.assertTrue(SOURCE_BOUNDARY.state_predicates_recovered)
        self.assertFalse(SOURCE_BOUNDARY.semantic_event_binding_recovered)
        self.assertFalse(SOURCE_BOUNDARY.sample_meaning_recovered)

        with self.assertRaisesRegex(
            Gate14AudioHooksDispatchError,
            "cannot promote",
        ):
            replace(SOURCE_BOUNDARY, semantic_event_binding_recovered=True)

    def test_rejects_out_of_range_or_wrong_type_inputs(self):
        for event_id in (1, 36):
            with self.subTest(event_id=event_id):
                with self.assertRaisesRegex(
                    Gate14AudioHooksDispatchError,
                    "2..35",
                ):
                    menus_sample_for_audiohooks_event(event_id, 0)
        with self.assertRaisesRegex(
            Gate14AudioHooksDispatchError,
            "state_value must be integer",
        ):
            menus_sample_for_audiohooks_event(17, True)


if __name__ == "__main__":
    unittest.main()
