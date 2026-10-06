"""Regression coverage for the source-backed PPreMatch surface boundary."""
from datetime import date
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from gate14_fastview_surfaced_picture_selection import (
    build_fastview_surfaced_resource_selection,
)
from gate14_fastview_surfaced_resource_loader import (
    VerifiedFastViewSurfacedResource,
)
from gate14_prematch_rating_widths import PrematchTeamRatingWidths
from gate14_prematch_surface import (
    BoundPrematchRatingRows,
    PrematchSurfaceBoundary,
    bind_prematch_rating_widths,
    build_verified_prematch_surface_boundary,
    prematch_surface_contract,
)
from original_prematch_panel import (
    PREMATCH_ALL_EA444_SPECS,
    PREMATCH_RATING_ROWS,
    PREMATCH_STATIC_PLACEMENTS,
)


def club(country_id, basename, fan_base_index):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
    )


class FakePrematchResources:
    def __init__(self):
        self._decoded = {
            spec.source_path: SimpleNamespace(
                width=spec.width,
                height=spec.height,
                rgba=bytes(spec.width * spec.height * 4),
            )
            for spec in PREMATCH_ALL_EA444_SPECS
        }
        self.selector_atlas = object()
        self.font = object()

    def decoded(self, source_path):
        return self._decoded[source_path]


class PrematchSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.clubs = {
            10: club(26, "arsenal", 25),
            11: club(26, "chelsea", 14),
        }
        self.countries = {
            26: SimpleNamespace(graphics_directory="England"),
        }

    def _selection(self):
        return build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=self.clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )

    def test_boundary_reuses_exact_team_background_selection_and_native_layers(self):
        selection = self._selection()
        background = VerifiedFastViewSurfacedResource(
            role="background",
            source_path=selection.background_source_candidates[0],
            byte_size=1,
            sha256="0" * 64,
            geometry=(800, 600),
            rgba=bytes(800 * 600 * 4),
            transparent_pixels=0,
        )
        prematch = FakePrematchResources()

        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ) as select,
            patch(
                "gate14_prematch_surface.load_verified_selected_background",
                return_value=background,
            ) as load_background,
            patch(
                "gate14_prematch_surface.load_verified_original_prematch_resources",
                return_value=prematch,
            ) as load_prematch,
        ):
            boundary = build_verified_prematch_surface_boundary(
                match_date=date(2001, 1, 13),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=None,
                source_root="/source",
                original_executable="/source/FOOTBAL.EXE",
            )

        self.assertIsInstance(boundary, PrematchSurfaceBoundary)
        select.assert_called_once()
        load_background.assert_called_once_with(
            selection,
            source_root="/source",
            original_executable="/source/FOOTBAL.EXE",
        )
        load_prematch.assert_called_once_with(
            source_root="/source",
            original_executable="/source/FOOTBAL.EXE",
        )
        self.assertEqual(boundary.background.source_path, selection.background_source_candidates[0])
        self.assertEqual(
            (
                boundary.background.rect.x,
                boundary.background.rect.y,
                boundary.background.rect.width,
                boundary.background.rect.height,
            ),
            (0, 0, 800, 600),
        )
        self.assertEqual(
            tuple(layer.role for layer in boundary.static_layers),
            tuple(placement.role for placement in PREMATCH_STATIC_PLACEMENTS),
        )
        self.assertEqual(
            tuple((surface.mode, surface.event_id, surface.label) for surface in boundary.selectors),
            (
                (0, 4, "3D Match"),
                (1, 3, "3D Highlights"),
                (2, 2, "FastView"),
                (3, 1, "Quick Match"),
            ),
        )

    def test_rating_rows_expose_geometry_and_pixels_without_inventing_meanings_or_widths(self):
        selection = self._selection()
        background = VerifiedFastViewSurfacedResource(
            role="background",
            source_path=selection.background_source_candidates[0],
            byte_size=1,
            sha256="0" * 64,
            geometry=(800, 600),
            rgba=bytes(800 * 600 * 4),
            transparent_pixels=0,
        )
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_selected_background",
                return_value=background,
            ),
            patch(
                "gate14_prematch_surface.load_verified_original_prematch_resources",
                return_value=FakePrematchResources(),
            ),
        ):
            boundary = build_verified_prematch_surface_boundary(
                match_date=date(2001, 1, 13),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=None,
                source_root="/source",
                original_executable="/source/FOOTBAL.EXE",
            )

        self.assertEqual(
            tuple(
                (
                    row.native_record_discriminator,
                    row.native_width_function_va,
                    row.left_rect.x,
                    row.right_rect.x,
                    row.left_rect.y,
                    row.left_rect.width,
                    row.left_rect.height,
                )
                for row in boundary.rating_rows
            ),
            tuple(
                (
                    row.native_record_discriminator,
                    row.native_width_function_va,
                    65,
                    564,
                    row.y,
                    171,
                    16,
                )
                for row in PREMATCH_RATING_ROWS
            ),
        )
        self.assertFalse(boundary.rating_dynamic_widths_bound_to_cleanroom_state)
        self.assertFalse(boundary.full_cross_layer_draw_order_recovered)
        self.assertFalse(boundary.management_launch_trigger_recovered)
        self.assertFalse(boundary.complete_prematch_frame)
        self.assertFalse(boundary.gate14_complete)

    def test_state_binding_uses_exact_left_growth_and_right_mirroring(self):
        selection = self._selection()
        background = VerifiedFastViewSurfacedResource(
            role="background",
            source_path=selection.background_source_candidates[0],
            byte_size=1,
            sha256="0" * 64,
            geometry=(800, 600),
            rgba=bytes(800 * 600 * 4),
            transparent_pixels=0,
        )
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_selected_background",
                return_value=background,
            ),
            patch(
                "gate14_prematch_surface.load_verified_original_prematch_resources",
                return_value=FakePrematchResources(),
            ),
        ):
            boundary = build_verified_prematch_surface_boundary(
                match_date=date(2001, 1, 13),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=None,
                source_root="/source",
                original_executable="/source/FOOTBAL.EXE",
            )

        left = PrematchTeamRatingWidths(169, 120, 80, 40)
        right = PrematchTeamRatingWidths(17, 34, 51, 68)
        bound = bind_prematch_rating_widths(
            boundary,
            left_widths=left,
            right_widths=right,
        )

        self.assertIsInstance(bound, BoundPrematchRatingRows)
        self.assertEqual(
            tuple(
                (
                    row.semantic_group,
                    row.left_width,
                    row.right_width,
                    (
                        row.left_dynamic_rect.x,
                        row.left_dynamic_rect.y,
                        row.left_dynamic_rect.width,
                        row.left_dynamic_rect.height,
                    ),
                    (
                        row.right_dynamic_rect.x,
                        row.right_dynamic_rect.y,
                        row.right_dynamic_rect.width,
                        row.right_dynamic_rect.height,
                    ),
                )
                for row in bound.rows
            ),
            (
                ("goalkeeper", 169, 17, (65, 497, 169, 16), (718, 497, 17, 16)),
                ("defence", 120, 34, (65, 515, 120, 16), (701, 515, 34, 16)),
                ("midfield", 80, 51, (65, 533, 80, 16), (684, 533, 51, 16)),
                ("attack", 40, 68, (65, 551, 40, 16), (667, 551, 68, 16)),
            ),
        )
        self.assertTrue(bound.source_state_bound)
        self.assertTrue(bound.native_mirroring_preserved)
        self.assertFalse(bound.complete_prematch_frame)
        self.assertFalse(bound.gate14_complete)

    def test_contract_keeps_all_unresolved_claims_fail_closed(self):
        contract = prematch_surface_contract()
        self.assertEqual(contract["native_surface"], (800, 600))
        self.assertTrue(contract["team_backgrounds_selector_reused"])
        self.assertTrue(contract["team_backgrounds_loader_reused"])
        self.assertEqual(contract["selector_modes"], (0, 1, 2, 3))
        self.assertEqual(contract["selector_events"], (4, 3, 2, 1))
        self.assertEqual(contract["rating_discriminators"], (3, 0, 1, 2))
        self.assertTrue(contract["rating_width_binding_available"])
        self.assertFalse(contract["rating_dynamic_widths_bound_by_resource_loader"])
        self.assertFalse(contract["rating_dynamic_widths_bound_to_cleanroom_state"])
        self.assertFalse(contract["full_cross_layer_draw_order_recovered"])
        self.assertFalse(contract["management_launch_trigger_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
