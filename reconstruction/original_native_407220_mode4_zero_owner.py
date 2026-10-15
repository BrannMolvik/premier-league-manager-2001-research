"""Original 407220(4, original-407EC0-null) native roster count source.

Static owner-authorized PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Original 407770(1) calls 407EC0 and then 407220(mode4, that pointer).
This is only the independently reached 407EC0 EAX==0 branch. Nonzero
dynamic owners dispatch substantial native 419350/4F8E40/other calls
and are deliberately NOT projected here. No original executable or
native callbacks were run, no GameState or score is mutated.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_native_406be0_roster_count import (
    SourceOriginal406BE0Player,
    SourceOriginal406BE0Count,
    source_original_406be0_arg1_one_arg2_zero_roster_count,
)


class Original407220SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal407220Mode4ZeroOwner:
    original_club_key_dword: int
    original_roster_count: int
    original_reached_407ec0_null: bool
    original_return_edi_count: int
    source_reached_41fab0_ids: tuple[int,...]
    source_eligible_41fab0_ids: tuple[int,...]
    native_407ec0_executed: bool = False
    native_41fab0_executed: bool = False
    native_407220_executed: bool = False
    live_game_state_modified: bool = False


def source_original_407220_mode4_with_null_407ec0(
    *,
    original_team_record: bytes,
    original_global_875640_player_array_address: int,
    original_ordered_player_records: tuple[SourceOriginal406BE0Player,...],
    original_reached_407ec0_return_eax: int,
) -> SourceOriginal407220Mode4ZeroOwner:
    """Source 407220 -> 41FAB0 -> flags+14 bit4, dynamic owner=0 only.

    Original 41FAB0(mode4, -1, team+4) first checks full signed
    WORD player+10 against DWORD team+4. Mismatch with mode4 returns
    EAX=0. Equal key reads original player+14 and returns bit4.
    407220 then re-tests SAME player+14 bit4. Only after that,
    original returned 407EC0 NULL pointer gives a direct increment
    at 40730D (no 419350 nor 4F8E40 calls).
    """
    if type(original_reached_407ec0_return_eax) is not int or original_reached_407ec0_return_eax!=0:
        raise Original407220SourceError(
            "actual zero pointer from reached 407EC0 required; nonzero dynamic owner unresolved")
    team=original_team_record
    if type(team) is not bytes or len(team)<0x298:
        raise Original407220SourceError("source original team bytes through +294 required")
    base=original_global_875640_player_array_address
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original407220SourceError("source original 875640 native base required")
    count=unpack_from("<i",team,0x294)[0]
    key=unpack_from("<I",team,4)[0]
    records=original_ordered_player_records
    if type(records) is not tuple:
        raise Original407220SourceError("actual original ordered player records required")
    if count<=0:
        if records:
            raise Original407220SourceError("407220 zero roster skips all player callbacks")
        return SourceOriginal407220Mode4ZeroOwner(key,count,True,0,(),())
    if len(team)<0x244+count*2 or len(records)!=count:
        raise Original407220SourceError("original team roster and complete native order required")
    reached=[]
    valid=[]
    for i,p in enumerate(records):
        if type(p) is not SourceOriginal406BE0Player:
            raise Original407220SourceError("source original player record type required")
        pid=unpack_from("<H",team,0x244+2*i)[0]
        expected=base+pid*0x250
        if (type(p.original_roster_word_id) is not int or p.original_roster_word_id!=pid or
            expected>0xffffffff or
            type(p.original_player_record_native_pointer) is not int or
            p.original_player_record_native_pointer!=expected):
            raise Original407220SourceError("original player +0x250 index/pointer or order mismatch")
        player=p.original_player_record_bytes
        if type(player) is not bytes or len(player)<0x18:
            raise Original407220SourceError("original player+10/+14 fields required")
        reached.append(pid)
        signed_key=unpack_from("<h",player,0x10)[0] & 0xffffffff
        flags14=unpack_from("<I",player,0x14)[0]
        if signed_key==key and flags14&0x10:
            valid.append(pid)
    return SourceOriginal407220Mode4ZeroOwner(
        key,count,True,len(valid),tuple(reached),tuple(valid),
    )


@dataclass(frozen=True)
class SourceOriginal407770FullArg1NullOwner:
    original_407220_mode4_count: SourceOriginal407220Mode4ZeroOwner
    original_406be0_role_one_count: SourceOriginal406BE0Count
    original_407770_arg1_receipt: object
    native_original_callbacks_executed: bool = False
    original_live_game_state_modified: bool = False


def source_original_407770_arg1_full_counts_with_null_407ec0(
    *,
    original_team_record: bytes,
    original_global_875640_player_array_address: int,
    original_ordered_player_records: tuple[SourceOriginal406BE0Player,...],
    original_reached_407ec0_return_eax: int,
    original_team_name_first_byte_if_reached: int,
) -> SourceOriginal407770FullArg1NullOwner:
    """Join original 407220 count==11 and 406BE0 count==1 on one source team.

    This branch is only reached when original 403640 returns zero and
    source first team-name byte != '!'; require this from raw team+74
    and independently reached native source name BYTE. Only original
    407EC0 result zero is qualified. The other 407220 owner paths
    require separate original 419350/4F8E40 source.
    """
    if type(original_team_record) is not bytes or len(original_team_record)<0x298:
        raise Original407220SourceError("actual original source team record required")
    if original_team_record[0x74] in (2,3):
        raise Original407220SourceError("403640 true: source 407220 not reached")
    if type(original_team_name_first_byte_if_reached) is not int or (
            original_team_name_first_byte_if_reached==0x21 or
            not 0<=original_team_name_first_byte_if_reached<=255):
        raise Original407220SourceError("actual reached non-bang team name first byte required")
    count1=source_original_407220_mode4_with_null_407ec0(
        original_team_record=original_team_record,
        original_global_875640_player_array_address=original_global_875640_player_array_address,
        original_ordered_player_records=original_ordered_player_records,
        original_reached_407ec0_return_eax=original_reached_407ec0_return_eax)
    count2=source_original_406be0_arg1_one_arg2_zero_roster_count(
        original_team_record=original_team_record,
        original_global_875640_player_array_address=original_global_875640_player_array_address,
        original_ordered_player_records=original_ordered_player_records)
    from original_native_407770_roster_eligibility import (
        source_original_407770_reached_roster_gate,
    )
    final=source_original_407770_reached_roster_gate(
        original_team_record=original_team_record,
        original_407770_argument=1,
        original_reached_403640_al_if_arg1=False,
        original_team_name_first_byte_if_reached=original_team_name_first_byte_if_reached,
        original_reached_407220_edi_if_arg1=count1.original_return_edi_count,
        original_reached_406be0_eax_if_arg1=count2.source_return_eax,
    )
    return SourceOriginal407770FullArg1NullOwner(count1,count2,final)
