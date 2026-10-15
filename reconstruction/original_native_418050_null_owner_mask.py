"""Native 418050 no-side-owner, bit11-clear original 409C90 player mask.

Original verified authorized PE footballmanager.exe 4,714,541 bytes
SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Pure source stage, NO native callback, dynamic 419350/4F8E40, roster
mutation, score, GameState, SaveLoad, match or Windows GUI executed.
"""
from dataclasses import dataclass
from struct import unpack_from
from original_native_406be0_roster_count import SourceOriginal406BE0Player


class Original418050SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal418050NoOwnerPlayerGate:
    original_player_pointer: int
    original_player_418050_team_full_dword_key: int
    original_player_signed_word10: int
    original_player_flags14_low3: int
    original_player_41b490_bit11: int
    original_null_side_owner_pointer: int
    source_418050_return_al: int
    native_418050_executed: bool = False
    native_41b490_executed: bool = False
    live_game_state_modified: bool = False


def source_original_418050_null_owner_41b490_clear_player_gate(
    *, original_player_pointer: int,
    original_player_record: bytes,
    original_team_full_owner_key: int,
    original_reached_418050_side_owner_pointer: int,
) -> SourceOriginal418050NoOwnerPlayerGate:
    """Native 418050 with actual second pointer EDI=0 (skip dynamic
    41B360, 4F8E40, 419350). It initially sets BL=1 when player
    BYTE+14 bits0..2 nonzero OR player's signed WORD+10 != team+4.

    Native always calls 41B490 and if player+14 bit11=1, then calls
    41B4D0 and 4E9BE0 on a separate global node. That case remains
    source-unresolved. When bit11=0, it returns BL unmodified.
    """
    if (type(original_player_pointer) is not int or
        not 0<original_player_pointer<=0xffffffff):
        raise Original418050SourceError("actual original player base pointer required")
    p=original_player_record
    if type(p) is not bytes or len(p)<0x18:
        raise Original418050SourceError("native source player+10/+14 required")
    key=original_team_full_owner_key
    if type(key) is not int or not 0<=key<=0xffffffff:
        raise Original418050SourceError("actual original team+4 full DWORD required")
    if type(original_reached_418050_side_owner_pointer) is not int or (
            original_reached_418050_side_owner_pointer!=0):
        raise Original418050SourceError(
            "actual original 418050 EDI pointer must be NULL, dynamic branch unmodeled")
    club=unpack_from("<h",p,0x10)[0]
    flags=unpack_from("<I",p,0x14)[0]
    bit11=(flags>>11)&1
    if bit11:
        raise Original418050SourceError(
            "source original 41B490 bit11 reaches unqualified 41B4D0/4E9BE0 callbacks")
    al=int(bool(flags&0x7) or ((club&0xffffffff)!=key))
    return SourceOriginal418050NoOwnerPlayerGate(
        original_player_pointer,key,club,flags&7,bit11,0,al)


@dataclass(frozen=True)
class SourceOriginal409C90NonClass23NoOwnerFirstMask:
    original_team_type_byte74: int
    original_409c90_reached_roster_arg: int
    source_ordered_original_roster_ids: tuple[int,...]
    source_reached_418050_results: tuple[SourceOriginal418050NoOwnerPlayerGate,...]
    source_second_allocated_mask_bytes: bytes
    native_409c90_executed: bool = False
    original_game_state_modified: bool = False


def source_original_409c90_nonclass23_noowner_mask(
    *, original_team_record_at_409c90: bytes,
    original_reached_roster_count_409b50_argument: int,
    original_reached_418050_side_owner_pointer: int,
    original_875640_player_array_pointer: int,
    original_ordered_player_records: tuple[SourceOriginal406BE0Player,...],
) -> SourceOriginal409C90NonClass23NoOwnerFirstMask:
    """Source 409D0E nonclass2/3→418050 per player. Exactly native
    signed roster count and ordered player WORD IDs, original global
    875640+index*0x250; complete only if each player has native
    bit11 clear and actual reached side owner pointer is NULL.
    Produces only the per-roster temporary byte mask at 409D5E.
    """
    team=original_team_record_at_409c90
    count=original_reached_roster_count_409b50_argument
    base=original_875640_player_array_pointer
    rows=original_ordered_player_records
    if type(team) is not bytes or len(team)<0x298:
        raise Original418050SourceError("original team bytes through +294 required")
    if team[0x74] in (2,3):
        raise Original418050SourceError("native 403640 true dispatches 418130, not 418050")
    if type(count) is not int or not 0<=count<=360:
        raise Original418050SourceError("reached signed native 409C90 roster count0..360 required")
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original418050SourceError("source global player array base required")
    if type(rows) is not tuple or len(rows)!=count or len(team)<0x244+2*count:
        raise Original418050SourceError("complete original ordered roster WORD IDs and records required")
    key=unpack_from("<I",team,4)[0]
    names=[]
    gates=[]
    for i,rec in enumerate(rows):
        pid=unpack_from("<H",team,0x244+i*2)[0]
        ptr=base+pid*0x250
        if (type(rec) is not SourceOriginal406BE0Player or
            type(rec.original_roster_word_id) is not int or rec.original_roster_word_id!=pid or
            type(rec.original_player_record_native_pointer) is not int or
            rec.original_player_record_native_pointer!=ptr or ptr>0xffffffff):
            raise Original418050SourceError("source indexed player pointer/order mismatch")
        gate=source_original_418050_null_owner_41b490_clear_player_gate(
            original_player_pointer=ptr,
            original_player_record=rec.original_player_record_bytes,
            original_team_full_owner_key=key,
            original_reached_418050_side_owner_pointer=original_reached_418050_side_owner_pointer)
        names.append(pid)
        gates.append(gate)
    return SourceOriginal409C90NonClass23NoOwnerFirstMask(
        team[0x74],count,tuple(names),tuple(gates),
        bytes(g.source_418050_return_al for g in gates))
