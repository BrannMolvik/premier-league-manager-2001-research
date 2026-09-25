"""Recovered pre-schedule startup RNG primitives.

Only behavior with proven executable ordering/bounds is modeled here.
"""

from typing import Iterable, Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class PlayerSource(Protocol):
    index: int
    club_id: int
    initial_flags: int


class SpareClubSource(Protocol):
    index: int
    name: str


STARTUP_YOUTH_CANDIDATE_CAP = 0x200


def startup_spare_club_id(clubs: Iterable[SpareClubSource]) -> int:
    """Reproduce 0x40C4E0: first exact !Spare team-table match, else 0."""
    for club in clubs:
        if str(club.name) == "!Spare":
            return int(club.index)
    return 0


def startup_youth_target_count(option_mode: int | None, rng: BoundedRng) -> int:
    """Reproduce 0x42C3A0 followed by the +4 in 0x61DF90."""
    if option_mode is None:
        return 4
    option_mode = int(option_mode)
    if option_mode == 0:
        return 4 + rng.randbelow(2)
    if option_mode == 1:
        return 5 + rng.randbelow(2)
    if option_mode == 2:
        return 6 + rng.randbelow(3)
    return 4


def startup_youth_candidate_ids(
    players: Iterable[PlayerSource],
    source_club_id: int,
) -> tuple[int, ...]:
    """Reproduce the 0x61DF90 source filter and fixed 512-WORD buffer."""
    source_club_id = int(source_club_id)
    result: list[int] = []
    for player in players:
        if int(player.club_id) != source_club_id:
            continue
        if int(player.initial_flags) & 0x08:
            continue
        result.append(int(player.index))
        if len(result) >= STARTUP_YOUTH_CANDIDATE_CAP:
            break
    return tuple(result)


def startup_youth_selection_bounds(
    candidate_count: int,
    target_count: int,
    *,
    destination_count: int = 0,
) -> tuple[int, ...]:
    """Return exact candidate-selection RNG bounds for one 0x61DF90 run.

    The loop stops when the candidate list is empty, the requested target has
    been reached, or the destination list reaches its hard cap of 20 entries.
    """
    candidate_count = max(0, int(candidate_count))
    remaining_slots = max(0, 20 - int(destination_count))
    draws = min(candidate_count, max(0, int(target_count)), remaining_slots)
    return tuple(candidate_count - offset for offset in range(draws))


def select_startup_youth_candidate(candidates: list[int], rng: BoundedRng) -> int:
    """Select one candidate and apply the executable swap-delete mutation."""
    if not candidates:
        raise ValueError("candidate list must not be empty")
    selected_index = rng.randbelow(len(candidates))
    selected = int(candidates[selected_index])
    candidates[selected_index] = candidates[-1]
    candidates.pop()
    return selected


class GeneratedNamePlayerSource(Protocol):
    index: int
    first_name: str
    surname: str
    nationality_id: int


class GeneratedNameCountrySource(Protocol):
    id: int
    nationality_id: int


class GeneratedNameClubSource(Protocol):
    index: int
    name: str
    country_id: int
    team_category_code: int


def generated_name_source_eligible(first_name: str, surname: str) -> bool:
    """Exact string gate used twice by 0x411A10 when building name sources."""
    first_name = str(first_name)
    surname = str(surname)

    def byte_at(value: str, index: int) -> int:
        if index >= len(value):
            return 0
        return ord(value[index])

    return (
        byte_at(first_name, 1) != 0x2E
        and byte_at(surname, 0) != 0x4E
        and byte_at(surname, 1) != 0x6F
        and byte_at(surname, 2) != 0x2E
    )


def generated_name_source_ids(
    players: Iterable[GeneratedNamePlayerSource],
    nationality_id: int,
) -> tuple[int, ...]:
    """Reproduce DBRNationality +0x0C/+0x10 source-vector construction."""
    nationality_id = int(nationality_id)
    return tuple(
        int(player.index)
        for player in players
        if int(player.nationality_id) == nationality_id
        and generated_name_source_eligible(player.first_name, player.surname)
    )


def generated_name_rng_bound(
    country_id: int,
    countries: Iterable[GeneratedNameCountrySource],
    players: Iterable[GeneratedNamePlayerSource],
) -> int:
    """Return the exact bound consumed by one 0x421BA0 call for a country."""
    player_list = tuple(players)
    country_by_id = {int(country.id): country for country in countries}
    country = country_by_id[int(country_id)]
    nationality_id = int(country.nationality_id)
    if nationality_id in (-1, 0xFFFFFFFF):
        nationality_id = 26
    source_count = len(generated_name_source_ids(player_list, nationality_id))
    return source_count if source_count > 10 else len(player_list)


def startup_team_name_country_ids(
    clubs: Iterable[GeneratedNameClubSource],
) -> tuple[int, ...]:
    """Return countries for the 0x414330 per-team 0x421C00 calls."""
    return tuple(
        int(club.country_id)
        for club in clubs
        if int(club.index) >= 0
        and int(club.team_category_code) not in (2, 3)
        and not str(club.name).startswith("!")
    )


def startup_team_name_rng_bounds(
    clubs: Iterable[GeneratedNameClubSource],
    countries: Iterable[GeneratedNameCountrySource],
    players: Iterable[GeneratedNamePlayerSource],
) -> tuple[int, ...]:
    """Flatten the two 0x421BA0 bounds consumed for each qualifying team."""
    club_list = tuple(clubs)
    country_list = tuple(countries)
    player_list = tuple(players)
    result: list[int] = []
    for country_id in startup_team_name_country_ids(club_list):
        bound = generated_name_rng_bound(country_id, country_list, player_list)
        result.extend((bound, bound))
    return tuple(result)
