"""Tests for the immutable Gate-14 FastView frame plan."""
from dataclasses import replace
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from fastview_semantic_shell import FastViewSemanticShell
from gate14_fastview_frame_plan import (
    FastViewFramePlanError,
    build_fastview_frame_plan,
)
from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_render_plan,
    build_fastview_player_row_snapshot,
)
from gate14_possession_figures import possession_figures_text_layout
from original_fastview_chrome_art import build_fastview_chrome_art
from original_fastview_possession_art import build_fastview_possession_art
from original_fastview_possession_figures_art import (
    OriginalFastViewPossessionFigureTextArt,
    OriginalFastViewPossessionFiguresArt,
)
from original_fastview_possession_resources import (
    FASTVIEW_POSSESSION_DIAGRAM_RESOURCES,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


def exact_chrome():
    return build_fastview_chrome_art(
        {
            "top_bar": image(800, 95, 1),
            "ticker": image(800, 33, 2),
        }
    )


def exact_possession(state=1):
    decoded = {
        resource.name: image(*resource.size, index + 3)
        for index, resource in enumerate(FASTVIEW_POSSESSION_DIAGRAM_RESOURCES)
    }
    return build_fastview_possession_art(decoded, state)


def exact_figures(side0=45, neutral=20):
    rows = []
    for source in possession_figures_text_layout(side0, neutral):
        rows.append(
            OriginalFastViewPossessionFigureTextArt(
                source=source,
                line_origin=source.rect[:2],
                clip_rect=source.rect,
                native_color_16=0xFFFF,
                glyph_width=1,
                glyph_height=1,
                glyph_rgba=b"\xff\xff\xff\xff",
            )
        )
    return OriginalFastViewPossessionFiguresArt(tuple(rows))


def row_snapshot():
    return build_fastview_player_row_snapshot(
        side_index=0,
        row_index=0,
        shirt_number=9,
        source_position_code=19,
        surname="Striker",
        first_name_initial="A",
        form_value=4,
        energy_value=79,
    )


def exact_shell():
    row = row_snapshot()
    plan = build_fastview_player_row_render_plan(row)
    return FastViewSemanticShell(
        match_reference=23,
        events=(),
        possession_figures=(),
        final_score=(1, 0),
        player_rows=(row,),
        player_row_render_plans=(plan,),
    )


class FastViewFramePlanTests(unittest.TestCase):
    def test_composes_shell_render_plans_and_partial_surface_without_promotion(self):
        shell = exact_shell()
        frame = build_fastview_frame_plan(
            shell,
            exact_chrome(),
            exact_possession(),
            exact_figures(),
        )

        self.assertEqual(frame.match_reference, 23)
        self.assertIs(frame.semantic_shell, shell)
        self.assertIs(frame.player_row_render_plans, shell.player_row_render_plans)
        self.assertEqual(frame.surface_layout.size, (800, 600))
        team_layers = [
            layer
            for layer in frame.surface_layout.layers
            if layer.component == "team_table_geometry"
        ]
        self.assertEqual(len(team_layers), 8)
        self.assertEqual(
            team_layers[0].identity,
            "side0:row0:name_grid:team_name_grid",
        )
        self.assertFalse(frame.complete_raster_frame)
        self.assertFalse(frame.audio_ready)
        self.assertFalse(frame.choreography_3d_ready)
        self.assertFalse(frame.surface_layout.raster_composition_available)
        self.assertFalse(frame.surface_layout.complete_fastview_frame_available)

    def test_rejects_shell_snapshot_render_plan_count_or_content_drift(self):
        shell = exact_shell()

        with self.assertRaisesRegex(FastViewFramePlanError, "counts differ"):
            build_fastview_frame_plan(
                replace(shell, player_row_render_plans=()),
                exact_chrome(),
                exact_possession(),
                exact_figures(),
            )

        drifted_plan = replace(
            shell.player_row_render_plans[0],
            energy_dynamic_rect=(309, 27, 350, 43),
        )
        with self.assertRaisesRegex(FastViewFramePlanError, "drifted"):
            build_fastview_frame_plan(
                replace(shell, player_row_render_plans=(drifted_plan,)),
                exact_chrome(),
                exact_possession(),
                exact_figures(),
            )

    def test_requires_exact_semantic_shell(self):
        with self.assertRaisesRegex(FastViewFramePlanError, "exact FastViewSemanticShell"):
            build_fastview_frame_plan(
                object(),
                exact_chrome(),
                exact_possession(),
                exact_figures(),
            )

    def test_frame_plan_module_does_not_import_gameplay_rng_audio_or_commentary(self):
        source = Path(__file__).with_name(
            "gate14_fastview_frame_plan.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "human_gameplay",
            "gameplay_controller",
            "random",
            "sound_effect",
            "commentary_text",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
