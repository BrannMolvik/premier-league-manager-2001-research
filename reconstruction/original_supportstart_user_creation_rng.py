"""Native DBRUser name-pair creation before ordinary TeamSelect staff births.

Original 0x4D8EF3 -> 0x413BB0 -> 0x4258D0 -> 0x42C400.
After source club pointer +0x5B4 is stored, 0x42C400 invokes the
original 0x421C00 player-name pair chooser NINE times explicitly and
FOUR more times in a loop. This is 13 * TWO source CRT draws.
Unlike CSupportStaff 0x4CA660, there is NO '-' first-name retry here.

Requires caller-supplied original source group and the SAME already-owned
shared CRT as subsequent normal TeamSelect staff constructors. This
module does not seed RNG, register a user, claim original GUI success, or
write native user fields into live GameState. Excludes unresolved RNG in
other user constructor/selection subcalls.
"""
from __future__ import annotations
from dataclasses import dataclass

from fm2001_data import Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute

SOURCE_USER_EXPLICIT_NAME_PAIR_COUNT = 9
SOURCE_USER_LOOP_NAME_PAIR_COUNT = 4
SOURCE_USER_NAME_PAIR_COUNT = 13
SOURCE_USER_NAME_RNG_CALL_COUNT = 26


class OriginalSourceUserBirthNameError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalUserBirthNamePair:
    source_first_player_id: int
    source_surname_player_id: int
    first_text_owner_offset: int
    surname_text_owner_offset: int
    source_first_text: str
    source_surname_text: str


@dataclass(frozen=True)
class SourceOriginalUserBirthNameReceipt:
    source_pairs: tuple[SourceOriginalUserBirthNamePair, ...]

    @property
    def direct_source_rng_call_count(self) -> int:
        return len(self.source_pairs) * 2


def _source_slot_offsets() -> tuple[tuple[int, int], ...]:
    return (
        tuple((0x520 + 8*i, 0x524 + 8*i)
              for i in range(SOURCE_USER_EXPLICIT_NAME_PAIR_COUNT))
        + tuple((0x568 + 4*i, 0x578 + 4*i)
                for i in range(SOURCE_USER_LOOP_NAME_PAIR_COUNT))
    )


def consume_original_user_birth_name_pairs(
    rng,
    players: tuple[Player, ...],
    source_route: OriginalNameGroupCandidateRoute,
) -> SourceOriginalUserBirthNameReceipt:
    """Consume exactly 26 native 0x421C00 CRT draws from caller RNG owner.

    Original 0x42C400 does NOT test '-' or repeat any first/surname pair.
    It writes pointers into 13 native DBRUser fields, not staff personal names.
    """
    if not callable(getattr(rng, "randbelow", None)):
        raise OriginalSourceUserBirthNameError("Shared CRT owner is missing")
    if (type(players) is not tuple or not players
            or type(source_route) is not OriginalNameGroupCandidateRoute
            or len(players) != source_route.global_player_count
            or any(type(p) is not Player or p.index != i
                   for i, p in enumerate(players))):
        raise OriginalSourceUserBirthNameError("Original source player array invalid")
    if source_route.candidate_source == "filtered_nationality_players":
        eligible = source_route.source_record_positions
    elif source_route.candidate_source == "global_players":
        eligible = tuple(range(len(players)))
    else:
        raise OriginalSourceUserBirthNameError("Unknown original name-group route")
    if (not eligible or len(set(eligible)) != len(eligible)
            or any(type(i) is not int or not 0 <= i < len(players)
                   or not source_route.eligible_source_player_position(i)
                   for i in eligible)):
        raise OriginalSourceUserBirthNameError("Invalid source player-name pool")
    for i in eligible:
        row = players[i]
        if (type(row.first_name) is not str or type(row.surname) is not str
                or not row.first_name or not row.surname
                or "\x00" in row.first_name or "\x00" in row.surname):
            raise OriginalSourceUserBirthNameError("Missing source name text")
        try:
            row.first_name.encode("cp1252")
            row.surname.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalSourceUserBirthNameError("Original name not CP1252") from exc

    result=[]
    for first_field, last_field in _source_slot_offsets():
        a=rng.randbelow(len(eligible))
        b=rng.randbelow(len(eligible))
        if (type(a) is not int or type(b) is not int
                or not 0 <= a < len(eligible) or not 0 <= b < len(eligible)):
            raise OriginalSourceUserBirthNameError("Invalid shared CRT draw")
        first=eligible[a]
        last=eligible[b]
        result.append(SourceOriginalUserBirthNamePair(
            source_first_player_id=first,
            source_surname_player_id=last,
            first_text_owner_offset=first_field,
            surname_text_owner_offset=last_field,
            source_first_text=players[first].first_name,
            source_surname_text=players[last].surname,
        ))
    return SourceOriginalUserBirthNameReceipt(tuple(result))
