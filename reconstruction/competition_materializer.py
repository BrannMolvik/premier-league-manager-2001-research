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
    PrimaryCompetitionRuntimeRngEvent,
    replay_primary_mode0_complete_competition_rng,
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
    initial_league_club_ids,
)
from cup_runtime import (
    PrimaryCupRuntimeMaterialization,
    materialize_primary_cup_runtime,
)
from match_schedule import MsvcCrtRng
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
    cup_runtime: PrimaryCupRuntimeMaterialization
    schedule_nodes: tuple[StartupScheduleNode, ...]
    schedule_sha256: str
    state_entering_primary_shuffle: int

    @property
    def schedule_node_count(self) -> int:
        return len(self.schedule_nodes)


class _InterleavingCompetitionRng:
    """Inject procedural-League RNG events around Cup-runtime RNG requests."""

    def __init__(
        self,
        delegate,
        events: tuple[PrimaryCompetitionRuntimeRngEvent, ...],
    ):
        self.delegate = delegate
        self.events = events
        self.event_index = 0
        self.bound_index = 0
        self.league_round_robins: dict[
            tuple[int, int], ProceduralLeagueRoundRobin
        ] = {}

    @property
    def state(self) -> int:
        return int(getattr(self.delegate, "state")) & 0xFFFFFFFF

    def _advance_empty_events(self) -> None:
        while self.event_index < len(self.events):
            event = self.events[self.event_index]
            if event.bounds:
                return
            self.event_index += 1
            self.bound_index = 0

    def _consume_league_events(self) -> None:
        self._advance_empty_events()
        while self.event_index < len(self.events):
            event = self.events[self.event_index]
            if event.kind != "procedural_league_round_robin":
                return
            if self.bound_index:
                raise RuntimeError("procedural League event began mid-bound stream")
            if event.participant_count is None:
                raise RuntimeError("procedural League event has no participant count")

            replay = generate_procedural_league_round_robin(
                tuple(range(int(event.participant_count))),
                self.delegate,
            )
            if tuple(replay.bounds) != tuple(event.bounds):
                raise RuntimeError(
                    "procedural League interleave diverged from verified RNG plan"
                )
            if self.state != int(event.state_after):
                raise RuntimeError(
                    "procedural League interleave ended at the wrong CRT state"
                )
            key = (int(event.competition_id), int(event.competition_context))
            if key in self.league_round_robins:
                raise RuntimeError(f"duplicate procedural League runtime {key}")
            self.league_round_robins[key] = replay
            self.event_index += 1
            self.bound_index = 0
            self._advance_empty_events()

    def randbelow(self, bound: int) -> int:
        bound = int(bound)
        self._consume_league_events()
        self._advance_empty_events()
        if self.event_index >= len(self.events):
            raise RuntimeError(
                f"Cup materializer requested unexpected trailing RNG({bound})"
            )

        event = self.events[self.event_index]
        if event.kind == "procedural_league_round_robin":
            raise RuntimeError("procedural League event was not consumed")
        if self.bound_index >= len(event.bounds):
            raise RuntimeError("RNG event bound cursor exceeded event length")

        expected = int(event.bounds[self.bound_index])
        if expected != bound:
            raise RuntimeError(
                f"RNG interleave mismatch at {event.kind}: expected "
                f"RNG({expected}), received RNG({bound})"
            )

        value = int(self.delegate.randbelow(bound))
        self.bound_index += 1
        if self.bound_index == len(event.bounds):
            if self.state != int(event.state_after):
                raise RuntimeError(
                    f"{event.kind} ended at the wrong CRT state"
                )
            self.event_index += 1
            self.bound_index = 0
        return value

    def finish(self) -> None:
        self._consume_league_events()
        self._advance_empty_events()
        if self.event_index != len(self.events) or self.bound_index:
            event = self.events[self.event_index]
            raise RuntimeError(
                "Cup materializer did not consume the complete non-League RNG "
                f"plan; next event is {event.kind}"
            )


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

    Procedural League participants are exact when they are either:
    - current direct members of the League in Master.dat; or
    - MiniLeague groups already materialized by the parent Cup.

    If neither source yields the expected participant count, this routine
    raises instead of manufacturing symbolic participant identities.
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

    plan_rng = MsvcCrtRng(int(start_state))
    plan = replay_primary_mode0_complete_competition_rng(
        plan_rng,
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
        tuple(plan.events),
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

    if interleaved_rng.state != int(plan.state_entering_primary_shuffle):
        raise RuntimeError("integrated competition materializer ended at wrong CRT state")
    if cup_runtime.champions_league_club_id != plan.champions_league_club_id:
        raise RuntimeError("Champions League selector diverged from RNG plan")
    if cup_runtime.uefa_cup_club_id != plan.uefa_cup_club_id:
        raise RuntimeError("UEFA Cup selector diverged from RNG plan")

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
    for event in plan.events:
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
            if len(direct_ids) != participant_count:
                raise ValueError(
                    f"procedural League {key} requires {participant_count} "
                    f"participants, but exact startup sources provide "
                    f"{len(direct_ids)}"
                )
            refs = tuple(direct_club_ref(club_id) for club_id in direct_ids)

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
    for event in plan.events:
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
    for event in plan.events:
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
    return PrimaryRngDrivenScheduleMaterialization(
        rng_plan_total_draw_count=int(plan.total_draw_count),
        rng_plan_event_count=len(plan.events),
        cup_runtime=cup_runtime,
        schedule_nodes=nodes,
        schedule_sha256=_node_digest(nodes),
        state_entering_primary_shuffle=interleaved_rng.state,
    )
