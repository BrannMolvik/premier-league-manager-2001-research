from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence

from match_calculator import (
    MatchSkillPlayer,
    PositionRole,
    build_positional_pools,
    effective_match_skill,
    select_initial_carrier,
)


class TeamOrderCategory(IntEnum):
    CAPTAIN = 0
    PENALTY = 1
    CORNER = 2
    FREE_KICK = 3


@dataclass(frozen=True)
class TeamOrderPriorities:
    """Exact four human Team Orders priority categories.

    Original storage is owned by the user-team companion/profile returned by
    0x403850. Category counts live at profile +0x206+category and category
    player-ID list pointers at profile +0x660+4*category. IDs are uint16 and
    are consumed in stored order.
    """

    captain: tuple[int, ...] = ()
    penalty: tuple[int, ...] = ()
    corner: tuple[int, ...] = ()
    free_kick: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        for name in ("captain", "penalty", "corner", "free_kick"):
            values = tuple(int(value) for value in getattr(self, name))
            if any(not 0 <= value <= 0xFFFF for value in values):
                raise ValueError(f"{name} player IDs must be uint16 values")
            object.__setattr__(self, name, values)

    def for_category(self, category: TeamOrderCategory | int) -> tuple[int, ...]:
        category = TeamOrderCategory(int(category))
        if category is TeamOrderCategory.CAPTAIN:
            return self.captain
        if category is TeamOrderCategory.PENALTY:
            return self.penalty
        if category is TeamOrderCategory.CORNER:
            return self.corner
        return self.free_kick


def first_active_priority(
    players: Sequence[MatchSkillPlayer],
    priority: Sequence[int],
) -> MatchSkillPlayer | None:
    """Return the first active player in one human Team Orders priority list."""
    by_index = {int(player.player_index): player for player in players}
    for player_index in priority:
        player = by_index.get(int(player_index))
        if player is not None:
            return player
    return None


def select_human_ordered_taker(
    players: Sequence[MatchSkillPlayer],
    priority: Sequence[int],
    rng,
) -> MatchSkillPlayer | None:
    """Human category 1/2/3 path: priority list, then 0x62B780 fallback."""
    selected = first_active_priority(players, priority)
    if selected is not None:
        return selected
    return select_initial_carrier(build_positional_pools(players), rng)


def _effective_set_piece(player: MatchSkillPlayer) -> int:
    return effective_match_skill(
        player.set_piece,
        player.condition,
        player.current_position,
        player.preferred_positions,
        player.form_state,
        player.minimum_strength_override,
    )


def select_ai_best_set_piece_taker(
    players: Sequence[MatchSkillPlayer],
    rng,
) -> MatchSkillPlayer | None:
    """AI category 2/3 path recovered from 0x631FB0 / 0x632280.

    Active goalkeepers are excluded. The first player with the strictly
    greatest effective Set Piece value wins, preserving roster iteration order
    on ties. If no eligible player exists, the executable falls back to
    0x62B780.
    """
    best: MatchSkillPlayer | None = None
    best_value = -1

    for player in players:
        if int(player.current_position) == int(PositionRole.GOALKEEPER):
            continue
        value = _effective_set_piece(player)
        if value > best_value:
            best = player
            best_value = value

    if best is not None:
        return best
    return select_initial_carrier(build_positional_pools(players), rng)


def select_set_piece_taker(
    players: Sequence[MatchSkillPlayer],
    category: TeamOrderCategory,
    user_controlled: bool,
    priority: Sequence[int],
    rng,
) -> MatchSkillPlayer | None:
    """Recovered top-level taker selection for categories 1/2/3."""
    if category is TeamOrderCategory.CAPTAIN:
        raise ValueError("captain selection does not use set-piece fallback")

    if user_controlled:
        return select_human_ordered_taker(players, priority, rng)

    if category is TeamOrderCategory.PENALTY:
        return select_initial_carrier(build_positional_pools(players), rng)

    return select_ai_best_set_piece_taker(players, rng)
