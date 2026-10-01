"""Single presentation-only view over both verified original first-screen bundles.

This seam exposes the exact original 800x600 background, unmodified source
button atlas frames, confirmed action rectangles and original-language glyph
masks for the currently active front-end screen. Pointer dispatch goes through
the previously tested original rectangle translator into FrontEndSession.

The original Button@ease_2001 group/frame state machine and PStartMenu Zurich
caption alignment are now exposed from executable evidence. The mask-4 group's
user-facing meaning remains deliberately neutral. TeamSelect's hierarchy rows
remain locations, not invented team IDs. A successful Start event produces a
backend handoff command; it does not silently synthesize a recovered
manager-home renderer.
"""
from __future__ import annotations

from dataclasses import dataclass

from front_end_session import FrontEndSession, FrontEndSessionOutcome
from front_end_state import FrontEndScreen
from original_button_frames import (
    OriginalButtonAtlas, OriginalButtonFrame, OriginalButtonState,
)
from original_front_end_input import dispatch_original_pointer
from original_front_end_layout import (
    OriginalRect,
    PSTARTMENU_ACTIONS,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_EVENT,
    TEAMSELECT_START_RECT,
)
from original_pstartmenu_labels import PStartMenuCaption
from original_pstartmenu_resources import OriginalPStartMenuResources
from original_teamselect_resources import OriginalTeamSelectResources
from original_teamselect_hierarchy_art import OriginalTeamSelectHierarchyArt


@dataclass(frozen=True)
class OriginalActionPresentation:
    event: int
    rect: OriginalRect
    atlas: OriginalButtonAtlas
    caption: PStartMenuCaption | None = None

    def exact_source_frame(self, index: int) -> OriginalButtonFrame:
        """Select an explicit source-frame index."""
        return self.atlas.frame(index)

    def exact_native_frame(self, state: OriginalButtonState) -> OriginalButtonFrame:
        """Select from the executable-proven group/subframe state."""
        return self.atlas.frame_for_state(state)


@dataclass(frozen=True)
class OriginalFirstScreenSnapshot:
    screen: FrontEndScreen
    background_rgba: bytes
    controls: tuple[OriginalActionPresentation, ...]
    hierarchy_row_origins: tuple[tuple[int, int], ...] = ()
    hierarchy_art: OriginalTeamSelectHierarchyArt | None = None


@dataclass
class OriginalFirstScreenPresenter:
    session: FrontEndSession
    start_menu: OriginalPStartMenuResources
    team_select: OriginalTeamSelectResources

    def snapshot(self) -> OriginalFirstScreenSnapshot:
        """Return the source-aligned visual inputs for the active original screen."""
        screen = self.session.navigation.screen
        if screen is FrontEndScreen.START_MENU:
            controls = tuple(
                OriginalActionPresentation(
                    action.event,
                    action.rect,
                    self.start_menu.button_atlas,
                    caption,
                )
                for action, caption in zip(
                    PSTARTMENU_ACTIONS, self.start_menu.captions, strict=True
                )
            )
            return OriginalFirstScreenSnapshot(
                screen, self.start_menu.background_rgba, controls
            )
        if screen is FrontEndScreen.TEAM_SELECT:
            atlas = self.team_select.action_atlas
            controls = (
                OriginalActionPresentation(
                    TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT, atlas
                ),
                OriginalActionPresentation(
                    TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT, atlas
                ),
            )
            return OriginalFirstScreenSnapshot(
                screen,
                self.team_select.background_rgba,
                controls,
                self.team_select.hierarchy_row_origins,
                self.team_select.hierarchy_art,
            )
        raise RuntimeError(f"Original renderer not yet recovered for {screen!r}")

    def pointer(self, x: int, y: int) -> FrontEndSessionOutcome | None:
        return dispatch_original_pointer(self.session, x, y)

    def choose_club(self, club_id: int) -> None:
        """Delegate selection to the established session/backend boundary."""
        self.session.choose_club(club_id)
