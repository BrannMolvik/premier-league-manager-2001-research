"""Tests for fail-closed FastView unresolved-overlap readiness."""
from dataclasses import replace
from hashlib import sha256
import unittest

from gate14_fastview_overlap_readiness import (
    FastViewOverlapReadinessError,
    audit_fastview_overlap_readiness,
    classify_fastview_overlap_group,
)
from gate14_fastview_resolved_composite import (
    FastViewResolvedOnlyComposite,
    FastViewUnresolvedOverlapGroup,
)


PIXELS = 800 * 600


def composite(
    component_names,
    groups,
):
    rgba = bytes(PIXELS * 4)
    unresolved = sum(group.pixel_count for group in groups)
    mask = bytearray(PIXELS)
    mask[:unresolved] = b"\x01" * unresolved
    mask = bytes(mask)
    return FastViewResolvedOnlyComposite(
        size=(800, 600),
        rgba=rgba,
        unresolved_overlap_mask=mask,
        resolved_pixel_count=0,
        unresolved_overlap_pixel_count=unresolved,
        contributing_components=tuple(component_names),
        source_plane_sha256=tuple(
            (name, sha256(name.encode("utf-8")).hexdigest())
            for name in component_names
        ),
        unresolved_overlap_groups=tuple(groups),
        rgba_sha256=sha256(rgba).hexdigest(),
        unresolved_overlap_mask_sha256=sha256(mask).hexdigest(),
    )


