"""Tests for source-closed partial FastView draw order."""
from dataclasses import replace
import unittest

from gate14_fastview_draw_order import (
    CHILD_RENDER_VIRTUAL_OFFSET,
    GENERIC_CHILD_RENDER_TARGET_VA,
    PARENT_DRAW_ARRAY_APPEND_HELPER_VA,
    PARENT_DRAW_ARRAY_COUNT_OFFSET,
    PARENT_DRAW_ARRAY_POINTER_OFFSET,
    PARENT_DRAW_ARRAY_REGISTER_VA,
    PARENT_DRAW_TRAVERSAL_VA,
    PICTURE_CONTROL_CONSTRUCTOR_VA,
    PICTURE_CONTROL_REGISTER_CALL_VA,
    POSSESSION_DIAGRAM_BEFORE_FIGURES,
    POSSESSION_DIAGRAM_CONSTRUCTOR_VA,
    POSSESSION_DIAGRAM_OWNER_CALL_VA,
    POSSESSION_FIGURES_CONSTRUCTOR_VA,
    POSSESSION_FIGURES_OWNER_CALL_VA,
    TEXT_CONTROL_CONSTRUCTOR_VA,
    TEXT_CONTROL_REGISTER_CALL_VA,
    FastViewDrawOrderError,
    later_component,
    source_closed_pairwise_order,
)


class FastViewDrawOrderTests(unittest.TestCase):
    def test_records_exact_registration_and_forward_traversal_chain(self):
        self.assertEqual(PARENT_DRAW_ARRAY_POINTER_OFFSET, 0x1C)
        self.assertEqual(PARENT_DRAW_ARRAY_COUNT_OFFSET, 0x38)
        self.assertEqual(PARENT_DRAW_ARRAY_REGISTER_VA, 0x5274C0)
        self.assertEqual(PARENT_DRAW_ARRAY_APPEND_HELPER_VA, 0x5275C0)
        self.assertEqual(PARENT_DRAW_TRAVERSAL_VA, 0x6533A0)
        self.assertEqual(CHILD_RENDER_VIRTUAL_OFFSET, 0x64)
        self.assertEqual(GENERIC_CHILD_RENDER_TARGET_VA, 0x64F6D0)

        self.assertEqual(PICTURE_CONTROL_CONSTRUCTOR_VA, 0x527730)
        self.assertEqual(PICTURE_CONTROL_REGISTER_CALL_VA, 0x52782A)
        self.assertEqual(TEXT_CONTROL_CONSTRUCTOR_VA, 0x527960)
        self.assertEqual(TEXT_CONTROL_REGISTER_CALL_VA, 0x527A15)

    def test_possession_figures_are_constructed_and_drawn_after_diagram(self):
        self.assertEqual(POSSESSION_DIAGRAM_OWNER_CALL_VA, 0x5206CD)
        self.assertEqual(POSSESSION_DIAGRAM_CONSTRUCTOR_VA, 0x5227D0)
        self.assertEqual(POSSESSION_FIGURES_OWNER_CALL_VA, 0x520802)
        self.assertEqual(POSSESSION_FIGURES_CONSTRUCTOR_VA, 0x51E7E0)
        self.assertLess(
            POSSESSION_DIAGRAM_OWNER_CALL_VA,
            POSSESSION_FIGURES_OWNER_CALL_VA,
        )

        relation = source_closed_pairwise_order(
            "possession_diagram",
            "possession_figures_text",
        )
        self.assertIs(relation, POSSESSION_DIAGRAM_BEFORE_FIGURES)
        self.assertEqual(relation.earlier_component, "possession_diagram")
        self.assertEqual(relation.later_component, "possession_figures_text")
        self.assertTrue(relation.same_parent_draw_array)
        self.assertTrue(relation.registration_is_append_order)
        self.assertTrue(relation.traversal_is_forward)
        self.assertFalse(relation.pixel_blend_rule_recovered)
        self.assertFalse(relation.global_z_order_recovered)

        # Lookup is symmetric, but the native result always stays earlier->later.
        reverse_lookup = source_closed_pairwise_order(
            "possession_figures_text",
            "possession_diagram",
        )
        self.assertIs(reverse_lookup, relation)
        self.assertEqual(
            later_component("possession_diagram", "possession_figures_text"),
            "possession_figures_text",
        )

    def test_unproven_pairs_fail_closed(self):
        for pair in (
            ("direct_chrome", "possession_diagram"),
            ("direct_chrome", "possession_figures_text"),
            ("team_table_static", "possession_figures_text"),
            ("league_scores_static", "league_table_static"),
        ):
            with self.subTest(pair=pair):
                with self.assertRaisesRegex(
                    FastViewDrawOrderError,
                    "remains unresolved",
                ):
                    source_closed_pairwise_order(*pair)

    def test_relation_cannot_promote_blend_or_global_order(self):
        with self.assertRaisesRegex(
            FastViewDrawOrderError,
            "cannot promote",
        ):
            replace(
                POSSESSION_DIAGRAM_BEFORE_FIGURES,
                pixel_blend_rule_recovered=True,
            )
        with self.assertRaisesRegex(
            FastViewDrawOrderError,
            "cannot promote",
        ):
            replace(
                POSSESSION_DIAGRAM_BEFORE_FIGURES,
                global_z_order_recovered=True,
            )


if __name__ == "__main__":
    unittest.main()
