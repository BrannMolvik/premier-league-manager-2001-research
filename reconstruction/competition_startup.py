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


@dataclass(frozen=True)
class PrimaryMode0CompetitionRngReplay:
    """RNG-visible Europe-root selections before primary 0x615BE0."""

    candidate_ids: tuple[int, ...]
    champions_league_club_id: int
    uefa_cup_club_id: int
    draw_count: int


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
    """Replay the exact mapped primary competition RNG tail before 0x615BE0.

    The canonical shipped path has only two RNG-visible root-Cup selections:
    Champions League ID 9 followed by UEFA Cup ID 10. Both independently
    build the same 0x40C6C0 candidate vector with exclusion -1 and use the
    original count-minus-one selector.

    WCC, primary DummyLeague roots, relevant child Leagues, Scottish PL, and
    the subsequent argument-1 team-finalization paths add no mapped CRT draw.
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
