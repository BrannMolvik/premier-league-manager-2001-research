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
    source's database-load boundary. Native TeamSelect row toggles create/remove
    original user objects immediately, and up to six selected clubs can coexist.
    The current modern gameplay backend still exposes one HumanManagerState, so
    this seam records the source-backed selection set but defers its single-club
    backend activation until Start/Continue. Multiple selected users therefore
    fail closed instead of being silently collapsed to one manager.

    Club eligibility is delegated to that backend. At this stage it only
    implements the Premier League subset that the existing backend supports;
    the original game's broader multi-user gameplay continuation is not claimed.
    """

    gameplay_factory: Callable[[], GameplaySelectionBackend]
    navigation: FrontEndState = field(default_factory=FrontEndState)
    gameplay: GameplaySelectionBackend | None = None
    selected_club_ids: tuple[int, ...] = ()
    started: bool = False

    @property
    def selected_club_id(self) -> int | None:
        """Compatibility view for the single-manager backend."""
        if len(self.selected_club_ids) != 1:
            return None
        return self.selected_club_ids[0]

    @classmethod
    def for_canonical_game_dir(cls, game_dir: str | Path) -> "FrontEndSession":
        """Wire the real backend lazily; do not load simulation on module import."""

        canonical_dir = Path(game_dir)

        def make_gameplay() -> GameplaySelectionBackend:
            from human_gameplay import HumanGameplayController

            return HumanGameplayController.from_canonical_game_dir(canonical_dir)

        return cls(gameplay_factory=make_gameplay)

    def set_club_selections(self, club_ids) -> None:
        """Replace source-backed TeamSelect user choices without starting gameplay."""
        if self.navigation.screen is not FrontEndScreen.TEAM_SELECT or self.started:
            raise FrontEndSessionError("Clubs can only be chosen in TeamSelect.")
        values = tuple(club_ids)
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise ValueError("Club IDs must be integers.")
        normalized = tuple(int(value) for value in values)
        if len(normalized) != len(set(normalized)):
            raise ValueError("Club selections must be unique.")
        if len(normalized) > 6:
            raise FrontEndSessionError("Original TeamSelect supports at most six users.")
        self.selected_club_ids = normalized

    def choose_club(self, club_id: int) -> None:
        """Set one explicit compatibility choice for the single-manager backend."""
        if isinstance(club_id, bool):
            raise ValueError("Club ID must be an integer.")
        self.set_club_selections((int(club_id),))

    def toggle_club_selection(self, club_id: int) -> tuple[int, ...]:
        """Mirror an original club-row user toggle while preserving selection order."""
        if isinstance(club_id, bool):
            raise ValueError("Club ID must be an integer.")
        club_id = int(club_id)
        selected = list(self.selected_club_ids)
        if club_id in selected:
            selected.remove(club_id)
        else:
            if len(selected) >= 6:
                raise FrontEndSessionError("Original TeamSelect supports at most six users.")
            selected.append(club_id)
        self.set_club_selections(selected)
        return self.selected_club_ids

    def clear_club_selection(self) -> None:
        """Clear all TeamSelect user choices without changing gameplay state."""
        self.set_club_selections(())

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
            self.selected_club_ids = ()
            self.started = False
            return FrontEndSessionOutcome(transition)

        if screen is FrontEndScreen.TEAM_SELECT and control == TeamSelectControl.START_CONTINUE:
            if self.started:
                raise FrontEndSessionError("TeamSelect Start has already completed.")
            if self.gameplay is None or not self.selected_club_ids:
                raise FrontEndSessionError("Choose a club before starting the game.")
            if len(self.selected_club_ids) != 1:
                raise FrontEndSessionError(
                    "Multiple original TeamSelect users are source-proven, but the "
                    "modern gameplay backend currently supports one human manager."
                )
            # Backend validates eligibility and roster. A rejected selection
            # leaves TeamSelect active and can be retried with a different club.
            selected = self.gameplay.select_club(self.selected_club_ids[0])
            transition = self.navigation.dispatch(control)
            if transition.command is not FrontEndCommand.TEAMSELECT_START_CONTINUE:
                raise RuntimeError("Recovered TeamSelect command changed.")
            self.started = True
            return FrontEndSessionOutcome(transition, selected_manager=selected)

        transition = self.navigation.dispatch(control)
        if screen is FrontEndScreen.TEAM_SELECT and control == TeamSelectControl.BACK:
            # The backend is kept until a new New Game event replaces it;
            # no undocumented simulation reset is synthesized on Back.
            self.selected_club_ids = ()
        return FrontEndSessionOutcome(transition)
