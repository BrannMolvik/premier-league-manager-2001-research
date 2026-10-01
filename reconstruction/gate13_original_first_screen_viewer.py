"""Private Windows/Tk developer viewer for the recovered FM2001 opening screens.

Only source-hash-verified assets are loaded. The user can manually cycle all
23 original atlas source frames to inspect artwork and click already-proven
action rectangles. This is intentionally NOT the game's final UI: native
mapping and PStartMenu caption placement/color endpoints are recovered and
drawn from the original glyph alpha, but this diagnostic keeps manual frame
selection; TeamSelect hierarchy content and manager-home
presentation still require recovered executable evidence.

Tk is imported only when this developer viewer is actually launched.
"""
from __future__ import annotations

import argparse
from base64 import b64encode
from pathlib import Path

from front_end_session import FrontEndSession
from front_end_state import FrontEndCommand, FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter,
    OriginalHierarchyInteraction,
)
from original_live_debug_view import (
    OriginalLiveDebugError, build_original_debug_frame, endpoint_text_rgba,
)
from original_hierarchy_debug_inspector import (
    OriginalHierarchyDebugError, inspect_original_hierarchy_source_frames,
)
from original_pstartmenu_resources import load_verified_english_pstartmenu_inputs
from original_teamselect_resources import load_verified_original_teamselect_inputs


