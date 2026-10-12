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
    selector_owner_offset: int
    display_text_first_owner_offset: int
    display_text_second_owner_offset: int
    native_group_index: int


def original_supportstart_row_anchors() -> tuple[SourceSupportStartRowAnchor, ...]:
    """Original 0x4C8014..0x4C8263 repeated 0x4C9510 calls.

    `0x64F380` confirms the two source position values are x and y.
    No unqualified width/height, clickable area or staff name is returned.
    """
    return tuple(
        SourceSupportStartRowAnchor(
            index=i,
            origin=(
                SOURCE_SUPPORTSTART_FIRST_ROW[0],
                SOURCE_SUPPORTSTART_FIRST_ROW[1] + SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP*i,
            ),
            selector_owner_offset=SOURCE_SUPPORTSTART_SELECTOR_FIRST_OFFSET + SOURCE_SUPPORTSTART_SELECTOR_STRIDE*i,
            display_text_first_owner_offset=SOURCE_SUPPORTSTART_TEXT_FIRST_OFFSET + SOURCE_SUPPORTSTART_TEXT_STRIDE*i,
            display_text_second_owner_offset=SOURCE_SUPPORTSTART_TEXT_SECOND_OFFSET + SOURCE_SUPPORTSTART_TEXT_STRIDE*i,
            native_group_index=SOURCE_SUPPORTSTART_CHILD_GROUP_FIRST_INDEX + i,
        )
        for i in range(SOURCE_SUPPORTSTART_ROW_COUNT)
    )
