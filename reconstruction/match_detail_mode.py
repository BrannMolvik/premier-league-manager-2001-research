"""Source-backed FM2001 pre-match Match Detail selection contract.

The shipped PPreMatchPanel writes one of four user selections to native global
0x877530. Normal match processing routes value 2 through FastViewPanel, values
0/1 through the sibling 3D wrapper, and value 3 through Quick Match with no
presentation wrapper.

The native settings object initially uses sentinel value 5 before persisted
settings/default resolution. The modern port represents that unresolved state
as None rather than exposing 5 as a selectable Match Detail mode.
"""
from __future__ import annotations

from enum import IntEnum


NATIVE_MATCH_DETAIL_GLOBAL_VA = 0x877530
NATIVE_UNRESOLVED_SENTINEL = 5


class MatchDetailMode(IntEnum):
    THREE_D_MATCH = 0
    THREE_D_HIGHLIGHTS = 1
    FASTVIEW = 2
    QUICK_MATCH = 3


MATCH_DETAIL_LABELS = {
    MatchDetailMode.THREE_D_MATCH: "3D Match",
    MatchDetailMode.THREE_D_HIGHLIGHTS: "3D Highlights",
    MatchDetailMode.FASTVIEW: "FastView",
    MatchDetailMode.QUICK_MATCH: "Quick Match",
}


def coerce_match_detail_mode(value: int | MatchDetailMode) -> MatchDetailMode:
    """Validate an exact selectable native Match Detail value."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Match Detail mode must be an integer value 0..3")
    try:
        mode = MatchDetailMode(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Match Detail mode must be an integer value 0..3") from exc
    return mode


def match_detail_label(value: int | MatchDetailMode) -> str:
    return MATCH_DETAIL_LABELS[coerce_match_detail_mode(value)]


def source_selects_fastview(
    value: int | MatchDetailMode | None,
) -> bool:
    """Return true only for the source-proven FastView selection.

    None intentionally represents the unresolved/native-sentinel state and
    never promotes a presentation route.
    """
    if value is None:
        return False
    return coerce_match_detail_mode(value) is MatchDetailMode.FASTVIEW
