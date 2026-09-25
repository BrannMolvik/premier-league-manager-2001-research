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


class OrderedCompetitionSource(CompetitionSource, Protocol):
    parent_competition_id: int | None
    initialization_order_value: int
    country_region_id: int


class OrderedRoundSource(RoundSource, Protocol):
    id: int
    type_code: int
    scheduled_week: int
    scheduled_weekday: int
    source_competition_reference: int


class CupAllocationInstructionSource(Protocol):
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int
    source_reference: int
    quantity: int
    auxiliary: int


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
class PrimaryMode0OrderedRngEvent:
    kind: str
    competition_id: int
    round_id: int | None
    bounds: tuple[int, ...]
    pre_sort_slot_order: tuple[int, ...]
    selected_club_id: int | None
    state_after: int


@dataclass(frozen=True)
class PrimaryMode0OrderedCompetitionRngReplay:
    events: tuple[PrimaryMode0OrderedRngEvent, ...]
    primary_cup_round_count: int
    cup_pairing_draw_count: int
    europe_selector_draw_count: int
    total_draw_count: int
    champions_league_club_id: int | None
    uefa_cup_club_id: int | None
    state_entering_primary_shuffle: int


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



def _msvc_small_qsort_by_key(items, key):
    """Reproduce the <=8-element path of CRT qsort at 0x668DA4."""
    result = list(items)
    if len(result) > 8:
        raise ValueError("small CRT qsort helper only models arrays of at most 8")
    for end in range(len(result) - 1, 0, -1):
        max_index = 0
        max_key = key(result[0])
        for index in range(1, end + 1):
            value = key(result[index])
            if value > max_key:
                max_index = index
                max_key = value
        result[max_index], result[end] = result[end], result[max_index]
    return tuple(result)


def _competition_subtree_has_primary_cup(
    competition_id: int,
    competitions_by_parent: dict[int, tuple[OrderedCompetitionSource, ...]],
    competition_by_id: dict[int, OrderedCompetitionSource],
) -> bool:
    competition = competition_by_id[int(competition_id)]
    if (
        int(competition.runtime_kind_code) == 2
        and int(competition.schedule_container_code) not in (2, 3)
    ):
        return True
    return any(
        _competition_subtree_has_primary_cup(
            int(child.id),
            competitions_by_parent,
            competition_by_id,
        )
        for child in competitions_by_parent.get(int(competition_id), ())
    )


def primary_mode0_root_initialization_order(
    competitions: Iterable[OrderedCompetitionSource],
    country_ids_in_source_order: Iterable[int],
) -> tuple[OrderedCompetitionSource, ...]:
    """Return root initialization order relevant to the primary container.

    Country root arrays are built in source competition order, qsorted by
    runtime +0x18 = -initialization_order_value, then traversed backwards.

    For root arrays of at most eight elements this reproduces the executable's
    exact small-array CRT qsort path. For larger arrays, unique-key ordering is
    exact; equal-key groups are accepted only when at most one member's
    subtree can consume primary Cup RNG, because then their internal
    permutation cannot change the emitted RNG event sequence.
    """
    competition_list = tuple(competitions)
    by_id = {int(competition.id): competition for competition in competition_list}
    children: dict[int, list[OrderedCompetitionSource]] = {}
    for competition in competition_list:
        parent = competition.parent_competition_id
        if parent is not None:
            children.setdefault(int(parent), []).append(competition)
    children_tuple = {
        parent: tuple(values)
        for parent, values in children.items()
    }

    roots_by_country: dict[int, list[OrderedCompetitionSource]] = {}
    for competition in competition_list:
        if competition.parent_competition_id is None:
            roots_by_country.setdefault(
                int(competition.country_region_id),
                [],
            ).append(competition)

    ordered: list[OrderedCompetitionSource] = []
    for country_id in country_ids_in_source_order:
        roots = roots_by_country.get(int(country_id), [])
        if not roots:
            continue

        if len(roots) <= 8:
            qsorted = _msvc_small_qsort_by_key(
                roots,
                lambda competition: -int(competition.initialization_order_value),
            )
            initialized = tuple(reversed(qsorted))
        else:
            groups: dict[int, list[OrderedCompetitionSource]] = {}
            for root in roots:
                groups.setdefault(
                    int(root.initialization_order_value),
                    [],
                ).append(root)
            for same_key in groups.values():
                rng_bearing = [
                    root
                    for root in same_key
                    if _competition_subtree_has_primary_cup(
                        int(root.id),
                        children_tuple,
                        by_id,
                    )
                ]
                if len(rng_bearing) > 1:
                    raise ValueError(
                        "large equal-key root group contains multiple primary "
                        "Cup RNG-bearing subtrees; full CRT qsort emulation required"
                    )
            initialized = tuple(
                sorted(
                    roots,
                    key=lambda competition: int(
                        competition.initialization_order_value
                    ),
                )
            )

        ordered.extend(
            competition
            for competition in initialized
            if int(competition.schedule_container_code) not in (2, 3)
        )

    return tuple(ordered)


