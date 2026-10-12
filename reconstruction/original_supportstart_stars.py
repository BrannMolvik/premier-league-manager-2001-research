"""Byte-verified original FM2001 PSupportStart cumulative star-strip selector.

Original EXE 0x4C97D0 selects one of five 0x64E500 crop wrappers.
The common source is FM2001_Art/Support/stars.444 (75x10).
This does not prove native input, mouse hit areas, or GUI acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass

STAR_RESOURCE = "FM2001_Art/Support/stars.444"
STAR_SOURCE_SIZE = (75, 10)
STAR_WRAPPERS = (0x945890, 0x945850, 0x945810, 0x9457D0, 0x945790)


@dataclass(frozen=True)
class OriginalSupportStartStarFrame:
    wrapper_va: int
    source_path: str
    crop_left_top_right_bottom: tuple[int, int, int, int]


def original_supportstart_star_frame(state: int) -> OriginalSupportStartStarFrame | None:
    """Return original source crop; native 0x4C97D0 returns NULL outside 1..5."""
    if type(state) is not int:
        raise TypeError("expected integer source state")
    if state < 1 or state > 5:
        return None
    return OriginalSupportStartStarFrame(
        STAR_WRAPPERS[state - 1], STAR_RESOURCE, (0, 0, 15 * state, 10)
    )


def original_supportstart_star_local_rect(row: int, state: int) -> tuple[int, int, int, int]:
    """Native 0x4C9510 -> 0x651BA0 -> 0x64F380 child bounds (x,y,w,h).

    This is a native-layout child rectangle, NOT verified screen-space hit
    geometry or a claim about parent GUI transforms. The seven calls to
    0x4C9510 use row origins (391,181+40*i); the sprite child is positioned
    at x+0xE6, y+4, and NULL sprite width/height are both zero.
    """
    if type(row) is not int or not 0 <= row < 7:
        raise ValueError("source row must be an integer from 0 through 6")
    frame = original_supportstart_star_frame(state)
    return (621, 185 + 40 * row, 0 if frame is None else 15 * state,
            0 if frame is None else 10)
