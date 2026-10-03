"""Clean fixed-surface FM2001 application host for recovered original UI.

Unlike the Gate-13 diagnostic viewer, this host has no manual source-frame
controls or developer sidebar. It renders the source-backed first screens at
native 800x600 coordinates using the recovered initial Button@ease frame and
routes proven clicks through FrontEndSession. Successful TeamSelect Start enters
the fixed PMenu management host.

The application-owned seasonal base and competition header are source-backed
for the twenty original Premiership clubs. PMenu row assets, fonts and geometry
are also recovered. Remaining shell controls and ordinary match-report context
capture stay fail-closed; the host does not invent a replacement skin.
"""
from __future__ import annotations

from base64 import b64encode
from pathlib import Path
from original_management_background import OriginalManagementBackground

from front_end_session import FrontEndSession
from front_end_state import FrontEndCommand, FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter,
    OriginalHierarchyInteraction,
)
from original_live_debug_view import build_original_debug_frame, endpoint_text_rgba
from original_league_fixtures_art import (
    OriginalLeagueFixturesGridArt,
    load_verified_league_fixtures_grid_art,
)
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_RESOURCES,
    validate_original_league_fixtures_resources,
)
from original_league_tables_art import (
    OriginalLeagueTablesHeaderArt,
    load_verified_league_tables_header_art,
)
from original_league_tables_resources import (
    LEAGUE_TABLES_RESOURCES,
    validate_original_league_tables_resources,
)
from original_management_canvas import (
    build_management_canvas_frame,
    build_management_pmenu_render,
    load_verified_management_pmenu_resources,
)
from original_management_presenter import OriginalManagementPresenter
from original_pmatchinfo_art import (
    OriginalPMatchInfoPopupArt,
    build_pmatchinfo_popup_art,
)
from original_pmatchinfo_presenter import (
    OriginalPMatchInfoStaticSnapshot,
    load_staged_pmatchinfo_snapshot,
)
from original_pmenu_activation import resolve_pmenu_pointer_press
from original_pmenu_presenter import candidate_pmenu_row_at_screen_point
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
from original_teamselect_resources import load_verified_original_teamselect_inputs
from original_squad_top_controls import (
    OriginalSquadTopResources,
    build_fresh_squad_top_render,
    load_verified_squad_top_resources,
)
from startup_media_playback import load_and_play_verified_startup_sequence
from runtime_layout import application_root, bundled_source_root


REPO_ROOT = application_root()
DEFAULT_SOURCE_ROOT = bundled_source_root()
SCREEN_SIZE = (800, 600)


class OriginalGameHostError(RuntimeError):
    """The source-backed application host cannot continue safely."""


def build_original_game_presenter(
    game_dir: str | Path,
    *,
    source_root: str | Path | None = None,
) -> OriginalFirstScreenPresenter:
    """Load all currently integrated first-screen inputs from verified originals."""
    game_dir = Path(game_dir)
    root = DEFAULT_SOURCE_ROOT if source_root is None else Path(source_root)
    executable = game_dir / "FOOTBAL.EXE"
    art_root = root / "FM2001_Art"
    font20 = root / "Fonts" / "Zurich_BdXCn_BT_20pixel.fnt"

    menu = load_verified_english_pstartmenu_inputs(
        original_art_dir=art_root,
        original_language_dir=root,
        original_zurich_font20=font20,
        original_executable=executable,
    )
    team = load_verified_original_teamselect_inputs(
        original_art_dir=art_root,
        original_executable=executable,
    )
    return OriginalFirstScreenPresenter(
        FrontEndSession.for_canonical_game_dir(game_dir),
        menu,
        team,
    )


