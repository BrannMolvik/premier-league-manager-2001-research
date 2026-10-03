"""Tests for the fail-closed FastView partial surface layout."""
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_background import BACKGROUND_BINDING_STATUS
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
from gate14_fastview_partial_surface import (
    FASTVIEW_SURFACE_SIZE,
    FastViewPartialSurfaceError,
    build_fastview_partial_surface_layout,
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


class FastViewPartialSurfaceTests(unittest.TestCase):
    def test_collects_only_exact_source_bound_regions_in_800x600_space(self):
        layout = build_fastview_partial_surface_layout(
            exact_chrome(),
            exact_possession(1),
            exact_figures(),
        )

        self.assertEqual(layout.size, FASTVIEW_SURFACE_SIZE)
        self.assertEqual(
            [(layer.component, layer.identity, layer.rect) for layer in layout.layers[:2]],
            [
                ("direct_chrome", "top_bar", (0, 0, 800, 95)),
                ("direct_chrome", "ticker", (0, 557, 800, 590)),
            ],
        )
        self.assertEqual(
            [layer.component for layer in layout.layers],
            [
                "direct_chrome",
                "direct_chrome",
                "possession_diagram",
                "possession_diagram",
                "possession_figures_text",
                "possession_figures_text",
                "possession_figures_text",
            ],
        )
        self.assertEqual(layout.background_binding_status, BACKGROUND_BINDING_STATUS)
        self.assertFalse(layout.cross_component_z_order_recovered)
        self.assertFalse(layout.raster_composition_available)
        self.assertFalse(layout.complete_fastview_frame_available)

    def test_detects_diagram_text_overlap_instead_of_guessing_draw_order(self):
        layout = build_fastview_partial_surface_layout(
            exact_chrome(),
            exact_possession(1),
            exact_figures(),
        )
        pairs = {
            (
                layout.layers[item.first_layer_index].identity,
                layout.layers[item.second_layer_index].identity,
                item.rect,
            )
            for item in layout.cross_component_overlaps
        }

        self.assertIn(("base_pitch:pitch_normal", "side1", (311, 181, 351, 199)), pairs)
        self.assertIn(("base_pitch:pitch_normal", "neutral", (382, 181, 422, 199)), pairs)
        self.assertIn(("base_pitch:pitch_normal", "side0", (454, 181, 494, 199)), pairs)
        self.assertIn(("active_overlay:pitch_middle", "neutral", (382, 181, 422, 199)), pairs)

    def test_bad_figure_origin_fails_closed(self):
        figures = exact_figures()
        first = figures.rows[0]
        broken = OriginalFastViewPossessionFiguresArt(
            (
                first.__class__(
                    source=first.source,
                    line_origin=(first.line_origin[0] + 1, first.line_origin[1]),
                    clip_rect=first.clip_rect,
                    native_color_16=first.native_color_16,
                    glyph_width=first.glyph_width,
                    glyph_height=first.glyph_height,
                    glyph_rgba=first.glyph_rgba,
                ),
                *figures.rows[1:],
            )
        )
        with self.assertRaisesRegex(FastViewPartialSurfaceError, "line origin"):
            build_fastview_partial_surface_layout(
                exact_chrome(),
                exact_possession(1),
                broken,
            )

    def test_wrong_component_types_fail_closed(self):
        with self.assertRaises(FastViewPartialSurfaceError):
            build_fastview_partial_surface_layout(
                object(),
                exact_possession(1),
                exact_figures(),
            )
        with self.assertRaises(FastViewPartialSurfaceError):
            build_fastview_partial_surface_layout(
                exact_chrome(),
                object(),
                exact_figures(),
            )
        with self.assertRaises(FastViewPartialSurfaceError):
            build_fastview_partial_surface_layout(
                exact_chrome(),
                exact_possession(1),
                object(),
            )


if __name__ == "__main__":
    unittest.main()
