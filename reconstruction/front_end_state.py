from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum


# Recovered from the original front-end factory/navigation path.
ORIGINAL_PSTARTMENU_SCREEN_ID = 0x323


class FrontEndScreen(Enum):
    START_MENU = "pstartmenu"
    TEAM_SELECT = "team_select"
    # Source-proven post-TeamSelect owner: PMenu with a concrete content panel.
    MANAGEMENT = "pmenu_management"


class StartMenuControl(IntEnum):
    # Confirmed PStartMenu event/control IDs from 0x4C1BA0/0x4C3770.
    CONTINUE = 1
    NEW_GAME = 2
    LOAD_GAME = 3
    QUIT_TO_WINDOWS = 4


class TeamSelectControl(IntEnum):
    # Confirmed PMain@TeamSelect event/control IDs.
    BACK = 0x29
    START_CONTINUE = 0x2A


class FrontEndCommand(Enum):
    CONTINUE_GAME = "continue_game"
    LOAD_GAME = "load_game"
    QUIT_TO_WINDOWS = "quit_to_windows"
    TEAMSELECT_START_CONTINUE = "teamselect_start_continue"


class UnsupportedFrontEndControl(ValueError):
    pass


@dataclass(frozen=True)
class FrontEndTransition:
    screen: FrontEndScreen
    command: FrontEndCommand | None = None


@dataclass
class FrontEndState:
    """Presentation-only navigation state for the recovered first front-end slice.

    This module deliberately has no gameplay/simulation imports. Rendering code
    may translate confirmed original control IDs into these transitions, while a
    separate application/controller layer decides how a command calls the stable
    simulation backend.
    """

    screen: FrontEndScreen = FrontEndScreen.START_MENU

    def dispatch(self, control_id: int) -> FrontEndTransition:
        if self.screen is FrontEndScreen.START_MENU:
            return self._dispatch_start_menu(control_id)
        if self.screen is FrontEndScreen.TEAM_SELECT:
            return self._dispatch_team_select(control_id)
        raise RuntimeError(f"Unsupported front-end screen: {self.screen!r}")

    def _dispatch_start_menu(self, control_id: int) -> FrontEndTransition:
        control_id = int(control_id)
        if control_id == int(StartMenuControl.CONTINUE):
            return FrontEndTransition(
                screen=self.screen,
                command=FrontEndCommand.CONTINUE_GAME,
            )
        if control_id == int(StartMenuControl.NEW_GAME):
            self.screen = FrontEndScreen.TEAM_SELECT
            return FrontEndTransition(screen=self.screen)
        if control_id == int(StartMenuControl.LOAD_GAME):
            return FrontEndTransition(
                screen=self.screen,
                command=FrontEndCommand.LOAD_GAME,
            )
        if control_id == int(StartMenuControl.QUIT_TO_WINDOWS):
            return FrontEndTransition(
                screen=self.screen,
                command=FrontEndCommand.QUIT_TO_WINDOWS,
            )
        raise UnsupportedFrontEndControl(
            f"Unrecovered PStartMenu control ID: {control_id:#x}"
        )

    def _dispatch_team_select(self, control_id: int) -> FrontEndTransition:
        control_id = int(control_id)
        if control_id == int(TeamSelectControl.BACK):
            self.screen = FrontEndScreen.START_MENU
            return FrontEndTransition(screen=self.screen)
        if control_id == int(TeamSelectControl.START_CONTINUE):
            self.screen = FrontEndScreen.MANAGEMENT
            return FrontEndTransition(
                screen=self.screen,
                command=FrontEndCommand.TEAMSELECT_START_CONTINUE,
            )
        raise UnsupportedFrontEndControl(
            f"Unrecovered TeamSelect control ID: {control_id:#x}"
        )
