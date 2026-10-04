"""Tests for the source-closed outer FastViewPanel draw-array order."""
from dataclasses import replace
import unittest

from gate14_fastview_outer_draw_order import (
    CLOCK_OWNER_CALL_VA,
    CLOCK_TEXT_REGISTER_CALL_VA,
    DIRECT_TEXT0_RECT,
    DIRECT_TEXT0_REGISTER_CALL_VA,
    DIRECT_TEXT1_RECT,
    DIRECT_TEXT1_REGISTER_CALL_VA,
    EMBEDDED_BUTTON0_CONSTRUCTOR_CALL_VA,
    EMBEDDED_BUTTON0_PARENT_OFFSET,
    EMBEDDED_BUTTON0_REGISTER_CALL_VA,
    EMBEDDED_BUTTON1_CONSTRUCTOR_CALL_VA,
    EMBEDDED_BUTTON1_PARENT_OFFSET,
    EMBEDDED_BUTTON1_REGISTER_CALL_VA,
    EMBEDDED_BUTTON_CONSTRUCTOR_VA,
    FASTVIEW_OUTER_DRAW_COUNT,
    FASTVIEW_OUTER_DRAW_ENTRIES,
    POST_TEAM_CONTROL_ARRAY_PARENT_OFFSET,
    POST_TEAM_CONTROL_CONSTRUCTOR_VA,
    POST_TEAM_CONTROL_COUNT,
    POST_TEAM_CONTROL_STRIDE,
    POST_TEAM_REGISTER_LOOP_CALL_VA,
    GOAL_FLASH_CHILD_CONSTRUCTOR_VA,
    GOAL_FLASH_CHILD_COUNT,
    GOAL_FLASH_CONSTRUCTOR_VA,
    GOAL_FLASH_OWNER_CALL_VA,
    GOAL_FLASH_TEXT_RECTS,
    GOAL_FLASH_TEXT_REGISTER_CALLS,
    POSSESSION_DIAGRAM_REGISTER_CALLS,
    POSSESSION_FIGURES_REGISTER_CALLS,
    SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA,
    SCORE_COMPOSITE_MAIN_CONSTRUCTORS,
    SCORE_COMPOSITE_MAIN_OWNER_CALL_VAS,
    SCORE_COMPOSITE_MAIN_REGISTER_CALLS,
    SCORES_SUBPANEL_REGISTER_CALL_VA,
    SURFACED_PICTURE_CONTROL_CONSTRUCTOR_VA,
    SURFACED_PICTURE_CONTROL_RTTI,
    SURFACED_PICTURE_CONTROL_VTABLE_VA,
    SURFACED_PICTURE_OWNER_CALLS,
    SURFACED_PICTURE_REGISTER_CALL_VA,
    SOURCE_BOUNDARY,
    TEAM_SUBPANEL_REGISTER_CALL_VA,
    FastViewOuterDrawOrderError,
    outer_draw_before,
    outer_draw_rank,
)


