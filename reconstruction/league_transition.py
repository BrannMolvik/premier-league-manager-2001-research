"""Source-backed LeagueAllocation season-transition exchanges.

FOOTBAL.EXE annual finalization iterates the globally sorted DBRLeagueAllocation
rows and swaps the current competition-membership values of the two clubs
selected by each paired ranking slot.  Selection competition identity and the
club's current membership are deliberately separate: a playoff winner is
selected through the playoff competition but still owns its parent-League
membership before the exchange.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol


class LeagueAllocationSource(Protocol):
    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int


ENGLISH_LEAGUE_ALLOCATION_IDS = (0, 1, 2, 3, 4, 5, 6, 25)


@dataclass(frozen=True)
class LeagueMembershipExchange:
    allocation_id: int
    slot_index: int
    club_a_id: int
    club_b_id: int
    membership_a_before: int
    membership_b_before: int


@dataclass(frozen=True)
class LeagueTransitionResult:
    memberships: dict[int, int]
    exchanges: tuple[LeagueMembershipExchange, ...]


def ordered_english_league_allocations(
    records: Iterable[LeagueAllocationSource],
) -> tuple[LeagueAllocationSource, ...]:
    """Return the instruction-closed English annual allocation order."""
    by_id = {int(record.id): record for record in records}
    missing = tuple(
        allocation_id
        for allocation_id in ENGLISH_LEAGUE_ALLOCATION_IDS
        if allocation_id not in by_id
    )
    if missing:
        raise ValueError(f"missing English LeagueAllocation rows {missing}")
    return tuple(by_id[allocation_id] for allocation_id in ENGLISH_LEAGUE_ALLOCATION_IDS)


def _inclusive_slots(start: int, end: int) -> tuple[int, ...]:
    start = int(start)
    end = int(end)
    step = 1 if end >= start else -1
    return tuple(range(start, end + step, step))


def apply_league_allocation_exchanges(
    records: Iterable[LeagueAllocationSource],
    rankings_by_competition: Mapping[int, tuple[int, ...]],
    current_memberships: Mapping[int, int],
) -> LeagueTransitionResult:
    """Apply 0x4F4BD0/0x4F4ED0 paired membership swaps.

    Rankings are immutable final-season snapshots.  Memberships are copied and
    then mutated in allocation order.  The smaller inclusive range length is
    used exactly as 0x4F83D0 requires.
    """
    memberships = {
        int(club_id): int(competition_id)
        for club_id, competition_id in current_memberships.items()
    }
    exchanges: list[LeagueMembershipExchange] = []

    for record in records:
        a_id = int(record.competition_a_id)
        b_id = int(record.competition_b_id)
        ranking_a = rankings_by_competition.get(a_id)
        ranking_b = rankings_by_competition.get(b_id)
        if ranking_a is None or ranking_b is None:
            raise ValueError(
                f"unresolved LeagueAllocation ranking endpoint {a_id}/{b_id}"
            )

        slots_a = _inclusive_slots(
            int(record.competition_a_start),
            int(record.competition_a_end),
        )
        slots_b = _inclusive_slots(
            int(record.competition_b_start),
            int(record.competition_b_end),
        )
        count = min(len(slots_a), len(slots_b))

        for slot_index, (position_a, position_b) in enumerate(
            zip(slots_a[:count], slots_b[:count])
        ):
            if not 0 <= position_a < len(ranking_a):
                raise ValueError(
                    f"allocation {int(record.id)} A position {position_a} "
                    f"is outside competition {a_id} ranking"
                )
            if not 0 <= position_b < len(ranking_b):
                raise ValueError(
                    f"allocation {int(record.id)} B position {position_b} "
                    f"is outside competition {b_id} ranking"
                )

            club_a = int(ranking_a[position_a])
            club_b = int(ranking_b[position_b])
            if club_a == club_b:
                raise ValueError(
                    f"allocation {int(record.id)} selects the same club twice"
                )
            if club_a not in memberships or club_b not in memberships:
                raise ValueError(
                    f"allocation {int(record.id)} references a club without "
                    "live competition membership"
                )

            membership_a = int(memberships[club_a])
            membership_b = int(memberships[club_b])
            memberships[club_a] = membership_b
            memberships[club_b] = membership_a
            exchanges.append(
                LeagueMembershipExchange(
                    allocation_id=int(record.id),
                    slot_index=slot_index,
                    club_a_id=club_a,
                    club_b_id=club_b,
                    membership_a_before=membership_a,
                    membership_b_before=membership_b,
                )
            )

    return LeagueTransitionResult(
        memberships=memberships,
        exchanges=tuple(exchanges),
    )
