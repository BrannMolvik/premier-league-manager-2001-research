from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import unittest

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen, StartMenuControl, TeamSelectControl
from gate13_management_source_data import ClubHeaderView
from original_management_canvas import (
    OriginalManagementCanvasError,
    build_management_canvas_frame,
)
from original_management_presenter import OriginalManagementPresenter


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
        self.assertFalse(frame.pmenu_text_placement_recovered)
        self.assertFalse(frame.complete_source_pixel_frame_available)

        # The source-proven PMenu intentionally overlaps the right side of the
        # full-width PSquadScreen parent. Do not "fix" this native geometry.
        menu_x, menu_y, menu_w, menu_h = frame.menu_rect
        panel_x, panel_y, panel_w, panel_h = frame.panel_rect
        self.assertLess(menu_x, panel_x + panel_w)
        self.assertLess(menu_y, panel_y + panel_h)
        self.assertEqual(menu_x + menu_w, 800)
        self.assertEqual(panel_x + panel_w, 800)

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
