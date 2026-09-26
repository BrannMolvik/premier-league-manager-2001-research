"""End-to-end primary Cup startup materialization.

This module composes the individually recovered Gate-3 primitives in
competition_startup.py.  It deliberately owns orchestration rather than
reimplementing the legacy algorithms: root/child traversal, lazy DummyLeague
ranking, Cup allocation, UEFA transfers, Europe-root selectors, and round
scheduling all consume one shared bounded RNG in the executable order.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

from competition_schedule import (
    StartupScheduleNode,
    materialize_cup_round_schedule_nodes,
)
from competition_startup import (
    CupClubRefDescriptor,
    MaterializedCupRuntime,
    europe_root_cup_candidate_ids,
    expand_champions_league_to_uefa_transfer,
    expand_standard_cup_allocation_instructions,
    initial_competition_enumeration_club_ids,
    initial_cup_enumeration_club_ids,
    initial_dummy_league_sort_entries,
    initial_ranked_league_club_ids,
    materialize_cup_runtime_rounds,
    ordered_cup_allocation_instructions,
    primary_cup_round_initialization_order,
    primary_mode0_root_initialization_order,
    rank_dummy_league_for_type5,
    select_europe_root_cup_candidate,
)


@dataclass(frozen=True)
class MaterializedPrimaryCup:
    competition_id: int
    sorted_round_ids: tuple[int, ...]
    runtime: MaterializedCupRuntime
    dropped_ref_count: int
    selected_direct_club_ids: tuple[int, ...]
    injected_type2_instruction_ids: tuple[int, ...]
    selector_club_id: int | None


@dataclass(frozen=True)
class PrimaryCupRuntimeMaterialization:
    cups: tuple[MaterializedPrimaryCup, ...]
    ordered_bounds: tuple[int, ...]
    champions_league_club_id: int | None
    uefa_cup_club_id: int | None
    type2_injected_ref_count: int
    participant_sha256: str
    pairing_sha256: str
    cup_schedule_nodes: tuple[StartupScheduleNode, ...]
    cup_schedule_sha256: str
    state_after: int | None

    @property
    def draw_count(self) -> int:
        return len(self.ordered_bounds)

    @property
    def round_count(self) -> int:
        return sum(len(cup.runtime.rounds) for cup in self.cups)

    @property
    def dropped_ref_count(self) -> int:
        return sum(cup.dropped_ref_count for cup in self.cups)


class _TracingRng:
    def __init__(self, delegate):
        self.delegate = delegate
        self.bounds: list[int] = []

    def randbelow(self, bound: int) -> int:
        bound = int(bound)
        self.bounds.append(bound)
        return int(self.delegate.randbelow(bound))

    def begin_cup_round(
        self,
        competition_id: int,
        round_id: int,
        participant_count: int,
    ) -> None:
        hook = getattr(self.delegate, "begin_cup_round", None)
        if callable(hook):
            hook(
                int(competition_id),
                int(round_id),
                int(participant_count),
            )

    @property
    def state(self) -> int | None:
        value = getattr(self.delegate, "state", None)
        if value is None:
            return None
        return int(value) & 0xFFFFFFFF


def _ref_signature(ref: CupClubRefDescriptor):
    token = ref.reference_token
    if token is not None:
        token = list(token)
    return [
        int(ref.type_code),
        int(ref.selector),
        None if ref.direct_club_id is None else int(ref.direct_club_id),
        None if ref.competition_id is None else int(ref.competition_id),
        int(ref.competition_context),
        token,
    ]


def _digest_json(value) -> str:
    blob = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(blob).hexdigest()


def _runtime_digests(
    cups: Iterable[MaterializedPrimaryCup],
) -> tuple[str, str]:
    participant_payload = []
    pairing_payload = []

    for cup in cups:
        for runtime_round in cup.runtime.rounds:
            participant_payload.append(
                [
                    int(cup.competition_id),
                    int(runtime_round.round_id),
                    int(runtime_round.round_type),
                    [_ref_signature(ref) for ref in runtime_round.participant_refs],
                ]
            )
            pairing_payload.append(
                [
                    int(cup.competition_id),
                    int(runtime_round.round_id),
                    [
                        [
                            int(pair.pair_index),
                            _ref_signature(pair.left_ref),
                            _ref_signature(pair.right_ref),
                            list(pair.result_token),
                        ]
                        for pair in runtime_round.pairings
                    ],
                    [
                        [_ref_signature(ref) for ref in group]
                        for group in runtime_round.minileague_groups
                    ],
                ]
            )

    return (
        _digest_json(participant_payload),
        _digest_json(pairing_payload),
    )


def materialize_primary_cup_runtime(
    rng,
    competitions: Iterable[object],
    rounds: Iterable[object],
    clubs: Iterable[object],
    countries: Iterable[object],
    allocation_instructions: Iterable[object],
    players: Iterable[object] = (),
    *,
    cup_enumerated_club_ids_by_source: dict[
        int, tuple[int | None, ...]
    ] | None = None,
) -> PrimaryCupRuntimeMaterialization:
    """Materialize every primary-container Cup in executable startup order.

    The caller supplies the shared CRT-compatible bounded RNG at the state that
    enters primary competition initialization.  For the canonical synthetic
    Gate-3 checkpoint that is MsvcCrtRng(0x2797444C).

    Cup allocation type 3 normally reads the dedicated League/DummyLeague/
    ScotPremierLeague historical-enumeration array, which is reconstructed
    directly from Master.dat fields.  The legacy Cup-source enumerator instead
    exposes Cup+0x40/+0x44; callers must supply those rare values explicitly
    through cup_enumerated_club_ids_by_source if such a source is encountered.
    This routine raises rather than approximating that pointer state.

    The returned ordered_bounds is the actual unified bounded-call stream used
    by lazy DummyLeague ranking, Europe selectors, and all Cup round shuffles.
    """
    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    club_list = tuple(clubs)
    country_list = tuple(countries)
    instruction_list = tuple(allocation_instructions)
    player_list = tuple(players)
    cup_enumerations = (
        {}
        if cup_enumerated_club_ids_by_source is None
        else {
            int(key): tuple(value)
            for key, value in cup_enumerated_club_ids_by_source.items()
        }
    )

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
    child_rounds_by_competition = {
        competition_id: tuple(values)
        for competition_id, values in rounds_by_competition.items()
    }

    tracing_rng = _TracingRng(rng)
    europe_candidates = europe_root_cup_candidate_ids(
        club_list,
        country_list,
        excluded_club_id=-1,
    )

    ranked_club_ids_by_source: dict[int, tuple[int, ...]] = {}
    enumerated_club_ids_by_source: dict[int, tuple[int | None, ...]] = {}
    materialized_by_competition: dict[int, MaterializedPrimaryCup] = {}
    sorted_rounds_by_cup: dict[int, tuple[object, ...]] = {}
    europe_assigned_direct_club_ids: set[int] = set()
    materialized_cups: list[MaterializedPrimaryCup] = []

    champions_league_club_id: int | None = None
    uefa_cup_club_id: int | None = None
    type2_injected_ref_count = 0

    def ranking_for_type5(source_id: int) -> tuple[int, ...]:
        source_id = int(source_id)
        existing = ranked_club_ids_by_source.get(source_id)
        if existing is not None:
            return existing

        source = competition_by_id.get(source_id)
        if source is None:
            raise ValueError(f"missing type-5 source competition {source_id}")

        runtime_kind = int(source.runtime_kind_code)
        if runtime_kind == 3:
            entries = initial_dummy_league_sort_entries(
                source_id,
                club_list,
                player_list,
            )
            if len(entries) <= 16:
                ranked = rank_dummy_league_for_type5(
                    entries,
                    tracing_rng,
                    len(entries),
                )
            else:
                # The recovered canonical >16 DummyLeague sources are consumed
                # only for their unique leading club.  The helper refuses any
                # stronger ordering claim for the old STL introsort tail.
                ranked = rank_dummy_league_for_type5(
                    entries,
                    tracing_rng,
                    1,
                )
            result = tuple(int(entry.club_id) for entry in ranked)
        elif runtime_kind == 1:
            result = initial_ranked_league_club_ids(club_list, source_id)
        else:
            raise ValueError(
                f"type-5 source {source_id} is runtime kind {runtime_kind}, "
                "not a League/DummyLeague"
            )

        ranked_club_ids_by_source[source_id] = result
        return result

    def enumeration_for_type3(source_id: int) -> tuple[int | None, ...]:
        source_id = int(source_id)
        existing = enumerated_club_ids_by_source.get(source_id)
        if existing is not None:
            return existing

        source = competition_by_id.get(source_id)
        if source is None:
            raise ValueError(f"missing type-3 source competition {source_id}")

        runtime_kind = int(source.runtime_kind_code)
        if runtime_kind in (1, 3):
            result = initial_competition_enumeration_club_ids(
                club_list,
                source_id,
            )
        elif runtime_kind == 2:
            if source_id in cup_enumerations:
                result = cup_enumerations[source_id]
            else:
                result = initial_cup_enumeration_club_ids(source)
        else:
            raise ValueError(
                f"type-3 source {source_id} has unsupported runtime kind "
                f"{runtime_kind}"
            )

        enumerated_club_ids_by_source[source_id] = tuple(result)
        return tuple(result)

    def visit(competition) -> None:
        nonlocal champions_league_club_id
        nonlocal uefa_cup_club_id
        nonlocal type2_injected_ref_count

        if int(competition.schedule_container_code) in (2, 3):
            return

        competition_id = int(competition.id)

        if int(competition.runtime_kind_code) == 2:
            sorted_rounds = primary_cup_round_initialization_order(
                competition_id,
                round_list,
            )
            sorted_rounds_by_cup[competition_id] = tuple(sorted_rounds)
            ordered_instructions = ordered_cup_allocation_instructions(
                competition_id,
                instruction_list,
            )

            # 0x4F4940 lazily sorts a DummyLeague on first type-5 access.
            # Non-Dummy type-5 rankings are deterministic at startup.
            for instruction in ordered_instructions:
                if int(instruction.instruction_type) == 5:
                    ranking_for_type5(int(instruction.source_reference))

            # Build every deterministic type-3 source array before allocation.
            for instruction in ordered_instructions:
                if int(instruction.instruction_type) == 3:
                    enumeration_for_type3(int(instruction.source_reference))

            special_type2_refs: dict[int, tuple[CupClubRefDescriptor, ...]] = {}
            injected_ids: list[int] = []
            for instruction in ordered_instructions:
                if int(instruction.instruction_type) != 2:
                    continue
                source_id = int(instruction.source_reference)
                source_materialized = materialized_by_competition.get(source_id)
                source_rounds = sorted_rounds_by_cup.get(source_id)
                if source_materialized is None or source_rounds is None:
                    raise ValueError(
                        f"type-2 instruction {int(instruction.id)} references "
                        f"Cup {source_id} before it has been materialized"
                    )
                transfer = expand_champions_league_to_uefa_transfer(
                    source_rounds,
                    dict(source_materialized.runtime.round_participant_refs),
                    source_round_index=int(instruction.auxiliary),
                    quantity=int(instruction.quantity),
                    child_rounds_by_competition=child_rounds_by_competition,
                )
                special_type2_refs[int(instruction.id)] = transfer.refs
                injected_ids.append(int(instruction.id))
                type2_injected_ref_count += len(transfer.refs)

            unavailable = (
                europe_assigned_direct_club_ids
                if int(competition.country_region_id) == 123
                else ()
            )
            expansion = expand_standard_cup_allocation_instructions(
                competition_id,
                sorted_rounds,
                ordered_instructions,
                ranked_club_ids_by_source=ranked_club_ids_by_source,
                enumerated_club_ids_by_source=enumerated_club_ids_by_source,
                unavailable_direct_club_ids=unavailable,
                special_type2_refs_by_instruction_id=special_type2_refs,
            )

            if int(competition.country_region_id) == 123:
                europe_assigned_direct_club_ids.update(
                    int(value)
                    for value in expansion.selected_direct_club_ids
                )

            selector_club_id: int | None = None
            if (
                getattr(competition, "parent_competition_id", None) is None
                and int(competition.country_region_id) == 123
            ):
                selector_club_id = select_europe_root_cup_candidate(
                    europe_candidates,
                    tracing_rng,
                )
                if competition_id == 9:
                    champions_league_club_id = selector_club_id
                elif competition_id == 10:
                    uefa_cup_club_id = selector_club_id

            runtime = materialize_cup_runtime_rounds(
                competition_id,
                sorted_rounds,
                expansion,
                tracing_rng,
                child_rounds_by_competition=child_rounds_by_competition,
            )
            cup_result = MaterializedPrimaryCup(
                competition_id=competition_id,
                sorted_round_ids=tuple(
                    int(round_definition.id)
                    for round_definition in sorted_rounds
                ),
                runtime=runtime,
                dropped_ref_count=len(expansion.dropped_refs),
                selected_direct_club_ids=tuple(
                    int(value)
                    for value in expansion.selected_direct_club_ids
                ),
                injected_type2_instruction_ids=tuple(injected_ids),
                selector_club_id=selector_club_id,
            )
            materialized_by_competition[competition_id] = cup_result
            materialized_cups.append(cup_result)

        for child in children.get(competition_id, ()):
            visit(child)

    country_ids = tuple(int(country.id) for country in country_list)
    for root in primary_mode0_root_initialization_order(
        competition_list,
        country_ids,
    ):
        visit(root)

    cups = tuple(materialized_cups)
    participant_digest, pairing_digest = _runtime_digests(cups)

    round_by_id = {
        int(round_definition.id): round_definition
        for round_definition in round_list
    }
    cup_schedule_nodes_list: list[StartupScheduleNode] = []
    for cup in cups:
        for runtime_round in cup.runtime.rounds:
            round_definition = round_by_id.get(int(runtime_round.round_id))
            if round_definition is None:
                raise ValueError(
                    f"missing round definition {int(runtime_round.round_id)} "
                    f"for Cup {int(cup.competition_id)}"
                )
            cup_schedule_nodes_list.extend(
                materialize_cup_round_schedule_nodes(
                    runtime_round,
                    round_definition,
                    competition_id=int(cup.competition_id),
                )
            )
    cup_schedule_nodes = tuple(cup_schedule_nodes_list)
    cup_schedule_digest = _digest_json(
        [
            [
                node.node_kind,
                int(node.competition_id),
                int(node.competition_context),
                None if node.round_id is None else int(node.round_id),
                int(node.pair_index),
                None if node.schedule_index is None else int(node.schedule_index),
                None if node.scheduled_week is None else int(node.scheduled_week),
                None
                if node.scheduled_weekday is None
                else int(node.scheduled_weekday),
                _ref_signature(node.participant_0_ref),
                _ref_signature(node.participant_1_ref),
                list(node.node_token),
            ]
            for node in cup_schedule_nodes
        ]
    )

    return PrimaryCupRuntimeMaterialization(
        cups=cups,
        ordered_bounds=tuple(tracing_rng.bounds),
        champions_league_club_id=champions_league_club_id,
        uefa_cup_club_id=uefa_cup_club_id,
        type2_injected_ref_count=type2_injected_ref_count,
        participant_sha256=participant_digest,
        pairing_sha256=pairing_digest,
        cup_schedule_nodes=cup_schedule_nodes,
        cup_schedule_sha256=cup_schedule_digest,
        state_after=tracing_rng.state,
    )
