"""Tests for source-closed ScoreComposite phase receiver ordering."""
from dataclasses import replace
import unittest

from gate14_fastview_phase_receiver_order import (
    EXTRA_TIME_DISPATCH_LOOP_END_VA,
    EXTRA_TIME_DISPATCH_LOOP_START_VA,
    HALF_TIME_DISPATCH_LOOP_END_VA,
    HALF_TIME_DISPATCH_LOOP_START_VA,
    LEAGUE_SCORES_ROW_BUILD_LOOP_VA,
    LEAGUE_SCORES_SCORE_FACTORY_CALLSITE_VA,
    PENALTIES_DISPATCH_LOOP_END_VA,
    PENALTIES_DISPATCH_LOOP_START_VA,
    PHASE_ICON_CONSTRUCTOR_CALLSITE_VA,
    PHASE_RECEIVER_FAMILIES,
    PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA,
    RECEIVER_CALLBACK_VTABLE_OFFSET,
    RECEIVER_LIST_APPEND_HELPER_VA,
    RECEIVER_NODE_DATA_COPY_VA,
    RECEIVER_NODE_NEXT_OFFSET,
    RECEIVER_NODE_OBJECT_OFFSET,
    RECEIVER_NODE_PREV_OFFSET,
    REGISTER_EXTRA_TIME_CALLSITE_VA,
    REGISTER_FULL_TIME_CALLSITE_VA,
    REGISTER_HALF_TIME_CALLSITE_VA,
    REGISTER_PENALTIES_CALLSITE_VA,
    SCORE_RECEIVER_EXTRA_TIME_OFFSET,
    SCORE_RECEIVER_FULL_TIME_OFFSET,
    SCORE_RECEIVER_HALF_TIME_OFFSET,
    SCORE_RECEIVER_PENALTIES_OFFSET,
    SENDER_EXTRA_TIME_OFFSET,
    SENDER_FULL_TIME_OFFSET,
    SENDER_HALF_TIME_OFFSET,
    SENDER_LIST_COUNT_OFFSET,
    SENDER_LIST_SENTINEL_OFFSET,
    SENDER_PENALTIES_OFFSET,
    FastViewPhaseReceiverOrderError,
    aggregate_runtime_icon_text_order_recovered,
    per_broadcast_control_append_sequence,
    phase_broadcast_receiver_order,
    phase_receiver_order_contract,
    source_row_registration_order,
)


