from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

from match_calculator import form_multiplier
from match_role_rating import best_preferred_role_rating, role_rating


class AiLineupPlayer(Protocol):
    player_index: int
    skills: Sequence[int]
    preferred_positions: Sequence[int]
    form_state: int


@dataclass(frozen=True)
class FormationSlot:
    role: int
    auxiliary_code: int


@dataclass(frozen=True)
class StarterAssignment:
    player_index: int
    role: int
    auxiliary_code: int


@dataclass(frozen=True)
class AiLineupCoreResult:
    starters: tuple[StarterAssignment, ...]
    substitutes: tuple[int, ...]
    unfilled_slot_indices: tuple[int, ...]


# Exact 21 x 11 table initialized by 0x50C3B0 at runtime 0x876CB8.
# Formation display names have not yet been proven and are intentionally absent.
AI_FORMATIONS: tuple[tuple[FormationSlot, ...], ...] = tuple(
    tuple(FormationSlot(role, auxiliary) for role, auxiliary in formation)
    for formation in (
        ((19,1),(19,0),(11,0),(10,0),(12,1),(12,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((19,1),(19,0),(14,0),(13,0),(9,1),(9,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((18,1),(18,0),(11,0),(10,0),(9,1),(9,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((19,1),(19,0),(15,0),(12,1),(12,0),(7,0),(6,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(18,0),(12,1),(12,0),(7,0),(6,0),(4,2),(4,1),(4,0),(1,0)),
        ((18,1),(18,0),(12,1),(12,0),(9,0),(7,0),(6,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(18,0),(11,0),(10,0),(9,1),(9,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(18,0),(14,0),(13,0),(12,1),(12,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,0),(18,1),(18,0),(11,0),(10,0),(9,1),(9,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(14,0),(13,0),(12,1),(12,0),(9,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(18,0),(14,0),(13,0),(9,1),(9,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(15,0),(11,0),(10,0),(9,1),(9,0),(4,2),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(18,0),(12,1),(12,0),(8,0),(7,0),(6,0),(4,1),(4,0),(1,0)),
        ((19,1),(19,0),(18,0),(15,1),(15,0),(12,0),(7,0),(6,0),(4,1),(4,0),(1,0)),
        ((19,0),(14,0),(13,0),(12,1),(12,0),(8,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((18,0),(15,1),(15,0),(11,0),(10,0),(8,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((19,1),(19,0),(18,0),(15,1),(15,0),(14,0),(13,0),(9,0),(4,1),(4,0),(1,0)),
        ((18,0),(15,1),(15,0),(11,0),(10,0),(5,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((19,1),(19,0),(14,0),(13,0),(12,1),(12,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
        ((19,1),(19,0),(15,0),(12,1),(12,0),(7,0),(6,0),(5,0),(4,1),(4,0),(1,0)),
        ((19,0),(18,1),(18,0),(15,0),(12,1),(12,0),(4,1),(4,0),(3,0),(2,0),(1,0)),
    )
)


# Exact broad category returned by 0x4EA310 for shipped runtime roles.
# 0 defender, 1 midfielder, 2 attacker, 3 goalkeeper, 255 unclassified.
ROLE_LINEUP_GROUP: tuple[int, ...] = (
    255, 3,
    0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    255, 255,
    2, 2,
)

BENCH_GROUP_ORDER = (1, 2, 0, 3)


def lineup_group_for_role(role: int) -> int:
    role = int(role)
    if not 0 <= role < len(ROLE_LINEUP_GROUP):
        return 255
    return ROLE_LINEUP_GROUP[role]


def _starter_score(player: AiLineupPlayer, target_role: int) -> int:
    value = int(
        role_rating(
            player.skills,
            target_role,
            player.preferred_positions,
        )
        * form_multiplier(player.form_state)
    )
    # 0x409C90 coerces a zero target-role score to one.
    return value if value != 0 else 1


def _bench_score(player: AiLineupPlayer) -> int:
    return int(
        best_preferred_role_rating(
            player.skills,
            player.preferred_positions,
        )
        * form_multiplier(player.form_state)
    )


def select_ai_lineup_core(
    players: Sequence[AiLineupPlayer],
    formation_id: int,
    substitute_quota: int,
    *,
    eligible: Callable[[AiLineupPlayer], bool] | None = None,
    starter_allowed: Callable[[AiLineupPlayer, Sequence[AiLineupPlayer]], bool] | None = None,
) -> AiLineupCoreResult:
    """Evidence-backed selection core of competitive AI routine 0x409C90.

    This deliberately leaves two still-partially-unresolved executable filters
    outside the selector. The eligible callback corresponds to the precomputed
    player-availability result (0x418050 / 0x418130 path). The starter_allowed
    callback can enforce the stateful bit-11/team-limit restriction.

    Passing no callbacks models only the now-proven formation/rating/ordering
    core. It must not be described as the complete 0x409C90 until those two
    filters are fully reconstructed.
    """
    formation_id = int(formation_id)
    substitute_quota = int(substitute_quota)
    if not 0 <= formation_id < len(AI_FORMATIONS):
        raise ValueError("formation_id must be in 0..20")
    if substitute_quota < 0:
        raise ValueError("substitute_quota must be non-negative")

    indices = [int(player.player_index) for player in players]
    if len(set(indices)) != len(indices):
        raise ValueError("player_index values must be unique")

    is_eligible = eligible or (lambda _player: True)
    may_start = starter_allowed or (lambda _player, _selected: True)
    formation = AI_FORMATIONS[formation_id]

    selected_indices: set[int] = set()
    selected_players: list[AiLineupPlayer] = []
    assignments: list[StarterAssignment | None] = [None] * 11

    def choose_for_slot(
        slot_index: int,
        *,
        require_preferred_match: bool,
    ) -> None:
        slot = formation[slot_index]
        best: AiLineupPlayer | None = None
        best_score = 0

        for player in players:
            player_index = int(player.player_index)
            if player_index in selected_indices:
                continue
            if not is_eligible(player):
                continue
            preferred = tuple(int(role) for role in player.preferred_positions[:3])
            if require_preferred_match and int(slot.role) not in preferred:
                continue
            if not may_start(player, tuple(selected_players)):
                continue

            score = _starter_score(player, slot.role)
            if score > best_score:
                best_score = score
                best = player

        if best is None:
            return

        selected_indices.add(int(best.player_index))
        selected_players.append(best)
        assignments[slot_index] = StarterAssignment(
            int(best.player_index),
            int(slot.role),
            int(slot.auxiliary_code),
        )

    # Stage 1: exact preferred-position match.
    for slot_index in range(11):
        choose_for_slot(slot_index, require_preferred_match=True)

    # Stage 2: fill only remaining slots, allowing out-of-position players.
    for slot_index, assignment in enumerate(assignments):
        if assignment is None:
            choose_for_slot(slot_index, require_preferred_match=False)

    substitutes: list[int] = []
    remaining = substitute_quota

    # Four ranked category passes, each able to add at most one player.
    for group in BENCH_GROUP_ORDER:
        if remaining <= 0:
            break

        best: AiLineupPlayer | None = None
        best_score = 0
        for player in players:
            player_index = int(player.player_index)
            if player_index in selected_indices:
                continue
            if not is_eligible(player):
                continue

            primary_role = int(player.preferred_positions[0])
            if lineup_group_for_role(primary_role) != group:
                continue

            score = _bench_score(player)
            if score > best_score:
                best_score = score
                best = player

        if best is not None:
            player_index = int(best.player_index)
            selected_indices.add(player_index)
            substitutes.append(player_index)
            remaining -= 1

    # Overflow substitutes are first-fit roster order, excluding goalkeepers.
    if remaining > 0:
        for player in players:
            if remaining <= 0:
                break

            player_index = int(player.player_index)
            if player_index in selected_indices:
                continue
            if not is_eligible(player):
                continue
            if lineup_group_for_role(int(player.preferred_positions[0])) == 3:
                continue

            selected_indices.add(player_index)
            substitutes.append(player_index)
            remaining -= 1

    return AiLineupCoreResult(
        starters=tuple(
            assignment
            for assignment in assignments
            if assignment is not None
        ),
        substitutes=tuple(substitutes),
        unfilled_slot_indices=tuple(
            index
            for index, assignment in enumerate(assignments)
            if assignment is None
        ),
    )
