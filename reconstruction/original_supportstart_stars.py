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
