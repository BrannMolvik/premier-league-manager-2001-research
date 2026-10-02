"""Fixed 800x600 host contract for the recovered FM2001 management shell.

This is deliberately a host/composition boundary, not a substitute skin.
It carries only screen/panel geometry already recovered from the canonical
executable and the live OriginalManagementPresenter snapshot. The surrounding
management background and exact PMenu label origin/clipping are still open, so
this module explicitly reports that a complete source-faithful pixel frame
cannot yet be drawn.

The point of this seam is to let TeamSelect Start enter the real PMenu-backed
management route without falling back to the generic ttk Play tab while keeping
unrecovered pixels fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass

from front_end_state import FrontEndScreen
from original_front_end_layout import SCREEN_SIZE
from original_management_presenter import (
    OriginalManagementPanelSnapshot,
    OriginalManagementPresenter,
)
from original_pmenu_chrome import PMENU_LIST_SCREEN_ORIGIN, PMENU_LIST_SIZE
from original_squad_resources import SQUAD_PANEL_RECT


class OriginalManagementCanvasError(ValueError):
    """The management host cannot be built from the recovered source boundary."""


@dataclass(frozen=True)
class OriginalManagementCanvasFrame:
    screen_size: tuple[int, int]
    menu_rect: tuple[int, int, int, int]
    panel_rect: tuple[int, int, int, int] | None
    presentation: OriginalManagementPanelSnapshot
    surrounding_background_recovered: bool
    pmenu_text_placement_recovered: bool

    @property
    def complete_source_pixel_frame_available(self) -> bool:
        return (
            self.surrounding_background_recovered
            and self.pmenu_text_placement_recovered
            and self.panel_rect is not None
        )


def build_management_canvas_frame(
    presenter: OriginalManagementPresenter,
) -> OriginalManagementCanvasFrame:
    """Bind a live management presenter to the fixed original screen surface.

    Only the fresh PSquadScreen parent rectangle is currently source-proven at
    the management-host level. Other integrated panels may still provide their
    own internal geometry through their snapshots, but this host does not
    invent a parent rectangle for them.
    """
    if not isinstance(presenter, OriginalManagementPresenter):
        raise OriginalManagementCanvasError(
            "Management canvas requires OriginalManagementPresenter"
        )
    session = presenter.session
    if session.navigation.screen is not FrontEndScreen.MANAGEMENT:
        raise OriginalManagementCanvasError(
            "Management canvas requires the recovered PMenu management state"
        )
    if not session.started:
        raise OriginalManagementCanvasError(
            "Management canvas requires a completed TeamSelect Start"
        )

    snapshot = presenter.snapshot()
    panel_rect = (
        SQUAD_PANEL_RECT
        if snapshot.panel_class == "PSquadScreen"
        else None
    )
    x, y = PMENU_LIST_SCREEN_ORIGIN
    width, height = PMENU_LIST_SIZE
    return OriginalManagementCanvasFrame(
        screen_size=SCREEN_SIZE,
        menu_rect=(x, y, width, height),
        panel_rect=panel_rect,
        presentation=snapshot,
        surrounding_background_recovered=False,
        pmenu_text_placement_recovered=False,
    )
