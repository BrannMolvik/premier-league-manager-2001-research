"""Default paired PSquadScreen row-owner hit mapping, no scrollbar/filter."""
from dataclasses import dataclass

from original_squad_membership import NativeSquadMembership, native_squad_slot
from original_squad_resources import SQUAD_PANEL_RECT, SQUAD_VISIBLE_ROW_Y_ORIGINS


@dataclass(frozen=True)
class NativeSquadPointerHit:
    ordered_index: int
    visible_index: int
    empty_owner: bool
    shirt_number: bool


def original_squad_row_at_point(membership, x, y, *, press=False):
    """4B6DF0 / 4B90A0 / 4B93BE for default left-first/right-reserve owners.

    Actual player-owner rectangle is 226x17, not the surrounding stats grid.
    4B56B0 -> 4B7FD0/6510F0 gives y154, row minimum17, width226;
    4466E0/446710 retains that minimum for native 16-high rows/empty owners.
    The panel's source parent y79 is retained, not a guessed modern offset.
    """
    if not isinstance(membership, NativeSquadMembership):
        raise ValueError('Native Squad pointer requires retained membership')
    if type(x) is not int or type(y) is not int or type(press) is not bool:
        raise ValueError('Native pointer coordinates must be integers')
    panel_x, panel_y = SQUAD_PANEL_RECT[:2]
    local_y = y - panel_y
    visible = next((i for i, top in enumerate(SQUAD_VISIBLE_ROW_Y_ORIGINS)
                    if top <= local_y < top + 17), None)
    if visible is None:
        return None
    reserve = None
    for candidate, origin in ((False, 37), (True, 418)):
        if panel_x + origin <= x < panel_x + origin + 226:
            reserve = candidate
            local_x = x - panel_x - origin
            break
    if reserve is None:
        return None
    slots = tuple(native_squad_slot(membership, visible_index=i, reserve=reserve,
                  source_count=len(membership.members)) for i in range(20))
    slot = slots[visible]
    if slot >= len(membership.members):
        return None  # Null DBRPlayer lookup does not own a row.
    empty = slot == -1
    prior_empty = sum(value == -1 for value in slots[:visible])
    if reserve:
        fa = sum(p.selection == 4 for p in membership.members)
        fs = sum(p.selection == 3 for p in membership.members)
        index = membership.first_list_boundary + visible - (
            11 + membership.substitute_quota - fa - fs + prior_empty)
    else:
        index = visible - prior_empty if visible < membership.first_list_boundary else visible
    if press and (empty or 30 < local_x < 70):
        return None  # 4B91E6..9224 role column rejects; boundaries are exact.
    return NativeSquadPointerHit(index, visible, empty, local_x < 30)
