"""Tests for source-cropped dynamic FastView PlayerRow energy pixels."""
from dataclasses import replace
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_render_plan,
    build_fastview_player_row_snapshot,
)
from gate14_fastview_team_energy_raster import (
    FastViewTeamEnergyRasterError,
    PICTURECONTROL_BLIT_WRAPPER_VA,
    PICTURECONTROL_RENDER_PREPARE_VA,
    PLAYERROW_DYNAMIC_PICTURECONTROL_CREATE_VA,
    PLAYERROW_ENERGY_RECT_WRITER_VA,
    PLAYERROW_STATIC_PICTURECONTROL_CREATE_VA,
    rasterize_fastview_team_energy_rows,
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


def plan(side, row, energy):
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


class FastViewTeamEnergyRasterTests(unittest.TestCase):
    def test_records_source_renderer_and_constructor_order_anchors(self):
        self.assertEqual(PLAYERROW_ENERGY_RECT_WRITER_VA, 0x526680)
        self.assertEqual(PLAYERROW_STATIC_PICTURECONTROL_CREATE_VA, 0x5262E6)
        self.assertEqual(PLAYERROW_DYNAMIC_PICTURECONTROL_CREATE_VA, 0x526351)
        self.assertLess(
            PLAYERROW_STATIC_PICTURECONTROL_CREATE_VA,
            PLAYERROW_DYNAMIC_PICTURECONTROL_CREATE_VA,
        )
        self.assertEqual(PICTURECONTROL_RENDER_PREPARE_VA, 0x64E5D0)
        self.assertEqual(PICTURECONTROL_BLIT_WRAPPER_VA, 0x6556C0)

    def test_side0_crops_team_bar_1_from_left_over_blank_bar(self):
        raster = rasterize_fastview_team_energy_rows(
            exact_art(),
            (plan(0, 0, 79),),
        )
        self.assertEqual(raster.row_identities, ((0, 0),))
        self.assertEqual(raster.source_layer_count, 3)
        self.assertTrue(raster.dynamic_energy_rasterized)
        self.assertEqual(
            raster.picturecontrol_resize_rule,
            "crop_equal_source_destination_extent",
        )
        self.assertFalse(raster.text_rasterized)
        self.assertFalse(raster.complete_team_table)

        # energy 79 -> 2 * (79 - 58) = 42 dynamic pixels.
        # team_bar_1=50 overlays blank_bar=60 for x 309..350.
        self.assertEqual(pixel(raster, 309, 27), (50, 51, 52, 255))
        self.assertEqual(pixel(raster, 350, 27), (50, 51, 52, 255))
        self.assertEqual(pixel(raster, 351, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(raster, 390, 27), (60, 61, 62, 255))

    def test_side1_crops_blank_bar_from_left_to_reveal_team_bar_2_from_right(self):
        raster = rasterize_fastview_team_energy_rows(
            exact_art(),
            (plan(1, 0, 79),),
        )

        # side 1 dynamic blank width = 82 - 42 = 40.
        # blank_bar=60 covers the left 40 pixels; team_bar_2=70 remains right.
        self.assertEqual(pixel(raster, 409, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(raster, 448, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(raster, 449, 27), (70, 71, 72, 255))
        self.assertEqual(pixel(raster, 490, 27), (70, 71, 72, 255))

    def test_energy_endpoints_preserve_empty_and_full_source_crops(self):
        art = exact_art()

        side0_low = rasterize_fastview_team_energy_rows(art, (plan(0, 0, 58),))
        side0_full = rasterize_fastview_team_energy_rows(art, (plan(0, 0, 99),))
        self.assertEqual(pixel(side0_low, 309, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(side0_low, 390, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(side0_full, 309, 27), (50, 51, 52, 255))
        self.assertEqual(pixel(side0_full, 390, 27), (50, 51, 52, 255))

        side1_low = rasterize_fastview_team_energy_rows(art, (plan(1, 0, 58),))
        side1_full = rasterize_fastview_team_energy_rows(art, (plan(1, 0, 99),))
        self.assertEqual(pixel(side1_low, 409, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(side1_low, 490, 27), (60, 61, 62, 255))
        self.assertEqual(pixel(side1_full, 409, 27), (70, 71, 72, 255))
        self.assertEqual(pixel(side1_full, 490, 27), (70, 71, 72, 255))

    def test_below_source_anchor_energy_stays_fail_closed_at_raster_boundary(self):
        with self.assertRaisesRegex(
            FastViewTeamEnergyRasterError,
            "outside the source-closed PictureControl domain",
        ):
            rasterize_fastview_team_energy_rows(
                exact_art(),
                (plan(0, 0, 57),),
            )

    def test_rejects_dynamic_rect_drift_or_false_fidelity_promotion(self):
        home = plan(0, 0, 79)
        drifted = replace(
            home,
            energy_dynamic_rect=(
                home.energy_dynamic_rect[0] + 1,
                home.energy_dynamic_rect[1],
                home.energy_dynamic_rect[2],
                home.energy_dynamic_rect[3],
            ),
        )
        with self.assertRaisesRegex(
            FastViewTeamEnergyRasterError,
            "rectangle ownership",
        ):
            rasterize_fastview_team_energy_rows(exact_art(), (drifted,))

        raster = rasterize_fastview_team_energy_rows(exact_art(), (home,))
        with self.assertRaisesRegex(
            FastViewTeamEnergyRasterError,
            "cannot promote",
        ):
            replace(raster, text_rasterized=True)
        with self.assertRaisesRegex(
            FastViewTeamEnergyRasterError,
            "crop rule",
        ):
            replace(raster, picturecontrol_resize_rule="stretch")


if __name__ == "__main__":
    unittest.main()
