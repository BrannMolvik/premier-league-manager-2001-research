"""Source-backed ordinary-management presentation after TeamSelect Start.

This module joins the recovered PMenu shell to read-only management data and
only the content panels whose current presentation boundary is source-proven
well enough to integrate without inventing a replacement UI:

* fresh Team -> Squad (PSquadScreen);
* Calendar -> League Fixtures (PLeagueFixtures), preserving bridge source order;
* TABLES -> League Tables (PLeagueTables), using the recovered table presenter.

It deliberately does not synthesize unresolved shell pixels, fixture-grid
member placement, Current Form ordering, or gameplay mutations. PMatchInfo is
exposed only through the already recovered fixture action gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from front_end_session import FrontEndSession
from gate13_management_source_data import (
    ClubHeaderView,
    FixtureRowView,
    ManagementSourceDataBridge,
)
from original_league_fixtures_resources import (
    LeagueFixturesMatchInfoAction,
    league_fixtures_match_info_action,
)
from original_league_tables_presenter import (
    OriginalLeagueTablesSnapshot,
    build_league_tables_snapshot,
)
from original_management_navigation import (
    LEAGUE_FIXTURES_PANEL,
    LEAGUE_TABLES_PANEL,
)
from original_management_shell import SQUAD_PANEL_CLASS, SQUAD_PANEL_CODE
from original_pmenu_chrome import PMENU_FRESH_SELECTED_CHILD_ID
from original_pmenu_presenter import OriginalPMenuSnapshot, build_pmenu_snapshot
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


@dataclass(frozen=True)
class OriginalManagementPanelSnapshot:
    """One integrated source-backed PMenu/content-panel selection."""

    club: ClubHeaderView
    menu: OriginalPMenuSnapshot
    panel_code: int
    panel_class: str
    squad: OriginalSquadViewportSnapshot | None = None
    source_squad_count: int = 0
    rows_beyond_initial_viewport: int = 0
    fixtures_in_source_order: tuple[FixtureRowView, ...] = ()
    league_tables: OriginalLeagueTablesSnapshot | None = None


def _require_started_session(session: FrontEndSession) -> None:
    if not isinstance(session, FrontEndSession):
        raise OriginalManagementPresentationError(
            "Management presentation requires a FrontEndSession"
        )
    if not session.started or session.gameplay is None:
        raise OriginalManagementPresentationError(
            "Complete a single-user TeamSelect Start before management presentation"
        )


def _bridge(session: FrontEndSession, bridge_factory: Callable[[object], object]):
    _require_started_session(session)
    return bridge_factory(session.gameplay)


def build_management_panel_snapshot(
    session: FrontEndSession,
    selected_child_id: int,
    *,
    bridge_factory: Callable[[object], object] = ManagementSourceDataBridge,
    staged_league_table_resource_names: Iterable[str] = (),
) -> OriginalManagementPanelSnapshot:
    """Project one source-proven integrated PMenu route.

    A PMenu child may exist in the recovered hierarchy without having an
    integrated panel presenter. Such children fail closed here instead of
    falling back to the generic ttk prototype.
    """
    if type(selected_child_id) is not int:
        raise OriginalManagementPresentationError(
            "Integrated PMenu child ID must be an integer"
        )

    bridge = _bridge(session, bridge_factory)
    club = bridge.club_header()
    menu = build_pmenu_snapshot(selected_child_id)

    if selected_child_id == SQUAD_PANEL_CODE:
        source_rows = tuple(bridge.squad_rows())
        visible_rows = source_rows[:SQUAD_VISIBLE_ROW_COUNT]
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            panel_code=SQUAD_PANEL_CODE,
            panel_class=SQUAD_PANEL_CLASS,
            squad=build_squad_row_viewport(visible_rows),
            source_squad_count=len(source_rows),
            rows_beyond_initial_viewport=max(0, len(source_rows) - len(visible_rows)),
        )

    if selected_child_id == LEAGUE_FIXTURES_PANEL.menu_id:
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            panel_code=LEAGUE_FIXTURES_PANEL.menu_id,
            panel_class=LEAGUE_FIXTURES_PANEL.panel_class,
            fixtures_in_source_order=tuple(bridge.fixture_rows()),
        )

    if selected_child_id == LEAGUE_TABLES_PANEL.menu_id:
        table = build_league_tables_snapshot(
            bridge.league_table_rows(),
            staged_resource_names=staged_league_table_resource_names,
        )
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            panel_code=LEAGUE_TABLES_PANEL.menu_id,
            panel_class=LEAGUE_TABLES_PANEL.panel_class,
            league_tables=table,
        )

    raise OriginalManagementPresentationError(
        f"PMenu child {selected_child_id:#x} has no integrated "
        "source-backed management panel presenter"
    )


def build_fresh_management_snapshot(
    session: FrontEndSession,
    *,
    bridge_factory: Callable[[object], object] = ManagementSourceDataBridge,
) -> OriginalFreshManagementSnapshot:
    """Compose the fresh PMenu -> PSquadScreen landing after a valid Start."""
    snapshot = build_management_panel_snapshot(
        session,
        PMENU_FRESH_SELECTED_CHILD_ID,
        bridge_factory=bridge_factory,
    )
    if snapshot.squad is None:
        raise OriginalManagementPresentationError(
            "Fresh management route did not resolve PSquadScreen"
        )
    return OriginalFreshManagementSnapshot(
        club=snapshot.club,
        menu=snapshot.menu,
        squad=snapshot.squad,
        source_squad_count=snapshot.source_squad_count,
        rows_beyond_initial_viewport=snapshot.rows_beyond_initial_viewport,
    )


@dataclass
class OriginalManagementPresenter:
    """Stateful PMenu navigation over the bounded integrated panel set.

    Navigation is transactional: the selected child changes only after the
    requested panel snapshot can be built from source-backed data.
    """

    session: FrontEndSession
    bridge_factory: Callable[[object], object] = ManagementSourceDataBridge
    selected_child_id: int = PMENU_FRESH_SELECTED_CHILD_ID
    staged_league_table_resource_names: tuple[str, ...] = ()

    def snapshot(self) -> OriginalManagementPanelSnapshot:
        return build_management_panel_snapshot(
            self.session,
            self.selected_child_id,
            bridge_factory=self.bridge_factory,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
        )

    def navigate(self, selected_child_id: int) -> OriginalManagementPanelSnapshot:
        snapshot = build_management_panel_snapshot(
            self.session,
            selected_child_id,
            bridge_factory=self.bridge_factory,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
        )
        self.selected_child_id = selected_child_id
        return snapshot

    def fixture_match_info_action(
        self,
        *,
        fixture_present: bool,
        linked_context_available: bool,
    ) -> LeagueFixturesMatchInfoAction | None:
        """Expose the exact PLeagueFixtures -> PMatchInfo action gate."""
        if self.selected_child_id != LEAGUE_FIXTURES_PANEL.menu_id:
            raise OriginalManagementPresentationError(
                "PMatchInfo action requires the integrated League Fixtures panel"
            )
        return league_fixtures_match_info_action(
            fixture_present=fixture_present,
            linked_context_available=linked_context_available,
        )