class OriginalGameTkHost:
    """Native-size source-backed game canvas without substitute management UI."""

    def __init__(
        self,
        presenter: OriginalFirstScreenPresenter,
        root,
        tk,
        *,
        management_presenter_factory=None,
        management_pmenu_resources=None,
        league_fixtures_grid_art=None,
        squad_top_resources=None,
        league_tables_header_art=None,
        pmatchinfo_snapshot=None,
        error_reporter=None,
        management_background=None,
    ):
        self.presenter = presenter
        self.root = root
        self.tk = tk
        self.management_presenter_factory = (
            management_presenter_factory
            or (lambda session: OriginalManagementPresenter(session))
        )
        self.management_presenter = None
        self.management_pmenu_resources = management_pmenu_resources
        self.league_fixtures_grid_art = league_fixtures_grid_art
        self.squad_top_resources = squad_top_resources
        self.league_tables_header_art = league_tables_header_art
        self.pmatchinfo_snapshot = pmatchinfo_snapshot
        self.error_reporter = error_reporter or self._show_transition_error
        self.management_background = management_background
        self.last_pmenu_activation = None
        self.last_squad_view_activation = None
        self.last_pmatchinfo_action = None
        self.active_pmatchinfo_context = None
        self.active_pmatchinfo_art = None
        self._photos = []
        self.last_status = "Source-backed FM2001 host ready"

        self.root.title("Premier League Manager 2001")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            root,
            width=SCREEN_SIZE[0],
            height=SCREEN_SIZE[1],
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-3>", self.on_fixture_report_press)
        self.canvas.bind("<Button-1>", self.on_click)
        self.redraw()

    def _show_transition_error(self, message: str) -> None:
        # Port compatibility feedback, not a claimed original-game dialog.
        from tkinter import messagebox
        messagebox.showerror("FM2001 port: action could not complete", message,
                             parent=self.root)

    def _photo(self, png: bytes):
        photo = self.tk.PhotoImage(
            data=b64encode(png).decode("ascii"),
            format="png",
        )
        self._photos.append(photo)
        return photo

    def _draw_first_screen(self) -> None:
        view = self.presenter.snapshot()
        frame = build_original_debug_frame(view, 0)
        self.canvas.delete("all")
        self._photos = []

        background = self._photo(frame.background_png)
        self.canvas.create_image(0, 0, image=background, anchor=self.tk.NW)

        for overlay in frame.original_source_frame_overlays:
            art = self._photo(overlay.source_frame_png)
            self.canvas.create_image(
                overlay.rect.x,
                overlay.rect.y,
                image=art,
                anchor=self.tk.NW,
            )

        for caption in frame.native_caption_overlays:
            glyphs = self._photo(caption.glyph_rgba_png)
            self.canvas.create_image(
                caption.line_origin_x,
                caption.line_origin_y,
                image=glyphs,
                anchor=self.tk.NW,
            )

        for row in (*view.hierarchy_rows, *view.club_rows):
            animation = self._photo(
                encode_rgba_png(
                    row.animation_frame.width,
                    row.animation_frame.height,
                    row.animation_frame.rgba,
                )
            )
            bar = self._photo(
                encode_rgba_png(
                    row.bar_frame.width,
                    row.bar_frame.height,
                    row.bar_frame.rgba,
                )
            )
            glyph_rgba = endpoint_text_rgba(
                row.glyph_mask.alpha,
                row.native_color_16,
            )
            glyphs = self._photo(
                encode_rgba_png(
                    row.glyph_mask.width,
                    row.glyph_mask.height,
                    glyph_rgba,
                )
            )
            self.canvas.create_image(
                row.animation_rect.x,
                row.animation_rect.y,
                image=animation,
                anchor=self.tk.NW,
            )
            self.canvas.create_image(
                row.bar_rect.x,
                row.bar_rect.y,
                image=bar,
                anchor=self.tk.NW,
            )
            self.canvas.create_image(
                row.line_origin_x,
                row.line_origin_y,
                image=glyphs,
                anchor=self.tk.NW,
            )

    def _draw_squad_top_controls(self, frame) -> int:
        """Draw only the exact native fresh PSquadScreen top-control state."""
        if frame.presentation.panel_class != "PSquadScreen":
            return 0
        transition = frame.presentation.squad_view_transition
        if transition is None:
            raise OriginalGameHostError(
                "Squad panel lost its source-proven view-transition state"
            )
        # Only control 3's initial selected/normal button frames are currently
        # source-closed. Controls 4/5 have proven container transitions but
        # their post-event button/formation/player pixels remain fail-closed.
        if transition.control_id != 3:
            return 0
        resources = self.squad_top_resources
        if not isinstance(resources, OriginalSquadTopResources):
            raise OriginalGameHostError(
                "Squad landing renderer requires verified original top-control resources"
            )
        rendered = build_fresh_squad_top_render(resources)
        count = 0
        for overlay in rendered.overlays:
            image = self._photo(overlay.png)
            self.canvas.create_image(
                overlay.x,
                overlay.y,
                image=image,
                anchor=self.tk.NW,
            )
            count += 1
        return count

    def _draw_league_fixtures_grid_art(self, frame) -> int:
        """Draw only PLeagueFixtures bitmaps with source-proven screen placement."""
        if frame.presentation.panel_class != "PLeagueFixtures":
            return 0
        if frame.presentation.league_fixtures is None:
            raise OriginalGameHostError(
                "League Fixtures panel lost its source-backed matrix snapshot"
            )
        if not frame.presentation.league_fixtures.exact_art_staged:
            raise OriginalGameHostError(
                "League Fixtures panel requires all six verified original assets"
            )
        art = self.league_fixtures_grid_art
        if not isinstance(art, OriginalLeagueFixturesGridArt):
            raise OriginalGameHostError(
                "League Fixtures renderer requires verified original grid art"
            )

        count = 0
        for placement in art.placements:
            png = encode_rgba_png(
                placement.width,
                placement.height,
                placement.rgba,
            )
            image = self._photo(png)
            self.canvas.create_image(
                placement.x,
                placement.y,
                image=image,
                anchor=self.tk.NW,
            )
            count += 1
        return count

    def _draw_league_tables_header_art(self, frame) -> int:
        """Draw only the exact PLeagueTables league_bar control."""
        if frame.presentation.panel_class != "PLeagueTables":
            return 0
        snapshot = frame.presentation.league_tables
        if snapshot is None:
            raise OriginalGameHostError(
                "League Tables panel lost its source-backed table snapshot"
            )
        if not snapshot.exact_art_staged:
            raise OriginalGameHostError(
                "League Tables renderer requires all 15 verified original assets"
            )
        art = self.league_tables_header_art
        if not isinstance(art, OriginalLeagueTablesHeaderArt):
            raise OriginalGameHostError(
                "League Tables renderer requires verified original header art"
            )
        image = self._photo(encode_rgba_png(art.width, art.height, art.rgba))
        self.canvas.create_image(
            art.x,
            art.y,
            image=image,
            anchor=self.tk.NW,
        )
        return 1

    def _draw_pmatchinfo_dialog(self) -> int:
        """Redraw only the globally source-proven PMatchInfo popup background."""
        art = self.active_pmatchinfo_art
        if art is None:
            return 0
        if not isinstance(art, OriginalPMatchInfoPopupArt):
            raise OriginalGameHostError(
                "Active PMatchInfo state must be verified popup art"
            )
        image = self._photo(encode_rgba_png(art.width, art.height, art.rgba))
        self.canvas.create_image(
            art.x,
            art.y,
            image=image,
            anchor=self.tk.NW,
        )
        return 1

    def _draw_management_host(self) -> None:
        if self.management_presenter is None:
            self.management_presenter = self.management_presenter_factory(
                self.presenter.session
            )
        frame = build_management_canvas_frame(self.management_presenter)
        if self.management_pmenu_resources is None:
            raise OriginalGameHostError(
                "Management PMenu renderer requires verified original row resources"
            )

        menu_render = build_management_pmenu_render(
            frame,
            self.management_pmenu_resources,
        )
        self.canvas.delete("all")
        self._photos = []

        if self.management_background is not None:
            for image in self.management_background.images(frame.presentation.club):
                photo = self._photo(encode_rgba_png(image.width, image.height, image.rgba))
                self.canvas.create_image(image.x, image.y, image=photo, anchor=self.tk.NW)

        squad_image_count = self._draw_squad_top_controls(frame)
        fixture_image_count = self._draw_league_fixtures_grid_art(frame)
        table_image_count = self._draw_league_tables_header_art(frame)
        panel_image_count = squad_image_count + fixture_image_count + table_image_count

        menu_x, menu_y, _menu_w, _menu_h = frame.menu_rect
        for overlay in menu_render.overlays:
            art = self._photo(overlay.png)
            self.canvas.create_image(
                menu_x + overlay.x,
                menu_y + overlay.y,
                image=art,
                anchor=self.tk.NW,
            )

        dialog_image_count = self._draw_pmatchinfo_dialog()

        panel_status = (
            f"; {panel_image_count} source panel bitmaps rendered"
            if panel_image_count
            else ""
        )
        dialog_status = (
            f"; {dialog_image_count} source PMatchInfo bitmap rendered"
            if dialog_image_count
            else ""
        )
        self.last_status = (
            f"Management host active: {frame.presentation.panel_class}; "
            f"source PMenu rows rendered{panel_status}{dialog_status}; "
            + ("native management base/header rendered; remaining shell controls unresolved"
               if self.management_background is not None
               else "surrounding management background unresolved")
        )

    def redraw(self) -> None:
        screen = self.presenter.session.navigation.screen
        if screen in (FrontEndScreen.START_MENU, FrontEndScreen.TEAM_SELECT):
            self._draw_first_screen()
            return
        if screen is FrontEndScreen.MANAGEMENT:
            self._draw_management_host()
            return
        raise OriginalGameHostError(f"Unsupported source-backed screen: {screen!r}")

    def apply_source_accepted_pmenu_action(
        self,
        row_kind: str,
        menu_id: int,
        source_flags: int,
    ):
        """Apply a recovered PMenu callback after source event acceptance.

        This remains useful for tests and non-pointer source adapters. Ordinary
        Tk pointer presses now use the separately recovered SelectBmp boundary.
        """
        if self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            raise OriginalGameHostError(
                "Source-accepted PMenu action requires the MANAGEMENT host"
            )
        if self.management_presenter is None:
            self.management_presenter = self.management_presenter_factory(
                self.presenter.session
            )
        result = self.management_presenter.source_accepted_pmenu_action(
            row_kind,
            menu_id,
            source_flags,
        )
        self.last_pmenu_activation = result
        self.redraw()
        self.last_status = (
            "Applied source-accepted PMenu action: "
            f"{result.action.action_kind} {menu_id:#x}"
        )
        return result

    def apply_source_accepted_squad_view(self, control_id: int):
        """Apply one proven Squad container transition after source acceptance.

        No modern pointer/key event is mapped here. Controls 4/5 intentionally
        redraw with their unresolved post-event Squad pixels withheld.
        """
        if self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            raise OriginalGameHostError(
                "Source-accepted Squad view transition requires the MANAGEMENT host"
            )
        if self.management_presenter is None:
            self.management_presenter = self.management_presenter_factory(
                self.presenter.session
            )
        activation = self.management_presenter.source_accepted_squad_view_transition(
            control_id
        )
        self.last_squad_view_activation = activation
        self.redraw()
        transition = activation.transition
        self.last_status = (
            "Applied source-accepted Squad view transition: "
            f"{transition.control_id} {transition.original_text}; "
            "post-event formation/player pixels remain fail-closed"
        )
        return activation

    def apply_source_accepted_fixture_match_info(
        self,
        *,
        fixture_present: bool,
        linked_context_available: bool,
        pointer_x: int,
        pointer_y: int,
    ):
        """Open only the source-proven PMatchInfo popup after its two source gates.

        The native right-press adapter resolves an explicit report owner/link
        before entering this seam. It never fabricates that owner from results.
        Other callers must supply already-adjudicated gate inputs explicitly;
        this seam alone is not evidence of ordinary runtime capture production.
        """
        if self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            raise OriginalGameHostError(
                "Source-accepted PMatchInfo action requires the MANAGEMENT host"
            )
        if self.management_presenter is None:
            self.management_presenter = self.management_presenter_factory(
                self.presenter.session
            )
        action = self.management_presenter.fixture_match_info_action(
            fixture_present=fixture_present,
            linked_context_available=linked_context_available,
        )
        if action is None:
            self.last_pmatchinfo_action = None
            self.active_pmatchinfo_art = None
            self.active_pmatchinfo_context = None
            self.last_status = "PMatchInfo source action rejected by recovered fixture gates"
            return None

        snapshot = self.pmatchinfo_snapshot
        if not isinstance(snapshot, OriginalPMatchInfoStaticSnapshot):
            raise OriginalGameHostError(
                "PMatchInfo action requires the verified complete popup snapshot"
            )
        art = build_pmatchinfo_popup_art(
            snapshot,
            pointer_x=pointer_x,
            pointer_y=pointer_y,
        )
        self.last_pmatchinfo_action = action
        self.active_pmatchinfo_context = None
        self.active_pmatchinfo_art = art
        self.redraw()
        self.last_status = (
            "Opened source-accepted PMatchInfo popup at "
            f"({art.x}, {art.y}); nested owner-local child art remains fail-closed"
        )
        return action

    def apply_source_accepted_pmatchinfo_exit(self) -> None:
        """Close the modal only after a separately source-accepted exit event."""
        if self.active_pmatchinfo_art is None:
            raise OriginalGameHostError("No active PMatchInfo dialog to close")
        self.active_pmatchinfo_art = None
        self.active_pmatchinfo_context = None
        self.last_pmatchinfo_action = None
        self.redraw()
        self.last_status = "Closed source-accepted PMatchInfo popup"

    def on_fixture_report_press(self, event) -> None:
        """WM_RBUTTONDOWN equivalent, proven at 0x531CF0..FA / 0x653600.

        Opening requires the native captured-report owner, not completion or a
        score. Current backend capture production remains incomplete, so an
        ordinary uncaptured fixture is still a source-compatible no-op.
        """
        if (self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT
                or self.active_pmatchinfo_art is not None):
            return
        if self.management_presenter is None:
            self.management_presenter = self.management_presenter_factory(self.presenter.session)
        try:
            context = self.management_presenter.fixture_report_at_screen_point(
                int(event.x), int(event.y))
        except Exception as exc:
            self.last_status = f'{type(exc).__name__}: {exc}'
            self.error_reporter(self.last_status)
            return
        if context is None:
            self.last_status = 'Native fixture report unavailable; no score-derived context'
            return
        try:
            action = self.apply_source_accepted_fixture_match_info(
                fixture_present=True, linked_context_available=True,
                pointer_x=int(event.x), pointer_y=int(event.y))
        except Exception as exc:
            self.last_status = f'{type(exc).__name__}: {exc}'
            self.error_reporter(self.last_status)
            return
        if action is not None:
            self.active_pmatchinfo_context = context

    def on_click(self, event) -> None:
        if self.presenter.session.navigation.screen is FrontEndScreen.MANAGEMENT:
            if self.active_pmatchinfo_art is not None:
                self.last_status = (
                    "PMatchInfo pointer interaction remains fail-closed until "
                    "owner-local source control transforms are recovered"
                )
                return
            if self.management_presenter is None:
                self.management_presenter = self.management_presenter_factory(
                    self.presenter.session
                )
            frame = build_management_canvas_frame(self.management_presenter)
            candidate = candidate_pmenu_row_at_screen_point(
                frame.presentation.menu,
                int(event.x),
                int(event.y),
            )
            if candidate is None:
                self.last_pmenu_activation = None
                self.last_status = (
                    "Management host active; no source-bounded PMenu candidate "
                    f"row at ({int(event.x)}, {int(event.y)})"
                )
            else:
                menu = frame.presentation.menu
                local_x = int(event.x) - menu.list_screen_origin[0]
                local_y = int(event.y) - menu.list_screen_origin[1] - candidate.y
                source_flags = 1 if candidate.selected else 0
                action = resolve_pmenu_pointer_press(
                    candidate.row_kind,
                    candidate.menu_id,
                    source_flags,
                    local_x,
                    local_y,
                )
                if action is None:
                    self.last_status = "PMenu pointer press rejected by source control gates"
                    return
                try:
                    result = self.management_presenter.source_accepted_pmenu_action(
                        candidate.row_kind,
                        candidate.menu_id,
                        source_flags,
                    )
                    self.last_pmenu_activation = result
                    self.redraw()
                    self.last_status = (
                        "PMenu source pointer press: "
                        f"{result.action.action_kind} {candidate.menu_id:#x}"
                    )
                except Exception as exc:
                    self.last_status = f"{type(exc).__name__}: {exc}"
            return
        try:
            result = self.presenter.pointer(int(event.x), int(event.y))
            if result is None:
                self.last_status = "No recovered action at this pixel"
            elif isinstance(result, OriginalHierarchyInteraction):
                self.last_status = (
                    f"{result.row_kind}:{result.source_id}:{result.text}"
                )
            elif result.transition.command is FrontEndCommand.TEAMSELECT_START_CONTINUE:
                self.last_status = "Entered recovered PMenu management host"
            elif result.transition.command is not None:
                self.last_status = result.transition.command.name
            else:
                self.last_status = result.transition.screen.name
        except Exception as exc:
            self.last_status = f"{type(exc).__name__}: {exc}"
            self.error_reporter(self.last_status)
            return
        self.redraw()


