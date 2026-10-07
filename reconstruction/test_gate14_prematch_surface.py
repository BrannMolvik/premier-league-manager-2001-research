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
    VerifiedFastViewSurfacedResourceSet,
)
from gate14_prematch_rating_widths import PrematchTeamRatingWidths
from gate14_prematch_marker_binding import (
    BoundPrematchStartingXIMarker,
    BoundPrematchStartingXIMarkers,
)
from gate14_prematch_supplied_state import (
    BoundPrematchSuppliedState,
    PrematchSuppliedStateError,
    bind_prematch_supplied_state,
    prematch_supplied_state_contract,
)
from original_front_end_layout import OriginalRect
from gate14_prematch_surface import (
    BoundPrematchPlayerRows,
    BoundPrematchRatingRows,
    BoundPrematchSelectorFrames,
    PrematchSurfaceBoundary,
    PrematchSurfaceError,
    bind_prematch_player_rows,
    bind_prematch_dynamic_text_state,
    bind_prematch_rating_state,
    bind_prematch_rating_widths,
    bind_prematch_selector_frames,
    build_verified_prematch_surface_boundary,
    prematch_surface_contract,
    prematch_child_family_coverage,
    source_prematch_text_controls,
    source_prematch_player_text_rows,
)
from original_prematch_panel import (
    PREMATCH_ALL_EA444_SPECS,
    PREMATCH_RATING_ROWS,
    PREMATCH_PLAYER_STRIP_ROWS,
    PREMATCH_STATIC_PLACEMENTS,
    PREMATCH_CHILD_COUNT,
    PREMATCH_CHILD_ORDER_RANGES,
)


def club(country_id, basename, fan_base_index):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
    )


def fake_surfaced_resources(selection):
    def resource(role, source_path, geometry):
        width, height = geometry
        return VerifiedFastViewSurfacedResource(
            role=role,
            source_path=source_path,
            byte_size=1,
            sha256="0" * 64,
            geometry=geometry,
            rgba=bytes(width * height * 4),
            transparent_pixels=0,
        )

    return VerifiedFastViewSurfacedResourceSet(
        selection=selection,
        background=resource(
            "background",
            selection.background_source_candidates[0],
            (800, 600),
        ),
        home_badge=resource(
            "home_badge",
            selection.home_badge_source_candidates[0],
            (135, 93),
        ),
        away_badge=resource(
            "away_badge",
            selection.away_badge_source_candidates[0],
            (135, 93),
        ),
    )


