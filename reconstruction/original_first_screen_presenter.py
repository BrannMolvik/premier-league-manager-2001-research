"""Single presentation-only view over both verified original first-screen bundles.

This seam exposes the exact original 800x600 background, unmodified source
button atlas frames, confirmed action rectangles and original-language glyph
masks for the currently active front-end screen. Pointer dispatch goes through
the previously tested original rectangle translator into FrontEndSession.

The original Button@ease_2001 group/frame state machine, Zurich caption
alignment, TeamSelect population order, hierarchy state transforms and
multi-user club toggles are exposed from executable evidence. The private
0x30-byte TeamSelect selection record is rollback state, not a club identity:
the clicked row carries the club and the original creates a user for it
immediately. This presenter mirrors that source-backed selected-club set while
the current gameplay backend remains deliberately single-manager. A successful
single-user Start event produces a backend handoff command; it does not silently
synthesize a recovered manager-home renderer.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable

from front_end_session import FrontEndSession, FrontEndSessionOutcome
from front_end_settings import (
    SourceStyledSettingsResources,
    candidate_settings_event,
    settings_surface_actions,
    start_menu_settings_action,
)
from front_end_state import FrontEndScreen
from original_button_frames import (
    OriginalButtonAtlas, OriginalButtonFrame, OriginalButtonState,
)
from original_front_end_input import dispatch_original_pointer
from original_front_end_layout import (
    OriginalRect,
    PSTARTMENU_SCREEN_ACTIONS,
    PSTARTMENU_BACKGROUND_RECT,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_EVENT,
    TEAMSELECT_START_RECT,
)
from original_pstartmenu_labels import PStartMenuCaption
from original_pstartmenu_resources import OriginalPStartMenuResources
from original_teamselect_resources import OriginalTeamSelectResources
from original_teamselect_hierarchy_art import OriginalTeamSelectHierarchyArt
from original_teamselect_native import (
    TeamSelectHierarchyModel,
    TeamSelectRowPresentation,
    build_teamselect_presentations,
    row_at_pointer,
)


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
    hierarchy_rows: tuple[TeamSelectRowPresentation, ...] = ()
    club_rows: tuple[TeamSelectRowPresentation, ...] = ()


@dataclass(frozen=True)
class OriginalHierarchyInteraction:
    row_kind: str
    text: str
    source_id: int
    selected_club_ids: tuple[int, ...]


@dataclass
class OriginalFirstScreenPresenter:
    session: FrontEndSession
    start_menu: OriginalPStartMenuResources
    team_select: OriginalTeamSelectResources | None = None
    team_select_loader: Callable[[], OriginalTeamSelectResources] | None = None
    hierarchy: TeamSelectHierarchyModel | None = None
    settings_resources: SourceStyledSettingsResources | None = None
    _teamselect_cache_key: tuple | None = field(default=None, init=False, repr=False)
    _teamselect_cache_rows: tuple = field(
        default_factory=lambda: ((), ()), init=False, repr=False
    )

    def _ensure_team_select_resources(self) -> OriginalTeamSelectResources:
        if self.team_select is None:
            if self.team_select_loader is None:
                raise RuntimeError("TeamSelect resources are not configured")
            self.team_select = self.team_select_loader()
        return self.team_select

    def _ensure_hierarchy(self) -> TeamSelectHierarchyModel | None:
        if self.hierarchy is not None:
            return self.hierarchy
        team_select = self._ensure_team_select_resources()
        if team_select.native_hierarchy is None:
            return None
        if self.session.gameplay is not None:
            state = getattr(self.session.gameplay, "state", None)
            if state is not None:
                self.hierarchy = TeamSelectHierarchyModel.from_game_state(state)
                return self.hierarchy
        catalog = getattr(self.session, "team_select_catalog", None)
        if catalog is None:
            return None
        self.hierarchy = TeamSelectHierarchyModel.from_catalog(catalog)
        return self.hierarchy

    def snapshot(self) -> OriginalFirstScreenSnapshot:
        """Return the source-aligned visual inputs for the active original screen."""
        screen = self.session.navigation.screen
        if screen is FrontEndScreen.START_MENU:
            controls = [
                OriginalActionPresentation(
                    action.event,
                    action.rect,
                    self.start_menu.button_atlas,
                    replace(
                        caption,
                        control_rect=action.rect,
                        clip_rect=action.rect,
                        line_origin_x=caption.line_origin_x + PSTARTMENU_BACKGROUND_RECT.x,
                        line_origin_y=caption.line_origin_y + PSTARTMENU_BACKGROUND_RECT.y,
                    ),
                )
                for action, caption in zip(
                    PSTARTMENU_SCREEN_ACTIONS, self.start_menu.captions, strict=True
                )
            ]
            if self.settings_resources is not None:
                action = start_menu_settings_action()
                controls.append(
                    OriginalActionPresentation(
                        action.event,
                        action.rect,
                        self.start_menu.button_atlas,
                        self.settings_resources.caption(
                            action.event, action.text, action.rect
                        ),
                    )
                )
            return OriginalFirstScreenSnapshot(
                screen, self.start_menu.background_rgba, tuple(controls)
            )
        if screen is FrontEndScreen.SETTINGS:
            if self.settings_resources is None:
                raise RuntimeError("Settings resources are not configured")
            controls = tuple(
                OriginalActionPresentation(
                    action.event,
                    action.rect,
                    self.start_menu.button_atlas,
                    self.settings_resources.caption(
                        action.event, action.text, action.rect
                    ),
                )
                for action in settings_surface_actions(self.session.settings)
            )
            return OriginalFirstScreenSnapshot(
                screen,
                self.start_menu.background_rgba,
                controls,
            )
        if screen is FrontEndScreen.TEAM_SELECT:
            team_select = self._ensure_team_select_resources()
            atlas = team_select.action_atlas
            captions = {item.event: item for item in team_select.captions}
            controls = (
                OriginalActionPresentation(
                    TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT, atlas,
                    captions.get(TEAMSELECT_BACK_EVENT),
                ),
                OriginalActionPresentation(
                    TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT, atlas,
                    captions.get(TEAMSELECT_START_EVENT),
                ),
            )
            hierarchy_rows = ()
            club_rows = ()
            model = self._ensure_hierarchy()
            if (
                model is not None
                and team_select.hierarchy_art is not None
                and team_select.native_hierarchy is not None
            ):
                cache_key = (
                    int(model.selected_country_id),
                    None if model.selected_competition_id is None
                    else int(model.selected_competition_id),
                    tuple(int(value) for value in model.selected_club_ids),
                )
                if cache_key != self._teamselect_cache_key:
                    self._teamselect_cache_rows = build_teamselect_presentations(
                        model,
                        team_select.hierarchy_art,
                        team_select.native_hierarchy,
                    )
                    self._teamselect_cache_key = cache_key
                hierarchy_rows, club_rows = self._teamselect_cache_rows
            return OriginalFirstScreenSnapshot(
                screen,
                team_select.background_rgba,
                controls,
                team_select.hierarchy_row_origins,
                team_select.hierarchy_art,
                hierarchy_rows,
                club_rows,
            )
        raise RuntimeError(f"Original renderer not yet recovered for {screen!r}")

    def pointer(
        self, x: int, y: int
    ) -> FrontEndSessionOutcome | OriginalHierarchyInteraction | None:
        screen = self.session.navigation.screen
        if self.settings_resources is not None:
            modern_event = candidate_settings_event(screen, x, y)
            if modern_event is not None:
                outcome = self.session.dispatch(modern_event)
                if outcome.transition.screen is FrontEndScreen.START_MENU:
                    self.hierarchy = None
                    self._teamselect_cache_key = None
                    self._teamselect_cache_rows = ((), ())
                return outcome
        if screen is FrontEndScreen.SETTINGS:
            return None
        if screen is FrontEndScreen.TEAM_SELECT:
            model = self._ensure_hierarchy()
            if model is not None:
                row = row_at_pointer(model.hierarchy_rows(), x, y)
                if row is not None:
                    activated = model.activate_hierarchy_row(row.visible_index)
                    return OriginalHierarchyInteraction(
                        activated.kind.value,
                        activated.text,
                        activated.source_id,
                        model.selected_club_ids,
                    )
                club = row_at_pointer(model.club_rows(), x, y)
                if club is not None:
                    toggled = model.toggle_club_row(club.visible_index)
                    # 0x4D8E90 receives the clicked row's club directly, while
                    # the private selection record stores displaced-manager
                    # rollback state. Keep the clean-room session keyed by the
                    # row's canonical club IDs and preserve source selection
                    # order. The session itself fails closed at Start if more
                    # than one original-style user is selected because the
                    # modern gameplay backend is still single-manager.
                    self.session.set_club_selections(model.selected_club_ids)
                    return OriginalHierarchyInteraction(
                        "club",
                        toggled.text,
                        toggled.club_id,
                        model.selected_club_ids,
                    )
        outcome = dispatch_original_pointer(self.session, x, y)
        if (
            outcome is not None
            and outcome.transition.screen is FrontEndScreen.START_MENU
        ):
            self.hierarchy = None
            self._teamselect_cache_key = None
            self._teamselect_cache_rows = ((), ())
        return outcome

    def choose_club(self, club_id: int) -> None:
        """Developer-only explicit single-club compatibility selection."""
        self.session.choose_club(club_id)

    def fresh_management_snapshot(self, *, bridge_factory=None):
        """Enter the source-backed fresh PMenu -> PSquadScreen composition.

        Import lazily so the original first-screen presenter retains its
        simulation-free import boundary. The called seam itself consumes only
        the read-only management bridge.
        """
        from original_management_presenter import build_fresh_management_snapshot

        if bridge_factory is None:
            return build_fresh_management_snapshot(self.session)
        return build_fresh_management_snapshot(
            self.session,
            bridge_factory=bridge_factory,
        )
