"""Source-closed FM2001 FastView PossessionFigures text placement.

The original receiver formats three EventPossession bytes as %u%%. Static
tracing also closes their 40x18 screen rectangles, shared text style, exact
18-pixel Zurich source font, endpoint-white native color, and left/top
alignment. This module preserves side indices exactly; it deliberately does not
rename side 0 or side 1 as the human team because that orientation is not yet
source-closed.
"""
from __future__ import annotations

from dataclasses import dataclass


SOURCE_CONSTRUCTOR_VA = 0x51E7E0
SOURCE_RECEIVER_VA = 0x51EA80
SOURCE_FASTVIEW_CALLSITE_VA = 0x520802
SOURCE_PERCENT_FORMAT_VA = 0x82924C
SOURCE_PERCENT_FORMAT = "%u%%"
SOURCE_EVENT_ACCESSOR_VAS = (0x51A700, 0x51A710, 0x51A720)
SOURCE_EVENT_BYTE_OFFSETS = (0x0D, 0x0E, 0x0F)

SOURCE_TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960
SOURCE_TEXT_STYLE_SELECTOR_VA = 0x527BA0
SOURCE_TEXT_STYLE_INDEX = 1
SOURCE_TEXT_STYLE_WRAPPER_VA = 0x87BE90
SOURCE_TEXT_STYLE_INIT_VA = 0x603670
SOURCE_TEXT_FONT_OBJECT_VA = 0x9197E0
SOURCE_TEXT_FONT_LOAD_CALL_VA = 0x6042F5
SOURCE_TEXT_FONT_PATH_LITERAL_VA = 0x839F00
SOURCE_TEXT_FONT_PATH = "Fonts/Zurich_BdXCn_BT_18pixel.fnt"
SOURCE_TEXT_FONT_SHA256 = (
    "4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd"
)
SOURCE_TEXT_FONT_BYTE_SIZE = 83174
SOURCE_TEXT_FONT_ATLAS_SIZE = (1633, 18)
SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT = 20
SOURCE_TEXT_CONSTRUCTOR_FLAGS = 1
SOURCE_TEXT_RENDER_FLAGS = 9
SOURCE_TEXT_NATIVE_COLOR_16 = 0xFFFF
SOURCE_TEXT_DRAW_VA = 0x64F090
SOURCE_TEXT_FONT_RASTER_VA = 0x657280
SOURCE_TEXT_HORIZONTAL_ALIGNMENT = "left"
SOURCE_TEXT_VERTICAL_ALIGNMENT = "top"

SIDE1_TEXT_RECT = (311, 181, 351, 199)
NEUTRAL_TEXT_RECT = (382, 181, 422, 199)
SIDE0_TEXT_RECT = (454, 181, 494, 199)


class PossessionFiguresError(ValueError):
    pass


@dataclass(frozen=True)
class PossessionFigureText:
    source_byte_offset: int
    accessor_va: int
    percent: int
    text: str
    rect: tuple[int, int, int, int]
    side_index: int | None


def _percent(value: int, *, label: str) -> int:
    if type(value) is not int or not 0 <= value <= 100:
        raise PossessionFiguresError(
            f"{label} must be an integer percentage in 0..100"
        )
    return value


def possession_figures_text_layout(
    side0_percent: int,
    neutral_percent: int,
) -> tuple[PossessionFigureText, PossessionFigureText, PossessionFigureText]:
    """Return source-indexed text and exact rectangles for one possession row."""
    side0 = _percent(side0_percent, label="side0_percent")
    neutral = _percent(neutral_percent, label="neutral_percent")
    side1 = 100 - side0 - neutral
    if not 0 <= side1 <= 100:
        raise PossessionFiguresError(
            "side0_percent + neutral_percent must leave side1 in 0..100"
        )
    return (
        PossessionFigureText(
            0x0F, 0x51A720, side1, f"{side1}%", SIDE1_TEXT_RECT, 1
        ),
        PossessionFigureText(
            0x0E, 0x51A710, neutral, f"{neutral}%", NEUTRAL_TEXT_RECT, None
        ),
        PossessionFigureText(
            0x0D, 0x51A700, side0, f"{side0}%", SIDE0_TEXT_RECT, 0
        ),
    )
