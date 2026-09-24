from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol, Sequence

from match_events import ChanceRecord, ChanceSource


class PositionRole(IntEnum):
    NONE = 0
    GOALKEEPER = 1
    RIGHT_BACK = 2
    LEFT_BACK = 3
    CENTRE_BACK = 4
    SWEEPER = 5
    RIGHT_WING_BACK = 6
    LEFT_WING_BACK = 7
    ANCHOR = 8
    DEFENSIVE_MIDFIELD = 9
    RIGHT_MIDFIELD = 10
    LEFT_MIDFIELD = 11
    CENTRE_MIDFIELD = 12
    RIGHT_WINGER = 13
    LEFT_WINGER = 14
    ATTACKING_MIDFIELD = 15
    RIGHT_FORWARD = 16
    LEFT_FORWARD = 17
    CENTRE_FORWARD = 18
    STRIKER = 19


FORM_MULTIPLIERS = (0.90, 0.95, 1.00, 1.05, 1.10)


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


@dataclass(frozen=True)
class MatchSkillPlayer:
    side: int
    player_index: int
    condition: int
    form_state: int
    current_position: int
    preferred_positions: tuple[int, int, int]
    shooting: int = 0
    goalkeeping: int = 0
    minimum_strength_override: bool = False

    def __post_init__(self) -> None:
        if self.side not in (0, 1):
            raise ValueError("side must be 0 or 1")
        if self.player_index < 0:
            raise ValueError("player_index must be non-negative")
        if len(self.preferred_positions) != 3:
            raise ValueError("FM2001 position state requires exactly three preferred positions")
        for name in ("condition", "shooting", "goalkeeping"):
            value = int(getattr(self, name))
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be in 0..255")
        if not 0 <= int(self.form_state) <= 4:
            raise ValueError("form_state must be in 0..4")


def _contains(preferred_positions: Sequence[int], *positions: int) -> bool:
    preferred = set(int(v) for v in preferred_positions[:3])
    return any(int(position) in preferred for position in positions)


def position_compatibility_multiplier(current_position: int, preferred_positions: Sequence[int]) -> float:
    """Exact numeric behavior of footballmanager.exe routine 0x4EA440."""
    current = int(current_position)
    preferred = tuple(int(v) for v in preferred_positions[:3])
    if len(preferred) != 3:
        raise ValueError("preferred_positions must contain at least three entries")

    if current in preferred:
        return 1.0
    if current == PositionRole.GOALKEEPER:
        return 0.10
    if current == PositionRole.RIGHT_BACK:
        if _contains(preferred, PositionRole.RIGHT_WING_BACK, PositionRole.CENTRE_BACK):
            return 0.90
        if _contains(preferred, PositionRole.LEFT_WING_BACK, PositionRole.LEFT_BACK):
            return 0.75
        return 0.50
    if current == PositionRole.LEFT_BACK:
        if _contains(preferred, PositionRole.LEFT_WING_BACK, PositionRole.CENTRE_BACK):
            return 0.90
        if _contains(preferred, PositionRole.RIGHT_BACK, PositionRole.RIGHT_WING_BACK):
            return 0.75
        return 0.50
    if current == PositionRole.CENTRE_BACK:
        return 0.90 if _contains(preferred, PositionRole.RIGHT_BACK, PositionRole.LEFT_BACK, PositionRole.SWEEPER) else 0.50
    if current == PositionRole.SWEEPER:
        if _contains(preferred, PositionRole.CENTRE_BACK):
            return 0.90
        if _contains(preferred, PositionRole.RIGHT_BACK, PositionRole.LEFT_BACK):
            return 0.75
        return 0.50
    if current == PositionRole.RIGHT_WING_BACK:
        if _contains(preferred, PositionRole.RIGHT_BACK):
            return 0.90
        if _contains(preferred, PositionRole.LEFT_BACK, PositionRole.LEFT_WING_BACK):
            return 0.75
        return 0.50
    if current == PositionRole.LEFT_WING_BACK:
        if _contains(preferred, PositionRole.LEFT_BACK):
            return 0.90
        if _contains(preferred, PositionRole.RIGHT_BACK, PositionRole.RIGHT_WING_BACK):
            return 0.75
        return 0.50
    if current in (PositionRole.ANCHOR, PositionRole.DEFENSIVE_MIDFIELD):
        if _contains(preferred, PositionRole.ANCHOR, PositionRole.DEFENSIVE_MIDFIELD,
                     PositionRole.LEFT_MIDFIELD, PositionRole.RIGHT_MIDFIELD, PositionRole.CENTRE_MIDFIELD):
            return 0.90
        if _contains(preferred, PositionRole.CENTRE_BACK, PositionRole.SWEEPER):
            return 0.80
        return 0.50
    if current == PositionRole.RIGHT_MIDFIELD:
        if _contains(preferred, PositionRole.RIGHT_WINGER):
            return 0.85
        if _contains(preferred, PositionRole.LEFT_MIDFIELD):
            return 0.70
        if _contains(preferred, PositionRole.CENTRE_MIDFIELD, PositionRole.DEFENSIVE_MIDFIELD,
                     PositionRole.ATTACKING_MIDFIELD):
            return 0.80
        return 0.50
    if current == PositionRole.LEFT_MIDFIELD:
        if _contains(preferred, PositionRole.LEFT_WINGER):
            return 0.85
        if _contains(preferred, PositionRole.RIGHT_MIDFIELD):
            return 0.70
        if _contains(preferred, PositionRole.CENTRE_MIDFIELD, PositionRole.DEFENSIVE_MIDFIELD,
                     PositionRole.ATTACKING_MIDFIELD):
            return 0.80
        return 0.50
    if current == PositionRole.CENTRE_MIDFIELD:
        if _contains(preferred, PositionRole.DEFENSIVE_MIDFIELD, PositionRole.LEFT_MIDFIELD,
                     PositionRole.RIGHT_MIDFIELD, PositionRole.ATTACKING_MIDFIELD):
            return 0.90
        if _contains(preferred, PositionRole.CENTRE_BACK):
            return 0.80
        return 0.50
    if current == PositionRole.RIGHT_WINGER:
        if _contains(preferred, PositionRole.RIGHT_MIDFIELD):
            return 0.80
        if _contains(preferred, PositionRole.LEFT_WINGER):
            return 0.70
        return 0.50
    if current == PositionRole.LEFT_WINGER:
        if _contains(preferred, PositionRole.LEFT_MIDFIELD):
            return 0.80
        if _contains(preferred, PositionRole.RIGHT_WINGER):
            return 0.70
        return 0.50
    if current == PositionRole.ATTACKING_MIDFIELD:
        if _contains(preferred, PositionRole.DEFENSIVE_MIDFIELD, PositionRole.RIGHT_MIDFIELD,
                     PositionRole.LEFT_MIDFIELD, PositionRole.CENTRE_MIDFIELD):
            return 0.90
        if _contains(preferred, PositionRole.CENTRE_FORWARD, PositionRole.STRIKER):
            return 0.75
        return 0.50
    if current in (PositionRole.RIGHT_FORWARD, PositionRole.LEFT_FORWARD):
        return 0.50
    if current in (PositionRole.CENTRE_FORWARD, PositionRole.STRIKER):
        if _contains(preferred, PositionRole.CENTRE_FORWARD, PositionRole.STRIKER):
            return 0.90
        if _contains(preferred, PositionRole.ATTACKING_MIDFIELD, PositionRole.CENTRE_MIDFIELD,
                     PositionRole.LEFT_MIDFIELD):
            return 0.75
        return 0.50
    return 0.50


