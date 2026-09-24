from __future__ import annotations

from typing import Sequence

from match_calculator import position_compatibility_multiplier


# Exact 0x41C7E0 role-weight terms in executable evaluation order.
# Each tuple contains (canonical 17-skill index, weight).
ROLE_SKILL_WEIGHTS: dict[int, tuple[tuple[int, float], ...]] = {
    1: ((1, .3), (14, .4), (0, .2), (5, .1), (11, .7), (12, .7), (13, .9)),
    2: ((1, .3), (14, .5), (0, .5), (8, .4), (6, .1), (5, .6), (7, .9)),
    3: ((1, .3), (14, .5), (0, .5), (8, .4), (6, .1), (5, .6), (7, .9)),
    4: ((1, .3), (14, .5), (0, .5), (8, .6), (6, .1), (5, .4), (7, .9)),
    5: ((1, .3), (14, .4), (0, .5), (8, .3), (6, .2), (5, .7), (7, .9)),
    6: ((1, .3), (14, .4), (0, .6), (8, .2), (6, .3), (5, .7), (7, .8)),
    7: ((1, .3), (14, .4), (0, .6), (8, .2), (6, .3), (5, .7), (7, .8)),
    8: ((1, .3), (14, .4), (0, .4), (8, .5), (6, .2), (5, .6), (7, .9)),
    9: ((1, .3), (14, .3), (0, .3), (8, .5), (6, .3), (5, .9), (7, .7)),
    10: ((1, .3), (14, .3), (0, .4), (8, .5), (6, .3), (5, .9), (7, .6)),
    11: ((1, .3), (14, .3), (0, .4), (8, .5), (6, .3), (5, .9), (7, .6)),
    12: ((1, .3), (14, .3), (0, .4), (8, .5), (6, .3), (5, .9), (7, .6)),
    13: ((1, .3), (14, .4), (0, .7), (8, .2), (6, .5), (5, .8), (7, .4)),
    14: ((1, .3), (14, .4), (0, .7), (8, .2), (6, .5), (5, .8), (7, .4)),
    15: ((1, .3), (14, .4), (0, .4), (8, .4), (6, .6), (5, .8), (7, .4)),
    18: ((1, .3), (14, .4), (0, .5), (8, .5), (6, .9), (5, .5), (7, .2)),
    19: ((1, .3), (14, .5), (0, .6), (8, .6), (6, .9), (5, .2), (7, .2)),
}


def display_skill(raw_skill: int) -> int:
    """Exact raw-byte to 0..30 conversion used inside 0x41C7E0."""
    raw_skill = int(raw_skill)
    if not 0 <= raw_skill <= 255:
        raise ValueError("raw_skill must be in 0..255")
    return (30 * raw_skill + 128) // 255


def role_rating(
    skills: Sequence[int],
    queried_role: int,
    preferred_positions: Sequence[int],
) -> int:
    """Clean-room implementation of player role-rating helper 0x41C7E0.

    Roles 16 and 17 use the executable's zero branch. Other supported runtime
    roles use seven weighted 0..30 display skills, then the exact positional
    compatibility multiplier, a 99.0 cap, +0.49, and truncation toward zero.
    """
    if len(skills) != 17:
        raise ValueError("skills must contain exactly 17 raw skill bytes")
    if any(not 0 <= int(value) <= 255 for value in skills):
        raise ValueError("skills must be in 0..255")
    if len(preferred_positions) < 3:
        raise ValueError("preferred_positions must contain at least three entries")

    role = int(queried_role)
    if not 1 <= role <= 19:
        return 0

    terms = ROLE_SKILL_WEIGHTS.get(role)
    if terms is None:
        # Runtime roles 16 and 17 both jump to 0x41E118.
        return 0

    weighted = 0.0
    for skill_index, weight in terms:
        weighted += display_skill(skills[skill_index]) * weight

    weighted *= position_compatibility_multiplier(role, preferred_positions)
    weighted = min(weighted, 99.0)

    # 0x668350 truncates toward zero. weighted is non-negative here.
    return int(weighted + 0.49)
