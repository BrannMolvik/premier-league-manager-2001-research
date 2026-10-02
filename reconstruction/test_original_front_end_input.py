"""Headless first-screen pointer tests against recovered original rectangles."""
import unittest

from front_end_session import FrontEndSession
from front_end_state import FrontEndCommand, FrontEndScreen, StartMenuControl
from original_front_end_input import (
    candidate_original_event,
    dispatch_original_pointer,
)
from original_front_end_layout import (
    PSTARTMENU_ACTIONS,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_EVENT,
    TEAMSELECT_START_RECT,
)


class DummyBackend:
    def __init__(self):
        self.choices = []

    def select_club(self, club_id):
        self.choices.append(club_id)
        return ("selected", club_id)


class OriginalFrontEndPointerTests(unittest.TestCase):
    def test_all_original_menu_control_rectangles_and_half_open_edges(self):
        self.assertEqual([action.event for action in PSTARTMENU_ACTIONS], [1, 2, 3, 4])
        for action in PSTARTMENU_ACTIONS:
            rect = action.rect
            with self.subTest(event=action.event):
                for x, y in (
                    (rect.x, rect.y),
                    (rect.right - 1, rect.y),
                    (rect.x, rect.bottom - 1),
                    (rect.right - 1, rect.bottom - 1),
                ):
                    self.assertEqual(
                        candidate_original_event(FrontEndScreen.START_MENU, x, y),
                        action.event,
                    )
                self.assertIsNone(candidate_original_event(
                    FrontEndScreen.START_MENU, rect.right, rect.y
                ))
                self.assertIsNone(candidate_original_event(
                    FrontEndScreen.START_MENU, rect.x, rect.bottom
                ))

    def test_exact_teamselect_back_and_start_rectangles(self):
        for event, rect in (
            (TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT),
            (TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT),
        ):
            with self.subTest(event=event):
                self.assertEqual(
                    candidate_original_event(
                        FrontEndScreen.TEAM_SELECT, rect.x, rect.y
                    ),
                    event,
                )
                self.assertEqual(
                    candidate_original_event(
                        FrontEndScreen.TEAM_SELECT,
                        rect.right - 1, rect.bottom - 1,
                    ),
                    event,
                )
                self.assertIsNone(candidate_original_event(
                    FrontEndScreen.TEAM_SELECT, rect.right, rect.y
                ))
                self.assertIsNone(candidate_original_event(
                    FrontEndScreen.TEAM_SELECT, rect.x, rect.bottom
                ))

    def test_background_and_unrecovered_hierarchy_regions_are_not_invented(self):
        for screen in (FrontEndScreen.START_MENU, FrontEndScreen.TEAM_SELECT):
            for x, y in ((0, 0), (799, 599), (-1, 100), (800, 100),
                         (200, -1), (200, 600)):
                self.assertIsNone(candidate_original_event(screen, x, y))
        with self.assertRaisesRegex(ValueError, "Unrecovered first-screen"):
            candidate_original_event(FrontEndScreen.MANAGEMENT, 0, 0)
        self.assertIsNone(
            candidate_original_event(FrontEndScreen.TEAM_SELECT, 20, 78)
        )
        for x, y in ((1.2, 478), (181, 478.5), (True, 478), (181, False)):
            with self.subTest(x=x, y=y):
                with self.assertRaises(TypeError):
                    candidate_original_event(FrontEndScreen.START_MENU, x, y)

    def test_pointer_routes_recovered_menu_and_teamselect_through_session(self):
        built = []

        def factory():
            backend = DummyBackend()
            built.append(backend)
            return backend

        session = FrontEndSession(factory)
        self.assertIsNone(dispatch_original_pointer(session, 0, 0))
        for x, y, command in (
            (181, 478, FrontEndCommand.CONTINUE_GAME),
            (355, 478, FrontEndCommand.LOAD_GAME),
            (181, 508, FrontEndCommand.QUIT_TO_WINDOWS),
        ):
            result = dispatch_original_pointer(session, x, y)
            self.assertEqual(result.transition.command, command)
            self.assertIs(session.navigation.screen, FrontEndScreen.START_MENU)
        self.assertEqual(built, [])

        result = dispatch_original_pointer(session, 7, 478)
        self.assertIs(result.transition.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIsNone(result.transition.command)
        self.assertEqual(len(built), 1)
        self.assertIsNone(dispatch_original_pointer(session, 20, 78))
        self.assertIsNone(session.selected_club_id)
        session.choose_club(12)
        start = dispatch_original_pointer(session, 426, 301)
        self.assertEqual(start.selected_manager, ("selected", 12))
        self.assertTrue(session.started)
        self.assertEqual(built[0].choices, [12])

    def test_teamselect_back_restores_menu_without_hidden_simulation_reset(self):
        session = FrontEndSession(DummyBackend)
        dispatch_original_pointer(session, 7, 478)
        current_backend = session.gameplay
        session.choose_club(12)
        result = dispatch_original_pointer(session, 225, 301)
        self.assertIs(result.transition.screen, FrontEndScreen.START_MENU)
        self.assertIs(session.gameplay, current_backend)
        self.assertIsNone(session.selected_club_id)
        self.assertFalse(session.started)
        self.assertEqual(session.gameplay.choices, [])


if __name__ == "__main__":
    unittest.main()
