"""Tests for the partial static FastView TeamTable pixel layer."""
from dataclasses import replace
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_render_plan,
    build_fastview_player_row_snapshot,
)
from gate14_fastview_team_static_raster import (
    FastViewTeamStaticRasterError,
    rasterize_fastview_team_static_rows,
)
from original_fastview_team_art import (
    FASTVIEW_TEAM_ART_RESOURCES,
    build_fastview_team_art,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes((value, value + 1, value + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


def exact_art():
    return build_fastview_team_art(
        {
            resource.name: image(*resource.size, 10 + index * 10)
            for index, resource in enumerate(FASTVIEW_TEAM_ART_RESOURCES)
        }
    )


def plan(side, row, energy=79):
    snapshot = build_fastview_player_row_snapshot(
        side_index=side,
        row_index=row,
        shirt_number=9,
        source_position_code=19,
        surname="Striker",
        first_name_initial="A",
        form_value=4,
        energy_value=energy,
    )
    return build_fastview_player_row_render_plan(snapshot)


def pixel(raster, x, y):
    offset = (y * 800 + x) * 4
    return tuple(raster.rgba[offset:offset + 4])


class FastViewTeamStaticRasterTests(unittest.TestCase):
    def test_rasterizes_only_name_grid_and_static_bar_for_each_row(self):
        home = plan(0, 0)
        away = plan(1, 0)
        raster = rasterize_fastview_team_static_rows(
            exact_art(),
            (home, away),
        )

        self.assertEqual(raster.size, (800, 600))
        self.assertEqual(raster.row_identities, ((0, 0), (1, 0)))
        self.assertEqual(raster.source_layer_count, 4)
        self.assertFalse(raster.dynamic_energy_rasterized)
        self.assertFalse(raster.text_rasterized)
        self.assertFalse(raster.complete_team_table)

        # Resource order values:
        # grid1=10, grid3=30, blank_bar=60, team_bar_2=70.
        self.assertEqual(pixel(raster, 37, 27), (10, 11, 12, 255))
        self.assertEqual(pixel(raster, 504, 27), (30, 31, 32, 255))
        self.assertEqual(pixel(raster, 309, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(raster, 409, 27), (70, 71, 72, 255))

        # Text semantics are not separately rasterized; outside the two source
        # art rectangles the plane remains transparent.
        self.assertEqual(pixel(raster, 400, 27), (0, 0, 0, 0))
        self.assertEqual(pixel(raster, 0, 0), (0, 0, 0, 0))

    def test_row_11_switches_to_source_alternate_name_grid(self):
        home = plan(0, 11)
        away = plan(1, 11)
        raster = rasterize_fastview_team_static_rows(
            exact_art(),
            (home, away),
        )
        y = 27 + 11 * 17
        # grid2=20, grid4=40.
        self.assertEqual(pixel(raster, 37, y), (20, 21, 22, 255))
        self.assertEqual(pixel(raster, 504, y), (40, 41, 42, 255))

    def test_dynamic_energy_width_does_not_change_static_plane(self):
        low = rasterize_fastview_team_static_rows(exact_art(), (plan(0, 0, 60),))
        high = rasterize_fastview_team_static_rows(exact_art(), (plan(0, 0, 99),))
        self.assertEqual(low.rgba, high.rgba)
        self.assertEqual(low.rgba_sha256, high.rgba_sha256)

    def test_rejects_duplicate_rows_or_drifted_static_geometry(self):
        home = plan(0, 0)
        with self.assertRaisesRegex(
            FastViewTeamStaticRasterError,
            "duplicate TeamTable PlayerRow identity",
        ):
            rasterize_fastview_team_static_rows(exact_art(), (home, home))

        drifted = replace(home, name_grid_rect=(37, 27, 295, 43))
        with self.assertRaisesRegex(
            FastViewTeamStaticRasterError,
            "does not match decoded resource geometry",
        ):
            rasterize_fastview_team_static_rows(exact_art(), (drifted,))

    def test_empty_retained_row_set_is_transparent_and_still_partial(self):
        raster = rasterize_fastview_team_static_rows(exact_art(), ())
        self.assertEqual(raster.row_identities, ())
        self.assertEqual(raster.source_layer_count, 0)
        self.assertEqual(set(raster.rgba), {0})
        self.assertFalse(raster.complete_team_table)


if __name__ == "__main__":
    unittest.main()
