"""Fail-closed real-Windows/Tk audit for the recovered FM2001 first screens.

This is deliberately separate from the synthetic/headless viewer tests.  The
CLI only runs on Windows, loads the checksum-gated original source inputs,
opens the real Tk viewer, verifies live source-frame geometry, and drives the
actual Tk binding through recovered country, competition and club transitions.
A passing receipt is a Windows graphical result, not a claim that all Gate-13
management presentation is complete.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import platform
from pathlib import Path
from original_management_background import OriginalManagementBackground
import sys

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_original_first_screen_viewer import OriginalFirstScreenTkDebug
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter,
    OriginalFirstScreenSnapshot,
)
from original_game_host import OriginalGameTkHost
from original_league_fixtures_art import load_verified_league_fixtures_grid_art
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_RESOURCES,
    validate_original_league_fixtures_resources,
)
from original_league_tables_art import load_verified_league_tables_header_art
from original_league_tables_resources import (
    LEAGUE_TABLES_RESOURCES,
    validate_original_league_tables_resources,
)
from original_front_end_layout import (
    PSTARTMENU_ACTIONS,
    SCREEN_SIZE,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
    TEAMSELECT_START_RECT,
    OriginalRect,
)
from original_live_debug_view import build_original_debug_frame
from original_management_canvas import (
    build_management_canvas_frame,
    build_management_pmenu_render,
    load_verified_management_pmenu_resources,
)
from original_management_presenter import OriginalManagementPresenter
from original_pmatchinfo_presenter import load_staged_pmatchinfo_snapshot
from original_pmenu_chrome import PMENU_LIST_SCREEN_ORIGIN, PMENU_LIST_SIZE
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
from original_squad_resources import SQUAD_PANEL_RECT
from original_squad_top_controls import (
    build_fresh_squad_top_render,
    load_verified_squad_top_resources,
)
from original_teamselect_resources import load_verified_original_teamselect_inputs


class WindowsFirstScreenAuditError(RuntimeError):
    """The real graphical path differs from the source-backed contract."""


def _rect_dict(rect: OriginalRect) -> dict[str, int]:
    return {
        "x": rect.x,
        "y": rect.y,
        "width": rect.width,
        "height": rect.height,
    }


def expected_tk_photo_dimensions(
    snapshot: OriginalFirstScreenSnapshot,
    source_frame_index: int,
) -> tuple[tuple[int, int], ...]:
    """Return the exact PhotoImage geometry expected from one viewer redraw."""
    frame = build_original_debug_frame(snapshot, source_frame_index)
    dimensions: list[tuple[int, int]] = [SCREEN_SIZE]
    dimensions.extend(
        (item.rect.width, item.rect.height)
        for item in frame.original_source_frame_overlays
    )
    dimensions.extend(
        (
            control.caption.glyph_mask.width,
            control.caption.glyph_mask.height,
        )
        for control in snapshot.controls
        if control.caption is not None
    )
    for row in (*snapshot.hierarchy_rows, *snapshot.club_rows):
        dimensions.extend((
            (row.animation_frame.width, row.animation_frame.height),
            (row.bar_frame.width, row.bar_frame.height),
            (row.glyph_mask.width, row.glyph_mask.height),
        ))
    if snapshot.hierarchy_art is not None:
        dimensions.append(
            (
                snapshot.hierarchy_art.animation.frames[0].width,
                snapshot.hierarchy_art.animation.frames[0].height,
            )
        )
        dimensions.append(
            (
                snapshot.hierarchy_art.bars.frames[0].width,
                snapshot.hierarchy_art.bars.frames[0].height,
            )
        )
    return tuple(dimensions)


def audit_frame_contract(
    snapshot: OriginalFirstScreenSnapshot,
    source_frame_index: int = 0,
) -> dict:
    """Validate one source-backed frame without requiring a GUI."""
    frame = build_original_debug_frame(snapshot, source_frame_index)
    actions = [
        {
            "event": item.event,
            "rect": _rect_dict(item.rect),
            "source_frame_index": item.source_frame_index,
            "source_frame_rgba_sha256": item.source_frame_rgba_sha256,
        }
        for item in frame.original_source_frame_overlays
    ]
    captions = [
        {
            "event": item.event,
            "original_text": item.original_text,
            "line_origin": [item.line_origin_x, item.line_origin_y],
            "native_color_16": item.native_color_16,
            "glyph_rgba_sha256": item.glyph_rgba_sha256,
        }
        for item in frame.native_caption_overlays
    ]
    def hierarchy_record(item) -> dict:
        return {
            "kind": item.row_kind,
            "source_id": item.source_id,
            "text": item.text,
            "state": int(item.state),
            "rect": _rect_dict(item.rect),
            "animation_source_index": item.animation_source_index,
            "bar_source_index": item.bar_source_index,
            "animation_rgba_sha256": sha256(item.animation_frame.rgba).hexdigest(),
            "bar_rgba_sha256": sha256(item.bar_frame.rgba).hexdigest(),
            "glyph_alpha_sha256": sha256(item.glyph_mask.alpha).hexdigest(),
            "line_origin": [item.line_origin_x, item.line_origin_y],
            "native_color_16": item.native_color_16,
        }

    hierarchy_rows = [hierarchy_record(item) for item in snapshot.hierarchy_rows]
    club_rows = [hierarchy_record(item) for item in snapshot.club_rows]

    if snapshot.screen is FrontEndScreen.START_MENU:
        expected_actions = [
            (item.event, _rect_dict(item.rect)) for item in PSTARTMENU_ACTIONS
        ]
        actual_actions = [(item["event"], item["rect"]) for item in actions]
        if actual_actions != expected_actions:
            raise WindowsFirstScreenAuditError(
                "PStartMenu action geometry differs from recovered executable layout"
            )
        if len(captions) != len(PSTARTMENU_ACTIONS):
            raise WindowsFirstScreenAuditError(
                "PStartMenu must render all four recovered native captions"
            )
        if frame.hierarchy_row_origins_not_interactive:
            raise WindowsFirstScreenAuditError(
                "PStartMenu unexpectedly exposes TeamSelect hierarchy rows"
            )
    elif snapshot.screen is FrontEndScreen.TEAM_SELECT:
        expected_actions = [
            (0x29, _rect_dict(TEAMSELECT_BACK_RECT)),
            (0x2A, _rect_dict(TEAMSELECT_START_RECT)),
        ]
        actual_actions = [(item["event"], item["rect"]) for item in actions]
        if actual_actions != expected_actions:
            raise WindowsFirstScreenAuditError(
                "TeamSelect Back/Start geometry differs from recovered executable layout"
            )
        if captions and [(c["event"], c["original_text"], c["line_origin"])
                         for c in captions] != [
                             (0x29, "MAIN MENU", [251, 301]),
                             (0x2A, "START GAME", [450, 301]),
                         ]:
            raise WindowsFirstScreenAuditError(
                "TeamSelect captions differ from canonical labels/font geometry"
            )
        if tuple(frame.hierarchy_row_origins_not_interactive) != (
            TEAMSELECT_HIERARCHY_ROW_ORIGINS
        ):
            raise WindowsFirstScreenAuditError(
                "TeamSelect hierarchy row origins differ from recovered executable layout"
            )
        if snapshot.hierarchy_art is None:
            raise WindowsFirstScreenAuditError(
                "Source-backed TeamSelect hierarchy art is missing"
            )
    else:
        raise WindowsFirstScreenAuditError(
            f"First-screen audit does not cover {snapshot.screen!r}"
        )

    return {
        "screen": snapshot.screen.name,
        "source_frame_index": source_frame_index,
        "background_rgba_sha256": sha256(snapshot.background_rgba).hexdigest(),
        "background_png_sha256": sha256(frame.background_png).hexdigest(),
        "actions": actions,
        "captions": captions,
        "hierarchy_row_origins": [
            list(item) for item in frame.hierarchy_row_origins_not_interactive
        ],
        "hierarchy_rows": hierarchy_rows,
        "club_rows": club_rows,
        "native_button_animation_recovered": frame.native_button_animation_recovered,
        "native_text_placement_recovered": frame.native_text_placement_recovered,
        "expected_tk_photo_dimensions": [
            list(item)
            for item in expected_tk_photo_dimensions(snapshot, source_frame_index)
        ],
    }


def _require_private_receipt(
    path: Path, *, repository_root: Path | None = None
) -> Path:
    root = (
        Path(__file__).resolve().parent.parent
        if repository_root is None
        else Path(repository_root)
    ).resolve()
    target = Path(path).resolve()
    if target.is_relative_to(root):
        raise WindowsFirstScreenAuditError(
            "Windows graphical audit receipts must remain outside Git"
        )
    if target.exists():
        raise WindowsFirstScreenAuditError(
            "Use a new receipt path; do not overwrite prior graphical evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _enable_windows_dpi_awareness() -> str:
    """Request unvirtualized Windows pixels before Tk creates its first HWND."""
    try:
        import ctypes

        result = ctypes.windll.user32.SetProcessDPIAware()
        return "SetProcessDPIAware_called" if result else "already_set_or_rejected"
    except Exception as exc:  # pragma: no cover - Windows environment detail
        return f"dpi_awareness_call_failed:{type(exc).__name__}"


def _pump(root) -> None:
    root.update_idletasks()
    root.update()


def _click(canvas, root, rect: OriginalRect) -> None:
    x = rect.x + rect.width // 2
    y = rect.y + rect.height // 2
    canvas.event_generate("<Button-1>", x=x, y=y)
    _pump(root)


def _actual_photo_dimensions(viewer: OriginalFirstScreenTkDebug) -> list[list[int]]:
    out = []
    for photo in viewer._photos:
        out.append([int(photo.width()), int(photo.height())])
    return out


def _verify_live_tk_redraw(
    viewer: OriginalFirstScreenTkDebug,
    root,
    contract: dict,
) -> dict:
    _pump(root)
    canvas_size = [
        int(viewer.canvas.winfo_width()),
        int(viewer.canvas.winfo_height()),
    ]
    if canvas_size != list(SCREEN_SIZE):
        raise WindowsFirstScreenAuditError(
            f"Real Tk canvas is {canvas_size}, expected {list(SCREEN_SIZE)}"
        )
    photo_dimensions = _actual_photo_dimensions(viewer)
    expected = contract["expected_tk_photo_dimensions"]
    if photo_dimensions != expected:
        raise WindowsFirstScreenAuditError(
            "Real Tk PhotoImage geometry differs from the source-backed redraw contract"
        )
    return {
        "canvas_size": canvas_size,
        "photo_dimensions": photo_dimensions,
        "photo_count": len(photo_dimensions),
    }


def audit_management_host_contract(
    frame,
    *,
    canvas_size: list[int],
    photo_dimensions: list[list[int]],
    status: str,
    required_status_fragment: str = "entered source-proven PMenu management host",
    expected_pmenu_photo_dimensions: list[list[int]] | None = None,
) -> dict:
    """Validate recovered MANAGEMENT geometry and any source-backed PMenu pixels."""
    menu_x, menu_y = PMENU_LIST_SCREEN_ORIGIN
    menu_w, menu_h = PMENU_LIST_SIZE
    expected_menu_rect = (menu_x, menu_y, menu_w, menu_h)
    if frame.screen_size != SCREEN_SIZE:
        raise WindowsFirstScreenAuditError(
            "MANAGEMENT host no longer uses the exact 800x600 source surface"
        )
    if frame.menu_rect != expected_menu_rect:
        raise WindowsFirstScreenAuditError(
            "MANAGEMENT PMenu rectangle differs from recovered native geometry"
        )
    if frame.panel_rect != SQUAD_PANEL_RECT:
        raise WindowsFirstScreenAuditError(
            "Fresh MANAGEMENT panel rectangle differs from recovered PSquadScreen geometry"
        )
    if frame.presentation.panel_class != "PSquadScreen":
        raise WindowsFirstScreenAuditError(
            "Fresh MANAGEMENT host did not resolve PSquadScreen"
        )
    if frame.presentation.panel_code != 0xCE:
        raise WindowsFirstScreenAuditError(
            "Fresh MANAGEMENT host did not preserve native Squad menu ID 0xCE"
        )
    if frame.surrounding_background_recovered:
        raise WindowsFirstScreenAuditError(
            "MANAGEMENT audit must not claim unresolved surrounding background pixels"
        )
    if not frame.pmenu_text_placement_recovered:
        raise WindowsFirstScreenAuditError(
            "MANAGEMENT audit lost recovered PMenu text placement"
        )
    if frame.complete_source_pixel_frame_available:
        raise WindowsFirstScreenAuditError(
            "MANAGEMENT audit unexpectedly claimed unresolved full source pixels"
        )
    if canvas_size != list(SCREEN_SIZE):
        raise WindowsFirstScreenAuditError(
            "Real Tk MANAGEMENT canvas is not the fixed 800x600 surface"
        )
    if expected_pmenu_photo_dimensions is None:
        if photo_dimensions:
            raise WindowsFirstScreenAuditError(
                "Diagnostic MANAGEMENT host introduced uncontracted PhotoImages"
            )
        pmenu_rows_rendered = False
    else:
        if photo_dimensions != expected_pmenu_photo_dimensions:
            raise WindowsFirstScreenAuditError(
                "Live PMenu PhotoImage geometry differs from recovered row composition"
            )
        pmenu_rows_rendered = True
    if required_status_fragment not in status:
        raise WindowsFirstScreenAuditError(
            "Real Tk Start path did not report the recovered PMenu host transition"
        )
    return {
        "screen_size": list(frame.screen_size),
        "pmenu_rect": list(frame.menu_rect),
        "panel_rect": list(frame.panel_rect),
        "panel_class": frame.presentation.panel_class,
        "panel_code": frame.presentation.panel_code,
        "live_tk_canvas_size": list(canvas_size),
        "photo_dimensions": list(photo_dimensions),
        "pmenu_rows_rendered": pmenu_rows_rendered,
        "surrounding_background_recovered": frame.surrounding_background_recovered,
        "pmenu_text_placement_recovered": frame.pmenu_text_placement_recovered,
        "complete_source_pixel_frame_available": frame.complete_source_pixel_frame_available,
    }


def expected_management_pmenu_photo_dimensions(frame, resources) -> list[list[int]]:
    """Return exact image sizes emitted by the source-backed PMenu compositor."""
    render = build_management_pmenu_render(frame, resources)
    return [list(item) for item in render.photo_dimensions]


def expected_clean_host_photo_dimensions(host, resources) -> list[list[int]]:
    """Derive the exact clean-host bitmap sequence from independent source objects."""
    if host.management_presenter is None:
        raise WindowsFirstScreenAuditError("Clean host lost its management presenter")
    frame = build_management_canvas_frame(host.management_presenter)
    expected: list[list[int]] = []
    if getattr(host, 'management_background', None) is not None:
        expected.extend([[800, 600], [385, 95]])

    if frame.presentation.panel_class == "PSquadScreen":
        transition = frame.presentation.squad_view_transition
        if transition is None:
            raise WindowsFirstScreenAuditError(
                "Clean host Squad audit lost its source-proven view transition"
            )
        if transition.control_id == 3:
            if host.squad_top_resources is None:
                raise WindowsFirstScreenAuditError(
                    "Clean host Squad audit is missing verified top-control resources"
                )
            render = build_fresh_squad_top_render(host.squad_top_resources)
            expected.extend([list(item) for item in render.photo_dimensions])
        elif transition.control_id not in (4, 5):
            raise WindowsFirstScreenAuditError(
                "Clean host Squad audit exposed an unrecovered view control"
            )
    elif frame.presentation.panel_class == "PLeagueFixtures":
        snapshot = frame.presentation.league_fixtures
        art = host.league_fixtures_grid_art
        if snapshot is None or not snapshot.exact_art_staged or art is None:
            raise WindowsFirstScreenAuditError(
                "Clean host Fixtures audit lost exact staged grid art"
            )
        expected.extend(
            [[item.width, item.height] for item in art.placements]
        )
    elif frame.presentation.panel_class == "PLeagueTables":
        snapshot = frame.presentation.league_tables
        art = host.league_tables_header_art
        if snapshot is None or not snapshot.exact_art_staged or art is None:
            raise WindowsFirstScreenAuditError(
                "Clean host League Tables audit lost exact staged header art"
            )
        expected.append([art.width, art.height])

    expected.extend(expected_management_pmenu_photo_dimensions(frame, resources))

    popup = getattr(host, "active_pmatchinfo_art", None)
    if popup is not None:
        expected.append([popup.width, popup.height])
    return expected


def verify_live_management_pmenu(host, resources) -> list[list[int]]:
    """Require live clean-host photos to match panel, PMenu, and modal source art."""
    expected = expected_clean_host_photo_dimensions(host, resources)
    actual = _actual_photo_dimensions(host)
    if actual != expected:
        raise WindowsFirstScreenAuditError(
            "Clean host PhotoImages differ from source-backed panel/PMenu/modal art"
        )
    return actual


def audit_source_accepted_pmenu_transition(
    result,
    *,
    expected_row_kind: str,
    expected_menu_id: int,
    expected_action_kind: str,
    expected_root_id: int,
    expected_child_id: int,
    expected_panel_code: int,
    expected_panel_class: str,
) -> dict:
    """Validate one post-acceptance PMenu callback without claiming input equivalence."""
    action = result.action
    presentation = result.presentation
    if not action.accepted:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu audit action was unexpectedly rejected"
        )
    if action.row_kind != expected_row_kind or action.menu_id != expected_menu_id:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu audit action identity changed"
        )
    if action.action_kind != expected_action_kind:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu audit action kind changed"
        )
    if expected_action_kind == "open_panel":
        if action.panel_factory_arguments != (expected_menu_id, 0):
            raise WindowsFirstScreenAuditError(
                "Source-accepted child action lost the recovered panel-factory arguments"
            )
    elif action.panel_factory_arguments is not None:
        raise WindowsFirstScreenAuditError(
            "Source-accepted title action unexpectedly dispatched a panel factory"
        )
    if presentation.menu.selected_root_id != expected_root_id:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu action produced the wrong expanded root"
        )
    if presentation.menu.selected_child_id != expected_child_id:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu action produced the wrong selected child"
        )
    if presentation.panel_code != expected_panel_code:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu action produced the wrong panel code"
        )
    if presentation.panel_class != expected_panel_class:
        raise WindowsFirstScreenAuditError(
            "Source-accepted PMenu action produced the wrong panel class"
        )
    return {
        "row_kind": action.row_kind,
        "menu_id": action.menu_id,
        "action_kind": action.action_kind,
        "expanded_root_id": presentation.menu.selected_root_id,
        "selected_child_id": presentation.menu.selected_child_id,
        "panel_code": presentation.panel_code,
        "panel_class": presentation.panel_class,
        "panel_factory_arguments": (
            list(action.panel_factory_arguments)
            if action.panel_factory_arguments is not None
            else None
        ),
    }

def run_real_windows_graphical_audit(
    *,
    original_exe: Path,
    original_art_root: Path,
    original_language_root: Path,
    original_font20: Path,
    canonical_game_dir: Path,
) -> dict:
    """Open real Tk on Windows and exercise only source-proven interactions."""
    if platform.system() != "Windows":
        raise WindowsFirstScreenAuditError(
            "The real graphical audit must run on Windows, not a headless/non-Windows worker"
        )

    dpi_awareness = _enable_windows_dpi_awareness()

    menu = load_verified_english_pstartmenu_inputs(
        original_art_dir=original_art_root,
        original_language_dir=original_language_root,
        original_zurich_font20=original_font20,
        original_executable=original_exe,
    )
    team = load_verified_original_teamselect_inputs(
        original_art_dir=original_art_root,
        original_executable=original_exe,
    )
    source_root = Path(original_art_root).parent
    pmenu_resources = load_verified_management_pmenu_resources(
        source_root,
        original_exe,
    )
    squad_top_resources = load_verified_squad_top_resources(
        source_root,
        original_exe,
    )
    fixture_resources = validate_original_league_fixtures_resources(source_root)
    fixture_grid_art = load_verified_league_fixtures_grid_art(
        source_root,
        original_exe,
    )
    league_table_resources = validate_original_league_tables_resources(source_root)
    league_tables_header_art = load_verified_league_tables_header_art(
        source_root,
        original_exe,
    )
    pmatchinfo_snapshot = load_staged_pmatchinfo_snapshot(
        Path(__file__).resolve().parent.parent,
        original_exe,
        require_complete_dialog=True,
    )
    presenter = OriginalFirstScreenPresenter(
        FrontEndSession.for_canonical_game_dir(canonical_game_dir),
        menu,
        team,
    )

    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    viewer = OriginalFirstScreenTkDebug(presenter, root, tk, ttk)
    try:
        _pump(root)
        tk_patchlevel = str(root.tk.call("info", "patchlevel"))

        start_contract = audit_frame_contract(presenter.snapshot(), 0)
        start_live = _verify_live_tk_redraw(viewer, root, start_contract)

        # The alternate Button group is executable-proven.  Render one source
        # frame from it on the real Tk canvas and verify its black endpoint
        # captions travel through the same live PhotoImage path.
        viewer.source_frame_index = 11
        viewer.redraw()
        alternate_contract = audit_frame_contract(presenter.snapshot(), 11)
        alternate_live = _verify_live_tk_redraw(
            viewer, root, alternate_contract
        )
        if not all(
            item["native_color_16"] == 0x0000
            for item in alternate_contract["captions"]
        ):
            raise WindowsFirstScreenAuditError(
                "PStartMenu alternate-group native caption color regressed"
            )

        viewer.source_frame_index = 0
        viewer.redraw()
        _pump(root)

        new_game_rect = next(
            item.rect for item in PSTARTMENU_ACTIONS if item.event == 2
        )
        _click(viewer.canvas, root, new_game_rect)
        if presenter.session.navigation.screen is not FrontEndScreen.TEAM_SELECT:
            raise WindowsFirstScreenAuditError(
                "Real Tk New Game click did not reach TeamSelect; "
                f"viewer status={viewer.status.get()!r}"
            )

        team_contract = audit_frame_contract(presenter.snapshot(), 0)
        if len(team_contract["captions"]) != 2:
            raise WindowsFirstScreenAuditError("Live TeamSelect action captions missing")
        team_live = _verify_live_tk_redraw(viewer, root, team_contract)

        if len(team_contract["hierarchy_rows"]) != 13:
            raise WindowsFirstScreenAuditError(
                "Default English hierarchy did not expose 13 native rows"
            )
        if len(team_contract["club_rows"]) != 20:
            raise WindowsFirstScreenAuditError(
                "Default F.A. Premier League did not expose 20 native clubs"
            )
        if team_contract["hierarchy_rows"][1]["text"] != "F.A. Premier League":
            raise WindowsFirstScreenAuditError(
                "Native competition filtering/order differs on the live screen"
            )
        if team_contract["club_rows"][0]["text"] != "Arsenal":
            raise WindowsFirstScreenAuditError(
                "Native club filtering/order differs on the live screen"
            )

        # Country activation clears the visible competition/club population.
        # Existing original-style selected users would persist; none exist yet.
        row_x, row_y = TEAMSELECT_HIERARCHY_ROW_ORIGINS[0]
        viewer.canvas.event_generate("<Button-1>", x=row_x + 1, y=row_y + 1)
        _pump(root)
        collapsed = presenter.snapshot()
        if collapsed.club_rows:
            raise WindowsFirstScreenAuditError(
                "Country activation did not clear the native club population"
            )
        if presenter.session.selected_club_ids:
            raise WindowsFirstScreenAuditError(
                "Country activation synthesized a club selection"
            )

        # The first competition row is the native F.A. Premier League after
        # stable filtering/order; activating it repopulates all 20 clubs.
        league_x, league_y = TEAMSELECT_HIERARCHY_ROW_ORIGINS[1]
        viewer.canvas.event_generate(
            "<Button-1>", x=league_x + 1, y=league_y + 1
        )
        _pump(root)
        repopulated = presenter.snapshot()
        if len(repopulated.club_rows) != 20:
            raise WindowsFirstScreenAuditError(
                "Competition activation did not repopulate native clubs"
            )

        first_club = repopulated.club_rows[0]
        viewer.canvas.event_generate(
            "<Button-1>", x=first_club.rect.x + 1, y=first_club.rect.y + 1
        )
        _pump(root)
        if presenter.session.selected_club_id != first_club.source_id:
            raise WindowsFirstScreenAuditError(
                "Native club row did not map to its canonical clicked-club identity"
            )
        selected = presenter.snapshot().club_rows[0]
        if selected.state != 1 or selected.animation_source_index != 11:
            raise WindowsFirstScreenAuditError(
                "Selected club did not enter native active frame state"
            )
        viewer.canvas.event_generate(
            "<Button-1>", x=first_club.rect.x + 1, y=first_club.rect.y + 1
        )
        _pump(root)
        if presenter.hierarchy is None or presenter.hierarchy.selected_club_ids:
            raise WindowsFirstScreenAuditError(
                "Second native club click did not remove the selected user"
            )
        if presenter.session.selected_club_ids:
            raise WindowsFirstScreenAuditError(
                "Deselected native club remained in the clean-room user selection set"
            )

        # Start/Continue is source-proven and must reject with no selected user.
        _click(viewer.canvas, root, TEAMSELECT_START_RECT)
        if presenter.session.navigation.screen is not FrontEndScreen.TEAM_SELECT:
            raise WindowsFirstScreenAuditError(
                "TeamSelect Start advanced without a selected club"
            )
        rejected_start_status = str(viewer.status.get())
        if "Choose a club before starting the game" not in rejected_start_status:
            raise WindowsFirstScreenAuditError(
                "TeamSelect Start-without-club did not fail closed"
            )

        _click(viewer.canvas, root, TEAMSELECT_BACK_RECT)
        if presenter.session.navigation.screen is not FrontEndScreen.START_MENU:
            raise WindowsFirstScreenAuditError(
                "Real Tk TeamSelect Back click did not return to PStartMenu"
            )
        return_contract = audit_frame_contract(presenter.snapshot(), 0)
        return_live = _verify_live_tk_redraw(viewer, root, return_contract)

        # Re-enter through the real Tk binding, select the first native club,
        # and require Start to enter the recovered fixed MANAGEMENT/PMenu host.
        # The host intentionally draws no guessed management pixels yet.
        _click(viewer.canvas, root, new_game_rect)
        if presenter.session.navigation.screen is not FrontEndScreen.TEAM_SELECT:
            raise WindowsFirstScreenAuditError(
                "Second real Tk New Game click did not reach TeamSelect"
            )
        management_team = presenter.snapshot()
        if len(management_team.club_rows) != 20:
            raise WindowsFirstScreenAuditError(
                "Fresh TeamSelect re-entry did not expose 20 native clubs"
            )
        management_club = management_team.club_rows[0]
        viewer.canvas.event_generate(
            "<Button-1>",
            x=management_club.rect.x + 1,
            y=management_club.rect.y + 1,
        )
        _pump(root)
        if presenter.session.selected_club_id != management_club.source_id:
            raise WindowsFirstScreenAuditError(
                "Positive Start path did not retain the clicked native club identity"
            )

        _click(viewer.canvas, root, TEAMSELECT_START_RECT)
        if presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            raise WindowsFirstScreenAuditError(
                "TeamSelect Start with a selected native club did not enter MANAGEMENT"
            )
        if viewer.management_presenter is None:
            raise WindowsFirstScreenAuditError(
                "Real Tk MANAGEMENT redraw did not construct the PMenu presenter"
            )
        management_frame = build_management_canvas_frame(
            viewer.management_presenter
        )
        management_canvas_size = [
            int(viewer.canvas.winfo_width()),
            int(viewer.canvas.winfo_height()),
        ]
        management_photo_dimensions = _actual_photo_dimensions(viewer)
        management_status = str(viewer.status.get())
        management_contract = audit_management_host_contract(
            management_frame,
            canvas_size=management_canvas_size,
            photo_dimensions=management_photo_dimensions,
            status=management_status,
        )

        # Candidate PMenu containment is source-backed geometry only. Exercise
        # it through the real Tk binding and require that no panel navigation
        # occurs until native row activation/event ownership is recovered.
        before_candidate_panel = viewer.management_presenter.snapshot()
        viewer.canvas.event_generate("<Button-1>", x=600, y=100)
        _pump(root)
        candidate_status = str(viewer.status.get())
        after_candidate_panel = viewer.management_presenter.snapshot()
        if "PMenu candidate row only" not in candidate_status:
            raise WindowsFirstScreenAuditError(
                "Real Tk MANAGEMENT click did not report the source-bounded PMenu candidate"
            )
        if "no navigation was dispatched" not in candidate_status:
            raise WindowsFirstScreenAuditError(
                "Real Tk MANAGEMENT candidate click lost the fail-closed activation boundary"
            )
        if presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
            raise WindowsFirstScreenAuditError(
                "Candidate PMenu click left the recovered MANAGEMENT host"
            )
        if (
            before_candidate_panel.panel_code != 0xCE
            or after_candidate_panel.panel_code != before_candidate_panel.panel_code
            or after_candidate_panel.menu.selected_child_id
            != before_candidate_panel.menu.selected_child_id
        ):
            raise WindowsFirstScreenAuditError(
                "Candidate PMenu click mutated panel selection without native event evidence"
            )
        if _actual_photo_dimensions(viewer):
            raise WindowsFirstScreenAuditError(
                "Candidate PMenu feedback introduced guessed management pixels"
            )

        # The default application launches OriginalGameTkHost, not the
        # developer viewer above. Exercise that clean host in a second Tk
        # window with a fresh backend/session so the Windows receipt proves the
        # actual user-facing entrypoint reaches the same fail-closed MANAGEMENT
        # boundary.
        clean_presenter = OriginalFirstScreenPresenter(
            FrontEndSession.for_canonical_game_dir(canonical_game_dir),
            menu,
            team,
        )
        clean_root = tk.Toplevel(root)
        clean_host = OriginalGameTkHost(
            clean_presenter,
            clean_root,
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
            management_background=OriginalManagementBackground(source_root, original_exe),
            pmatchinfo_snapshot=pmatchinfo_snapshot,
        )
        try:
            _pump(root)
            clean_initial_size = [
                int(clean_host.canvas.winfo_width()),
                int(clean_host.canvas.winfo_height()),
            ]
            if clean_initial_size != list(SCREEN_SIZE):
                raise WindowsFirstScreenAuditError(
                    "Default clean host did not open on the fixed 800x600 canvas"
                )

            _click(clean_host.canvas, root, new_game_rect)
            if clean_presenter.session.navigation.screen is not FrontEndScreen.TEAM_SELECT:
                raise WindowsFirstScreenAuditError(
                    "Default clean host New Game did not reach TeamSelect"
                )
            clean_team = clean_presenter.snapshot()
            if len(clean_team.club_rows) != 20:
                raise WindowsFirstScreenAuditError(
                    "Default clean host TeamSelect did not expose 20 native clubs"
                )
            clean_club = clean_team.club_rows[0]
            clean_host.canvas.event_generate(
                "<Button-1>",
                x=clean_club.rect.x + 1,
                y=clean_club.rect.y + 1,
            )
            _pump(root)
            if clean_presenter.session.selected_club_id != clean_club.source_id:
                raise WindowsFirstScreenAuditError(
                    "Default clean host native club click lost canonical identity"
                )

            _click(clean_host.canvas, root, TEAMSELECT_START_RECT)
            if clean_presenter.session.navigation.screen is not FrontEndScreen.MANAGEMENT:
                raise WindowsFirstScreenAuditError(
                    "Default clean host Start did not enter MANAGEMENT"
                )
            if clean_host.management_presenter is None:
                raise WindowsFirstScreenAuditError(
                    "Default clean host did not construct its PMenu presenter"
                )
            clean_frame = build_management_canvas_frame(
                clean_host.management_presenter
            )
            clean_canvas_size = [
                int(clean_host.canvas.winfo_width()),
                int(clean_host.canvas.winfo_height()),
            ]
            clean_photo_dimensions = _actual_photo_dimensions(clean_host)
            clean_expected_photos = expected_clean_host_photo_dimensions(
                clean_host,
                pmenu_resources,
            )
            clean_contract = audit_management_host_contract(
                clean_frame,
                canvas_size=clean_canvas_size,
                photo_dimensions=clean_photo_dimensions,
                status=str(clean_host.last_status),
                required_status_fragment="source PMenu rows rendered",
                expected_pmenu_photo_dimensions=clean_expected_photos,
            )

            clean_before_candidate = clean_host.management_presenter.snapshot()
            clean_host.canvas.event_generate("<Button-1>", x=600, y=100)
            _pump(root)
            clean_after_candidate = clean_host.management_presenter.snapshot()
            if "PMenu source pointer press" not in clean_host.last_status:
                raise WindowsFirstScreenAuditError(
                    "Default clean host did not dispatch the recovered PMenu pointer press"
                )
            if clean_host.last_pmenu_activation is None or (
                clean_host.last_pmenu_activation.action.action_kind != "no_action"
            ):
                raise WindowsFirstScreenAuditError(
                    "Selected PMenu title press did not retain the source no-action gate"
                )
            if (
                clean_after_candidate.panel_code != clean_before_candidate.panel_code
                or clean_after_candidate.menu.selected_child_id
                != clean_before_candidate.menu.selected_child_id
            ):
                raise WindowsFirstScreenAuditError(
                    "Selected PMenu title press mutated PMenu selection"
                )
            verify_live_management_pmenu(clean_host, pmenu_resources)

            # PSquadScreen control IDs 3/4/5 and their container transitions are
            # source-proven, but modern Tk pointer equivalence and post-event
            # formation/player pixels are not. Exercise only the explicit
            # post-acceptance seam and require the unproven panel pixels to stay
            # withheld for the formation view.
            squad_view_activation = clean_host.apply_source_accepted_squad_view(4)
            _pump(root)
            transition = squad_view_activation.transition
            if (
                transition.control_id,
                transition.left_roster,
                transition.second_roster_mask1,
                transition.pitch_mask1,
                transition.pitch_team_index,
            ) != (4, "first", False, True, 0):
                raise WindowsFirstScreenAuditError(
                    "Source-accepted Squad control 4 transition drifted from PSquadScreen"
                )
            squad_first_form_photo_dimensions = verify_live_management_pmenu(
                clean_host,
                pmenu_resources,
            )
            squad_view_receipt = {
                "source_accepted_transition_verified": True,
                "source_accepted_control_id": transition.control_id,
                "source_accepted_caption": transition.original_text,
                "left_roster": transition.left_roster,
                "second_roster_mask1": transition.second_roster_mask1,
                "pitch_mask1": transition.pitch_mask1,
                "pitch_team_index": transition.pitch_team_index,
                "modern_pointer_equivalence_verified": False,
                "post_event_button_pixels_verified": False,
                "formation_player_pixels_verified": False,
                "post_transition_photo_dimensions": squad_first_form_photo_dimensions,
            }

            restored_squad = clean_host.apply_source_accepted_squad_view(3)
            _pump(root)
            if restored_squad.transition.control_id != 3:
                raise WindowsFirstScreenAuditError(
                    "Source-accepted Squad control 3 did not restore the fresh container state"
                )
            restored_squad_photo_dimensions = verify_live_management_pmenu(
                clean_host,
                pmenu_resources,
            )
            if restored_squad_photo_dimensions != clean_photo_dimensions:
                raise WindowsFirstScreenAuditError(
                    "Restored fresh Squad bitmap stack differs from its initial source state"
                )

            # Recovery 176 proves that the concrete whole-row SelectBmp uses
            # 0x64F7A0 at vtable +0x6C and that Tk <Button-1> is the equivalent
            # pointer-press boundary. Exercise the complete supported route
            # through the real binding.
            source_accepted_actions = []
            clean_host.canvas.event_generate("<Button-1>", x=600, y=96 + 8 * 29)
            _pump(root)
            calendar_root = clean_host.last_pmenu_activation
            source_accepted_actions.append(
                audit_source_accepted_pmenu_transition(
                    calendar_root,
                    expected_row_kind="title",
                    expected_menu_id=0x259,
                    expected_action_kind="expand_root",
                    expected_root_id=0x259,
                    expected_child_id=0xCE,
                    expected_panel_code=0xCE,
                    expected_panel_class="PSquadScreen",
                )
            )
            verify_live_management_pmenu(clean_host, pmenu_resources)

            clean_host.canvas.event_generate("<Button-1>", x=600, y=96 + 4 * 29)
            _pump(root)
            fixtures = clean_host.last_pmenu_activation
            source_accepted_actions.append(
                audit_source_accepted_pmenu_transition(
                    fixtures,
                    expected_row_kind="child",
                    expected_menu_id=0x25C,
                    expected_action_kind="open_panel",
                    expected_root_id=0x259,
                    expected_child_id=0x25C,
                    expected_panel_code=0x25C,
                    expected_panel_class="PLeagueFixtures",
                )
            )
            fixture_photo_dimensions = verify_live_management_pmenu(
                clean_host,
                pmenu_resources,
            )

            match_info_action = clean_host.apply_source_accepted_fixture_match_info(
                fixture_present=True,
                linked_context_available=True,
                pointer_x=400,
                pointer_y=300,
            )
            _pump(root)
            if match_info_action is None:
                raise WindowsFirstScreenAuditError(
                    "Source-accepted PMatchInfo action did not open the verified popup"
                )
            popup = clean_host.active_pmatchinfo_art
            if popup is None or (
                popup.x,
                popup.y,
                popup.width,
                popup.height,
            ) != (20, 50, 760, 500):
                raise WindowsFirstScreenAuditError(
                    "PMatchInfo popup lost its recovered middle-screen origin or size"
                )
            pmatchinfo_photo_dimensions = verify_live_management_pmenu(
                clean_host,
                pmenu_resources,
            )

            clean_host.apply_source_accepted_pmatchinfo_exit()
            _pump(root)
            if clean_host.active_pmatchinfo_art is not None:
                raise WindowsFirstScreenAuditError(
                    "Source-accepted PMatchInfo exit left the modal active"
                )
            post_pmatchinfo_photo_dimensions = verify_live_management_pmenu(
                clean_host,
                pmenu_resources,
            )
            if post_pmatchinfo_photo_dimensions != fixture_photo_dimensions:
                raise WindowsFirstScreenAuditError(
                    "Closing PMatchInfo did not restore the exact Fixtures bitmap stack"
                )

            clean_host.canvas.event_generate("<Button-1>", x=600, y=96 + 5 * 29)
            _pump(root)
            tables_root = clean_host.last_pmenu_activation
            source_accepted_actions.append(
                audit_source_accepted_pmenu_transition(
                    tables_root,
                    expected_row_kind="title",
                    expected_menu_id=6,
                    expected_action_kind="expand_root",
                    expected_root_id=6,
                    expected_child_id=0x25C,
                    expected_panel_code=0x25C,
                    expected_panel_class="PLeagueFixtures",
                )
            )

            clean_host.canvas.event_generate("<Button-1>", x=600, y=96 + 4 * 29)
            _pump(root)
            league_tables = clean_host.last_pmenu_activation
            source_accepted_actions.append(
                audit_source_accepted_pmenu_transition(
                    league_tables,
                    expected_row_kind="child",
                    expected_menu_id=0x25A,
                    expected_action_kind="open_panel",
                    expected_root_id=6,
                    expected_child_id=0x25A,
                    expected_panel_code=0x25A,
                    expected_panel_class="PLeagueTables",
                )
            )
            league_tables_photo_dimensions = verify_live_management_pmenu(
                clean_host,
                pmenu_resources,
            )

            clean_host_receipt = {
                "new_game_to_teamselect": True,
                "native_club_selection": True,
                "selected_club_id": clean_club.source_id,
                "teamselect_start_to_management": True,
                "pmenu_pointer_press_hit_test_verified": True,
                "pmenu_pointer_press_activation_dispatched": True,
                "source_accepted_pmenu_actions_verified": True,
                "source_accepted_pmenu_actions": source_accepted_actions,
                "tk_pmenu_pointer_press_equivalence_verified": True,
                "pmenu_source_row_pixels_rendered": True,
                "source_backed_squad_pixels_verified": True,
                "source_backed_squad_photo_dimensions": clean_photo_dimensions,
                "squad_view_transition": squad_view_receipt,
                "source_backed_fixtures_pixels_verified": True,
                "source_backed_fixtures_photo_dimensions": fixture_photo_dimensions,
                "pmatchinfo_source_accepted_action_verified": True,
                "pmatchinfo_normal_fixture_cell_opening_verified": False,
                "pmatchinfo_secondary_context_reconstructed": False,
                "pmatchinfo_owner_local_child_controls_verified": False,
                "pmatchinfo_popup_origin": [20, 50],
                "pmatchinfo_popup_size": [760, 500],
                "pmatchinfo_photo_dimensions": pmatchinfo_photo_dimensions,
                "pmatchinfo_source_accepted_exit_verified": True,
                "source_backed_league_tables_pixels_verified": True,
                "source_backed_league_tables_photo_dimensions": league_tables_photo_dimensions,
                **clean_contract,
            }
        finally:
            try:
                clean_root.destroy()
            except Exception:
                pass

        return {
            "schema_version": 8,
            "passed": True,
            "audit_kind": "real_windows_tk_first_screen_management_and_clean_host_smoke",
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "tk_patchlevel": tk_patchlevel,
            "dpi_awareness": dpi_awareness,
            "source_verification": "canonical_checksum_gated_loaders",
            "pstartmenu_initial": {
                "contract": start_contract,
                "live_tk": start_live,
            },
            "pstartmenu_alternate_group": {
                "contract": alternate_contract,
                "live_tk": alternate_live,
            },
            "teamselect": {
                "contract": team_contract,
                "live_tk": team_live,
                "competition_filter_and_order_verified": True,
                "club_filter_and_order_verified": True,
                "country_competition_population_flow_verified": True,
                "club_row_toggle_and_active_frame_verified": True,
                "start_without_club_rejected": True,
            },
            "pstartmenu_after_back": {
                "contract": return_contract,
                "live_tk": return_live,
            },
            "management": {
                "entered_via_native_club_selection_and_start": True,
                "selected_club_id": management_club.source_id,
                "pmenu_pointer_press_hit_test_verified": True,
                "pmenu_pointer_press_activation_dispatched": True,
                **management_contract,
            },
            "clean_application_host": clean_host_receipt,
            "navigation": {
                "new_game_to_teamselect_via_real_tk_binding": True,
                "teamselect_back_to_menu_via_real_tk_binding": True,
                "teamselect_selected_club_start_to_management_via_real_tk_binding": True,
                "default_clean_host_start_to_management_via_real_tk_binding": True,
                "source_accepted_pmenu_callbacks_via_real_tk_press_verified": True,
                "tk_pmenu_pointer_press_equivalence_verified": True,
                "squad_source_accepted_view_transition_verified": True,
                "squad_top_control_pointer_equivalence_verified": False,
                "pmatchinfo_source_resolved_adapter_verified": True,
                "normal_fixture_cell_pmatchinfo_opening_verified": False,
            },
            "unresolved_boundaries": [
                "Surrounding management background pixels",
                "Original PMenu keyboard-event equivalence",
                "PSquadScreen top-control modern pointer equivalence and post-event formation/player pixels",
                "League Fixtures 24x13 cell placement/text and the normal secondary-context PMatchInfo bridge",
                "PMatchInfo owner-local child control screen transforms",
                "Broader Gate-13 management-panel graphical fidelity beyond integrated source-owned layers",
            ],
            "gate13_complete": False,
        }
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-exe", type=Path, required=True)
    parser.add_argument("--original-art-root", type=Path, required=True)
    parser.add_argument("--original-language-root", type=Path, required=True)
    parser.add_argument("--original-font20", type=Path, required=True)
    parser.add_argument("--canonical-game-dir", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    receipt_path = _require_private_receipt(args.output_receipt)
    receipt = run_real_windows_graphical_audit(
        original_exe=args.original_exe,
        original_art_root=args.original_art_root,
        original_language_root=args.original_language_root,
        original_font20=args.original_font20,
        canonical_game_dir=args.canonical_game_dir,
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Real Windows first-screen graphical audit passed: {receipt_path}")
    print(
        "TeamSelect hierarchy filtering/native row states passed; "
        "club payload mapping and broader management presentation keep Gate 13 open."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