class FastViewPhaseReceiverOrderTests(unittest.TestCase):
    def test_exact_registration_source_anchors(self):
        self.assertEqual(LEAGUE_SCORES_ROW_BUILD_LOOP_VA, 0x522E3A)
        self.assertEqual(LEAGUE_SCORES_SCORE_FACTORY_CALLSITE_VA, 0x522E6C)
        self.assertEqual(RECEIVER_LIST_APPEND_HELPER_VA, 0x5302C0)
        self.assertEqual(RECEIVER_NODE_DATA_COPY_VA, 0x530330)
        self.assertEqual(SENDER_LIST_SENTINEL_OFFSET, 0x08)
        self.assertEqual(SENDER_LIST_COUNT_OFFSET, 0x0C)
        self.assertEqual(RECEIVER_NODE_NEXT_OFFSET, 0)
        self.assertEqual(RECEIVER_NODE_PREV_OFFSET, 4)
        self.assertEqual(RECEIVER_NODE_OBJECT_OFFSET, 8)
        self.assertEqual(RECEIVER_CALLBACK_VTABLE_OFFSET, 4)

    def test_four_phase_families_register_from_same_row_loop(self):
        self.assertEqual(
            tuple(
                (
                    item.event_name,
                    item.receiver_offset,
                    item.sender_offset,
                    item.registration_callsite_va,
                )
                for item in PHASE_RECEIVER_FAMILIES
            ),
            (
                ("EventHalfTime", 0x94, 0x40, 0x522F5C),
                ("EventExtraTime", 0x98, 0x60, 0x522FAF),
                ("EventPenalties", 0x9C, 0x70, 0x523002),
                ("EventFullTime", 0xA0, 0x50, 0x523055),
            ),
        )
        self.assertEqual(SCORE_RECEIVER_HALF_TIME_OFFSET, 0x94)
        self.assertEqual(SCORE_RECEIVER_EXTRA_TIME_OFFSET, 0x98)
        self.assertEqual(SCORE_RECEIVER_PENALTIES_OFFSET, 0x9C)
        self.assertEqual(SCORE_RECEIVER_FULL_TIME_OFFSET, 0xA0)
        self.assertEqual(SENDER_HALF_TIME_OFFSET, 0x40)
        self.assertEqual(SENDER_FULL_TIME_OFFSET, 0x50)
        self.assertEqual(SENDER_EXTRA_TIME_OFFSET, 0x60)
        self.assertEqual(SENDER_PENALTIES_OFFSET, 0x70)
        self.assertEqual(REGISTER_HALF_TIME_CALLSITE_VA, 0x522F5C)
        self.assertEqual(REGISTER_EXTRA_TIME_CALLSITE_VA, 0x522FAF)
        self.assertEqual(REGISTER_PENALTIES_CALLSITE_VA, 0x523002)
        self.assertEqual(REGISTER_FULL_TIME_CALLSITE_VA, 0x523055)

    def test_forward_dispatch_loop_anchors(self):
        self.assertEqual(
            (HALF_TIME_DISPATCH_LOOP_START_VA, HALF_TIME_DISPATCH_LOOP_END_VA),
            (0x519A75, 0x519AAE),
        )
        self.assertEqual(
            (EXTRA_TIME_DISPATCH_LOOP_START_VA, EXTRA_TIME_DISPATCH_LOOP_END_VA),
            (0x519B00, 0x519B1A),
        )
        self.assertEqual(
            (PENALTIES_DISPATCH_LOOP_START_VA, PENALTIES_DISPATCH_LOOP_END_VA),
            (0x519B5A, 0x519B74),
        )

    def test_tail_registration_plus_forward_dispatch_preserves_source_row_order(self):
        for count in (1, 2, 6, 12):
            with self.subTest(count=count):
                expected = tuple(range(count))
                self.assertEqual(source_row_registration_order(count), expected)
                self.assertEqual(phase_broadcast_receiver_order(count), expected)

    def test_one_broadcast_appends_icon_then_text_per_row_in_source_order(self):
        self.assertLess(
            PHASE_ICON_CONSTRUCTOR_CALLSITE_VA,
            PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA,
        )
        self.assertEqual(
            per_broadcast_control_append_sequence(3),
            (
                ("icon", 0),
                ("text", 0),
                ("icon", 1),
                ("text", 1),
                ("icon", 2),
                ("text", 2),
            ),
        )

    def test_aggregate_family_order_stays_fail_closed_across_broadcasts(self):
        self.assertFalse(aggregate_runtime_icon_text_order_recovered())
        contract = phase_receiver_order_contract()
        self.assertTrue(contract["tail_insertion_recovered"])
        self.assertTrue(contract["forward_sender_traversal_recovered"])
        self.assertTrue(contract["source_row_registration_order_recovered"])
        self.assertTrue(contract["per_broadcast_receiver_order_recovered"])
        self.assertTrue(contract["per_callback_icon_before_text_recovered"])
        self.assertFalse(contract["aggregate_runtime_icon_text_order_recovered"])
        self.assertFalse(contract["flattened_runtime_phase_planes"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])

    def test_invalid_visible_page_count_fails_closed(self):
        for count in (0, 13, -1, True, 1.5):
            with self.subTest(count=count):
                with self.assertRaises(FastViewPhaseReceiverOrderError):
                    source_row_registration_order(count)


if __name__ == "__main__":
    unittest.main()
