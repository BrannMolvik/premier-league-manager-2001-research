"""Recovered pre-schedule startup RNG primitives.

Only behavior with proven executable ordering/bounds is modeled here.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class RawCrtRng(Protocol):
    def rand15(self) -> int: ...


class StatefulStartupRng(BoundedRng, RawCrtRng, Protocol):
    state: int


LOADER444_FIRST_DECODE_RAW_DRAWS = 260


def consume_loader444_first_decode_rng(rng: RawCrtRng) -> int:
    """Advance the shared CRT stream for the first startup .444 decode.

    The original Loader444 path consumes 259 raw rand() calls while lazily
    initializing its process-global table, followed by one mutually-exclusive
    pixel-conversion/dither rand() call.

    The modern Windows 11 port may decode bground.444 differently, but startup
    fidelity still requires advancing the shared MSVC CRT state by all 260
    original raw draws before DBTPlayers construction begins.

    Returns the number of raw CRT draws consumed.
    """
    for _ in range(LOADER444_FIRST_DECODE_RAW_DRAWS):
        rng.rand15()
    return LOADER444_FIRST_DECODE_RAW_DRAWS


def consume_dbtplayers_startup_rng(rng: BoundedRng, player_count: int) -> int:
    """Advance the exact DBTPlayers construction/load RNG sequence.

    DBTPlayers constructs every DBRPlayer before loading any compact records.
    Therefore all RNG(15) constructor morale draws happen first. The later
    per-record load pass first consumes one wage-range RNG call through
    DBTAccessSkillFinancialValues::0x423A50, followed by development
    RNG(1), RNG(2), RNG(2) and contract-span RNG(5), in table order.
    The wage bound varies by the player's financial-value band; this state-only
    replay uses RNG(1) as a neutral one-call surrogate because every bounded
    CRT call advances the same hidden LCG state once.

    Returns the number of raw/bounded CRT calls consumed.
    """
    player_count = int(player_count)
    if player_count < 0:
        raise ValueError("player_count must not be negative")

    for _ in range(player_count):
        rng.randbelow(15)

    for _ in range(player_count):
        # 0x418E6E -> 0x423A50: randomized starting weekly wage. The exact
        # bound comes from DBTAccessSkillFinancialValues +0x14. For startup
        # hidden-state replay only, any positive bound is equivalent because
        # 0x64D540 consumes exactly one CRT rand() call.
        rng.randbelow(1)
        rng.randbelow(1)
        rng.randbelow(2)
        rng.randbelow(2)
        rng.randbelow(5)

    return player_count * 6


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


class StartupPlayerSource(PlayerSource, GeneratedNamePlayerSource, Protocol):
    pass


class StartupClubSource(SpareClubSource, GeneratedNameClubSource, Protocol):
    pass


@dataclass(frozen=True)
class StartupUserRngConfig:
    """RNG-visible user configuration consumed by 0x413980 / 0x61DF90."""

    country_id: int
    option_mode: int | None
    destination_count: int = 0


@dataclass(frozen=True)
class PrecompetitionStartupRngReplay:
    """Intermediate shared-CRT checkpoints for the recovered startup ledger."""

    after_loader444_state: int
    after_players_state: int
    after_team_names_state: int
    after_youth_state: int
    loader444_draw_count: int
    player_draw_count: int
    team_name_draw_count: int
    youth_targets: tuple[int, ...]
    youth_source_ids: tuple[tuple[int, ...], ...]


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


def consume_rng_bounds(rng: BoundedRng, bounds: Iterable[int]) -> tuple[int, ...]:
    """Consume one original bounded draw for every supplied bound."""
    results: list[int] = []
    for bound in bounds:
        bound = int(bound)
        if bound <= 0:
            raise ValueError("RNG bounds must be positive")
        results.append(int(rng.randbelow(bound)))
    return tuple(results)


def consume_startup_team_name_rng(
    rng: BoundedRng,
    clubs: Iterable[GeneratedNameClubSource],
    countries: Iterable[GeneratedNameCountrySource],
    players: Iterable[GeneratedNamePlayerSource],
    selected_user_country_id: int,
) -> int:
    """Consume the exact 0x414330 generated-name RNG calls.

    The team-table pass consumes two draws for every qualifying team.  The
    later fixed blocks make 54 more 0x421C00 calls using the currently selected
    user's team country, i.e. another 108 draws with that country's name bound.

    Returns the number of bounded RNG calls consumed.
    """
    club_list = tuple(clubs)
    country_list = tuple(countries)
    player_list = tuple(players)
    team_bounds = startup_team_name_rng_bounds(
        club_list,
        country_list,
        player_list,
    )
    consume_rng_bounds(rng, team_bounds)

    user_bound = generated_name_rng_bound(
        int(selected_user_country_id),
        country_list,
        player_list,
    )
    consume_rng_bounds(rng, (user_bound,) * 108)
    return len(team_bounds) + 108


def replay_startup_youth_generation(
    rng: BoundedRng,
    candidates: Iterable[int],
    option_mode: int | None,
    name_bound: int,
    *,
    destination_count: int = 0,
) -> tuple[int, tuple[int, ...]]:
    """Replay the RNG-visible portion of 0x61DF90 for one user.

    Exact order per generated player is:

        RNG(current_candidate_count)
        RNG(name_bound)
        RNG(name_bound)

    Candidate removal is swap-with-last.  The option-size draw, when present,
    occurs before the loop.  Returned candidate IDs are the exact selected
    source players; generated first/surname values are intentionally not
    materialized here, but their two RNG calls are consumed in the right place.
    """
    candidate_list = [int(value) for value in candidates]
    name_bound = int(name_bound)
    if name_bound <= 0:
        raise ValueError("name_bound must be positive")

    target_count = startup_youth_target_count(option_mode, rng)
    draw_count = len(
        startup_youth_selection_bounds(
            len(candidate_list),
            target_count,
            destination_count=destination_count,
        )
    )

    selected: list[int] = []
    for _ in range(draw_count):
        selected.append(select_startup_youth_candidate(candidate_list, rng))
        rng.randbelow(name_bound)
        rng.randbelow(name_bound)

    return target_count, tuple(selected)


def replay_startup_youth_generation_for_country(
    rng: BoundedRng,
    candidates: Iterable[int],
    option_mode: int | None,
    country_id: int,
    countries: Iterable[GeneratedNameCountrySource],
    players: Iterable[GeneratedNamePlayerSource],
    *,
    destination_count: int = 0,
) -> tuple[int, tuple[int, ...]]:
    """Resolve the 0x421C00 country name bound and replay one user's youth RNG."""
    country_list = tuple(countries)
    player_list = tuple(players)
    name_bound = generated_name_rng_bound(
        int(country_id),
        country_list,
        player_list,
    )
    return replay_startup_youth_generation(
        rng,
        candidates,
        option_mode,
        name_bound,
        destination_count=destination_count,
    )


