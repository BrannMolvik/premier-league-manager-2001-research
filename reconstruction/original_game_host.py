"""Clean fixed-surface FM2001 application host for recovered original UI.

Unlike the Gate-13 diagnostic viewer, this host has no manual source-frame
controls or developer sidebar. It renders the source-backed first screens at
native 800x600 coordinates using the recovered initial Button@ease frame and
routes proven clicks through FrontEndSession. Successful TeamSelect Start enters
the fixed PMenu management host.

The surrounding application-owned management background remains unresolved,
but the PMenu row assets, exact title/child fonts, line origins, clipping and
static state colors/arrows are source-backed. The management host renders those
known pixels and leaves only the unrecovered surrounding shell fail-closed
rather than drawing the old generic ttk Play replacement or inventing a skin.
"""
from __future__ import annotations

from base64 import b64encode
from pathlib import Path

from front_end_session import FrontEndSession
from front_end_state import FrontEndCommand, FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter,
    OriginalHierarchyInteraction,
)
from original_live_debug_view import build_original_debug_frame, endpoint_text_rgba
from original_management_canvas import (
    build_management_canvas_frame,
    build_management_pmenu_render,
    load_verified_management_pmenu_resources,
)
from original_management_presenter import OriginalManagementPresenter
from original_management_panel_canvas import (
    build_management_panel_render,
    load_verified_management_panel_resources,
)
from original_pmenu_activation import resolve_pmenu_pointer_press
from original_pmenu_presenter import candidate_pmenu_row_at_screen_point
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
from original_teamselect_resources import load_verified_original_teamselect_inputs
from startup_media_playback import load_and_play_verified_startup_sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_ROOT = REPO_ROOT / "original_assets" / "source"
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
        management_panel_resources=None,
    ):
        self.presenter = presenter
        self.root = root
        self.tk = tk
        self.management_panel_resources = management_panel_resources
        if management_presenter_factory is None:
            staged_fixtures = (
                ()
                if management_panel_resources is None
                else management_panel_resources.league_fixtures_resource_names
            )
            self.management_presenter_factory = lambda session: OriginalManagementPresenter(
                session,
                staged_league_fixture_resource_names=staged_fixtures,
            )
        else:
            self.management_presenter_factory = management_presenter_factory
        self.management_presenter = None
        self.management_pmenu_resources = management_pmenu_resources
        self.last_pmenu_activation = None
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
        self.canvas.bind("<Button-1>", self.on_click)
        self.redraw()

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
        panel_render = None
        if self.management_panel_resources is not None:
            panel_render = build_management_panel_render(
                frame,
                self.management_panel_resources,
            )

        self.canvas.delete("all")
        self._photos = []

        # Panel-owned art is below PMenu. This preserves the recovered native
        # overlap where the menu occupies the right edge of management panels.
        if panel_render is not None:
            for overlay in panel_render.overlays:
                art = self._photo(overlay.png)
                self.canvas.create_image(
                    overlay.x,
                    overlay.y,
                    image=art,
                    anchor=self.tk.NW,
                )

        menu_x, menu_y, _menu_w, _menu_h = frame.menu_rect
        for overlay in menu_render.overlays:
            art = self._photo(overlay.png)
            self.canvas.create_image(
                menu_x + overlay.x,
                menu_y + overlay.y,
                image=art,
                anchor=self.tk.NW,
            )

        panel_pixel_count = 0 if panel_render is None else len(panel_render.overlays)
        self.last_status = (
            f"Management host active: {frame.presentation.panel_class}; "
            f"{panel_pixel_count} source panel overlays; source PMenu rows rendered; "
            "surrounding management background unresolved"
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

    def on_click(self, event) -> None:
        if self.presenter.session.navigation.screen is FrontEndScreen.MANAGEMENT:
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
    panel_resources = load_verified_management_panel_resources(
        resolved_source_root,
        original_executable,
    )
    import tkinter as tk

    root = tk.Tk()
    OriginalGameTkHost(
        presenter,
        root,
        tk,
        management_pmenu_resources=pmenu_resources,
        management_panel_resources=panel_resources,
    )
    root.mainloop()
