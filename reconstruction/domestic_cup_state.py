"""Live English domestic-Cup schedule state for Gate 12.

Startup competition materialization already owns Cup allocation, pairing and
symbolic ClubRef construction. This module only carries the already-materialized
FA Cup / League Cup schedule nodes into dated live state. It deliberately does
not recreate draw RNG or invent match-engine completion rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from competition_schedule import StartupScheduleNode
from competition_startup import CupClubRefDescriptor
from competition_state import season_weekday_date
from cup_progression import CupResultRegistry


ENGLISH_DOMESTIC_CUP_IDS = frozenset((1, 5))


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
            scheduled_date=season_weekday_date(
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

    def snapshot(self) -> dict:
        return {
            "nodes": [node.snapshot() for node in self.nodes],
            "completed_node_tokens": [
                list(token)
                for token in sorted(self.completed_node_tokens, key=repr)
            ],
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
        return state
