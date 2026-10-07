"""Clean fixed-surface FM2001 application host for recovered original UI.

Unlike the Gate-13 diagnostic viewer, this host has no manual source-frame
controls or developer sidebar. It renders the source-backed first screens at
native 800x600 coordinates using recovered live Button@ease update states and
routes proven clicks through FrontEndSession. Successful TeamSelect Start enters
the fixed PMenu management host.

The application-owned seasonal base and competition header are source-backed
for the twenty original Premiership clubs. PMenu row assets, fonts and geometry
are also recovered. Remaining shell controls and ordinary match-report context
capture stay fail-closed; the host does not invent a replacement skin.
"""
from __future__ import annotations

from base64 import b64encode
from functools import lru_cache
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import struct
import sys
import traceback
import zlib
from types import SimpleNamespace
from original_management_background import OriginalManagementBackground
from original_management_header import (
    HEADER_COMPOUND_RECT,
    OriginalManagementHeaderResources,
    OriginalManagementHeaderState,
    load_verified_management_header_resources,
    management_header_caption_overlay,
    management_header_overlays,
)
from original_fixtures_pager import (
    OriginalFixturesPagerArt, fixtures_page_controls, fixtures_page_press,
    load_verified_fixtures_pager_art,
)
from original_pmatchinfo_summary import (
    ordinary_pmatchinfo_summary_lines, summary_line_pixels,
    ordinary_pmatchinfo_pitch_pixels,
    ordinary_pmatchinfo_possession_lines, load_pmatchinfo_nested_font,
    ordinary_pmatchinfo_header_lines,
)
from original_pmatchinfo_script_rows import load_script_row_art
from original_pmenu_chrome import validate_original_pmenu_font

from front_end_session import FrontEndSession
from front_end_settings import load_source_styled_settings_resources
from front_end_state import FrontEndCommand, FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from gate14_live_first_screen_audio import (
    Gate14LiveFirstScreenAudioError,
    install_live_first_screen_audio,
)
from gate14_match_detail_route_source import (
    MatchPresentationRoute,
    source_match_detail_dispatch,
)
from gate14_fastview_human_tk_window import open_human_fastview_tk_window
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter,
    OriginalHierarchyInteraction,
)
from original_live_debug_view import build_original_debug_frame, endpoint_text_rgba
from original_front_end_animation import OriginalFirstScreenAnimation
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
from original_management_club_caption import management_club_caption_pixels
from original_management_text import (
    OriginalManagementTextResources,
    league_tables_row_text_overlays,
    load_verified_management_text_resources,
)
from original_pmatchinfo_art import (
    OriginalPMatchInfoPopupArt,
    build_pmatchinfo_popup_art,
)
from original_pmatchinfo_presenter import (
    OriginalPMatchInfoStaticSnapshot,
    load_staged_pmatchinfo_snapshot,
)
from original_pmenu_activation import resolve_pmenu_pointer_press
from original_pmenu_popup import pmenu_open_press, pmenu_app_pointer_dismiss
from original_pmenu_presenter import candidate_pmenu_row_at_screen_point
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
from gate13_pstartmenu_derivative import (
    PSTARTMENU_SOURCE_ORIGINALS,
    PStartMenuDecoderProvenance,
    load_verified_pstartmenu_derivative_bundle,
)
from original_teamselect_resources import load_verified_original_teamselect_inputs
from original_squad_status import (
    OriginalSquadStatusResources,
    build_first_roster_direct_status_overlays,
    load_verified_squad_status_resources,
)
from original_squad_top_controls import (
    OriginalSquadTopResources,
    build_fresh_squad_top_render,
    load_verified_squad_top_resources,
)
from original_squad_row_style import (
    build_first_roster_column_heading_overlays,
    OriginalSquadRowTextResources,
    build_first_roster_name_overlays,
    build_first_roster_role_overlays,
    build_first_roster_scf_numeric_overlays,
    load_verified_squad_row_text_resources,
)
from startup_fmv_presentation import ORIGINAL_STARTUP_FMV_PRESENTATION
from startup_media_input import WM_KEYDOWN, VK_ESCAPE
from original_window_viewport import window_fit_scale
from startup_media_playback import (
    load_and_play_verified_startup_sequence,
    play_verified_startup_sequence,
)
from runtime_layout import application_root, bundled_source_root
from runtime_diagnostics import timed_stage


REPO_ROOT = application_root()
DEFAULT_SOURCE_ROOT = bundled_source_root()
DEFAULT_PSTARTMENU_DERIVATIVE_ROOT = (
    REPO_ROOT / "original_assets" / "converted" / "pstartmenu-v1"
)
PSTARTMENU_DERIVATIVE_MANIFEST_SHA256 = (
    "cc541cac0e844abdb7539627ea68a982288c0ba735a6bf91c84d3c502961877e"
)
PSTARTMENU_DERIVATIVE_DECODER = PStartMenuDecoderProvenance(
    executable_sha256=(
        "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"
    ),
    tqia_section_sha256=(
        "c62a13efbb812fb2157c067aaa3eae8afbbb52283dc5dc3eaf6cb86c5a11e8da"
    ),
    quant_source_sha256=(
        "6fb2af66cb6a51e4b3fa7da9bacab417fa40f180aa0c18c85adb2550c04c89eb"
    ),
)
SCREEN_SIZE = (800, 600)

MANAGEMENT_RESOURCE_FAMILY_BY_PANEL = {
    "PSquadScreen": "squad",
    "PLeagueFixtures": "fixtures",
    "PLeagueTables": "league_tables",
}
MANAGEMENT_RESOURCE_FAMILIES = frozenset(MANAGEMENT_RESOURCE_FAMILY_BY_PANEL.values())


@lru_cache(maxsize=1024)
def _cached_runtime_png(width: int, height: int, rgba: bytes) -> bytes:
    return encode_rgba_png(width, height, rgba)


