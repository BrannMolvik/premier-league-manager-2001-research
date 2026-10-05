"""Tests for source-closed FastView GoalFlash row contract."""
import unittest

from gate14_fastview_goalflash_source import (
    ACTIVE_RGB,
    CONTROL_EXTRA_0X1000_SEMANTIC_RECOVERED,
    CONTROL_RAW_FLAGS,
    CONTROL_RENDER_FLAGS,
    EVENT_GOAL_SOURCE_OFFSETS,
    EVENT_SCORE_SOURCE_OFFSETS,
    GOALFLASH_CELLS,
    GOALFLASH_CHILD_COUNT,
    GOALFLASH_EVENT_GOAL_CALLBACK_VA,
    GOALFLASH_EVENT_SCORE_CALLBACK_VA,
    GOALFLASH_FONT_PATH,
    GOALFLASH_PENALTY_MISSED,
    GOALFLASH_PENALTY_SCORED,
    GOALFLASH_PENALTY_SHOT_CALLBACK_VA,
    GOALFLASH_RECEIVER_TYPES,
    GOALFLASH_STYLE_INDEX,
    INACTIVE_RGB,
    PENALTY_SHOT_SOURCE_OFFSETS,
    goalflash_row_rects,
    goalflash_source_contract,
    normal_goalflash_active_cells,
    normal_goalflash_texts,
    penalty_goalflash_active_cells,
    penalty_goalflash_texts,
)


class FastViewGoalFlashSourceTests(unittest.TestCase):
    def test_rtti_closes_three_typed_receivers_and_two_child_rows(self):
        self.assertEqual(GOALFLASH_CHILD_COUNT, 2)
        self.assertEqual(
            GOALFLASH_RECEIVER_TYPES,
            (
                "Receiver<EventGoal>",
                "Receiver<EventScore>",
                "Receiver<EventPenaltyShootoutShot>",
            ),
        )
        self.assertEqual(GOALFLASH_EVENT_GOAL_CALLBACK_VA, 0x51CD70)
        self.assertEqual(GOALFLASH_EVENT_SCORE_CALLBACK_VA, 0x51CE80)
        self.assertEqual(GOALFLASH_PENALTY_SHOT_CALLBACK_VA, 0x51CEA0)
        self.assertEqual(EVENT_SCORE_SOURCE_OFFSETS, (0x0C, 0x10, 0x14, 0x18))
        self.assertEqual(EVENT_GOAL_SOURCE_OFFSETS, (0x00, 0x04, 0x08, 0x0C, 0x10))
        self.assertEqual(
            PENALTY_SHOT_SOURCE_OFFSETS,
            (0x00, 0x04, 0x08, 0x0C, 0x10, 0x24),
        )

    def test_five_cells_form_exact_488_by_33_dynamic_row(self):
        self.assertEqual(
            tuple((cell.x_offset, cell.width) for cell in GOALFLASH_CELLS),
            ((0, 134), (134, 30), (164, 30), (194, 134), (328, 160)),
        )
        self.assertEqual(
            goalflash_row_rects(100, 50),
            (
                (100, 50, 234, 83),
                (234, 50, 264, 83),
                (264, 50, 294, 83),
                (294, 50, 428, 83),
                (428, 50, 588, 83),
            ),
        )
        self.assertEqual(GOALFLASH_STYLE_INDEX, 1)
        self.assertEqual(GOALFLASH_FONT_PATH, "Fonts/Zurich_BdXCn_BT_18pixel.fnt")
        self.assertEqual(CONTROL_RAW_FLAGS, (0x22, 0x22, 0x21, 0x21, 0x1022))
        self.assertEqual(
            CONTROL_RENDER_FLAGS,
            (0x2A, 0x2A, 0x29, 0x29, 0x102A),
        )
        self.assertFalse(CONTROL_EXTRA_0X1000_SEMANTIC_RECOVERED)

    def test_normal_goal_formatter_preserves_exact_source_string_shape(self):
        self.assertEqual(
            normal_goalflash_texts(
                "ARSENAL",
                2,
                1,
                "CHELSEA",
                "Henry",
                67,
            ),
            ("ARSENAL", "2", "1", "CHELSEA", " (Henry 67)"),
        )
        self.assertEqual(normal_goalflash_active_cells(True), (0, 1))
        self.assertEqual(normal_goalflash_active_cells(False), (2, 3))
        self.assertEqual(ACTIVE_RGB, (255, 255, 255))
        self.assertEqual(INACTIVE_RGB, (0, 0, 0))

    def test_penalty_shootout_formatter_uses_exact_scored_missed_suffixes(self):
        self.assertEqual(GOALFLASH_PENALTY_SCORED, " scored")
        self.assertEqual(GOALFLASH_PENALTY_MISSED, " missed")
        self.assertEqual(
            penalty_goalflash_texts(
                "ARSENAL", 4, 3, "CHELSEA", "Player A", scored=True
            ),
            ("ARSENAL", "4", "3", "CHELSEA", "Player A scored"),
        )
        self.assertEqual(
            penalty_goalflash_texts(
                "ARSENAL", 4, 3, "CHELSEA", "Player B", scored=False
            ),
            ("ARSENAL", "4", "3", "CHELSEA", "Player B missed"),
        )
        self.assertEqual(
            penalty_goalflash_active_cells(True, scored=True),
            (0, 1),
        )
        self.assertEqual(
            penalty_goalflash_active_cells(False, scored=True),
            (2, 3),
        )
        self.assertEqual(penalty_goalflash_active_cells(True, scored=False), ())

    def test_contract_keeps_unproven_goal_event_labels_and_pixels_fail_closed(self):
        contract = goalflash_source_contract()
        self.assertEqual(contract["child_count"], 2)
        self.assertTrue(contract["penalty_suffix_semantics_recovered"])
        self.assertTrue(contract["dynamic_row_position_recovered"])
        self.assertFalse(contract["normal_event_string_semantic_recovered"])
        self.assertFalse(contract["normal_event_dword0_semantic_recovered"])
        self.assertFalse(contract["absolute_flash_timing_position_recovered"])
        self.assertFalse(contract["goalflash_pixels_rasterized"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
