"""Tests for source-backed separate FastView component raster planes."""
from dataclasses import replace
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_component_rasters import (
    FastViewComponentRasterError,
    build_fastview_component_rasters,
    rasterize_fastview_chrome_plane,
    rasterize_fastview_possession_figures_plane,
    rasterize_fastview_possession_plane,
    rasterize_fastview_team_table_plane,
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
from gate14_fastview_team_static_raster import FastViewTeamStaticRaster
from gate14_fastview_score_table_static_raster import (
    FastViewScoreTableStaticPlane,
    FastViewScoreTableStaticRasterSet,
)
from hashlib import sha256


def image(width, height, rgba):
    pixel = bytes(rgba)
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=pixel * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


def chrome():
    return build_fastview_chrome_art(
        {
            "top_bar": image(800, 95, (10, 20, 30, 255)),
            "ticker": image(800, 33, (40, 50, 60, 255)),
        }
    )


def possession(state=1):
    decoded = {}
    for index, resource in enumerate(FASTVIEW_POSSESSION_DIAGRAM_RESOURCES):
        decoded[resource.name] = image(
            *resource.size,
            (70 + index, 80 + index, 90 + index, 255),
        )
    return build_fastview_possession_art(decoded, state)


def figures():
    rows = []
    for index, source in enumerate(possession_figures_text_layout(45, 20)):
        rows.append(
            OriginalFastViewPossessionFigureTextArt(
                source=source,
                line_origin=source.rect[:2],
                clip_rect=source.rect,
                native_color_16=0xFFFF,
                glyph_width=2,
                glyph_height=1,
                glyph_rgba=bytes((100 + index, 110, 120, 255)) * 2,
            )
        )
    return OriginalFastViewPossessionFiguresArt(tuple(rows))



def score_table_rasters():
    rgba_a = bytes((11, 12, 13, 255)) * (800 * 600)
    rgba_b = bytes((21, 22, 23, 255)) * (800 * 600)
    return FastViewScoreTableStaticRasterSet(
        league_scores=FastViewScoreTableStaticPlane(
            component="league_scores_static",
            size=(800, 600),
            rgba=rgba_a,
            source_layer_count=2,
            rgba_sha256=sha256(rgba_a).hexdigest(),
        ),
        league_table=FastViewScoreTableStaticPlane(
            component="league_table_static",
            size=(800, 600),
            rgba=rgba_b,
            source_layer_count=3,
            rgba_sha256=sha256(rgba_b).hexdigest(),
        ),
    )

def pixel(plane, x, y):
    offset = (y * 800 + x) * 4
    return tuple(plane.rgba[offset:offset + 4])


class FastViewComponentRasterTests(unittest.TestCase):
    def test_chrome_plane_places_only_direct_source_chrome(self):
        plane = rasterize_fastview_chrome_plane(chrome())
        self.assertEqual(plane.component, "direct_chrome")
        self.assertEqual(plane.size, (800, 600))
        self.assertEqual(plane.source_layer_count, 2)
        self.assertEqual(pixel(plane, 0, 0), (10, 20, 30, 255))
        self.assertEqual(pixel(plane, 799, 94), (10, 20, 30, 255))
        self.assertEqual(pixel(plane, 0, 556), (0, 0, 0, 0))
        self.assertEqual(pixel(plane, 0, 557), (40, 50, 60, 255))
        self.assertEqual(pixel(plane, 799, 589), (40, 50, 60, 255))
        self.assertEqual(pixel(plane, 0, 590), (0, 0, 0, 0))
        self.assertFalse(plane.complete_fastview_frame)

    def test_possession_plane_preserves_internal_base_then_overlay_order(self):
        art = possession(state=0)
        plane = rasterize_fastview_possession_plane(art)
        self.assertEqual(plane.component, "possession_diagram")
        self.assertEqual(plane.source_layer_count, len(art.placements))

        base = art.placements[0]
        overlay = art.placements[1]

        # State 0's left overlay begins at the base pitch's top-left, so that
        # pixel must show the later overlay. Check an uncovered base pixel
        # separately, then assert the overlap itself preserves overlay order.
        self.assertEqual(
            pixel(plane, base.x + base.width - 1, base.y),
            tuple(base.rgba[:4]),
        )
        self.assertEqual(
            pixel(plane, overlay.x, overlay.y),
            tuple(overlay.rgba[:4]),
        )

    def test_possession_figures_plane_uses_glyph_bounds_not_full_control_box(self):
        art = figures()
        plane = rasterize_fastview_possession_figures_plane(art)
        self.assertEqual(plane.component, "possession_figures_text")
        self.assertEqual(plane.source_layer_count, 3)

        first = art.rows[0]
        x, y = first.line_origin
        self.assertEqual(pixel(plane, x, y), tuple(first.glyph_rgba[:4]))
        self.assertEqual(pixel(plane, x + 1, y), tuple(first.glyph_rgba[4:8]))
        self.assertEqual(pixel(plane, x + 2, y), (0, 0, 0, 0))
        self.assertEqual(pixel(plane, first.clip_rect[2] - 1, y), (0, 0, 0, 0))

    def test_team_table_plane_accepts_verified_static_raster_including_empty_rows(self):
        rgba = bytes(800 * 600 * 4)
        static = FastViewTeamStaticRaster(
            size=(800, 600),
            rgba=rgba,
            row_identities=(),
            source_layer_count=0,
            rgba_sha256=sha256(rgba).hexdigest(),
        )
        plane = rasterize_fastview_team_table_plane(static)
        self.assertEqual(plane.component, "team_table_static")
        self.assertEqual(plane.source_layer_count, 0)
        self.assertEqual(plane.rgba, rgba)
        self.assertFalse(plane.complete_fastview_frame)

    def test_score_and_table_static_planes_lift_as_verified_pair(self):
        source = score_table_rasters()
        rasters = build_fastview_component_rasters(
            chrome(),
            possession(),
            figures(),
            score_table=source,
        )
        self.assertIsNotNone(rasters.league_scores)
        self.assertIsNotNone(rasters.league_table)
        self.assertEqual(rasters.league_scores.component, "league_scores_static")
        self.assertEqual(rasters.league_table.component, "league_table_static")
        self.assertEqual(
            rasters.league_scores.rgba_sha256,
            source.league_scores.rgba_sha256,
        )
        self.assertEqual(
            rasters.league_table.rgba_sha256,
            source.league_table.rgba_sha256,
        )
        self.assertFalse(rasters.cross_component_z_order_recovered)
        self.assertFalse(rasters.flattened_frame_available)

    def test_score_table_bundle_fails_closed_on_wrong_type_or_partial_pair(self):
        with self.assertRaisesRegex(
            FastViewComponentRasterError,
            "score_table must be exact",
        ):
            build_fastview_component_rasters(
                chrome(),
                possession(),
                figures(),
                score_table=object(),
            )

        source = score_table_rasters()
        rasters = build_fastview_component_rasters(
            chrome(),
            possession(),
            figures(),
            score_table=source,
        )
        with self.assertRaisesRegex(
            FastViewComponentRasterError,
            "supplied as one verified pair",
        ):
            replace(rasters, league_table=None)

    def test_component_set_remains_unflattened_and_has_no_cross_component_order(self):
        rasters = build_fastview_component_rasters(
            chrome(),
            possession(),
            figures(),
        )
        self.assertFalse(rasters.cross_component_z_order_recovered)
        self.assertFalse(rasters.flattened_frame_available)
        self.assertEqual(
            (
                rasters.chrome.component,
                rasters.possession_diagram.component,
                rasters.possession_figures.component,
            ),
            (
                "direct_chrome",
                "possession_diagram",
                "possession_figures_text",
            ),
        )
        self.assertEqual(len({p.rgba_sha256 for p in (
            rasters.chrome,
            rasters.possession_diagram,
            rasters.possession_figures,
        )}), 3)

    def test_rejects_drifted_or_out_of_clip_source_payloads(self):
        bad_chrome = chrome()
        bad_top = replace(
            bad_chrome.placements[0],
            rgba=bad_chrome.placements[0].rgba[:-4],
        )
        with self.assertRaisesRegex(
            FastViewComponentRasterError,
            "source RGBA payload",
        ):
            rasterize_fastview_chrome_plane(
                replace(bad_chrome, placements=(bad_top,) + bad_chrome.placements[1:])
            )

        art = figures()
        first = art.rows[0]
        bad_first = replace(
            first,
            line_origin=(first.clip_rect[2], first.clip_rect[1]),
        )
        with self.assertRaisesRegex(
            FastViewComponentRasterError,
            "exceeds its recovered source clip",
        ):
            rasterize_fastview_possession_figures_plane(
                replace(art, rows=(bad_first,) + art.rows[1:])
            )

    def test_raster_plane_hash_guard_rejects_mutation(self):
        plane = rasterize_fastview_chrome_plane(chrome())
        with self.assertRaisesRegex(FastViewComponentRasterError, "SHA-256"):
            replace(plane, rgba_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
