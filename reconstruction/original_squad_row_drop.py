"""Primary row-name drop state machine at 4B9350 (not shirt-number drag).

Input is retained native ordered roster and explicitly qualified hit context.
The output precedes 4B7500 ordering. No match lineup or visual state is guessed.
"""
from dataclasses import dataclass, replace

from original_squad_preparation import (
    PreparedSquadPlayer, NATIVE_ROLE_CAPACITIES, native_role_occupancy,
    _clear, _set_selection,
)


@dataclass(frozen=True)
class NativeSquadDropResult:
    players: tuple[PreparedSquadPlayer, ...]
    accepted: bool
    first_active_player_ids: tuple[int, ...] = ()


def drop_original_squad_row(players, *, source_index, target_index,
                            empty_row_index=None, substitute_quota):
    """4B9486 empty-owner / 4B9692 populated-owner transaction.

    target_index is the native translated index (may exceed N for a qualified
    empty owner). empty_row_index is the retained raw row number, or None for
    a real populated owner. Loan ownership must be qualified by the caller.
    """
    players = tuple(players)
    if (not players or len(players) > 40
            or any(not isinstance(p, PreparedSquadPlayer) for p in players)
            or len({p.player_id for p in players}) != len(players)):
        raise ValueError('Row drop requires a complete retained native roster')
    if type(substitute_quota) is not int or not 0 <= substitute_quota <= 9:
        raise ValueError('Row drop requires the explicit native quota')
    if type(source_index) is not int or not 0 <= source_index < len(players):
        raise ValueError('Invalid retained source row')
    if type(target_index) is not int or target_index < 0:
        raise ValueError('Invalid retained target row')
    if (empty_row_index is not None and
            (type(empty_row_index) is not int or not 0 <= empty_row_index < 20)):
        raise ValueError('Invalid native empty-owner row')
    if empty_row_index is None and target_index >= len(players):
        raise ValueError('Null lookup is not a populated player')
    result = list(players)
    source = result[source_index]
    active = []

    def set_kind(index, kind, role=None, aux=None):
        if kind == 4:
            active.append(result[index].player_id)
        value = (_clear(result[index]) if kind == 0 else
                 _set_selection(result[index], kind))
        if role is not None:
            value = replace(value, current_role=role & 31, current_aux=aux & 15)
        result[index] = value

    if empty_row_index is not None:
        # 4B94C5 uses the TRANSLATED index, not a modern pane identity.
        reserve = target_index >= 20
        role, aux = source.current_role, source.current_aux
        occupancy = native_role_occupancy(players, role=role, reserve=reserve,
                                          excluded_player_id=source.player_id)
        cap = NATIVE_ROLE_CAPACITIES[role] if role < len(NATIVE_ROLE_CAPACITIES) else 1
        if empty_row_index < 11 and occupancy == cap:
            return NativeSquadDropResult(players, False)
        if not reserve:
            kind = 4 if empty_row_index < 11 else (
                3 if empty_row_index < 11 + substitute_quota else 0)
        elif len(players) >= substitute_quota + 25:
            kind = 2 if empty_row_index < 11 else (1 if empty_row_index < 14 else 0)
        else:
            kind = 0
        set_kind(source_index, kind, role if kind in (2, 4) else None, aux)
    else:
        target = result[target_index]
        target_kind = target.selection
        role, aux = target.current_role, target.current_aux
        if target_kind in (2, 4):
            # Literal role-one count goes to esp+14 (the +1C write occurs
            # under two pushed arguments), not retained target aux at +1C.
            goalkeeper_count = sum(p.selection == target_kind and p.current_role == 1
                                   for p in result)
            # Both 406BE0 (First) and 406DF0 (Reserve) reach 4B97D2..F3;
            # the selected-XI count belongs to the target side in either case.
            if (goalkeeper_count == 0
                    and sum(p.selection == target_kind for p in result) == 11
                    and source.current_role == 1):
                role, aux = 1, 0  # 4B97DF..F3, not a goalkeeper approximation
        # Exact sequence also matters when source and target are identical.
        set_kind(target_index, 0)
        live_source = result[source_index]
        set_kind(target_index, live_source.selection,
                 live_source.current_role if live_source.selection in (2, 4) else None,
                 live_source.current_aux)
        set_kind(source_index, 0)
        set_kind(source_index, target_kind,
                 role if target_kind in (2, 4) else None, aux)
        result[source_index], result[target_index] = result[target_index], result[source_index]
    return NativeSquadDropResult(tuple(result), True, tuple(active))
