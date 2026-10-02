"""First source-backed ordinary-management composition after TeamSelect Start.

This seam joins the already recovered PMenu and PSquadList presenters to the
read-only management bridge. It does not render unknown shell pixels, mutate
gameplay, or infer scrolling: the initial viewport is the first 20 entries in
the bridge's source-preserved roster order and reports any rows beyond it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from front_end_session import FrontEndSession
from gate13_management_source_data import (
    ClubHeaderView,
    ManagementSourceDataBridge,
)
from original_pmenu_presenter import OriginalPMenuSnapshot, build_fresh_pmenu_snapshot
from original_squad_presenter import (
    OriginalSquadViewportSnapshot,
    build_squad_row_viewport,
)
from original_squad_resources import SQUAD_VISIBLE_ROW_COUNT


class OriginalManagementPresentationError(ValueError):
    """The verified front-end/backend seam is not ready for management UI."""


@dataclass(frozen=True)
class OriginalFreshManagementSnapshot:
    club: ClubHeaderView
    menu: OriginalPMenuSnapshot
    squad: OriginalSquadViewportSnapshot
    source_squad_count: int
    rows_beyond_initial_viewport: int


def build_fresh_management_snapshot(
    session: FrontEndSession,
    *,
    bridge_factory: Callable[[object], object] = ManagementSourceDataBridge,
) -> OriginalFreshManagementSnapshot:
    """Compose the fresh PMenu -> PSquadScreen landing after a valid Start."""
    if not isinstance(session, FrontEndSession):
        raise OriginalManagementPresentationError(
            "Management presentation requires a FrontEndSession"
        )
    if not session.started or session.gameplay is None:
        raise OriginalManagementPresentationError(
            "Complete a single-user TeamSelect Start before management presentation"
        )

    bridge = bridge_factory(session.gameplay)
    club = bridge.club_header()
    source_rows = tuple(bridge.squad_rows())
    visible_rows = source_rows[:SQUAD_VISIBLE_ROW_COUNT]
    return OriginalFreshManagementSnapshot(
        club=club,
        menu=build_fresh_pmenu_snapshot(),
        squad=build_squad_row_viewport(visible_rows),
        source_squad_count=len(source_rows),
        rows_beyond_initial_viewport=max(0, len(source_rows) - len(visible_rows)),
    )
