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
from original_fixture_match_info_link import (
    fixture_cell_at_screen_point, source_fixture_report_control_accepts,
    SourceFixtureMatchInfoContext,
)
from gate13_management_source_data import (
    ClubHeaderView,
    FixtureRowView,
    ManagementHeaderMatchView,
    ManagementSourceDataBridge,
)
from original_league_fixtures_selector_context import (
    LeagueFixturesSelectionContext,
    LeagueFixturesSelectorContextError,
)
from original_league_fixtures_presenter import (
    OriginalLeagueFixturesSnapshot,
    build_league_fixtures_snapshot,
)
from original_league_fixtures_resources import (
    LeagueFixturesMatchInfoAction,
    league_fixtures_column_page_offset,
    league_fixtures_match_info_action,
)
from original_league_tables_selector_context import (
    OriginalLeagueTablesSelectionContext,
    OriginalLeagueTablesSelectorError,
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
from original_squad_paired_presenter import OriginalPairedSquadSnapshot


class OriginalManagementPresentationError(ValueError):
    """The verified front-end/backend seam is not ready for management UI."""


@dataclass(frozen=True)
class OriginalFreshManagementSnapshot:
    club: ClubHeaderView
    menu: OriginalPMenuSnapshot
    header_match: ManagementHeaderMatchView | None
    squad: OriginalSquadViewportSnapshot
    squad_view_transition: OriginalSquadViewTransition
    source_squad_count: int
    rows_beyond_initial_viewport: int
    paired_squad: OriginalPairedSquadSnapshot | None = None


@dataclass(frozen=True)
class OriginalManagementPanelSnapshot:
    """One integrated source-backed PMenu/content-panel selection."""

    club: ClubHeaderView
    menu: OriginalPMenuSnapshot
    header_match: ManagementHeaderMatchView | None
    panel_code: int
    panel_class: str
    squad: OriginalSquadViewportSnapshot | None = None
    squad_view_transition: OriginalSquadViewTransition | None = None
    source_squad_count: int = 0
    rows_beyond_initial_viewport: int = 0
    fixtures_in_source_order: tuple[FixtureRowView, ...] = ()
    league_fixtures: OriginalLeagueFixturesSnapshot | None = None
    league_fixtures_selection: LeagueFixturesSelectionContext | None = None
    league_tables: OriginalLeagueTablesSnapshot | None = None
    league_tables_selection: OriginalLeagueTablesSelectionContext | None = None
    paired_squad: OriginalPairedSquadSnapshot | None = None


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


@dataclass(frozen=True)
class OriginalManagementLeagueFixturesPageActivation:
    """One source-accepted PLeagueFixtures +/-12 column-window transition."""

    direction: int
    previous_offset: int
    column_offset: int
    presentation: OriginalManagementPanelSnapshot


@dataclass(frozen=True)
class OriginalManagementLeagueFixturesRadioActivation:
    """An original event1..14 state change, not inferred mouse acceptance."""

    event_id: int
    selection: LeagueFixturesSelectionContext
    presentation: OriginalManagementPanelSnapshot


@dataclass(frozen=True)
class OriginalManagementLeagueTablesRadioActivation:
    """Original PLeagueTables event1..15, independently source-accepted."""

    event_id: int
    selection: OriginalLeagueTablesSelectionContext
    presentation: OriginalManagementPanelSnapshot


@dataclass(frozen=True)
class OriginalManagementLeagueFixturesGridActivation:
    """Exact PLeagueGrid selector indices resolved from one source grid press."""

    pointer_x: int
    pointer_y: int
    column: int
    row: int
    fixture_id: int | None
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
    league_fixtures_column_offset: int = 0,
    league_fixtures_selection: LeagueFixturesSelectionContext | None = None,
    league_tables_selection: OriginalLeagueTablesSelectionContext | None = None,
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
    header_match_resolver = getattr(bridge, "management_header_match", None)
    header_match = (
        header_match_resolver() if callable(header_match_resolver) else None
    )
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
        paired_resolver = getattr(bridge, 'original_paired_squad', None)
        paired = paired_resolver(source_rows) if callable(paired_resolver) else None
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            header_match=header_match,
            panel_code=SQUAD_PANEL_CODE,
            panel_class=SQUAD_PANEL_CLASS,
            squad=paired.first if paired is not None else build_squad_row_viewport(visible_rows),
            paired_squad=paired,
            squad_view_transition=view_transition,
            source_squad_count=len(source_rows),
            rows_beyond_initial_viewport=(len(paired.unpresented_player_ids) if paired is not None
                                         else max(0, len(source_rows) - len(visible_rows))),
        )

    if selected_child_id == LEAGUE_FIXTURES_PANEL.menu_id:
        # The legacy current-manager path stays untouched until an independently
        # source-accepted native radio event selects another real League.
        source = (bridge.league_fixtures_grid_source()
                  if league_fixtures_selection is None else
                  bridge.source_selected_nonpl_league_fixtures_grid_source(
                      league_fixtures_selection))
        fixtures = build_league_fixtures_snapshot(
            source,
            column_offset=league_fixtures_column_offset,
            staged_resource_names=staged_league_fixture_resource_names,
        )
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            header_match=header_match,
            panel_code=LEAGUE_FIXTURES_PANEL.menu_id,
            panel_class=LEAGUE_FIXTURES_PANEL.panel_class,
            fixtures_in_source_order=tuple(source.fixtures_in_source_order),
            league_fixtures=fixtures,
            league_fixtures_selection=league_fixtures_selection,
        )

    if selected_child_id == LEAGUE_TABLES_PANEL.menu_id:
        # Preserve the normal current-manager table until a validated native
        # country/DIVISION event chooses a different source-backed League.
        table_rows = (bridge.league_table_rows()
                      if league_tables_selection is None else
                      bridge.source_selected_nonpl_league_table_rows(
                          league_tables_selection))
        table = build_league_tables_snapshot(
            table_rows,
            staged_resource_names=staged_league_table_resource_names,
        )
        return OriginalManagementPanelSnapshot(
            club=club,
            menu=menu,
            header_match=header_match,
            panel_code=LEAGUE_TABLES_PANEL.menu_id,
            panel_class=LEAGUE_TABLES_PANEL.panel_class,
            league_tables=table,
            league_tables_selection=league_tables_selection,
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
        header_match=snapshot.header_match,
        squad=snapshot.squad,
        squad_view_transition=snapshot.squad_view_transition,
        source_squad_count=snapshot.source_squad_count,
        rows_beyond_initial_viewport=snapshot.rows_beyond_initial_viewport,
        paired_squad=snapshot.paired_squad,
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
    league_fixtures_column_offset: int = 0
    league_fixtures_selection: LeagueFixturesSelectionContext | None = None
    league_tables_selection: OriginalLeagueTablesSelectionContext | None = None

    def __post_init__(self):
        # Recreated UI after source save/load still runs its real constructor;
        # never rerun the first-season selector or fall back to database-first20.
        gameplay = self.session.gameplay
        state = getattr(gameplay, 'state', None)
        human = getattr(gameplay, 'human', None)
        club_id = getattr(human, 'club_id', None)
        retained = getattr(state, 'native_squad_first_formations', {})
        if club_id in retained and getattr(gameplay, 'original_squad_membership', None) is None:
            gameplay.original_squad_membership = state.construct_original_primary_squad_membership(club_id)

    def snapshot(self) -> OriginalManagementPanelSnapshot:
        return build_management_panel_snapshot(
            self.session,
            self.selected_child_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
            league_fixtures_column_offset=self.league_fixtures_column_offset,
            league_fixtures_selection=self.league_fixtures_selection,
            league_tables_selection=self.league_tables_selection,
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
            league_fixtures_column_offset=0,
        )
        self.selected_child_id = selected_child_id
        self.league_fixtures_column_offset = 0
        self.league_fixtures_selection = None  # A newly constructed panel resets radios.
        self.league_tables_selection = None
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

        if action.action_kind == 'return_to_pstartmenu':
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
            league_fixtures_column_offset=0,
        )
        self.selected_child_id = menu_id
        self.league_fixtures_column_offset = 0
        self.league_fixtures_selection = None  # Source PMenu constructs a fresh panel.
        self.league_tables_selection = None
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
            league_fixtures_column_offset=self.league_fixtures_column_offset,
        )
        self.squad_view_control_id = transition.control_id
        return OriginalManagementSquadViewActivation(transition, snapshot)

    def source_accepted_league_tables_radio_event(
        self, event_id: int,
    ) -> OriginalManagementLeagueTablesRadioActivation:
        """Native PLeagueTables 1..8 country, 9..13 DIVISION, 14/15 sort.

        This is an explicit NON-POINTER event-owner seam. The original
        fmRadioTextSm click/hit dispatch and Current Form 0x4F4A10 ranking
        are not yet qualified for normal GUI interaction. No state changes
        unless an actual source table snapshot can be built successfully.
        """
        if self.selected_child_id != LEAGUE_TABLES_PANEL.menu_id:
            raise OriginalManagementPresentationError(
                "League Tables radio event requires the integrated PLeagueTables panel"
            )
        if type(event_id) is not int:
            raise OriginalManagementPresentationError(
                "Original League Tables radio event ID must be an integer"
            )
        initial = self.league_tables_selection
        if initial is None:
            bridge = _bridge(self.session, self.bridge_factory)
            resolver = getattr(bridge, "original_league_tables_selection_context", None)
            if not callable(resolver):
                raise OriginalManagementPresentationError(
                    "Original League Tables selector source is unavailable"
                )
            initial = resolver()
        try:
            selected = initial.accept_native_radio_event(event_id)
        except OriginalLeagueTablesSelectorError as exc:
            raise OriginalManagementPresentationError(str(exc)) from exc
        snapshot = build_management_panel_snapshot(
            self.session,
            LEAGUE_TABLES_PANEL.menu_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
            league_fixtures_column_offset=self.league_fixtures_column_offset,
            league_tables_selection=selected,
        )
        self.league_tables_selection = selected
        return OriginalManagementLeagueTablesRadioActivation(
            event_id=event_id, selection=selected, presentation=snapshot,
        )

    def source_accepted_league_fixtures_radio_event(
        self, event_id: int,
    ) -> OriginalManagementLeagueFixturesRadioActivation:
        """Commit native PLeagueFixtures events1..14 only after valid data builds.

        Source 0x46E040 owns these event IDs and Recovery507 owns all eight
        per-country indices. This method intentionally accepts no screen
        coordinates and grants no fmRadioTextSm click-hit permission. Unsupported
        Premier0 and incomplete alternate calendar source fail transactionally.
        """
        if self.selected_child_id != LEAGUE_FIXTURES_PANEL.menu_id:
            raise OriginalManagementPresentationError(
                "League Fixtures radio events require the integrated PLeagueFixtures panel"
            )
        if type(event_id) is not int:
            raise OriginalManagementPresentationError(
                "Original League Fixtures radio event ID must be an integer"
            )
        initial = self.league_fixtures_selection
        if initial is None:
            bridge = _bridge(self.session, self.bridge_factory)
            resolver = getattr(bridge, "original_league_fixtures_selection_context", None)
            if not callable(resolver):
                raise OriginalManagementPresentationError(
                    "Original League Fixtures selector source is unavailable"
                )
            initial = resolver()
        try:
            next_selection = initial.accept_native_radio_event(event_id)
        except LeagueFixturesSelectorContextError as exc:
            raise OriginalManagementPresentationError(str(exc)) from exc
        # Do not mutate visible selection/page until the exact selected League
        # has a qualified native calendar, source ranking, and presenter matrix.
        snapshot = build_management_panel_snapshot(
            self.session,
            LEAGUE_FIXTURES_PANEL.menu_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
            league_fixtures_column_offset=0,
            league_fixtures_selection=next_selection,
        )
        self.league_fixtures_selection = next_selection
        self.league_fixtures_column_offset = 0
        return OriginalManagementLeagueFixturesRadioActivation(
            event_id=event_id,
            selection=next_selection,
            presentation=snapshot,
        )

    def source_accepted_league_fixtures_page(
        self,
        direction: int,
    ) -> OriginalManagementLeagueFixturesPageActivation:
        """Apply the recovered +/-12 column window after source control acceptance.

        This is deliberately a non-pointer seam. It preserves the source-proven
        PLeagueFixtures+0xA4 paging arithmetic but does not invent page-button
        rectangles, captions, keyboard bindings, hover state, or event mapping.
        """
        if self.selected_child_id != LEAGUE_FIXTURES_PANEL.menu_id:
            raise OriginalManagementPresentationError(
                "League Fixtures paging requires the integrated PLeagueFixtures panel"
            )
        if type(direction) is not int or direction not in (-1, 1):
            raise OriginalManagementPresentationError(
                "League Fixtures page direction must be exact -1 or 1"
            )
        current = self.snapshot()
        grid = current.league_fixtures
        if grid is None:
            raise OriginalManagementPresentationError(
                "League Fixtures paging lost the integrated grid snapshot"
            )
        previous = self.league_fixtures_column_offset
        try:
            updated = league_fixtures_column_page_offset(
                previous,
                len(grid.member_club_ids),
                direction,
            )
        except ValueError as exc:
            raise OriginalManagementPresentationError(str(exc)) from exc
        snapshot = build_management_panel_snapshot(
            self.session,
            LEAGUE_FIXTURES_PANEL.menu_id,
            bridge_factory=self.bridge_factory,
            staged_league_fixture_resource_names=self.staged_league_fixture_resource_names,
            staged_league_table_resource_names=self.staged_league_table_resource_names,
            expanded_root_id=self.expanded_root_id,
            squad_view_control_id=self.squad_view_control_id,
            league_fixtures_column_offset=updated,
            league_fixtures_selection=self.league_fixtures_selection,
        )
        self.league_fixtures_column_offset = updated
        return OriginalManagementLeagueFixturesPageActivation(
            direction=direction,
            previous_offset=previous,
            column_offset=updated,
            presentation=snapshot,
        )

    def league_fixtures_grid_pointer_press(
        self,
        pointer_x: int,
        pointer_y: int,
    ) -> OriginalManagementLeagueFixturesGridActivation | None:
        """Resolve the exact PLeagueGrid column/row selectors for a left press.

        Source method 0x46D300 reduces the half-open screen grid
        (378,235,348,336) by 29x14 and dispatches the resulting visible column
        and row selector indices separately. The older source trace does not
        prove that this pair can be collapsed into one single-cell visual
        selection state: the recovered toggled-box update is a 24-entry
        selected-index operation. Therefore this seam records only the exact
        selector indices and leaves visual selector-band composition fail-closed.

        PMatchInfo remains the separately recovered right-press/context route.
        """
        if self.selected_child_id != LEAGUE_FIXTURES_PANEL.menu_id:
            return None
        if type(pointer_x) is not int or type(pointer_y) is not int:
            raise OriginalManagementPresentationError(
                "League Fixtures grid pointer coordinates must be integers"
            )
        try:
            point = fixture_cell_at_screen_point(pointer_x, pointer_y)
        except ValueError as exc:
            raise OriginalManagementPresentationError(str(exc)) from exc
        if point is None:
            return None

        column, row = point
        current = self.snapshot()
        grid = current.league_fixtures
        if grid is None:
            raise OriginalManagementPresentationError(
                "League Fixtures grid selection lost the integrated snapshot"
            )
        matches = tuple(
            cell for cell in grid.cells
            if cell.column == column and cell.row == row
        )
        if not matches:
            # Source hides unused row/column controls. A point inside the
            # enclosing 12x24 rectangle is not accepted when its concrete cell
            # control is absent for the current competition.
            return None
        if len(matches) != 1:
            raise OriginalManagementPresentationError(
                "League Fixtures grid point resolved an ambiguous cell"
            )

        return OriginalManagementLeagueFixturesGridActivation(
            pointer_x=pointer_x,
            pointer_y=pointer_y,
            column=column,
            row=row,
            fixture_id=matches[0].fixture_id,
            presentation=current,
        )

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

    def fixture_report_at_screen_point(self, x: int, y: int):
        """Native right-press read-only route; no result-derived context."""
        if self.selected_child_id != LEAGUE_FIXTURES_PANEL.menu_id:
            return None
        # Fresh enabled visible grid, with no already-held right-press/modal.
        if not source_fixture_report_control_accepts(0x183):
            return None
        point = fixture_cell_at_screen_point(x, y)
        if point is None:
            return None
        snapshot = self.snapshot().league_fixtures
        if snapshot is None:
            return None
        column, row = point
        cells = [cell for cell in snapshot.cells
                 if cell.column == column and cell.row == row]
        if len(cells) != 1 or cells[0].fixture_id is None:
            return None
        bridge = self.bridge_factory(self.session.gameplay)
        resolver = getattr(bridge, 'fixture_match_info_context', None)
        if not callable(resolver):
            return None
        context = resolver(cells[0].fixture_id)
        if context is None:
            return None
        if not isinstance(context, SourceFixtureMatchInfoContext) or (
            context.fixture_id != cells[0].fixture_id
            or context.captured_report is None
        ):
            raise OriginalManagementPresentationError('Native report context identity mismatch')
        return context
