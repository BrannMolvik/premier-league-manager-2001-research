"""Bounded annual primary-container season regeneration.

This module models the instruction-closed shared mode-0 season-construction
subset reached by 0x4F9010 -> 0x616620(0):

- use current live club competition memberships after LeagueAllocation swaps;
- initialize every primary League procedurally, including Premier League ID 0;
- reuse the recovered Cup/child competition initialization machinery;
- place nodes through 0x615950 using the new season's calendar;
- shuffle every populated primary bucket through 0x615BE0 -> 0x615AE0 on the
  same CRT stream.

It deliberately does not mutate GameState yet. Annual team/player maintenance,
post-shuffle competition +0x0C finalization, secondary-container regeneration,
and any still-unclosed cross-season qualification state remain separate
boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from competition_materializer import (
    PrimaryRngDrivenScheduleMaterialization,
    materialize_primary_rng_driven_schedule,
)
from primary_schedule import (
    PrimarySchedulePlacement,
    PrimaryScheduleShuffle,
    place_primary_schedule_nodes,
    shuffle_primary_schedule_buckets,
)


class LiveCompetitionClubView:
    """Read-only source club view with live competition membership overlaid."""

    __slots__ = ("_source", "competition_id")

    def __init__(self, source, competition_id: int):
        self._source = source
        self.competition_id = int(competition_id)

    def __getattr__(self, name):
        return getattr(self._source, name)

    @property
    def index(self) -> int:
        return int(self._source.index)


@dataclass(frozen=True)
class AnnualPrimaryScheduleRegeneration:
    season_year: int
    live_clubs: tuple[LiveCompetitionClubView, ...]
    competition: PrimaryRngDrivenScheduleMaterialization
    placement: PrimarySchedulePlacement
    shuffle: PrimaryScheduleShuffle
    state_before: int
    state_entering_shuffle: int
    state_after: int

    @property
    def competition_draw_count(self) -> int:
        return int(self.competition.rng_plan_total_draw_count)

    @property
    def bucket_shuffle_draw_count(self) -> int:
        return int(self.shuffle.draw_count)

    @property
    def total_draw_count(self) -> int:
        return self.competition_draw_count + self.bucket_shuffle_draw_count


def clubs_with_live_competition_memberships(
    clubs: Iterable[object],
    memberships: Mapping[int, int],
) -> tuple[LiveCompetitionClubView, ...]:
    """Overlay live competition membership without mutating source Club rows."""

    membership_map = {
        int(club_id): int(competition_id)
        for club_id, competition_id in memberships.items()
    }
    result: list[LiveCompetitionClubView] = []
    for club in clubs:
        club_id = int(getattr(club, "index"))
        if club_id in membership_map:
            competition_id = membership_map[club_id]
        elif hasattr(club, "competition_id"):
            competition_id = int(getattr(club, "competition_id"))
        else:
            raise ValueError(
                f"club {club_id} has no source or live competition membership"
            )
        result.append(LiveCompetitionClubView(club, competition_id))
    return tuple(result)


def materialize_annual_primary_schedule(
    rng,
    competitions: Iterable[object],
    rounds: Iterable[object],
    clubs: Iterable[object],
    countries: Iterable[object],
    allocation_instructions: Iterable[object],
    players: Iterable[object],
    *,
    club_competition_membership: Mapping[int, int],
    season_year: int,
    cup_enumerated_club_ids_by_source: dict[
        int, tuple[int | None, ...]
    ] | None = None,
) -> AnnualPrimaryScheduleRegeneration:
    """Materialize the proven annual primary-container construction subset.

    FOOTBAL.EXE League::init(0x4F5150) takes the procedural builder on annual
    mode 0 even for Premier League ID 0, so no fixed real-fixture competition
    IDs or shipped 2000/01 fixture rows are supplied here.

    The caller's RNG is consumed in place. The state leaving competition
    initialization is therefore exactly the state entering 0x615BE0, and the
    same stream immediately continues through each bucket's 0x615AE0 shuffle.
    """

    state_before = getattr(rng, "state", None)
    if state_before is None:
        raise TypeError("annual regeneration requires an RNG with CRT state")
    season_year = int(season_year)
    live_clubs = clubs_with_live_competition_memberships(
        tuple(clubs),
        club_competition_membership,
    )

    competition = materialize_primary_rng_driven_schedule(
        rng,
        competitions,
        rounds,
        live_clubs,
        countries,
        allocation_instructions,
        players,
        fixed_fixture_competition_ids=(),
        real_fixtures=(),
        cup_enumerated_club_ids_by_source=cup_enumerated_club_ids_by_source,
    )
    placement = place_primary_schedule_nodes(
        competition.schedule_nodes,
        season_year=season_year,
    )
    shuffle = shuffle_primary_schedule_buckets(
        placement.buckets,
        rng,
    )
    state_after = getattr(rng, "state", None)
    if state_after is None:
        raise TypeError("annual regeneration RNG lost its CRT state")

    return AnnualPrimaryScheduleRegeneration(
        season_year=season_year,
        live_clubs=live_clubs,
        competition=competition,
        placement=placement,
        shuffle=shuffle,
        state_before=int(state_before) & 0xFFFFFFFF,
        state_entering_shuffle=int(
            competition.state_entering_primary_shuffle
        ) & 0xFFFFFFFF,
        state_after=int(state_after) & 0xFFFFFFFF,
    )
