"""Explicit native first/reserve list binding; never a database-first-20 split.

Input selection/order must come from 4B7BD0 followed by 4B7500. Empty owners
and null player lookups remain separate from populated rows. This bounded
adapter does not fabricate a human lineup or accept a pointer event.
"""
from dataclasses import dataclass

from original_squad_membership import NativeSquadMembership, native_squad_slot
from original_squad_presenter import build_squad_row_viewport, OriginalSquadViewportSnapshot


@dataclass(frozen=True)
class OriginalPairedSquadSnapshot:
    first: OriginalSquadViewportSnapshot
    reserve: OriginalSquadViewportSnapshot
    first_empty_slots: tuple[int, ...]
    reserve_empty_slots: tuple[int, ...]
    first_null_player_slots: tuple[int, ...]
    reserve_null_player_slots: tuple[int, ...]
    unpresented_player_ids: tuple[int, ...]


def build_paired_squad_snapshot(membership, rows):
    """Bind player identity after each native slot lookup, preserving all holes.

    4B7170's -1 branch constructs PPlayerEmptyRow/PSCFEmptyRow. Its nonnegative
    branch calls 406F00; indices >= roster count return null and create no row.
    Negative indices other than -1 would read outside the retained word roster
    and are intentionally rejected rather than using Python negative indexing.
    """
    if not isinstance(membership, NativeSquadMembership):
        raise ValueError('Paired Squad requires native prepared ordered membership')
    rows = tuple(rows)
    by_id = {row.player_id: row for row in rows}
    ids = tuple(p.player_id for p in membership.members)
    if len(by_id) != len(rows) or set(by_id) != set(ids):
        raise ValueError('Paired Squad source rows do not match the native roster')
    viewports, empty_sets, null_sets = [], [], []
    presented = set()
    for reserve in (False, True):
        slots, empty, null = [], [], []
        for visible_index in range(20):
            index = native_squad_slot(membership, visible_index=visible_index,
                                      reserve=reserve, source_count=len(ids))
            if index == -1:
                empty.append(visible_index)
                slots.append(None)
            elif index >= len(ids):
                null.append(visible_index)
                slots.append(None)
            elif index < 0:
                raise ValueError('Native Squad slot reads outside retained roster')
            else:
                player_id = ids[index]
                slots.append(by_id[player_id])
                presented.add(player_id)
        viewports.append(build_squad_row_viewport(slots))
        empty_sets.append(tuple(empty))
        null_sets.append(tuple(null))
    return OriginalPairedSquadSnapshot(
        *viewports, empty_sets[0], empty_sets[1], null_sets[0], null_sets[1],
        tuple(player_id for player_id in ids if player_id not in presented))
