"""Developer-only live original first-screen pixel inspection model.

Renders the exact source-composed background and a MANUALLY chosen numeric
source-atlas frame at each previously proven action rectangle. PStartMenu
captions are now drawn at the executable-proven Zurich line origins using the
original glyph alpha and the only two recovered native 16-bit endpoint colors.
Mapping 0x0000 to all channels off and 0xFFFF to all channels on requires no
choice of an otherwise-unproven 16-bit channel layout. TeamSelect hierarchy
rows remain positional evidence only.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from front_end_state import FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_button_frames import button_group_subframe_for_source_index
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
class OriginalDebugCaptionOverlay:
    event: int
    original_text: str
    line_origin_x: int
    line_origin_y: int
    clip_rect: OriginalRect
    native_color_16: int
    glyph_rgba_png: bytes
    glyph_rgba_sha256: str


@dataclass(frozen=True)
class OriginalLiveDebugFrame:
    screen: FrontEndScreen
    background_png: bytes
    original_source_frame_overlays: tuple[OriginalDebugOverlay, ...]
    native_caption_overlays: tuple[OriginalDebugCaptionOverlay, ...]
    hierarchy_row_origins_not_interactive: tuple[tuple[int, int], ...]
    native_button_animation_recovered: bool = True
    native_text_placement_recovered: bool = False


def endpoint_text_rgba(alpha: bytes, native_color_16: int) -> bytes:
    """Convert only the two proven all-bits-off/on native endpoint colors."""
    if native_color_16 == 0x0000:
        channel = 0
    elif native_color_16 == 0xFFFF:
        channel = 255
    else:
        raise OriginalLiveDebugError(
            "No generic native 16-bit -> RGBA conversion has been recovered"
        )
    out = bytearray(len(alpha) * 4)
    for index, value in enumerate(alpha):
        pos = index * 4
        out[pos:pos + 4] = bytes((channel, channel, channel, value))
    return bytes(out)


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
    captions = []
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
                # Legacy field name retained for callers while the label now
                # also has a separately positioned source-backed overlay.
                source_label_not_positioned=(
                    control.caption.original_text if control.caption else None
                ),
            )
        )
        if control.caption is not None:
            group, _subframe = button_group_subframe_for_source_index(
                source_frame_index
            )
            caption = control.caption
            mask = caption.glyph_mask
            right = caption.line_origin_x + mask.width
            bottom = caption.line_origin_y + mask.height
            if (
                caption.line_origin_x < caption.clip_rect.x
                or caption.line_origin_y < caption.clip_rect.y
                or right > caption.clip_rect.right
                or bottom > caption.clip_rect.bottom
            ):
                raise OriginalLiveDebugError(
                    "Recovered Zurich glyph mask exceeds its native clip rectangle"
                )
            native_color = caption.native_color_for_group(group)
            rgba = endpoint_text_rgba(mask.alpha, native_color)
            captions.append(
                OriginalDebugCaptionOverlay(
                    event=control.event,
                    original_text=caption.original_text,
                    line_origin_x=caption.line_origin_x,
                    line_origin_y=caption.line_origin_y,
                    clip_rect=caption.clip_rect,
                    native_color_16=native_color,
                    glyph_rgba_png=encode_rgba_png(mask.width, mask.height, rgba),
                    glyph_rgba_sha256=sha256(rgba).hexdigest(),
                )
            )
    return OriginalLiveDebugFrame(
        screen=snapshot.screen,
        background_png=encode_rgba_png(*SCREEN_SIZE, snapshot.background_rgba),
        original_source_frame_overlays=tuple(overlays),
        native_caption_overlays=tuple(captions),
        hierarchy_row_origins_not_interactive=snapshot.hierarchy_row_origins,
        native_text_placement_recovered=bool(captions) and len(captions) == len(overlays),
    )
