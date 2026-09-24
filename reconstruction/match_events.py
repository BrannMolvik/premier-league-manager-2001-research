from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable


class ChanceSource(IntEnum):
    """Active MatchCalculator chance source codes in the analyzed FM2001 build."""

    OPEN_PLAY = 1
    FREE_KICK = 2
    CORNER = 3
    PENALTY = 4


class ChanceOutcome(IntEnum):
    """Base chance result encoded by record +0x24 modulo three."""

    GOAL = 0
    MISS = 1
    SAVE = 2


class FinishMode(IntEnum):
    """Verified chance-record +0x2C finish selector."""

    HEADED = 0
    SHOOTING = 1


class IncidentKind(IntEnum):
    """Type-5 per-player incident/status subtypes."""

    BOOKED = 0
    SENT_OFF = 1
    INJURED = 2


class BoundaryType(IntEnum):
    HALF_TIME = 6
    FULL_TIME = 7
    EXTRA_TIME = 8
    PENALTIES = 9


SUBSTITUTION_RECORD_TYPE = 10


@dataclass(frozen=True)
class ChanceRecord:
    """Clean-room representation of the verified chance-record semantics.

    source corresponds to calculator record +0x28 for active types 1..4.
    raw_outcome corresponds to +0x24 and is one of 0..5. Values 3..5 are
    presentation variants of the same base results as 0..2.
    player_side/player_index correspond to the involved player's actual side
    and side-local index. side_inversion corresponds to +0x20 and changes a
    scored chance into an own-goal attribution for the opposing side.

    finish_mode corresponds to calculator record +0x2C:
    0 = headed finish (Heading branch), 1 = shooting/kicked finish
    (Shooting branch). This is independent of source, outcome and own-goal
    attribution.
    """

    source: ChanceSource
    raw_outcome: int
    player_side: int
    player_index: int
    side_inversion: bool = False
    finish_mode: FinishMode = FinishMode.HEADED

    def __post_init__(self) -> None:
        if not isinstance(self.source, ChanceSource):
            object.__setattr__(self, "source", ChanceSource(int(self.source)))
        if self.raw_outcome not in range(6):
            raise ValueError("raw_outcome must be one of 0..5")
        if self.player_side not in (0, 1):
            raise ValueError("player_side must be 0 or 1")
        if self.player_index < 0:
            raise ValueError("player_index must be non-negative")
        object.__setattr__(self, "side_inversion", bool(self.side_inversion))
        if not isinstance(self.finish_mode, FinishMode):
            object.__setattr__(self, "finish_mode", FinishMode(int(self.finish_mode)))

    @property
    def outcome(self) -> ChanceOutcome:
        return ChanceOutcome(self.raw_outcome % 3)

    @property
    def presentation_variant(self) -> bool:
        return self.raw_outcome >= 3

    @property
    def is_goal(self) -> bool:
        return self.outcome is ChanceOutcome.GOAL

    @property
    def credited_side(self) -> int | None:
        if not self.is_goal:
            return None
        return 1 - self.player_side if self.side_inversion else self.player_side

    @property
    def is_own_goal(self) -> bool:
        return self.is_goal and self.side_inversion


@dataclass(frozen=True)
class IncidentRecord:
    kind: IncidentKind
    player_side: int
    player_index: int

    def __post_init__(self) -> None:
        if not isinstance(self.kind, IncidentKind):
            object.__setattr__(self, "kind", IncidentKind(int(self.kind)))
        if self.player_side not in (0, 1):
            raise ValueError("player_side must be 0 or 1")
        if self.player_index < 0:
            raise ValueError("player_index must be non-negative")


@dataclass(frozen=True)
class BoundaryRecord:
    kind: BoundaryType

    def __post_init__(self) -> None:
        if not isinstance(self.kind, BoundaryType):
            object.__setattr__(self, "kind", BoundaryType(int(self.kind)))


@dataclass(frozen=True)
class PossessionRecord:
    """Verified EventPossession payload from one five-minute segment.

    territory is the separate +0x100C-derived territorial/pitch-position metric.
    side0_percent and neutral_percent are the two explicitly stored possession
    percentages; side1_percent is reconstructed as the remainder to 100.
    """

    territory: int
    side0_percent: int
    neutral_percent: int

    def __post_init__(self) -> None:
        for name in ("territory", "side0_percent", "neutral_percent"):
            value = int(getattr(self, name))
            if not 0 <= value <= 100:
                raise ValueError(f"{name} must be in 0..100")
            object.__setattr__(self, name, value)
        if self.side0_percent + self.neutral_percent > 100:
            raise ValueError("side0_percent + neutral_percent cannot exceed 100")

    @property
    def side1_percent(self) -> int:
        return 100 - self.side0_percent - self.neutral_percent


MatchEvent = ChanceRecord | IncidentRecord | BoundaryRecord | PossessionRecord


@dataclass
class MatchTimeline:
    """Semantic timeline built only from already-recovered calculator records."""

    events: list[MatchEvent] = field(default_factory=list)

    def extend(self, events: Iterable[MatchEvent]) -> None:
        self.events.extend(events)

    def append(self, event: MatchEvent) -> None:
        self.events.append(event)

    def score(self) -> tuple[int, int]:
        scores = [0, 0]
        for event in self.events:
            if isinstance(event, ChanceRecord):
                side = event.credited_side
                if side is not None:
                    scores[side] += 1
        return scores[0], scores[1]
