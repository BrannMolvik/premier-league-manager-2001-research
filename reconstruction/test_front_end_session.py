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
            session.dispatch(5)
        self.assertEqual(backends, [])
        self.assertIs(session.navigation.screen, FrontEndScreen.START_MENU)

    def test_recovered_non_new_menu_events_return_commands_without_loading_backend(self):
        for event, command in (
            (StartMenuControl.CONTINUE, FrontEndCommand.CONTINUE_GAME),
            (StartMenuControl.LOAD_GAME, FrontEndCommand.LOAD_GAME),
            (StartMenuControl.QUIT_TO_WINDOWS, FrontEndCommand.QUIT_TO_WINDOWS),
        ):
            with self.subTest(event=event):
                session, backends = self.new_session()
                outcome = session.dispatch(event)
                self.assertIs(outcome.transition.screen, FrontEndScreen.START_MENU)
                self.assertIs(outcome.transition.command, command)
                self.assertIsNone(outcome.selected_manager)
                self.assertEqual(backends, [])
                self.assertIsNone(session.gameplay)
                self.assertFalse(session.started)

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
        self.assertIs(session.navigation.screen, FrontEndScreen.MANAGEMENT)
        self.assertIs(result.transition.screen, FrontEndScreen.MANAGEMENT)
        self.assertTrue(session.started)

    def test_source_style_multiple_users_are_recorded_but_fail_closed_at_start(self):
        session, backends = self.new_session()
        session.dispatch(StartMenuControl.NEW_GAME)

        self.assertEqual(session.toggle_club_selection(12), (12,))
        self.assertEqual(session.toggle_club_selection(13), (12, 13))
        self.assertIsNone(session.selected_club_id)
        self.assertEqual(backends[0].selections, [])

        with self.assertRaisesRegex(FrontEndSessionError, "one human manager"):
            session.dispatch(TeamSelectControl.START_CONTINUE)
        self.assertFalse(session.started)
        self.assertEqual(backends[0].selections, [])

        self.assertEqual(session.toggle_club_selection(13), (12,))
        self.assertEqual(session.selected_club_id, 12)
        session.dispatch(TeamSelectControl.START_CONTINUE)
        self.assertEqual(backends[0].selections, [12])

    def test_source_style_selection_cap_is_six_and_unique(self):
        session, _backends = self.new_session()
        session.dispatch(StartMenuControl.NEW_GAME)
        for club_id in range(6):
            session.toggle_club_selection(club_id)
        self.assertEqual(session.selected_club_ids, tuple(range(6)))
        with self.assertRaisesRegex(FrontEndSessionError, "at most six"):
            session.toggle_club_selection(6)
        with self.assertRaisesRegex(ValueError, "unique"):
            session.set_club_selections((1, 1))

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
        self.assertEqual(session.selected_club_ids, ())
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

    def test_catalog_failure_never_enters_team_select(self):
        def failing_catalog():
            raise OSError("canonical catalog unavailable")

        session = FrontEndSession(
            lambda: StubGameplay(),
            team_select_catalog_factory=failing_catalog,
            gameplay_from_catalog_factory=lambda catalog: StubGameplay(),
        )

        with self.assertRaisesRegex(OSError, "canonical catalog unavailable"):
            session.dispatch(StartMenuControl.NEW_GAME)

        self.assertIs(session.navigation.screen, FrontEndScreen.START_MENU)
        self.assertIsNone(session.team_select_catalog)
        self.assertIsNone(session.gameplay)
        self.assertFalse(session.started)

    def test_deferred_gameplay_failure_leaves_team_select_retryable(self):
        catalog = object()

        def failing_gameplay(source):
            self.assertIs(source, catalog)
            raise RuntimeError("world build failed")

        session = FrontEndSession(
            lambda: StubGameplay(),
            team_select_catalog_factory=lambda: catalog,
            gameplay_from_catalog_factory=failing_gameplay,
        )
        session.dispatch(StartMenuControl.NEW_GAME)
        session.choose_club(12)

        with self.assertRaisesRegex(RuntimeError, "world build failed"):
            session.dispatch(TeamSelectControl.START_CONTINUE)

        self.assertIs(session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIs(session.team_select_catalog, catalog)
        self.assertIsNone(session.gameplay)
        self.assertEqual(session.selected_club_ids, (12,))
        self.assertFalse(session.started)

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

    def test_canonical_new_game_builds_catalog_and_defers_heavy_gameplay_until_start(self):
        verified = []
        parsed = []
        gameplay_builds = []

        fake_verify = types.ModuleType("verify")
        fake_data = types.ModuleType("fm2001_data")
        fake_gameplay = types.ModuleType("human_gameplay")

        def verify_canonical_files(game_dir):
            verified.append(Path(game_dir))

        class FakeDatabase:
            def __init__(self, game_dir):
                self.game_dir = Path(game_dir)
                self.countries = ()
                self.competitions = ()
                self.clubs = ()
                parsed.append(self)

        class FakeController:
            @classmethod
            def from_canonical_game_dir(cls, game_dir):
                raise AssertionError("New Game must not construct the heavy controller")

            @classmethod
            def from_verified_canonical_database(cls, game_dir, database):
                gameplay_builds.append((Path(game_dir), database))
                return StubGameplay()

        fake_verify.verify_canonical_files = verify_canonical_files
        fake_data.FM2001Database = FakeDatabase
        fake_gameplay.HumanGameplayController = FakeController

        with patch.dict(
            sys.modules,
            {
                "verify": fake_verify,
                "fm2001_data": fake_data,
                "human_gameplay": fake_gameplay,
            },
        ):
            session = FrontEndSession.for_canonical_game_dir("/canonical/game")
            self.assertEqual(verified, [])
            self.assertEqual(parsed, [])
            self.assertEqual(gameplay_builds, [])

            session.dispatch(StartMenuControl.NEW_GAME)

            self.assertEqual(verified, [Path("/canonical/game")])
            self.assertEqual(len(parsed), 1)
            self.assertIs(session.team_select_catalog, parsed[0])
            self.assertIsNone(session.gameplay)
            self.assertEqual(gameplay_builds, [])
            self.assertIs(session.navigation.screen, FrontEndScreen.TEAM_SELECT)

            session.choose_club(12)
            session.dispatch(TeamSelectControl.START_CONTINUE)

        self.assertEqual(
            gameplay_builds,
            [(Path("/canonical/game"), parsed[0])],
        )
        self.assertIsNotNone(session.gameplay)
        self.assertTrue(session.started)


if __name__ == "__main__":
    unittest.main()
