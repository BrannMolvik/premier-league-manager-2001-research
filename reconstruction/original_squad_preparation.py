"""Primary-club Squad preparation: 4B7BD0 -> 40AB40 / 4067B0.

This is a state producer, not a visual 20/10 split or prototype autofill.
Callers retain every input explicitly. Secondary-club contexts are not covered.
No RNG is consumed by these functions. The subsequent ordering/slot producer
is original_squad_membership, not Python's database or surname ordering.
"""
from dataclasses import dataclass, replace
from typing import Callable

from match_calculator import form_multiplier
from match_lineup import AI_FORMATIONS
from match_role_rating import role_rating


# 5F0E00 initializes the 0x24-byte records at 87AF98; 5F2110 attaches
# those records to 87AE64. 5F0D20 returns 1 + max(matching record +8).
NATIVE_ROLE_CAPACITIES = (1, 1, 1, 1, 3, 1, 1, 1, 1, 3,
                          1, 1, 3, 1, 1, 3, 1, 1, 3, 3)
# Jump tables 406B98 / 406DA8 for roles 2..19. Role 8 has a distinct
# first-XI divisor; reserve occupancy adds the entire role-4 contribution.
_OTHER_OCCUPANCY_ROLES = {
    2: (6,), 3: (7,), 4: (8,), 6: (2,), 7: (3,), 8: (4,),
    9: (12, 15), 12: (9, 15), 15: (9, 12), 18: (19,), 19: (18,),
}


@dataclass(frozen=True)
class PreparedSquadPlayer:
    player_id: int
    selection: int
    current_role: int
    current_aux: int
    reserve_role: int
    reserve_aux: int
    preferred_roles: tuple[int, int, int]
    skills: tuple[int, ...]
    form_state: int
    unavailable: bool

    def __post_init__(self):
        for name, maximum in (('player_id', 65535), ('selection', 4),
                              ('current_role', 31), ('current_aux', 15),
                              ('reserve_role', 255), ('reserve_aux', 255)):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= maximum:
                raise ValueError(f'Invalid retained Squad {name}')
        if (len(self.preferred_roles) != 3 or len(self.skills) != 17
                or type(self.unavailable) is not bool):
            raise ValueError('Squad source role/skill/availability inputs are incomplete')


@dataclass(frozen=True)
class PreparedSquadResult:
    players: tuple[PreparedSquadPlayer, ...]
    reserve_formation: int
    reserve_selection_attempted: bool
    reserve_selection_complete: bool


def _clear(player):
    # 4181B0 clears all selections and calls 4EA370. Clearing reserve XI
    # first calls 418220, retaining the previous reserve role in +152/+153.
    if player.selection == 2:
        player = _swap_reserve_role(player)
    return replace(player, selection=0, current_role=player.preferred_roles[0], current_aux=0)


def _swap_reserve_role(player):
    # 418220 retains whole previous read-back bytes in +152/+153, but the
    # role-object setters mask new values to low five/four bits.
    return replace(player, current_role=player.reserve_role & 31,
                   current_aux=player.reserve_aux & 15,
                   reserve_role=player.current_role, reserve_aux=player.current_aux)


def _set_selection(player, selection):
    if (player.selection == 2) != (selection == 2):
        player = _swap_reserve_role(player)
    player = replace(player, selection=selection)
    if selection in (1, 3):
        player = replace(player, current_role=player.preferred_roles[0], current_aux=0)
    return player


def native_role_occupancy(players, *, role, reserve, excluded_player_id):
    selection = 2 if reserve else 4
    def count(target):
        return sum(p.player_id != excluded_player_id and p.selection == selection
                   and p.current_role == target for p in players)
    value = count(role)
    for other in _OTHER_OCCUPANCY_ROLES.get(role, ()):
        value += count(other) // (3 if role == 8 and not reserve else 1)
    return value


def _adjust_role(players, index, reserve):
    # 406690/406720 retain an existing nonzero role if occupancy < cap.
    # Otherwise scan native roles 1..19, not an invented formation order.
    player = players[index]
    def occupancy(role):
        return native_role_occupancy(players, role=role, reserve=reserve,
                                     excluded_player_id=player.player_id)
    role = player.current_role
    cap = NATIVE_ROLE_CAPACITIES[role] if role < len(NATIVE_ROLE_CAPACITIES) else 1
    if role and occupancy(role) < cap:
        return
    for role in range(1, 20):
        used = occupancy(role)
        if used < NATIVE_ROLE_CAPACITIES[role]:
            players[index] = replace(player, current_role=role, current_aux=used & 15)
            return