@lru_cache(maxsize=32)
def _scaled_rgba(
    width: int,
    height: int,
    rgba: bytes,
    numerator: int,
    denominator: int,
) -> tuple[int, int, bytes]:
    """Nearest-neighbour scale directly to the final rational-size surface.

    This deliberately avoids Tk's zoom(n)->subsample(d) path, which can create
    very large transient images (for example 5600x4200 for a 7/4 scale of the
    800x600 background) and caused hands-on TeamSelect stalls/crashes.
    """
    if numerator <= 0 or denominator <= 0:
        raise OriginalGameHostError("Invalid display scale")
    if len(rgba) != width * height * 4:
        raise OriginalGameHostError("RGBA source size does not match geometry")
    if numerator == denominator:
        return width, height, rgba

    out_width = (width * numerator + denominator - 1) // denominator
    out_height = (height * numerator + denominator - 1) // denominator

    # Cache each scaled source row; vertical nearest-neighbour scaling often
    # reuses source rows, while the horizontal mapping is identical for every
    # row of the image.
    xmap = tuple(
        min(width - 1, x * denominator // numerator)
        for x in range(out_width)
    )
    row_cache: dict[int, bytes] = {}
    output = bytearray(out_width * out_height * 4)
    for out_y in range(out_height):
        src_y = min(height - 1, out_y * denominator // numerator)
        scaled_row = row_cache.get(src_y)
        if scaled_row is None:
            src_start = src_y * width * 4
            source_row = rgba[src_start:src_start + width * 4]
            row = bytearray(out_width * 4)
            for out_x, src_x in enumerate(xmap):
                src = src_x * 4
                dst = out_x * 4
                row[dst:dst + 4] = source_row[src:src + 4]
            scaled_row = bytes(row)
            row_cache[src_y] = scaled_row
        dst_start = out_y * out_width * 4
        output[dst_start:dst_start + len(scaled_row)] = scaled_row
    return out_width, out_height, bytes(output)


@lru_cache(maxsize=256)
def _decode_generated_rgba_png(png: bytes) -> tuple[int, int, bytes]:
    """Decode PNGs produced by this reconstruction's filter-0 RGBA encoder."""
    signature = b"\x89PNG\r\n\x1a\n"
    if not png.startswith(signature):
        raise OriginalGameHostError("Unsupported non-PNG management layer")
    cursor = len(signature)
    width = height = None
    compressed = bytearray()
    while cursor + 12 <= len(png):
        size = struct.unpack(">I", png[cursor:cursor + 4])[0]
        kind = png[cursor + 4:cursor + 8]
        data_start = cursor + 8
        data_end = data_start + size
        if data_end + 4 > len(png):
            raise OriginalGameHostError("Truncated generated PNG")
        data = png[data_start:data_end]
        if kind == b"IHDR":
            if len(data) != 13:
                raise OriginalGameHostError("Invalid generated PNG IHDR")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", data
            )
            if (
                bit_depth != 8
                or color_type != 6
                or compression != 0
                or filter_method != 0
                or interlace != 0
            ):
                raise OriginalGameHostError("Unsupported generated PNG format")
        elif kind == b"IDAT":
            compressed.extend(data)
        elif kind == b"IEND":
            break
        cursor = data_end + 4
    if width is None or height is None:
        raise OriginalGameHostError("Generated PNG is missing IHDR")
    scanlines = zlib.decompress(bytes(compressed))
    row_bytes = width * 4
    expected = height * (row_bytes + 1)
    if len(scanlines) != expected:
        raise OriginalGameHostError("Generated PNG scanline size mismatch")
    rgba = bytearray(width * height * 4)
    for row in range(height):
        src = row * (row_bytes + 1)
        if scanlines[src] != 0:
            raise OriginalGameHostError("Generated PNG used an unexpected filter")
        dst = row * row_bytes
        rgba[dst:dst + row_bytes] = scanlines[src + 1:src + 1 + row_bytes]
    return width, height, bytes(rgba)


@lru_cache(maxsize=512)
def _cached_endpoint_png(
    width: int,
    height: int,
    alpha: bytes,
    native_color_16: int,
) -> bytes:
    return encode_rgba_png(
        width,
        height,
        endpoint_text_rgba(alpha, native_color_16),
    )


class OriginalGameHostError(RuntimeError):
    """The source-backed application host cannot continue safely."""


def build_original_game_presenter(
    game_dir: str | Path,
    *,
    source_root: str | Path | None = None,
    pstartmenu_derivative_root: str | Path | None = None,
) -> OriginalFirstScreenPresenter:
    """Load the first screen from the pinned derivative in normal runtime.

    Explicit custom source roots retain the original source-decoder path for
    research/verification. The default packaged/repository runtime must use the
    separately pinned deterministic derivative and fails closed if it is absent
    or differs; it never silently falls back to a 26-second cold source decode.
    """
    game_dir = Path(game_dir)
    root = DEFAULT_SOURCE_ROOT if source_root is None else Path(source_root)
    executable = game_dir / "FOOTBAL.EXE"
    art_root = root / "FM2001_Art"

    if source_root is None or root.resolve() == DEFAULT_SOURCE_ROOT.resolve():
        derivative_root = (
            DEFAULT_PSTARTMENU_DERIVATIVE_ROOT
            if pstartmenu_derivative_root is None
            else Path(pstartmenu_derivative_root)
        )
        menu = load_verified_pstartmenu_derivative_bundle(
            derivative_root,
            expected_decoder=PSTARTMENU_DERIVATIVE_DECODER,
            expected_manifest_sha256=PSTARTMENU_DERIVATIVE_MANIFEST_SHA256,
            expected_sources=PSTARTMENU_SOURCE_ORIGINALS,
        )
    else:
        if pstartmenu_derivative_root is not None:
            raise OriginalGameHostError(
                "Explicit PStartMenu derivative root is valid only with the "
                "default verified source root"
            )
        font20 = root / "Fonts" / "Zurich_BdXCn_BT_20pixel.fnt"
        menu = load_verified_english_pstartmenu_inputs(
            original_art_dir=art_root,
            original_language_dir=root,
            original_zurich_font20=font20,
            original_executable=executable,
        )

    # Canonical original-behavior audit: 4C1BA0 creates only the four recovered
    # PStartMenu actions. Keep the non-original Settings extension available to
    # explicit research presenters, but absent from the normal/default host.
    # It must not be a resource-loading dependency of the original baseline.
    return OriginalFirstScreenPresenter(
        FrontEndSession.for_canonical_game_dir(game_dir),
        menu,
        team_select_loader=lambda: load_verified_original_teamselect_inputs(
            original_art_dir=art_root,
            original_executable=executable,
        ),
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
        fixtures_pager_art=None,
        squad_top_resources=None,
        squad_row_text_resources=None,
        squad_status_resources=None,
        league_tables_header_art=None,
        pmatchinfo_snapshot=None,
        pmatchinfo_font=None,
        pmatchinfo_nested_font=None,
        pmatchinfo_script_art=None,
        error_reporter=None,
        management_background=None,
        management_header_resources=None,
        management_text_resources=None,
        management_resource_loader=None,
        management_thread_factory=Thread,
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
        self.fixtures_pager_art = fixtures_pager_art
        self.fixtures_pager_flags = {-1: 0x183, 1: 0x183}
        # PMenu is pushed by application event 2, not a permanent panel layer.
        self.pmenu_popup_active = False
        self.squad_top_resources = squad_top_resources
        self.squad_row_text_resources = squad_row_text_resources
        self.squad_status_resources = squad_status_resources
        self.league_tables_header_art = league_tables_header_art
        self.pmatchinfo_snapshot = pmatchinfo_snapshot
        self.pmatchinfo_font = pmatchinfo_font
        self.pmatchinfo_nested_font = pmatchinfo_nested_font
        self.pmatchinfo_script_art = pmatchinfo_script_art
        self.error_reporter = error_reporter or self._show_transition_error
        self.management_background = management_background
        self.management_header_resources = management_header_resources
        self.management_text_resources = management_text_resources
        self.management_resource_loader = management_resource_loader
        if not callable(management_thread_factory):
            raise OriginalGameHostError("management_thread_factory must be callable")
        self.management_thread_factory = management_thread_factory
        self._management_resource_families_loaded = (
            set(MANAGEMENT_RESOURCE_FAMILIES)
            if management_resource_loader is None
            else set()
        )
        # Compatibility alias retained for the fresh MANAGEMENT boundary: it now
        # means the shell + fresh Squad family is ready, not that every panel has
        # been eagerly decoded.
        self._management_resources_loaded = "squad" in self._management_resource_families_loaded
        self._management_loading_family = None
        self._management_load_queue = None
        self._management_load_thread = None
        self._management_load_poll = None
        self.management_header_state = OriginalManagementHeaderState()
        self._management_header_idle = None
        self.last_pmenu_activation = None
        self.last_squad_view_activation = None
        self.last_league_fixtures_grid_activation = None
        self.last_pmatchinfo_action = None
        self.active_pmatchinfo_context = None
        self.pmatchinfo_script_offsets = {1: 0, 0: 0}
        self.pmatchinfo_script_pressed = None
        self.active_pmatchinfo_art = None
        self._photos = []
        self._first_screen_photo_cache = {}
        self._generic_photo_cache = {}
        self.first_screen_animation = OriginalFirstScreenAnimation()
        self.first_screen_frame = None
        self._first_screen_items = {}
        self._first_screen_pointer = None
        self._first_screen_idle = None
        self.last_status = "Source-backed FM2001 host ready"
        self.last_fastview_window = None

        self.root.title("Premier League Manager 2001")
        self.root.resizable(True, True)
        if callable(getattr(self.root, "minsize", None)):
            self.root.minsize(320, 240)
        self._viewport_resize_idle = None
        self._pending_viewport_size = None
        self._windowed_size = SCREEN_SIZE
        self._fullscreen = False
        screen_width = (
            int(self.root.winfo_screenwidth())
            if hasattr(self.root, "winfo_screenwidth")
            else SCREEN_SIZE[0]
        )
        screen_height = (
            int(self.root.winfo_screenheight())
            if hasattr(self.root, "winfo_screenheight")
            else SCREEN_SIZE[1]
        )
        self.display_scale_num, self.display_scale_den = window_fit_scale(
            screen_width, screen_height
        )
        self.display_scale = self.display_scale_num / self.display_scale_den
        self.display_width = (
            SCREEN_SIZE[0] * self.display_scale_num + self.display_scale_den - 1
        ) // self.display_scale_den
        self.display_height = (
            SCREEN_SIZE[1] * self.display_scale_num + self.display_scale_den - 1
        ) // self.display_scale_den
        if hasattr(self.root, "configure"):
            self.root.configure(background="black")
        self.canvas = tk.Canvas(
            root,
            width=self.display_width,
            height=self.display_height,
            highlightthickness=0,
            borderwidth=0,
        )
        # Keep native 800x600 game coordinates intact. In fullscreen the
        # canvas is centered rather than stretched, avoiding interpolation and
        # preserving every recovered pointer rectangle exactly.
        self.canvas.pack(expand=True)
        self.root.bind("<Configure>", self.on_window_configure)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Alt-Return>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.leave_fullscreen)
        self._set_fullscreen(True)
        self.canvas.bind("<Button-3>", self.on_fixture_report_press)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_script_arrow_release)
        self.canvas.bind("<Motion>", self.on_fixtures_pager_motion)
        self.canvas.bind("<Leave>", self.on_fixtures_pager_leave)
        self.redraw()

    def on_window_configure(self, event) -> None:
        if getattr(event, "widget", None) is not self.root:
            return  # Child/configure events are not the available game client.
        width, height = int(event.width), int(event.height)
        if width < 320 or height < 240:
            return  # Ignore construction/minimization, not a usable viewport.
        self._pending_viewport_size = (width, height)
        if self._viewport_resize_idle is None:
            self._viewport_resize_idle = self.root.after(50, self._resize_viewport)

    def _resize_viewport(self) -> None:
        self._viewport_resize_idle = None
        width, height = self._pending_viewport_size
        numerator, denominator = window_fit_scale(width, height)
        if (numerator, denominator) == (self.display_scale_num, self.display_scale_den):
            return
        self.display_scale_num, self.display_scale_den = numerator, denominator
        self.display_scale = numerator / denominator
        self.display_width = self._native_to_display(SCREEN_SIZE[0])
        self.display_height = self._native_to_display(SCREEN_SIZE[1])
        self.canvas.configure(width=self.display_width, height=self.display_height)
        # All cached PhotoImages carry the previous viewport scale. Retaining
        # them would mix sizes and break both visuals and pointer rectangles.
        self._first_screen_photo_cache.clear()
        self._generic_photo_cache.clear()
        self._photos = []
        if getattr(self, "_startup_media_active", False):
            self.canvas.coords(self._startup_media_backdrop, 0, 0,
                               self.display_width, self.display_height)
        else:
            self.redraw()

    def startup_media_child_binding(self) -> dict[str, int]:
        """Return the game-owned child-HWND rectangle for source-faithful FMVs."""
        for method_name in ("update_idletasks", "winfo_id"):
            if not callable(getattr(self.root, method_name, None)):
                raise OriginalGameHostError(
                    "Startup-media child hosting requires a realized Tk window"
                )
        for method_name in ("winfo_x", "winfo_y"):
            if not callable(getattr(self.canvas, method_name, None)):
                raise OriginalGameHostError(
                    "Startup-media child hosting requires realized canvas geometry"
                )
        self.root.update_idletasks()
        presentation = ORIGINAL_STARTUP_FMV_PRESENTATION
        return {
            "parent_hwnd": int(self.root.winfo_id()),
            "x": int(self.canvas.winfo_x())
            + self._native_to_display(presentation.movie_x),
            "y": int(self.canvas.winfo_y())
            + self._native_to_display(presentation.movie_y),
            "width": self._native_to_display(presentation.movie_width),
            "height": self._native_to_display(presentation.movie_height),
        }

    def show_startup_media_backdrop(self) -> None:
        """Hide the menu behind the native black startup-movie presentation field."""
        self._startup_media_active = True
        create = getattr(self.canvas, "create_rectangle", None)
        if not callable(create):
            raise OriginalGameHostError(
                "Startup-media backdrop requires a drawable game canvas"
            )
        self._startup_media_backdrop = create(
            0,
            0,
            self.display_width,
            self.display_height,
            fill="black",
            outline="",
        )
        raise_item = getattr(self.canvas, "tag_raise", None)
        if callable(raise_item):
            raise_item(self._startup_media_backdrop)
        update = getattr(self.root, "update", None)
        if callable(update):
            update()
        elif callable(getattr(self.root, "update_idletasks", None)):
            self.root.update_idletasks()

    def hide_startup_media_backdrop(self) -> None:
        self._startup_media_active = False
        item = getattr(self, "_startup_media_backdrop", None)
        if item is not None:
            self.canvas.delete(item)
            self._startup_media_backdrop = None
            self.redraw()

    def pump_startup_media_events(self) -> None:
        """Serve child-window messages before mainloop, without menu actions."""
        self.root.update()
        if not self.root.winfo_exists():
            raise OriginalGameHostError("Game window closed during startup media")

    def _set_fullscreen(self, enabled: bool) -> None:
        if enabled and not self._fullscreen and callable(getattr(self.root, "winfo_width", None)):
            size = (self.root.winfo_width(), self.root.winfo_height())
            if size[0] >= 320 and size[1] >= 240:
                self._windowed_size = size
        self._fullscreen = bool(enabled)
        self.presenter.session.settings.fullscreen = self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)
        if not enabled and callable(getattr(self.root, "geometry", None)):
            # Do not restore a monitor-sized requested canvas into a decorated
            # window; preserve the last actual windowed client instead.
            self.root.geometry(f"{self._windowed_size[0]}x{self._windowed_size[1]}")

    def toggle_fullscreen(self, event=None):
        if getattr(self, "_startup_media_active", False):
            return "break"  # The live WPF child owns the fixed presentation rect.
        self._set_fullscreen(not self._fullscreen)
        if self.presenter.session.navigation.screen is FrontEndScreen.SETTINGS:
            self.redraw()
        return "break"

    def leave_fullscreen(self, event=None):
        if getattr(self, "_startup_media_active", False):
            request = getattr(self, '_startup_native_input', None)
            if callable(request):
                request(WM_KEYDOWN, VK_ESCAPE)
            return "break"
        if self._fullscreen:
            self._set_fullscreen(False)
            if self.presenter.session.navigation.screen is FrontEndScreen.SETTINGS:
                self.redraw()
        return "break"

    def _normalize_pointer_event(self, event):
        # Real Tk events identify the canvas widget and arrive in scaled
        # display coordinates. Direct source/unit adapters intentionally pass
        # native coordinates without a widget and therefore remain unchanged.
        if (
            (self.display_scale_num != self.display_scale_den)
            and getattr(event, "widget", None) is self.canvas
        ):
            return SimpleNamespace(
                x=int(event.x) * self.display_scale_den // self.display_scale_num,
                y=int(event.y) * self.display_scale_den // self.display_scale_num,
            )
        return event

    def _photo_from_rgba(self, key, width: int, height: int, rgba: bytes):
        photo = self._first_screen_photo_cache.get(key)
        if photo is None:
            scaled_width, scaled_height, scaled_rgba = _scaled_rgba(
                width,
                height,
                rgba,
                self.display_scale_num,
                self.display_scale_den,
            )
            png = encode_rgba_png(scaled_width, scaled_height, scaled_rgba)
            photo = self.tk.PhotoImage(
                data=b64encode(png).decode("ascii"),
                format="png",
            )
            self._first_screen_photo_cache[key] = photo
        self._photos.append(photo)
        return photo

    def _native_to_display(self, value: int) -> int:
        return (
            int(value) * self.display_scale_num + self.display_scale_den - 1
        ) // self.display_scale_den

    def _create_native_image(self, x, y, **kwargs):
        return self.canvas.create_image(
            self._native_to_display(x),
            self._native_to_display(y),
            **kwargs,
        )

    def _first_screen_photo(self, key, png: bytes):
        """Cache an already-display-sized PNG.

        Kept for compatibility with source-backed callers that already provide
        final-size pixels. Native first-screen controls now use _photo_from_rgba
        to avoid transient Tk zoom allocations.
        """
        photo = self._first_screen_photo_cache.get(key)
        if photo is None:
            photo = self.tk.PhotoImage(
                data=b64encode(png).decode("ascii"),
                format="png",
            )
            self._first_screen_photo_cache[key] = photo
        self._photos.append(photo)
        return photo

    def _show_transition_error(self, message: str) -> None:
        # Port compatibility feedback, not a claimed original-game dialog.
        from tkinter import messagebox
        messagebox.showerror("FM2001 port: action could not complete", message,
                             parent=self.root)

    def _photo(self, png: bytes):
        # All host-generated management/report PNGs use the reconstruction's
        # deterministic RGBA/filter-0 encoder. Decode once, scale directly to
        # the final rational display size, and retain the Tk image by source
        # bytes so redraws do not repeat conversion or allocation.
        photo = self._generic_photo_cache.get(png)
        if photo is None:
            width, height, rgba = _decode_generated_rgba_png(png)
            scaled_width, scaled_height, scaled_rgba = _scaled_rgba(
                width,
                height,
                rgba,
                self.display_scale_num,
                self.display_scale_den,
            )
            scaled_png = encode_rgba_png(
                scaled_width,
                scaled_height,
                scaled_rgba,
            )
            photo = self.tk.PhotoImage(
                data=b64encode(scaled_png).decode("ascii"),
                format="png",
            )
            self._generic_photo_cache[png] = photo
        self._photos.append(photo)
        return photo

    def _rgba_photo(self, width: int, height: int, rgba: bytes):
        """Cache before PNG encoding, not after an unchanged image is compressed.

        Content and dimensions identify the pixels; a changed value never reuses
        stale text/art. The existing viewport invalidation clears this cache too.
        """
        return self._photo_from_rgba(('management-rgba', width, height, rgba),
                                     width, height, rgba)

    def _draw_first_screen(self) -> None:
        if self._management_header_idle is not None:
            self.root.after_cancel(self._management_header_idle)
            self._management_header_idle = None
        view = self.presenter.snapshot()
        self.first_screen_animation.observe(view, self._first_screen_pointer)
        frame = build_original_debug_frame(view, self.first_screen_animation.frames(view))
        self.first_screen_frame = frame
        self._schedule_first_screen_update(view)
        self.canvas.delete("all")
        self._photos = []
        self._first_screen_items = {}

        background = self._photo_from_rgba(
            (view.screen, "background"),
            SCREEN_SIZE[0],
            SCREEN_SIZE[1],
            view.background_rgba,
        )
        self._first_screen_items[("background", None)] = self._create_native_image(
            0, 0, image=background, anchor=self.tk.NW
        )

        controls_by_event = {control.event: control for control in view.controls}
        for overlay in frame.original_source_frame_overlays:
            source = controls_by_event[overlay.event].exact_source_frame(
                overlay.source_frame_index
            )
            art = self._photo_from_rgba(
                (view.screen, "button", overlay.event, overlay.source_frame_index),
                source.width,
                source.height,
                source.rgba,
            )
            self._first_screen_items[("button", overlay.event)] = (
                self._create_native_image(
                    overlay.rect.x,
                    overlay.rect.y,
                    image=art,
                    anchor=self.tk.NW,
                )
            )

        for caption in frame.native_caption_overlays:
            control = controls_by_event[caption.event]
            mask = control.caption.glyph_mask
            glyph_rgba = endpoint_text_rgba(mask.alpha, caption.native_color_16)
            glyphs = self._photo_from_rgba(
                (
                    view.screen,
                    "caption",
                    caption.event,
                    caption.native_color_16,
                    caption.original_text,
                ),
                mask.width,
                mask.height,
                glyph_rgba,
            )
            self._first_screen_items[("caption", caption.event)] = (
                self._create_native_image(
                    caption.line_origin_x,
                    caption.line_origin_y,
                    image=glyphs,
                    anchor=self.tk.NW,
                )
            )

        for row in (*view.hierarchy_rows, *view.club_rows):
            animation = self._photo_from_rgba(
                (
                    view.screen,
                    "team-row-animation-source",
                    row.row_kind,
                    row.animation_source_index,
                ),
                row.animation_frame.width,
                row.animation_frame.height,
                row.animation_frame.rgba,
            )
            bar = self._photo_from_rgba(
                (
                    view.screen,
                    "team-row-bar-source",
                    row.row_kind,
                    row.bar_source_index,
                ),
                row.bar_frame.width,
                row.bar_frame.height,
                row.bar_frame.rgba,
            )
            glyph_rgba = endpoint_text_rgba(
                row.glyph_mask.alpha,
                row.native_color_16,
            )
            glyphs = self._photo_from_rgba(
                (
                    view.screen,
                    "team-row-text",
                    row.text,
                    row.native_color_16,
                ),
                row.glyph_mask.width,
                row.glyph_mask.height,
                glyph_rgba,
            )
            row_key = (row.row_kind, int(row.source_id))
            self._first_screen_items[("team-row-animation", *row_key)] = (
                self._create_native_image(
                    row.animation_rect.x,
                    row.animation_rect.y,
                    image=animation,
                    anchor=self.tk.NW,
                )
            )
            self._first_screen_items[("team-row-bar", *row_key)] = (
                self._create_native_image(
                    row.bar_rect.x,
                    row.bar_rect.y,
                    image=bar,
                    anchor=self.tk.NW,
                )
            )
            self._first_screen_items[("team-row-text", *row_key)] = (
                self._create_native_image(
                    row.line_origin_x,
                    row.line_origin_y,
                    image=glyphs,
                    anchor=self.tk.NW,
                )
            )

    def _update_teamselect_club_row(self, source_id: int) -> bool:
        """Update one toggled club row without rebuilding the TeamSelect canvas."""
        if self.presenter.session.navigation.screen is not FrontEndScreen.TEAM_SELECT:
            return False
        view = self.presenter.snapshot()
        row = next(
            (item for item in view.club_rows if int(item.source_id) == int(source_id)),
            None,
        )
        if row is None:
            return False
        row_key = (row.row_kind, int(row.source_id))
        animation_item = self._first_screen_items.get(
            ("team-row-animation", *row_key)
        )
        bar_item = self._first_screen_items.get(("team-row-bar", *row_key))
        text_item = self._first_screen_items.get(("team-row-text", *row_key))
        if animation_item is None or bar_item is None or text_item is None:
            return False

        animation = self._photo_from_rgba(
            (
                view.screen,
                "team-row-animation-source",
                row.row_kind,
                row.animation_source_index,
            ),
            row.animation_frame.width,
            row.animation_frame.height,
            row.animation_frame.rgba,
        )
        bar = self._photo_from_rgba(
            (
                view.screen,
                "team-row-bar-source",
                row.row_kind,
                row.bar_source_index,
            ),
            row.bar_frame.width,
            row.bar_frame.height,
            row.bar_frame.rgba,
        )
        glyph_rgba = endpoint_text_rgba(
            row.glyph_mask.alpha,
            row.native_color_16,
        )
        glyphs = self._photo_from_rgba(
            (
                view.screen,
                "team-row-text",
                row.text,
                row.native_color_16,
            ),
            row.glyph_mask.width,
            row.glyph_mask.height,
            glyph_rgba,
        )
        self.canvas.itemconfigure(animation_item, image=animation)
        self.canvas.itemconfigure(bar_item, image=bar)
        self.canvas.itemconfigure(text_item, image=glyphs)
        return True

    def _schedule_first_screen_update(self, view):
        if self._first_screen_idle is None and self.first_screen_animation.pending(view):
            self._first_screen_idle = self.root.after_idle(self._advance_first_screen)

    def _update_first_screen_animation_layers(self, view) -> None:
        """Swap only Button/caption layers whose native source state changed.

        TeamSelect can have more than one hundred persistent row/background
        canvas items. Rebuilding all of them for every one of the eleven native
        hover subframes made the recovered animation unusably slow. The original
        control update changes only the affected Button child, so mirror that
        ownership here rather than performing a full-screen redraw.
        """
        previous = self.first_screen_frame
        frame = build_original_debug_frame(
            view,
            self.first_screen_animation.frames(view),
        )
        self.first_screen_frame = frame
        controls_by_event = {control.event: control for control in view.controls}
        previous_frames = (
            {}
            if previous is None or previous.screen is not frame.screen
            else {
                overlay.event: overlay.source_frame_index
                for overlay in previous.original_source_frame_overlays
            }
        )
        previous_colors = (
            {}
            if previous is None or previous.screen is not frame.screen
            else {
                caption.event: caption.native_color_16
                for caption in previous.native_caption_overlays
            }
        )

        for overlay in frame.original_source_frame_overlays:
            if previous_frames.get(overlay.event) == overlay.source_frame_index:
                continue
            item = self._first_screen_items.get(("button", overlay.event))
            if item is None:
                # A screen transition or unexpected ownership change requires a
                # normal full draw rather than fabricating an incremental item.
                self._draw_first_screen()
                return
            source = controls_by_event[overlay.event].exact_source_frame(
                overlay.source_frame_index
            )
            art = self._photo_from_rgba(
                (
                    view.screen,
                    "button",
                    overlay.event,
                    overlay.source_frame_index,
                ),
                source.width,
                source.height,
                source.rgba,
            )
            self.canvas.itemconfigure(item, image=art)

        for caption in frame.native_caption_overlays:
            if previous_colors.get(caption.event) == caption.native_color_16:
                continue
            item = self._first_screen_items.get(("caption", caption.event))
            if item is None:
                continue
            control = controls_by_event[caption.event]
            mask = control.caption.glyph_mask
            glyph_rgba = endpoint_text_rgba(mask.alpha, caption.native_color_16)
            glyphs = self._photo_from_rgba(
                (
                    view.screen,
                    "caption",
                    caption.event,
                    caption.native_color_16,
                    caption.original_text,
                ),
                mask.width,
                mask.height,
                glyph_rgba,
            )
            self.canvas.itemconfigure(item, image=glyphs)

        self._schedule_first_screen_update(view)

    def _advance_first_screen(self):
        self._first_screen_idle = None
        if self.presenter.session.navigation.screen not in (
                FrontEndScreen.START_MENU,
                FrontEndScreen.SETTINGS,
                FrontEndScreen.TEAM_SELECT,
        ):
            return
        view = self.presenter.snapshot()
        self.first_screen_animation.observe(view, self._first_screen_pointer)
        if self.first_screen_animation.advance(view):
            self._update_first_screen_animation_layers(view)

    @staticmethod
    def _management_resource_family(panel_class: str) -> str:
        try:
            return MANAGEMENT_RESOURCE_FAMILY_BY_PANEL[panel_class]
        except KeyError as exc:
            raise OriginalGameHostError(
                f"No management resource family is defined for {panel_class!r}"
            ) from exc

    def _apply_management_resources(self, family: str, loaded) -> None:
        if family not in MANAGEMENT_RESOURCE_FAMILIES:
            raise OriginalGameHostError(
                f"Unknown management resource family: {family!r}"
            )
        if not isinstance(loaded, dict):
            raise OriginalGameHostError(
                "Management resource loader must return a resource mapping"
            )
        required_by_family = {
            "squad": (
                "management_pmenu_resources",
                "squad_top_resources",
                "squad_row_text_resources",
                "squad_status_resources",
                "management_background",
                "management_header_resources",
            ),
            "fixtures": (
                "league_fixtures_grid_art",
                "fixtures_pager_art",
                "pmatchinfo_snapshot",
                "pmatchinfo_font",
                "pmatchinfo_nested_font",
                "pmatchinfo_script_art",
                "_fixture_resource_names",
            ),
            "league_tables": (
                "league_tables_header_art",
                "management_text_resources",
                "_league_table_resource_names",
            ),
        }
        required = required_by_family[family]
        missing = [name for name in required if name not in loaded]
        if missing:
            raise OriginalGameHostError(
                f"Management {family} resource loader omitted: " + ", ".join(missing)
            )
        for name in required:
            setattr(self, name, loaded[name])
        self._management_resource_families_loaded.add(family)
        self._management_resources_loaded = "squad" in self._management_resource_families_loaded

    def _ensure_management_resources(self, family: str = "squad") -> None:
        """Synchronous compatibility helper used outside the live Tk transition."""
        if family in self._management_resource_families_loaded:
            return
        loader = self.management_resource_loader
        if loader is None:
            self._management_resource_families_loaded.add(family)
            self._management_resources_loaded = "squad" in self._management_resource_families_loaded
            return
        with timed_stage(f"management.resources.load_{family}"):
            loaded = loader(family)
        self._apply_management_resources(family, loaded)

    def _schedule_management_resource_poll(self) -> None:
        if self._management_load_poll is None:
            self._management_load_poll = self.root.after(
                25,
                self._poll_management_resource_load,
            )

    def _begin_management_resource_load(self, family: str = "squad") -> None:
        """Decode one verified management route family without blocking Tk."""
        if family in self._management_resource_families_loaded:
            with timed_stage("management.first_draw"):
                self.redraw()
            return
        if self._management_load_thread is not None:
            return
        loader = self.management_resource_loader
        if loader is None:
            self._management_resource_families_loaded.add(family)
            self._management_resources_loaded = "squad" in self._management_resource_families_loaded
            with timed_stage("management.first_draw"):
                self.redraw()
            return

        self.last_status = f"Preparing source-backed management {family} resources..."
        self.root.configure(cursor="watch")
        result_queue = Queue()
        self._management_load_queue = result_queue
        self._management_loading_family = family

        def worker():
            try:
                with timed_stage(f"management.resources.load_{family}"):
                    loaded = loader(family)
            except Exception as exc:
                result_queue.put(("error", family, exc, traceback.format_exc()))
            else:
                result_queue.put(("ok", family, loaded, None))

        thread = self.management_thread_factory(target=worker, daemon=True)
        self._management_load_thread = thread
        thread.start()
        self._schedule_management_resource_poll()

    def _poll_management_resource_load(self) -> None:
        self._management_load_poll = None
        result_queue = self._management_load_queue
        if result_queue is None:
            return
        try:
            status, family, payload, traceback_text = result_queue.get_nowait()
        except Empty:
            self._schedule_management_resource_poll()
            return

        self._management_load_thread = None
        self._management_load_queue = None
        self._management_loading_family = None
        if status == "error":
            self.root.configure(cursor="")
            self.last_status = f"{type(payload).__name__}: {payload}"
            if traceback_text:
                print(traceback_text, file=sys.stderr, flush=True)
            self.error_reporter(self.last_status)
            return

        try:
            self._apply_management_resources(family, payload)
            self.root.configure(cursor="")
            with timed_stage("management.first_draw"):
                self.redraw()
        except Exception as exc:
            self.root.configure(cursor="")
            self.last_status = f"{type(exc).__name__}: {exc}"
            traceback.print_exc(file=sys.stderr)
            self.error_reporter(self.last_status)

    def _schedule_management_header_update(self) -> None:
        if (
            isinstance(self.management_header_resources, OriginalManagementHeaderResources)
            and self._management_header_idle is None
            and self.management_header_state.pending()
        ):
            self._management_header_idle = self.root.after_idle(
                self._advance_management_header
            )

    def _advance_management_header(self) -> None:
        self._management_header_idle = None
        if self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            return
        if self.management_header_state.update():
            self.redraw()

    def _draw_management_header(self, club=None) -> int:
        resources = self.management_header_resources
        if resources is None:
            return 0
        if not isinstance(resources, OriginalManagementHeaderResources):
            raise OriginalGameHostError(
                "Management header requires verified original header resources"
            )

        self.management_header_state.set_selected(self.pmenu_popup_active)
        frame = self.management_header_state.source_frame()
        count = 0
        for overlay in management_header_overlays(resources, frame):
            self._create_native_image(
                overlay.x,
                overlay.y,
                image=self._rgba_photo(overlay.width, overlay.height, overlay.rgba),
                anchor=self.tk.NW,
            )
            count += 1

        caption = management_header_caption_overlay(resources)
        self._create_native_image(
            caption.x,
            caption.y,
            image=self._rgba_photo(caption.width, caption.height, caption.rgba),
            anchor=self.tk.NW,
        )
        count += 1
        if club is not None and resources.club_font is not None:
            pixels = management_club_caption_pixels(
                resources.club_font, club.name, club.native_user_club_caption
            )
            if pixels is not None:
                x, y, width, height, rgba = pixels
                self._create_native_image(
                    x, y, image=self._rgba_photo(width, height, rgba), anchor=self.tk.NW
                )
                count += 1
        self._schedule_management_header_update()
        return count

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
            self._create_native_image(
                overlay.x,
                overlay.y,
                image=image,
                anchor=self.tk.NW,
            )
            count += 1
        return count

    def _draw_squad_rows(self, frame) -> int:
        """Draw source-closed first-roster text plus source-qualified PSCF status."""
        if frame.presentation.panel_class != "PSquadScreen":
            return 0
        transition = frame.presentation.squad_view_transition
        if transition is None:
            raise OriginalGameHostError(
                "Squad panel lost its source-proven view-transition state"
            )
        # The current presenter exposes the source-order first-roster viewport
        # only for the fresh combined control-3 state. Controls 4/5 still lack
        # complete post-event roster/pitch membership and therefore remain
        # fail-closed instead of reusing stale row pixels.
        if transition.control_id != 3:
            return 0
        snapshot = frame.presentation.squad
        if snapshot is None:
            raise OriginalGameHostError(
                "Squad landing renderer requires its source-backed row viewport"
            )
        resources = self.squad_row_text_resources
        if not isinstance(resources, OriginalSquadRowTextResources):
            raise OriginalGameHostError(
                "Squad landing renderer requires verified original row font resources"
            )
        overlays = (
            *build_first_roster_column_heading_overlays(resources),
            *build_first_roster_role_overlays(snapshot.rows, resources),
            *build_first_roster_name_overlays(snapshot.rows, resources),
            *build_first_roster_scf_numeric_overlays(snapshot.rows, resources),
        )
        count = 0
        for overlay in overlays:
            self._create_native_image(
                overlay.x,
                overlay.y,
                image=self._rgba_photo(overlay.width, overlay.height, overlay.rgba),
                anchor=self.tk.NW,
            )
            count += 1

        source_qualified_status_rows = tuple(
            row for row in snapshot.rows
            if getattr(row, "native_status_frame_index", None) is not None
        )
        if source_qualified_status_rows:
            status_resources = self.squad_status_resources
            if not isinstance(status_resources, OriginalSquadStatusResources):
                raise OriginalGameHostError(
                    "Squad source-qualified status renderer requires verified original status resources"
                )
            for overlay in build_first_roster_direct_status_overlays(
                source_qualified_status_rows,
                status_resources,
            ):
                self._create_native_image(
                    overlay.x,
                    overlay.y,
                    image=self._rgba_photo(overlay.width, overlay.height, overlay.rgba),
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
            self._create_native_image(
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
        self._create_native_image(
            art.x,
            art.y,
            image=image,
            anchor=self.tk.NW,
        )
        return 1

    def _draw_league_tables_row_text(self, frame) -> int:
        """Draw only the source-qualified PLeagueTableRow visible strings."""
        if frame.presentation.panel_class != "PLeagueTables":
            return 0
        snapshot = frame.presentation.league_tables
        if snapshot is None:
            raise OriginalGameHostError(
                "League Tables text renderer lost its source-backed snapshot"
            )
        resources = self.management_text_resources
        if resources is None:
            return 0
        if not isinstance(resources, OriginalManagementTextResources):
            raise OriginalGameHostError(
                "League Tables text renderer requires verified source font resources"
            )
        overlays = league_tables_row_text_overlays(snapshot, resources)
        for overlay in overlays:
            self._create_native_image(
                overlay.x,
                overlay.y,
                image=self._photo(
                    encode_rgba_png(
                        overlay.width,
                        overlay.height,
                        overlay.rgba,
                    )
                ),
                anchor=self.tk.NW,
            )
        return len(overlays)

    def _fixtures_page_controls(self):
        if (self.active_pmatchinfo_art is not None
                or self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT
                or self.management_presenter is None
                or not isinstance(self.fixtures_pager_art, OriginalFixturesPagerArt)):
            return ()
        snapshot = self.management_presenter.snapshot()
        if snapshot.panel_class != 'PLeagueFixtures' or snapshot.league_fixtures is None:
            return ()
        return fixtures_page_controls(self.management_presenter.league_fixtures_column_offset,
            len(snapshot.league_fixtures.member_club_ids), self.fixtures_pager_flags)

    def _draw_fixtures_pager(self):
        controls = self._fixtures_page_controls()
        for control in controls:
            image = self._photo(encode_rgba_png(27, 18, self.fixtures_pager_art.pixels(control)))
            self._create_native_image(*control.rect[:2], image=image, anchor=self.tk.NW)
        return len(controls)

    def on_fixtures_pager_motion(self, event):
        if getattr(self, "_startup_media_active", False):
            return
        event = self._normalize_pointer_event(event)
        self._first_screen_pointer = (int(event.x), int(event.y))
        if self.presenter.session.navigation.screen in (
                FrontEndScreen.START_MENU,
                FrontEndScreen.SETTINGS,
                FrontEndScreen.TEAM_SELECT,
        ):
            view = self.presenter.snapshot()
            self.first_screen_animation.observe(view, self._first_screen_pointer)
            self._schedule_first_screen_update(view)
            return
        if self.presenter.session.navigation.screen is FrontEndScreen.MANAGEMENT:
            x, y, width, height = HEADER_COMPOUND_RECT
            inside_header = (
                x <= int(event.x) < x + width
                and y <= int(event.y) < y + height
            )
            self.management_header_state.set_pointer_inside(inside_header)
            self.management_header_state.set_selected(self.pmenu_popup_active)
            self._schedule_management_header_update()
        changed = False
        if (self.presenter.session.navigation.screen is FrontEndScreen.MANAGEMENT
                and self.active_pmatchinfo_art is None and self.pmenu_popup_active
                and pmenu_app_pointer_dismiss(int(event.x), int(event.y))):
            self.pmenu_popup_active = False
            changed = True
        for control in self._fixtures_page_controls():
            x, y, w, h = control.rect
            old = self.fixtures_pager_flags[control.direction]
            inside = (not self.pmenu_popup_active
                      and x <= int(event.x) < x+w and y <= int(event.y) < y+h)
            new = old | 8 if inside else old & ~8
            self.fixtures_pager_flags[control.direction] = new
            changed |= old != new
        if changed:
            self.redraw()

    def on_fixtures_pager_leave(self, event):
        self.on_fixtures_pager_motion(type('Outside', (), {'x': -1, 'y': -1})())

    def _draw_pmatchinfo_dialog(self) -> int:
        """Draw the popup and source-closed ordinary summary/default pitch."""
        art = self.active_pmatchinfo_art
        if art is None:
            return 0
        if not isinstance(art, OriginalPMatchInfoPopupArt):
            raise OriginalGameHostError(
                "Active PMatchInfo state must be verified popup art"
            )
        image = self._photo(encode_rgba_png(art.width, art.height, art.rgba))
        self._create_native_image(
            art.x,
            art.y,
            image=image,
            anchor=self.tk.NW,
        )
        context = self.active_pmatchinfo_context
        if context is not None and self.pmatchinfo_snapshot is not None:
            pixels = ordinary_pmatchinfo_pitch_pixels(
                context.captured_report, self.pmatchinfo_snapshot)
            if pixels is not None:
                x, y, w, h, png = pixels
                self._create_native_image(art.x + x, art.y + y,
                    image=self._photo(png), anchor=self.tk.NW)
            if self.pmatchinfo_nested_font is not None:
                controller = self.presenter.session.gameplay
                header = (() if controller is None else ordinary_pmatchinfo_header_lines(
                    context.captured_report, controller.state.clubs))
                for line in header + ordinary_pmatchinfo_possession_lines(
                        context.captured_report, self.pmatchinfo_snapshot):
                    pixels = summary_line_pixels(line, self.pmatchinfo_nested_font)
                    if pixels is not None:
                        x, y, w, h, png = pixels
                        self._create_native_image(art.x + x, art.y + y,
                            image=self._photo(png), anchor=self.tk.NW)
        if context is not None and self.pmatchinfo_font is not None:
            controller = self.presenter.session.gameplay
            if controller is not None:
                for line in ordinary_pmatchinfo_summary_lines(
                        context.captured_report, controller.state.players):
                    pixels = summary_line_pixels(line, self.pmatchinfo_font)
                    if pixels is None:
                        continue
                    x, y, w, h, png = pixels
                    self._create_native_image(art.x + x, art.y + y,
                        image=self._photo(png), anchor=self.tk.NW)
            if (self.pmatchinfo_script_art is not None and self.pmatchinfo_snapshot is not None
                    and self.pmatchinfo_snapshot.selected_tab_event_id == 1):
                from original_pmatchinfo_script_rows import script_list_pixels, script_arrow_pixels
                for side in (1, 0):
                    offset = self.pmatchinfo_script_offsets[side]
                    layers = script_list_pixels(
                            context.captured_report, side, self.pmatchinfo_script_art,
                            self.pmatchinfo_font,
                            players=None if controller is None else controller.state.players,
                            first_row=offset)
                    layers += script_arrow_pixels(context.captured_report, side,
                            self.pmatchinfo_script_art, first_row=offset,
                            pressed_direction=(self.pmatchinfo_script_pressed[1]
                                if self.pmatchinfo_script_pressed is not None
                                and self.pmatchinfo_script_pressed[0] == side else None))
                    for x, y, w, h, png in layers:
                        self._create_native_image(art.x + x, art.y + y,
                            image=self._photo(png), anchor=self.tk.NW)
        return 1

    def _draw_management_host(self) -> None:
        if self._first_screen_idle is not None:
            self.root.after_cancel(self._first_screen_idle)
            self._first_screen_idle = None
        if self.management_presenter is None:
            with timed_stage("management.presenter.construct"):
                self.management_presenter = self.management_presenter_factory(
                    self.presenter.session
                )
        with timed_stage("management.first_snapshot"):
            frame = build_management_canvas_frame(self.management_presenter)
        family = self._management_resource_family(frame.presentation.panel_class)
        if family not in self._management_resource_families_loaded:
            self._begin_management_resource_load(family)
            return
        if self.management_pmenu_resources is None:
            raise OriginalGameHostError(
                "Management PMenu renderer requires verified original row resources"
            )

        menu_render = None
        if self.pmenu_popup_active:
            with timed_stage("management.pmenu.render"):
                menu_render = build_management_pmenu_render(
                    frame,
                    self.management_pmenu_resources,
                )
        self.canvas.delete("all")
        self._photos = []

        if self.management_background is not None:
            for image in self.management_background.images(frame.presentation.club):
                photo = self._rgba_photo(image.width, image.height, image.rgba)
                self._create_native_image(image.x, image.y, image=photo, anchor=self.tk.NW)

        header_image_count = self._draw_management_header(frame.presentation.club)
        squad_image_count = self._draw_squad_top_controls(frame)
        squad_image_count += self._draw_squad_rows(frame)
        fixture_image_count = self._draw_league_fixtures_grid_art(frame)
        fixture_image_count += self._draw_fixtures_pager()
        table_image_count = self._draw_league_tables_header_art(frame)
        table_text_count = self._draw_league_tables_row_text(frame)
        panel_image_count = (
            squad_image_count + fixture_image_count + table_image_count + table_text_count
        )

        menu_x, menu_y, _menu_w, _menu_h = frame.menu_rect
        for overlay in (menu_render.overlays if menu_render is not None else ()):
            art = self._photo(overlay.png)
            self._create_native_image(
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
        header_status = (
            f"; {header_image_count} source management-header layers rendered"
            if header_image_count
            else ""
        )
        if self.management_background is not None and header_image_count:
            shell_status = "native management base and event-2 header rendered"
        elif self.management_background is not None:
            shell_status = "native management base rendered; event-2 header unresolved"
        else:
            shell_status = "surrounding management background unresolved"
        self.last_status = (
            f"Management host active: {frame.presentation.panel_class}; "
            f"source PMenu {'rows rendered' if self.pmenu_popup_active else 'popup closed'}"
            f"{panel_status}{dialog_status}{header_status}; {shell_status}"
        )

    def redraw(self) -> None:
        if getattr(self, "_startup_media_active", False):
            return  # Keep the black source movie field above the menu.
        screen = self.presenter.session.navigation.screen
        if screen in (
            FrontEndScreen.START_MENU,
            FrontEndScreen.SETTINGS,
            FrontEndScreen.TEAM_SELECT,
        ):
            self._draw_first_screen()
            return
        if screen is FrontEndScreen.MANAGEMENT:
            self._draw_management_host()
            return
        raise OriginalGameHostError(f"Unsupported source-backed screen: {screen!r}")

    def present_completed_match_by_source_mode(self, presentation, mode):
        """Apply only the source-closed post-PPreMatch presentation dispatch.

        The caller must already own a completed-human presentation bundle and
        an accepted Match Detail mode. This method does not start, simulate,
        advance, or select a fixture and is deliberately not called from any
        management pointer/navigation path while the native entry trigger
        remains unresolved.

        Source routes 0/1 require the still-unrecovered 3D presentation
        wrapper and therefore fail closed. Mode 2 opens the existing FastView
        surface. Mode 3 is Quick Match and intentionally opens no presentation
        wrapper.
        """
        dispatch = source_match_detail_dispatch(mode)
        if dispatch.route is MatchPresentationRoute.FASTVIEW:
            return self.present_completed_match_fastview(presentation)
        if dispatch.route is MatchPresentationRoute.QUICK_MATCH:
            self.last_status = (
                "Applied source Match Detail Quick Match route; "
                "native mode 3 has no presentation wrapper"
            )
            return None
        raise OriginalGameHostError(
            "Selected Match Detail mode requires the unrecovered native 3D "
            "presentation wrapper; FastView substitution is forbidden"
        )

    def present_completed_match_fastview(self, presentation):
        """Open the existing resolved FastView bundle without inventing navigation.

        The caller must already own a completed-human presentation bundle. This
        host method creates no match state and is deliberately not called from
        on_click() or any PMenu transition until the original runtime trigger is
        source-qualified.
        """
        opened = open_human_fastview_tk_window(
            presentation,
            self.tk,
            self.root,
        )
        self.last_fastview_window = opened
        self.last_status = (
            "Opened source-bounded partial FastView presentation; "
            "source navigation trigger remains unrecovered"
        )
        return opened

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
        family = self._management_resource_family(result.presentation.panel_class)
        if family not in self._management_resource_families_loaded:
            self._begin_management_resource_load(family)
        else:
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

    def apply_source_accepted_league_fixtures_page(self, direction: int):
        """Apply one proven PLeagueFixtures column-window page after source acceptance.

        This seam intentionally accepts no pointer coordinates or Tk event.
        Ordinary mouse mapping remains fail-closed until the original page
        controls' input rectangles/event boundary are recovered.
        """
        if self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            raise OriginalGameHostError(
                "Source-accepted League Fixtures paging requires the MANAGEMENT host"
            )
        if self.management_presenter is None:
            self.management_presenter = self.management_presenter_factory(
                self.presenter.session
            )
        activation = self.management_presenter.source_accepted_league_fixtures_page(
            direction
        )
        self.redraw()
        self.last_status = (
            "Applied source-accepted League Fixtures page transition: "
            f"{activation.previous_offset} -> {activation.column_offset}; "
            + ("ordinary page-button pointer mapping remains fail-closed without verified art"
               if self.fixtures_pager_art is None
               else "ordinary page-button pointer mapping is separately source-qualified")
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
        if getattr(self, "_startup_media_active", False):
            return
        event = self._normalize_pointer_event(event)
        """WM_RBUTTONDOWN equivalent, proven at 0x531CF0..FA / 0x653600.

        Opening requires the native captured-report owner, not completion or a
        score. The complete ordinary producer publishes explicit owner/link
        state; an uncaptured fixture is still a source-compatible no-op.
        """
        if (self.presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT
                or self.active_pmatchinfo_art is not None):
            return
        if self.pmenu_popup_active:
            self.last_status = 'PMenu popup owns input; fixture report press blocked'
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
            self.pmatchinfo_script_offsets = {1: 0, 0: 0}
            self.pmatchinfo_script_pressed = None
            self.redraw()

    def on_script_arrow_release(self, event) -> None:
        if getattr(self, "_startup_media_active", False):
            return
        event = self._normalize_pointer_event(event)
        pager_changed = any(flags & 0x10 for flags in self.fixtures_pager_flags.values())
        self.fixtures_pager_flags = {direction: flags & ~0x10
                                    for direction, flags in self.fixtures_pager_flags.items()}
        if pager_changed:
            self.redraw()
        # 64F860 -> 64F470(0) clears bit4; no second scroll on release.
        if self.pmatchinfo_script_pressed is not None:
            self.pmatchinfo_script_pressed = None
            self.redraw()

    def on_click(self, event) -> None:
        if getattr(self, "_startup_media_active", False):
            return  # Startup skip/menu semantics are not inferred from input.
        event = self._normalize_pointer_event(event)
        if self.presenter.session.navigation.screen is FrontEndScreen.MANAGEMENT:
            if self._management_load_thread is not None:
                self.last_status = (
                    "Preparing source-backed management "
                    f"{self._management_loading_family or 'squad'} resources..."
                )
                return
            if not self._management_resources_loaded:
                self._begin_management_resource_load("squad")
                return
        if self.presenter.session.navigation.screen is FrontEndScreen.MANAGEMENT:
            if self.active_pmatchinfo_art is not None:
                if (self.active_pmatchinfo_context is not None
                        and self.pmatchinfo_snapshot is not None
                        and self.pmatchinfo_snapshot.selected_tab_event_id == 1):
                    from original_pmatchinfo_script_rows import script_arrow_at_point, script_scroll_step
                    art = self.active_pmatchinfo_art
                    arrow = script_arrow_at_point(int(event.x) - art.x, int(event.y) - art.y)
                    if arrow is not None:
                        if self.pmatchinfo_script_pressed == arrow:
                            self.last_status = 'PMatchInfo native script arrow rejects already-pressed control'
                            return
                        side, direction = arrow
                        old = self.pmatchinfo_script_offsets[side]
                        new = script_scroll_step(self.active_pmatchinfo_context.captured_report,
                                                 old, direction)
                        if new != old:
                            self.pmatchinfo_script_pressed = arrow
                            self.pmatchinfo_script_offsets[side] = new
                            self.redraw()
                            self.last_status = f'PMatchInfo native script list {side}: offset {new}'
                        else:
                            self.last_status = 'PMatchInfo native script arrow disabled at bound'
                        return
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
            if pmenu_open_press(int(event.x), int(event.y), active=self.pmenu_popup_active):
                self.pmenu_popup_active = True
                self.redraw()
                self.last_status += '; native application event 2: PMenu popup opened'
                return
            page = (None if self.pmenu_popup_active else fixtures_page_press(
                self._fixtures_page_controls(), int(event.x), int(event.y)))
            if page is not None:
                self.fixtures_pager_flags[page.direction] |= 0x10
                activation = self.management_presenter.source_accepted_league_fixtures_page(page.direction)
                self.redraw()
                self.last_status = f'League Fixtures native event {page.event_id}: offset {activation.column_offset}'
                return
            candidate = (candidate_pmenu_row_at_screen_point(
                frame.presentation.menu,
                int(event.x),
                int(event.y),
            ) if self.pmenu_popup_active else None)
            if candidate is None:
                self.last_pmenu_activation = None
                if self.pmenu_popup_active:
                    self.last_status = 'PMenu popup owns input; no source-bounded PMenu candidate row'
                    return
                try:
                    grid = self.management_presenter.league_fixtures_grid_pointer_press(
                        int(event.x),
                        int(event.y),
                    )
                except Exception as exc:
                    self.last_league_fixtures_grid_activation = None
                    self.last_status = f"{type(exc).__name__}: {exc}"
                    return
                if grid is not None:
                    self.last_league_fixtures_grid_activation = grid
                    self.redraw()
                    self.last_status = (
                        "League Fixtures source grid press: "
                        f"column {grid.column}, row {grid.row}, "
                        f"fixture {grid.fixture_id}"
                    )
                    return
                self.last_league_fixtures_grid_activation = None
                self.last_status = (
                    "Management host active; no source-bounded PMenu candidate row "
                    "or League Fixtures grid control at "
                    f"({int(event.x)}, {int(event.y)})"
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
                    family = self._management_resource_family(result.presentation.panel_class)
                    if family not in self._management_resource_families_loaded:
                        self._begin_management_resource_load(family)
                    else:
                        self.redraw()
                    self.last_status = (
                        "PMenu source pointer press: "
                        f"{result.action.action_kind} {candidate.menu_id:#x}"
                    )
                except Exception as exc:
                    self.last_status = f"{type(exc).__name__}: {exc}"
            return
        try:
            pointer_screen = self.presenter.session.navigation.screen
            with timed_stage(f"frontend.pointer screen={pointer_screen.value}"):
                result = self.presenter.pointer(int(event.x), int(event.y))
            if result is None:
                self.last_status = "No recovered action at this pixel"
            elif isinstance(result, OriginalHierarchyInteraction):
                self.last_status = (
                    f"{result.row_kind}:{result.source_id}:{result.text}"
                )
                if (
                    result.row_kind == "club"
                    and self._update_teamselect_club_row(result.source_id)
                ):
                    return
            elif result.transition.command is FrontEndCommand.TEAMSELECT_START_CONTINUE:
                self.last_status = "Entered recovered PMenu management host"
                if (
                    self.management_resource_loader is not None
                    and not self._management_resources_loaded
                ):
                    self._begin_management_resource_load("squad")
                    return
            elif result.transition.command is FrontEndCommand.APPLY_SETTINGS:
                self._set_fullscreen(self.presenter.session.settings.fullscreen)
                self.last_status = (
                    "Settings applied: "
                    f"profile={self.presenter.session.settings.profile_name}; "
                    f"fullscreen={'on' if self._fullscreen else 'off'}"
                )
            elif result.transition.command is FrontEndCommand.QUIT_TO_WINDOWS:
                self.last_status = "QUIT_TO_WINDOWS"
                if self._first_screen_idle is not None:
                    self.root.after_cancel(self._first_screen_idle)
                    self._first_screen_idle = None
                if self._management_header_idle is not None:
                    self.root.after_cancel(self._management_header_idle)
                    self._management_header_idle = None
                if self._management_load_poll is not None:
                    self.root.after_cancel(self._management_load_poll)
                    self._management_load_poll = None
                self.root.destroy()
                return
            elif result.transition.command is not None:
                self.last_status = result.transition.command.name
            else:
                self.last_status = result.transition.screen.name
        except Exception as exc:
            self.last_status = f"{type(exc).__name__}: {exc}"
            self.error_reporter(self.last_status)
            return
        if (
            result is not None
            and getattr(result, "transition", None) is not None
            and result.transition.command is FrontEndCommand.TEAMSELECT_START_CONTINUE
        ):
            with timed_stage("management.first_draw"):
                self.redraw()
        else:
            redraw_screen = self.presenter.session.navigation.screen
            with timed_stage(f"frontend.redraw screen={redraw_screen.value}"):
                self.redraw()


def play_configured_startup_media(
    *,
    receipt_path: str | Path | None,
    backend,
    repo_root: str | Path | None = None,
    derivatives=None,
):
    """Play either private-receipt or already-verified bundled startup media."""
    if derivatives is not None:
        if receipt_path is not None:
            raise OriginalGameHostError(
                "Startup media cannot combine bundled derivatives with a private receipt"
            )
        if backend is None:
            raise OriginalGameHostError(
                "Verified bundled startup media requires a playback backend"
            )
        return play_verified_startup_sequence(derivatives, backend)

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
    startup_media_derivatives=None,
    repo_root: str | Path | None = None,
    host_ready_callback=None,
) -> None:
    """Launch verified startup media, then the current source-backed UI surface.

    host_ready_callback is an audit-only observation seam. When supplied, it is
    called exactly once with the production host and the installed first-screen
    audio binding immediately before mainloop. Normal application launches leave
    it as None.
    """
    resolved_source_root = (
        DEFAULT_SOURCE_ROOT if source_root is None else Path(source_root)
    )
    with timed_stage("startup.presenter_build"):
        presenter = build_original_game_presenter(
            game_dir,
            source_root=resolved_source_root,
        )
    original_executable = Path(game_dir) / "FOOTBAL.EXE"
    runtime_repo_root = REPO_ROOT if repo_root is None else Path(repo_root)

    def load_management_resources(family: str):
        # Fresh MANAGEMENT must not wait for unrelated panels. Each family is
        # source-verified only when its route first needs it, then retained for
        # the rest of the session.
        if family == "squad":
            with timed_stage("management.resources.pmenu"):
                pmenu_resources = load_verified_management_pmenu_resources(
                    resolved_source_root,
                    original_executable,
                )
            with timed_stage("management.resources.squad_top"):
                squad_top_resources = load_verified_squad_top_resources(
                    resolved_source_root,
                    original_executable,
                )
            with timed_stage("management.resources.squad_rows"):
                squad_row_text_resources = load_verified_squad_row_text_resources(
                    resolved_source_root
                )
            with timed_stage("management.resources.squad_status"):
                squad_status_resources = load_verified_squad_status_resources(
                    resolved_source_root
                )
            with timed_stage("management.resources.background"):
                management_background = OriginalManagementBackground(
                    resolved_source_root,
                    original_executable,
                )
            with timed_stage("management.resources.header"):
                management_header_resources = load_verified_management_header_resources(
                    resolved_source_root,
                    original_executable,
                )
            return {
                "management_pmenu_resources": pmenu_resources,
                "squad_top_resources": squad_top_resources,
                "squad_row_text_resources": squad_row_text_resources,
                "squad_status_resources": squad_status_resources,
                "management_background": management_background,
                "management_header_resources": management_header_resources,
            }

        if family == "fixtures":
            with timed_stage("management.resources.fixture_contracts"):
                fixture_resources = validate_original_league_fixtures_resources(
                    resolved_source_root
                )
            with timed_stage("management.resources.league_fixtures_grid_art"):
                league_fixtures_grid_art = load_verified_league_fixtures_grid_art(
                    resolved_source_root,
                    original_executable,
                )
            with timed_stage("management.resources.fixtures_pager_art"):
                fixtures_pager_art = load_verified_fixtures_pager_art(
                    resolved_source_root,
                    original_executable,
                )
            # PMatchInfo is reachable only from the Fixtures route, so its
            # source family is staged with that route rather than fresh Squad.
            with timed_stage("management.resources.pmatchinfo_snapshot"):
                pmatchinfo_snapshot = load_staged_pmatchinfo_snapshot(
                    runtime_repo_root,
                    original_executable,
                    require_complete_dialog=True,
                )
            with timed_stage("management.resources.pmatchinfo_font"):
                pmatchinfo_font = validate_original_pmenu_font(resolved_source_root)
            with timed_stage("management.resources.pmatchinfo_nested_font"):
                pmatchinfo_nested_font = load_pmatchinfo_nested_font(
                    resolved_source_root
                )
            with timed_stage("management.resources.pmatchinfo_script_art"):
                pmatchinfo_script_art = load_script_row_art(
                    runtime_repo_root,
                    original_executable,
                    game_dir=game_dir,
                )
            return {
                "league_fixtures_grid_art": league_fixtures_grid_art,
                "fixtures_pager_art": fixtures_pager_art,
                "pmatchinfo_snapshot": pmatchinfo_snapshot,
                "pmatchinfo_font": pmatchinfo_font,
                "pmatchinfo_nested_font": pmatchinfo_nested_font,
                "pmatchinfo_script_art": pmatchinfo_script_art,
                "_fixture_resource_names": tuple(
                    resource.name for resource in fixture_resources
                ),
            }

        if family == "league_tables":
            with timed_stage("management.resources.league_table_contracts"):
                league_table_resources = validate_original_league_tables_resources(
                    resolved_source_root
                )
            with timed_stage("management.resources.league_tables_header"):
                league_tables_header_art = load_verified_league_tables_header_art(
                    resolved_source_root,
                    original_executable,
                )
            with timed_stage("management.resources.text"):
                management_text_resources = load_verified_management_text_resources(
                    resolved_source_root,
                )
            return {
                "league_tables_header_art": league_tables_header_art,
                "management_text_resources": management_text_resources,
                "_league_table_resource_names": tuple(
                    resource.name for resource in league_table_resources
                ),
            }

        raise OriginalGameHostError(
            f"Unsupported management resource family: {family!r}"
        )

    import tkinter as tk

    from windows_display_context import initialize_windows_display_context
    initialize_windows_display_context()

    with timed_stage("startup.tk_root"):
        root = tk.Tk()
    host = OriginalGameTkHost(
        presenter,
        root,
        tk,
        management_presenter_factory=lambda session: OriginalManagementPresenter(
            session,
            staged_league_fixture_resource_names=tuple(
                resource.name for resource in LEAGUE_FIXTURES_RESOURCES
            ),
            staged_league_table_resource_names=tuple(
                resource.name for resource in LEAGUE_TABLES_RESOURCES
            ),
        ),
        management_resource_loader=load_management_resources,
    )
    if startup_media_backend is not None:
        host._startup_native_input = getattr(startup_media_backend, 'request_native_input', None)
        host.show_startup_media_backdrop()
        try:
            bind_pump = getattr(startup_media_backend, "bind_event_pump", None)
            if callable(bind_pump):
                bind_pump(host.pump_startup_media_events)
            bind_parent = getattr(
                startup_media_backend, "bind_parent_window", None
            )
            if callable(bind_parent):
                binding = host.startup_media_child_binding()
                bind_parent(
                    binding["parent_hwnd"],
                    x=binding["x"],
                    y=binding["y"],
                    width=binding["width"],
                    height=binding["height"],
                )
            bind_geometry = getattr(startup_media_backend, "bind_presentation_geometry", None)
            if callable(bind_geometry):
                bind_geometry(host.startup_media_child_binding)
            with timed_stage("startup.media"):
                play_configured_startup_media(
                    receipt_path=startup_media_receipt,
                    backend=startup_media_backend,
                    repo_root=repo_root,
                    derivatives=startup_media_derivatives,
                )
        finally:
            host._startup_native_input = None
            host.hide_startup_media_backdrop()
    else:
        with timed_stage("startup.media"):
            play_configured_startup_media(
                receipt_path=startup_media_receipt,
                backend=None,
                repo_root=repo_root,
                derivatives=startup_media_derivatives,
            )

    audio_binding = None
    try:
        audio_binding = install_live_first_screen_audio(host, game_dir)
    except Gate14LiveFirstScreenAudioError as exc:
        print(
            f"[FM2001 audio] first-screen audio unavailable: {exc}",
            file=sys.stderr,
            flush=True,
        )
    if host_ready_callback is not None:
        if not callable(host_ready_callback):
            raise OriginalGameHostError("host_ready_callback must be callable")
        host_ready_callback(host, audio_binding)
    root.mainloop()
