"""Exact FM2001 MatchCalculator target performance-rating primitive.

This module reconstructs the integer target written to participant record +0x30
by FOOTBAL.EXE 0x6309D0. It deliberately keeps the two original random streams
separate: most adjustments use the shared MSVC CRT bounded RNG, while the
low-rating lift uses the MatchEngine separate 0x981BF0 / 0x64D5B0 generator.

The later 24-step FastView trajectory is not part of this primitive.
"""

from __future__ import annotations

from typing import Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


def target_match_performance_rating(
    *,
    current_role: int,
    own_score: int,
    opponent_score: int,
    primary_goal_count: int,
    secondary_goal_count: int,
    booked: bool,
    sent_off: bool,
    form_state: int,
    previous_rating: int,
    shared_rng: BoundedRng,
    match_engine_rng: BoundedRng,
) -> int:
    """Reproduce the target byte written at MatchCalculator participant +0x30.

    primary_goal_count is participant +0x40 and is the primary goal-family
    attribution counter (ordinary scorer/finisher on the mapped goal records).
    secondary_goal_count is participant +0x44 and remains neutrally named
    because not every goal-family source has yet proven a universal assist
    meaning for that raw secondary player slot.

    previous_rating is the value returned by DBRPlayer::0x41FA20. Callers
    should pass zero when the original history-availability guard does not
    expose a prior rating.
    """

    role = int(current_role)
    own = max(0, int(own_score))
    opponent = max(0, int(opponent_score))
    primary = max(0, int(primary_goal_count))
    secondary = max(0, int(secondary_goal_count))
    form = int(form_state)
    previous = max(0, int(previous_rating))

    if role < 0:
        raise ValueError("current_role must be non-negative")

    if 8 <= role <= 15:
        if primary > 0:
            rating = 8 + primary // 2
        else:
            rating = 6
            if own > opponent:
                rating += int(shared_rng.randbelow(2))
        rating -= opponent // 2
    elif role >= 16:
        if primary > 0:
            rating = 8 + primary // 2
        else:
            rating = 6
            if own > opponent:
                rating += int(shared_rng.randbelow(2))
        rating -= opponent // 3
    else:
        rating = (
            7
            + int(shared_rng.randbelow(2))
            + (primary + 1) // 2
            - (opponent + 1) // 2
        )

    if secondary == 1:
        rating += int(shared_rng.randbelow(2))
    else:
        rating += secondary // 2

    if bool(sent_off):
        rating -= 1
    elif bool(booked):
        rating -= int(shared_rng.randbelow(2))

    if form == 0:
        rating -= 1
    elif form == 1:
        rating -= int(shared_rng.randbelow(2))
    elif form == 3:
        rating += int(shared_rng.randbelow(2))
    elif form == 4:
        rating += 1

    # Exact non-monotonic clamp sequence: exactly 10 becomes 9, while
    # values above 10 are capped to 10.
    if rating == 10:
        rating = 9
    elif rating > 10:
        rating = 10
    elif rating < 4:
        rating = 4

    if rating < 6:
        rating += int(match_engine_rng.randbelow(7 - rating))

    if previous > 0:
        if previous > rating + 1:
            rating += 1
        elif previous < rating - 1:
            rating -= 1

    return int(rating)
