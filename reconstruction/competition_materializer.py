"""Integrated RNG-driven primary competition startup materialization.

This module composes the verified complete primary competition RNG replay with
the exact Cup runtime materializer and procedural League schedule descriptors.
It preserves one real MSVC CRT stream: procedural-League solvers are injected
at their recovered competition-initialization positions while the Cup
materializer consumes its own bounded calls.

Fixed real-fixture Leagues consume no pre-0x615BE0 RNG. They are represented
by explicit zero-draw traversal markers so their LeagueMatch nodes retain the
correct position relative to procedural League and Cup initialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

from competition_runtime import (
    PrimaryCompetitionRuntimeEventSpec,
    PrimaryCompetitionRuntimeRngEvent,
    primary_mode0_competition_event_skeleton,
)
from competition_schedule import (
    StartupScheduleNode,
    direct_club_ref,
    materialize_cup_round_schedule_nodes,
    materialize_fixed_league_schedule_nodes,
    materialize_procedural_league_schedule_nodes,
    materialize_scot_premier_split_schedule_nodes,
    ordered_league_schedule_entries,
)
from competition_startup import (
    CupClubRefDescriptor,
    expand_league_position_allocation_instructions,
    initial_league_club_ids,
)
from cup_runtime import (
    PrimaryCupRuntimeMaterialization,
    materialize_primary_cup_runtime,
)
from procedural_league import (
    ProceduralLeagueMatchEmission,
    ProceduralLeagueRoundRobin,
    generate_procedural_league_round_robin,
    materialize_procedural_league_match_emissions,
    materialize_scot_premier_split_match_emissions,
)


@dataclass(frozen=True)
class PrimaryRngDrivenScheduleMaterialization:
    """Primary Cup + procedural-League state before the global bucket shuffle."""

    rng_plan_total_draw_count: int
    rng_plan_event_count: int
    rng_bounds_sha256: str
    rng_events: tuple[PrimaryCompetitionRuntimeRngEvent, ...]
    cup_runtime: PrimaryCupRuntimeMaterialization
    schedule_nodes: tuple[StartupScheduleNode, ...]
    schedule_sha256: str
    state_entering_primary_shuffle: int

    @property
    def schedule_node_count(self) -> int:
        return len(self.schedule_nodes)


class _InterleavingCompetitionRng:
    """Consume the exact competition event skeleton on one live CRT stream.

    Procedural League RNG is injected at recovered traversal positions.
    DummyLeague/Europe events verify their known bounds. Cup round bounds are
    supplied by begin_cup_round() from the runtime round's actual +0x0C
    ClubRef count immediately before its Fisher-Yates loop.
    """

    def __init__(
        self,
        delegate,
        event_specs: tuple[PrimaryCompetitionRuntimeEventSpec, ...],
    ):
        self.delegate = delegate
        self.event_specs = event_specs
        self.event_index = 0
        self.bound_index = 0
        self.active_cup_bounds: tuple[int, ...] | None = None
        self.active_cup_participant_count: int | None = None
        self.events: list[PrimaryCompetitionRuntimeRngEvent] = []
        self.league_round_robins: dict[
            tuple[int, int], ProceduralLeagueRoundRobin
        ] = {}

    @property
    def state(self) -> int:
        return int(getattr(self.delegate, "state")) & 0xFFFFFFFF

    def _record_event(
        self,
        spec: PrimaryCompetitionRuntimeEventSpec,
        bounds: tuple[int, ...],
        *,
        participant_count: int | None = None,
        selected_club_id: int | None = None,
    ) -> None:
        self.events.append(
            PrimaryCompetitionRuntimeRngEvent(
                kind=spec.kind,
                competition_id=int(spec.competition_id),
                competition_context=int(spec.competition_context),
                round_id=(
                    None if spec.round_id is None else int(spec.round_id)
                ),
                participant_count=(
                    spec.participant_count
                    if participant_count is None
                    else int(participant_count)
                ),
                source_competition_id=(
                    None
                    if spec.source_competition_id is None
                    else int(spec.source_competition_id)
                ),
                bounds=tuple(int(value) for value in bounds),
                selected_club_id=(
                    spec.selected_club_id
                    if selected_club_id is None
                    else int(selected_club_id)
                ),
                state_after=self.state,
            )
        )

    def _advance_event(self) -> None:
        self.event_index += 1
        self.bound_index = 0
        self.active_cup_bounds = None
        self.active_cup_participant_count = None

    def _drain_internal_events(self) -> None:
        while self.event_index < len(self.event_specs):
            spec = self.event_specs[self.event_index]

            if spec.kind == "procedural_league_round_robin":
                if spec.participant_count is None:
                    raise RuntimeError(
                        "procedural League event has no participant count"
                    )
                replay = generate_procedural_league_round_robin(
                    tuple(range(int(spec.participant_count))),
                    self.delegate,
                )
                key = (
                    int(spec.competition_id),
                    int(spec.competition_context),
                )
                if key in self.league_round_robins:
                    raise RuntimeError(
                        f"duplicate procedural League runtime {key}"
                    )
                self.league_round_robins[key] = replay
                self._record_event(
                    spec,
                    tuple(replay.bounds),
                    participant_count=int(spec.participant_count),
                )
                self._advance_event()
                continue

            if spec.kind == "fixed_league":
                self._record_event(spec, ())
                self._advance_event()
                continue

            if (
                spec.kind in ("dummy_league_lazy_sort", "europe_selector")
                and not spec.expected_bounds
            ):
                self._record_event(spec, ())
                self._advance_event()
                continue

            return

    def begin_cup_round(
        self,
        competition_id: int,
        round_id: int,
        participant_count: int,
    ) -> None:
        self._drain_internal_events()
        if self.event_index >= len(self.event_specs):
            raise RuntimeError(
                f"unexpected Cup round {competition_id}/{round_id} after event plan"
            )
        spec = self.event_specs[self.event_index]
        if (
            spec.kind != "cup_round_shuffle"
            or int(spec.competition_id) != int(competition_id)
            or spec.round_id is None
            or int(spec.round_id) != int(round_id)
        ):
            raise RuntimeError(
                "Cup round traversal diverged from competition event skeleton: "
                f"expected {spec.kind} {spec.competition_id}/{spec.round_id}, "
                f"received {competition_id}/{round_id}"
            )
        if self.active_cup_bounds is not None:
            raise RuntimeError("previous Cup round RNG event is still active")

        participant_count = int(participant_count)
        if participant_count < 0:
            raise ValueError("Cup participant count must be non-negative")
        self.active_cup_participant_count = participant_count
        self.active_cup_bounds = tuple(
            range(participant_count, 1, -1)
        )
        self.bound_index = 0

        if not self.active_cup_bounds:
            self._record_event(
                spec,
                (),
                participant_count=participant_count,
            )
            self._advance_event()

    def randbelow(self, bound: int) -> int:
        bound = int(bound)
        self._drain_internal_events()
        if self.event_index >= len(self.event_specs):
            raise RuntimeError(f"unexpected trailing RNG({bound})")

        spec = self.event_specs[self.event_index]
        if spec.kind == "cup_round_shuffle":
            if self.active_cup_bounds is None:
                raise RuntimeError(
                    "Cup scheduler called RNG before reporting its actual "
                    "runtime participant count"
                )
            expected_bounds = self.active_cup_bounds
        elif spec.kind in ("dummy_league_lazy_sort", "europe_selector"):
            expected_bounds = tuple(spec.expected_bounds)
        else:
            raise RuntimeError(
                f"external RNG({bound}) reached unexpected event {spec.kind}"
            )

        if self.bound_index >= len(expected_bounds):
            raise RuntimeError(
                f"RNG event {spec.kind} exceeded its recovered bound sequence"
            )
        expected = int(expected_bounds[self.bound_index])
        if expected != bound:
            raise RuntimeError(
                f"RNG interleave mismatch at {spec.kind}: expected "
                f"RNG({expected}), received RNG({bound})"
            )

        value = int(self.delegate.randbelow(bound))
        self.bound_index += 1
        if self.bound_index == len(expected_bounds):
            self._record_event(
                spec,
                expected_bounds,
                participant_count=(
                    self.active_cup_participant_count
                    if spec.kind == "cup_round_shuffle"
                    else spec.participant_count
                ),
            )
            self._advance_event()
        return value

    def finish(self) -> None:
        self._drain_internal_events()
        if self.event_index != len(self.event_specs):
            spec = self.event_specs[self.event_index]
            raise RuntimeError(
                "competition materializer did not consume the complete event "
                f"skeleton; next event is {spec.kind} "
                f"{spec.competition_id}/{spec.round_id}"
            )
        if self.active_cup_bounds is not None:
            raise RuntimeError("competition materializer ended mid-Cup shuffle")


def _mapped_league_replay(
    replay: ProceduralLeagueRoundRobin,
    participant_refs: tuple[CupClubRefDescriptor, ...],
) -> ProceduralLeagueRoundRobin:
    """Replace placeholder slot integers with exact ClubRef descriptors."""
    if len(participant_refs) != len(replay.rounds) + 1:
        raise ValueError("procedural League participant count does not match replay")

    mapped_rounds = []
    for round_pairs in replay.rounds:
        mapped_rounds.append(
            tuple(
                (
                    participant_refs[int(left)],
                    participant_refs[int(right)],
                )
                for left, right in round_pairs
            )
        )
    return ProceduralLeagueRoundRobin(
        rounds=tuple(mapped_rounds),
        bounds=tuple(replay.bounds),
        state_after=replay.state_after,
    )


def _node_digest(nodes: tuple[StartupScheduleNode, ...]) -> str:
    payload = []
    for node in nodes:
        refs = []
        for ref in (node.participant_0_ref, node.participant_1_ref):
            refs.append(
                [
                    int(ref.type_code),
                    int(ref.selector),
                    None if ref.direct_club_id is None else int(ref.direct_club_id),
                    None if ref.competition_id is None else int(ref.competition_id),
                    int(ref.competition_context),
                    None
                    if ref.reference_token is None
                    else list(ref.reference_token),
                ]
            )
        payload.append(
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
                refs,
                list(node.node_token),
            ]
        )
    blob = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(blob).hexdigest()


def materialize_primary_rng_driven_schedule(
    rng,
    competitions: Iterable[object],
    rounds: Iterable[object],
    clubs: Iterable[object],
    countries: Iterable[object],
    allocation_instructions: Iterable[object],
    players: Iterable[object] = (),
    *,
    fixed_fixture_competition_ids: Iterable[int] = (0,),
    real_fixtures: Iterable[object] = (),
    cup_enumerated_club_ids_by_source: dict[
        int, tuple[int | None, ...]
    ] | None = None,
) -> PrimaryRngDrivenScheduleMaterialization:
    """Materialize Cup and procedural-League nodes on one exact CRT stream.

    The event plan is produced on a cloned MSVC state, so it does not mutate
    the caller's RNG.  The real RNG is then consumed exactly once by the
    interleaving adapter and existing Cup materializer.

    Procedural League participants are exact when they are:
    - MiniLeague groups already materialized by the parent Cup;
    - current direct members of the League in Master.dat; or
    - type-2 source-position ClubRefs created by League::Initialize helper
      0x4F4FD0 from the League's allocation-instruction vector.

    If those recovered sources do not yield the expected participant count,
    this routine raises instead of manufacturing participant identities.
    """
    start_state = getattr(rng, "state", None)
    if start_state is None:
        raise TypeError("integrated materialization requires an RNG with CRT state")

    competition_list = tuple(competitions)
    round_list = tuple(rounds)
    club_list = tuple(clubs)
    country_list = tuple(countries)
    instruction_list = tuple(allocation_instructions)
    player_list = tuple(players)
    fixed_ids = tuple(int(value) for value in fixed_fixture_competition_ids)
    real_fixture_list = tuple(real_fixtures)

    event_specs = primary_mode0_competition_event_skeleton(
        competition_list,
        round_list,
        club_list,
        country_list,
        instruction_list,
        player_list,
        fixed_fixture_competition_ids=fixed_ids,
        include_zero_rng_competition_events=True,
    )

    interleaved_rng = _InterleavingCompetitionRng(
        rng,
        tuple(event_specs),
    )
    cup_runtime = materialize_primary_cup_runtime(
        interleaved_rng,
        competition_list,
        round_list,
        club_list,
        country_list,
        instruction_list,
        player_list,
        cup_enumerated_club_ids_by_source=cup_enumerated_club_ids_by_source,
    )
    interleaved_rng.finish()

    competition_by_id = {
        int(competition.id): competition
        for competition in competition_list
    }
    rounds_by_competition: dict[int, list[object]] = {}
    round_by_id: dict[int, object] = {}
    for round_definition in round_list:
        round_by_id[int(round_definition.id)] = round_definition
        rounds_by_competition.setdefault(
            int(round_definition.competition_id), []
        ).append(round_definition)

    cup_round_nodes: dict[tuple[int, int], tuple[StartupScheduleNode, ...]] = {}
    mini_league_participants: dict[
        tuple[int, int], tuple[CupClubRefDescriptor, ...]
    ] = {}
    for cup in cup_runtime.cups:
        for runtime_round in cup.runtime.rounds:
            round_definition = round_by_id[int(runtime_round.round_id)]
            key = (int(cup.competition_id), int(runtime_round.round_id))
            cup_round_nodes[key] = materialize_cup_round_schedule_nodes(
                runtime_round,
                round_definition,
                competition_id=int(cup.competition_id),
            )
            if int(runtime_round.round_type) == 3:
                child_competition_id = (
                    int(round_definition.source_competition_reference) & 0xFFFF
                )
                for context, group in enumerate(runtime_round.minileague_groups):
                    mini_league_participants[
                        (child_competition_id, context)
                    ] = tuple(group)

    league_nodes: dict[tuple[int, int], tuple[StartupScheduleNode, ...]] = {}
    for event in interleaved_rng.events:
        if event.kind != "procedural_league_round_robin":
            continue
        key = (int(event.competition_id), int(event.competition_context))
        replay = interleaved_rng.league_round_robins[key]
        participant_count = int(event.participant_count or 0)

        refs = mini_league_participants.get(key)
        if refs is None:
            direct_ids = initial_league_club_ids(
                club_list,
                int(event.competition_id),
            )
            if len(direct_ids) == participant_count:
                refs = tuple(direct_club_ref(club_id) for club_id in direct_ids)
            else:
                allocation_expansion = (
                    expand_league_position_allocation_instructions(
                        int(event.competition_id),
                        instruction_list,
                    )
                )
                if len(allocation_expansion.participant_refs) == participant_count:
                    refs = allocation_expansion.participant_refs
                else:
                    raise ValueError(
                        f"procedural League {key} requires {participant_count} "
                        f"participants, but direct membership provides "
                        f"{len(direct_ids)} and League allocation helper "
                        f"0x4F4FD0 provides "
                        f"{len(allocation_expansion.participant_refs)}"
                    )

        if len(refs) != participant_count:
            raise ValueError(
                f"procedural League {key} participant source has "
                f"{len(refs)} refs; expected {participant_count}"
            )

        competition = competition_by_id[int(event.competition_id)]
        schedule_entries = ordered_league_schedule_entries(
            rounds_by_competition.get(int(event.competition_id), ())
        )
        mapped = _mapped_league_replay(replay, tuple(refs))
        emissions = materialize_procedural_league_match_emissions(
            mapped,
            int(competition.scheduled_matchday_count),
        )

        if int(event.competition_id) == 27:
            cycle_count = max(
                (int(emission.cycle_index) for emission in emissions),
                default=-1,
            ) + 1
            generic_emissions = tuple(
                emission
                for emission in emissions
                if int(emission.cycle_index) < cycle_count - 1
            )
            nodes = list(
                materialize_procedural_league_schedule_nodes(
                    generic_emissions,
                    schedule_entries,
                    competition_id=27,
                    competition_context=int(event.competition_context),
                )
            )
            split_emissions = materialize_scot_premier_split_match_emissions(
                participant_count,
                int(competition.scheduled_matchday_count),
            )
            nodes.extend(
                materialize_scot_premier_split_schedule_nodes(
                    split_emissions,
                    schedule_entries,
                    competition_id=27,
                    competition_context=int(event.competition_context),
                )
            )
            league_nodes[key] = tuple(nodes)
            continue

        league_nodes[key] = materialize_procedural_league_schedule_nodes(
            emissions,
            schedule_entries,
            competition_id=int(event.competition_id),
            competition_context=int(event.competition_context),
        )

    fixed_nodes: dict[tuple[int, int], tuple[StartupScheduleNode, ...]] = {}
    for event in interleaved_rng.events:
        if event.kind != "fixed_league":
            continue
        key = (int(event.competition_id), int(event.competition_context))
        fixed_nodes[key] = materialize_fixed_league_schedule_nodes(
            round_list,
            real_fixture_list,
            competition_id=int(event.competition_id),
            competition_context=int(event.competition_context),
        )

    ordered_nodes: list[StartupScheduleNode] = []
    for event in interleaved_rng.events:
        if event.kind == "fixed_league":
            ordered_nodes.extend(
                fixed_nodes[
                    (int(event.competition_id), int(event.competition_context))
                ]
            )
        elif event.kind == "procedural_league_round_robin":
            ordered_nodes.extend(
                league_nodes[
                    (int(event.competition_id), int(event.competition_context))
                ]
            )
        elif event.kind == "cup_round_shuffle":
            if event.round_id is None:
                raise RuntimeError("Cup round RNG event has no round id")
            ordered_nodes.extend(
                cup_round_nodes[
                    (int(event.competition_id), int(event.round_id))
                ]
            )

    nodes = tuple(ordered_nodes)
    actual_events = tuple(interleaved_rng.events)
    ordered_bounds = tuple(
        int(bound)
        for event in actual_events
        for bound in event.bounds
    )
    bounds_blob = b"".join(
        int(bound).to_bytes(2, "little")
        for bound in ordered_bounds
    )
    return PrimaryRngDrivenScheduleMaterialization(
        rng_plan_total_draw_count=len(ordered_bounds),
        rng_plan_event_count=len(actual_events),
        rng_bounds_sha256=sha256(bounds_blob).hexdigest(),
        rng_events=actual_events,
        cup_runtime=cup_runtime,
        schedule_nodes=nodes,
        schedule_sha256=_node_digest(nodes),
        state_entering_primary_shuffle=interleaved_rng.state,
    )
