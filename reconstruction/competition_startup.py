"""Recovered startup competition-selection helpers.

These helpers preserve executable quirks without assigning unsupported football
semantics to still-neutral source fields.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol


class ClubSource(Protocol):
    index: int
    country_id: int
    runtime_value_1c_source: int
    team_category_code: int


class CountrySource(Protocol):
    id: int
    eu_status_flag: int


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class RawCrtRng(Protocol):
    state: int
    def rand15(self) -> int: ...


class CompetitionSource(Protocol):
    id: int
    runtime_kind_code: int
    schedule_container_code: int


class RoundSource(Protocol):
    competition_id: int
    team_count: int


@dataclass(frozen=True)
class PrimaryMode0CompetitionRngReplay:
    """Isolated Europe-root selector mechanics.

    This is not the complete primary pre-0x615BE0 RNG tail: Cup round
    schedulers interleave additional participant-pairing shuffles.
    """

    candidate_ids: tuple[int, ...]
    champions_league_club_id: int
    uefa_cup_club_id: int
    draw_count: int


@dataclass(frozen=True)
class PrimaryMode0PreShuffleStateReplay:
    """State-only replay of all mapped primary competition RNG calls.

    Bounds/output interleaving for Cup pairings is intentionally not
    materialized here. Every bounded MSVC helper call advances the same LCG
    exactly once, so the hidden CRT state depends only on the total call count.
    """

    primary_cup_round_count: int
    cup_pairing_draw_count: int
    europe_selector_draw_count: int
    total_draw_count: int
    state_entering_primary_shuffle: int


def europe_root_cup_candidate_ids(
    clubs: Iterable[ClubSource],
    countries: Iterable[CountrySource],
    *,
    excluded_club_id: int = -1,
) -> tuple[int, ...]:
    """Reproduce the filtering loop in 0x40C6C0.

    Candidates retain runtime team-table iteration order. The source fields map
    to Master.dat club +98 (runtime team type byte +0x74), Master.dat club +18
    (runtime team dword +0x1C), and Static.dat country +16
    (runtime DBRCountry word +0x18).
    """
    country_by_id = {int(country.id): country for country in countries}
    result: list[int] = []
    excluded_club_id = int(excluded_club_id)

    for club in clubs:
        club_id = int(club.index)
        if club_id == excluded_club_id:
            continue
        if int(club.team_category_code) not in (2, 3):
            continue
        if int(club.runtime_value_1c_source) <= 50000:
            continue
        country = country_by_id.get(int(club.country_id))
        if country is None or int(country.eu_status_flag) == 0:
            continue
        result.append(club_id)
    return tuple(result)


def select_europe_root_cup_candidate(
    candidate_ids: Iterable[int],
    rng: BoundedRng,
) -> int:
    """Reproduce 0x5EE6A0 -> 0x5EE6C0, including count-1 quirk.

    Empty lists return -1. One-entry lists return their only entry without an
    RNG call. For count > 1 the executable calls RNG(count - 1), making the
    final vector entry unreachable.
    """
    candidates = tuple(int(value) for value in candidate_ids)
    if not candidates:
        return -1
    if len(candidates) == 1:
        return candidates[0]
    return candidates[rng.randbelow(len(candidates) - 1)]


def replay_primary_mode0_competition_rng(
    rng: BoundedRng,
    clubs: Iterable[ClubSource],
    countries: Iterable[CountrySource],
) -> PrimaryMode0CompetitionRngReplay:
    """Replay only the two Europe-root 0x40C6C0 selector mechanics.

    Champions League ID 9 and UEFA Cup ID 10 independently build the same
    candidate vector and use the original count-minus-one selector. Their
    calls are *not* adjacent in the full startup stream because Cup round
    schedulers consume participant-shuffle RNG between root competition
    initialization steps. Use replay_primary_mode0_pre_shuffle_state() for
    the complete hidden CRT-state advance.
    """
    club_list = tuple(clubs)
    country_list = tuple(countries)
    candidates = europe_root_cup_candidate_ids(
        club_list,
        country_list,
        excluded_club_id=-1,
    )

    champions_league_club_id = select_europe_root_cup_candidate(candidates, rng)
    uefa_cup_club_id = select_europe_root_cup_candidate(candidates, rng)

    return PrimaryMode0CompetitionRngReplay(
        candidate_ids=candidates,
        champions_league_club_id=champions_league_club_id,
        uefa_cup_club_id=uefa_cup_club_id,
        draw_count=2 if len(candidates) > 1 else 0,
    )



def primary_mode0_cup_round_team_counts(
    competitions: Iterable[CompetitionSource],
    rounds: Iterable[RoundSource],
) -> tuple[int, ...]:
    """Return packed team counts for all primary-container Cup rounds.

    runtime_kind_code == 2 is the recovered Cup class. Schedule-container
    codes 2/3 belong to the secondary container and are excluded here.

    Source order is preserved for diagnostics. The state-only replay depends
    on the multiset of counts, not their order, because every Fisher-Yates
    bounded call advances the MSVC CRT LCG exactly once.
    """
    primary_cup_ids = {
        int(competition.id)
        for competition in competitions
        if int(competition.runtime_kind_code) == 2
        and int(competition.schedule_container_code) not in (2, 3)
    }
    return tuple(
        int(round_definition.team_count)
        for round_definition in rounds
        if int(round_definition.competition_id) in primary_cup_ids
    )


def primary_mode0_cup_pairing_draw_count(
    competitions: Iterable[CompetitionSource],
    rounds: Iterable[RoundSource],
) -> int:
    """Count mandatory first-shuffle calls across primary Cup round schedulers.

    NormalRound, TwoLegRound and MiniLeagueRound all begin by shuffling the
    runtime participant array. A round containing N participants therefore
    consumes max(N-1, 0) bounded CRT calls before schedule-bucket shuffling.
    """
    return sum(
        max(0, int(team_count) - 1)
        for team_count in primary_mode0_cup_round_team_counts(
            competitions,
            rounds,
        )
    )


def replay_primary_mode0_pre_shuffle_state(
    rng: RawCrtRng,
    competitions: Iterable[CompetitionSource],
    rounds: Iterable[RoundSource],
    clubs: Iterable[ClubSource],
    countries: Iterable[CountrySource],
) -> PrimaryMode0PreShuffleStateReplay:
    """Advance the exact mapped CRT *state* to primary 0x615BE0.

    The primary Cup round schedulers contribute one raw CRT state advance for
    every Fisher-Yates bounded call. The two Europe-root selectors contribute
    one call each only when their shipped candidate vector has more than one
    entry.

    This helper deliberately advances raw rand15() calls instead of pretending
    the selector/pairing outputs are adjacent. It is exact for hidden CRT state;
    exact bounded-output interleaving and Cup pair identities remain separate
    scheduler-fidelity work.
    """
    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    club_list = tuple(clubs)
    country_list = tuple(countries)

    team_counts = primary_mode0_cup_round_team_counts(
        competition_list,
        round_list,
    )
    pairing_draw_count = sum(max(0, value - 1) for value in team_counts)

    candidates = europe_root_cup_candidate_ids(
        club_list,
        country_list,
        excluded_club_id=-1,
    )
    selector_draw_count = 2 if len(candidates) > 1 else 0
    total_draw_count = pairing_draw_count + selector_draw_count

    for _ in range(total_draw_count):
        rng.rand15()

    state = int(getattr(rng, "state")) & 0xFFFFFFFF
    return PrimaryMode0PreShuffleStateReplay(
        primary_cup_round_count=len(team_counts),
        cup_pairing_draw_count=pairing_draw_count,
        europe_selector_draw_count=selector_draw_count,
        total_draw_count=total_draw_count,
        state_entering_primary_shuffle=state,
    )
