"""Operator-visible Tk window for the resolved-only Gate-14 FastView bundle.

This is a presentation boundary over an already-built
HumanFastViewResolvedPresentation. It creates no match state, performs no RNG,
does not choose presentation resources, and does not invent a source navigation
trigger. The caller supplies the completed-match presentation and an existing
Tk parent window.

Only the canonical resolved-preview PNG is drawn. Unresolved overlap pixels stay
transparent exactly as recorded by the preview; the surrounding Tk window/canvas
is compatibility chrome and is not claimed as original FM2001 pixels.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_human_resolved_presentation import (
    HumanFastViewResolvedPresentation,
    HumanFastViewResolvedPresentationError,
    draw_human_fastview_resolved_presentation,
)
from gate14_fastview_tk_surface import FastViewResolvedTkDraw


class HumanFastViewTkWindowError(ValueError):
    pass


FASTVIEW_NATIVE_SIZE = (800, 600)
FASTVIEW_WINDOW_TITLE = "FM2001 FastView - verified partial presentation"


@dataclass(frozen=True)
class HumanFastViewTkWindow:
    """Keep ownership of one non-authoritative compatibility window."""

    presentation: HumanFastViewResolvedPresentation
    window: object
    canvas: object
    draw: FastViewResolvedTkDraw
    native_size: tuple[int, int] = FASTVIEW_NATIVE_SIZE
    source_navigation_trigger_recovered: bool = False
    unresolved_pixels_remain_transparent: bool = True
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if type(self.presentation) is not HumanFastViewResolvedPresentation:
            raise HumanFastViewTkWindowError(
                "FastView window requires exact completed-human presentation"
            )
        if type(self.draw) is not FastViewResolvedTkDraw:
            raise HumanFastViewTkWindowError(
                "FastView window requires exact resolved Tk draw"
            )
        if self.draw.preview is not self.presentation.preview:
            raise HumanFastViewTkWindowError(
                "FastView window draw must retain the presentation's canonical preview"
            )
        if self.native_size != FASTVIEW_NATIVE_SIZE:
            raise HumanFastViewTkWindowError(
                "FastView window must preserve the native 800x600 surface"
            )
        if (
            self.source_navigation_trigger_recovered
            or not self.unresolved_pixels_remain_transparent
            or self.complete_fastview_frame
            or self.presentation.complete_fastview_frame
            or self.draw.complete_fastview_frame
        ):
            raise HumanFastViewTkWindowError(
                "FastView window cannot promote unresolved presentation fidelity"
            )


def open_human_fastview_tk_window(
    presentation: HumanFastViewResolvedPresentation,
    tk_module,
    parent,
) -> HumanFastViewTkWindow:
    """Open one bounded 800x600 Tk window for an existing resolved bundle.

    This function deliberately does not call mainloop(), grab_set(), focus_force(),
    fullscreen APIs, or any gameplay/navigation method. The caller owns lifecycle
    and decides when a source-backed runtime trigger exists.
    """
    if type(presentation) is not HumanFastViewResolvedPresentation:
        raise HumanFastViewTkWindowError(
            "FastView window requires exact completed-human presentation"
        )
    if not hasattr(tk_module, "Toplevel") or not hasattr(tk_module, "Canvas"):
        raise HumanFastViewTkWindowError(
            "FastView window requires Tk Toplevel and Canvas constructors"
        )
    if parent is None:
        raise HumanFastViewTkWindowError(
            "FastView window requires an existing caller-owned Tk parent"
        )

    window = tk_module.Toplevel(parent)
    if hasattr(window, "title"):
        window.title(FASTVIEW_WINDOW_TITLE)
    if hasattr(window, "resizable"):
        window.resizable(False, False)

    canvas = tk_module.Canvas(
        window,
        width=FASTVIEW_NATIVE_SIZE[0],
        height=FASTVIEW_NATIVE_SIZE[1],
        highlightthickness=0,
        borderwidth=0,
    )
    if not hasattr(canvas, "pack"):
        raise HumanFastViewTkWindowError(
            "FastView compatibility canvas must expose pack()"
        )
    canvas.pack()

    try:
        draw = draw_human_fastview_resolved_presentation(
            presentation,
            tk_module,
            canvas,
        )
    except HumanFastViewResolvedPresentationError as exc:
        raise HumanFastViewTkWindowError(
            "FastView presentation could not be drawn without fidelity promotion"
        ) from exc

    return HumanFastViewTkWindow(
        presentation=presentation,
        window=window,
        canvas=canvas,
        draw=draw,
    )