def form_multiplier(form_state: int) -> float:
    try:
        return FORM_MULTIPLIERS[int(form_state)]
    except (IndexError, ValueError) as exc:
        raise ValueError("form_state must be in 0..4") from exc


def effective_match_skill(
    raw_skill: int,
    condition: int,
    current_position: int,
    preferred_positions: Sequence[int],
    form_state: int,
    minimum_strength_override: bool = False,
) -> int:
    """Exact positive-integer strength pipeline used by type-4 penalties."""
    if minimum_strength_override:
        return 1
    raw_skill = int(raw_skill)
    condition = int(condition)
    if not 0 <= raw_skill <= 255 or not 0 <= condition <= 255:
        raise ValueError("raw_skill and condition must be in 0..255")

    value = (condition // 3 + 66) * raw_skill
    value = int(value * position_compatibility_multiplier(current_position, preferred_positions))
    value = int(value * form_multiplier(form_state))
    return value if value != 0 else 1


def _presentation_outcome(base_outcome: int, rng: BoundedRng) -> int:
    return int(base_outcome) + (3 if rng.randbelow(100) < 10 else 0)


def resolve_penalty(
    taker: MatchSkillPlayer,
    goalkeeper: MatchSkillPlayer,
    current_attacking_score: int,
    rng: BoundedRng,
) -> ChanceRecord | None:
    """Reconstruct normal-match type-4 resolver 0x62D660 after taker selection."""
    score = int(current_attacking_score)
    if score < 0:
        raise ValueError("current_attacking_score must be non-negative")

    if rng.randbelow(3) == 0:
        shooting_strength = effective_match_skill(
            taker.shooting,
            taker.condition,
            taker.current_position,
            taker.preferred_positions,
            taker.form_state,
            taker.minimum_strength_override,
        )
        if rng.randbelow(256) >= shooting_strength // 100:
            return ChanceRecord(
                ChanceSource.PENALTY,
                _presentation_outcome(1, rng),
                taker.side,
                taker.player_index,
                context_flag=True,
            )

    goalkeeping_strength = effective_match_skill(
        goalkeeper.goalkeeping,
        goalkeeper.condition,
        goalkeeper.current_position,
        goalkeeper.preferred_positions,
        goalkeeper.form_state,
        goalkeeper.minimum_strength_override,
    )
    if rng.randbelow(800) < goalkeeping_strength // 100:
        return ChanceRecord(
            ChanceSource.PENALTY,
            _presentation_outcome(2, rng),
            taker.side,
            taker.player_index,
            context_flag=True,
        )

    if rng.randbelow(10) >= 10 - score:
        return None

    return ChanceRecord(
        ChanceSource.PENALTY,
        _presentation_outcome(0, rng),
        taker.side,
        taker.player_index,
        context_flag=True,
    )