class FastViewOverlapReadinessTests(unittest.TestCase):
    def test_known_possession_pair_is_blocked_only_by_cross_component_blend(self):
        group = FastViewUnresolvedOverlapGroup(
            components=("possession_diagram", "possession_figures_text"),
            pixel_count=17,
            bounding_rect=(311, 181, 494, 199),
        )
        item = classify_fastview_overlap_group(group)

        self.assertEqual(item.required_pairwise_relation_count, 1)
        self.assertEqual(item.recovered_pairwise_relation_count, 1)
        self.assertTrue(item.complete_draw_order_recovered)
        self.assertEqual(
            tuple(
                (relation.earlier_component, relation.later_component)
                for relation in item.recovered_pairwise_order
            ),
            (("possession_diagram", "possession_figures_text"),),
        )
        self.assertFalse(item.cross_component_blend_rule_recovered)
        self.assertFalse(item.pixels_resolvable)
        self.assertEqual(item.blockers, ("cross_component_blend_rule",))

    def test_direct_chrome_team_pair_is_now_order_resolved_but_blend_blocked(self):
        group = FastViewUnresolvedOverlapGroup(
            components=("direct_chrome", "team_table_static"),
            pixel_count=9,
            bounding_rect=(37, 27, 296, 43),
        )
        item = classify_fastview_overlap_group(group)

        self.assertEqual(item.required_pairwise_relation_count, 1)
        self.assertEqual(item.recovered_pairwise_relation_count, 1)
        self.assertTrue(item.complete_draw_order_recovered)
        self.assertEqual(
            tuple(
                (relation.earlier_component, relation.later_component)
                for relation in item.recovered_pairwise_order
            ),
            (("direct_chrome", "team_table_static"),),
        )
        self.assertEqual(item.blockers, ("cross_component_blend_rule",))
        self.assertFalse(item.pixels_resolvable)

    def test_score_table_aggregate_pair_keeps_draw_order_fail_closed(self):
        components = (
            "direct_chrome",
            "possession_diagram",
            "possession_figures_text",
            "league_table_static",
            "league_scores_static",
            "team_table_static",
        )
        group = FastViewUnresolvedOverlapGroup(
            components=components,
            pixel_count=4,
            bounding_rect=(37, 27, 763, 217),
        )
        item = classify_fastview_overlap_group(group)

        self.assertEqual(item.required_pairwise_relation_count, 15)
        self.assertEqual(item.recovered_pairwise_relation_count, 14)
        self.assertFalse(item.complete_draw_order_recovered)
        self.assertEqual(
            item.blockers,
            ("cross_component_draw_order", "cross_component_blend_rule"),
        )
        self.assertFalse(item.cross_component_blend_rule_recovered)
        self.assertFalse(item.pixels_resolvable)

    def test_phase_split_score_group_has_complete_source_order_but_stays_blend_blocked(self):
        components = (
            "league_scores_early_rows_static",
            "league_table_static",
            "league_scores_late_grid_static",
            "league_scores_runtime_phase_icons",
            "team_table_static",
        )
        group = FastViewUnresolvedOverlapGroup(
            components=components,
            pixel_count=6,
            bounding_rect=(38, 32, 763, 283),
        )
        item = classify_fastview_overlap_group(group)

        self.assertEqual(item.required_pairwise_relation_count, 10)
        self.assertEqual(item.recovered_pairwise_relation_count, 10)
        self.assertTrue(item.complete_draw_order_recovered)
        self.assertEqual(item.blockers, ("cross_component_blend_rule",))
        self.assertFalse(item.cross_component_blend_rule_recovered)
        self.assertFalse(item.pixels_resolvable)
        self.assertEqual(
            tuple(
                (relation.earlier_component, relation.later_component)
                for relation in item.recovered_pairwise_order
            )[-1],
            ("league_scores_runtime_phase_icons", "team_table_static"),
        )

    def test_runtime_icon_text_group_keeps_only_their_aggregate_order_unresolved(self):
        components = (
            "league_scores_early_rows_static",
            "league_table_static",
            "league_scores_late_grid_static",
            "league_scores_runtime_phase_icons",
            "league_scores_runtime_phase_text",
            "team_table_static",
        )
        group = FastViewUnresolvedOverlapGroup(
            components=components,
            pixel_count=3,
            bounding_rect=(349, 55, 377, 128),
        )
        item = classify_fastview_overlap_group(group)

        self.assertEqual(item.required_pairwise_relation_count, 15)
        self.assertEqual(item.recovered_pairwise_relation_count, 14)
        self.assertFalse(item.complete_draw_order_recovered)
        self.assertEqual(
            item.blockers,
            ("cross_component_draw_order", "cross_component_blend_rule"),
        )
        recovered = {
            (relation.earlier_component, relation.later_component)
            for relation in item.recovered_pairwise_order
        }
        self.assertNotIn(
            (
                "league_scores_runtime_phase_icons",
                "league_scores_runtime_phase_text",
            ),
            recovered,
        )
        self.assertIn(
            (
                "league_scores_late_grid_static",
                "league_scores_runtime_phase_text",
            ),
            recovered,
        )
        self.assertIn(
            (
                "league_scores_runtime_phase_text",
                "team_table_static",
            ),
            recovered,
        )
        self.assertFalse(item.pixels_resolvable)

    def test_unmodeled_component_retains_draw_order_blocker(self):
        group = FastViewUnresolvedOverlapGroup(
            components=(
                "direct_chrome",
                "possession_diagram",
                "unmodeled_fastview_layer",
            ),
            pixel_count=4,
            bounding_rect=(0, 0, 350, 217),
        )
        item = classify_fastview_overlap_group(group)

        self.assertEqual(item.required_pairwise_relation_count, 3)
        self.assertEqual(item.recovered_pairwise_relation_count, 1)
        self.assertFalse(item.complete_draw_order_recovered)
        self.assertEqual(
            tuple(
                (relation.earlier_component, relation.later_component)
                for relation in item.recovered_pairwise_order
            ),
            (("direct_chrome", "possession_diagram"),),
        )
        self.assertEqual(
            item.blockers,
            ("cross_component_draw_order", "cross_component_blend_rule"),
        )

    def test_audit_partitions_known_and_unmodeled_pixels_without_unmasking(self):
        ordered = FastViewUnresolvedOverlapGroup(
            components=("direct_chrome", "team_table_energy"),
            pixel_count=7,
            bounding_rect=(37, 27, 491, 43),
        )
        unknown = FastViewUnresolvedOverlapGroup(
            components=("direct_chrome", "unmodeled_fastview_layer"),
            pixel_count=5,
            bounding_rect=(0, 0, 100, 10),
        )
        source = composite(
            (
                "direct_chrome",
                "team_table_energy",
                "unmodeled_fastview_layer",
            ),
            (ordered, unknown),
        )

        audit = audit_fastview_overlap_readiness(source)

        self.assertEqual(audit.unresolved_overlap_pixel_count, 12)
        self.assertEqual(audit.draw_order_resolved_overlap_pixel_count, 7)
        self.assertEqual(audit.draw_order_unresolved_overlap_pixel_count, 5)
        self.assertEqual(audit.blend_unresolved_overlap_pixel_count, 12)
        self.assertEqual(audit.raster_resolvable_overlap_pixel_count, 0)
        self.assertEqual(audit.source_composite_rgba_sha256, source.rgba_sha256)
        self.assertEqual(
            audit.source_overlap_mask_sha256,
            source.unresolved_overlap_mask_sha256,
        )
        self.assertFalse(audit.cross_component_blend_rule_recovered)
        self.assertFalse(audit.all_overlap_pixels_resolvable)
        self.assertFalse(audit.complete_fastview_frame)

    def test_zero_overlap_composite_is_valid_but_does_not_promote_frame(self):
        source = composite(
            (
                "direct_chrome",
                "possession_diagram",
                "possession_figures_text",
            ),
            (),
        )
        audit = audit_fastview_overlap_readiness(source)

        self.assertEqual(audit.unresolved_overlap_pixel_count, 0)
        self.assertEqual(audit.groups, ())
        self.assertEqual(audit.raster_resolvable_overlap_pixel_count, 0)
        self.assertFalse(audit.complete_fastview_frame)

    def test_audit_and_group_records_reject_false_fidelity_promotion(self):
        group = FastViewUnresolvedOverlapGroup(
            components=("possession_diagram", "possession_figures_text"),
            pixel_count=2,
            bounding_rect=(311, 181, 313, 182),
        )
        item = classify_fastview_overlap_group(group)
        with self.assertRaisesRegex(
            FastViewOverlapReadinessError,
            "cannot promote",
        ):
            replace(item, cross_component_blend_rule_recovered=True)

        source = composite(
            ("possession_diagram", "possession_figures_text"),
            (group,),
        )
        audit = audit_fastview_overlap_readiness(source)
        with self.assertRaisesRegex(
            FastViewOverlapReadinessError,
            "cannot promote",
        ):
            replace(audit, complete_fastview_frame=True)
        with self.assertRaisesRegex(
            FastViewOverlapReadinessError,
            "no current unresolved overlap pixels may be promoted",
        ):
            replace(audit, raster_resolvable_overlap_pixel_count=1)

    def test_requires_exact_source_types(self):
        with self.assertRaisesRegex(
            FastViewOverlapReadinessError,
            "exact FastViewResolvedOnlyComposite",
        ):
            audit_fastview_overlap_readiness(object())
        with self.assertRaisesRegex(
            FastViewOverlapReadinessError,
            "exact compositor overlap groups",
        ):
            classify_fastview_overlap_group(object())


if __name__ == "__main__":
    unittest.main()
