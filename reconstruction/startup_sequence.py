"""Composed startup RNG replay through the primary schedule-shuffle boundary.

This module joins the independently recovered startup and primary competition
RNG phases on one shared MSVC CRT stream. It intentionally stops immediately
before 0x615BE0 begins shuffling primary schedule buckets.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol

from competition_startup import (
    ClubSource as CompetitionClubSource,
    CompetitionSource,
    CountrySource as CompetitionCountrySource,
    PrimaryMode0PreShuffleStateReplay,
    RoundSource,
    replay_primary_mode0_pre_shuffle_state,
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
    primary_competition_state: PrimaryMode0PreShuffleStateReplay
    state_entering_primary_shuffle: int


def replay_startup_rng_to_primary_shuffle(
    rng: StatefulStartupRng,
    clubs: Iterable[FullStartupClubSource],
    countries: Iterable[FullStartupCountrySource],
    players: Iterable[StartupPlayerSource],
    selected_user_country_id: int,
    users: Iterable[StartupUserRngConfig],
    competitions: Iterable[CompetitionSource],
    rounds: Iterable[RoundSource],
) -> StartupToPrimaryShuffleReplay:
    """Advance one shared RNG through every mapped state change before 0x615BE0.

    The competition phase currently replays the exact hidden CRT-state advance
    from primary Cup pairing shuffles plus the two Europe selectors. Exact Cup
    pairing outputs/interleaving are tracked separately from this state ledger.
    """

    club_list = tuple(clubs)
    country_list = tuple(countries)
    player_list = tuple(players)
    user_list = tuple(users)
    competition_list = tuple(competitions)
    round_list = tuple(rounds)

    precompetition = replay_precompetition_startup_rng(
        rng,
        club_list,
        country_list,
        player_list,
        selected_user_country_id=int(selected_user_country_id),
        users=user_list,
    )
    primary_competition_state = replay_primary_mode0_pre_shuffle_state(
        rng,
        competition_list,
        round_list,
        club_list,
        country_list,
    )
    return StartupToPrimaryShuffleReplay(
        precompetition=precompetition,
        primary_competition_state=primary_competition_state,
        state_entering_primary_shuffle=int(rng.state) & 0xFFFFFFFF,
    )
