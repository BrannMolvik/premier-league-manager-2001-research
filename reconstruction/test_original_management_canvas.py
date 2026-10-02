from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen, StartMenuControl, TeamSelectControl
from gate13_management_source_data import ClubHeaderView
from original_management_canvas import (
    OriginalManagementCanvasError,
    OriginalPMenuRenderResources,
    build_management_canvas_frame,
    build_management_pmenu_render,
)
from original_management_presenter import OriginalManagementPresenter
from original_pmenu_chrome import (
    PMENU_CHILD_ARROW_RESOURCE,
    PMENU_CHILD_BOX_RESOURCE,
    PMENU_TITLE_ARROW_RESOURCE,
    PMENU_TITLE_BOX_RESOURCE,
    validate_original_pmenu_row_fonts,
)


class Backend:
    def select_club(self, club_id):
        return ("manager", club_id)


@dataclass(frozen=True)
class Row:
    source_roster_index: int
    player_id: int
    full_name: str
    current_position: int = 12
    condition: int = 90
    recent_form_average: float = 7.0
    current_role_rating: int = 61


class Bridge:
    def __init__(self, backend):
        self.backend = backend

    def club_header(self):
        return ClubHeaderView(12, "Source Club", "Source", date(2000, 8, 1))

    def squad_rows(self):
        return (Row(0, 1000, "Player 0"),)


def started_session():
    session = FrontEndSession(Backend)
    session.dispatch(StartMenuControl.NEW_GAME)
    session.choose_club(12)
    outcome = session.dispatch(TeamSelectControl.START_CONTINUE)
    assert outcome.transition.screen is FrontEndScreen.MANAGEMENT
    return session


def _solid_original_image(resource):
    width, height = resource.size
    rgba = bytearray(width * height * 4)
    for index in range(resource.frame_count):
        pixel = bytes((index, index, index, 255))
        row = pixel * width
        first_y = index * resource.frame_height
        for y in range(first_y, first_y + resource.frame_height):
            start = y * width * 4
            rgba[start:start + width * 4] = row
    return EA444DecodedImage(width, height, bytes(rgba), 0, 0)


def _pmenu_resources():
    source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
    fonts = {
        layout.row_kind: font
        for layout, font in validate_original_pmenu_row_fonts(source_root)
    }
    return OriginalPMenuRenderResources(
        title_arrow=_solid_original_image(PMENU_TITLE_ARROW_RESOURCE),
        title_box=_solid_original_image(PMENU_TITLE_BOX_RESOURCE),
        child_arrow=_solid_original_image(PMENU_CHILD_ARROW_RESOURCE),
        child_box=_solid_original_image(PMENU_CHILD_BOX_RESOURCE),
        title_font=fonts["title"],
        child_font=fonts["child"],
    )


