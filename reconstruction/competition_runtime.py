"""Complete primary competition RNG replay through 0x615BE0.

This layer extends the Cup-focused replay in competition_startup.py with the
randomized procedural-League round-robin generator reached through 0x6170F0.
The older 1,863-call Cup/DummyLeague/Europe stream remains useful as a subset,
but is not the final primary competition state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from competition_startup import (
    europe_root_cup_candidate_ids,
    initial_dummy_league_sort_entries,
    ordered_cup_allocation_instructions,
    primary_cup_round_initialization_order,
    primary_mode0_root_initialization_order,
)
from procedural_league import generate_procedural_league_round_robin


@dataclass(frozen=True)
class PrimaryCompetitionRuntimeRngEvent:
    kind: str
    competition_id: int
    competition_context: int
    round_id: int | None
    participant_count: int | None
    source_competition_id: int | None
    bounds: tuple[int, ...]
    selected_club_id: int | None
    state_after: int


@dataclass(frozen=True)
class PrimaryCompetitionRuntimeEventSpec:
    """RNG-independent competition-initialization event skeleton.

    Cup round shuffle bounds are deliberately absent here because the
    executable uses the runtime round's actual ClubRef count at +0x0C, which
    can be below the packed Static.dat team capacity after allocation
    filtering. The integrated materializer supplies that count immediately
    before each round scheduler runs.
    """

    kind: str
    competition_id: int
    competition_context: int
    round_id: int | None = None
    participant_count: int | None = None
    source_competition_id: int | None = None
    expected_bounds: tuple[int, ...] = ()
    selected_club_id: int | None = None


@dataclass(frozen=True)
class PrimaryMode0CompleteCompetitionRngReplay:
    events: tuple[PrimaryCompetitionRuntimeRngEvent, ...]
    procedural_league_instance_count: int
    procedural_league_draw_count: int
    primary_cup_round_count: int
    cup_pairing_draw_count: int
    dummy_league_sort_draw_count: int
    europe_selector_draw_count: int
    total_draw_count: int
    champions_league_club_id: int | None
    uefa_cup_club_id: int | None
    state_entering_primary_shuffle: int


def _state(rng) -> int:
    return int(getattr(rng, "state", 0)) & 0xFFFFFFFF


def _procedural_league_team_count(
    competition_id: int,
    clubs: tuple[object, ...],
    rounds_by_competition: dict[int, tuple[object, ...]],
) -> int:
    competition_id = int(competition_id)
    current_member_count = sum(
        int(getattr(club, "competition_id", -1)) == competition_id
        for club in clubs
    )
    if current_member_count:
        return current_member_count

    rounds = rounds_by_competition.get(competition_id, ())
    if not rounds:
        raise ValueError(
            f"procedural League {competition_id} has no current clubs or rounds"
        )
    return int(rounds[0].team_count)


def replay_primary_mode0_complete_competition_rng(
    rng,
    competitions: Iterable[object],
    rounds: Iterable[object],
    clubs: Iterable[object],
    countries: Iterable[object],
    allocation_instructions: Iterable[object] = (),
    players: Iterable[object] = (),
    *,
    fixed_fixture_competition_ids: Iterable[int] = (0,),
    include_zero_rng_competition_events: bool = False,
) -> PrimaryMode0CompleteCompetitionRngReplay:
    """Replay all currently proven primary competition RNG before 0x615BE0.

    Runtime initialization order is:
    - country/root order recovered by primary_mode0_root_initialization_order;
    - each competition's local initializer;
    - then child runtime objects in source-definition order, repeated according
      to packed DBRCompetition +8 / runtime +0x0C multiplicity.

    Ordinary procedural Leagues execute 0x6170F0's randomized round-robin
    solver before their child competitions. Competition 0 is fixed-fixture in
    the canonical release and is therefore excluded by default.

    Cup initialization retains the already recovered ordering: first-access
    DummyLeague type-5 ranking, Europe-root selector, then sorted Cup-round
    participant Fisher-Yates calls. DummyLeague root initialization itself does
    not execute the procedural League builder.
    """
    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    club_list = tuple(clubs)
    country_list = tuple(countries)
    instruction_list = tuple(allocation_instructions)
    player_list = tuple(players)
    fixed_ids = {int(value) for value in fixed_fixture_competition_ids}

    competition_by_id = {
        int(competition.id): competition
        for competition in competition_list
    }
    children: dict[int, list[object]] = {}
    for competition in competition_list:
        parent = getattr(competition, "parent_competition_id", None)
        if parent is not None:
            children.setdefault(int(parent), []).append(competition)

    rounds_by_competition: dict[int, list[object]] = {}
    for round_definition in round_list:
        rounds_by_competition.setdefault(
            int(round_definition.competition_id),
            [],
        ).append(round_definition)
    rounds_by_competition_tuple = {
        competition_id: tuple(values)
        for competition_id, values in rounds_by_competition.items()
    }

    candidates = europe_root_cup_candidate_ids(
        club_list,
        country_list,
        excluded_club_id=-1,
    )
    sorted_dummy_league_ids: set[int] = set()
    events: list[PrimaryCompetitionRuntimeRngEvent] = []
    champions_league_club_id: int | None = None
    uefa_cup_club_id: int | None = None

    def append_event(
        *,
        kind: str,
        competition_id: int,
        competition_context: int,
        bounds: tuple[int, ...],
        round_id: int | None = None,
        participant_count: int | None = None,
        source_competition_id: int | None = None,
        selected_club_id: int | None = None,
    ) -> None:
        events.append(
            PrimaryCompetitionRuntimeRngEvent(
                kind=kind,
                competition_id=int(competition_id),
                competition_context=int(competition_context),
                round_id=None if round_id is None else int(round_id),
                participant_count=(
                    None if participant_count is None else int(participant_count)
                ),
                source_competition_id=(
                    None
                    if source_competition_id is None
                    else int(source_competition_id)
                ),
                bounds=tuple(int(value) for value in bounds),
                selected_club_id=(
                    None if selected_club_id is None else int(selected_club_id)
                ),
                state_after=_state(rng),
            )
        )

    def visit(competition, competition_context: int) -> None:
        nonlocal champions_league_club_id, uefa_cup_club_id

        if int(competition.schedule_container_code) in (2, 3):
            return

        competition_id = int(competition.id)
        runtime_kind = int(competition.runtime_kind_code)

        if runtime_kind == 1 and competition_id not in fixed_ids:
            participant_count = _procedural_league_team_count(
                competition_id,
                club_list,
                rounds_by_competition_tuple,
            )
            replay = generate_procedural_league_round_robin(
                tuple(range(participant_count)),
                rng,
            )
            append_event(
                kind="procedural_league_round_robin",
                competition_id=competition_id,
                competition_context=competition_context,
                participant_count=participant_count,
                bounds=replay.bounds,
            )

        elif runtime_kind == 1 and include_zero_rng_competition_events:
            append_event(
                kind="fixed_league",
                competition_id=competition_id,
                competition_context=competition_context,
                participant_count=sum(
                    int(getattr(club, "competition_id", -1)) == competition_id
                    for club in club_list
                ),
                bounds=(),
            )

        elif runtime_kind == 2:
            for instruction in ordered_cup_allocation_instructions(
                competition_id,
                instruction_list,
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
                append_event(
                    kind="dummy_league_lazy_sort",
                    competition_id=competition_id,
                    competition_context=competition_context,
                    source_competition_id=source_id,
                    participant_count=len(entries),
                    bounds=tuple(bounds),
                )

            if (
                getattr(competition, "parent_competition_id", None) is None
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

                if competition_id == 9:
                    champions_league_club_id = selected
                elif competition_id == 10:
                    uefa_cup_club_id = selected

                append_event(
                    kind="europe_selector",
                    competition_id=competition_id,
                    competition_context=competition_context,
                    selected_club_id=selected,
                    bounds=bounds,
                )

            for round_definition in primary_cup_round_initialization_order(
                competition_id,
                round_list,
            ):
                participant_count = int(round_definition.team_count)
                bounds: list[int] = []
                for remaining in range(participant_count, 1, -1):
                    rng.randbelow(remaining)
                    bounds.append(remaining)
                append_event(
                    kind="cup_round_shuffle",
                    competition_id=competition_id,
                    competition_context=competition_context,
                    round_id=int(round_definition.id),
                    participant_count=participant_count,
                    bounds=tuple(bounds),
                )

        # Runtime child objects are constructed in source DBRCompetition order.
        # Packed +8 / runtime +0x0C is the child multiplicity.
        for child in children.get(competition_id, ()):
            multiplicity = int(getattr(child, "runtime_instance_count", 1))
            if multiplicity < 0:
                raise ValueError("runtime child competition multiplicity is negative")
            for child_context in range(multiplicity):
                visit(child, child_context)

    country_ids = tuple(int(country.id) for country in country_list)
    for root in primary_mode0_root_initialization_order(
        competition_list,
        country_ids,
    ):
        visit(root, 0)

    procedural_events = tuple(
        event
        for event in events
        if event.kind == "procedural_league_round_robin"
    )
    cup_events = tuple(
        event for event in events if event.kind == "cup_round_shuffle"
    )
    dummy_events = tuple(
        event for event in events if event.kind == "dummy_league_lazy_sort"
    )
    selector_events = tuple(
        event for event in events if event.kind == "europe_selector"
    )

    total_draw_count = sum(len(event.bounds) for event in events)
    return PrimaryMode0CompleteCompetitionRngReplay(
        events=tuple(events),
        procedural_league_instance_count=len(procedural_events),
        procedural_league_draw_count=sum(
            len(event.bounds) for event in procedural_events
        ),
        primary_cup_round_count=len(cup_events),
        cup_pairing_draw_count=sum(len(event.bounds) for event in cup_events),
        dummy_league_sort_draw_count=sum(
            len(event.bounds) for event in dummy_events
        ),
        europe_selector_draw_count=sum(
            len(event.bounds) for event in selector_events
        ),
        total_draw_count=total_draw_count,
        champions_league_club_id=champions_league_club_id,
        uefa_cup_club_id=uefa_cup_club_id,
        state_entering_primary_shuffle=_state(rng),
    )


def primary_mode0_competition_event_skeleton(
    competitions: Iterable[object],
    rounds: Iterable[object],
    clubs: Iterable[object],
    countries: Iterable[object],
    allocation_instructions: Iterable[object] = (),
    players: Iterable[object] = (),
    *,
    fixed_fixture_competition_ids: Iterable[int] = (0,),
    include_zero_rng_competition_events: bool = True,
) -> tuple[PrimaryCompetitionRuntimeEventSpec, ...]:
    """Build exact traversal markers without pre-consuming the CRT stream.

    This is the event-order companion to the older state replay. Procedural
    League participant counts and DummyLeague/Europe bounds are knowable before
    execution. Cup round bounds are not: 0x4F64D0/0x4F6820 read runtime
    round+0x0C after allocations and prior-round propagation, so the adaptive
    materializer fills those bounds from the live round immediately before the
    scheduler's Fisher-Yates loop.
    """
    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    club_list = tuple(clubs)
    country_list = tuple(countries)
    instruction_list = tuple(allocation_instructions)
    player_list = tuple(players)
    fixed_ids = {int(value) for value in fixed_fixture_competition_ids}

    competition_by_id = {
        int(competition.id): competition
        for competition in competition_list
    }
    children: dict[int, list[object]] = {}
    for competition in competition_list:
        parent = getattr(competition, "parent_competition_id", None)
        if parent is not None:
            children.setdefault(int(parent), []).append(competition)

    rounds_by_competition: dict[int, list[object]] = {}
    for round_definition in round_list:
        rounds_by_competition.setdefault(
            int(round_definition.competition_id),
            [],
        ).append(round_definition)
    rounds_by_competition_tuple = {
        competition_id: tuple(values)
        for competition_id, values in rounds_by_competition.items()
    }

    candidates = europe_root_cup_candidate_ids(
        club_list,
        country_list,
        excluded_club_id=-1,
    )
    sorted_dummy_league_ids: set[int] = set()
    events: list[PrimaryCompetitionRuntimeEventSpec] = []

    def visit(competition, competition_context: int) -> None:
        if int(competition.schedule_container_code) in (2, 3):
            return

        competition_id = int(competition.id)
        runtime_kind = int(competition.runtime_kind_code)

        if runtime_kind == 1 and competition_id not in fixed_ids:
            events.append(
                PrimaryCompetitionRuntimeEventSpec(
                    kind="procedural_league_round_robin",
                    competition_id=competition_id,
                    competition_context=int(competition_context),
                    participant_count=_procedural_league_team_count(
                        competition_id,
                        club_list,
                        rounds_by_competition_tuple,
                    ),
                )
            )
        elif runtime_kind == 1 and include_zero_rng_competition_events:
            events.append(
                PrimaryCompetitionRuntimeEventSpec(
                    kind="fixed_league",
                    competition_id=competition_id,
                    competition_context=int(competition_context),
                    participant_count=sum(
                        int(getattr(club, "competition_id", -1)) == competition_id
                        for club in club_list
                    ),
                )
            )
        elif runtime_kind == 2:
            for instruction in ordered_cup_allocation_instructions(
                competition_id,
                instruction_list,
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
                events.append(
                    PrimaryCompetitionRuntimeEventSpec(
                        kind="dummy_league_lazy_sort",
                        competition_id=competition_id,
                        competition_context=int(competition_context),
                        source_competition_id=source_id,
                        participant_count=len(entries),
                        expected_bounds=tuple(
                            int(entry.rng_bound) for entry in entries
                        ),
                    )
                )

            if (
                getattr(competition, "parent_competition_id", None) is None
                and int(competition.country_region_id) == 123
            ):
                if not candidates:
                    bounds = ()
                    selected = -1
                elif len(candidates) == 1:
                    bounds = ()
                    selected = int(candidates[0])
                else:
                    bounds = (len(candidates) - 1,)
                    selected = None
                events.append(
                    PrimaryCompetitionRuntimeEventSpec(
                        kind="europe_selector",
                        competition_id=competition_id,
                        competition_context=int(competition_context),
                        expected_bounds=bounds,
                        selected_club_id=selected,
                    )
                )

            for round_definition in primary_cup_round_initialization_order(
                competition_id,
                round_list,
            ):
                events.append(
                    PrimaryCompetitionRuntimeEventSpec(
                        kind="cup_round_shuffle",
                        competition_id=competition_id,
                        competition_context=int(competition_context),
                        round_id=int(round_definition.id),
                    )
                )

        for child in children.get(competition_id, ()):
            multiplicity = int(getattr(child, "runtime_instance_count", 1))
            if multiplicity < 0:
                raise ValueError("runtime child competition multiplicity is negative")
            for child_context in range(multiplicity):
                visit(child, child_context)

    country_ids = tuple(int(country.id) for country in country_list)
    for root in primary_mode0_root_initialization_order(
        competition_list,
        country_ids,
    ):
        visit(root, 0)

    return tuple(events)
