"""Exact schedule-order primitives recovered from FOOTBAL.EXE.

This module contains no game data.  It preserves the original MSVC CRT
pseudo-random generator and the per-date linked-list shuffle used by the
schedule container.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence, TypeVar


T = TypeVar("T")


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class OrdinaryLeagueMatchSource(Protocol):
    home_club_id: int
    away_club_id: int


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



def ordinary_league_matches_conflict(
    existing: OrdinaryLeagueMatchSource,
    candidate: OrdinaryLeagueMatchSource,
) -> bool:
    """Reproduce the ordinary LeagueMatch team-overlap test beneath 0x615790.

    This intentionally models the normal unflagged LeagueMatch path only.
    0x615790 has additional generic-node flag checks before it dispatches the
    virtual overlap predicate; fixed/procedural ordinary LeagueMatch nodes
    enter with those skip flags clear.
    """
    existing_teams = {
        int(existing.home_club_id),
        int(existing.away_club_id),
    }
    return (
        int(candidate.home_club_id) in existing_teams
        or int(candidate.away_club_id) in existing_teams
    )


def first_ordinary_league_conflict_near(
    buckets: Sequence[Sequence[OrdinaryLeagueMatchSource]],
    center_index: int,
    candidate: OrdinaryLeagueMatchSource,
) -> int | None:
    """Reproduce 0x615890 for ordinary unflagged LeagueMatch nodes.

    The executable scans bucket center-1, center and center+1, clipped at the
    container ends, and returns the first bucket whose existing normal match
    shares either club with the candidate.
    """
    center_index = int(center_index)
    bucket_count = len(buckets)
    if not 0 <= center_index < bucket_count:
        raise ValueError("center_index must reference an existing schedule bucket")

    start = center_index - 1 if center_index != 0 else 0
    stop = min(center_index + 2, bucket_count)
    for bucket_index in range(start, stop):
        if any(
            ordinary_league_matches_conflict(existing, candidate)
            for existing in buckets[bucket_index]
        ):
            return bucket_index
    return None


def choose_ordinary_league_schedule_bucket(
    buckets: Sequence[Sequence[OrdinaryLeagueMatchSource]],
    nominal_index: int,
    candidate: OrdinaryLeagueMatchSource,
) -> int:
    """Reproduce the 0x615950 conflict-search placement for LeagueMatch.

    If the nominal day or either adjacent day already contains an ordinary
    match sharing a club, the original searches outward in two-day jumps.
    It probes the side closer to the nominal target; on an equal-distance tie
    it probes the later side first.

    The original code assumes schedule targets far enough from the container
    edges for its outward probes. Raise rather than silently invent behavior if
    a synthetic caller violates that invariant.
    """
    nominal_index = int(nominal_index)
    bucket_count = len(buckets)
    if not 0 <= nominal_index < bucket_count:
        raise ValueError("nominal_index must reference an existing schedule bucket")

    conflict = first_ordinary_league_conflict_near(
        buckets,
        nominal_index,
        candidate,
    )
    if conflict is None:
        return nominal_index

    lower = conflict - 2
    upper = conflict + 2

    while True:
        lower_distance = nominal_index - lower
        upper_distance = upper - nominal_index

        # Exact 0x6159D1 branch: the lower side wins only when strictly
        # closer. A tie falls through to the later/upper side.
        if (
            lower_distance < upper_distance
            and lower != 0
            and upper < bucket_count
        ):
            if not 0 <= lower < bucket_count:
                raise ValueError(
                    "original lower conflict-search probe escaped schedule bounds"
                )
            conflict = first_ordinary_league_conflict_near(
                buckets,
                lower,
                candidate,
            )
            if conflict is None:
                return lower
            lower = conflict - 2
            continue

        if not 0 <= upper < bucket_count:
            raise ValueError(
                "original upper conflict-search probe escaped schedule bounds"
            )
        conflict = first_ordinary_league_conflict_near(
            buckets,
            upper,
            candidate,
        )
        if conflict is None:
            return upper
        upper = conflict + 2


def insert_ordinary_league_match(
    buckets: list[list[T]],
    nominal_index: int,
    candidate: T,
) -> int:
    """Place then head-insert one ordinary LeagueMatch as 0x615950 does."""
    chosen = choose_ordinary_league_schedule_bucket(
        buckets,
        nominal_index,
        candidate,
    )
    buckets[chosen].insert(0, candidate)
    return chosen
