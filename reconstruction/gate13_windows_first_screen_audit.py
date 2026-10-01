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
import sys

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_original_first_screen_viewer import OriginalFirstScreenTkDebug
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter,
    OriginalFirstScreenSnapshot,
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
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
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
        if captions:
            raise WindowsFirstScreenAuditError(
                "TeamSelect captions are still unresolved and must not be invented"
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

        # Country activation clears the selected competition and club list.
        row_x, row_y = TEAMSELECT_HIERARCHY_ROW_ORIGINS[0]
        viewer.canvas.event_generate("<Button-1>", x=row_x + 1, y=row_y + 1)
        _pump(root)
        collapsed = presenter.snapshot()
        if collapsed.club_rows:
            raise WindowsFirstScreenAuditError(
                "Country activation did not clear the native club population"
            )
        if presenter.session.selected_club_id is not None:
            raise WindowsFirstScreenAuditError(
                "Country activation retained a club selection"
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
        if presenter.session.selected_club_id is not None:
            raise WindowsFirstScreenAuditError(
                "Unresolved native selection payload leaked into gameplay club selection"
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
        if presenter.hierarchy is None or presenter.hierarchy.selected_club_id is not None:
            raise WindowsFirstScreenAuditError(
                "Second native club click did not clear the visual selection record"
            )
        if presenter.session.selected_club_id is not None:
            raise WindowsFirstScreenAuditError(
                "Unresolved native selection payload leaked into gameplay after toggle"
            )

        # Start/Continue is source-proven, but without a recovered hierarchy
        # selection it must reject rather than synthesize a club.
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

        return {
            "schema_version": 2,
            "passed": True,
            "audit_kind": "real_windows_tk_first_screen_graphical_smoke",
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
            "navigation": {
                "new_game_to_teamselect_via_real_tk_binding": True,
                "teamselect_back_to_menu_via_real_tk_binding": True,
            },
            "unresolved_boundaries": [
                "Exact native TeamSelect selection-record payload -> gameplay club-ID mapping",
                "Broader Gate-13 management-screen graphical fidelity",
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
