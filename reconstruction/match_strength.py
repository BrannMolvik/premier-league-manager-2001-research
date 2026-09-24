from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from match_calculator import effective_match_skill, formation_coverage_multiplier


PLAYER_SKILLS = 17

ATTACK_ROLE_FACTORS = (
    105, 108, 110, 120, 112, 115, 97, 95, 102, 92,
    90, 117, 100, 100, 100, 100, 100, 100, 100,
)
DEFENCE_ROLE_FACTORS = tuple(
    (200 - value) if role <= 12 else 100
    for role, value in enumerate(ATTACK_ROLE_FACTORS)
)

ATTACK_BIAS_MULTIPLIERS = (0.80, 0.90, 1.00, 1.10, 1.20)
DEFENCE_BIAS_MULTIPLIERS = (1.20, 1.10, 1.00, 0.90, 0.80)


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


@dataclass(frozen=True)
class TeamStrengthPlayer:
    """All player inputs consumed by 0x62F140 / 0x62F3E0."""

    side: int
    player_index: int
    condition: int
    form_state: int
    current_position: int
    preferred_positions: tuple[int, int, int]
    skills: tuple[int, ...]
    minimum_strength_override: bool = False

    def __post_init__(self) -> None:
        if self.side not in (0, 1):
            raise ValueError("side must be 0 or 1")
        if self.player_index < 0:
            raise ValueError("player_index must be non-negative")
        if not 0 <= int(self.condition) <= 255:
            raise ValueError("condition must be in 0..255")
        if not 0 <= int(self.form_state) <= 4:
            raise ValueError("form_state must be in 0..4")
        if not 0 <= int(self.current_position) <= 19:
            raise ValueError("current_position must be in 0..19")
        if len(self.preferred_positions) != 3:
            raise ValueError("preferred_positions must contain exactly three entries")
        if len(self.skills) != PLAYER_SKILLS:
            raise ValueError("skills must contain exactly 17 raw skill bytes")
        if any(not 0 <= int(value) <= 255 for value in self.skills):
            raise ValueError("skills must be in 0..255")

    @property
    def confidence(self) -> int:
        return int(self.skills[14])

    @property
    def leadership(self) -> int:
        return int(self.skills[15])


@dataclass(frozen=True)
class TeamStrengthContext:
    """Tactical/team state used by one side's strength builder."""

    tactic_style: int
    match_bias: int
    user_controlled: bool
    aggression: int = 5
    captain_player_index: int | None = None

    def __post_init__(self) -> None:
        if not 0 <= int(self.tactic_style) <= 3:
            raise ValueError("tactic_style must be in 0..3")
        if not 0 <= int(self.match_bias) <= 4:
            raise ValueError("match_bias must be in 0..4")
        if not 0 <= int(self.aggression) <= 9:
            raise ValueError("aggression must be in 0..9")


@dataclass(frozen=True)
class SegmentAttack:
    side: int
    minute: int


def _coefficient(
    matrix: Sequence[Sequence[Sequence[float]]],
    tactic: int,
    role: int,
    skill: int,
) -> float:
    try:
        return float(matrix[tactic][role][skill])
    except (IndexError, TypeError) as exc:
        raise ValueError("coefficient matrix must be shaped 4 x 20 x 17") from exc


def _captain(
    players: Sequence[TeamStrengthPlayer],
    player_index: int | None,
) -> TeamStrengthPlayer | None:
    if player_index is None:
        return None
    return next(
        (player for player in players if player.player_index == player_index),
        None,
    )


def _base_strength(
    players: Sequence[TeamStrengthPlayer],
    matrix: Sequence[Sequence[Sequence[float]]],
    tactic_style: int,
    role_factors: Sequence[int],
) -> float:
    total = 0.0
    for player in players:
        role = int(player.current_position)
        role_factor = role_factors[role] / 100.0
        for skill_index, raw_skill in enumerate(player.skills):
            effective = effective_match_skill(
                raw_skill,
                player.condition,
                role,
                player.preferred_positions,
                player.form_state,
                player.minimum_strength_override,
            )
            total += (
                (effective / 255.0)
                * _coefficient(matrix, tactic_style, role, skill_index)
                * role_factor
            )
    return total


def attack_team_strength(
    players: Sequence[TeamStrengthPlayer],
    attack_matrix: Sequence[Sequence[Sequence[float]]],
    context: TeamStrengthContext,
) -> float:
    """Clean-room implementation of the verified 0x62F140 strength pipeline."""
    total = _base_strength(
        players,
        attack_matrix,
        context.tactic_style,
        ATTACK_ROLE_FACTORS,
    )
    total *= ATTACK_BIAS_MULTIPLIERS[context.match_bias]

    if context.user_controlled:
        captain = _captain(players, context.captain_player_index)
        if captain is not None:
            total *= 0.95 + (captain.confidence + captain.leadership) / 5120.0
        total *= 1.0 + (context.aggression - 5) * 0.02
    else:
        total *= 1.05

    return total


def defence_team_strength(
    players: Sequence[TeamStrengthPlayer],
    defence_matrix: Sequence[Sequence[Sequence[float]]],
    context: TeamStrengthContext,
) -> float:
    """Clean-room implementation of the verified 0x62F3E0 strength pipeline."""
    total = _base_strength(
        players,
        defence_matrix,
        context.tactic_style,
        DEFENCE_ROLE_FACTORS,
    )
    total *= DEFENCE_BIAS_MULTIPLIERS[context.match_bias]

    if context.user_controlled:
        captain = _captain(players, context.captain_player_index)
        if captain is not None:
            total *= 0.90 + (captain.confidence + captain.leadership) / 2560.0
        total *= 1.0 + (context.aggression - 5) * 0.02
    else:
        total *= 1.10

    total *= formation_coverage_multiplier(players)
    return total


def attack_weights(
    side0_attack: float,
    side0_defence: float,
    side1_attack: float,
    side1_defence: float,
) -> tuple[int, int]:
    """Exact ratio/bias conversion at the head of 0x62B1A0."""
    if side0_defence <= 0 or side1_defence <= 0:
        raise ValueError("defence strengths must be positive")

    weight0 = int((side0_attack / side1_defence) * 1.10 * 100.0)
    weight1 = int((side1_attack / side0_defence) * 0.90 * 100.0)
    return weight0, weight1


def schedule_segment_attacks(
    segment_start: int,
    weights: tuple[int, int],
    rng: BoundedRng,
) -> tuple[SegmentAttack, ...]:
    """Strength-derived attack-side/minute scheduler from 0x62B1A0."""
    weight0, weight1 = (int(weights[0]), int(weights[1]))
    if weight0 < 0 or weight1 < 0:
        raise ValueError("attack weights must be non-negative")

    total_weight = weight0 + weight1
    sequence_count = total_weight // 30
    if sequence_count == 0:
        return ()

    attacks: list[SegmentAttack] = []
    for index in range(sequence_count):
        side = 0 if rng.randbelow(total_weight) < weight0 else 1
        minute = int(segment_start) + (5 * index) // sequence_count + 1
        attacks.append(SegmentAttack(side, minute))

    return tuple(attacks)
