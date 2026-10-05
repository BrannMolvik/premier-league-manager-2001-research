"""Tests for the fail-closed outer ScoreCompositeMain source contract."""
import unittest

from gate14_fastview_outer_draw_order import (
    SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA,
    SCORE_COMPOSITE_MAIN_CONSTRUCTORS,
    SCORE_COMPOSITE_MAIN_OWNER_CALL_VAS,
    SCORE_COMPOSITE_MAIN_REGISTER_CALLS,
    outer_draw_rank,
)
from gate14_fastview_scorecomposite_main_source import (
    SCORE_COMPOSITE_MAIN_BRANCHES,
    SCORE_COMPOSITE_MAIN_CONTROL_IDENTITIES,
    SCORE_COMPOSITE_MAIN_CONTROL_KINDS,
    SCORE_COMPOSITE_MAIN_INSTANCE_COUNT,
    SOURCE_BRANCHES,
    FastViewScoreCompositeMainSourceError,
    scorecomposite_main_branch,
    scorecomposite_main_outer_ranks,
    scorecomposite_main_source_contract,
)


class FastViewScoreCompositeMainSourceTests(unittest.TestCase):
    def test_exact_one_instance_three_branch_topology(self):
        self.assertEqual(SCORE_COMPOSITE_MAIN_INSTANCE_COUNT, 1)
        self.assertEqual(
            SCORE_COMPOSITE_MAIN_OWNER_CALL_VAS,
            (0x520356, 0x520416, 0x5204D6),
        )
        self.assertEqual(
            SCORE_COMPOSITE_MAIN_CONSTRUCTORS,
            (0x51B400, 0x51B330),
        )
        self.assertEqual(
            SCORE_COMPOSITE_MAIN_BRANCHES,
            (
                (0x520356, 0x51B400),
                (0x520416, 0x51B330),
                (0x5204D6, 0x51B330),
            ),
        )
        self.assertEqual(SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA, 0x51A730)
        self.assertEqual(
            tuple((b.owner_call_va, b.constructor_va) for b in SOURCE_BRANCHES),
            SCORE_COMPOSITE_MAIN_BRANCHES,
        )

    def test_owner_branch_resolution_is_exact_and_does_not_infer_selector(self):
        self.assertEqual(
            scorecomposite_main_branch(0x520356).constructor_va,
            0x51B400,
        )
        self.assertEqual(
            scorecomposite_main_branch(0x520416).constructor_va,
            0x51B330,
        )
        self.assertEqual(
            scorecomposite_main_branch(0x5204D6).constructor_va,
            0x51B330,
        )
        for value in (0x520355, 0x520357, -1, True, "0x520356"):
            with self.subTest(value=value):
                with self.assertRaises(FastViewScoreCompositeMainSourceError):
                    scorecomposite_main_branch(value)

    def test_five_outer_controls_keep_exact_builder_order(self):
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
        self.assertEqual(
            SCORE_COMPOSITE_MAIN_CONTROL_KINDS,
            tuple(kind for _va, kind in SCORE_COMPOSITE_MAIN_REGISTER_CALLS),
        )
        self.assertEqual(
            SCORE_COMPOSITE_MAIN_CONTROL_IDENTITIES,
            tuple(f"score_composite_main_control_{i}" for i in range(5)),
        )

    def test_outer_ranks_are_contiguous_between_goalflash_and_surfaced_badge(self):
        self.assertEqual(scorecomposite_main_outer_ranks(), (16, 17, 18, 19, 20))
        self.assertEqual(outer_draw_rank("goal_flash_1_text_4"), 15)
        self.assertEqual(outer_draw_rank("surfaced_picture_control_1"), 21)

    def test_contract_promotes_topology_only(self):
        contract = scorecomposite_main_source_contract()
        self.assertEqual(contract["instance_count"], 1)
        self.assertEqual(contract["outer_draw_ranks"], (16, 17, 18, 19, 20))
        self.assertEqual(
            contract["control_kinds"],
            (
                "picture_control_constructor",
                "text_control_constructor",
                "text_control_constructor",
                "text_control_constructor",
                "text_control_constructor",
            ),
        )
        self.assertFalse(contract["branch_selector_semantics_recovered"])
        self.assertFalse(contract["control_geometry_recovered"])
        self.assertFalse(contract["runtime_content_semantics_recovered"])
        self.assertFalse(contract["resource_identity_recovered"])
        self.assertFalse(contract["absolute_position_recovered"])
        self.assertFalse(contract["pixels_rasterized"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
