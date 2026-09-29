"""Live English domestic-Cup schedule state for Gate 12.

Startup competition materialization already owns Cup allocation, pairing and
symbolic ClubRef construction. This module only carries the already-materialized
FA Cup / League Cup schedule nodes into dated live state. It deliberately does
not recreate draw RNG or invent match-engine completion rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Iterable

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_startup import CupClubRefDescriptor
from cup_progression import (
    CupMatchCompletion,
    CupMatchRuntimeState,
    CupResultRegistry,
)


ENGLISH_DOMESTIC_CUP_IDS = frozenset((1, 5))


def domestic_cup_source_date(season_year: int, week: int, weekday: int) -> date:
    """Convert primary-container Cup week/day through 0x6169F0/0x615950.

    The primary schedule container anchor is the first Monday on or after
    July 1. Runtime round construction copies the packed week unchanged and
    stores packed weekday - 1, then 0x615950 inserts at
    anchor + 7 * week + (weekday - 1).

    This is intentionally separate from Premier League season_weekday_date(),
    whose recovered league fixture convention uses the Monday containing
    July 1.
    """
    weekday = int(weekday)
    if not 1 <= weekday <= 7:
        raise ValueError("FM2001 Cup scheduled weekday must be 1..7")
    july_first = date(int(season_year), 7, 1)
    days_to_monday = (-july_first.weekday()) % 7
    anchor = july_first + timedelta(days=days_to_monday)
    return anchor + timedelta(weeks=int(week), days=weekday - 1)


def _tuple_tree(value):
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    return value


def _snapshot_ref(ref: CupClubRefDescriptor) -> dict:
    return {
        "type_code": int(ref.type_code),
        "selector": int(ref.selector),
        "direct_club_id": (
            None if ref.direct_club_id is None else int(ref.direct_club_id)
        ),
        "competition_id": (
            None if ref.competition_id is None else int(ref.competition_id)
        ),
        "competition_context": int(ref.competition_context),
        "reference_token": (
            None if ref.reference_token is None else list(ref.reference_token)
        ),
    }


def _restore_ref(value: dict) -> CupClubRefDescriptor:
    return CupClubRefDescriptor(
        type_code=int(value["type_code"]),
        selector=int(value["selector"]),
        direct_club_id=(
            None
            if value["direct_club_id"] is None
            else int(value["direct_club_id"])
        ),
        competition_id=(
            None
            if value["competition_id"] is None
            else int(value["competition_id"])
        ),
        competition_context=int(value["competition_context"]),
        reference_token=(
            None
            if value["reference_token"] is None
            else _tuple_tree(value["reference_token"])
        ),
    )


@dataclass(frozen=True)
class DomesticCupScheduledNode:
    """One already-materialized domestic Cup node on its live season date."""

    node_kind: str
    competition_id: int
    competition_context: int
    round_id: int
    pair_index: int
    scheduled_date: date
    participant_0_ref: CupClubRefDescriptor
    participant_1_ref: CupClubRefDescriptor
    node_token: tuple

    @classmethod
    def from_startup_node(
        cls,
        node: StartupScheduleNode,
        *,
        season_year: int,
    ) -> "DomesticCupScheduledNode":
        if int(node.competition_id) not in ENGLISH_DOMESTIC_CUP_IDS:
            raise ValueError("node is not an English domestic Cup match")
        if node.node_kind not in ("cup_match", "first_leg_match", "second_leg_match"):
            raise ValueError(f"unsupported domestic Cup node kind {node.node_kind}")
        if node.round_id is None:
            raise ValueError("Cup schedule node has no round id")
        if node.scheduled_week is None or node.scheduled_weekday is None:
            raise ValueError("Cup schedule node has no source date")

        return cls(
            node_kind=str(node.node_kind),
            competition_id=int(node.competition_id),
            competition_context=int(node.competition_context),
            round_id=int(node.round_id),
            pair_index=int(node.pair_index),
            scheduled_date=domestic_cup_source_date(
                int(season_year),
                int(node.scheduled_week),
                int(node.scheduled_weekday),
            ),
            participant_0_ref=node.participant_0_ref,
            participant_1_ref=node.participant_1_ref,
            node_token=tuple(node.node_token),
        )

    @property
    def first_leg_token(self) -> tuple | None:
        if self.node_kind != "second_leg_match":
            return None
        return (
            "cup_first_leg",
            int(self.competition_id),
            int(self.round_id),
            int(self.pair_index),
        )

    def resolve_pair(
        self,
        registry: CupResultRegistry,
    ) -> tuple[int, int] | None:
        return registry.resolve_pair(
            self.participant_0_ref,
            self.participant_1_ref,
        )

    def snapshot(self) -> dict:
        return {
            "node_kind": self.node_kind,
            "competition_id": int(self.competition_id),
            "competition_context": int(self.competition_context),
            "round_id": int(self.round_id),
            "pair_index": int(self.pair_index),
            "scheduled_date": self.scheduled_date.isoformat(),
            "participant_0_ref": _snapshot_ref(self.participant_0_ref),
            "participant_1_ref": _snapshot_ref(self.participant_1_ref),
            "node_token": list(self.node_token),
        }

    @classmethod
    def restore(cls, value: dict) -> "DomesticCupScheduledNode":
        return cls(
            node_kind=str(value["node_kind"]),
            competition_id=int(value["competition_id"]),
            competition_context=int(value["competition_context"]),
            round_id=int(value["round_id"]),
            pair_index=int(value["pair_index"]),
            scheduled_date=date.fromisoformat(value["scheduled_date"]),
            participant_0_ref=_restore_ref(value["participant_0_ref"]),
            participant_1_ref=_restore_ref(value["participant_1_ref"]),
            node_token=_tuple_tree(value["node_token"]),
        )


@dataclass
class DomesticCupScheduleState:
    """Persistent schedule identity and completion state for FA/League Cups."""

    nodes: tuple[DomesticCupScheduledNode, ...] = ()
    completed_node_tokens: set[tuple] = field(default_factory=set)
    match_states: dict[tuple, CupMatchRuntimeState] = field(default_factory=dict)

    @classmethod
    def from_startup_nodes(
        cls,
        nodes: Iterable[StartupScheduleNode],
        *,
        season_year: int,
    ) -> "DomesticCupScheduleState":
        materialized = tuple(
            DomesticCupScheduledNode.from_startup_node(
                node,
                season_year=int(season_year),
            )
            for node in nodes
            if int(node.competition_id) in ENGLISH_DOMESTIC_CUP_IDS
            and node.node_kind in ("cup_match", "first_leg_match", "second_leg_match")
        )
        tokens = [node.node_token for node in materialized]
        if len(tokens) != len(set(tokens)):
            raise ValueError("domestic Cup schedule contains duplicate node tokens")
        return cls(nodes=materialized)

    def node(self, node_token: tuple) -> DomesticCupScheduledNode:
        token = tuple(node_token)
        for node in self.nodes:
            if node.node_token == token:
                return node
        raise KeyError(token)

    def mark_completed(self, node_token: tuple) -> None:
        token = tuple(node_token)
        self.node(token)
        if token in self.completed_node_tokens:
            raise ValueError("domestic Cup schedule node is already complete")
        self.completed_node_tokens.add(token)

    def _paired_second_leg_node(
        self,
        first: DomesticCupScheduledNode,
    ) -> DomesticCupScheduledNode:
        for node in self.nodes:
            if (
                node.node_kind == "second_leg_match"
                and node.competition_id == first.competition_id
                and node.round_id == first.round_id
                and node.pair_index == first.pair_index
            ):
                return node
        raise KeyError("FirstLeg schedule node has no paired SecondLeg node")

    def materialize_normal_match(
        self,
        node_token: tuple,
        registry: CupResultRegistry,
        *,
        extra_time_capable: bool,
        decisive_tiebreak: bool,
        auxiliary_flag: bool = False,
    ) -> CupMatchRuntimeState:
        token = tuple(node_token)
        node = self.node(token)
        if node.node_kind != "cup_match":
            raise ValueError("normal Cup match requires a cup_match schedule node")
        if token in self.match_states:
            raise ValueError("domestic Cup match state already materialized")
        pair = node.resolve_pair(registry)
        if pair is None:
            raise ValueError("domestic Cup node participants are unresolved")
        match = CupMatchRuntimeState.normal(
            node.node_token,
            pair[0],
            pair[1],
            extra_time_capable=bool(extra_time_capable),
            decisive_tiebreak=bool(decisive_tiebreak),
            auxiliary_flag=bool(auxiliary_flag),
        )
        self.match_states[token] = match
        return match

    def materialize_two_leg_pair(
        self,
        first_leg_token: tuple,
        registry: CupResultRegistry,
        *,
        second_leg_extra_time_capable: bool,
        second_leg_auxiliary_flag: bool = False,
    ) -> tuple[CupMatchRuntimeState, CupMatchRuntimeState]:
        first_token = tuple(first_leg_token)
        first_node = self.node(first_token)
        if first_node.node_kind != "first_leg_match":
            raise ValueError("two-leg materialization must start from FirstLeg node")
        second_node = self._paired_second_leg_node(first_node)
        if first_token in self.match_states or second_node.node_token in self.match_states:
            raise ValueError("domestic Cup two-leg state already materialized")
        pair = first_node.resolve_pair(registry)
        if pair is None:
            raise ValueError("domestic Cup node participants are unresolved")

        first, second = CupMatchRuntimeState.two_leg_pair(
            second_node.node_token,
            pair[0],
            pair[1],
            second_leg_extra_time_capable=bool(second_leg_extra_time_capable),
            second_leg_auxiliary_flag=bool(second_leg_auxiliary_flag),
        )
        self.match_states[first_token] = first
        self.match_states[second_node.node_token] = second
        return first, second

    def match_state(self, node_token: tuple) -> CupMatchRuntimeState | None:
        return self.match_states.get(tuple(node_token))

    def insert_replay_from_completion(
        self,
        original_node_token: tuple,
        completion: CupMatchCompletion,
        *,
        current_date: date,
    ) -> DomesticCupScheduledNode:
        """Insert the canonical shipped domestic-Cup replay after a draw.

        Source 0x51392A schedules the replay at current relative schedule day
        + 14 unless runtime round +0x2C exceeds 6. Canonical shipped FA Cup
        replay-producing rounds all carry replay_weekday=3, so that floor
        branch is never taken. League Cup normal rounds are decisive and do
        not reach this path.
        """
        original_token = tuple(original_node_token)
        original_node = self.node(original_token)
        if original_node.node_kind != "cup_match":
            raise ValueError("Cup replay can only follow a normal Cup schedule node")

        original_match = self.match_states.get(original_token)
        if original_match is None:
            raise ValueError("Cup replay requires materialized original match state")
        replay = completion.replay
        if replay is None:
            raise ValueError("Cup completion did not produce a replay")
        if replay.prior_match is not original_match:
            raise ValueError("Cup replay is not linked to the scheduled original match")
        if not original_match.complete:
            raise ValueError("Cup replay requires a completed original match")

        replay_token = (
            "cup_replay",
            int(original_node.competition_id),
            int(original_node.round_id),
            int(original_node.pair_index),
        )
        if any(node.node_token == replay_token for node in self.nodes):
            raise ValueError("Cup replay schedule node already exists")
        if replay_token in self.match_states:
            raise ValueError("Cup replay match state already exists")
        if original_token in self.completed_node_tokens:
            raise ValueError("original Cup schedule node is already complete")

        replay_node = DomesticCupScheduledNode(
            node_kind="replay_match",
            competition_id=int(original_node.competition_id),
            competition_context=int(original_node.competition_context),
            round_id=int(original_node.round_id),
            pair_index=int(original_node.pair_index),
            scheduled_date=current_date + timedelta(days=14),
            participant_0_ref=direct_club_ref(replay.participant_0_club_id),
            participant_1_ref=direct_club_ref(replay.participant_1_club_id),
            node_token=replay_token,
        )
        self.nodes += (replay_node,)
        self.match_states[replay_token] = replay
        self.completed_node_tokens.add(original_token)
        return replay_node

    def is_playable(
        self,
        node: DomesticCupScheduledNode,
        registry: CupResultRegistry,
    ) -> bool:
        if node.node_token in self.completed_node_tokens:
            return False
        if node.node_kind == "second_leg_match":
            first_leg_token = node.first_leg_token
            if first_leg_token not in self.completed_node_tokens:
                return False
        return node.resolve_pair(registry) is not None

    def due_nodes(
        self,
        on_date: date,
        registry: CupResultRegistry,
    ) -> tuple[DomesticCupScheduledNode, ...]:
        return tuple(
            node
            for node in self.nodes
            if node.scheduled_date == on_date
            and self.is_playable(node, registry)
        )

    def _match_token_for_identity(
        self,
        match: CupMatchRuntimeState | None,
    ) -> tuple | None:
        if match is None:
            return None
        for token, candidate in self.match_states.items():
            if candidate is match:
                return token
        raise ValueError("linked Cup match is not registered in schedule state")

    def _snapshot_match_states(self) -> list[dict]:
        records = []
        for token, match in sorted(self.match_states.items(), key=lambda item: repr(item[0])):
            records.append(
                {
                    "node_token": list(token),
                    "result_token": list(match.result_token),
                    "match_kind": int(match.match_kind),
                    "participant_0_club_id": int(match.participant_0_club_id),
                    "participant_1_club_id": int(match.participant_1_club_id),
                    "extra_time_capable": bool(match.extra_time_capable),
                    "decisive_tiebreak": bool(match.decisive_tiebreak),
                    "auxiliary_flag": bool(match.auxiliary_flag),
                    "base_score_0": int(match.base_score_0),
                    "base_score_1": int(match.base_score_1),
                    "decisive_score_0": int(match.decisive_score_0),
                    "decisive_score_1": int(match.decisive_score_1),
                    "complete": bool(match.complete),
                    "prior_node_token": (
                        None
                        if match.prior_match is None
                        else list(self._match_token_for_identity(match.prior_match))
                    ),
                }
            )
        return records

    def snapshot(self) -> dict:
        return {
            "nodes": [node.snapshot() for node in self.nodes],
            "completed_node_tokens": [
                list(token)
                for token in sorted(self.completed_node_tokens, key=repr)
            ],
            "match_states": self._snapshot_match_states(),
        }

    @classmethod
    def restore(cls, value: dict | None) -> "DomesticCupScheduleState":
        if value is None:
            return cls()
        state = cls(
            nodes=tuple(
                DomesticCupScheduledNode.restore(node)
                for node in value.get("nodes", ())
            ),
            completed_node_tokens={
                _tuple_tree(token)
                for token in value.get("completed_node_tokens", ())
            },
        )
        known = {node.node_token for node in state.nodes}
        unknown = state.completed_node_tokens - known
        if unknown:
            raise ValueError("saved domestic Cup completion references unknown nodes")

        pending_links: list[tuple[tuple, tuple | None]] = []
        for record in value.get("match_states", ()):
            token = _tuple_tree(record["node_token"])
            if token not in known:
                raise ValueError("saved Cup match state references unknown schedule node")
            if token in state.match_states:
                raise ValueError("saved Cup match state contains duplicate node token")
            match = CupMatchRuntimeState(
                result_token=_tuple_tree(record["result_token"]),
                match_kind=int(record["match_kind"]),
                participant_0_club_id=int(record["participant_0_club_id"]),
                participant_1_club_id=int(record["participant_1_club_id"]),
                extra_time_capable=bool(record["extra_time_capable"]),
                decisive_tiebreak=bool(record["decisive_tiebreak"]),
                auxiliary_flag=bool(record["auxiliary_flag"]),
                base_score_0=int(record["base_score_0"]),
                base_score_1=int(record["base_score_1"]),
                decisive_score_0=int(record["decisive_score_0"]),
                decisive_score_1=int(record["decisive_score_1"]),
                complete=bool(record["complete"]),
            )
            state.match_states[token] = match
            prior_token = record.get("prior_node_token")
            pending_links.append(
                (
                    token,
                    None if prior_token is None else _tuple_tree(prior_token),
                )
            )

        for token, prior_token in pending_links:
            if prior_token is None:
                continue
            prior = state.match_states.get(prior_token)
            if prior is None:
                raise ValueError("saved Cup match link references unknown match state")
            current = state.match_states[token]
            current.prior_match = prior
            prior.following_match = current
        return state
