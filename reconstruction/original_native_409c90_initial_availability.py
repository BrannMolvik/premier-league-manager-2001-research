"""Join original 409C90 initial roster mask for both native 403640 paths.

Original source, static canonical SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
At 409D12 team BYTE+74=2 or3 -> 418130, otherwise ->418050
with source native team+4 key and a 409C90 at-call owner pointer.
All 418050 dynamic callback receipts are independent ORIGINAL observations.
No callbacks or native roster/world mutations execute here.
"""
from dataclasses import dataclass
from struct import unpack_from
from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_418050_dynamic_eligibility import SourceOriginal418050Eligibility
from original_native_409c90_assignment_status import (
    source_original_409c90_class23_initial_roster_mask,
)

class Original409C90InitialMaskSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal409C90InitialMask:
    original_team_class_byte74: int
    original_club_key_dword: int
    original_reached_roster_count: int
    original_source_409c90_dynamic_owner_ptr: int
    original_roster_word_ids_in_order: tuple[int,...]
    source_mask_bytes: bytes
    original_418050_receipts_if_reached: tuple[SourceOriginal418050Eligibility,...]
    native_original_callbacks_executed: bool = False
    original_native_heap_buffer_allocated: bool = False
    live_game_state_modified: bool = False


def source_original_409c90_initial_roster_mask_all_team_classes(
    *, original_team_record_at_409c90: bytes,
    original_reached_409b50_roster_count_argument: int,
    original_global_875640_native_player_base: int,
    original_ordered_at_call_player_records: tuple[SourceOriginal406BE0Player,...],
    original_reached_409c90_dynamic_owner_ptr: int | None = None,
    original_418050_receipts_if_reached:
        tuple[SourceOriginal418050Eligibility,...] | None = None,
) -> SourceOriginal409C90InitialMask:
    """Bounded original 409D0E→409D5E exact AL byte mask.

    Original class2/3 calls 418130(player), a pure player+14 bits0/1
    test. Other classes call 418050(player,team+4, dynamic owner ptr),
    whose original callbacks MAY MUTATE PLAYER/WORLD and are NEVER
    inferred from current reconstruction. Require a complete original
    source receipt for EVERY reached 418050 in current roster order.
    """
    team=original_team_record_at_409c90
    count=original_reached_409b50_roster_count_argument
    base=original_global_875640_native_player_base
    rows=original_ordered_at_call_player_records
    if type(team) is not bytes or len(team)<0x298:
        raise Original409C90InitialMaskSourceError("original team through +294 bytes required")
    if type(count) is not int or not 0<=count<=360:
        raise Original409C90InitialMaskSourceError("bounded actual 409B50 signed roster count required")
    roster_count=unpack_from("<i",team,0x294)[0]
    if count>roster_count or len(team)<0x244+count*2:
        raise Original409C90InitialMaskSourceError(
            "requested reached 409C90 roster count extends past native actual team roster")
    if type(base) is not int or not 0<base<=0xffffffff or type(rows) is not tuple or len(rows)!=count:
        raise Original409C90InitialMaskSourceError("complete source 875640 indexed player records required")
    clas=team[0x74]
    key=unpack_from("<I",team,4)[0]
    ids=[]
    for i,row in enumerate(rows):
        pid=unpack_from("<H",team,0x244+2*i)[0]
        expected=base+pid*0x250
        if (type(row) is not SourceOriginal406BE0Player or
                type(row.original_roster_word_id) is not int or
                row.original_roster_word_id!=pid or expected>0xffffffff or
                type(row.original_player_record_native_pointer) is not int or
                row.original_player_record_native_pointer!=expected or
                type(row.original_player_record_bytes) is not bytes or
                len(row.original_player_record_bytes)<0x178):
            raise Original409C90InitialMaskSourceError(
                "original roster WORD/0x250 player identity and at-call bytes required")
        ids.append(pid)
    if clas in (2,3):
        if original_reached_409c90_dynamic_owner_ptr is not None or (
                original_418050_receipts_if_reached is not None):
            raise Original409C90InitialMaskSourceError("class 2/3 418130 never calls 418050")
        try:
            r=source_original_409c90_class23_initial_roster_mask(
                original_team_record_at_409c90=team,
                original_409b50_reached_roster_count_argument=count,
                original_global_875640_player_base=base,
                original_ordered_player_records=rows,
            )
        except ValueError as exc:
            raise Original409C90InitialMaskSourceError("original 418130 class mask source invalid") from exc
        return SourceOriginal409C90InitialMask(
            clas,key,count,0,tuple(ids),r.source_second_allocated_mask_bytes,())
    ptr=original_reached_409c90_dynamic_owner_ptr
    receipts=original_418050_receipts_if_reached
    if (type(ptr) is not int or not 0<=ptr<=0xffffffff or
            type(receipts) is not tuple or len(receipts)!=count):
        raise Original409C90InitialMaskSourceError(
            "independently reached 409C90 dynamic owner and all 418050 return receipts required")
    mask=[]
    for i,(row,receipt) in enumerate(zip(rows,receipts)):
        if (type(receipt) is not SourceOriginal418050Eligibility or
            receipt.original_player_record_at_418050!=row.original_player_record_bytes or
            receipt.original_player_word_id!=ids[i] or
            receipt.original_source_club_key!=key or
            receipt.original_owner_pointer_at_call!=ptr or
            receipt.native_418050_executed or
            receipt.live_player_or_match_world_modified):
            raise Original409C90InitialMaskSourceError(
                "unqualified source 418050 result or wrong native roster/owner/call snapshot")
        mask.append(int(receipt.original_source_return_al_nonzero))
    return SourceOriginal409C90InitialMask(
        clas,key,count,ptr,tuple(ids),bytes(mask),receipts)
