"""Recovered startup competition-selection helpers.

These helpers preserve executable quirks without assigning unsupported football
semantics to still-neutral source fields.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol

from match_role_rating import best_preferred_role_rating


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


class DummyLeagueRatingPlayerSource(Protocol):
    club_id: int
    current_raw: tuple[int, ...]
    positions: tuple[int, int, int]


@dataclass(frozen=True)
class DummyLeagueSortEntry:
    club_id: int
    base_score: int
    rng_bound: int


@dataclass(frozen=True)
class DummyLeagueRankedEntry:
    club_id: int
    base_score: int
    rng_bound: int
    roll: int
    randomized_score: int


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
    dummy_league_sort_draw_count: int
    europe_selector_draw_count: int
    total_draw_count: int
    state_entering_primary_shuffle: int

@dataclass(frozen=True)
class CupClubRefDescriptor:
    """Semantic reconstruction of the 16-byte runtime ClubRef."""

    type_code: int
    selector: int = 0
    direct_club_id: int | None = None
    competition_id: int | None = None
    competition_context: int = 0
    reference_token: tuple | None = None


@dataclass(frozen=True)
class PreparedKnockoutRound:
    shuffled_refs: tuple[CupClubRefDescriptor, ...]
    sorted_refs: tuple[CupClubRefDescriptor, ...]
    pairs: tuple[tuple[CupClubRefDescriptor, CupClubRefDescriptor], ...]


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


def primary_mode0_dummy_league_sort_source_ids(
    competitions: Iterable[CompetitionSource],
    allocation_instructions: Iterable[CupAllocationInstructionSource],
) -> tuple[int, ...]:
    """Return unique DummyLeague sources lazily sorted by primary Cup type-5 allocation.

    Type-5 allocation calls 0x4F4940 on the source competition before reading
    its ranking. Ordinary League uses deterministic 0x4F4720; DummyLeague
    dispatches RNG-bearing 0x4F4750. The sorted flag on source +0x40 means
    only the first such access per DummyLeague consumes RNG.
    """
    competition_by_id = {
        int(competition.id): competition
        for competition in competitions
    }
    result: list[int] = []
    seen: set[int] = set()
    for instruction in allocation_instructions:
        if int(instruction.instruction_type) != 5:
            continue
        destination = competition_by_id.get(
            int(instruction.destination_competition_id)
        )
        source = competition_by_id.get(int(instruction.source_reference))
        if destination is None or source is None:
            continue
        if int(destination.runtime_kind_code) != 2:
            continue
        if int(destination.schedule_container_code) in (2, 3):
            continue
        if int(source.runtime_kind_code) != 3:
            continue
        source_id = int(source.id)
        if source_id not in seen:
            seen.add(source_id)
            result.append(source_id)
    return tuple(result)


def primary_mode0_dummy_league_sort_draw_count(
    competitions: Iterable[CompetitionSource],
    allocation_instructions: Iterable[CupAllocationInstructionSource],
    clubs: Iterable[object],
) -> int:
    """Count one 0x64D540 call per member on each first DummyLeague lazy sort."""
    source_ids = set(
        primary_mode0_dummy_league_sort_source_ids(
            competitions,
            allocation_instructions,
        )
    )
    return sum(
        1
        for club in clubs
        if int(getattr(club, "competition_id", -1)) in source_ids
    )


def replay_primary_mode0_pre_shuffle_state(
    rng: RawCrtRng,
    competitions: Iterable[CompetitionSource],
    rounds: Iterable[RoundSource],
    clubs: Iterable[ClubSource],
    countries: Iterable[CountrySource],
    allocation_instructions: Iterable[CupAllocationInstructionSource] = (),
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
    dummy_league_sort_draw_count = primary_mode0_dummy_league_sort_draw_count(
        competition_list,
        tuple(allocation_instructions),
        club_list,
    )
    total_draw_count = (
        pairing_draw_count
        + dummy_league_sort_draw_count
        + selector_draw_count
    )

    for _ in range(total_draw_count):
        rng.rand15()

    state = int(getattr(rng, "state")) & 0xFFFFFFFF
    return PrimaryMode0PreShuffleStateReplay(
        primary_cup_round_count=len(team_counts),
        cup_pairing_draw_count=pairing_draw_count,
        dummy_league_sort_draw_count=dummy_league_sort_draw_count,
        europe_selector_draw_count=selector_draw_count,
        total_draw_count=total_draw_count,
        state_entering_primary_shuffle=state,
    )



def _compare_orderable(left, right) -> int:
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def msvc_crt_qsort(items, comparator):
    """Reproduce the VC-era CRT qsort at 0x668DA4.

    The executable uses an iterative quicksort with an eight-element cutoff.
    Ranges of <=8 elements go through 0x668EF8, a selection-style shortsort
    that is deliberately *not stable* for equal elements.

    Larger ranges:
    - swap the middle element to the low/pivot slot;
    - scan inward with <= / >= comparisons against the pivot;
    - swap the pivot into the final high-scan position;
    - process the smaller partition immediately and push the larger partition.

    Exact equal-element movement matters for Cup ClubRef ordering because
    comparator 0x4F67D0 returns zero for most non-type2 pairs.
    """
    result = list(items)
    if len(result) < 2:
        return tuple(result)

    stack: list[tuple[int, int]] = []
    low = 0
    high = len(result) - 1

    while True:
        count = high - low + 1
        if count <= 8:
            end = high
            while end > low:
                max_index = low
                for index in range(low + 1, end + 1):
                    if comparator(result[index], result[max_index]) > 0:
                        max_index = index
                result[max_index], result[end] = result[end], result[max_index]
                end -= 1

            if not stack:
                break
            low, high = stack.pop()
            continue

        middle = low + count // 2
        result[middle], result[low] = result[low], result[middle]

        low_scan = low
        high_scan = high + 1
        while True:
            low_scan += 1
            while (
                low_scan <= high
                and comparator(result[low_scan], result[low]) <= 0
            ):
                low_scan += 1

            high_scan -= 1
            while (
                high_scan > low
                and comparator(result[high_scan], result[low]) >= 0
            ):
                high_scan -= 1

            if high_scan < low_scan:
                break

            result[low_scan], result[high_scan] = (
                result[high_scan],
                result[low_scan],
            )

        result[low], result[high_scan] = result[high_scan], result[low]

        left = (low, high_scan - 1)
        right = (low_scan, high)
        left_count = max(0, left[1] - left[0] + 1)
        right_count = max(0, right[1] - right[0] + 1)

        # 0x668E8F branches when the left partition is strictly smaller,
        # pushing the larger partition and immediately processing the smaller.
        if left_count >= right_count:
            if left_count >= 2:
                stack.append(left)
            if right_count >= 2:
                low, high = right
                continue
        else:
            if right_count >= 2:
                stack.append(right)
            if left_count >= 2:
                low, high = left
                continue

        if not stack:
            break
        low, high = stack.pop()

    return tuple(result)


def _msvc_qsort_by_key(items, key):
    return msvc_crt_qsort(
        items,
        lambda left, right: _compare_orderable(key(left), key(right)),
    )


def _msvc_small_qsort_by_key(items, key):
    """Compatibility wrapper; exact CRT behavior now supports all sizes."""
    return _msvc_qsort_by_key(items, key)


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

        qsorted = _msvc_qsort_by_key(
            roots,
            lambda competition: -int(competition.initialization_order_value),
        )
        initialized = tuple(reversed(qsorted))

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


def initial_dummy_league_sort_entries(
    source_competition_id: int,
    clubs: Iterable[object],
    players: Iterable[DummyLeagueRatingPlayerSource],
) -> tuple[DummyLeagueSortEntry, ...]:
    """Build 0x4F4750's initial DummyLeague score/bound stream.

    Runtime team rosters are Master.dat player order filtered by club. 0x409900
    sums best-preferred-position rating (0x41E1D0) for at most the first 11
    roster players. 0x4F4750 then calls RNG(floor(score/20)) once per league
    member before sorting by score-roll.
    """
    source_competition_id = int(source_competition_id)
    players_by_club: dict[int, list[DummyLeagueRatingPlayerSource]] = {}
    for player in players:
        players_by_club.setdefault(int(player.club_id), []).append(player)

    result: list[DummyLeagueSortEntry] = []
    for club in clubs:
        if int(getattr(club, "competition_id", -1)) != source_competition_id:
            continue
        club_id = int(getattr(club, "index"))
        roster = players_by_club.get(club_id, ())
        score = sum(
            best_preferred_role_rating(
                tuple(int(value) for value in player.current_raw),
                tuple(int(value) for value in player.positions[:3]),
            )
            for player in roster[:11]
        )
        bound = score // 20
        if bound <= 0:
            raise ValueError(
                f"DummyLeague club {club_id} produced non-positive RNG bound {bound}"
            )
        result.append(
            DummyLeagueSortEntry(
                club_id=club_id,
                base_score=score,
                rng_bound=bound,
            )
        )
    return tuple(result)


def rank_dummy_league_for_type5(
    entries: Iterable[DummyLeagueSortEntry],
    rng: BoundedRng,
    quantity: int,
) -> tuple[DummyLeagueRankedEntry, ...]:
    """Return the exact prefix consumed by canonical type-5 Cup allocation.

    0x4F4750 consumes one bounded draw per DummyLeague participant and sorts
    temporary (LeagueClub*, score-roll) entries descending by randomized score.

    For arrays of <=16 elements the analyzed old-MSVC STL path is insertion
    sort; equal scores retain source order. Canonical multi-club type-5 reads
    all use such arrays.

    Canonical >16 DummyLeague sources are only read with quantity==1. For those
    sources the corrected startup replay produces a unique maximum, so the top
    club is exact without claiming the unresolved remainder of the old STL
    introsort order.
    """
    entry_list = tuple(entries)
    quantity = int(quantity)
    if quantity < 0 or quantity > len(entry_list):
        raise ValueError("quantity must be within the DummyLeague entry count")

    scored: list[DummyLeagueRankedEntry] = []
    for entry in entry_list:
        roll = int(rng.randbelow(int(entry.rng_bound)))
        scored.append(
            DummyLeagueRankedEntry(
                club_id=int(entry.club_id),
                base_score=int(entry.base_score),
                rng_bound=int(entry.rng_bound),
                roll=roll,
                randomized_score=int(entry.base_score) - roll,
            )
        )

    if len(scored) <= 16:
        # Exact old-STL insertion-sort semantics: move earlier elements only
        # while candidate score is strictly greater. Equal scores are stable.
        ordered: list[DummyLeagueRankedEntry] = []
        for candidate in scored:
            insert_at = len(ordered)
            while (
                insert_at > 0
                and candidate.randomized_score
                > ordered[insert_at - 1].randomized_score
            ):
                insert_at -= 1
            ordered.insert(insert_at, candidate)
        return tuple(ordered[:quantity])

    if quantity == 0:
        return ()
    if quantity != 1:
        raise ValueError(
            "exact >16 DummyLeague ordering beyond the unique top entry "
            "requires the full legacy STL introsort"
        )

    best_score = max(entry.randomized_score for entry in scored)
    best = tuple(
        entry for entry in scored if entry.randomized_score == best_score
    )
    if len(best) != 1:
        raise ValueError(
            "top DummyLeague randomized score is tied; legacy >16 sort "
            "tie behavior must be reproduced before selecting quantity 1"
        )
    return best


def replay_primary_mode0_ordered_competition_rng(
    rng: BoundedRng,
    competitions: Iterable[OrderedCompetitionSource],
    rounds: Iterable[OrderedRoundSource],
    clubs: Iterable[ClubSource],
    countries: Iterable[CountrySource],
    allocation_instructions: Iterable[CupAllocationInstructionSource] = (),
    players: Iterable[DummyLeagueRatingPlayerSource] = (),
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
    allocation_list = tuple(allocation_instructions)
    player_list = tuple(players)
    competition_by_id = {
        int(competition.id): competition
        for competition in competition_list
    }

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
    sorted_dummy_league_ids: set[int] = set()

    def current_state() -> int:
        return int(getattr(rng, "state", 0)) & 0xFFFFFFFF

    def visit(competition: OrderedCompetitionSource) -> None:
        nonlocal champions_league_club_id, uefa_cup_club_id

        if int(competition.schedule_container_code) in (2, 3):
            return

        if int(competition.runtime_kind_code) == 2:
            if allocation_list:
                for instruction in ordered_cup_allocation_instructions(
                    int(competition.id),
                    allocation_list,
                ):
                    if int(instruction.instruction_type) != 5:
                        continue
                    source = competition_by_id.get(int(instruction.source_reference))
                    if source is None or int(source.runtime_kind_code) != 3:
                        continue
                    source_id = int(source.id)
                    if source_id in sorted_dummy_league_ids:
                        continue
                    sorted_dummy_league_ids.add(source_id)
                    entries = initial_dummy_league_sort_entries(
                        source_id,
                        club_list,
                        player_list,
                    )
                    bounds: list[int] = []
                    for entry in entries:
                        rng.randbelow(int(entry.rng_bound))
                        bounds.append(int(entry.rng_bound))
                    events.append(
                        PrimaryMode0OrderedRngEvent(
                            kind="dummy_league_lazy_sort",
                            competition_id=int(competition.id),
                            round_id=None,
                            bounds=tuple(bounds),
                            pre_sort_slot_order=tuple(
                                int(entry.club_id) for entry in entries
                            ),
                            selected_club_id=None,
                            state_after=current_state(),
                        )
                    )

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
    return _msvc_qsort_by_key(
        selected,
        lambda instruction: int(instruction.sequence_index),
    )



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



class HistoricalCompetitionClubSource(Protocol):
    index: int
    competition_id: int
    historical_competition_id: int
    historical_slot_index: int


def initial_competition_enumeration_club_ids(
    clubs: Iterable[HistoricalCompetitionClubSource],
    competition_id: int,
) -> tuple[int | None, ...]:
    """Reproduce startup's competition +0x30 historical/qualification array.

    For ordinary League/Dummy/Scot competitions, capacity +0x3C is finalized
    from the number of current members before the array is allocated. The
    subsequent DBRClub pass uses packed club +32 as target competition and
    packed +36 as preferred slot.

    In-range preferred slots replace any occupant; a displaced club is put in
    the first empty slot. Out-of-range clubs also use the first empty slot.
    If no empty slot remains, 0x4F7BD0 silently leaves the extra club out.
    """
    club_list = tuple(clubs)
    competition_id = int(competition_id)
    capacity = sum(
        int(club.competition_id) == competition_id
        for club in club_list
    )
    slots: list[int | None] = [None] * capacity

    def insert_first_empty(club_id: int) -> None:
        for index, value in enumerate(slots):
            if value is None:
                slots[index] = int(club_id)
                return

    for club in club_list:
        if int(club.historical_competition_id) != competition_id:
            continue

        club_id = int(club.index)
        preferred = int(club.historical_slot_index)
        if 0 <= preferred < capacity:
            displaced = slots[preferred]
            slots[preferred] = club_id
            if displaced is not None:
                insert_first_empty(displaced)
        else:
            insert_first_empty(club_id)

    return tuple(slots)


def compare_cup_club_refs(
    left: CupClubRefDescriptor,
    right: CupClubRefDescriptor,
) -> int:
    """Reproduce ClubRef comparator 0x4F67D0."""
    left_type = int(left.type_code)
    right_type = int(right.type_code)

    if left_type == 2:
        if right_type != 2:
            return -1
        left_key = (
            int(left.competition_id if left.competition_id is not None else -1),
            int(left.competition_context),
        )
        right_key = (
            int(right.competition_id if right.competition_id is not None else -1),
            int(right.competition_context),
        )
        return _compare_orderable(left_key, right_key)

    if right_type == 2:
        return 1
    return 0


def prepare_cup_knockout_round(
    participant_refs: Iterable[CupClubRefDescriptor],
    rng: BoundedRng,
) -> PreparedKnockoutRound:
    """Reproduce NormalRound/TwoLegRound shuffle, qsort, and pairing."""
    shuffled = list(participant_refs)
    if len(shuffled) % 2:
        raise ValueError(
            "canonical primary knockout rounds have even participant counts"
        )

    for remaining in range(len(shuffled), 1, -1):
        selected = rng.randbelow(remaining)
        last = remaining - 1
        shuffled[selected], shuffled[last] = shuffled[last], shuffled[selected]

    ordered = msvc_crt_qsort(shuffled, compare_cup_club_refs)
    half = len(ordered) // 2
    pairs = tuple(
        (ordered[index], ordered[half + index])
        for index in range(half)
    )
    return PreparedKnockoutRound(
        shuffled_refs=tuple(shuffled),
        sorted_refs=ordered,
        pairs=pairs,
    )


def select_type5_direct_club_ids(
    ranked_club_ids: Iterable[int],
    quantity: int,
    *,
    already_in_destination: Iterable[int] = (),
    unavailable_direct_club_ids: Iterable[int] = (),
) -> tuple[int, ...]:
    """Reproduce 0x4F5F97's scan-until-N-successes behavior.

    Type-5 starts at source ranking index zero for every instruction. It
    advances the source index on every candidate, but increments its success
    count only when 0x4F5840 accepts the club. The instruction +0x1C
    auxiliary field is not consulted on this path.
    """
    quantity = int(quantity)
    if quantity < 0:
        raise ValueError("quantity must be non-negative")

    blocked = {int(value) for value in already_in_destination}
    blocked.update(int(value) for value in unavailable_direct_club_ids)

    selected: list[int] = []
    for club_id in ranked_club_ids:
        club_id = int(club_id)
        if club_id in blocked:
            continue
        selected.append(club_id)
        blocked.add(club_id)
        if len(selected) == quantity:
            break

    return tuple(selected)


@dataclass
class CupRoundAllocationBucket:
    round_id: int
    new_entrant_quota: int
    participant_refs: list[CupClubRefDescriptor]


def allocate_ref_to_latest_open_cup_round(
    round_buckets: list[CupRoundAllocationBucket],
    current_round_index: int,
    club_ref: CupClubRefDescriptor,
) -> int:
    """Reproduce 0x4F5790 -> 0x4F57E0 latest-round-first entrant filling."""
    index = int(current_round_index)
    while index >= 0:
        bucket = round_buckets[index]
        if len(bucket.participant_refs) < int(bucket.new_entrant_quota):
            bucket.participant_refs.append(club_ref)
            return index
        index -= 1
    return -1


@dataclass(frozen=True)
class StandardCupAllocationExpansion:
    round_buckets: tuple[CupRoundAllocationBucket, ...]
    emitted_refs: tuple[CupClubRefDescriptor, ...]
    dropped_refs: tuple[CupClubRefDescriptor, ...]
    source_position_offsets: tuple[tuple[int, int], ...]
    selected_direct_club_ids: tuple[int, ...]


def expand_standard_cup_allocation_instructions(
    destination_competition_id: int,
    sorted_rounds: Iterable[OrderedRoundSource],
    allocation_instructions: Iterable[CupAllocationInstructionSource],
    *,
    ranked_club_ids_by_source: dict[int, tuple[int, ...]],
    enumerated_club_ids_by_source: dict[int, tuple[int | None, ...]],
    unavailable_direct_club_ids: Iterable[int] = (),
    special_type2_refs_by_instruction_id: dict[
        int, tuple[CupClubRefDescriptor, ...]
    ] | None = None,
) -> StandardCupAllocationExpansion:
    """Expand canonical allocation types 1/3/4/5 into Cup round ClubRefs."""
    destination_competition_id = int(destination_competition_id)
    round_list = tuple(sorted_rounds)
    buckets = [
        CupRoundAllocationBucket(
            round_id=int(round_definition.id),
            new_entrant_quota=int(getattr(round_definition, "new_entrants")),
            participant_refs=[],
        )
        for round_definition in round_list
    ]
    current_round_index = len(buckets) - 1

    source_offsets: dict[int, int] = {}
    direct_ids: set[int] = set()
    unavailable = {int(value) for value in unavailable_direct_club_ids}
    special_type2_refs_by_instruction_id = (
        {} if special_type2_refs_by_instruction_id is None
        else special_type2_refs_by_instruction_id
    )
    emitted: list[CupClubRefDescriptor] = []
    dropped: list[CupClubRefDescriptor] = []

    def append_ref(ref: CupClubRefDescriptor) -> None:
        nonlocal current_round_index
        selected_round_index = allocate_ref_to_latest_open_cup_round(
            buckets,
            current_round_index,
            ref,
        )
        if selected_round_index < 0:
            # 0x4F57E0 silently ignores the ClubRef when 0x4F5790 reports that
            # every round has reached its new-entrant quota. Callers such as
            # 0x4F5840 still treat the direct-club allocation as successful
            # and update destination ownership state.
            current_round_index = -1
            dropped.append(ref)
            return
        current_round_index = selected_round_index
        emitted.append(ref)

    for instruction in ordered_cup_allocation_instructions(
        destination_competition_id,
        allocation_instructions,
    ):
        instruction_type = int(instruction.instruction_type)
        source_id = int(instruction.source_reference)
        quantity = int(instruction.quantity)

        if instruction_type == 4:
            source_offsets[source_id] = source_offsets.get(source_id, 0) + quantity
            continue

        if instruction_type == 1:
            start = source_offsets.get(source_id, 0)
            for selector in range(start, start + quantity):
                append_ref(
                    CupClubRefDescriptor(
                        type_code=2,
                        selector=selector,
                        competition_id=source_id,
                        competition_context=0,
                        reference_token=(
                            "competition_position",
                            source_id,
                            selector,
                        ),
                    )
                )
            source_offsets[source_id] = start + quantity
            continue

        if instruction_type == 3:
            source_ids = enumerated_club_ids_by_source.get(source_id)
            if source_ids is None:
                raise ValueError(f"missing type-3 enumeration for source {source_id}")
            for _ in range(quantity):
                selected = None
                for club_id in source_ids:
                    if club_id is None:
                        continue
                    club_id = int(club_id)
                    if club_id in direct_ids or club_id in unavailable:
                        continue
                    selected = club_id
                    break
                if selected is None:
                    raise ValueError(
                        f"type-3 source {source_id} ran out of eligible clubs"
                    )
                direct_ids.add(selected)
                append_ref(
                    CupClubRefDescriptor(
                        type_code=0,
                        direct_club_id=selected,
                        reference_token=("direct_club", selected),
                    )
                )
            continue

        if instruction_type == 5:
            source_ids = ranked_club_ids_by_source.get(source_id)
            if source_ids is None:
                raise ValueError(f"missing type-5 ranking for source {source_id}")
            selected_ids = select_type5_direct_club_ids(
                source_ids,
                quantity,
                already_in_destination=direct_ids,
                unavailable_direct_club_ids=unavailable,
            )
            if len(selected_ids) != quantity:
                raise ValueError(
                    f"type-5 source {source_id} produced {len(selected_ids)} "
                    f"of {quantity} requested clubs"
                )
            for club_id in selected_ids:
                club_id = int(club_id)
                direct_ids.add(club_id)
                append_ref(
                    CupClubRefDescriptor(
                        type_code=0,
                        direct_club_id=club_id,
                        reference_token=("direct_club", club_id),
                    )
                )
            continue

        if instruction_type == 2:
            supplied = special_type2_refs_by_instruction_id.get(
                int(instruction.id)
            )
            if supplied is None:
                raise NotImplementedError(
                    "allocation type 2 requires Champions-League transfer "
                    "descriptors"
                )
            if len(supplied) != quantity:
                raise ValueError(
                    f"type-2 instruction {int(instruction.id)} supplied "
                    f"{len(supplied)} refs for quantity {quantity}"
                )
            for ref in supplied:
                append_ref(ref)
            continue

        raise ValueError(
            f"unsupported Cup allocation instruction type {instruction_type}"
        )

    return StandardCupAllocationExpansion(
        round_buckets=tuple(buckets),
        emitted_refs=tuple(emitted),
        dropped_refs=tuple(dropped),
        source_position_offsets=tuple(sorted(source_offsets.items())),
        selected_direct_club_ids=tuple(sorted(direct_ids)),
    )



@dataclass(frozen=True)
class UefaTransferExpansion:
    source_round_id: int
    source_path: str
    refs: tuple[CupClubRefDescriptor, ...]


def expand_champions_league_to_uefa_transfer(
    source_sorted_rounds: Iterable[OrderedRoundSource],
    source_round_participant_refs: dict[int, tuple[CupClubRefDescriptor, ...]],
    *,
    source_round_index: int,
    quantity: int,
    child_rounds_by_competition: dict[int, tuple[OrderedRoundSource, ...]],
) -> UefaTransferExpansion:
    """Reproduce the two canonical allocation-type-2 UEFA transfer branches.

    The instruction auxiliary field indexes the source Champions League round
    array after Cup round qsort.

    Non-MiniLeague branch:
      - inspect the *next* source round;
      - scan its participant ClubRefs in order;
      - for each type-1 propagated winner ref, create type-1 selector=1
        against the same referenced match token (the losing/opposite side).

    MiniLeague branch:
      - use the selected MiniLeague round itself;
      - derive group size from the first round of its child League template;
      - group_count = source_round.team_count / group_size;
      - initial position index = group_size - 2;
      - emit group positions in reverse group order;
      - after one full group cycle, increment the position index.

    Canonical Champions League -> UEFA instructions use:
      aux=3, quantity=8  -> MiniLeague third-place transfers;
      aux=2, quantity=16 -> knockout losers feeding the same UEFA Cup.
    """
    rounds = tuple(source_sorted_rounds)
    source_round_index = int(source_round_index)
    quantity = int(quantity)

    if not 0 <= source_round_index < len(rounds):
        raise ValueError("source_round_index is outside the sorted Cup round array")
    if quantity < 0:
        raise ValueError("quantity must be non-negative")

    source_round = rounds[source_round_index]

    if int(source_round.type_code) != 3:
        next_index = source_round_index + 1
        if next_index >= len(rounds):
            raise ValueError(
                "non-MiniLeague UEFA transfer requires a following source round"
            )
        next_round = rounds[next_index]
        result: list[CupClubRefDescriptor] = []
        for ref in source_round_participant_refs.get(int(next_round.id), ()):
            if int(ref.type_code) != 1:
                continue
            if ref.reference_token is None:
                raise ValueError(
                    "propagated type-1 source ref lacks a match reference token"
                )
            result.append(
                CupClubRefDescriptor(
                    type_code=1,
                    selector=1,
                    reference_token=ref.reference_token,
                )
            )
            if len(result) == quantity:
                break
        if len(result) != quantity:
            raise ValueError(
                f"knockout loser transfer found {len(result)} of "
                f"{quantity} required propagated winner refs"
            )
        return UefaTransferExpansion(
            source_round_id=int(source_round.id),
            source_path="knockout_losers",
            refs=tuple(result),
        )

    child_competition_id = int(source_round.source_competition_reference) & 0xFFFF
    child_rounds = child_rounds_by_competition.get(child_competition_id, ())
    if not child_rounds:
        raise ValueError(
            f"MiniLeague source round {int(source_round.id)} has no child League rounds"
        )

    group_size = int(child_rounds[0].team_count)
    if group_size <= 0:
        raise ValueError("MiniLeague child group size must be positive")
    if int(source_round.team_count) % group_size:
        raise ValueError(
            "MiniLeague source team count is not divisible by child group size"
        )

    group_count = int(source_round.team_count) // group_size
    if group_count <= 0:
        raise ValueError("MiniLeague group count must be positive")

    position_index = group_size - 2
    remaining_group_counter = group_count
    result: list[CupClubRefDescriptor] = []

    for _ in range(quantity):
        remaining_group_counter -= 1
        group_index = remaining_group_counter
        result.append(
            CupClubRefDescriptor(
                type_code=3,
                selector=position_index,
                competition_id=child_competition_id,
                competition_context=group_index,
                reference_token=(
                    "group_position",
                    child_competition_id,
                    group_index,
                    position_index,
                ),
            )
        )
        if remaining_group_counter == 0:
            position_index += 1
            remaining_group_counter = group_count

    return UefaTransferExpansion(
        source_round_id=int(source_round.id),
        source_path="minileague_group_positions",
        refs=tuple(result),
    )


@dataclass(frozen=True)
class PreparedMiniLeagueRound:
    shuffled_refs: tuple[CupClubRefDescriptor, ...]
    sorted_refs: tuple[CupClubRefDescriptor, ...]
    groups: tuple[tuple[CupClubRefDescriptor, ...], ...]
    propagated_refs: tuple[CupClubRefDescriptor, ...]


def prepare_cup_minileague_round(
    participant_refs: Iterable[CupClubRefDescriptor],
    rng: BoundedRng,
    *,
    child_competition_id: int,
    group_size: int,
    next_round_existing_count: int = 0,
    next_round_capacity: int = 0,
) -> PreparedMiniLeagueRound:
    """Reproduce primary MiniLeague shuffle/distribution/qualification refs."""
    refs = list(participant_refs)
    group_size = int(group_size)
    if group_size <= 0:
        raise ValueError("group_size must be positive")
    if len(refs) % group_size:
        raise ValueError("MiniLeague participant count must divide into equal groups")

    for remaining in range(len(refs), 1, -1):
        selected = rng.randbelow(remaining)
        last = remaining - 1
        refs[selected], refs[last] = refs[last], refs[selected]

    ordered = msvc_crt_qsort(refs, compare_cup_club_refs)
    group_count = len(ordered) // group_size
    groups: list[list[CupClubRefDescriptor]] = [
        [] for _ in range(group_count)
    ]

    group_index = 0
    for ref in ordered:
        if int(ref.type_code) == 0:
            continue
        groups[group_index].append(ref)
        group_index += 1
        if group_index == group_count:
            group_index = 0

    for ref in ordered:
        if int(ref.type_code) != 0:
            continue
        groups[group_index].append(ref)
        group_index += 1
        if group_index == group_count:
            group_index = 0

    if any(len(group) != group_size for group in groups):
        raise ValueError("MiniLeague round-robin distribution produced uneven groups")

    needed = max(0, int(next_round_capacity) - int(next_round_existing_count))
    propagated: list[CupClubRefDescriptor] = []
    position_index = 0
    while len(propagated) < needed:
        for child_group_index in range(group_count):
            if len(propagated) == needed:
                break
            if position_index >= group_size:
                raise ValueError(
                    "next round requires more MiniLeague positions than available"
                )
            propagated.append(
                CupClubRefDescriptor(
                    type_code=2,
                    selector=position_index,
                    competition_id=int(child_competition_id),
                    competition_context=child_group_index,
                    reference_token=(
                        "group_position",
                        int(child_competition_id),
                        child_group_index,
                        position_index,
                    ),
                )
            )
        position_index += 1

    return PreparedMiniLeagueRound(
        shuffled_refs=tuple(refs),
        sorted_refs=ordered,
        groups=tuple(tuple(group) for group in groups),
        propagated_refs=tuple(propagated),
    )


@dataclass(frozen=True)
class CupPairingDescriptor:
    competition_id: int
    round_id: int
    round_type: int
    pair_index: int
    left_ref: CupClubRefDescriptor
    right_ref: CupClubRefDescriptor
    result_token: tuple


@dataclass(frozen=True)
class MaterializedCupRound:
    round_id: int
    round_type: int
    participant_refs: tuple[CupClubRefDescriptor, ...]
    pairings: tuple[CupPairingDescriptor, ...]
    minileague_groups: tuple[tuple[CupClubRefDescriptor, ...], ...] = ()


@dataclass(frozen=True)
class MaterializedCupRuntime:
    competition_id: int
    rounds: tuple[MaterializedCupRound, ...]
    round_participant_refs: tuple[
        tuple[int, tuple[CupClubRefDescriptor, ...]], ...
    ]


def materialize_cup_runtime_rounds(
    competition_id: int,
    sorted_rounds: Iterable[OrderedRoundSource],
    allocation_expansion: StandardCupAllocationExpansion,
    rng: BoundedRng,
    *,
    child_rounds_by_competition: dict[int, tuple[OrderedRoundSource, ...]],
) -> MaterializedCupRuntime:
    """Materialize parent-Cup round ClubRefs and pairings in startup order."""
    competition_id = int(competition_id)
    round_list = tuple(sorted_rounds)
    allocation_by_round = {
        int(bucket.round_id): list(bucket.participant_refs)
        for bucket in allocation_expansion.round_buckets
    }
    participant_refs_by_round = {
        int(round_definition.id): list(
            allocation_by_round.get(int(round_definition.id), ())
        )
        for round_definition in round_list
    }

    materialized: list[MaterializedCupRound] = []

    for round_index, round_definition in enumerate(round_list):
        round_id = int(round_definition.id)
        round_type = int(round_definition.type_code)
        current_refs = participant_refs_by_round[round_id]
        expected_count = int(round_definition.team_count)
        if len(current_refs) != expected_count:
            raise ValueError(
                f"Cup {competition_id} round {round_id} has "
                f"{len(current_refs)} refs before scheduling; expected "
                f"{expected_count}"
            )

        next_round = (
            round_list[round_index + 1]
            if round_index + 1 < len(round_list)
            else None
        )

        if round_type in (1, 2):
            prepared = prepare_cup_knockout_round(current_refs, rng)
            pairings: list[CupPairingDescriptor] = []
            for pair_index, (left_ref, right_ref) in enumerate(prepared.pairs):
                result_token = (
                    "cup_result",
                    competition_id,
                    round_id,
                    pair_index,
                )
                pairings.append(
                    CupPairingDescriptor(
                        competition_id=competition_id,
                        round_id=round_id,
                        round_type=round_type,
                        pair_index=pair_index,
                        left_ref=left_ref,
                        right_ref=right_ref,
                        result_token=result_token,
                    )
                )
                if next_round is not None:
                    participant_refs_by_round[int(next_round.id)].append(
                        CupClubRefDescriptor(
                            type_code=1,
                            selector=0,
                            reference_token=result_token,
                        )
                    )
            materialized.append(
                MaterializedCupRound(
                    round_id=round_id,
                    round_type=round_type,
                    participant_refs=prepared.sorted_refs,
                    pairings=tuple(pairings),
                )
            )
            continue

        if round_type == 3:
            child_competition_id = (
                int(round_definition.source_competition_reference) & 0xFFFF
            )
            child_rounds = child_rounds_by_competition.get(
                child_competition_id,
                (),
            )
            if not child_rounds:
                raise ValueError(
                    f"MiniLeague round {round_id} has no child League rounds"
                )
            group_size = int(child_rounds[0].team_count)
            next_existing = (
                len(participant_refs_by_round[int(next_round.id)])
                if next_round is not None
                else 0
            )
            next_capacity = (
                int(next_round.team_count)
                if next_round is not None
                else 0
            )
            prepared = prepare_cup_minileague_round(
                current_refs,
                rng,
                child_competition_id=child_competition_id,
                group_size=group_size,
                next_round_existing_count=next_existing,
                next_round_capacity=next_capacity,
            )
            if next_round is not None:
                participant_refs_by_round[int(next_round.id)].extend(
                    prepared.propagated_refs
                )
            materialized.append(
                MaterializedCupRound(
                    round_id=round_id,
                    round_type=round_type,
                    participant_refs=prepared.sorted_refs,
                    pairings=(),
                    minileague_groups=prepared.groups,
                )
            )
            continue

        raise ValueError(
            f"unsupported parent Cup round type {round_type}"
        )

    return MaterializedCupRuntime(
        competition_id=competition_id,
        rounds=tuple(materialized),
        round_participant_refs=tuple(
            (int(round_definition.id), tuple(participant_refs_by_round[int(round_definition.id)]))
            for round_definition in round_list
        ),
    )
