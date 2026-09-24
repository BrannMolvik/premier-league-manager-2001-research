from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence

from match_events import IncidentKind, IncidentRecord


class DisciplinePlayer(Protocol):
    side: int
    player_index: int
    current_position: int
    balance_position_code: int


@dataclass
class DisciplineState:
    booked_players: set[tuple[int, int]] = field(default_factory=set)
    sent_off_players: set[tuple[int, int]] = field(default_factory=set)
    red_counts: list[int] = field(default_factory=lambda: [0, 0])

    def __post_init__(self) -> None:
        if len(self.red_counts) != 2:
            raise ValueError("red_counts must contain exactly two side totals")
        if any(int(value) < 0 for value in self.red_counts):
            raise ValueError("red_counts cannot be negative")


def discipline_incident_threshold(aggression: int) -> int:
    """Exact outer 0x62E130 RNG(800) threshold."""
    aggression = int(aggression)
    if not 0 <= aggression <= 9:
        raise ValueError("aggression must be in 0..9")
    return (aggression * aggression) // 2 + 12


def _role_band(selection_roll: int) -> tuple[int, int]:
    """Strict lower/upper bounds passed to 0x62E5D0."""
    roll = int(selection_roll)
    if not 0 <= roll < 100:
        raise ValueError("selection_roll must be in 0..99")
    if roll <= 40:
        return 2, 8
    if roll <= 85:
        return 7, 13
    return 12, 30


def select_discipline_candidate(
    players: Sequence[DisciplinePlayer],
    lower_exclusive: int,
    upper_exclusive: int,
    state: DisciplineState,
    rng,
) -> DisciplinePlayer | None:
    """Exact selection order of 0x62E5D0 for an already-active roster.

    The original first filters players through 0x417F50 before applying the
    strict current-role bounds. Callers should therefore pass the active
    eligible roster in executable iteration order. Sent-off players are also
    excluded here because the original removal path takes them out of active
    selection state.
    """
    eligible = [
        player
        for player in players
        if (player.side, player.player_index) not in state.sent_off_players
        and int(player.current_position) > int(lower_exclusive)
        and int(player.current_position) < int(upper_exclusive)
    ]
    if not eligible:
        return None

    target = rng.randbelow(len(eligible)) + 1
    seen = 0
    for player in eligible:
        seen += 1
        if seen == target:
            return player

        # 0x62E5D0's unusual early-selection bias uses the separate
        # position-state +0x05 code, not the current assigned role.
        if int(player.balance_position_code) == 8:
            if rng.randbelow(10) < 5:
                return player

    return None


def apply_sequence_discipline(
    attacking_side: int,
    side0_players: Sequence[DisciplinePlayer],
    side1_players: Sequence[DisciplinePlayer],
    side0_aggression: int,
    side1_aggression: int,
    state: DisciplineState,
    rng,
    enabled: bool = True,
) -> IncidentRecord | None:
    """Exact mapped booking/sending-off path from 0x62E130.

    Discipline targets the side opposing the scheduler-selected attacker.
    The enabled argument mirrors the match-state +0x1145 guard; that byte
    defaults to 1 in the calculator constructor, but its higher-level semantic
    name is not yet proven.
    """
    if not enabled:
        return None

    attacking_side = int(attacking_side)
    if attacking_side not in (0, 1):
        raise ValueError("attacking_side must be 0 or 1")

    defending_side = 1 - attacking_side
    players = (side0_players, side1_players)[defending_side]
    aggression = int((side0_aggression, side1_aggression)[defending_side])
    if not 0 <= aggression <= 9:
        raise ValueError("aggression must be in 0..9")

    if rng.randbelow(800) >= discipline_incident_threshold(aggression):
        return None

    lower, upper = _role_band(rng.randbelow(100))
    candidate = select_discipline_candidate(
        players,
        lower,
        upper,
        state,
        rng,
    )
    if candidate is None:
        return None

    key = (defending_side, int(candidate.player_index))
    if key not in state.booked_players:
        if rng.randbelow(100) >= aggression:
            state.booked_players.add(key)
            return IncidentRecord(
                IncidentKind.BOOKED,
                defending_side,
                candidate.player_index,
            )

    # Already-booked players, and unbooked players whose RNG(100) fell below
    # Aggression, proceed directly into the dismissal escalation.
    if rng.randbelow(10) >= aggression:
        return None

    red_count = int(state.red_counts[defending_side])
    if rng.randbelow(5) >= 4 - red_count:
        return None

    state.sent_off_players.add(key)
    state.red_counts[defending_side] = red_count + 1
    return IncidentRecord(
        IncidentKind.SENT_OFF,
        defending_side,
        candidate.player_index,
    )
