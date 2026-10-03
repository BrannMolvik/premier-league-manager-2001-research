"""Canonical TeamSelect action captions, not generic Back/Start labels.

0x4D888A and 0x4D9270 select language globals 0x98211C/0x982124;
the complete 0x635F30 loader binds IDX 2487/2485. Setup uses font wrapper
0x896340, loaded from Zurich_XCn_BT_30pixel.fnt at 0x604600..0x604651.
"""
from ea_font import EAFont
from ea_language_strings import EAStringIndex, EAStringTable
from original_front_end_layout import (
    TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT,
)
from original_pstartmenu_labels import PStartMenuCaption

TEAMSELECT_ACTION_FONT_PATH = "Fonts/Zurich_XCn_BT_30pixel.fnt"
TEAMSELECT_ACTION_FONT_SHA256 = (
    "0fe5f5315006a35438d3cdca79a29e4b334ea714c76b26148b9ad0a3f666a607"
)


def prepare_original_teamselect_captions(
    font: EAFont, strings: EAStringTable, index: EAStringIndex,
) -> tuple[PStartMenuCaption, ...]:
    captions = []
    for event, rect, position in (
        (TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT, 2487),
        (TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT, 2485),
    ):
        text = index.resolve(strings, position)
        captions.append(PStartMenuCaption(
            event, position, text, rect, font.render_text_alpha(text),
            rect.x + (rect.width - font.measure_text(text)) // 2,
            rect.y + (rect.height - font.native_line_height()) // 2,
            rect,
        ))
    return tuple(captions)
