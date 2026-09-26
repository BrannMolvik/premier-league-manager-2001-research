"""Composed startup RNG replay through the primary schedule-shuffle boundary.

This module joins the independently recovered startup and primary competition
RNG phases on one shared MSVC CRT stream. It intentionally stops immediately
before 0x615BE0 begins shuffling primary schedule buckets.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol

from competition_startup import (
    ClubSource as CompetitionClubSource,
    CountrySource as CompetitionCountrySource,
    CupAllocationInstructionSource,
    OrderedCompetitionSource,
    OrderedRoundSource,
)
from competition_materializer import (
    PrimaryRngDrivenScheduleMaterialization,
    materialize_primary_rng_driven_schedule,
)
from startup_rng import (
    GeneratedNameCountrySource,
    PrecompetitionStartupRngReplay,
    StatefulStartupRng,
    StartupClubSource,
    StartupPlayerSource,
    StartupUserRngConfig,
    replay_precompetition_startup_rng,
)


class FullStartupClubSource(
    StartupClubSource,
    CompetitionClubSource,
    Protocol,
):
    pass


class FullStartupCountrySource(
    GeneratedNameCountrySource,
    CompetitionCountrySource,
    Protocol,
):
    pass


@dataclass(frozen=True)
class StartupToPrimaryShuffleReplay:
    """All recovered checkpoints through entry to primary 0x615BE0."""

    precompetition: PrecompetitionStartupRngReplay
    primary_competition_state: PrimaryRngDrivenScheduleMaterialization
    state_entering_primary_shuffle: int


def replay_startup_rng_to_primary_shuffle(
    rng: StatefulStartupRng,
    clubs: Iterable[FullStartupClubSource],
    countries: Iterable[FullStartupCountrySource],
    players: Iterable[StartupPlayerSource],
    selected_user_country_id: int,
    users: Iterable[StartupUserRngConfig],
    competitions: Iterable[OrderedCompetitionSource],
    rounds: Iterable[OrderedRoundSource],
    allocation_instructions: Iterable[CupAllocationInstructionSource] = (),
    *,
    real_fixtures: Iterable[object] = (),
    fixed_fixture_competition_ids: Iterable[int] = (0,),
    cup_enumerated_club_ids_by_source: dict[
        int, tuple[int | None, ...]
    ] | None = None,
) -> StartupToPrimaryShuffleReplay:
    """Advance one shared RNG through every mapped state change before 0x615BE0.

    The competition phase materializes the recovered runtime participants and
    schedule nodes while consuming the same CRT stream. Cup Fisher-Yates
    bounds therefore come from each runtime round's actual +0x0C participant
    count after allocation/propagation, not the packed Static.dat capacity.
    """

    club_list = tuple(clubs)
    country_list = tuple(countries)
    player_list = tuple(players)
    user_list = tuple(users)
    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    allocation_list = tuple(allocation_instructions)

    precompetition = replay_precompetition_startup_rng(
        rng,
        club_list,
        country_list,
        player_list,
        selected_user_country_id=int(selected_user_country_id),
        users=user_list,
    )
    primary_competition_state = materialize_primary_rng_driven_schedule(
        rng,
        competition_list,
        round_list,
        club_list,
        country_list,
        allocation_list,
        player_list,
        fixed_fixture_competition_ids=fixed_fixture_competition_ids,
        real_fixtures=real_fixtures,
        cup_enumerated_club_ids_by_source=cup_enumerated_club_ids_by_source,
    )
    return StartupToPrimaryShuffleReplay(
        precompetition=precompetition,
        primary_competition_state=primary_competition_state,
        state_entering_primary_shuffle=int(rng.state) & 0xFFFFFFFF,
    )