def native_reserve_target_score(player, role):
    value = int(role_rating(player.skills, role, player.preferred_roles)
                * form_multiplier(player.form_state))
    return value if value else 1


def _select_reserves(players, formation, score):
    masked = [p.unavailable or p.selection in (3, 4) for p in players]
    chosen = []
    selected = set()
    for slot in AI_FORMATIONS[formation]:
        best, best_score = None, 0
        for index, player in enumerate(players):
            if masked[index] or index in selected:
                continue
            value = score(player, slot.role)
            if type(value) is not int:
                raise ValueError('Native reserve target score must be an integer')
            if not value:
                value = 1
            if value > best_score:  # strict greater; first equal candidate wins
                best, best_score = index, value
        if best is None:
            return False  # 40AF37: no partial selection is committed
        selected.add(best)
        chosen.append(best)
    for index, player in enumerate(players):
        if player.selection not in (3, 4):
            players[index] = _clear(player)
    for index, slot in zip(chosen, AI_FORMATIONS[formation]):
        players[index] = replace(_set_selection(players[index], 2),
                                 current_role=slot.role, current_aux=slot.auxiliary_code)
    remaining = 3  # 40AEA9 overwrites caller quota with native literal three
    for index in range(len(players)):
        if remaining and not masked[index] and index not in selected:
            players[index] = _set_selection(players[index], 1)
            remaining -= 1
    return True


def _repair_overflow(players, quota, on_first_active):
    counts = {s: sum(p.selection == s for p in players) for s in (1, 2, 3, 4)}
    fa, fs, ra, rs = (counts[s] for s in (4, 3, 2, 1))
    if len(players) < quota + 25:
        ra, rs = 11, 3  # native count substitution, NOT fabricated flags
    excess = len(players) - rs - ra - fs - fa + quota - 15
    if excess <= 0:
        return
    for index in range(len(players) - 1, -1, -1):
        if players[index].selection:
            continue
        # Four SEQUENTIAL checks: later setters can replace earlier state of
        # this very same player. Do not change them into elif/one-slot filling.
        if fa < 11:
            on_first_active(players[index])  # 4182F0 side-effect qualification
            players[index] = _set_selection(players[index], 4)
            _adjust_role(players, index, False)
            fa += 1
            excess -= 1
        if ra < 11:
            players[index] = _set_selection(players[index], 2)
            _adjust_role(players, index, True)
            ra += 1
            excess -= 1
        if fs < quota:
            players[index] = _set_selection(players[index], 3)
            fs += 1
            excess -= 1
        if rs < 3:
            players[index] = _set_selection(players[index], 1)
            rs += 1
            excess -= 1
        if excess == 0:
            break  # native equality, not <=0


def prepare_primary_squad(players, *, substitute_quota, reserve_formation,
                          on_first_active: Callable[[PreparedSquadPlayer], None],
                          target_score=native_reserve_target_score):
    """Reproduce the primary-owned branch with no guessed missing state.

    Availability is the retained 418050(club, null) result, including the
    source Non-EU date predicate. The mandatory callback qualifies/applies
    4182F0's loan-list side effect before allowing its first-XI setter.
    Secondary-club records require their separate native predicates and are
    outside this explicit primary-owned API.
    """
    players = list(players)
    if (len(players) > 40 or any(not isinstance(p, PreparedSquadPlayer) for p in players)
            or len({p.player_id for p in players}) != len(players)):
        raise ValueError('Invalid primary native Squad roster')
    if type(substitute_quota) is not int or not 0 <= substitute_quota <= 9:
        raise ValueError('Native Squad quota is required')
    if type(reserve_formation) is not int or reserve_formation not in (*range(21), 22):
        raise ValueError('Retained native reserve formation is required')
    if not callable(on_first_active) or not callable(target_score):
        raise ValueError('Native setter/score contracts are required')
    large = len(players) >= substitute_quota + 25
    has_reserves = any(p.selection in (1, 2) for p in players)
    attempted = large and not has_reserves
    complete = False
    if attempted:
        if reserve_formation == 22:
            reserve_formation = 0
        complete = _select_reserves(players, reserve_formation, target_score)
    elif not large and has_reserves:
        players = [_clear(p) if p.selection in (1, 2) else p for p in players]
    _repair_overflow(players, substitute_quota, on_first_active)
    return PreparedSquadResult(tuple(players), reserve_formation, attempted, complete)
