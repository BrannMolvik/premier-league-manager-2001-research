"""Clean fixed-surface FM2001 application host for recovered original UI.

Unlike the Gate-13 diagnostic viewer, this host has no manual source-frame
controls or developer sidebar. It renders the source-backed first screens at
native 800x600 coordinates using the recovered initial Button@ease frame and
routes proven clicks through FrontEndSession. Successful TeamSelect Start enters
the fixed PMenu management host.

The management shell still has two explicit pixel blockers: the surrounding
application-owned management background and exact PMenu label origin/clipping.
When that state is reached this host fails closed rather than drawing the old
generic ttk Play replacement or inventing a skin.
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
from original_management_canvas import build_management_canvas_frame
from original_management_presenter import OriginalManagementPresenter
from original_pmenu_presenter import candidate_pmenu_row_at_screen_point
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
from original_teamselect_resources import load_verified_original_teamselect_inputs


DEFAULT_SOURCE_ROOT = (
    Path(__file__).resolve().parent.parent / "original_assets" / "source"
)
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
    ):
        self.presenter = presenter
        self.root = root
        self.tk = tk
        self.management_presenter_factory = (
            management_presenter_factory
            or (lambda session: OriginalManagementPresenter(session))
        )
        self.management_presenter = None
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
        if frame.complete_source_pixel_frame_available:
            raise OriginalGameHostError(
                "Management pixel renderer flag changed without a renderer implementation"
            )

        # Do not preserve the previous TeamSelect image underneath PMenu. The
        # original management background is not yet source-bound, so the only
        # honest live state is an empty fixed host with the recovered presenter
        # attached and no invented pixels.
        self.canvas.delete("all")
        self._photos = []
        self.last_status = (
            f"Management host active: {frame.presentation.panel_class}; "
            "source background/text placement still unresolved"
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
                self.last_status = (
                    "Management host active; no source-bounded PMenu candidate "
                    f"row at ({int(event.x)}, {int(event.y)})"
                )
            else:
                self.last_status = (
                    "PMenu candidate row only: "
                    f"{candidate.caption} (menu ID {candidate.menu_id:#x}); "
                    "native activation unresolved; no navigation dispatched"
                )
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


def run_original_game_ui(
    game_dir: str | Path,
    *,
    source_root: str | Path | None = None,
) -> None:
    """Launch the current source-backed UI as the normal application surface."""
    presenter = build_original_game_presenter(
        game_dir,
        source_root=source_root,
    )
    import tkinter as tk

    root = tk.Tk()
    OriginalGameTkHost(presenter, root, tk)
    root.mainloop()