def replay_precompetition_startup_rng(
    rng: StatefulStartupRng,
    clubs: Iterable[StartupClubSource],
    countries: Iterable[GeneratedNameCountrySource],
    players: Iterable[StartupPlayerSource],
    selected_user_country_id: int,
    users: Iterable[StartupUserRngConfig],
) -> PrecompetitionStartupRngReplay:
    """Replay every recovered mandatory RNG consumer before competition entry.

    This is the executable form of research/STARTUP_RNG_LEDGER.md. It advances
    one shared CRT stream through:

      Loader444 first-decode compatibility side effect
      -> DBTPlayers construction/load
      -> 0x414330 generated-name block
      -> one 0x61DF90 youth block per linked user

    It intentionally stops before competition initialization. The function
    models RNG-visible startup behavior only; it does not construct player or
    user objects.
    """
    club_list = tuple(clubs)
    country_list = tuple(countries)
    player_list = tuple(players)
    user_list = tuple(users)

    loader444_draw_count = consume_loader444_first_decode_rng(rng)
    after_loader444_state = int(rng.state) & 0xFFFFFFFF

    player_draw_count = consume_dbtplayers_startup_rng(rng, len(player_list))
    after_players_state = int(rng.state) & 0xFFFFFFFF

    team_name_draw_count = consume_startup_team_name_rng(
        rng,
        club_list,
        country_list,
        player_list,
        selected_user_country_id=int(selected_user_country_id),
    )
    after_team_names_state = int(rng.state) & 0xFFFFFFFF

    spare_club_id = startup_spare_club_id(club_list)
    candidates = startup_youth_candidate_ids(player_list, spare_club_id)

    youth_targets: list[int] = []
    youth_source_ids: list[tuple[int, ...]] = []
    for user in user_list:
        target, selected = replay_startup_youth_generation_for_country(
            rng,
            candidates,
            user.option_mode,
            int(user.country_id),
            country_list,
            player_list,
            destination_count=int(user.destination_count),
        )
        youth_targets.append(int(target))
        youth_source_ids.append(tuple(int(value) for value in selected))

    return PrecompetitionStartupRngReplay(
        after_loader444_state=after_loader444_state,
        after_players_state=after_players_state,
        after_team_names_state=after_team_names_state,
        after_youth_state=int(rng.state) & 0xFFFFFFFF,
        loader444_draw_count=loader444_draw_count,
        player_draw_count=player_draw_count,
        team_name_draw_count=team_name_draw_count,
        youth_targets=tuple(youth_targets),
        youth_source_ids=tuple(youth_source_ids),
    )
