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
For the canonical 2000/01 primary schedule, week 25 / weekday 1 maps to
Christmas Day and is advanced by one bucket before conflict placement.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

from competition_schedule import StartupScheduleNode, schedule_nodes_conflict
from competition_state import season_weekday_date
from match_schedule import BoundedRng, shuffle_schedule_bucket


PRIMARY_SCHEDULE_BUCKET_COUNT = 373
PRIMARY_SCHEDULE_BASE_OFFSET = -1
PRIMARY_CHRISTMAS_WEEK = 25
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


def primary_schedule_source_bucket(
    scheduled_week: int,
    scheduled_weekday: int,
) -> int:
    """Return 0x615950's raw relative day before calendar exceptions."""

    week = int(scheduled_week)
    weekday = int(scheduled_weekday)
    if weekday < 1 or weekday > 7:
        raise ValueError("scheduled_weekday must be in 1..7")
    return 7 * week + weekday + PRIMARY_SCHEDULE_BASE_OFFSET


def nominal_primary_schedule_bucket(
    scheduled_week: int,
    scheduled_weekday: int,
    *,
    season_year: int = 2000,
) -> int:
    """Reproduce the primary 0x615950 nominal bucket calculation.

    0x615950 first computes:

        7 * week + weekday + container.offset

    and primary ScheduleContainer construction initializes offset to -1.
    It then advances one bucket when the corresponding Gregorian calendar date
    is 25 December. In the canonical 2000/01 primary schedule that happens to
    be week 25 / weekday 1; later seasons must derive the slot from the actual
    season-year calendar rather than reuse that first-season coordinate.
    """

    week = int(scheduled_week)
    weekday = int(scheduled_weekday)
    bucket = primary_schedule_source_bucket(week, weekday)
    on_date = season_weekday_date(int(season_year), week, weekday)
    if (on_date.month, on_date.day) == (12, 25):
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
    season_year: int = 2000,
    bucket_count: int = PRIMARY_SCHEDULE_BUCKET_COUNT,
) -> PrimarySchedulePlacement:
    """Place startup nodes through exact primary 0x615950 semantics.

    Nodes must be supplied in original construction/insertion order. Each
    accepted node is head-inserted into its chosen bucket, so the returned
    bucket tuples are already in the linked-list order seen by 0x615AE0.
    season_year is required for the executable's Gregorian 25-December skip;
    its default preserves the shipped 2000/01 startup path.
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
            season_year=int(season_year),
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


def gate12_primary_matchday_order(
    buckets: Iterable[Iterable[StartupScheduleNode]],
    *,
    season_year: int,
    premier_league_competition_id: int = 0,
    domestic_cup_ids: tuple[int, ...] = (1, 5, 11, 12, 13),
    european_cup_ids: tuple[int, ...] = (9, 10),
    qualification_cup_ids: tuple[int, ...] = (19, 23, 33, 91, 98, 101),
    procedural_league_ids: tuple[int, ...] = (14, 167),
) -> tuple[tuple[date, tuple[tuple, ...]], ...]:
    """Retain exact shuffled live Gate-12 interleaving by Gregorian date.

    Bucket index is the primary-container relative day. Now that the mode-0
    calendar anchor is instruction-closed, bucket 0 is the shared week-0
    Monday and each subsequent bucket is one calendar day later. English
    divisional playoffs 11/12/13 share the same generic Cup runtime and are
    tagged with the domestic-Cup execution path. Other competitions remain
    outside this Gate-12 view.
    """
    anchor = season_weekday_date(int(season_year), 0, 1)
    domestic_ids = {int(value) for value in domestic_cup_ids}
    european_ids = {int(value) for value in european_cup_ids}
    qualification_ids = {int(value) for value in qualification_cup_ids}
    procedural_ids = {int(value) for value in procedural_league_ids}
    league_id = int(premier_league_competition_id)
    result: list[tuple[date, tuple[tuple, ...]]] = []

    for bucket_index, bucket in enumerate(buckets):
        entries: list[tuple] = []
        for node in bucket:
            if (
                node.node_kind in ("fixed_league_match", "league_match")
                and int(node.competition_id) == league_id
                and int(node.competition_context) == 0
            ):
                if not node.node_token:
                    raise ValueError("Premier League schedule node has no fixture token")
                entries.append(("premier_league", int(node.node_token[-1])))
                continue

            if (
                int(node.competition_id) in domestic_ids
                and node.node_kind
                in ("cup_match", "first_leg_match", "second_leg_match")
            ):
                entries.append(("domestic_cup", tuple(node.node_token)))
            if (
                int(node.competition_id) in european_ids
                and node.node_kind
                in ("cup_match", "first_leg_match", "second_leg_match")
            ):
                entries.append(("european_cup", tuple(node.node_token)))
            if (
                int(node.competition_id) in qualification_ids
                and node.node_kind
                in ("cup_match", "first_leg_match", "second_leg_match")
            ):
                entries.append(("qualification_cup", tuple(node.node_token)))
            if (
                node.node_kind == "league_match"
                and int(node.competition_id) in procedural_ids
            ):
                entries.append(("procedural_league", tuple(node.node_token)))
                continue


        if entries:
            result.append(
                (
                    anchor + timedelta(days=int(bucket_index)),
                    tuple(entries),
                )
            )
    return tuple(result)


def fixed_league_fixture_order_by_round(
    buckets: Iterable[Iterable[StartupScheduleNode]],
    *,
    competition_id: int = 0,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Extract head-to-tail fixed-League execution order per round.

    0x615C10 walks each shuffled bucket from its linked-list head through +0x04
    next pointers. Scanning buckets in ascending container order and retaining
    that per-bucket order therefore yields the scheduler-visible fixture order.

    The fixed League node token is emitted as
    ("fixed_league_match", competition_id, context, fixture_id).
    """

    competition_id = int(competition_id)
    by_round: dict[int, list[int]] = {}
    round_order: list[int] = []

    for bucket in buckets:
        for node in bucket:
            if (
                node.node_kind != "fixed_league_match"
                or int(node.competition_id) != competition_id
                or node.round_id is None
            ):
                continue

            round_id = int(node.round_id)
            if round_id not in by_round:
                by_round[round_id] = []
                round_order.append(round_id)

            if not node.node_token:
                raise ValueError("fixed League schedule node has no fixture token")
            by_round[round_id].append(int(node.node_token[-1]))

    return tuple(
        (round_id, tuple(by_round[round_id]))
        for round_id in round_order
    )

def premier_league_fixture_order_by_round(
    buckets: Iterable[Iterable[StartupScheduleNode]],
    *,
    competition_id: int = 0,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Extract shuffled PL fixture order for fixed or annual procedural seasons.

    First-season fixed nodes use round_id, while annual mode-0 LeagueMatch nodes
    use schedule_index as the matchday index. Both are walked in exact shuffled
    bucket head-to-tail order.
    """
    competition_id = int(competition_id)
    by_round: dict[int, list[int]] = {}
    round_order: list[int] = []

    for bucket in buckets:
        for node in bucket:
            if int(node.competition_id) != competition_id:
                continue
            if node.node_kind == "fixed_league_match":
                if node.round_id is None:
                    continue
                round_index = int(node.round_id)
            elif node.node_kind == "league_match":
                if int(node.competition_context) != 0 or node.schedule_index is None:
                    continue
                round_index = int(node.schedule_index)
            else:
                continue

            if not node.node_token:
                raise ValueError("Premier League schedule node has no fixture token")
            if round_index not in by_round:
                by_round[round_index] = []
                round_order.append(round_index)
            by_round[round_index].append(int(node.node_token[-1]))

    return tuple(
        (round_index, tuple(by_round[round_index]))
        for round_index in round_order
    )