class OriginalFirstScreenTkDebug:
    """Fixed, unscaled 800x600 original-pixel diagnostic with external controls."""

    def __init__(self, presenter: OriginalFirstScreenPresenter, root, tk, ttk):
        self.presenter = presenter
        self.root = root
        self.tk = tk
        self.ttk = ttk
        self.source_frame_index = 0
        # Independent source indices: the two original hierarchy strips do
        # not have to contain the same number of frames as action atlases.
        self.hierarchy_animation_source_index = 0
        self.hierarchy_bars_source_index = 0
        self._photos = []

        self.root.title("FM2001 verified original pixels: DEVELOPER PREVIEW ONLY")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=800, height=600,
                                highlightthickness=0, borderwidth=0)
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.on_original_click)

        sidebar = ttk.Frame(root, width=330)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)
        ttk.Label(
            sidebar, wraplength=300,
            text="SOURCE PIXEL DIAGNOSTIC, NOT ORIGINAL FM2001 UI. "
                 "Frame selection below remains MANUAL for atlas inspection. "
                 "Native groups and PStartMenu text placement are recovered; "
                 "TeamSelect rows use their recovered native states.",
        ).pack(anchor="w")

        buttons = ttk.Frame(sidebar)
        buttons.pack(anchor="w", pady=8)
        ttk.Button(
            buttons, text="Previous source frame",
            command=lambda: self.step_source_frame(-1),
        ).pack(side=tk.LEFT)
        ttk.Button(
            buttons, text="Next",
            command=lambda: self.step_source_frame(1),
        ).pack(side=tk.LEFT)
        self.frame_label = ttk.Label(sidebar, text="")
        self.frame_label.pack(anchor="w")
        self.events_label = ttk.Label(sidebar, text="", wraplength=300,
                                      justify=tk.LEFT)
        self.events_label.pack(anchor="w", pady=8)

        ttk.Label(
            sidebar, text="Independent hierarchy source-strip inspector. "
            "The canvas uses recovered state-specific frames and captions.",
            wraplength=300,
        ).pack(anchor="w")
        anim_controls = ttk.Frame(sidebar)
        anim_controls.pack(anchor="w")
        ttk.Button(
            anim_controls, text="Previous hierarchy animation source",
            command=lambda: self.step_hierarchy_source_frame("animation", -1),
        ).pack(side=tk.LEFT)
        ttk.Button(
            anim_controls, text="Next",
            command=lambda: self.step_hierarchy_source_frame("animation", 1),
        ).pack(side=tk.LEFT)
        self.hierarchy_anim_label = ttk.Label(
            sidebar, text="Animation source frame unavailable"
        )
        self.hierarchy_anim_label.pack(anchor="w")
        bars_controls = ttk.Frame(sidebar)
        bars_controls.pack(anchor="w")
        ttk.Button(
            bars_controls, text="Previous hierarchy bars source",
            command=lambda: self.step_hierarchy_source_frame("bars", -1),
        ).pack(side=tk.LEFT)
        ttk.Button(
            bars_controls, text="Next",
            command=lambda: self.step_hierarchy_source_frame("bars", 1),
        ).pack(side=tk.LEFT)
        self.hierarchy_bars_label = ttk.Label(
            sidebar, text="Bars source frame unavailable"
        )
        self.hierarchy_bars_label.pack(anchor="w")

        ttk.Label(
            sidebar,
            text="Developer-only explicit club ID override:"
        ).pack(anchor="w")
        self.club_id_text = tk.StringVar()
        ttk.Entry(sidebar, textvariable=self.club_id_text,
                  width=14).pack(anchor="w")
        ttk.Button(
            sidebar, text="Set explicit backend club",
            command=self.choose_debug_club,
        ).pack(anchor="w", pady=4)

        self.status = tk.StringVar(value="Original source-pixel diagnostic ready")
        ttk.Label(sidebar, textvariable=self.status,
                  wraplength=300).pack(anchor="w", pady=8)
        root.bind("<Left>", lambda _: self.step_source_frame(-1))
        root.bind("<Right>", lambda _: self.step_source_frame(1))
        self.redraw()

    def _photo(self, png: bytes):
        # Tk 8.6 PhotoImage accepts base64 PNG. Do not use Pillow or synthesize art.
        photo = self.tk.PhotoImage(
            data=b64encode(png).decode("ascii"), format="png"
        )
        self._photos.append(photo)
        return photo

    def redraw(self):
        view = self.presenter.snapshot()
        try:
            frame = build_original_debug_frame(
                view, self.source_frame_index
            )
        except OriginalLiveDebugError:
            # This viewer exposes a global manual source index for both
            # original atlases, but never wraps a bad frame silently.
            self.source_frame_index = 0
            frame = build_original_debug_frame(view, 0)
        self.canvas.delete("all")
        self._photos = []
        background = self._photo(frame.background_png)
        self.canvas.create_image(0, 0, image=background, anchor=self.tk.NW)
        for overlay in frame.original_source_frame_overlays:
            art = self._photo(overlay.source_frame_png)
            self.canvas.create_image(
                overlay.rect.x, overlay.rect.y,
                image=art, anchor=self.tk.NW
            )
        for caption in frame.native_caption_overlays:
            glyphs = self._photo(caption.glyph_rgba_png)
            self.canvas.create_image(
                caption.line_origin_x, caption.line_origin_y,
                image=glyphs, anchor=self.tk.NW
            )
        for row in (*view.hierarchy_rows, *view.club_rows):
            animation = self._photo(encode_rgba_png(
                row.animation_frame.width,
                row.animation_frame.height,
                row.animation_frame.rgba,
            ))
            bar = self._photo(encode_rgba_png(
                row.bar_frame.width,
                row.bar_frame.height,
                row.bar_frame.rgba,
            ))
            glyph_rgba = endpoint_text_rgba(
                row.glyph_mask.alpha, row.native_color_16
            )
            glyphs = self._photo(encode_rgba_png(
                row.glyph_mask.width,
                row.glyph_mask.height,
                glyph_rgba,
            ))
            self.canvas.create_image(
                row.animation_rect.x, row.animation_rect.y,
                image=animation, anchor=self.tk.NW,
            )
            self.canvas.create_image(
                row.bar_rect.x, row.bar_rect.y,
                image=bar, anchor=self.tk.NW,
            )
            self.canvas.create_image(
                row.line_origin_x, row.line_origin_y,
                image=glyphs, anchor=self.tk.NW,
            )
        self.frame_label.configure(
            text=f"Manually selected original source frame: "
                 f"{self.source_frame_index} (native mapping available; "
                 "manual inspection mode)"
        )
        actions = [
            f"Event {overlay.event}: "
            f"{overlay.source_label_not_positioned or '[native label unresolved]'} "
            f"@ ({overlay.rect.x},{overlay.rect.y})"
            for overlay in frame.original_source_frame_overlays
        ]
        if frame.screen is FrontEndScreen.TEAM_SELECT:
            actions.append(
                f"Hierarchy: {len(view.hierarchy_rows)} visible country/league "
                f"rows and {len(view.club_rows)} visible club rows."
            )
        self.events_label.configure(text="\n".join(actions))
        try:
            hierarchy = inspect_original_hierarchy_source_frames(
                view,
                animation_source_index=self.hierarchy_animation_source_index,
                bars_source_index=self.hierarchy_bars_source_index,
            )
        except OriginalHierarchyDebugError:
            self.hierarchy_animation_source_index = 0
            self.hierarchy_bars_source_index = 0
            hierarchy = inspect_original_hierarchy_source_frames(view)
        if hierarchy is None:
            self.hierarchy_anim_label.configure(
                text="Hierarchy animation source not present on this view", image=""
            )
            self.hierarchy_bars_label.configure(
                text="Hierarchy bars source not present on this view", image=""
            )
        else:
            anim_photo = self._photo(hierarchy.animation.source_frame_png)
            bar_photo = self._photo(hierarchy.bars.source_frame_png)
            self.hierarchy_anim_label.configure(
                text=(
                    "Animation source frame "
                    f"{hierarchy.animation.source_frame_index_only}/"
                    f"{hierarchy.animation.source_frame_count - 1}: "
                    "NOT original screen placement"
                ),
                image=anim_photo, compound="top",
            )
            self.hierarchy_bars_label.configure(
                text=(
                    "Bars source frame "
                    f"{hierarchy.bars.source_frame_index_only}/"
                    f"{hierarchy.bars.source_frame_count - 1}: "
                    "NOT original screen placement"
                ),
                image=bar_photo, compound="top",
            )

    def step_hierarchy_source_frame(self, kind: str, delta: int):
        view = self.presenter.snapshot()
        if view.screen is not FrontEndScreen.TEAM_SELECT or view.hierarchy_art is None:
            self.status.set("No original hierarchy strip available for source inspection")
            return
        if kind == "animation":
            count = len(view.hierarchy_art.animation.frames)
            attr = "hierarchy_animation_source_index"
        elif kind == "bars":
            count = len(view.hierarchy_art.bars.frames)
            attr = "hierarchy_bars_source_index"
        else:
            raise ValueError("Unknown original hierarchy source family")
        if count <= 0:
            self.status.set("Original hierarchy source strip has no frames")
            return
        setattr(self, attr, (getattr(self, attr) + delta) % count)
        self.redraw()

    def step_source_frame(self, delta: int):
        view = self.presenter.snapshot()
        count = min(len(item.atlas.frames) for item in view.controls)
        if count <= 0:
            self.status.set("Original action atlas has no available source frames")
            return
        self.source_frame_index = (self.source_frame_index + delta) % count
        self.redraw()

    def on_original_click(self, event):
        """Canvas uses fixed original 800x600 unscaled source coordinates."""
        try:
            result = self.presenter.pointer(int(event.x), int(event.y))
            if result is None:
                self.status.set("No executable-proven click action here.")
            elif isinstance(result, OriginalHierarchyInteraction):
                if result.row_kind == "club":
                    verb = (
                        "selected" if result.selected_club_record_index is not None
                        else "cleared"
                    )
                    self.status.set(
                        f"Native club row {result.text!r} {verb}; "
                        f"record index {result.source_id}. Backend club selection "
                        "remains fail-closed pending payload re-trace."
                    )
                else:
                    self.status.set(
                        f"Native {result.row_kind} row activated: "
                        f"{result.text!r} (source ID {result.source_id})."
                    )
            elif result.transition.command is FrontEndCommand.TEAMSELECT_START_CONTINUE:
                self.status.set(
                    f"Backend selection returned {result.selected_manager!r}; "
                    "native manager-home presentation is not yet reconstructed."
                )
            elif result.transition.command is not None:
                self.status.set(
                    f"Recovered event command: {result.transition.command.name}; "
                    "non-New-Game host routing remains unfinished."
                )
            else:
                self.status.set(
                    f"Recovered navigation: {result.transition.screen.name}"
                )
        except Exception as exc:
            # Developer preview only. Preserve active original screen so a
            # failed database load or missing club can be diagnosed/retried.
            self.status.set(f"Action was rejected: {type(exc).__name__}: {exc}")
        self.redraw()

    def choose_debug_club(self):
        if self.presenter.session.navigation.screen is not FrontEndScreen.TEAM_SELECT:
            self.status.set("Explicit debug club selection requires TeamSelect")
            return
        try:
            value = int(self.club_id_text.get())
            self.presenter.choose_club(value)
            self.status.set(
                f"Developer-only explicit club ID {value} selected; "
                "native hierarchy record remains unchanged pending payload re-trace."
            )
        except (ValueError, TypeError, RuntimeError) as exc:
            self.status.set(f"Explicit club selection rejected: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-exe", type=Path, required=True)
    parser.add_argument("--original-art-root", type=Path, required=True)
    parser.add_argument("--original-language-root", type=Path, required=True)
    parser.add_argument("--original-font20", type=Path, required=True)
    parser.add_argument("--canonical-game-dir", type=Path, required=True)
    args = parser.parse_args()

    # Fail closed on source mismatch before opening a diagnostic window.
    menu = load_verified_english_pstartmenu_inputs(
        original_art_dir=args.original_art_root,
        original_language_dir=args.original_language_root,
        original_zurich_font20=args.original_font20,
        original_executable=args.original_exe,
    )
    team = load_verified_original_teamselect_inputs(
        original_art_dir=args.original_art_root,
        original_executable=args.original_exe,
    )
    presenter = OriginalFirstScreenPresenter(
        FrontEndSession.for_canonical_game_dir(args.canonical_game_dir),
        menu, team,
    )
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    OriginalFirstScreenTkDebug(presenter, root, tk, ttk)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
