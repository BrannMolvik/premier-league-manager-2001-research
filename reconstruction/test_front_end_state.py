import unittest

from front_end_state import (
    FrontEndCommand,
    FrontEndScreen,
    FrontEndState,
    ORIGINAL_PSTARTMENU_SCREEN_ID,
    StartMenuControl,
    TeamSelectControl,
    UnsupportedFrontEndControl,
)


class FrontEndStateTests(unittest.TestCase):
    def test_recovered_original_ids_are_kept_literal(self):
        self.assertEqual(ORIGINAL_PSTARTMENU_SCREEN_ID, 0x323)
        self.assertEqual(int(StartMenuControl.CONTINUE), 1)
        self.assertEqual(int(StartMenuControl.NEW_GAME), 2)
        self.assertEqual(int(StartMenuControl.LOAD_GAME), 3)
        self.assertEqual(int(StartMenuControl.QUIT_TO_WINDOWS), 4)
        self.assertEqual(int(TeamSelectControl.BACK), 0x29)
        self.assertEqual(int(TeamSelectControl.START_CONTINUE), 0x2A)

    def test_all_recovered_start_menu_ids_and_commands(self):
        expected = (
            (StartMenuControl.CONTINUE, FrontEndCommand.CONTINUE_GAME),
            (StartMenuControl.LOAD_GAME, FrontEndCommand.LOAD_GAME),
            (StartMenuControl.QUIT_TO_WINDOWS, FrontEndCommand.QUIT_TO_WINDOWS),
        )
        for control, command in expected:
            state = FrontEndState()
            transition = state.dispatch(control)
            self.assertIs(state.screen, FrontEndScreen.START_MENU)
            self.assertIs(transition.screen, FrontEndScreen.START_MENU)
            self.assertIs(transition.command, command)

    def test_new_game_moves_from_start_menu_to_team_select(self):
        state = FrontEndState()

        transition = state.dispatch(StartMenuControl.NEW_GAME)

        self.assertIs(state.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIs(transition.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIsNone(transition.command)

    def test_team_select_back_returns_to_start_menu(self):
        state = FrontEndState(screen=FrontEndScreen.TEAM_SELECT)

        transition = state.dispatch(TeamSelectControl.BACK)

        self.assertIs(state.screen, FrontEndScreen.START_MENU)
        self.assertIs(transition.screen, FrontEndScreen.START_MENU)
        self.assertIsNone(transition.command)

    def test_team_select_start_emits_command_without_simulating(self):
        state = FrontEndState(screen=FrontEndScreen.TEAM_SELECT)

        transition = state.dispatch(TeamSelectControl.START_CONTINUE)

        self.assertIs(state.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIs(transition.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIs(
            transition.command,
            FrontEndCommand.TEAMSELECT_START_CONTINUE,
        )

    def test_unrecovered_controls_fail_closed_instead_of_guessing(self):
        state = FrontEndState()
        with self.assertRaises(UnsupportedFrontEndControl):
            state.dispatch(8)

        state.screen = FrontEndScreen.TEAM_SELECT
        with self.assertRaises(UnsupportedFrontEndControl):
            state.dispatch(0x28)


if __name__ == "__main__":
    unittest.main()