def _effective_cup_round_sort_key(
    round_definition: OrderedRoundSource,
    rounds_by_competition: dict[int, tuple[OrderedRoundSource, ...]],
) -> tuple[int, int]:
    if int(round_definition.type_code) != 3:
        return (
            int(round_definition.scheduled_week),
            int(round_definition.scheduled_weekday) - 1,
        )

    child_competition_id = int(round_definition.source_competition_reference) & 0xFFFF
    child_rounds = rounds_by_competition.get(child_competition_id, ())
    if not child_rounds:
        raise ValueError(
            f"MiniLeague round {int(round_definition.id)} has no child League schedule"
        )
    first_child_round = child_rounds[0]
    return (
        int(first_child_round.scheduled_week),
        int(first_child_round.scheduled_weekday) - 1,
    )


def primary_cup_round_initialization_order(
    competition_id: int,
    rounds: Iterable[OrderedRoundSource],
) -> tuple[OrderedRoundSource, ...]:
    """Reproduce Cup+0x38 qsort order before Cup::init schedules rounds."""
    round_list = tuple(rounds)
    by_competition: dict[int, list[OrderedRoundSource]] = {}
    for round_definition in round_list:
        by_competition.setdefault(
            int(round_definition.competition_id),
            [],
        ).append(round_definition)
    by_competition_tuple = {
        competition: tuple(values)
        for competition, values in by_competition.items()
    }
    cup_rounds = by_competition_tuple.get(int(competition_id), ())
    if len(cup_rounds) > 8:
        raise ValueError("canonical Cup round qsort model supports at most 8 rounds")
    return _msvc_small_qsort_by_key(
        cup_rounds,
        lambda round_definition: _effective_cup_round_sort_key(
            round_definition,
            by_competition_tuple,
        ),
    )


def replay_primary_mode0_ordered_competition_rng(
    rng: BoundedRng,
    competitions: Iterable[OrderedCompetitionSource],
    rounds: Iterable[OrderedRoundSource],
    clubs: Iterable[ClubSource],
    countries: Iterable[CountrySource],
) -> PrimaryMode0OrderedCompetitionRngReplay:
    """Replay primary competition RNG in the recovered executable order.

    This closes exact bounded-call ordering before primary 0x615BE0:
    country traversal, root competition ordering, recursive child ordering,
    Europe selector positions, Cup round qsort order, and each round's first
    participant Fisher-Yates.

    pre_sort_slot_order is the randomized participant-slot order immediately
    after the mandatory Fisher-Yates. NormalRound and TwoLegRound subsequently
    qsort the 16-byte participant records by seeding/reference fields, so this
    slot order is not yet the final club pairing for those rounds.
    """
    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    club_list = tuple(clubs)
    country_list = tuple(countries)

    children: dict[int, list[OrderedCompetitionSource]] = {}
    for competition in competition_list:
        parent = competition.parent_competition_id
        if parent is not None:
            children.setdefault(int(parent), []).append(competition)

    candidates = europe_root_cup_candidate_ids(
        club_list,
        country_list,
        excluded_club_id=-1,
    )

    events: list[PrimaryMode0OrderedRngEvent] = []
    champions_league_club_id: int | None = None
    uefa_cup_club_id: int | None = None

    def current_state() -> int:
        return int(getattr(rng, "state", 0)) & 0xFFFFFFFF

    def visit(competition: OrderedCompetitionSource) -> None:
        nonlocal champions_league_club_id, uefa_cup_club_id

        if int(competition.schedule_container_code) in (2, 3):
            return

        if int(competition.runtime_kind_code) == 2:
            if (
                competition.parent_competition_id is None
                and int(competition.country_region_id) == 123
            ):
                if not candidates:
                    selected = -1
                    bounds: tuple[int, ...] = ()
                elif len(candidates) == 1:
                    selected = int(candidates[0])
                    bounds = ()
                else:
                    bound = len(candidates) - 1
                    selected = int(candidates[rng.randbelow(bound)])
                    bounds = (bound,)

                if int(competition.id) == 9:
                    champions_league_club_id = selected
                elif int(competition.id) == 10:
                    uefa_cup_club_id = selected

                events.append(
                    PrimaryMode0OrderedRngEvent(
                        kind="europe_selector",
                        competition_id=int(competition.id),
                        round_id=None,
                        bounds=bounds,
                        pre_sort_slot_order=(),
                        selected_club_id=selected,
                        state_after=current_state(),
                    )
                )

            for round_definition in primary_cup_round_initialization_order(
                int(competition.id),
                round_list,
            ):
                participant_count = int(round_definition.team_count)
                slots = list(range(participant_count))
                bounds = []
                for remaining in range(participant_count, 1, -1):
                    selected_index = rng.randbelow(remaining)
                    last = remaining - 1
                    slots[selected_index], slots[last] = (
                        slots[last],
                        slots[selected_index],
                    )
                    bounds.append(remaining)
                events.append(
                    PrimaryMode0OrderedRngEvent(
                        kind="cup_round_shuffle",
                        competition_id=int(competition.id),
                        round_id=int(round_definition.id),
                        bounds=tuple(bounds),
                        pre_sort_slot_order=tuple(slots),
                        selected_club_id=None,
                        state_after=current_state(),
                    )
                )

        for child in children.get(int(competition.id), ()):
            visit(child)

    country_ids = tuple(int(country.id) for country in country_list)
    for root in primary_mode0_root_initialization_order(
        competition_list,
        country_ids,
    ):
        visit(root)

    cup_round_events = tuple(
        event for event in events if event.kind == "cup_round_shuffle"
    )
    selector_events = tuple(
        event for event in events if event.kind == "europe_selector"
    )
    total_draw_count = sum(len(event.bounds) for event in events)

    return PrimaryMode0OrderedCompetitionRngReplay(
        events=tuple(events),
        primary_cup_round_count=len(cup_round_events),
        cup_pairing_draw_count=sum(
            len(event.bounds)
            for event in cup_round_events
        ),
        europe_selector_draw_count=sum(
            len(event.bounds)
            for event in selector_events
        ),
        total_draw_count=total_draw_count,
        champions_league_club_id=champions_league_club_id,
        uefa_cup_club_id=uefa_cup_club_id,
        state_entering_primary_shuffle=current_state(),
    )