class FastViewOuterDrawOrderTests(unittest.TestCase):
    def test_exhaustive_outer_sequence_has_36_unique_ranks(self):
        self.assertEqual(FASTVIEW_OUTER_DRAW_COUNT, 36)
        self.assertEqual(len(FASTVIEW_OUTER_DRAW_ENTRIES), 36)
        self.assertEqual(
            tuple(row.rank for row in FASTVIEW_OUTER_DRAW_ENTRIES),
            tuple(range(36)),
        )
        self.assertEqual(
            len({row.identity for row in FASTVIEW_OUTER_DRAW_ENTRIES}),
            36,
        )

    def test_exact_outer_sequence(self):
        self.assertEqual(
            tuple(row.identity for row in FASTVIEW_OUTER_DRAW_ENTRIES),
            (
                "surfaced_picture_control_0",
                "top_bar_picture",
                "ticker_picture",
                "clock_text",
                "embedded_button_0",
                "embedded_button_1",
                "goal_flash_0_text_0",
                "goal_flash_0_text_1",
                "goal_flash_0_text_2",
                "goal_flash_0_text_3",
                "goal_flash_0_text_4",
                "goal_flash_1_text_0",
                "goal_flash_1_text_1",
                "goal_flash_1_text_2",
                "goal_flash_1_text_3",
                "goal_flash_1_text_4",
                "score_composite_main_control_0",
                "score_composite_main_control_1",
                "score_composite_main_control_2",
                "score_composite_main_control_3",
                "score_composite_main_control_4",
                "surfaced_picture_control_1",
                "surfaced_picture_control_2",
                "possession_diagram_picture_0",
                "possession_diagram_picture_1",
                "possession_diagram_picture_2",
                "possession_diagram_picture_3",
                "possession_figures_text_0",
                "possession_figures_text_1",
                "possession_figures_text_2",
                "direct_text_0",
                "direct_text_1",
                "scores_subpanel",
                "team_subpanel",
                "post_team_control_0",
                "post_team_control_1",
            ),
        )

    def test_clock_and_nested_component_source_anchors(self):
        self.assertEqual(SURFACED_PICTURE_CONTROL_CONSTRUCTOR_VA, 0x526940)
        self.assertEqual(SURFACED_PICTURE_CONTROL_VTABLE_VA, 0x7CA974)
        self.assertEqual(
            SURFACED_PICTURE_CONTROL_RTTI,
            ".?AVSurfacedPictureControl@FastViewPanel@@",
        )
        self.assertEqual(SURFACED_PICTURE_REGISTER_CALL_VA, 0x5269E5)
        self.assertEqual(
            SURFACED_PICTURE_OWNER_CALLS,
            (
                (0x51FD31, (0, 0, 800, 600)),
                (0x520642, (38, 1, 173, 94)),
                (0x520697, (627, 1, 762, 94)),
            ),
        )
        self.assertEqual(CLOCK_OWNER_CALL_VA, 0x51FE7B)
        self.assertEqual(CLOCK_TEXT_REGISTER_CALL_VA, 0x51EC30)
        self.assertEqual(
            POSSESSION_DIAGRAM_REGISTER_CALLS,
            (0x522894, 0x52291D, 0x5229AA, 0x522A33),
        )
        self.assertEqual(
            POSSESSION_FIGURES_REGISTER_CALLS,
            (0x51E876, 0x51E900, 0x51E990),
        )
        self.assertEqual(GOAL_FLASH_OWNER_CALL_VA, 0x5200CB)
        self.assertEqual(GOAL_FLASH_CONSTRUCTOR_VA, 0x51C700)
        self.assertEqual(GOAL_FLASH_CHILD_CONSTRUCTOR_VA, 0x51BE20)
        self.assertEqual(GOAL_FLASH_CHILD_COUNT, 2)
        self.assertEqual(
            GOAL_FLASH_TEXT_REGISTER_CALLS,
            (0x51BF51, 0x51BFDC, 0x51C067, 0x51C0F2, 0x51C180),
        )
        self.assertEqual(
            GOAL_FLASH_TEXT_RECTS,
            (
                (0, 0, 134, 33),
                (0, 0, 30, 33),
                (0, 0, 30, 33),
                (0, 0, 134, 33),
                (0, 0, 160, 33),
            ),
        )
        self.assertEqual(SCORE_COMPOSITE_MAIN_OWNER_CALL_VAS, (0x520356, 0x520416, 0x5204D6))
        self.assertEqual(SCORE_COMPOSITE_MAIN_CONSTRUCTORS, (0x51B400, 0x51B330))
        self.assertEqual(SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA, 0x51A730)
        self.assertEqual(
            SCORE_COMPOSITE_MAIN_REGISTER_CALLS,
            (
                (0x51A825, "picture_control_constructor"),
                (0x51A8C1, "text_control_constructor"),
                (0x51A93C, "text_control_constructor"),
                (0x51A9D2, "text_control_constructor"),
                (0x51AA83, "text_control_constructor"),
            ),
        )
        self.assertEqual(SCORES_SUBPANEL_REGISTER_CALL_VA, 0x520DEF)
        self.assertEqual(TEAM_SUBPANEL_REGISTER_CALL_VA, 0x520EEF)

    def test_embedded_controls_and_direct_text_anchors(self):
        self.assertEqual(EMBEDDED_BUTTON0_PARENT_OFFSET, 0x388)
        self.assertEqual(EMBEDDED_BUTTON0_REGISTER_CALL_VA, 0x51FFE5)
        self.assertEqual(EMBEDDED_BUTTON0_CONSTRUCTOR_CALL_VA, 0x520061)
        self.assertEqual(EMBEDDED_BUTTON1_PARENT_OFFSET, 0x3D4)
        self.assertEqual(EMBEDDED_BUTTON1_REGISTER_CALL_VA, 0x52000B)
        self.assertEqual(EMBEDDED_BUTTON1_CONSTRUCTOR_CALL_VA, 0x52009F)
        self.assertEqual(EMBEDDED_BUTTON_CONSTRUCTOR_VA, 0x652FD0)
        self.assertEqual(DIRECT_TEXT0_REGISTER_CALL_VA, 0x520A16)
        self.assertEqual(DIRECT_TEXT0_RECT, (250, 45, 550, 75))
        self.assertEqual(DIRECT_TEXT1_REGISTER_CALL_VA, 0x520A69)
        self.assertEqual(DIRECT_TEXT1_RECT, (250, 70, 550, 86))

    def test_post_team_loop_appends_two_embedded_controls(self):
        self.assertEqual(POST_TEAM_CONTROL_ARRAY_PARENT_OFFSET, 0x424)
        self.assertEqual(POST_TEAM_CONTROL_STRIDE, 0x54)
        self.assertEqual(POST_TEAM_CONTROL_COUNT, 2)
        self.assertEqual(POST_TEAM_REGISTER_LOOP_CALL_VA, 0x520F8B)
        self.assertEqual(POST_TEAM_CONTROL_CONSTRUCTOR_VA, 0x652C50)
        rows = FASTVIEW_OUTER_DRAW_ENTRIES[-2:]
        self.assertEqual(
            tuple(row.parent_object_offset for row in rows),
            (0x424, 0x478),
        )
        self.assertEqual(
            tuple(row.registration_call_va for row in rows),
            (0x520F8B, 0x520F8B),
        )

    def test_outer_order_lookup_is_source_deterministic(self):
        self.assertTrue(outer_draw_before("clock_text", "scores_subpanel"))
        self.assertTrue(outer_draw_before("scores_subpanel", "team_subpanel"))
        self.assertTrue(outer_draw_before("team_subpanel", "post_team_control_0"))
        self.assertFalse(outer_draw_before("direct_text_1", "top_bar_picture"))
        self.assertEqual(outer_draw_rank("direct_text_0"), 30)
        with self.assertRaisesRegex(FastViewOuterDrawOrderError, "unknown"):
            outer_draw_rank("not_a_source_child")

    def test_outer_boundary_refuses_global_promotion(self):
        self.assertTrue(SOURCE_BOUNDARY.outer_draw_array_exhaustively_recovered)
        self.assertTrue(SOURCE_BOUNDARY.outer_forward_order_recovered)
        self.assertFalse(SOURCE_BOUNDARY.score_subpanel_internal_inventory_complete)
        self.assertFalse(SOURCE_BOUNDARY.team_subpanel_internal_inventory_complete)
        self.assertFalse(SOURCE_BOUNDARY.global_fastview_z_order_recovered)
        with self.assertRaisesRegex(
            FastViewOuterDrawOrderError,
            "cannot promote",
        ):
            replace(SOURCE_BOUNDARY, global_fastview_z_order_recovered=True)


if __name__ == "__main__":
    unittest.main()