class FakeSelectorAtlas:
    def frame(self, source_index):
        return SimpleNamespace(source_index=source_index)


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
        self.selector_atlas = FakeSelectorAtlas()
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
        surfaced = fake_surfaced_resources(selection)
        prematch = FakePrematchResources()

        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ) as select,
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
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
            tuple(
                (
                    badge.role,
                    badge.source_path,
                    (badge.rect.x, badge.rect.y, badge.rect.width, badge.rect.height),
                )
                for badge in boundary.team_badges
            ),
            (
                (
                    "home_badge",
                    selection.home_badge_source_candidates[0],
                    (38, 1, 135, 93),
                ),
                (
                    "away_badge",
                    selection.away_badge_source_candidates[0],
                    (627, 1, 135, 93),
                ),
            ),
        )
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
        self.assertEqual(boundary.text_controls, source_prematch_text_controls())
        self.assertEqual(
            tuple(
                (
                    control.role,
                    (
                        control.rect.x,
                        control.rect.y,
                        control.rect.width,
                        control.rect.height,
                    ),
                    control.style_wrapper_va,
                    control.fixed_text,
                    control.source_buffer_offset,
                    control.dynamic_text_source_closed,
                )
                for control in boundary.text_controls
            ),
            (
                ("fixture_header", (250, 45, 300, 30), 0x87BE30, None, 0x170, False),
                ("date_weather", (250, 70, 300, 16), 0x87BE30, None, 0x270, False),
                ("team_identity_0", (184, 4, 185, 39), 0x87BE80, None, None, False),
                ("versus", (374, 5, 52, 37), 0x87BE70, "V", None, False),
                ("team_identity_1", (429, 4, 185, 39), 0x87BE80, None, None, False),
                ("rating_left_gk", (37, 498, 25, 14), 0x87BEA0, "GK", None, True),
                ("rating_left_def", (37, 516, 25, 14), 0x87BEA0, "DEF", None, True),
                ("rating_left_mid", (37, 534, 25, 14), 0x87BEA0, "MID", None, True),
                ("rating_left_att", (37, 552, 25, 14), 0x87BEA0, "ATT", None, True),
                ("rating_right_gk", (737, 498, 25, 14), 0x87BEA0, "GK", None, True),
                ("rating_right_def", (737, 516, 25, 14), 0x87BEA0, "DEF", None, True),
                ("rating_right_mid", (737, 534, 25, 14), 0x87BEA0, "MID", None, True),
                ("rating_right_att", (737, 552, 25, 14), 0x87BEA0, "ATT", None, True),
            ),
        )
        self.assertEqual(boundary.player_text_rows, source_prematch_player_text_rows())
        self.assertEqual(len(boundary.player_text_rows), 36)
        self.assertEqual(
            (
                boundary.player_text_rows[0].number_rect.x,
                boundary.player_text_rows[0].name_rect.x,
                boundary.player_text_rows[18].number_rect.x,
                boundary.player_text_rows[18].name_rect.x,
            ),
            (37, 67, 737, 564),
        )
        self.assertEqual(boundary.player_text_rows[11].strip_variant(11), "disabled")
        self.assertEqual(boundary.player_text_rows[11].strip_variant(12), "active")
        self.assertEqual(len(boundary.player_strip_rows), 36)
        self.assertEqual(
            tuple(
                (
                    surface.side,
                    surface.roster_group,
                    surface.row_index,
                    (
                        surface.rect.x,
                        surface.rect.y,
                        surface.rect.width,
                        surface.rect.height,
                    ),
                    surface.active_source_path,
                    surface.disabled_source_path,
                    surface.variant_state_source_closed,
                )
                for surface in boundary.player_strip_rows
            ),
            tuple(
                (
                    row.side,
                    row.roster_group,
                    row.row_index,
                    (row.rect.x, row.rect.y, row.rect.width, row.rect.height),
                    row.active_spec.source_path,
                    row.disabled_spec.source_path if row.disabled_spec is not None else None,
                    True,
                )
                for row in PREMATCH_PLAYER_STRIP_ROWS
            ),
        )
        self.assertTrue(
            all(
                len(surface.active_rgba) == 200 * 16 * 4
                for surface in boundary.player_strip_rows
            )
        )
        self.assertTrue(
            all(
                surface.disabled_rgba is None
                for surface in boundary.player_strip_rows
                if surface.roster_group == "starter"
            )
        )
        self.assertTrue(
            all(
                surface.disabled_rgba is not None
                and len(surface.disabled_rgba) == 200 * 16 * 4
                for surface in boundary.player_strip_rows
                if surface.roster_group == "reserve"
            )
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
        self.assertTrue(all(s.native_visual_state_source_closed for s in boundary.selectors))
        self.assertTrue(all(not s.persistent_selected_visual for s in boundary.selectors))
        self.assertEqual(tuple(s.initial_flags for s in boundary.selectors), (0x183,) * 4)
        self.assertEqual(tuple(s.group_lengths for s in boundary.selectors), ((11, 11, 1),) * 4)

    def test_dynamic_text_state_binding_uses_boundary_selection_without_raster_claim(self):
        text_clubs = {
            10: SimpleNamespace(
                country_id=26,
                graphics_basename="arsenal",
                fan_base_index=25,
                short_name="Arsenal",
                stadium="Highbury",
            ),
            11: SimpleNamespace(
                country_id=26,
                graphics_basename="chelsea",
                fan_base_index=14,
                short_name="Chelsea",
                stadium="Stamford Bridge",
            ),
        }
        selection = build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=text_clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
            ),
            patch(
                "gate14_prematch_surface.load_verified_original_prematch_resources",
                return_value=FakePrematchResources(),
            ),
        ):
            boundary = build_verified_prematch_surface_boundary(
                match_date=date(2001, 1, 13),
                clubs=text_clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=None,
                source_root="/source",
                original_executable="/source/FOOTBAL.EXE",
            )

        bound = bind_prematch_dynamic_text_state(
            boundary,
            clubs=text_clubs,
            competition_name="F.A. Premier League",
            weather_code=4,
            temperature_c=-1,
            home_team_name_override=None,
            away_team_name_override="Chelsea Network",
        )
        self.assertEqual(
            bound.fixture_header,
            "F.A. Premier League MATCH TODAY AT Highbury",
        )
        self.assertEqual(
            bound.date_weather,
            "13th January 2001 Snowy -1°C",
        )
        self.assertEqual(bound.home_team_identity, "Arsenal")
        self.assertEqual(bound.away_team_identity, "Chelsea Network")
        self.assertFalse(bound.text_pixels_rasterized)
        self.assertFalse(bound.complete_prematch_frame)

        with self.assertRaisesRegex(PrematchSurfaceError, "exact PrematchSurfaceBoundary"):
            bind_prematch_dynamic_text_state(
                object(),
                clubs=text_clubs,
                competition_name="F.A. Premier League",
                weather_code=0,
                temperature_c=10,
                home_team_name_override=None,
                away_team_name_override=None,
            )

    def test_player_row_binding_uses_source_name_number_and_count_driven_state(self):
        selection = self._selection()
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
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

        left = tuple(
            SimpleNamespace(
                shirt_number=index + 1,
                first_name="-Alias" if index == 1 else "David",
                surname="Ronaldo" if index == 1 else f"Left{index}",
            )
            for index in range(12)
        )
        right = tuple(
            SimpleNamespace(
                shirt_number=index + 20,
                first_name="Ryan",
                surname=f"Right{index}",
            )
            for index in range(18)
        )

        bound = bind_prematch_player_rows(
            boundary,
            left_players=left,
            right_players=right,
        )

        self.assertIsInstance(bound, BoundPrematchPlayerRows)
        self.assertEqual(bound.left_participant_count, 12)
        self.assertEqual(bound.right_participant_count, 18)
        self.assertEqual(len(bound.rows), 36)

        left_rows = bound.rows[:18]
        right_rows = bound.rows[18:]
        self.assertEqual(
            tuple(row.variant for row in left_rows),
            ("active",) * 12 + ("disabled",) * 6,
        )
        self.assertEqual(
            tuple(row.variant for row in right_rows),
            ("active",) * 18,
        )
        self.assertEqual(left_rows[0].shirt_number_text, "1")
        self.assertEqual(left_rows[0].display_name_text, "D. Left0")
        self.assertEqual(left_rows[1].display_name_text, "Ronaldo")
        self.assertIsNone(left_rows[12].shirt_number_text)
        self.assertIsNone(left_rows[12].display_name_text)
        self.assertEqual(right_rows[0].shirt_number_text, "20")
        self.assertEqual(right_rows[0].display_name_text, "R. Right0")
        self.assertTrue(bound.source_state_bound)
        self.assertFalse(bound.complete_prematch_frame)
        self.assertFalse(bound.gate14_complete)

        with self.assertRaisesRegex(PrematchSurfaceError, "cannot exceed 18"):
            bind_prematch_player_rows(
                boundary,
                left_players=tuple(left) + tuple(left[:7]),
                right_players=right,
            )

    def test_selector_binding_requires_explicit_native_frame_state(self):
        selection = self._selection()
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
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

        bound = bind_prematch_selector_frames(
            boundary,
            source_frame_indices=(0, 10, 11, 22),
        )
        self.assertIsInstance(bound, BoundPrematchSelectorFrames)
        self.assertEqual(
            tuple(item.source.mode for item in bound.selectors),
            (0, 1, 2, 3),
        )
        self.assertEqual(
            tuple(item.source_frame_index for item in bound.selectors),
            (0, 10, 11, 22),
        )
        self.assertEqual(
            tuple(item.frame.source_index for item in bound.selectors),
            (0, 10, 11, 22),
        )
        self.assertTrue(bound.supplied_pointer_update_state_bound)
        self.assertFalse(bound.persistent_selected_visual)
        self.assertFalse(bound.complete_prematch_frame)
        self.assertFalse(bound.gate14_complete)

        with self.assertRaisesRegex(PrematchSurfaceError, "one native frame index"):
            bind_prematch_selector_frames(
                boundary,
                source_frame_indices=(0, 1, 2),
            )
        with self.assertRaisesRegex(PrematchSurfaceError, "0..22"):
            bind_prematch_selector_frames(
                boundary,
                source_frame_indices=(0, 1, 2, 23),
            )

    def test_rating_rows_expose_geometry_and_pixels_without_inventing_meanings_or_widths(self):
        selection = self._selection()
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
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
        self.assertTrue(boundary.full_cross_layer_draw_order_recovered)
        self.assertFalse(boundary.management_launch_trigger_recovered)
        self.assertFalse(boundary.complete_prematch_frame)
        self.assertFalse(boundary.gate14_complete)

    def test_state_binding_uses_exact_left_growth_and_right_mirroring(self):
        selection = self._selection()
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
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

    def test_state_helper_composes_native_xi_calculation_for_both_sides(self):
        selection = self._selection()
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
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

        expected_left = PrematchTeamRatingWidths(10, 20, 30, 40)
        expected_right = PrematchTeamRatingWidths(50, 60, 70, 80)
        with patch(
            "gate14_prematch_surface.source_prematch_team_rating_widths",
            side_effect=(expected_left, expected_right),
        ) as calculate:
            bound = bind_prematch_rating_state(
                boundary,
                left_starters=tuple(range(11)),
                right_starters=tuple(range(11, 22)),
                positions={},
            )

        self.assertEqual(calculate.call_count, 2)
        self.assertEqual(bound.left_widths, expected_left)
        self.assertEqual(bound.right_widths, expected_right)
        self.assertEqual(
            tuple(row.semantic_group for row in bound.rows),
            ("goalkeeper", "defence", "midfield", "attack"),
        )

    def test_complete_supplied_child_state_attaches_every_family_without_pixel_claim(self):
        text_clubs = {
            10: SimpleNamespace(
                country_id=26,
                graphics_basename="arsenal",
                fan_base_index=25,
                short_name="Arsenal",
                stadium="Highbury",
            ),
            11: SimpleNamespace(
                country_id=26,
                graphics_basename="chelsea",
                fan_base_index=14,
                short_name="Chelsea",
                stadium="Stamford Bridge",
            ),
        }
        selection = build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=text_clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )
        surfaced = fake_surfaced_resources(selection)
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=surfaced,
            ),
            patch(
                "gate14_prematch_surface.load_verified_original_prematch_resources",
                return_value=FakePrematchResources(),
            ),
        ):
            boundary = build_verified_prematch_surface_boundary(
                match_date=date(2001, 1, 13),
                clubs=text_clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=None,
                source_root="/source",
                original_executable="/source/FOOTBAL.EXE",
            )

        left_players = tuple(
            SimpleNamespace(
                shirt_number=index + 1,
                first_name="Left",
                surname=f"Player{index}",
            )
            for index in range(11)
        )
        right_players = tuple(
            SimpleNamespace(
                shirt_number=index + 20,
                first_name="Right",
                surname=f"Player{index}",
            )
            for index in range(11)
        )
        player_rows = bind_prematch_player_rows(
            boundary,
            left_players=left_players,
            right_players=right_players,
        )
        dynamic_text = bind_prematch_dynamic_text_state(
            boundary,
            clubs=text_clubs,
            competition_name="F.A. Premier League",
            weather_code=0,
            temperature_c=12,
            home_team_name_override=None,
            away_team_name_override=None,
        )
        ratings = bind_prematch_rating_widths(
            boundary,
            left_widths=PrematchTeamRatingWidths(100, 101, 102, 103),
            right_widths=PrematchTeamRatingWidths(104, 105, 106, 107),
        )
        selectors = bind_prematch_selector_frames(
            boundary,
            source_frame_indices=(0, 0, 0, 0),
        )

        markers = []
        for side in (0, 1):
            for slot in range(11):
                markers.append(
                    BoundPrematchStartingXIMarker(
                        side=side,
                        slot_index=slot,
                        child_index=(10 if side == 0 else 21) + slot,
                        visible=True,
                        rect=OriginalRect(300 + slot, 200 + side * 40, 36, 32),
                        source_kind=(
                            "goalkeeper_original"
                            if slot == 0
                            else "custom_original"
                        ),
                        source_path=(
                            "goalkeeper.444"
                            if slot == 0
                            else f"team{side}.444"
                        ),
                        frame_number=None if slot == 0 else slot,
                        rgba=bytes(36 * 32 * 4),
                    )
                )
        marker_state = BoundPrematchStartingXIMarkers(markers=tuple(markers))

        supplied = bind_prematch_supplied_state(
            boundary=boundary,
            dynamic_text=dynamic_text,
            player_rows=player_rows,
            starting_xi_markers=marker_state,
            rating_rows=ratings,
            selector_frames=selectors,
        )
        self.assertIsInstance(supplied, BoundPrematchSuppliedState)
        self.assertEqual(supplied.source_child_count, 182)
        self.assertEqual(
            supplied.supplied_state_complete_families,
            tuple(role for role, _start, _end in PREMATCH_CHILD_ORDER_RANGES),
        )
        self.assertTrue(supplied.all_native_child_state_bound)
        self.assertTrue(supplied.full_cross_layer_draw_order_recovered)
        self.assertFalse(supplied.text_pixels_rasterized)
        self.assertFalse(supplied.flattened_frame_available)
        self.assertFalse(supplied.complete_prematch_frame)
        self.assertFalse(supplied.gate14_complete)

        contract = prematch_supplied_state_contract()
        self.assertTrue(contract["all_native_child_state_binding_available"])
        self.assertEqual(contract["source_child_count"], 182)
        self.assertFalse(contract["flattened_frame_available"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

        inconsistent_markers = BoundPrematchStartingXIMarkers(
            markers=tuple(
                BoundPrematchStartingXIMarker(
                    side=marker.side,
                    slot_index=marker.slot_index,
                    child_index=marker.child_index,
                    visible=False,
                    rect=None,
                    source_kind=None,
                    source_path=None,
                    frame_number=None,
                    rgba=None,
                )
                for marker in markers
            )
        )
        with self.assertRaisesRegex(
            PrematchSuppliedStateError,
            "visibility differs",
        ):
            bind_prematch_supplied_state(
                boundary=boundary,
                dynamic_text=dynamic_text,
                player_rows=player_rows,
                starting_xi_markers=inconsistent_markers,
                rating_rows=ratings,
                selector_frames=selectors,
            )

    def test_child_family_coverage_partitions_every_native_slot_fail_closed(self):
        coverage = prematch_child_family_coverage()
        self.assertEqual(
            tuple((family.role, family.start_index, family.end_index) for family in coverage),
            PREMATCH_CHILD_ORDER_RANGES,
        )
        self.assertEqual(
            tuple(
                index
                for family in coverage
                for index in range(family.start_index, family.end_index + 1)
            ),
            tuple(range(182)),
        )
        self.assertEqual(sum(family.source_control_count for family in coverage), 182)
        self.assertEqual(sum(family.represented_controls for family in coverage), 182)
        self.assertEqual(
            tuple(family.role for family in coverage if family.supplied_state_complete),
            ("live_background", "pitch", "top_bar", "team_badges", "rating_captions"),
        )
        self.assertTrue(
            all(
                family.blocker
                for family in coverage
                if not family.supplied_state_complete
            )
        )
        self.assertFalse(
            next(
                family
                for family in coverage
                if family.role == "starting_xi_pitch_markers"
            ).supplied_state_complete
        )
        self.assertEqual(
            next(
                family
                for family in coverage
                if family.role == "starting_xi_pitch_markers"
            ).represented_controls,
            22,
        )
        badge_family = next(
            family
            for family in coverage
            if family.role == "team_badges"
        )
        self.assertEqual(badge_family.represented_controls, 2)
        self.assertTrue(badge_family.supplied_state_complete)
        self.assertIsNone(badge_family.blocker)

    def test_contract_keeps_all_unresolved_claims_fail_closed(self):
        contract = prematch_surface_contract()
        self.assertEqual(contract["native_surface"], (800, 600))
        self.assertTrue(contract["team_backgrounds_selector_reused"])
        self.assertTrue(contract["team_backgrounds_loader_reused"])
        self.assertEqual(contract["team_badge_selector_va"], 0x40C850)
        self.assertTrue(contract["team_badge_selector_reused"])
        self.assertTrue(contract["team_badge_loader_reused"])
        self.assertTrue(contract["team_badge_pixels_bound_by_resource_loader"])
        self.assertEqual(contract["team_badge_control_count"], 2)
        self.assertEqual(contract["text_control_count"], 13)
        self.assertEqual(
            contract["text_control_roles"],
            (
                "fixture_header",
                "date_weather",
                "team_identity_0",
                "versus",
                "team_identity_1",
                "rating_left_gk",
                "rating_left_def",
                "rating_left_mid",
                "rating_left_att",
                "rating_right_gk",
                "rating_right_def",
                "rating_right_mid",
                "rating_right_att",
            ),
        )
        self.assertTrue(contract["dynamic_text_state_binding_available"])
        self.assertFalse(contract["dynamic_fixture_and_date_buffers_bound"])
        self.assertFalse(contract["team_identity_text_bound"])
        self.assertTrue(contract["fixed_versus_and_rating_captions_available"])
        self.assertEqual(contract["player_strip_row_count"], 36)
        self.assertTrue(contract["starting_xi_marker_resource_binding_available"])
        self.assertFalse(contract["starting_xi_marker_supplied_state_bound_by_resource_loader"])
        self.assertTrue(contract["player_strip_rows_source_geometry_available"])
        self.assertTrue(contract["reserve_variant_state_source_closed"])
        self.assertEqual(contract["player_text_row_count"], 36)
        self.assertTrue(contract["player_row_text_controls_source_closed"])
        self.assertTrue(contract["player_row_state_binding_available"])
        self.assertTrue(contract["player_row_display_name_reuses_source_formatter"])
        self.assertTrue(contract["player_row_shirt_number_reuses_source_formatter"])
        self.assertTrue(contract["selector_visual_state_source_closed"])
        self.assertTrue(contract["selector_supplied_frame_binding_available"])
        self.assertFalse(contract["selector_persistent_selected_visual"])
        self.assertEqual(contract["selector_modes"], (0, 1, 2, 3))
        self.assertEqual(contract["selector_events"], (4, 3, 2, 1))
        self.assertEqual(contract["rating_discriminators"], (3, 0, 1, 2))
        self.assertTrue(contract["rating_width_binding_available"])
        self.assertTrue(contract["rating_state_binding_available"])
        self.assertFalse(contract["rating_dynamic_widths_bound_by_resource_loader"])
        self.assertFalse(contract["rating_dynamic_widths_bound_to_cleanroom_state"])
        self.assertEqual(contract["source_child_count"], PREMATCH_CHILD_COUNT)
        self.assertEqual(contract["source_child_count"], 182)
        self.assertEqual(contract["child_order_ranges"], PREMATCH_CHILD_ORDER_RANGES)
        self.assertEqual(contract["represented_child_controls"], 182)
        self.assertEqual(
            contract["complete_child_families"],
            ("live_background", "pitch", "top_bar", "team_badges", "rating_captions"),
        )
        self.assertIn("starting_xi_pitch_markers", contract["unresolved_child_families"])
        self.assertIn("match_detail_selectors", contract["unresolved_child_families"])
        self.assertEqual(contract["child_family_coverage"], prematch_child_family_coverage())
        self.assertTrue(contract["full_cross_layer_draw_order_recovered"])
        self.assertFalse(contract["management_launch_trigger_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
