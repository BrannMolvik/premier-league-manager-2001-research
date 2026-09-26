"""Startup schedule-node descriptors recovered from FOOTBAL.EXE.

This module is data-free. It joins the already-recovered Cup and procedural
League pairing layers to the symbolic match objects that are inserted through
0x615950 before the global per-date schedule shuffle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from competition_startup import (
    CupClubRefDescriptor,
    MaterializedCupRound,
)
from procedural_league import (
    ProceduralLeagueMatchEmission,
    ScotPremierSplitMatchEmission,
)


@dataclass(frozen=True)
class StartupScheduleNode:
    """One pre-0x615950 match object in executable insertion order."""

    node_kind: str
    competition_id: int
    competition_context: int
    round_id: int | None
    pair_index: int
    schedule_index: int | None
    scheduled_week: int | None
    scheduled_weekday: int | None
    participant_0_ref: CupClubRefDescriptor
    participant_1_ref: CupClubRefDescriptor
    node_token: tuple


def direct_club_ref(club_id: int) -> CupClubRefDescriptor:
    club_id = int(club_id)
    return CupClubRefDescriptor(
        type_code=0,
        direct_club_id=club_id,
        reference_token=("direct_club", club_id),
    )


def _coerce_club_ref(value) -> CupClubRefDescriptor:
    if isinstance(value, CupClubRefDescriptor):
        return value
    return direct_club_ref(int(value))


def _runtime_object_identity(ref: CupClubRefDescriptor):
    """Semantic stand-in for the runtime pointer compared by 0x4F2830."""
    if int(ref.type_code) == 1 and ref.reference_token is not None:
        return ("match", tuple(ref.reference_token))
    if ref.competition_id is not None:
        return (
            "competition",
            int(ref.competition_id),
            int(ref.competition_context),
        )
    if ref.reference_token is not None:
        return ("token", tuple(ref.reference_token))
    return None


def club_refs_conflict(
    left: CupClubRefDescriptor,
    right: CupClubRefDescriptor,
) -> bool:
    """Reproduce ClubRef identity behavior beneath 0x510A40 / 0x4F2830.

    Direct refs conflict only when both resolve to the same club. A direct ref
    never conflicts with an unresolved symbolic ref. Two unresolved refs
    conflict only when their type, runtime source object, and selector match.
    """
    left_direct = left.direct_club_id
    right_direct = right.direct_club_id

    if left_direct is not None:
        return (
            right_direct is not None
            and int(left_direct) == int(right_direct)
        )
    if right_direct is not None:
        return False

    return (
        int(left.type_code) == int(right.type_code)
        and int(left.selector) == int(right.selector)
        and _runtime_object_identity(left) == _runtime_object_identity(right)
    )


def schedule_nodes_conflict(
    left: StartupScheduleNode,
    right: StartupScheduleNode,
) -> bool:
    return any(
        club_refs_conflict(left_ref, right_ref)
        for left_ref in (left.participant_0_ref, left.participant_1_ref)
        for right_ref in (right.participant_0_ref, right.participant_1_ref)
    )


def materialize_cup_round_schedule_nodes(
    runtime_round: MaterializedCupRound,
    round_definition,
    *,
    competition_id: int,
    competition_context: int = 0,
) -> tuple[StartupScheduleNode, ...]:
    """Emit NormalRound/TwoLegRound nodes in exact scheduler insertion order.

    NormalRound 0x4F64D0 emits one CupMatch per split-half pairing.
    TwoLegRound 0x4F6820 emits FirstLegMatch then SecondLegMatch for each
    pairing. The second-leg constructor reverses the two ClubRefs. MiniLeague
    emits no parent match node here; its child League runtimes schedule games.
    """
    round_type = int(runtime_round.round_type)
    if int(round_definition.id) != int(runtime_round.round_id):
        raise ValueError("runtime Cup round does not match round definition")
    if int(round_definition.type_code) != round_type:
        raise ValueError("runtime Cup round type does not match definition")

    competition_id = int(competition_id)
    competition_context = int(competition_context)

    if round_type == 3:
        return ()
    if round_type not in (1, 2):
        raise ValueError(f"unsupported Cup round type {round_type}")

    primary_week = int(round_definition.scheduled_week)
    primary_weekday = int(round_definition.scheduled_weekday)
    second_week = int(round_definition.replay_week)
    second_weekday = int(round_definition.replay_weekday)

    nodes: list[StartupScheduleNode] = []
    for pairing in runtime_round.pairings:
        pair_index = int(pairing.pair_index)
        left_ref = pairing.left_ref
        right_ref = pairing.right_ref

        if round_type == 1:
            nodes.append(
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=competition_id,
                    competition_context=competition_context,
                    round_id=int(runtime_round.round_id),
                    pair_index=pair_index,
                    schedule_index=None,
                    scheduled_week=primary_week,
                    scheduled_weekday=primary_weekday,
                    participant_0_ref=left_ref,
                    participant_1_ref=right_ref,
                    node_token=tuple(pairing.result_token),
                )
            )
            continue

        first_leg_token = (
            "cup_first_leg",
            competition_id,
            int(runtime_round.round_id),
            pair_index,
        )
        nodes.append(
            StartupScheduleNode(
                node_kind="first_leg_match",
                competition_id=competition_id,
                competition_context=competition_context,
                round_id=int(runtime_round.round_id),
                pair_index=pair_index,
                schedule_index=None,
                scheduled_week=primary_week,
                scheduled_weekday=primary_weekday,
                participant_0_ref=left_ref,
                participant_1_ref=right_ref,
                node_token=first_leg_token,
            )
        )
        nodes.append(
            StartupScheduleNode(
                node_kind="second_leg_match",
                competition_id=competition_id,
                competition_context=competition_context,
                round_id=int(runtime_round.round_id),
                pair_index=pair_index,
                schedule_index=None,
                scheduled_week=second_week,
                scheduled_weekday=second_weekday,
                participant_0_ref=right_ref,
                participant_1_ref=left_ref,
                node_token=tuple(pairing.result_token),
            )
        )

    return tuple(nodes)


def ordered_league_schedule_entries(
    round_definitions: Iterable[object],
) -> tuple[tuple[int, int], ...]:
    """Reproduce League+0x60 date-array construction and ordering.

    League::AddRound at 0x4F4500 appends DBRRound scheduled week and
    scheduled_weekday-1 into the 8-byte entries at League+0x60/+0x64.
    The dedicated 0x4F4580 qsort then orders those entries by week first and
    zero-based weekday second using comparator 0x4F45A0.

    Return source-style one-based weekdays so StartupScheduleNode uses the same
    public week/weekday convention as Cup round definitions. Equal runtime date
    entries are byte-identical, so their qsort permutation cannot change this
    returned date sequence.
    """
    entries = [
        (
            int(round_definition.scheduled_week),
            int(round_definition.scheduled_weekday) - 1,
        )
        for round_definition in round_definitions
    ]
    entries.sort(key=lambda value: (value[0], value[1]))
    return tuple((week, weekday + 1) for week, weekday in entries)


def materialize_procedural_league_schedule_nodes(
    emissions: Iterable[ProceduralLeagueMatchEmission],
    schedule_entries: Sequence[tuple[int, int]],
    *,
    competition_id: int,
    competition_context: int = 0,
) -> tuple[StartupScheduleNode, ...]:
    """Convert generic 0x6170F0 emissions into symbolic LeagueMatch nodes.

    schedule_entries is the League+0x60 date array after its dedicated date
    ordering step. Entries use source week and one-based weekday values.
    """
    competition_id = int(competition_id)
    competition_context = int(competition_context)
    nodes: list[StartupScheduleNode] = []

    for emission_index, emission in enumerate(emissions):
        schedule_index = int(emission.schedule_index)
        if not 0 <= schedule_index < len(schedule_entries):
            raise ValueError("procedural League schedule index exceeds date array")
        week, weekday = schedule_entries[schedule_index]
        nodes.append(
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=competition_id,
                competition_context=competition_context,
                round_id=None,
                pair_index=int(emission.pair_index),
                schedule_index=schedule_index,
                scheduled_week=int(week),
                scheduled_weekday=int(weekday),
                participant_0_ref=_coerce_club_ref(emission.home_team),
                participant_1_ref=_coerce_club_ref(emission.away_team),
                node_token=(
                    "league_match",
                    competition_id,
                    competition_context,
                    emission_index,
                ),
            )
        )
    return tuple(nodes)


def materialize_scot_premier_split_schedule_nodes(
    emissions: Iterable[ScotPremierSplitMatchEmission],
    schedule_entries: Sequence[tuple[int, int]],
    *,
    competition_id: int = 27,
    competition_context: int = 0,
) -> tuple[StartupScheduleNode, ...]:
    """Convert 0x4FAC60 type-4 Scottish split refs into LeagueMatch nodes."""
    competition_id = int(competition_id)
    competition_context = int(competition_context)
    nodes: list[StartupScheduleNode] = []

    for emission_index, emission in enumerate(emissions):
        schedule_index = int(emission.schedule_index)
        if not 0 <= schedule_index < len(schedule_entries):
            raise ValueError("Scottish split schedule index exceeds date array")
        week, weekday = schedule_entries[schedule_index]

        ref0 = CupClubRefDescriptor(
            type_code=4,
            selector=int(emission.participant_0_selector),
            competition_id=competition_id,
            competition_context=competition_context,
            reference_token=(
                "scot_split",
                competition_id,
                competition_context,
                int(emission.participant_0_selector),
            ),
        )
        ref1 = CupClubRefDescriptor(
            type_code=4,
            selector=int(emission.participant_1_selector),
            competition_id=competition_id,
            competition_context=competition_context,
            reference_token=(
                "scot_split",
                competition_id,
                competition_context,
                int(emission.participant_1_selector),
            ),
        )
        nodes.append(
            StartupScheduleNode(
                node_kind="scot_split_league_match",
                competition_id=competition_id,
                competition_context=competition_context,
                round_id=None,
                pair_index=int(emission.pair_index),
                schedule_index=schedule_index,
                scheduled_week=int(week),
                scheduled_weekday=int(weekday),
                participant_0_ref=ref0,
                participant_1_ref=ref1,
                node_token=(
                    "scot_split_match",
                    competition_id,
                    competition_context,
                    emission_index,
                ),
            )
        )

    return tuple(nodes)
