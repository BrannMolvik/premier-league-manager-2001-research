"""Prepare source-derived original PStartMenu captions without inventing layout.

The canonical executable's language loader 0x635F30 binds original English.idx
entries 0, 1, 2 and 6 to primary menu events 1..4, respectively. This layer
resolves the actual STR/IDX bytes through ea_language_strings and generates
bit-exact font masks through the recovered original EAUK bitmap font parser.

Absolute caption baselines, label colors and Button@ease_2001 animation frames
are deliberately *not* guessed. Consumers must use separately recovered
placement/appearance evidence before describing a composited frame as original.
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


def prepare_original_pstartmenu_captions(
    font: EAFont, strings: EAStringTable, index: EAStringIndex
) -> tuple[PStartMenuCaption, ...]:
    """Bind the four proven event/IDX pairs to original-language glyph pixels.

    Pixel masks remain local to their own bounding boxes, not placed on the
    final 800x600 surface until the original text-alignment routine is traced.
    The same source format supports other original CP1252 language choices.
    """
    captions: list[PStartMenuCaption] = []
    frame_width, frame_height = PSTARTMENU_ACTION_FRAME_SIZE
    for action in PSTARTMENU_ACTIONS:
        if (action.rect.width, action.rect.height) != (
            frame_width, frame_height
        ):
            raise ValueError("Recovered action/control atlas geometry disagrees")
        text = index.resolve(strings, action.language_index)
        captions.append(
            PStartMenuCaption(
                event=action.event,
                source_idx_position=action.language_index,
                original_text=text,
                control_rect=action.rect,
                glyph_mask=font.render_text_alpha(text),
            )
        )
    return tuple(captions)
