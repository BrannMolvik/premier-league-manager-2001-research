from __future__ import annotations

from dataclasses import dataclass

from match_events import BoundaryType


NORMAL_FIRST_HALF_SEGMENTS = (5, 10, 15, 20, 25, 30, 35, 40)
NORMAL_SECOND_HALF_SEGMENTS = (50, 55, 60, 65, 70, 75, 80, 85)
EXTRA_TIME_FIRST_HALF_SEGMENTS = (95, 100)
EXTRA_TIME_SECOND_HALF_SEGMENTS = (110, 115)


@dataclass(frozen=True)
class TimedBoundary:
    minute: int
    kind: BoundaryType


@dataclass(frozen=True)
class MatchPhasePlan:
    segment_minutes: tuple[int, ...]
    boundaries: tuple[TimedBoundary, ...]
    final_record_minute: int


def build_match_phase_plan(extra_time: bool = False, penalties: bool = False) -> MatchPhasePlan:
    """Reproduce the verified 0x62AE90 match-clock scaffold.

    Upstream competition/tie rules decide whether extra time or penalties are
    required; this function reproduces the original timeline once decided.
    """
    segments = list(NORMAL_FIRST_HALF_SEGMENTS)
    boundaries = [TimedBoundary(45, BoundaryType.HALF_TIME)]
    segments.extend(NORMAL_SECOND_HALF_SEGMENTS)

    if extra_time:
        boundaries.append(TimedBoundary(90, BoundaryType.EXTRA_TIME))
        segments.extend(EXTRA_TIME_FIRST_HALF_SEGMENTS)
        boundaries.append(TimedBoundary(105, BoundaryType.EXTRA_TIME))
        segments.extend(EXTRA_TIME_SECOND_HALF_SEGMENTS)

    if penalties:
        boundaries.append(TimedBoundary(120 if extra_time else 90, BoundaryType.PENALTIES))
        final_minute = 130
    else:
        final_minute = 120 if extra_time else 90

    boundaries.append(TimedBoundary(final_minute, BoundaryType.FULL_TIME))
    return MatchPhasePlan(tuple(segments), tuple(boundaries), final_minute)
