"""Source-bounded PSupportStart seven-row geometry from the shipped original PE.

Not a complete window renderer. Source vtable 0x7C6DDC+4 -> 0x4C7B70
lays out seven staff child groups through 0x4C9510; that method calls the
native coordinate owner 0x64F380. The screen's full child rectangles,
button hit regions, glyphs and complete user interaction remain unresolved.
Original PE SHA-256: 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations
from dataclasses import dataclass

SOURCE_SUPPORTSTART_NATIVE_SIZE = (760, 500)
SOURCE_SUPPORTSTART_ROW_COUNT = 7
SOURCE_SUPPORTSTART_FIRST_ROW = (391, 181)
SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP = 40
# Native Generic/user_entry/text_bars.444 has 306x68 source header.
# 0x5F61D0 creates its 306x17 cropped frame; +0x14/+0x18 fields
# are 306/17 (0x64E500); 0x4C9510 adds 20 to each dimension
# before calling native rectangle owner 0x64F380.
SOURCE_SUPPORTSTART_ROW_RECT_SIZE = (326, 37)
SOURCE_SUPPORTSTART_BACKGROUND_SOURCE = 'FM2001_Art/Generic/user_entry/background.444'
SOURCE_SUPPORTSTART_ROW_BARS_SOURCE = 'FM2001_Art/Generic/user_entry/text_bars.444'
SOURCE_SUPPORTSTART_ROW_BUTTON_SOURCE = 'FM2001_Art/Generic/GenericButtonsAndBars/user_entry_anim.444'
SOURCE_SUPPORTSTART_SELECTOR_FIRST_OFFSET = 0x2224
SOURCE_SUPPORTSTART_SELECTOR_STRIDE = 0x4C
SOURCE_SUPPORTSTART_TEXT_FIRST_OFFSET = 0x70
SOURCE_SUPPORTSTART_TEXT_SECOND_OFFSET = 0x4F0
SOURCE_SUPPORTSTART_TEXT_STRIDE = 0x80
SOURCE_SUPPORTSTART_CHILD_GROUP_FIRST_INDEX = 8


@dataclass(frozen=True)
class SourceSupportStartRowAnchor:
    """Original editor row anchor and per-row owner offsets, not a hit rectangle."""

    index: int
    origin: tuple[int, int]
    # Source x/y/width/height through 0x4C9510 -> 0x64F380;
    # this is an original layout child bounding rect, not yet an input hit map.
    source_layout_rect: tuple[int, int, int, int]
    selector_owner_offset: int
    display_text_first_owner_offset: int
    display_text_second_owner_offset: int
    native_group_index: int


def original_supportstart_row_anchors() -> tuple[SourceSupportStartRowAnchor, ...]:
    """Original 0x4C8014..0x4C8263 repeated 0x4C9510 calls.

    `0x64F380` confirms the two source position values are x and y.
    Width/height come from original text_bars cropped frame 306x17 plus
    original native +20/+20 padding. Still NOT proof of on-screen click hit
    behavior, staff names, hover frame or fully decoded artwork.
    """
    return tuple(
        SourceSupportStartRowAnchor(
            index=i,
            origin=(
                SOURCE_SUPPORTSTART_FIRST_ROW[0],
                SOURCE_SUPPORTSTART_FIRST_ROW[1] + SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP*i,
            ),
            source_layout_rect=(
                SOURCE_SUPPORTSTART_FIRST_ROW[0],
                SOURCE_SUPPORTSTART_FIRST_ROW[1] + SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP*i,
                *SOURCE_SUPPORTSTART_ROW_RECT_SIZE,
            ),
            selector_owner_offset=SOURCE_SUPPORTSTART_SELECTOR_FIRST_OFFSET + SOURCE_SUPPORTSTART_SELECTOR_STRIDE*i,
            display_text_first_owner_offset=SOURCE_SUPPORTSTART_TEXT_FIRST_OFFSET + SOURCE_SUPPORTSTART_TEXT_STRIDE*i,
            display_text_second_owner_offset=SOURCE_SUPPORTSTART_TEXT_SECOND_OFFSET + SOURCE_SUPPORTSTART_TEXT_STRIDE*i,
            native_group_index=SOURCE_SUPPORTSTART_CHILD_GROUP_FIRST_INDEX + i,
        )
        for i in range(SOURCE_SUPPORTSTART_ROW_COUNT)
    )
