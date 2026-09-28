"""Recovered concession-offer candidate selection mechanics.

The 25 rules are small executable tuning constants used by 0x5E5230. Original
stadium maps and presentation/resource data are deliberately not embedded here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


@dataclass(frozen=True)
class ConcessionCandidateRule:
    family: int
    tier: int
    value_min: int
    value_max: int
    local_min: int
    local_max: int
    capacity_min: int
    capacity_max: int


CONCESSION_CANDIDATE_RULES = (
    ConcessionCandidateRule(2, 1, 1000, 1400, 1, 1, 1, 4),
    ConcessionCandidateRule(3, 2, 1000, 1400, 1, 1, 1, 5),
    ConcessionCandidateRule(3, 3, 1000, 1500, 2, 3, 1, 8),
    ConcessionCandidateRule(3, 4, 1000, 1600, 2, 3, 1, 6),
    ConcessionCandidateRule(4, 5, 1000, 1650, 3, 3, 1, 7),
    ConcessionCandidateRule(2, 1, 1200, 1400, 1, 1, 2, 10),
    ConcessionCandidateRule(3, 2, 1100, 1450, 1, 2, 2, 12),
    ConcessionCandidateRule(3, 3, 1200, 1500, 2, 3, 2, 10),
    ConcessionCandidateRule(3, 4, 1100, 1560, 3, 3, 2, 15),
    ConcessionCandidateRule(4, 5, 1200, 1650, 3, 3, 2, 10),
    ConcessionCandidateRule(2, 1, 1100, 1200, 1, 2, 5, 15),
    ConcessionCandidateRule(3, 2, 1200, 1300, 2, 2, 5, 13),
    ConcessionCandidateRule(3, 3, 1200, 1250, 2, 2, 5, 15),
    ConcessionCandidateRule(3, 4, 1200, 1300, 2, 3, 5, 18),
    ConcessionCandidateRule(4, 5, 1200, 1350, 3, 3, 5, 24),
    ConcessionCandidateRule(2, 1, 850, 1200, 2, 2, 10, 30),
    ConcessionCandidateRule(3, 2, 950, 1200, 2, 2, 10, 35),
    ConcessionCandidateRule(3, 3, 950, 1200, 2, 3, 10, 35),
    ConcessionCandidateRule(3, 4, 950, 1200, 3, 3, 10, 35),
    ConcessionCandidateRule(4, 5, 850, 1300, 3, 4, 10, 40),
    ConcessionCandidateRule(2, 1, 900, 1200, 2, 2, 20, 50),
    ConcessionCandidateRule(3, 2, 900, 1250, 2, 2, 20, 50),
    ConcessionCandidateRule(3, 3, 900, 1350, 2, 3, 20, 50),
    ConcessionCandidateRule(3, 4, 900, 1150, 3, 4, 20, 55),
    ConcessionCandidateRule(4, 5, 900, 1250, 4, 5, 20, 60),
)


def concession_candidate_value(
    rng: BoundedRng,
    *,
    club_metric: int,
    access_metric: int,
    stadium_total: int,
    adjustment_percent: float = 20.0,
) -> int:
    """Reproduce 0x5E5170's RNG(800)+850 adjusted candidate value."""

    stadium_total = int(stadium_total)
    if stadium_total <= 0:
        raise ValueError("stadium_total must be positive")

    base = 850 + int(rng.randbelow(800))
    club_ratio = int(club_metric) // stadium_total
    access_ratio = int(access_metric) // stadium_total
    delta = club_ratio - access_ratio
    half_club_ratio = club_ratio // 2
    adjustment = int(float(base) * 0.01 * float(adjustment_percent))
    if delta < half_club_ratio:
        return base + adjustment
    return base - adjustment


def select_fresh_concession_candidate(
    rng: BoundedRng,
    *,
    capacity: int,
    candidate_value: int,
    max_attempts: int = 25,
) -> tuple[int | None, int]:
    """Reproduce the fresh-empty-list 0x5E5230 selector.

    The original duplicate-name predicate is always successful while the active
    concession list is empty, so this clean slice checks only the two numeric
    rule ranges. Returns (candidate_index, RNG_draw_count).
    """

    capacity = int(capacity)
    candidate_value = int(candidate_value)
    draws = 0
    for _ in range(int(max_attempts)):
        index = int(rng.randbelow(25))
        draws += 1
        rule = CONCESSION_CANDIDATE_RULES[index]
        if not rule.capacity_min <= capacity <= rule.capacity_max:
            continue
        if not rule.value_min <= candidate_value <= rule.value_max:
            continue
        return index, draws
    return None, draws


def choose_concession_local_value(rng: BoundedRng, candidate_index: int) -> tuple[int, int]:
    """Reproduce candidate-local +0x10/+0x14 range selection at 0x5E5495."""

    rule = CONCESSION_CANDIDATE_RULES[int(candidate_index)]
    if rule.local_min == rule.local_max:
        return rule.local_min, 0
    return (
        rule.local_min + int(rng.randbelow(rule.local_max - rule.local_min)),
        1,
    )
