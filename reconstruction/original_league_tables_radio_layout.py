"""Source-derived original PLeagueTables radio rectangles, NOT accepted clicks.

The 0x448640/0x446F00 panel and 0x5D4C70 native fmRadioTextSm source
establish construction geometry. Clipped child hit ownership, actual mouse
acceptance and rendering are deliberately not inferred from rectangles.
"""
from __future__ import annotations

from dataclasses import dataclass

COUNTRY_COUNT = 8
DIVISION_CAPACITY = 5
SORT_COUNT = 2
RADIO_X = 27
RADIO_WIDTH = 182
RADIO_HEIGHT = 18
RADIO_VERTICAL_STEP = 20
COUNTRY_START_Y = 172
DIVISION_START_Y = 361
SORT_START_Y = 490


@dataclass(frozen=True)
class OriginalLeagueTablesRadioRect:
    family: str
    index: int
    event_id: int
    rect: tuple[int, int, int, int]


def original_league_tables_radio_rects(
    *, division_option_count: int,
) -> tuple[OriginalLeagueTablesRadioRect, ...]:
    """Construct original candidates while suppressing unconstructed divisions."""
    if (type(division_option_count) is not int
            or not 1 <= division_option_count <= DIVISION_CAPACITY):
        raise ValueError(
            "Original PLeagueTables requires 1..5 source-qualified visible divisions"
        )
    return tuple(
        OriginalLeagueTablesRadioRect(
            "country", i, i + 1,
            (RADIO_X, COUNTRY_START_Y + i * RADIO_VERTICAL_STEP,
             RADIO_WIDTH, RADIO_HEIGHT),
        )
        for i in range(COUNTRY_COUNT)
    ) + tuple(
        OriginalLeagueTablesRadioRect(
            "division", i, i + 9,
            (RADIO_X, DIVISION_START_Y + i * RADIO_VERTICAL_STEP,
             RADIO_WIDTH, RADIO_HEIGHT),
        )
        for i in range(division_option_count)
    ) + tuple(
        OriginalLeagueTablesRadioRect(
            "sort", i, i + 14,
            (RADIO_X, SORT_START_Y + i * RADIO_VERTICAL_STEP,
             RADIO_WIDTH, RADIO_HEIGHT),
        )
        for i in range(SORT_COUNT)
    )


def original_league_tables_radio_candidate_at_point(
    x: int, y: int, *, division_option_count: int,
) -> OriginalLeagueTablesRadioRect | None:
    """Geometry candidate only; NOT a native mouse-event authorization."""
    if type(x) is not int or type(y) is not int:
        raise ValueError("Original radio pointer coordinates must be integers")
    for radio in original_league_tables_radio_rects(
        division_option_count=division_option_count,
    ):
        left, top, width, height = radio.rect
        if left <= x < left + width and top <= y < top + height:
            return radio
    return None
