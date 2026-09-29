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
    """Read-only source club view with annual live/qualification state overlaid."""

    __slots__ = (
        "_source",
        "competition_id",
        "historical_competition_id",
        "historical_slot_index",
    )

    def __init__(
        self,
        source,
        competition_id: int,
        *,
        historical_competition_id: int | None = None,
        historical_slot_index: int | None = None,
    ):
        self._source = source
        self.competition_id = int(competition_id)
        self.historical_competition_id = int(
            getattr(source, "historical_competition_id", -1)
            if historical_competition_id is None
            else historical_competition_id
        )
        self.historical_slot_index = int(
            getattr(source, "historical_slot_index", -1)
            if historical_slot_index is None
            else historical_slot_index
        )

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
    *,
    qualification_rankings_by_competition: Mapping[
        int, tuple[int, ...]
    ] | None = None,
) -> tuple[LiveCompetitionClubView, ...]:
    """Overlay annual membership plus finished-season qualification slots.

    0x4F7F70 writes each root League's sorted final table index to club+0x30;
    0x4F9010 then copies the club's finished competition ID to club+0x2C
    before LeagueAllocation swaps update current membership at club+0x10.
    The source DB fields have the same startup representation, so reuse that
    interface with annual values rather than mutating immutable Club records.
    """

    membership_map = {
        int(club_id): int(competition_id)
        for club_id, competition_id in memberships.items()
    }
    qualification_by_club: dict[int, tuple[int, int]] = {}
    for competition_id, ranking in (
        {} if qualification_rankings_by_competition is None
        else qualification_rankings_by_competition
    ).items():
        competition_id = int(competition_id)
        for slot_index, club_id in enumerate(ranking):
            club_id = int(club_id)
            previous = qualification_by_club.get(club_id)
            if previous is not None and previous != (competition_id, slot_index):
                raise ValueError(
                    f"club {club_id} appears in multiple annual qualification rankings"
                )
            qualification_by_club[club_id] = (competition_id, slot_index)

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
        qualification = qualification_by_club.get(club_id)
        result.append(
            LiveCompetitionClubView(
                club,
                competition_id,
                historical_competition_id=(
                    None if qualification is None else qualification[0]
                ),
                historical_slot_index=(
                    None if qualification is None else qualification[1]
                ),
            )
        )
    return tuple(result)


def required_annual_type3_sources(
    competitions: Iterable[object],
    allocation_instructions: Iterable[object],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return primary type-3 League/Dummy and Cup source IDs."""

    competition_by_id = {
        int(competition.id): competition
        for competition in competitions
    }
    league_sources: set[int] = set()
    cup_sources: set[int] = set()
    for instruction in allocation_instructions:
        if int(getattr(instruction, "instruction_type")) != 3:
            continue
        destination = competition_by_id.get(
            int(getattr(instruction, "destination_competition_id"))
        )
        if (
            destination is None
            or int(getattr(destination, "runtime_kind_code", 0)) != 2
            or int(getattr(destination, "schedule_container_code", 0)) in (2, 3)
        ):
            continue
        source_id = int(getattr(instruction, "source_reference"))
        source = competition_by_id.get(source_id)
        if source is None:
            raise ValueError(
                f"annual type-3 allocation references missing competition {source_id}"
            )
        runtime_kind = int(getattr(source, "runtime_kind_code", 0))
        if runtime_kind in (1, 3):
            league_sources.add(source_id)
        elif runtime_kind == 2:
            cup_sources.add(source_id)
    return tuple(sorted(league_sources)), tuple(sorted(cup_sources))


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
    qualification_rankings_by_competition: Mapping[
        int, tuple[int, ...]
    ] | None = None,
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

    Annual type-3 qualification state is mandatory when referenced: League and
    DummyLeague sources receive the finished-season competition/ranking slots
    written by 0x4F7F70/0x4F9010, while Cup sources must provide the completed
    Cup+0x40/+0x44 result pair written by Cup::finalize 0x4F8F80. The annual
    path never falls back to shipped first-season historical references.
    """

    state_before = getattr(rng, "state", None)
    if state_before is None:
        raise TypeError("annual regeneration requires an RNG with CRT state")
    season_year = int(season_year)
    competition_list = tuple(competitions)
    allocation_list = tuple(allocation_instructions)
    required_league_sources, required_cup_sources = required_annual_type3_sources(
        competition_list,
        allocation_list,
    )
    qualification_rankings = (
        {}
        if qualification_rankings_by_competition is None
        else {
            int(key): tuple(int(club_id) for club_id in value)
            for key, value in qualification_rankings_by_competition.items()
        }
    )
    cup_enumerations = (
        {}
        if cup_enumerated_club_ids_by_source is None
        else {
            int(key): tuple(value)
            for key, value in cup_enumerated_club_ids_by_source.items()
        }
    )
    missing_league = tuple(
        source_id
        for source_id in required_league_sources
        if source_id not in qualification_rankings
    )
    missing_cup = tuple(
        source_id
        for source_id in required_cup_sources
        if source_id not in cup_enumerations
    )
    if missing_league:
        raise ValueError(
            "annual type-3 League/Dummy qualification rankings are missing for "
            f"{missing_league}"
        )
    if missing_cup:
        raise ValueError(
            "annual type-3 Cup result enumerations are missing for "
            f"{missing_cup}"
        )

    live_clubs = clubs_with_live_competition_memberships(
        tuple(clubs),
        club_competition_membership,
        qualification_rankings_by_competition=qualification_rankings,
    )

    competition = materialize_primary_rng_driven_schedule(
        rng,
        competition_list,
        rounds,
        live_clubs,
        countries,
        allocation_list,
        players,
        fixed_fixture_competition_ids=(),
        real_fixtures=(),
        cup_enumerated_club_ids_by_source=cup_enumerations,
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
