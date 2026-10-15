"""Original 405A20 -> 4058B0 merge-sort / 40B4A0 -> 417E20 score.

Source original canonical footballmanager.exe 4,714,541 bytes SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This independently reproduces a bounded source comparison/sort on supplied
original pre-405A20 bytes. Native 405A20, allocator, callbacks, GUI and real
team/world writes are NOT executed. A predicted sorted team is NOT proof
that the reached native callback completed or that 409B50 has run.
"""
from dataclasses import dataclass
from struct import pack_into, unpack_from
from original_native_406be0_roster_count import SourceOriginal406BE0Player


class Original405A20SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal405A20NativeRosterSort:
    original_team_key_dword: int
    original_team_roster_before_405a20: bytes
    source_projected_team_after_405a20: bytes
    original_player_records_sorted_for_510cd0: tuple[SourceOriginal406BE0Player,...]
    source_player_ids_before: tuple[int,...]
    source_player_ids_after: tuple[int,...]
    source_player_score_pairs_before: tuple[tuple[int,int],...]
    original_405a20_executed: bool = False
    original_4058b0_allocations_executed: bool = False
    original_417e20_callbacks_executed: bool = False
    original_game_state_modified: bool = False


def source_original_405a20_sort_team_roster_by_417e20(
    *, original_team_at_405a20: bytes,
    original_global_875640_player_base: int,
    original_ordered_player_records: tuple[SourceOriginal406BE0Player,...],
    original_874b68_role_table: bytes,
) -> SourceOriginal405A20NativeRosterSort:
    """Native 40B4A0 is score(first)<score(second); merge picks right
    on true, left on equal. Equivalent to stable descending key 417E20.
    That scoring method uses source full team key, signed player WORD+10,
    +14 bits4/5 or +174 bits0/1, 4EA3C0 returned status BYTE+3&31,
    and subtracts original 874B68[20*role +16] BYTE.
    """
    team=original_team_at_405a20
    if type(team) is not bytes or len(team)<0x298:
        raise Original405A20SourceError("native pre-405A20 team bytes through +294 required")
    base=original_global_875640_player_base
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original405A20SourceError("source original 875640 player array base required")
    table=original_874b68_role_table
    if type(table) is not bytes or len(table)<32*20:
        raise Original405A20SourceError("source original 874B68 32*20 role-table bytes required")
    count=unpack_from("<i",team,0x294)[0]
    rows=original_ordered_player_records
    if type(rows) is not tuple:
        raise Original405A20SourceError("original ordered roster records tuple required")
    if count<0 or count>360 or len(rows)!=count or len(team)<0x244+2*count:
        raise Original405A20SourceError("native roster count/order/capacity invalid or unsafe")
    key=unpack_from("<I",team,0x04)[0]
    scores=[]
    for i,row in enumerate(rows):
        if type(row) is not SourceOriginal406BE0Player:
            raise Original405A20SourceError("actual native player receipt type required")
        pid=unpack_from("<H",team,0x244+2*i)[0]
        pointer=base+pid*0x250
        if (pointer>0xffffffff or type(row.original_roster_word_id) is not int or
            row.original_roster_word_id!=pid or
            type(row.original_player_record_native_pointer) is not int or
            row.original_player_record_native_pointer!=pointer):
            raise Original405A20SourceError("native 875640 + roster WORD*0x250 pointer/order required")
        player=row.original_player_record_bytes
        if type(player) is not bytes or len(player)<0x24c:
            raise Original405A20SourceError("source 417E20 player +248 native status pointer required")
        status=row.original_4ea3c0_status_record_if_417ee0_true
        if (unpack_from("<I",player,0x248)[0]==0 or type(status) is not bytes or len(status)<4):
            raise Original405A20SourceError("native 4EA3C0 pointer and separate status+3 required")
        owner=unpack_from("<h",player,0x10)[0]&0xffffffff
        flags=unpack_from("<I",player,0x14)[0]
        extras=unpack_from("<I",player,0x174)[0]
        tier=0
        if owner==key:
            if flags & 0x10:
                tier=4000
            elif flags & 0x20:
                tier=3000
            elif extras & 1:
                tier=2000
            elif extras & 2:
                tier=1000
        role=status[3]&0x1f
        penalty=table[role*20+16]
        scores.append((pid,tier-penalty))
    # Native 4058B0 recursively sorts the mutable roster WORD array.
    # 40B4A0 returns 1 iff score(left)<score(right), so merge chooses
    # right only for a strictly larger score. Equal scores keep left:
    # stable descending order, not ascending and not player-ID order.
    indexes=sorted(range(count),key=lambda ix:-scores[ix][1])
    new_team=bytearray(team)
    for slot,ix in enumerate(indexes):
        pack_into("<H",new_team,0x244+slot*2,scores[ix][0])
    return SourceOriginal405A20NativeRosterSort(
        key,team,bytes(new_team),
        tuple(rows[ix] for ix in indexes),
        tuple(pair[0] for pair in scores),
        tuple(scores[ix][0] for ix in indexes),
        tuple(scores),False,False,False,False,
    )
