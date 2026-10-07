"""Native 4B7500 ordering and 4B6FE0 slots, for an explicitly prepared roster.

This is not the preceding 4B7BD0 reserve/overflow producer. It is deliberately
not connected to the ordinary host until that producer is source-integrated.
Selection values are native 4218E0: none, reserve sub, reserve XI, first sub,
first XI. No database-first-20 split or scrollbar is inferred here.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class NativeSquadMember:
    player_id: int
    selection: int
    current_role: int
    preferred_role: int

    def __post_init__(self):
        for name, maximum in (('player_id', 65535), ('selection', 4),
                              ('current_role', 31), ('preferred_role', 31)):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= maximum:
                raise ValueError(f'Invalid native Squad {name}')


@dataclass(frozen=True)
class NativeSquadMembership:
    members: tuple[NativeSquadMember, ...]
    substitute_quota: int
    first_list_boundary: int
    cleared_player_ids: tuple[int, ...]


def _quota(value):
    if type(value) is not int or not 0 <= value <= 9:
        raise ValueError('Squad quota must be an explicit native value in 0..9')


def _adjacent_passes(members, start, should_swap):
    changed = True
    while changed:
        changed = False
        for index in range(start, len(members) - 1):
            if should_swap(members[index], members[index + 1]):
                members[index], members[index + 1] = members[index + 1], members[index]
                changed = True


def prepare_ordered_squad_membership(prepared_members, *, substitute_quota):
    """Apply only 4B7500 to retained state AFTER native reserve preparation.

    Excess clearing returns updated flags/current roles rather than mutating
    GameState. Its other native bytes are not represented by this bounded view.
    """
    _quota(substitute_quota)
    members = list(prepared_members)
    if len(members) > 40:
        raise ValueError('Native +244 word roster cannot overlap its +294 count')
    if any(not isinstance(member, NativeSquadMember) for member in members):
        raise ValueError('Prepared Squad requires explicit native member state')
    if len({member.player_id for member in members}) != len(members):
        raise ValueError('Native Squad roster contains duplicate player IDs')
    counts = {selection: sum(m.selection == selection for m in members)
              for selection in range(1, 5)}
    limits = {1: 3, 2: 11, 3: substitute_quota, 4: 11}
    cleared = []
    for index, member in enumerate(members):
        if member.selection and counts[member.selection] > limits[member.selection]:
            counts[member.selection] -= 1
            cleared.append(member.player_id)
            members[index] = replace(member, selection=0, current_role=member.preferred_role)

    def first_swap(left, right):
        if right.selection not in (4, 3):
            return False
        if right.selection == 3 and left.selection == 4:
            return False
        if left.selection == right.selection:
            return right.current_role < left.current_role
        return True

    _adjacent_passes(members, 0, first_swap)
    first_count = sum(m.selection in (4, 3) for m in members)
    unassigned_count = sum(m.selection == 0 for m in members)
    addition = min(unassigned_count, 20 - (11 + substitute_quota))
    boundary = 11 + substitute_quota
    reserve_start = first_count
    if addition > 0:
        def unassigned_swap(left, right):
            return (right.selection not in (2, 1) and
                    (right.current_role > left.current_role or left.selection in (2, 1)))
        _adjacent_passes(members, first_count, unassigned_swap)
        boundary += addition
        reserve_start += addition

    def reserve_swap(left, right):
        if right.selection not in (2, 1):
            return False
        if right.selection == 1 and left.selection == 2:
            return False
        if left.selection == right.selection:
            return right.current_role < left.current_role
        return True

    _adjacent_passes(members, reserve_start, reserve_swap)
    return NativeSquadMembership(tuple(members), substitute_quota, boundary, tuple(cleared))


def native_squad_slot(membership, *, visible_index, reserve, source_count):
    """Return 4B6FE0's ordered index, or -1 for its original empty-row owner.

    Only filter=0 is qualified here: virtual +C0 must equal actual roster count.
    The membership D8 is produced, never guessed from allocation or row capacity.
    """
    if not isinstance(membership, NativeSquadMembership):
        raise ValueError('Native Squad membership is missing')
    if type(visible_index) is not int or not 0 <= visible_index < 20 or type(reserve) is not bool:
        raise ValueError('Invalid native Squad slot request')
    if type(source_count) is not int or source_count != len(membership.members):
        raise ValueError('Default native virtual +C0 count must equal the roster count')
    _quota(membership.substitute_quota)
    counts = {selection: sum(m.selection == selection for m in membership.members)
              for selection in range(1, 5)}
    fa, fs, ra, rs = (counts[selection] for selection in (4, 3, 2, 1))
    quota = membership.substitute_quota
    boundary = membership.first_list_boundary
    if not reserve:
        offset = (11 - fa if visible_index >= 11 else 0)
        if visible_index >= 11 + quota:
            offset += quota - fs
        if (visible_index >= boundary or fa <= visible_index < 11 or
                11 + fs <= visible_index < 11 + quota):
            return -1
        return visible_index - offset

    index = visible_index + 20
    offset = 11 + quota - fs - fa
    original_offset = offset
    full_reserve = source_count >= quota + 25
    if full_reserve:
        if index >= 31:
            offset += 11 - ra
        if index >= 34:
            offset += 3 - rs
    limit = source_count + original_offset + offset - boundary + 20
    if (index >= limit or (full_reserve and
            (20 + ra <= index < 31 or 31 + rs <= index < 34))):
        return -1
    return boundary + visible_index - offset
