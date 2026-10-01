"""Prepare source-derived original PStartMenu captions at native coordinates.

The canonical executable's language loader 0x635F30 binds original English.idx
entries 0, 1, 2 and 6 to primary menu events 1..4, respectively. This layer
resolves the actual STR/IDX bytes through ea_language_strings and generates
bit-exact font masks through the recovered original EAUK bitmap font parser.

Direct canonical-executable tracing now also proves the shared Button setup
uses style 0x2000, zero x/y offsets, centered Zurich line origins, and 16-bit
values 0xFFFF normally or 0x0000 for native animation group 1. The color
values remain in their original render format rather than being guessed as a
modern RGB conversion.
"""

from __future__ import annotations

from dataclasses import dataclass

from ea_font import EAFont, EATextMask
from ea_language_strings import EAStringIndex, EAStringTable
from original_front_end_layout import (
    OriginalRect,
    PSTARTMENU_ACTIONS,
    PSTARTMENU_ACTION_FRAME_SIZE,
)


@dataclass(frozen=True)
class PStartMenuCaption:
    event: int
    source_idx_position: int
    original_text: str
    control_rect: OriginalRect
    glyph_mask: EATextMask
    line_origin_x: int
    line_origin_y: int
    clip_rect: OriginalRect
    native_style: int = 0x2000
    normal_color_16: int = 0xFFFF
    alternate_group_color_16: int = 0x0000

    def native_color_for_group(self, group: int) -> int:
        """Mirror Button vtable slot 41 at 0x653020."""
        if type(group) is not int or not 0 <= group <= 2:
            raise ValueError("Invalid native Button@ease group")
        return self.alternate_group_color_16 if group == 1 else self.normal_color_16


def prepare_original_pstartmenu_captions(
    font: EAFont, strings: EAStringTable, index: EAStringIndex
) -> tuple[PStartMenuCaption, ...]:
    """Bind the four proven event/IDX pairs to original-language glyph pixels.

    The same source format supports other original CP1252 language choices.
    ``line_origin_y`` is the native line origin; per-glyph ``draw_y`` remains
    encoded in the returned alpha mask exactly as in the original renderer.
    """
    captions: list[PStartMenuCaption] = []
    frame_width, frame_height = PSTARTMENU_ACTION_FRAME_SIZE
    for action in PSTARTMENU_ACTIONS:
        if (action.rect.width, action.rect.height) != (
            frame_width, frame_height
        ):
            raise ValueError("Recovered action/control atlas geometry disagrees")
        text = index.resolve(strings, action.language_index)
        glyph_mask = font.render_text_alpha(text)
        measured_width = font.measure_text(text)
        if glyph_mask.width != measured_width:
            raise ValueError("Zurich mask width differs from native text measure")
        line_height = font.native_line_height()
        captions.append(
            PStartMenuCaption(
                event=action.event,
                source_idx_position=action.language_index,
                original_text=text,
                control_rect=action.rect,
                glyph_mask=glyph_mask,
                line_origin_x=action.rect.x + (action.rect.width - measured_width) // 2,
                line_origin_y=action.rect.y + (action.rect.height - line_height) // 2,
                clip_rect=action.rect,
            )
        )
    return tuple(captions)
