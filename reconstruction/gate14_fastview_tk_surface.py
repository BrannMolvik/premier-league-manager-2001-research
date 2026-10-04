"""Standalone Tk draw boundary for the resolved-only Gate-14 FastView preview.

The canonical resolved-preview layer owns lossless PNG encoding and the
authoritative overlap-mask export. This module adds only the Tk presentation
seam: it places the already-built RGBA preview on a caller-owned canvas.

Unresolved pixels remain transparent exactly as exported. This module does not
clear or color the canvas beneath them, does not draw a background, does not
rerun simulation, and does not claim a complete FastView frame.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass

from gate14_fastview_resolved_composite import FastViewResolvedOnlyComposite
from gate14_fastview_resolved_preview import (
    FastViewResolvedPreview,
    build_fastview_resolved_preview,
)


class FastViewResolvedTkSurfaceError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewResolvedTkDraw:
    """Keep Tk image ownership plus the canonical preview audit record."""

    preview: FastViewResolvedPreview
    photo_image: object
    canvas_item_id: object
    unresolved_pixels_remain_transparent: bool = True
    cross_component_z_order_recovered: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if type(self.preview) is not FastViewResolvedPreview:
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw requires exact resolved preview"
            )
        if (
            self.preview.cross_component_z_order_recovered
            or self.preview.flattened_frame_available
            or self.preview.complete_fastview_frame
        ):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw cannot accept promoted preview fidelity"
            )
        if (
            not self.unresolved_pixels_remain_transparent
            or self.cross_component_z_order_recovered
            or self.complete_fastview_frame
        ):
            raise FastViewResolvedTkSurfaceError(
                "FastView Tk draw cannot promote unresolved frame fidelity"
            )


def draw_fastview_preview_on_tk_canvas(
    preview: FastViewResolvedPreview,
    tk_module,
    canvas,
) -> FastViewResolvedTkDraw:
    """Draw one canonical resolved preview at native 800x600 origin.

    The caller owns the canvas/window lifecycle. No canvas clear, background
    color, scaling, fullscreen policy, event binding, or frame substitution is
    performed here.
    """
    if type(preview) is not FastViewResolvedPreview:
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires exact resolved preview"
        )
    if (
        preview.cross_component_z_order_recovered
        or preview.flattened_frame_available
        or preview.complete_fastview_frame
    ):
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface cannot accept promoted preview fidelity"
        )
    if not hasattr(tk_module, "PhotoImage") or not hasattr(tk_module, "NW"):
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires PhotoImage and NW from the Tk module"
        )
    if not hasattr(canvas, "create_image"):
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires a canvas create_image boundary"
        )

    photo = tk_module.PhotoImage(
        data=b64encode(preview.rgba_png).decode("ascii"),
        format="png",
    )
    item_id = canvas.create_image(
        0,
        0,
        image=photo,
        anchor=tk_module.NW,
    )
    return FastViewResolvedTkDraw(
        preview=preview,
        photo_image=photo,
        canvas_item_id=item_id,
    )


def draw_fastview_resolved_on_tk_canvas(
    composite: FastViewResolvedOnlyComposite,
    tk_module,
    canvas,
) -> FastViewResolvedTkDraw:
    """Build the canonical preview, then draw only its resolved RGBA subset."""
    if type(composite) is not FastViewResolvedOnlyComposite:
        raise FastViewResolvedTkSurfaceError(
            "FastView Tk surface requires exact resolved-only composite"
        )
    return draw_fastview_preview_on_tk_canvas(
        build_fastview_resolved_preview(composite),
        tk_module,
        canvas,
    )