def ordered_cup_allocation_instructions(
    destination_competition_id: int,
    instructions: Iterable[CupAllocationInstructionSource],
) -> tuple[CupAllocationInstructionSource, ...]:
    """Reproduce per-destination DBRCupAllocInstruction qsort order.

    Startup attaches pointers in source-table order and qsorts each
    competition's pointer array with comparator 0x4F7A30 over sequence_index.

    Canonical lists with <=8 entries use the exact small-array CRT qsort path.
    Larger canonical lists have unique sequence keys, so ordinary ascending
    key order is equivalent. Refuse a large equal-key group instead of
    silently assuming stability.
    """
    selected = tuple(
        instruction
        for instruction in instructions
        if int(instruction.destination_competition_id)
        == int(destination_competition_id)
    )
    if len(selected) <= 8:
        return _msvc_small_qsort_by_key(
            selected,
            lambda instruction: int(instruction.sequence_index),
        )

    keys = [int(instruction.sequence_index) for instruction in selected]
    if len(set(keys)) != len(keys):
        raise ValueError(
            "large Cup allocation list contains equal sequence keys; "
            "full CRT qsort ordering is required"
        )
    return tuple(sorted(selected, key=lambda instruction: int(instruction.sequence_index)))



class InitialLeagueClubSource(Protocol):
    index: int
    short_name: str
    competition_id: int


def initial_league_club_ids(
    clubs: Iterable[InitialLeagueClubSource],
    competition_id: int,
) -> tuple[int, ...]:
    """Return 0x4F7A60's initial unsorted League membership.

    Startup scans DBRClub records in canonical Master.dat order and appends a
    direct type-0 ClubRef/LeagueClub to the runtime competition named by
    DBRClub+0x10, which maps from packed club dword +8.
    """
    competition_id = int(competition_id)
    return tuple(
        int(club.index)
        for club in clubs
        if int(club.competition_id) == competition_id
    )


def initial_ranked_league_club_ids(
    clubs: Iterable[InitialLeagueClubSource],
    competition_id: int,
) -> tuple[int, ...]:
    """Return the initial 0x4F4940 League ranking order.

    LeagueClub statistics are zero at new-game construction, so comparator
    0x4F45E0 reaches its final club-string tie-breaker. That string is
    DBRClub+0x0C, the runtime short-name string loaded from the second packed
    club name ID. The original comparison is bytewise; CP1252 reproduces the
    canonical English data.
    """
    competition_id = int(competition_id)
    selected = [
        club
        for club in clubs
        if int(club.competition_id) == competition_id
    ]
    selected.sort(key=lambda club: str(club.short_name).encode("cp1252"))
    return tuple(int(club.index) for club in selected)
