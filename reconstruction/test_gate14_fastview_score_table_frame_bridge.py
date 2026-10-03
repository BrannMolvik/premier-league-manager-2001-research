"""Focused bridge tests for optional FastView score/table frame-plan rasters."""
from hashlib import sha256
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastview_semantic_shell import FastViewSemanticShell
from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
)
from gate14_fastview_frame_plan import build_fastview_frame_plan
from gate14_fastview_human_frame_plan import build_human_fastview_frame_plan


def component_plane(component: str, value: int) -> FastViewComponentRasterPlane:
    rgba = bytes((value, value, value, 255)) * (800 * 600)
    return FastViewComponentRasterPlane(
        component=component,
        size=(800, 600),
        rgba=rgba,
        source_layer_count=1,
        rgba_sha256=sha256(rgba).hexdigest(),
    )


def base_component_set() -> FastViewComponentRasterSet:
    return FastViewComponentRasterSet(
        chrome=component_plane("direct_chrome", 1),
        possession_diagram=component_plane("possession_diagram", 2),
        possession_figures=component_plane("possession_figures_text", 3),
    )


class FastViewScoreTableFrameBridgeTests(unittest.TestCase):
    def test_frame_plan_forwards_explicit_bundle_without_deriving_counts(self):
        shell = FastViewSemanticShell(
            match_reference=23,
            events=(),
            possession_figures=(),
            final_score=(0, 0),
            player_rows=(),
            player_row_render_plans=(),
        )
        chrome = object()
        possession = object()
        figures = object()
        team_art = object()
        score_table = object()
        surface = SimpleNamespace(
            raster_composition_available=False,
            complete_fastview_frame_available=False,
        )
        team_static = object()
        components = base_component_set()

        with (
            patch(
                "gate14_fastview_frame_plan.build_fastview_partial_surface_from_render_plans",
                return_value=surface,
            ) as build_surface,
            patch(
                "gate14_fastview_frame_plan.rasterize_fastview_team_static_rows",
                return_value=team_static,
            ) as raster_team,
            patch(
                "gate14_fastview_frame_plan.build_fastview_component_rasters",
                return_value=components,
            ) as build_components,
        ):
            frame = build_fastview_frame_plan(
                shell,
                chrome,
                possession,
                figures,
                team_art,
                score_table_static=score_table,
            )

        self.assertIs(frame.component_rasters, components)
        build_surface.assert_called_once_with(
            chrome,
            possession,
            figures,
            render_plans=(),
        )
        raster_team.assert_called_once_with(team_art, ())
        build_components.assert_called_once_with(
            chrome,
            possession,
            figures,
            team_static,
            score_table=score_table,
        )

    def test_human_adapter_only_forwards_bundle_and_does_not_infer_context(self):
        outcome = object()
        presentation = object()
        shell = object()
        frame = object()
        chrome = object()
        possession = object()
        figures = object()
        team_art = object()
        score_table = object()

        with (
            patch(
                "gate14_fastview_human_frame_plan.build_human_match_presentation",
                return_value=presentation,
            ) as build_presentation,
            patch(
                "gate14_fastview_human_frame_plan.build_fastview_semantic_shell",
                return_value=shell,
            ) as build_shell,
            patch(
                "gate14_fastview_human_frame_plan.build_fastview_frame_plan",
                return_value=frame,
            ) as build_frame,
        ):
            result = build_human_fastview_frame_plan(
                outcome,
                chrome,
                possession,
                figures,
                team_art,
                score_table_static=score_table,
            )

        self.assertIs(result, frame)
        build_presentation.assert_called_once_with(outcome)
        build_shell.assert_called_once_with(presentation)
        build_frame.assert_called_once_with(
            shell,
            chrome,
            possession,
            figures,
            team_art,
            score_table_static=score_table,
        )


if __name__ == "__main__":
    unittest.main()
