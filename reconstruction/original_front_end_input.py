"""Translate proven original first-screen control rectangles into session events.

The original executable establishes the PStartMenu action rectangles and
TeamSelect Back/Start rectangles. This adapter maps pixels in the original
800x600 coordinate system to those recovered event IDs and dispatches through
the existing application seam. It does not simulate an unknown hover frame,
alpha-based hit policy, hierarchy-row selection or gameplay-side Continue/
Load/Quit handling; those require independent original-source evidence.
"""

from __future__ import annotations

from front_end_session import FrontEndSession, FrontEndSessionOutcome
from front_end_state import FrontEndScreen
from original_front_end_layout import (
    PSTARTMENU_ACTIONS,
    SCREEN_SIZE,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_EVENT,
    TEAMSELECT_START_RECT,
    OriginalRect,
)


def _inside(rect: OriginalRect, x: int, y: int) -> bool:
    """Half-open rectangle containment, not a claim about original alpha hit tests."""
    return rect.x <= x < rect.right and rect.y <= y < rect.bottom


def candidate_original_event(
    screen: FrontEndScreen, x: int, y: int
) -> int | None:
    """Return a rectangle-matched recovered event, or None for untouched space.

    The inputs use original unscaled 800x600 pixels. Callers that scale the
    rendered screen must first convert their pointer position to those pixels.
    """
    if type(x) is not int or type(y) is not int:
        raise TypeError("Original screen pointer coordinates must be integer pixels")
    if not 0 <= x < SCREEN_SIZE[0] or not 0 <= y < SCREEN_SIZE[1]:
        return None
    if screen is FrontEndScreen.START_MENU:
        for action in PSTARTMENU_ACTIONS:
            if _inside(action.rect, x, y):
                return action.event
        return None
    if screen is FrontEndScreen.TEAM_SELECT:
        for event, rect in (
            (TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT),
            (TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT),
        ):
            if _inside(rect, x, y):
                return event
        return None
    if screen is FrontEndScreen.MANAGEMENT:
        # Management owns a separate PMenu/panel pointer router. The first-
        # screen adapter must not reinterpret management pixels as menu events.
        return None
    raise ValueError(f"Unrecovered first-screen pointer target: {screen!r}")


def dispatch_original_pointer(
    session: FrontEndSession, x: int, y: int
) -> FrontEndSessionOutcome | None:
    """Bridge a recovered original control rectangle to the existing session.

    A click outside a confirmed action does nothing. This intentionally leaves
    the original TeamSelect hierarchy rows to their separate source recovery.
    """
    event = candidate_original_event(session.navigation.screen, x, y)
    return None if event is None else session.dispatch(event)
