"""Source-backed ordinary-management presentation after TeamSelect Start.

This module joins the recovered PMenu shell to read-only management data and
only the content panels whose current presentation boundary is source-proven
well enough to integrate without inventing a replacement UI:

* fresh Team -> Squad (PSquadScreen);
* Calendar -> League Fixtures (PLeagueFixtures), including its recovered directed-pair grid;
* TABLES -> League Tables (PLeagueTables), using the recovered table presenter.

It deliberately does not synthesize unresolved shell pixels, surrounding
League Fixtures chrome, Current Form ordering, or gameplay mutations. PMatchInfo is
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
from original_league_fixtures_presenter import (
    OriginalLeagueFixturesSnapshot,
    build_league_fixtures_snapshot,
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
from original_pmenu_activation import OriginalPMenuRowAction, resolve_pmenu_row_action
from original_pmenu_chrome import PMENU_FRESH_SELECTED_CHILD_ID
from original_pmenu_presenter import OriginalPMenuSnapshot, build_pmenu_snapshot
from original_squad_presenter import (
    OriginalSquadViewportSnapshot,
    build_squad_row_viewport,
)
from original_squad_resources import (
    OriginalSquadResourceError,
    OriginalSquadViewTransition,
    SQUAD_VISIBLE_ROW_COUNT,
    squad_view_transition,
)


class OriginalManagementPresentationError(ValueError):
    """The verified front-end/backend seam is not ready for management UI."""


@dataclass(frozen=True)
class OriginalFreshManagementSnapshot:
    club: ClubHeaderView
    menu: OriginalPMenuSnapshot
    squad: OriginalSquadViewportSnapshot
    squad_view_transition: OriginalSquadViewTransition
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
    squad_view_transition: OriginalSquadViewTransition | None = None
    source_squad_count: int = 0
    rows_beyond_initial_viewport: int = 0
    fixtures_in_source_order: tuple[FixtureRowView, ...] = ()
    league_fixtures: OriginalLeagueFixturesSnapshot | None = None
    league_tables: OriginalLeagueTablesSnapshot | None = None


@dataclass(frozen=True)
class OriginalManagementPMenuActivation:
    """Result of applying one source-accepted PMenu row callback."""

    action: OriginalPMenuRowAction
    presentation: OriginalManagementPanelSnapshot


@dataclass(frozen=True)
class OriginalManagementSquadViewActivation:
    """Result of one explicitly source-accepted PSquadScreen control event."""

    transition: OriginalSquadViewTransition
    presentation: OriginalManagementPanelSnapshot


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
    staged_league_fixture_resource_names: Iterable[str] = (),
    staged_league_table_resource_names: Iterable[str] = (),
    expanded_root_id: int | None = None,
    squad_view_control_id: int = 3,
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
    menu = build_pmenu_snapshot(
        selected_child_id,
        expanded_root_id=expanded_root_id,
    )

    if selected_child_id == SQUAD_PANEL_CODE:
        try:
            view_transition = squad_view_transition(squad_view_control_id)
        except OriginalSquadResourceError as exc:
            raise OriginalManagementPresentationError(str(exc)) from exc
        source_rows = tuple(bridge.squad_rows())
        visible_rows = source_rows[:SQUAD_VISIBLE_ROW_COUNT]
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            panel_code=SQUAD_PANEL_CODE,
            panel_class=SQUAD_PANEL_CLASS,
            squad=build_squad_row_viewport(visible_rows),
            squad_view_transition=view_transition,
            source_squad_count=len(source_rows),
            rows_beyond_initial_viewport=max(0, len(source_rows) - len(visible_rows)),
        )

    if selected_child_id == LEAGUE_FIXTURES_PANEL.menu_id:
        source = bridge.league_fixtures_grid_source()
        fixtures = build_league_fixtures_snapshot(
            source,
            staged_resource_names=staged_league_fixture_resource_names,
        )
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            panel_code=LEAGUE_FIXTURES_PANEL.menu_id,
            panel_class=LEAGUE_FIXTURES_PANEL.panel_class,
            fixtures_in_source_order=tuple(source.fixtures_in_source_order),
            league_fixtures=fixtures,
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
        squad_view_transition=snapshot.squad_view_transition,
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
    staged_league_fixture_resource_names: tuple[str, ...] = ()
    staged_league_table_resource_names: tuple[str, ...] = ()
    expanded_root_id: int | None = None
    squad_view_control_id: int = 3

    def snapshot(self) -> OriginalManagementPanelSnapshot:
        return build_management_panel_snapshot(
            self.session,
            self.selected_child_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
        )

    def navigate(self, selected_child_id: int) -> OriginalManagementPanelSnapshot:
        snapshot = build_management_panel_snapshot(
            self.session,
            selected_child_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
        )
        self.selected_child_id = selected_child_id
        return snapshot

    def source_accepted_pmenu_action(
        self,
        row_kind: str,
        menu_id: int,
        source_flags: int,
    ) -> OriginalManagementPMenuActivation:
        """Apply one row callback only after native control acceptance is proven.

        This method deliberately has no screen-coordinate or Tk-event input.
        Callers must already have the source control/event acceptance evidence
        represented by the recovered row callback contract. Hidden rows fail
        closed so this seam cannot be used to dispatch an arbitrary menu ID.
        """
        current = self.snapshot()
        visible = [
            row
            for row in current.menu.rows
            if row.row_kind == row_kind and row.menu_id == menu_id
        ]
        if len(visible) != 1:
            raise OriginalManagementPresentationError(
                "Source-accepted PMenu action requires one currently visible recovered row"
            )

        action = resolve_pmenu_row_action(row_kind, menu_id, source_flags)
        if not action.accepted:
            return OriginalManagementPMenuActivation(action, current)

        if action.action_kind == "expand_root":
            self.expanded_root_id = menu_id
            return OriginalManagementPMenuActivation(action, self.snapshot())

        if action.action_kind != "open_panel":
            raise OriginalManagementPresentationError(
                f"Unsupported recovered PMenu action kind: {action.action_kind}"
            )

        snapshot = build_management_panel_snapshot(
            self.session,
            menu_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
        )
        self.selected_child_id = menu_id
        return OriginalManagementPMenuActivation(action, snapshot)

    def source_accepted_squad_view_transition(
        self,
        control_id: int,
    ) -> OriginalManagementSquadViewActivation:
        """Apply only the recovered PSquadScreen 3/4/5 container transition.

        The caller must already own the native event-acceptance evidence. This
        method deliberately accepts no coordinates or Tk event, and the returned
        snapshot does not claim unrecovered formation/player pixels.
        """
        if self.selected_child_id != SQUAD_PANEL_CODE:
            raise OriginalManagementPresentationError(
                "Squad view transition requires the integrated PSquadScreen panel"
            )
        try:
            transition = squad_view_transition(control_id)
        except OriginalSquadResourceError as exc:
            raise OriginalManagementPresentationError(str(exc)) from exc

        snapshot = build_management_panel_snapshot(
            self.session,
            SQUAD_PANEL_CODE,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=transition.control_id,
        )
        self.squad_view_control_id = transition.control_id
        return OriginalManagementSquadViewActivation(transition, snapshot)

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