class OriginalManagementCanvasTests(unittest.TestCase):
    def test_fresh_management_host_preserves_exact_fixed_geometry_and_open_pixels(self):
        presenter = OriginalManagementPresenter(
            started_session(), bridge_factory=Bridge
        )
        frame = build_management_canvas_frame(presenter)

        self.assertEqual(frame.screen_size, (800, 600))
        self.assertEqual(frame.menu_rect, (599, 96, 201, 504))
        self.assertEqual(frame.panel_rect, (0, 79, 800, 520))
        self.assertEqual(frame.presentation.panel_class, "PSquadScreen")
        self.assertEqual(frame.presentation.menu.selected_child_id, 0xCE)
        self.assertFalse(frame.surrounding_background_recovered)
        self.assertTrue(frame.pmenu_text_placement_recovered)
        self.assertFalse(frame.complete_source_pixel_frame_available)

        # The source-proven PMenu intentionally overlaps the right side of the
        # full-width PSquadScreen parent. Do not "fix" this native geometry.
        menu_x, menu_y, menu_w, menu_h = frame.menu_rect
        panel_x, panel_y, panel_w, panel_h = frame.panel_rect
        self.assertLess(menu_x, panel_x + panel_w)
        self.assertLess(menu_y, panel_y + panel_h)
        self.assertEqual(menu_x + menu_w, 800)
        self.assertEqual(panel_x + panel_w, 800)

    def test_live_pmenu_compositor_uses_recovered_static_states_fonts_and_clipping(self):
        presenter = OriginalManagementPresenter(
            started_session(), bridge_factory=Bridge
        )
        frame = build_management_canvas_frame(presenter)
        rendered = build_management_pmenu_render(frame, _pmenu_resources())

        self.assertEqual(rendered.list_screen_origin, (599, 96))
        self.assertEqual(rendered.list_size, (201, 504))
        self.assertEqual(rendered.row_count, 15)
        self.assertEqual(len(rendered.overlays), 45)
        self.assertTrue(all(item.png.startswith(b"\x89PNG\r\n\x1a\n")
                            for item in rendered.overlays))

        def overlay(menu_id, role):
            matches = [
                item for item in rendered.overlays
                if item.menu_id == menu_id and item.role == role
            ]
            self.assertEqual(len(matches), 1)
            return matches[0]

        team_arrow = overlay(2, "arrow")
        team_box = overlay(2, "background")
        team_text = overlay(2, "text")
        self.assertEqual(team_arrow.source_index, 10)
        self.assertEqual((team_arrow.width, team_arrow.height), (30, 29))
        self.assertEqual(team_box.source_index, 2)
        self.assertEqual((team_box.x, team_box.y), (30, 0))
        self.assertEqual(team_text.source_path, "Fonts/Zurich_XCn_BT_25pixel.fnt")
        self.assertEqual((team_text.x, team_text.y), (30, 1))
        self.assertEqual(team_text.native_color_16, 0xFFFF)
        self.assertLessEqual(team_text.x + team_text.width, 198)
        self.assertLessEqual(team_text.y + team_text.height, 29)

        squad_arrow = overlay(0xCE, "arrow")
        squad_box = overlay(0xCE, "background")
        squad_text = overlay(0xCE, "text")
        self.assertEqual(squad_arrow.source_index, 11)
        self.assertEqual(squad_box.source_index, 2)
        self.assertEqual(squad_text.source_path, "Fonts/Zurich_XCn_BT_16pixel.fnt")
        self.assertEqual((squad_text.x, squad_text.y), (30, 46))
        self.assertEqual(squad_text.native_color_16, 0xFFFF)
        self.assertLessEqual(squad_text.x + squad_text.width, 198)
        self.assertLessEqual(squad_text.y + squad_text.height, 58)

        stats_arrow = overlay(0xCA, "arrow")
        stats_box = overlay(0xCA, "background")
        stats_text = overlay(0xCA, "text")
        self.assertEqual(stats_arrow.source_index, 0)
        self.assertEqual(stats_box.source_index, 0)
        self.assertEqual(stats_text.native_color_16, 0x0000)
        self.assertEqual((stats_text.x, stats_text.y), (30, 75))
        self.assertLessEqual(stats_text.y + stats_text.height, 87)

    def test_pmenu_compositor_rejects_unverified_resource_object(self):
        presenter = OriginalManagementPresenter(
            started_session(), bridge_factory=Bridge
        )
        frame = build_management_canvas_frame(presenter)
        with self.assertRaisesRegex(
            OriginalManagementCanvasError,
            "verified decoded original resources",
        ):
            build_management_pmenu_render(frame, object())

    def test_host_rejects_pre_management_session(self):
        session = FrontEndSession(Backend)
        session.dispatch(StartMenuControl.NEW_GAME)
        presenter = OriginalManagementPresenter(session, bridge_factory=Bridge)
        with self.assertRaisesRegex(
            OriginalManagementCanvasError,
            "PMenu management state",
        ):
            build_management_canvas_frame(presenter)

    def test_host_type_is_fail_closed(self):
        with self.assertRaisesRegex(
            OriginalManagementCanvasError,
            "OriginalManagementPresenter",
        ):
            build_management_canvas_frame(object())


if __name__ == "__main__":
    unittest.main()
