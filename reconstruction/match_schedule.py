"""Exact schedule-order primitives recovered from FOOTBAL.EXE.

This module contains no game data.  It preserves the original MSVC CRT
pseudo-random generator and the per-date linked-list shuffle used by the
schedule container.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol, TypeVar


T = TypeVar("T")


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


@dataclass
class MsvcCrtRng:
    """MSVC CRT rand()/srand() state used by the analyzed FM2001 release."""

    state: int

    def __post_init__(self) -> None:
        self.state &= 0xFFFFFFFF

    def seed(self, value: int) -> None:
        self.state = int(value) & 0xFFFFFFFF

    def rand15(self) -> int:
        self.state = (self.state * 0x343FD + 0x269EC3) & 0xFFFFFFFF
        return (self.state >> 16) & 0x7FFF

    def randbelow(self, bound: int) -> int:
        """Reproduce 0x64D540 for a positive bound.

        FOOTBAL.EXE computes floor(rand15 * bound / 32768).  Integer
        arithmetic is equivalent for the positive schedule/list counts used
        by the original routine and avoids introducing host-FPU differences.
        """
        bound = int(bound)
        if bound <= 0:
            raise ValueError("bound must be positive")
        return (self.rand15() * bound) // 32768


def schedule_bucket_pre_shuffle_order(insertion_order: Iterable[T]) -> tuple[T, ...]:
    """Return the linked-list order produced by 0x615950 head insertion."""

    return tuple(reversed(tuple(insertion_order)))


def shuffle_schedule_bucket(items: Iterable[T], rng: BoundedRng) -> tuple[T, ...]:
    """Reproduce the 0x615AE0 descending Fisher-Yates shuffle.

    For N entries the exact RNG bound sequence is N, N-1, ..., 2.
    The executable copies the current linked-list order to an array, performs
    these swaps, then rewires the linked list in the shuffled array order.
    """

    shuffled = list(items)
    for remaining in range(len(shuffled), 1, -1):
        selected = rng.randbelow(remaining)
        last = remaining - 1
        shuffled[selected], shuffled[last] = shuffled[last], shuffled[selected]
    return tuple(shuffled)


def build_and_shuffle_schedule_bucket(
    insertion_order: Iterable[T],
    rng: BoundedRng,
) -> tuple[T, ...]:
    """Compose exact head insertion with the later per-bucket shuffle."""

    return shuffle_schedule_bucket(
        schedule_bucket_pre_shuffle_order(insertion_order),
        rng,
    )
