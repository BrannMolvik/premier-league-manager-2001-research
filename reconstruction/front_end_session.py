"""Gate 13 application boundary for the proven PStartMenu -> TeamSelect flow.

The recovered control IDs live in front_end_state.py. This module translates
those presentation events into calls on an injected gameplay backend without
importing simulation modules at import time. It is not a visual replacement for
the original FM2001 UI; original graphics/layout still require source recovery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from front_end_state import (
    FrontEndCommand,
    FrontEndScreen,
    FrontEndState,
    FrontEndTransition,
    StartMenuControl,
    TeamSelectControl,
)


class GameplaySelectionBackend(Protocol):
    def select_club(self, club_id: int) -> object:
        ...


class FrontEndSessionError(RuntimeError):
    """The application boundary cannot yet honor a recovered UI action."""


@dataclass(frozen=True)
class FrontEndSessionOutcome:
    transition: FrontEndTransition
    selected_manager: object | None = None


@dataclass
class FrontEndSession:
    """Keep original navigation, team choice and backend startup separate.

    The factory runs on confirmed PStartMenu New Game (event 2), matching the
    source's database-load boundary. Merely choosing a team is presentation
    state; only the proven TeamSelect Start/Continue event (0x2A) invokes the
    modern backend's select_club method.

    Club eligibility is delegated to that backend. At this stage it only
    implements the Premier League subset that the existing backend supports;
    the original game's broader country/competition chooser is not claimed.
    """

    gameplay_factory: Callable[[], GameplaySelectionBackend]
    navigation: FrontEndState = field(default_factory=FrontEndState)
    gameplay: GameplaySelectionBackend | None = None
    selected_club_id: int | None = None
    started: bool = False

    @classmethod
    def for_canonical_game_dir(cls, game_dir: str | Path) -> "FrontEndSession":
        """Wire the real backend lazily; do not load simulation on module import."""

        canonical_dir = Path(game_dir)

        def make_gameplay() -> GameplaySelectionBackend:
            from human_gameplay import HumanGameplayController

            return HumanGameplayController.from_canonical_game_dir(canonical_dir)

        return cls(gameplay_factory=make_gameplay)

    def choose_club(self, club_id: int) -> None:
        """Store a user choice without starting or changing gameplay state."""
        if self.navigation.screen is not FrontEndScreen.TEAM_SELECT or self.started:
            raise FrontEndSessionError("Clubs can only be chosen in TeamSelect.")
        if isinstance(club_id, bool):
            raise ValueError("Club ID must be an integer.")
        self.selected_club_id = int(club_id)

    def dispatch(self, control_id: int) -> FrontEndSessionOutcome:
        """Dispatch only recovered controls and preserve retryable failures."""
        control = int(control_id)
        screen = self.navigation.screen

        if screen is FrontEndScreen.START_MENU and control == StartMenuControl.NEW_GAME:
            # Do not move off PStartMenu if the database cannot be loaded.
            backend = self.gameplay_factory()
            if backend is None:
                raise FrontEndSessionError("New Game backend factory returned nothing.")
            transition = self.navigation.dispatch(control)
            self.gameplay = backend
            self.selected_club_id = None
            self.started = False
            return FrontEndSessionOutcome(transition)

        if screen is FrontEndScreen.TEAM_SELECT and control == TeamSelectControl.START_CONTINUE:
            if self.started:
                raise FrontEndSessionError("TeamSelect Start has already completed.")
            if self.gameplay is None or self.selected_club_id is None:
                raise FrontEndSessionError("Choose a club before starting the game.")
            # Backend validates eligibility and roster. A rejected selection
            # leaves TeamSelect active and can be retried with a different club.
            selected = self.gameplay.select_club(self.selected_club_id)
            transition = self.navigation.dispatch(control)
            if transition.command is not FrontEndCommand.TEAMSELECT_START_CONTINUE:
                raise RuntimeError("Recovered TeamSelect command changed.")
            self.started = True
            return FrontEndSessionOutcome(transition, selected_manager=selected)

        transition = self.navigation.dispatch(control)
        if screen is FrontEndScreen.TEAM_SELECT and control == TeamSelectControl.BACK:
            # The backend is kept until a new New Game event replaces it;
            # no undocumented simulation reset is synthesized on Back.
            self.selected_club_id = None
        return FrontEndSessionOutcome(transition)
