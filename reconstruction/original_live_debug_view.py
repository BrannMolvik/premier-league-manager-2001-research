"""Developer-only live original first-screen pixel inspection model.

Renders the exact source-composed background and a MANUALLY chosen numeric
source-atlas frame at each previously proven action rectangle. Choosing the
source index globally is a diagnostic convenience and does not reproduce the
legacy Button@ease_2001 idle/hover/down/disabled state transitions.
Recovered English labels are listed for debugging, NOT drawn at guessed
coordinates or colors. TeamSelect hierarchy rows are positional evidence
only; no country/league/club hit behavior is synthesized here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from front_end_state import FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_first_screen_presenter import OriginalFirstScreenSnapshot
from original_front_end_layout import OriginalRect, SCREEN_SIZE


class OriginalLiveDebugError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalDebugOverlay:
    event: int
    source_frame_index: int
    rect: OriginalRect
    source_frame_png: bytes
    source_frame_rgba_sha256: str
    source_label_not_positioned: str | None


@dataclass(frozen=True)
class OriginalLiveDebugFrame:
    screen: FrontEndScreen
    background_png: bytes
    original_source_frame_overlays: tuple[OriginalDebugOverlay, ...]
    hierarchy_row_origins_not_interactive: tuple[tuple[int, int], ...]
    native_button_animation_recovered: bool = False
    native_text_placement_recovered: bool = False


def build_original_debug_frame(
    snapshot: OriginalFirstScreenSnapshot, source_frame_index: int
) -> OriginalLiveDebugFrame:
    """Use original pixel coordinates/source frames with no substituted skin."""
    if type(source_frame_index) is not int or source_frame_index < 0:
        raise OriginalLiveDebugError(
            "Source frame index must be a nonnegative integer, not a native state"
        )
    if len(snapshot.background_rgba) != SCREEN_SIZE[0] * SCREEN_SIZE[1] * 4:
        raise OriginalLiveDebugError("Missing complete 800x600 original background")
    overlays = []
    for control in snapshot.controls:
        if (
            control.rect.x < 0 or control.rect.y < 0
            or control.rect.right > SCREEN_SIZE[0]
            or control.rect.bottom > SCREEN_SIZE[1]
        ):
            raise OriginalLiveDebugError("Recovered original control exceeds original screen")
        if source_frame_index >= len(control.atlas.frames):
            raise OriginalLiveDebugError(
                f"Requested source frame {source_frame_index} exceeds original atlas"
            )
        source = control.exact_source_frame(source_frame_index)
        if (source.width, source.height) != (
            control.rect.width, control.rect.height
        ):
            raise OriginalLiveDebugError(
                "Original source frame geometry differs from proven action rectangle"
            )
        overlays.append(
            OriginalDebugOverlay(
                event=control.event,
                source_frame_index=source_frame_index,
                rect=control.rect,
                source_frame_png=encode_rgba_png(
                    source.width, source.height, source.rgba
                ),
                source_frame_rgba_sha256=sha256(source.rgba).hexdigest(),
                source_label_not_positioned=(
                    control.caption.original_text if control.caption else None
                ),
            )
        )
    return OriginalLiveDebugFrame(
        screen=snapshot.screen,
        background_png=encode_rgba_png(*SCREEN_SIZE, snapshot.background_rgba),
        original_source_frame_overlays=tuple(overlays),
        hierarchy_row_origins_not_interactive=snapshot.hierarchy_row_origins,
    )