def play_configured_startup_media(
    *,
    receipt_path: str | Path | None,
    backend,
    repo_root: str | Path | None = None,
):
    """Run verified startup media only when both explicit inputs are configured."""
    if receipt_path is None and backend is None:
        return None
    if receipt_path is None or backend is None:
        raise OriginalGameHostError(
            "Startup media requires both a private conversion receipt and a playback backend"
        )
    return load_and_play_verified_startup_sequence(
        receipt_path=Path(receipt_path),
        repo_root=REPO_ROOT if repo_root is None else Path(repo_root),
        backend=backend,
    )


def run_original_game_ui(
    game_dir: str | Path,
    *,
    source_root: str | Path | None = None,
    startup_media_receipt: str | Path | None = None,
    startup_media_backend=None,
    repo_root: str | Path | None = None,
) -> None:
    """Launch verified startup media, then the current source-backed UI surface."""
    play_configured_startup_media(
        receipt_path=startup_media_receipt,
        backend=startup_media_backend,
        repo_root=repo_root,
    )
    resolved_source_root = (
        DEFAULT_SOURCE_ROOT if source_root is None else Path(source_root)
    )
    presenter = build_original_game_presenter(
        game_dir,
        source_root=resolved_source_root,
    )
    original_executable = Path(game_dir) / "FOOTBAL.EXE"
    pmenu_resources = load_verified_management_pmenu_resources(
        resolved_source_root,
        original_executable,
    )
    fixture_resources = validate_original_league_fixtures_resources(
        resolved_source_root
    )
    fixture_grid_art = load_verified_league_fixtures_grid_art(
        resolved_source_root,
        original_executable,
    )
    squad_top_resources = load_verified_squad_top_resources(
        resolved_source_root,
        original_executable,
    )
    league_table_resources = validate_original_league_tables_resources(
        resolved_source_root
    )
    league_tables_header_art = load_verified_league_tables_header_art(
        resolved_source_root,
        original_executable,
    )
    runtime_repo_root = REPO_ROOT if repo_root is None else Path(repo_root)
    pmatchinfo_snapshot = load_staged_pmatchinfo_snapshot(
        runtime_repo_root,
        original_executable,
        require_complete_dialog=True,
    )
    import tkinter as tk

    root = tk.Tk()
    OriginalGameTkHost(
        presenter,
        root,
        tk,
        management_presenter_factory=lambda session: OriginalManagementPresenter(
            session,
            staged_league_fixture_resource_names=tuple(
                resource.name for resource in fixture_resources
            ),
            staged_league_table_resource_names=tuple(
                resource.name for resource in league_table_resources
            ),
        ),
        management_pmenu_resources=pmenu_resources,
        league_fixtures_grid_art=fixture_grid_art,
        squad_top_resources=squad_top_resources,
        league_tables_header_art=league_tables_header_art,
        pmatchinfo_snapshot=pmatchinfo_snapshot,
        management_background=OriginalManagementBackground(
            resolved_source_root, original_executable),
    )
    root.mainloop()
