"""Original PLeagueFixtures native radio control geometry, source qualified.

This is a SOURCE RECTANGLE and candidate-point projection, not proof of the
fmRadioTextSm child hit-test callback, displayed captions or host click route.
The actual user input path remains fail-closed until those dependencies and a
fully qualified selected competition data provider are integrated.
"""
from __future__ import annotations

from dataclasses import dataclass

COUNTRY_COUNT = 8
LEAGUE_CAPACITY = 6
RADIO_X = 27
RADIO_WIDTH = 182
RADIO_HEIGHT = 18
RADIO_VERTICAL_STEP = 20
COUNTRY_START_Y = 256
LEAGUE_START_Y = 445


@dataclass(frozen=True)
class OriginalLeagueFixturesRadioRect:
    family: str
    index: int
    event_id: int
    rect: tuple[int, int, int, int]


def original_league_fixtures_radio_rects(*, league_option_count: int) -> tuple[OriginalLeagueFixturesRadioRect, ...]:
    """Return constructed native candidate rects, suppressing absent League radios."""
    if type(league_option_count) is not int or not 1 <= league_option_count <= LEAGUE_CAPACITY:
        raise ValueError("Original PLeagueFixtures requires 1..6 qualified visible League options")
    return tuple(
        OriginalLeagueFixturesRadioRect(
            "country", i, i + 1,
            (RADIO_X, COUNTRY_START_Y + i * RADIO_VERTICAL_STEP, RADIO_WIDTH, RADIO_HEIGHT),
        )
        for i in range(COUNTRY_COUNT)
    ) + tuple(
        OriginalLeagueFixturesRadioRect(
            "league", i, i + 9,
            (RADIO_X, LEAGUE_START_Y + i * RADIO_VERTICAL_STEP, RADIO_WIDTH, RADIO_HEIGHT),
        )
        for i in range(league_option_count)
    )


def original_league_fixtures_radio_candidate_at_point(
    x: int, y: int, *, league_option_count: int,
) -> OriginalLeagueFixturesRadioRect | None:
    """Find a containing source rectangle; not an authorized native click event."""
    if type(x) is not int or type(y) is not int:
        raise ValueError("Native pointer coordinates must be integers")
    for radio in original_league_fixtures_radio_rects(league_option_count=league_option_count):
        left, top, width, height = radio.rect
        if left <= x < left + width and top <= y < top + height:
            return radio
    return None
