"""Regression coverage for exact supplied PPreMatch text rasterization."""
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
from gate14_prematch_surface import (
    bind_prematch_dynamic_text_state,
    bind_prematch_player_rows,
    build_verified_prematch_surface_boundary,
)
from gate14_prematch_text_raster import (
    PREMATCH_DIRECT_TEXT_CHILD_INDEX,
    PrematchTextFontSet,
    PrematchTextRasterError,
    build_prematch_text_rasters,
    prematch_text_raster_contract,
    source_text_line_origin,
)
from gate14_prematch_text_style import (
    PREMATCH_HEADER_STYLE,
    PREMATCH_ROW_STYLE,
    PREMATCH_TEAM_STYLE,
    PREMATCH_VERSUS_STYLE,
)
from original_front_end_layout import OriginalRect
from original_prematch_panel import PREMATCH_ALL_EA444_SPECS


class FakeFont:
    def __init__(self, style, *, glyph_width):
        self.atlas_width, self.atlas_height = style.atlas_size
        self._line_height = style.native_line_height
        self._glyph_width = glyph_width

    def native_line_height(self):
        return self._line_height

    def measure_text(self, text):
        return len(text) * self._glyph_width

    def render_text_alpha(self, text):
        width = self.measure_text(text)
        height = self._line_height
        return SimpleNamespace(
            width=width,
            height=height,
            alpha=bytes([255]) * (width * height),
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


def club(country_id, basename, fan_base_index, short_name, stadium):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
        short_name=short_name,
        stadium=stadium,
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


class PrematchTextRasterTests(unittest.TestCase):
    def setUp(self):
        self.clubs = {
            10: club(26, "arsenal", 25, "Arsenal", "Highbury"),
            11: club(26, "chelsea", 14, "Chelsea", "Stamford Bridge"),
        }
        self.countries = {
            26: SimpleNamespace(graphics_directory="England"),
        }
        self.fonts = PrematchTextFontSet(
            header=FakeFont(PREMATCH_HEADER_STYLE, glyph_width=4),
            team=FakeFont(PREMATCH_TEAM_STYLE, glyph_width=5),
            versus=FakeFont(PREMATCH_VERSUS_STYLE, glyph_width=6),
            row=FakeFont(PREMATCH_ROW_STYLE, glyph_width=4),
        )

    def _selection(self):
        return build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=self.clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )

    def _boundary(self):
        selection = self._selection()
        with (
            patch(
                "gate14_prematch_surface.build_fastview_surfaced_resource_selection",
                return_value=selection,
            ),
            patch(
                "gate14_prematch_surface.load_verified_fastview_surfaced_resources",
                return_value=fake_surfaced_resources(selection),
            ),
            patch(
                "gate14_prematch_surface.load_verified_original_prematch_resources",
                return_value=FakePrematchResources(),
            ),
        ):
            return build_verified_prematch_surface_boundary(
                match_date=date(2001, 1, 13),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=None,
                source_root="/source",
                original_executable="/source/FOOTBAL.EXE",
            )

    def test_native_21_22_24_alignment_origins_are_exact(self):
        font = FakeFont(PREMATCH_ROW_STYLE, glyph_width=4)
        rect = OriginalRect(10, 20, 100, 30)
        text = "abcdefghij"
        self.assertEqual(
            source_text_line_origin(font, text, rect, 0x21),
            (10, 26),
        )
        self.assertEqual(
            source_text_line_origin(font, text, rect, 0x22),
            (70, 26),
        )
        self.assertEqual(
            source_text_line_origin(font, text, rect, 0x24),
            (40, 26),
        )

    def test_negative_vertical_center_delta_truncates_toward_zero(self):
        font = FakeFont(PREMATCH_ROW_STYLE, glyph_width=4)
        rect = OriginalRect(37, 153, 25, 14)
        self.assertEqual(
            source_text_line_origin(font, "1", rect, 0x24),
            (47, 151),
        )

    def test_supplied_state_rasterizes_every_visible_text_child_and_records_hidden_rows(self):
        boundary = self._boundary()
        dynamic = bind_prematch_dynamic_text_state(
            boundary,
            clubs=self.clubs,
            competition_name="F.A. Premier League",
            weather_code=2,
            temperature_c=-3,
            home_team_name_override=None,
            away_team_name_override=None,
        )
        left = tuple(
            SimpleNamespace(
                shirt_number=index + 1,
                first_name="Left",
                surname=f"Player{index}",
            )
            for index in range(12)
        )
        right = tuple(
            SimpleNamespace(
                shirt_number=index + 20,
                first_name="Right",
                surname=f"Player{index}",
            )
            for index in range(11)
        )
        players = bind_prematch_player_rows(
            boundary,
            left_players=left,
            right_players=right,
        )

        rasters = build_prematch_text_rasters(
            boundary,
            dynamic_text=dynamic,
            player_rows=players,
            fonts=self.fonts,
        )

        self.assertEqual(len(rasters.registered_text_child_indices), 85)
        self.assertEqual(len(rasters.children), 13 + (12 + 11) * 2)
        self.assertEqual(len(rasters.hidden_text_child_indices), (18 - 12) * 2 + (18 - 11) * 2)
        self.assertEqual(
            set(child.child_index for child in rasters.children)
            | set(rasters.hidden_text_child_indices),
            set(rasters.registered_text_child_indices),
        )
        self.assertEqual(
            rasters.children[0].child_index,
            PREMATCH_DIRECT_TEXT_CHILD_INDEX["fixture_header"],
        )
        self.assertTrue(all(child.rgba_sha256 for child in rasters.children))
        self.assertTrue(rasters.text_pixels_rasterized)
        self.assertFalse(rasters.complete_prematch_frame)
        self.assertFalse(rasters.gate14_complete)

        by_index = {child.child_index: child for child in rasters.children}
        left_team = by_index[7]
        right_team = by_index[9]
        self.assertEqual(left_team.raw_flags, 0x22)
        self.assertEqual(right_team.raw_flags, 0x21)
        self.assertEqual(
            left_team.line_origin[0],
            left_team.rect.x + left_team.rect.width
            - self.fonts.team.measure_text(left_team.text),
        )
        self.assertEqual(right_team.line_origin[0], right_team.rect.x)

    def test_font_set_rejects_metric_drift_and_rotated_text_fails_closed(self):
        with self.assertRaisesRegex(PrematchTextRasterError, "line-height"):
            PrematchTextFontSet(
                header=FakeFont(PREMATCH_HEADER_STYLE, glyph_width=4),
                team=FakeFont(PREMATCH_TEAM_STYLE, glyph_width=5),
                versus=FakeFont(PREMATCH_VERSUS_STYLE, glyph_width=6),
                row=SimpleNamespace(
                    atlas_width=PREMATCH_ROW_STYLE.atlas_size[0],
                    atlas_height=PREMATCH_ROW_STYLE.atlas_size[1],
                    measure_text=lambda text: len(text),
                    native_line_height=lambda: 99,
                    render_text_alpha=lambda text: None,
                ),
            )
        with self.assertRaisesRegex(PrematchTextRasterError, "rotated"):
            source_text_line_origin(
                self.fonts.row,
                "Player",
                OriginalRect(0, 0, 100, 20),
                0x40 | 0x21,
            )

    def test_contract_retains_frame_boundary(self):
        contract = prematch_text_raster_contract()
        self.assertEqual(contract["registered_text_child_count"], 85)
        self.assertTrue(contract["control_clipping_preserved"])
        self.assertTrue(contract["source_font_hashes_required"])
        self.assertTrue(contract["text_pixels_rasterized_for_supplied_state"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
