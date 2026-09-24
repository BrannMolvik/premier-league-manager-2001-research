from __future__ import annotations

from typing import Protocol, Sequence

from match_calculator import form_multiplier
from match_events import SubstitutionRecord
from match_role_rating import role_rating


class MutableSubstitutionPlayer(Protocol):
    side: int
    player_index: int
    active: bool
    substitution_available: bool
    form_state: int
    current_position: int
    position_aux_code: int
    preferred_positions: tuple[int, int, int]
    skills: tuple[int, ...]


def _attacking_role_band(role: int) -> bool:
    """Combined 0x62E580 / 0x62E5B0 test used by 0x62E2F0."""
    return int(role) >= 8


def substitution_timing_value(
    players: Sequence[MutableSubstitutionPlayer],
    starting_player_indices: Sequence[int],
) -> int:
    """Exact state-derived value returned by team helper 0x409A70.

    The original starts at three and decrements for every original starting-XI
    player whose active bit is no longer set.
    """
    by_index = {int(player.player_index): player for player in players}
    value = 3
    for player_index in starting_player_indices:
        player = by_index.get(int(player_index))
        if player is None or not bool(player.active):
            value -= 1
    return value


def substitution_availability_value(
    players: Sequence[MutableSubstitutionPlayer],
) -> int:
    """State counter used inside replacement helper 0x409950.

    Match participants in neither the active nor substitute-available state
    decrement the helper's hard-coded initial value of three.
    """
    value = 3
    for player in players:
        if not bool(player.active) and not bool(player.substitution_available):
            value -= 1
    return value


def best_available_replacement(
    players: Sequence[MutableSubstitutionPlayer],
    outgoing_role: int,
) -> MutableSubstitutionPlayer | None:
    """Exact candidate ranking core of team helper 0x409950."""
    if substitution_availability_value(players) <= 0:
        return None

    best = None
    best_rating = 0
    for player in players:
        if not bool(player.substitution_available):
            continue
        rating = role_rating(
            player.skills,
            outgoing_role,
            player.preferred_positions,
        )
        if rating > best_rating:
            best_rating = rating
            best = player
    return best


def ai_substitution_threshold_minute(
    players: Sequence[MutableSubstitutionPlayer],
    starting_player_indices: Sequence[int],
) -> int:
    """Exact (9 - 0x409A70(team)) * 10 threshold used by 0x62E2F0."""
    return (9 - substitution_timing_value(players, starting_player_indices)) * 10


def _perform_substitution(
    outgoing: MutableSubstitutionPlayer,
    incoming: MutableSubstitutionPlayer,
) -> SubstitutionRecord:
    """Apply the position/status mutations performed by team helper 0x409AC0."""
    side = int(outgoing.side)
    if int(incoming.side) != side:
        raise ValueError("substitution players must belong to the same side")

    outgoing_role = int(outgoing.current_position)
    outgoing_aux = int(outgoing.position_aux_code)

    # Incoming inherits assigned role (+0x03 low five bits) and the +0x04
    # low nibble. The separate +0x05 balance-position code is untouched.
    incoming.current_position = outgoing_role
    incoming.position_aux_code = outgoing_aux

    outgoing.active = False
    outgoing.substitution_available = False
    incoming.substitution_available = False
    incoming.active = True

    # 0x4181B0 -> 0x4EA370 resets the outgoing position state.
    outgoing.current_position = int(outgoing.preferred_positions[0])
    outgoing.position_aux_code = 0

    return SubstitutionRecord(
        player_side=side,
        outgoing_player_index=int(outgoing.player_index),
        incoming_player_index=int(incoming.player_index),
    )


def apply_injury_substitution(
    side: int,
    injured_player_index: int,
    players: Sequence[MutableSubstitutionPlayer],
    user_controlled: bool,
    *,
    match_mode_code: int | None = None,
    enabled: bool = True,
) -> SubstitutionRecord | None:
    """Immediate replacement path inside injury routine 0x62EAE0.

    AI-controlled teams always enter the replacement path. A user-controlled
    team does so only when the still-generically-named MatchCalculator +0xD3C
    mode value is 1 or 3. Replacement ranking is 0x409950 and, unlike the
    automatic 0x62E2F0 path, there is no additional role>=8 filter.
    """
    if not enabled:
        return None

    side = int(side)
    if side not in (0, 1):
        raise ValueError("side must be 0 or 1")

    if bool(user_controlled) and match_mode_code not in (1, 3):
        return None

    injured = None
    for player in players:
        if int(player.player_index) == int(injured_player_index):
            injured = player
            break
    if injured is None:
        raise KeyError(injured_player_index)
    if int(injured.side) != side:
        raise ValueError("injured player side does not match substitution side")
    if not bool(injured.active):
        return None

    replacement = best_available_replacement(players, int(injured.current_position))
    if replacement is None:
        return None

    return _perform_substitution(injured, replacement)


def apply_ai_substitution(
    side: int,
    minute: int,
    scores: Sequence[int],
    players: Sequence[MutableSubstitutionPlayer],
    starting_player_indices: Sequence[int],
    user_controlled: bool,
    *,
    enabled: bool = True,
) -> SubstitutionRecord | None:
    """Clean-room implementation of the recovered AI routine 0x62E2F0.

    This function starts after the scheduler's separate RNG(7)==0 gate. It
    preserves the original state-derived timing, score guard, reverse starting
    XI scan, replacement ranking, role-band filtering, pair score, position
    inheritance, and type-10 semantic event.
    """
    if not enabled or bool(user_controlled):
        return None

    side = int(side)
    if side not in (0, 1):
        raise ValueError("side must be 0 or 1")
    if len(scores) != 2:
        raise ValueError("scores must contain exactly two side scores")

    minute = int(minute)
    if minute < ai_substitution_threshold_minute(players, starting_player_indices):
        return None
    if int(scores[side]) > int(scores[1 - side]):
        return None

    by_index = {int(player.player_index): player for player in players}
    best_outgoing = None
    best_incoming = None
    best_difference = 200

    # 0x62E2F0 scans the original eleven lineup entries from slot 10 to slot 0.
    for player_index in reversed(tuple(starting_player_indices)):
        outgoing = by_index.get(int(player_index))
        if outgoing is None or not bool(outgoing.active):
            continue
        outgoing_role = int(outgoing.current_position)
        if not _attacking_role_band(outgoing_role):
            continue

        incoming = best_available_replacement(players, outgoing_role)
        if incoming is None:
            continue

        # The original performs this second broad-role check only after
        # 0x409950 has already selected its best candidate.
        if not _attacking_role_band(incoming.current_position):
            continue

        outgoing_value = (
            role_rating(
                outgoing.skills,
                outgoing_role,
                outgoing.preferred_positions,
            )
            * form_multiplier(outgoing.form_state)
        )
        incoming_value = (
            role_rating(
                incoming.skills,
                outgoing_role,
                incoming.preferred_positions,
            )
            * form_multiplier(incoming.form_state)
        )

        # 0x668350 truncates toward zero.
        difference = int(outgoing_value - incoming_value)
        if difference < best_difference:
            best_difference = difference
            best_outgoing = outgoing
            best_incoming = incoming

    if best_outgoing is None or best_incoming is None:
        return None

    return _perform_substitution(best_outgoing, best_incoming)
