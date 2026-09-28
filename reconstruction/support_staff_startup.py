"""Fresh support-staff startup RNG primitives recovered from FOOTBAL.EXE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


@dataclass(frozen=True)
class GeneratedSupportStaff:
    pool_index: int
    staff_type: int
    age_like: int
    rating: int


@dataclass(frozen=True)
class CandidateRebuildResult:
    candidate_pool_indices: tuple[int, ...]
    pruned_pool_indices: tuple[int, ...]
    selected_pool_indices: tuple[int, ...]
    attempt_count: int
    draw_count: int
    state_after: int | None


def _rng_state(rng: BoundedRng) -> int | None:
    state = getattr(rng, "state", None)
    return None if state is None else int(state) & 0xFFFFFFFF


def generate_fresh_support_staff_pool(
    rng: BoundedRng,
    count: int = 200,
) -> tuple[GeneratedSupportStaff, ...]:
    """Reproduce fresh generic CSupportStaff generator 0x4C98B0."""
    result: list[GeneratedSupportStaff] = []
    for pool_index in range(int(count)):
        age_like = int(rng.randbelow(25)) + 25
        if age_like <= 30:
            base_rating = 1
        elif age_like <= 40:
            base_rating = 2
        else:
            base_rating = 3

        rating = base_rating + int(rng.randbelow(4)) - 1
        rating = max(1, min(5, rating))
        staff_type = int(rng.randbelow(16)) + 1
        result.append(
            GeneratedSupportStaff(
                pool_index=pool_index,
                staff_type=staff_type,
                age_like=age_like,
                rating=rating,
            )
        )
    return tuple(result)


def rebuild_support_staff_candidates(
    rng: BoundedRng,
    pool: tuple[GeneratedSupportStaff, ...],
    candidate_pool_indices: tuple[int, ...] = (),
) -> CandidateRebuildResult:
    """Reproduce the RNG-bearing candidate-list core of 0x4C9E90."""
    candidates = list(int(value) for value in candidate_pool_indices)
    pruned: list[int] = []
    selected: list[int] = []
    draw_count = 0

    def draw(bound: int) -> int:
        nonlocal draw_count
        draw_count += 1
        return int(rng.randbelow(bound))

    # The original increments its logical list index even after removal.
    index = 0
    while index < len(candidates):
        if draw(5) == 1:
            pruned.append(candidates.pop(index))
        index += 1

    attempts = 0
    if len(candidates) < 15:
        attempts = draw(18 - len(candidates)) + 2
        for _ in range(attempts):
            pool_index = draw(len(pool))
            selected.append(pool_index)
            # Fresh 0x4C98B0 records always have type 1..16, so the
            # type-zero RNG(16) repair branch cannot run here.
            if pool_index not in candidates:
                candidates.append(pool_index)

    return CandidateRebuildResult(
        candidate_pool_indices=tuple(candidates),
        pruned_pool_indices=tuple(pruned),
        selected_pool_indices=tuple(selected),
        attempt_count=attempts,
        draw_count=draw_count,
        state_after=_rng_state(rng),
    )
