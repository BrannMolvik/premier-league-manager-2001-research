"""Tests for source-closed partial FastView draw order."""
from dataclasses import replace
import unittest

from gate14_fastview_draw_order import (
    CHILD_RENDER_VIRTUAL_OFFSET,
    FASTVIEW_SCORES_OBJECT_OFFSET,
    FASTVIEW_SCORES_SUBPANEL_OFFSET,
    FASTVIEW_SCORES_SUBPANEL_REGISTER_CALL_VA,
    FASTVIEW_TEAM_CONSTRUCTOR_VA,
    FASTVIEW_TEAM_OBJECT_OFFSET,
    FASTVIEW_TEAM_OWNER_CALL_VA,
    FASTVIEW_TEAM_SUBPANEL_OFFSET,
    FASTVIEW_TEAM_SUBPANEL_REGISTER_CALL_VA,
    GENERIC_CHILD_RENDER_TARGET_VA,
    FASTVIEW_LEAGUE_SCORES_SETUP_VA,
    FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA,
    FASTVIEW_SCORE_ENTRY_BUILDER_VA,
    FASTVIEW_SCORE_FACTORY_VTABLE_SLOT,
    FASTVIEW_SCORE_FACTORY_VA,
    LEAGUE_SCORES_TITLE_BAR_22_PICTURE_CALLSITE_VA,
    LEAGUE_SCORES_CURRENT_FIX_GRID_1_PICTURE_CALLSITE_VA,
    LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA,
    LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA,
    LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA,
    LEAGUE_TABLE_ROW_CONSTRUCTOR_VA,
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
    SOURCE_CLOSED_RASTER_COMPONENT_ORDER_LEVELS,
    SOURCE_CLOSED_SCORE_PHASE_ORDER_LEVELS,
    SUBPANEL_CONTROL_RENDER_VA,
    SUBPANEL_CONTROL_TARGET_PANEL_OFFSET,
    SUBPANEL_CONTROL_TRAVERSAL_CALL_VA,
    SUBPANEL_CONTROL_VTABLE_VA,
    TEXT_CONTROL_CONSTRUCTOR_VA,
    TEXT_CONTROL_REGISTER_CALL_VA,
    TICKER_PICTURE_CALL_VA,
    TOP_BAR_PICTURE_CALL_VA,
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
        self.assertFalse(relation.nested_subpanel_bridge_recovered)
        self.assertFalse(relation.pixel_blend_rule_recovered)
        self.assertFalse(relation.global_z_order_recovered)

        reverse_lookup = source_closed_pairwise_order(
            "possession_figures_text",
            "possession_diagram",
        )
        self.assertIs(reverse_lookup, relation)
        self.assertEqual(
            later_component("possession_diagram", "possession_figures_text"),
            "possession_figures_text",
        )

    def test_records_subpanel_bridge_for_score_then_team_subtrees(self):
        self.assertEqual(SUBPANEL_CONTROL_VTABLE_VA, 0x7CA5E4)
        self.assertEqual(SUBPANEL_CONTROL_TARGET_PANEL_OFFSET, 0x2C)
        self.assertEqual(SUBPANEL_CONTROL_RENDER_VA, 0x650BB0)
        self.assertEqual(SUBPANEL_CONTROL_TRAVERSAL_CALL_VA, 0x650BFF)

        self.assertEqual(FASTVIEW_SCORES_OBJECT_OFFSET, 0x90)
        self.assertEqual(FASTVIEW_SCORES_SUBPANEL_REGISTER_CALL_VA, 0x520DEF)
        self.assertEqual(FASTVIEW_SCORES_SUBPANEL_OFFSET, 0x98)
        self.assertEqual(FASTVIEW_TEAM_OBJECT_OFFSET, 0x94)
        self.assertEqual(FASTVIEW_TEAM_OWNER_CALL_VA, 0x520E67)
        self.assertEqual(FASTVIEW_TEAM_CONSTRUCTOR_VA, 0x524920)
        self.assertEqual(FASTVIEW_TEAM_SUBPANEL_REGISTER_CALL_VA, 0x520EEF)
        self.assertEqual(FASTVIEW_TEAM_SUBPANEL_OFFSET, 0x9C)
        self.assertLess(
            FASTVIEW_SCORES_SUBPANEL_REGISTER_CALL_VA,
            FASTVIEW_TEAM_SUBPANEL_REGISTER_CALL_VA,
        )

        relation = source_closed_pairwise_order(
            "league_scores_static",
            "team_table_static",
        )
        self.assertFalse(relation.same_parent_draw_array)
        self.assertTrue(relation.nested_subpanel_bridge_recovered)
        self.assertEqual(relation.earlier_component, "league_scores_static")
        self.assertEqual(relation.later_component, "team_table_static")

    def test_aggregate_score_and_table_planes_have_no_false_pairwise_edge(self):
        self.assertEqual(FASTVIEW_LEAGUE_SCORES_SETUP_VA, 0x523370)
        self.assertEqual(FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA, 0x5233C2)
        self.assertEqual(FASTVIEW_SCORE_ENTRY_BUILDER_VA, 0x522CD0)
        self.assertEqual(FASTVIEW_SCORE_FACTORY_VTABLE_SLOT, 0x5C)
        self.assertEqual(FASTVIEW_SCORE_FACTORY_VA, 0x523CC0)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA, 0x523472)
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA, 0x51E000)
        self.assertEqual(LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA, 0x51DCB0)
        self.assertEqual(LEAGUE_TABLE_ROW_CONSTRUCTOR_VA, 0x51D730)
        self.assertEqual(LEAGUE_SCORES_TITLE_BAR_22_PICTURE_CALLSITE_VA, 0x523554)
        self.assertEqual(
            LEAGUE_SCORES_CURRENT_FIX_GRID_1_PICTURE_CALLSITE_VA,
            0x5239F3,
        )
        self.assertLess(
            FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA,
            LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA,
        )
        self.assertLess(
            LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA,
            LEAGUE_SCORES_CURRENT_FIX_GRID_1_PICTURE_CALLSITE_VA,
        )
        with self.assertRaisesRegex(FastViewDrawOrderError, "remains unresolved"):
            source_closed_pairwise_order(
                "league_table_static",
                "league_scores_static",
            )

    def test_current_raster_families_have_source_closed_partial_relative_order(self):
        expected_levels = (
            ("direct_chrome",),
            ("possession_diagram",),
            ("possession_figures_text",),
            ("league_scores_static", "league_table_static"),
            ("team_table_static", "team_table_energy"),
        )
        self.assertEqual(SOURCE_CLOSED_RASTER_COMPONENT_ORDER_LEVELS, expected_levels)

        for score_component in ("league_scores_static", "league_table_static"):
            relation = source_closed_pairwise_order(
                "possession_figures_text",
                score_component,
            )
            self.assertEqual(relation.earlier_component, "possession_figures_text")
            self.assertEqual(relation.later_component, score_component)
            relation = source_closed_pairwise_order(
                score_component,
                "team_table_static",
            )
            self.assertEqual(relation.earlier_component, score_component)
            self.assertEqual(relation.later_component, "team_table_static")

        self.assertEqual(
            later_component("direct_chrome", "team_table_energy"),
            "team_table_energy",
        )
        self.assertEqual(
            later_component("league_table_static", "team_table_energy"),
            "team_table_energy",
        )

    def test_phase_specific_score_planes_restore_precise_partial_order(self):
        self.assertEqual(
            SOURCE_CLOSED_SCORE_PHASE_ORDER_LEVELS,
            (
                ("direct_chrome",),
                ("possession_diagram",),
                ("possession_figures_text",),
                ("league_scores_early_rows_static",),
                ("league_table_static",),
                ("league_scores_late_grid_static",),
                ("league_scores_runtime_phase_icons",),
                ("team_table_static", "team_table_energy"),
            ),
        )
        chain = (
            "league_scores_early_rows_static",
            "league_table_static",
            "league_scores_late_grid_static",
            "league_scores_runtime_phase_icons",
            "team_table_static",
        )
        for earlier, later in zip(chain, chain[1:]):
            with self.subTest(earlier=earlier, later=later):
                relation = source_closed_pairwise_order(earlier, later)
                self.assertEqual(relation.earlier_component, earlier)
                self.assertEqual(relation.later_component, later)
                self.assertTrue(relation.traversal_is_forward)

        # The aggregate compatibility plane stays intentionally unordered
        # against LeagueTable even though the phase-specific planes are precise.
        with self.assertRaisesRegex(FastViewDrawOrderError, "remains unresolved"):
            source_closed_pairwise_order(
                "league_scores_static",
                "league_table_static",
            )

    def test_direct_chrome_is_source_earlier_than_nested_score_and_team_subtrees(self):
        self.assertLess(TOP_BAR_PICTURE_CALL_VA, POSSESSION_DIAGRAM_OWNER_CALL_VA)
        self.assertLess(TICKER_PICTURE_CALL_VA, POSSESSION_DIAGRAM_OWNER_CALL_VA)
        for later in (
            "league_table_static",
            "league_scores_static",
            "team_table_static",
            "team_table_energy",
        ):
            relation = source_closed_pairwise_order("direct_chrome", later)
            self.assertTrue(relation.nested_subpanel_bridge_recovered)
            self.assertFalse(relation.same_parent_draw_array)

    def test_unmodeled_or_alias_pairs_fail_closed(self):
        for pair in (
            ("team_table_static", "team_table_energy"),
            ("direct_chrome", "unmodeled_fastview_layer"),
            ("league_scores_static", "unmodeled_fastview_layer"),
            ("direct_chrome", "direct_chrome"),
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
