import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from front_end_session import FrontEndSession, FrontEndSessionError
from front_end_state import (
    FrontEndCommand,
    FrontEndScreen,
    StartMenuControl,
    TeamSelectControl,
    UnsupportedFrontEndControl,
)


class StubGameplay:
    def __init__(self, eligible=(12,)):
        self.eligible = set(eligible)
        self.selections = []

    def select_club(self, club_id):
        self.selections.append(club_id)
        if club_id not in self.eligible:
            raise ValueError("unsupported club")
        return ("human-manager", club_id)


class FrontEndSessionTests(unittest.TestCase):
    def new_session(self):
        backends = []

        def factory():
            backend = StubGameplay()
            backends.append(backend)
            return backend

        return FrontEndSession(factory), backends

    def test_new_game_creates_backend_at_confirmed_event_and_enters_team_select(self):
        session, backends = self.new_session()
        self.assertEqual(len(backends), 0)

        result = session.dispatch(StartMenuControl.NEW_GAME)

        self.assertEqual(len(backends), 1)
        self.assertIs(session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIs(result.transition.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIsNone(result.selected_manager)
        self.assertEqual(backends[0].selections, [])

    def test_unsupported_start_menu_event_does_not_construct_backend(self):
        session, backends = self.new_session()
        with self.assertRaises(UnsupportedFrontEndControl):
            session.dispatch(1)
        self.assertEqual(backends, [])
        self.assertIs(session.navigation.screen, FrontEndScreen.START_MENU)

    def test_choosing_team_does_not_mutate_gameplay_until_start(self):
        session, backends = self.new_session()
        session.dispatch(StartMenuControl.NEW_GAME)
        session.choose_club(12)
        self.assertEqual(backends[0].selections, [])

        result = session.dispatch(TeamSelectControl.START_CONTINUE)

        self.assertEqual(backends[0].selections, [12])
        self.assertEqual(result.selected_manager, ("human-manager", 12))
        self.assertIs(
            result.transition.command,
            FrontEndCommand.TEAMSELECT_START_CONTINUE,
        )
        self.assertIs(session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertTrue(session.started)

    def test_requires_explicit_club_selection_no_default_team(self):
        session, backends = self.new_session()
        session.dispatch(StartMenuControl.NEW_GAME)
        with self.assertRaisesRegex(FrontEndSessionError, "Choose a club"):
            session.dispatch(TeamSelectControl.START_CONTINUE)
        self.assertEqual(backends[0].selections, [])
        self.assertFalse(session.started)

    def test_backend_rejected_selection_stays_retryable(self):
        session, backends = self.new_session()
        session.dispatch(StartMenuControl.NEW_GAME)
        session.choose_club(999)
        with self.assertRaisesRegex(ValueError, "unsupported club"):
            session.dispatch(TeamSelectControl.START_CONTINUE)
        self.assertIs(session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertFalse(session.started)
        session.choose_club(12)
        session.dispatch(TeamSelectControl.START_CONTINUE)
        self.assertEqual(backends[0].selections, [999, 12])
        self.assertTrue(session.started)

    def test_back_only_changes_navigation_not_backend_or_team_state(self):
        session, backends = self.new_session()
        session.dispatch(StartMenuControl.NEW_GAME)
        backend = backends[0]
        session.choose_club(12)

        result = session.dispatch(TeamSelectControl.BACK)

        self.assertIs(result.transition.screen, FrontEndScreen.START_MENU)
        self.assertIsNone(session.selected_club_id)
        self.assertIs(session.gameplay, backend)
        self.assertEqual(backend.selections, [])

        session.dispatch(StartMenuControl.NEW_GAME)
        self.assertIsNot(session.gameplay, backend)
        self.assertIsNone(session.selected_club_id)

    def test_factory_failure_never_changes_screen(self):
        def failing_factory():
            raise OSError("game data missing")

        session = FrontEndSession(failing_factory)
        with self.assertRaisesRegex(OSError, "game data missing"):
            session.dispatch(StartMenuControl.NEW_GAME)
        self.assertIs(session.navigation.screen, FrontEndScreen.START_MENU)
        self.assertIsNone(session.gameplay)

    def test_duplicate_start_and_out_of_context_choice_fail(self):
        session, backends = self.new_session()
        with self.assertRaises(FrontEndSessionError):
            session.choose_club(12)
        session.dispatch(StartMenuControl.NEW_GAME)
        with self.assertRaises(ValueError):
            session.choose_club(True)
        session.choose_club(12)
        session.dispatch(TeamSelectControl.START_CONTINUE)
        with self.assertRaises(FrontEndSessionError):
            session.dispatch(TeamSelectControl.START_CONTINUE)
        with self.assertRaises(FrontEndSessionError):
            session.choose_club(12)
        self.assertEqual(backends[0].selections, [12])

    def test_canonical_game_directory_is_lazily_passed_to_real_backend_factory(self):
        requested = []
        fake_module = types.ModuleType("human_gameplay")

        class FakeController:
            @classmethod
            def from_canonical_game_dir(cls, game_dir):
                requested.append(game_dir)
                return StubGameplay()

        fake_module.HumanGameplayController = FakeController

        with patch.dict(sys.modules, {"human_gameplay": fake_module}):
            session = FrontEndSession.for_canonical_game_dir("/canonical/game")
            self.assertEqual(requested, [])
            session.dispatch(StartMenuControl.NEW_GAME)

        self.assertEqual(requested, [Path("/canonical/game")])


if __name__ == "__main__":
    unittest.main()
