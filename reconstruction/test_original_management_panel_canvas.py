from __future__ import annotations

from types import SimpleNamespace
import unittest

from ea444_decoder import EA444DecodedImage
from original_league_fixtures_art import build_league_fixtures_grid_art
from original_league_fixtures_resources import (
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
    LEAGUE_FIXTURES_RESOURCES,
)
from original_management_canvas import OriginalManagementCanvasFrame
from original_management_panel_canvas import (
    OriginalManagementPanelCanvasError,
    OriginalManagementPanelResources,
    build_management_panel_render,
)


def _image(resource, marker):
    width, height = resource.size
    return EA444DecodedImage(
        width,
        height,
        bytes((marker, marker + 1, marker + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


def _resources():
    grid = build_league_fixtures_grid_art(
        {
            FIXTURES_VERTICAL_GRID.name: _image(FIXTURES_VERTICAL_GRID, 7),
            FIXTURES_HORIZONTAL_GRID.name: _image(FIXTURES_HORIZONTAL_GRID, 17),
        }
    )
    return OriginalManagementPanelResources(
        league_fixtures_grid_art=grid,
        league_fixtures_resource_names=tuple(
            resource.name for resource in LEAGUE_FIXTURES_RESOURCES
        ),
    )


def _frame(panel_class, *, exact_art_staged=True):
    return OriginalManagementCanvasFrame(
        screen_size=(800, 600),
        menu_rect=(599, 96, 201, 504),
        panel_rect=None,
        presentation=SimpleNamespace(
            panel_class=panel_class,
            league_fixtures=(
                SimpleNamespace(exact_art_staged=exact_art_staged)
                if panel_class == "PLeagueFixtures"
                else None
            ),
        ),
        surrounding_background_recovered=False,
        pmenu_text_placement_recovered=True,
    )


class OriginalManagementPanelCanvasTests(unittest.TestCase):
    def test_league_fixtures_render_preserves_exact_36_grid_setup_calls(self):
        rendered = build_management_panel_render(
            _frame("PLeagueFixtures"),
            _resources(),
        )

        self.assertEqual(rendered.panel_class, "PLeagueFixtures")
        self.assertEqual(len(rendered.overlays), 36)
        self.assertEqual(
            tuple((item.x, item.y) for item in rendered.overlays[:12]),
            tuple((378 + 29 * n, 98) for n in range(12)),
        )
        self.assertEqual(
            tuple((item.x, item.y) for item in rendered.overlays[12:]),
            tuple((241, 235 + 14 * n) for n in range(24)),
        )
        self.assertTrue(
            all(item.role == "league_fixtures_grid" for item in rendered.overlays)
        )
        self.assertTrue(
            all(item.png.startswith(b"\x89PNG\r\n\x1a\n")
                for item in rendered.overlays)
        )
        self.assertEqual(
            {item.source_path for item in rendered.overlays},
            {
                FIXTURES_VERTICAL_GRID.source_path,
                FIXTURES_HORIZONTAL_GRID.source_path,
            },
        )
        self.assertIn(
            "fixture-cell 24x13 final placement/text composition",
            rendered.unresolved_pixel_boundaries,
        )

    def test_nonintegrated_panel_returns_no_guessed_pixels(self):
        rendered = build_management_panel_render(
            _frame("PSquadScreen"),
            _resources(),
        )
        self.assertEqual(rendered.overlays, ())
        self.assertEqual(rendered.panel_class, "PSquadScreen")
        self.assertIn(
            "panel-specific pixel composition is not yet integrated",
            rendered.unresolved_pixel_boundaries,
        )

    def test_fixtures_require_complete_staged_source_art(self):
        with self.assertRaisesRegex(
            OriginalManagementPanelCanvasError,
            "all six exact imported resources staged",
        ):
            build_management_panel_render(
                _frame("PLeagueFixtures", exact_art_staged=False),
                _resources(),
            )

    def test_resource_identity_and_types_fail_closed(self):
        grid = _resources().league_fixtures_grid_art
        with self.assertRaisesRegex(
            OriginalManagementPanelCanvasError,
            "staged resource identity",
        ):
            OriginalManagementPanelResources(
                league_fixtures_grid_art=grid,
                league_fixtures_resource_names=("fixtures_vert_grid",),
            )
        with self.assertRaisesRegex(
            OriginalManagementPanelCanvasError,
            "verified original management resources",
        ):
            build_management_panel_render(
                _frame("PLeagueFixtures"),
                object(),
            )


if __name__ == "__main__":
    unittest.main()
