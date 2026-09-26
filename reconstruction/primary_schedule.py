"""Exact primary schedule-container placement and shuffle primitives.

Recovered from FOOTBAL.EXE:
- primary container constructor 0x615670 -> 0x615700 creates 373 buckets;
- 0x615950 maps a round date to a nominal bucket, performs the 0x615890
  three-bucket conflict probe / outward two-day search, then head-inserts;
- 0x615BE0 walks buckets from index 0 upward and calls 0x615AE0;
- 0x615AE0 copies the current linked-list order, applies descending
  Fisher-Yates, and rewires the linked list in the shuffled array order;
- 0x615C10 later traverses the bucket linked list head-to-tail.

The primary FM2001 season has one explicit Christmas-Day skip inside 0x615950.
For the canonical 2000/01 primary schedule, week 26 / weekday 1 maps to
Christmas Day and is advanced by one bucket before conflict placement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from competition_schedule import StartupScheduleNode, schedule_nodes_conflict
from match_schedule import BoundedRng, shuffle_schedule_bucket


PRIMARY_SCHEDULE_BUCKET_COUNT = 373
PRIMARY_SCHEDULE_BASE_OFFSET = -1
PRIMARY_CHRISTMAS_WEEK = 26
PRIMARY_CHRISTMAS_WEEKDAY = 1


@dataclass(frozen=True)
class PrimarySchedulePlacement:
    """Primary-container state immediately before 0x615BE0."""

    buckets: tuple[tuple[StartupScheduleNode, ...], ...]
    nominal_bucket_indices: tuple[int, ...]
    chosen_bucket_indices: tuple[int, ...]

    @property
    def node_count(self) -> int:
        return sum(len(bucket) for bucket in self.buckets)


@dataclass(frozen=True)
class PrimaryScheduleShuffle:
    """Primary-container state immediately after 0x615BE0."""

    buckets: tuple[tuple[StartupScheduleNode, ...], ...]
    draw_count: int
    state_after: int | None

    @property
    def node_count(self) -> int:
        return sum(len(bucket) for bucket in self.buckets)


def nominal_primary_schedule_bucket(
    scheduled_week: int,
    scheduled_weekday: int,
) -> int:
    """Reproduce the primary 0x615950 nominal bucket calculation.

    0x615950 computes:

        7 * week + weekday + container.offset

    and primary ScheduleContainer construction initializes offset to -1.
    The function then constructs the corresponding calendar date and advances
    one bucket when that date is 25 December. In the canonical 2000/01
    primary schedule that date is week 26 / weekday 1.
    """

    week = int(scheduled_week)
    weekday = int(scheduled_weekday)
    if weekday < 1 or weekday > 7:
        raise ValueError("scheduled_weekday must be in 1..7")

    bucket = 7 * week + weekday + PRIMARY_SCHEDULE_BASE_OFFSET
    if (
        week == PRIMARY_CHRISTMAS_WEEK
        and weekday == PRIMARY_CHRISTMAS_WEEKDAY
    ):
        bucket += 1
    return bucket


def _first_schedule_node_conflict_near(
    buckets: list[list[StartupScheduleNode]],
    center_index: int,
    candidate: StartupScheduleNode,
) -> int | None:
    """Reproduce 0x615890 for startup schedule nodes."""

    center = int(center_index)
    bucket_count = len(buckets)
    if not 0 <= center < bucket_count:
        raise ValueError("center_index must reference an existing schedule bucket")

    start = center - 1 if center != 0 else 0
    stop = min(center + 2, bucket_count)
    for bucket_index in range(start, stop):
        for existing in buckets[bucket_index]:
            if schedule_nodes_conflict(existing, candidate):
                return bucket_index
    return None


def choose_primary_schedule_bucket(
    buckets: list[list[StartupScheduleNode]],
    nominal_index: int,
    candidate: StartupScheduleNode,
) -> int:
    """Reproduce 0x615950's outward conflict-search placement.

    The initial probe covers nominal-1, nominal, nominal+1. After a conflict,
    the search expands in two-bucket jumps. The side closer to the original
    nominal target is tested first; exact-distance ties choose the later side,
    matching the branch at 0x6159D1.
    """

    nominal = int(nominal_index)
    bucket_count = len(buckets)
    if not 0 <= nominal < bucket_count:
        raise ValueError("nominal_index must reference an existing schedule bucket")

    conflict = _first_schedule_node_conflict_near(
        buckets,
        nominal,
        candidate,
    )
    if conflict is None:
        return nominal

    lower = conflict - 2
    upper = conflict + 2

    while True:
        lower_distance = nominal - lower
        upper_distance = upper - nominal

        if (
            lower_distance < upper_distance
            and lower != 0
            and upper < bucket_count
        ):
            if not 0 <= lower < bucket_count:
                raise ValueError(
                    "original lower conflict-search probe escaped schedule bounds"
                )
            conflict = _first_schedule_node_conflict_near(
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
        conflict = _first_schedule_node_conflict_near(
            buckets,
            upper,
            candidate,
        )
        if conflict is None:
            return upper
        upper = conflict + 2


def place_primary_schedule_nodes(
    nodes: Iterable[StartupScheduleNode],
    *,
    bucket_count: int = PRIMARY_SCHEDULE_BUCKET_COUNT,
) -> PrimarySchedulePlacement:
    """Place startup nodes through exact primary 0x615950 semantics.

    Nodes must be supplied in original construction/insertion order. Each
    accepted node is head-inserted into its chosen bucket, so the returned
    bucket tuples are already in the linked-list order seen by 0x615AE0.
    """

    bucket_count = int(bucket_count)
    if bucket_count <= 0:
        raise ValueError("bucket_count must be positive")

    buckets: list[list[StartupScheduleNode]] = [
        [] for _ in range(bucket_count)
    ]
    nominal_indices: list[int] = []
    chosen_indices: list[int] = []

    for node in nodes:
        if node.scheduled_week is None or node.scheduled_weekday is None:
            raise ValueError("primary schedule node has no startup date")

        nominal = nominal_primary_schedule_bucket(
            int(node.scheduled_week),
            int(node.scheduled_weekday),
        )
        if not 0 <= nominal < bucket_count:
            raise ValueError(
                f"primary schedule nominal bucket {nominal} is outside "
                f"0..{bucket_count - 1}"
            )

        chosen = choose_primary_schedule_bucket(
            buckets,
            nominal,
            node,
        )
        buckets[chosen].insert(0, node)
        nominal_indices.append(nominal)
        chosen_indices.append(chosen)

    return PrimarySchedulePlacement(
        buckets=tuple(tuple(bucket) for bucket in buckets),
        nominal_bucket_indices=tuple(nominal_indices),
        chosen_bucket_indices=tuple(chosen_indices),
    )


def shuffle_primary_schedule_buckets(
    buckets: Iterable[Iterable[StartupScheduleNode]],
    rng: BoundedRng,
) -> PrimaryScheduleShuffle:
    """Reproduce 0x615BE0 -> 0x615AE0 across the primary container."""

    bucket_list = tuple(tuple(bucket) for bucket in buckets)
    shuffled: list[tuple[StartupScheduleNode, ...]] = []
    draw_count = 0

    for bucket in bucket_list:
        draw_count += max(0, len(bucket) - 1)
        shuffled.append(shuffle_schedule_bucket(bucket, rng))

    state = getattr(rng, "state", None)
    return PrimaryScheduleShuffle(
        buckets=tuple(shuffled),
        draw_count=draw_count,
        state_after=None if state is None else int(state) & 0xFFFFFFFF,
    )
