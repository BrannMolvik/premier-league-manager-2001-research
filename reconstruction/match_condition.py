from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol, Sequence

from match_events import IncidentKind, IncidentRecord, SubstitutionRecord


DEFAULT_CONDITION_INJURY_INDUCING_LEVEL = 75
DEFAULT_CONDITION_INJURY_RANDOMISER = 3


class MutableConditionPlayer(Protocol):
    side: int
    player_index: int
    condition: int
    current_position: int
    skills: tuple[int, ...]


@dataclass(frozen=True)
class ConditionInjurySettings:
    """Known inputs to 0x62E6F0 / 0x62EAE0.

    environment_byte is kept deliberately generic: only its top two bits are
    proven to contribute to injury incidence. The executable's shipped default
    ConditionInjuryInducingLevel is 75.
    """

    environment_byte: int
    injury_inducing_level: int = DEFAULT_CONDITION_INJURY_INDUCING_LEVEL

    def __post_init__(self) -> None:
        if not 0 <= int(self.environment_byte) <= 255:
            raise ValueError("environment_byte must be in 0..255")
        if not 0 <= int(self.injury_inducing_level) <= 255:
            raise ValueError("injury_inducing_level must be in 0..255")


@dataclass
class ConditionInjuryState:
    last_injury_minute: int = 0
    injured_players: set[tuple[int, int]] = field(default_factory=set)


def condition_decay_threshold(stamina: int, aggression: int) -> int:
    """Exact 0x62E6C0 threshold before full/half workload scaling."""
    stamina = int(stamina)
    aggression = int(aggression)
    if not 0 <= stamina <= 255:
        raise ValueError("stamina must be in 0..255")
    if not 0 <= aggression <= 9:
        raise ValueError("aggression must be in 0..9")
    return (256 - stamina) // 32 + 2 * aggression


def _workload_threshold(role: int, attacking: bool, base: int) -> int | None:
    role = int(role)
    if role == 0:
        return None

    if attacking:
        if role >= 16:
            return base
        if 8 <= role <= 15:
            return base // 2
        return None

    if role <= 7:
        return base
    if 8 <= role <= 15:
        return base // 2
    return None


def injury_incidence_score(
    environment_byte: int,
    injury_proneness: int,
    condition: int,
    inducing_level: int = DEFAULT_CONDITION_INJURY_INDUCING_LEVEL,
) -> int:
    """Exact integer score compared against RNG(1000) in 0x62EAE0."""
    environment_byte = int(environment_byte)
    injury_proneness = int(injury_proneness)
    condition = int(condition)
    inducing_level = int(inducing_level)

    if not 0 <= environment_byte <= 255:
        raise ValueError("environment_byte must be in 0..255")
    if not 0 <= injury_proneness <= 255:
        raise ValueError("injury_proneness must be in 0..255")
    if not 0 <= condition <= 255:
        raise ValueError("condition must be in 0..255")

    return (
        (environment_byte >> 6)
        + (injury_proneness >> 3)
        + max(0, inducing_level - condition)
    )


def _injury_after_condition_change(
    player: MutableConditionPlayer,
    minute: int,
    settings: ConditionInjurySettings,
    state: ConditionInjuryState,
    rng,
    enabled: bool = True,
) -> IncidentRecord | None:
    # 0x62EAE0 excludes the goalkeeper role, then checks the shared
    # MatchCalculator +0x1145 guard before incidence processing.
    if int(player.current_position) == 1:
        return None
    if not enabled:
        return None

    key = (int(player.side), int(player.player_index))
    if key in state.injured_players:
        return None

    score = injury_incidence_score(
        settings.environment_byte,
        player.skills[4],
        player.condition,
        settings.injury_inducing_level,
    )

    # The executable consumes RNG(1000) before the nonzero and cooldown checks.
    if rng.randbelow(1000) >= score:
        return None
    if score == 0:
        return None

    minute = int(minute)
    if state.last_injury_minute >= minute - 10:
        return None

    state.last_injury_minute = minute
    state.injured_players.add(key)
    return IncidentRecord(
        IncidentKind.INJURED,
        player.side,
        player.player_index,
    )


def apply_sequence_condition_and_injuries(
    attacking_side: int,
    side0_players: Sequence[MutableConditionPlayer],
    side1_players: Sequence[MutableConditionPlayer],
    side0_aggression: int,
    side1_aggression: int,
    minute: int,
    settings: ConditionInjurySettings,
    state: ConditionInjuryState,
    rng,
    injury_enabled: bool = True,
    injury_substitution_handler: Callable[[IncidentRecord], SubstitutionRecord | None] | None = None,
) -> tuple[IncidentRecord | SubstitutionRecord, ...]:
    """Exact mapped 0x62E6F0 workload/Condition loop plus 0x62EAE0 incidence.

    The caller supplies match participants in executable iteration order.
    Each entry is checked for active state at the moment it is reached, matching
    0x417F50 in the original loop. This matters because an immediate injury
    replacement can activate a bench player before a later roster slot is
    visited. When injury_substitution_handler is provided, the returned type-10
    record is appended immediately after the type-5 injury record.
    """
    attacking_side = int(attacking_side)
    if attacking_side not in (0, 1):
        raise ValueError("attacking_side must be 0 or 1")

    players_by_side = (side0_players, side1_players)
    aggression_by_side = (int(side0_aggression), int(side1_aggression))
    incidents: list[IncidentRecord | SubstitutionRecord] = []

    # 0x62E6F0 iterates the attacking roster first, then the defending roster.
    for side in (attacking_side, 1 - attacking_side):
        aggression = aggression_by_side[side]
        if not 0 <= aggression <= 9:
            raise ValueError("aggression must be in 0..9")

        for player in players_by_side[side]:
            if not bool(getattr(player, "active", True)):
                continue

            base = condition_decay_threshold(player.skills[2], aggression)
            threshold = _workload_threshold(
                player.current_position,
                attacking=(side == attacking_side),
                base=base,
            )
            if threshold is None:
                continue

            if rng.randbelow(100) >= threshold:
                continue
            if int(player.condition) <= 1:
                continue

            player.condition = int(player.condition) - 1
            incident = _injury_after_condition_change(
                player,
                minute,
                settings,
                state,
                rng,
                enabled=injury_enabled,
            )
            if incident is not None:
                incidents.append(incident)
                if injury_substitution_handler is not None:
                    substitution = injury_substitution_handler(incident)
                    if substitution is not None:
                        incidents.append(substitution)

    return tuple(incidents)
