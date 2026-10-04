"""Tests for complete source-backed retained FastView PlayerRow pixels."""
from dataclasses import replace
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_render_plan,
    build_fastview_player_row_snapshot,
)
from gate14_fastview_playerrows_raster import (
    PLAYERROW_DYNAMIC_BAR_CREATE_VA,
    PLAYERROW_FIRST_TEXT_CREATE_VA,
    PLAYERROW_LAST_TEXT_CREATE_VA,
    PLAYERROW_NAME_GRID_CREATE_VA,
    PLAYERROW_STATIC_BAR_CREATE_VA,
    FastViewPlayerRowsRasterError,
    compose_fastview_player_rows_raster,
)
from gate14_fastview_team_energy_raster import rasterize_fastview_team_energy_rows
from gate14_fastview_team_text_raster import rasterize_fastview_playerrow_text
from original_fastview_team_art import (
    FASTVIEW_TEAM_ART_RESOURCES,
    build_fastview_team_art,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


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


def plan(*, side=0, row=0, energy=79, goal=None, own_goal=None):
    snapshot = build_fastview_player_row_snapshot(
        side_index=side,
        row_index=row,
        shirt_number=9,
        source_position_code=19,
        surname="Striker",
        first_name_initial="A",
        form_value=7,
        energy_value=energy,
        displayed_goal_count=goal,
        displayed_own_goal_count=own_goal,
    )
    return build_fastview_player_row_render_plan(snapshot)


def pixel(raster, x, y):
    offset = (y * 800 + x) * 4
    return tuple(raster.rgba[offset:offset + 4])


class FastViewPlayerRowsRasterTests(unittest.TestCase):
    def test_records_native_control_construction_order(self):
        self.assertLess(PLAYERROW_NAME_GRID_CREATE_VA, PLAYERROW_FIRST_TEXT_CREATE_VA)
        self.assertLess(PLAYERROW_FIRST_TEXT_CREATE_VA, PLAYERROW_LAST_TEXT_CREATE_VA)
        self.assertLess(PLAYERROW_LAST_TEXT_CREATE_VA, PLAYERROW_STATIC_BAR_CREATE_VA)
        self.assertLess(PLAYERROW_STATIC_BAR_CREATE_VA, PLAYERROW_DYNAMIC_BAR_CREATE_VA)

    def test_composes_complete_written_playerrow_without_promoting_team_table(self):
        render_plans = (plan(goal=2, own_goal=1),)
        energy = rasterize_fastview_team_energy_rows(exact_art(), render_plans)
        text = rasterize_fastview_playerrow_text(REPO_ROOT, render_plans)

        raster = compose_fastview_player_rows_raster(energy, text, render_plans)

        self.assertEqual(raster.row_identities, ((0, 0),))
        self.assertEqual(raster.energy_rgba_sha256, energy.rgba_sha256)
        self.assertEqual(raster.text_rgba_sha256, text.rgba_sha256)
        self.assertTrue(raster.native_row_control_order_recovered)
        self.assertTrue(raster.text_energy_rectangles_disjoint)
        self.assertTrue(raster.complete_retained_player_rows)
        self.assertFalse(raster.complete_team_table)
        self.assertFalse(raster.complete_fastview_frame)

        # Dynamic energy remains byte-identical in the disjoint bar region.
        self.assertEqual(pixel(raster, 309, 27), pixel(energy, 309, 27))
        self.assertEqual(pixel(raster, 350, 27), pixel(energy, 350, 27))
        self.assertEqual(pixel(raster, 351, 27), pixel(energy, 351, 27))

        # At least one visible text pixel must alter the name-grid area.
        changed = False
        for y in range(27, 43):
            for x in range(37, 296):
                if pixel(raster, x, y) != pixel(energy, x, y):
                    changed = True
                    break
            if changed:
                break
        self.assertTrue(changed)

    def test_unwritten_goal_cells_need_no_placeholder_pixels(self):
        render_plans = (plan(),)
        energy = rasterize_fastview_team_energy_rows(exact_art(), render_plans)
        text = rasterize_fastview_playerrow_text(REPO_ROOT, render_plans)
        self.assertEqual(
            text.rendered_cells,
            ((0, 0, 1), (0, 0, 2), (0, 0, 3), (0, 0, 6)),
        )

        raster = compose_fastview_player_rows_raster(energy, text, render_plans)
        self.assertTrue(raster.complete_retained_player_rows)

    def test_rejects_row_identity_or_rendered_cell_drift(self):
        render_plans = (plan(),)
        energy = rasterize_fastview_team_energy_rows(exact_art(), render_plans)
        text = rasterize_fastview_playerrow_text(REPO_ROOT, render_plans)

        with self.assertRaisesRegex(
            FastViewPlayerRowsRasterError,
            "energy raster row identities drifted",
        ):
            compose_fastview_player_rows_raster(
                replace(energy, row_identities=((1, 0),)),
                text,
                render_plans,
            )

        with self.assertRaisesRegex(
            FastViewPlayerRowsRasterError,
            "rendered-cell set drifted",
        ):
            compose_fastview_player_rows_raster(
                energy,
                replace(text, rendered_cells=text.rendered_cells[:-1]),
                render_plans,
            )

    def test_rejects_false_broader_completeness(self):
        render_plans = (plan(),)
        raster = compose_fastview_player_rows_raster(
            rasterize_fastview_team_energy_rows(exact_art(), render_plans),
            rasterize_fastview_playerrow_text(REPO_ROOT, render_plans),
            render_plans,
        )
        for field in ("complete_team_table", "complete_fastview_frame"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    FastViewPlayerRowsRasterError,
                    "cannot promote broader completeness",
                ):
                    replace(raster, **{field: True})


if __name__ == "__main__":
    unittest.main()
