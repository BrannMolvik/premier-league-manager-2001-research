"""Source-exact 406BE0(1,0) counted roster role from original player bytes.

Original source: SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
footballmanager.exe, static x86 analysis only. The native team at ECX has
+294 signed number of roster WORD IDs at +244; these address original global
875640 source player records (0x250 bytes each). This routine is a pure,
immutable bounded projection of 406BE0's reached (arg1=1,arg2=0) count.
No native callback, calendar, player world, match, GameState or GUI executes.
"""
from dataclasses import dataclass
from struct import unpack_from


class Original406BE0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal406BE0Player:
    original_roster_word_id: int
    original_player_record_native_pointer: int
    original_player_record_bytes: bytes
    original_4ea3c0_status_record_if_417ee0_true: bytes | None


@dataclass(frozen=True)
class SourceOriginal406BE0Count:
    original_club_key_dword: int
    original_roster_count: int
    source_return_eax: int
    reached_417ee0_player_ids: tuple[int, ...]
    reached_4ea3c0_player_ids: tuple[int, ...]
    matched_4ea3c0_role_one_player_ids: tuple[int, ...]
    native_406be0_executed: bool = False
    original_callback_world_executed: bool = False
    live_game_state_modified: bool = False


def source_original_406be0_arg1_one_arg2_zero_roster_count(
    *,
    original_team_record: bytes,
    original_global_875640_player_array_address: int,
    original_ordered_player_records:
        tuple[SourceOriginal406BE0Player, ...],
) -> SourceOriginal406BE0Count:
    """Source at 406BE0..406C6A with exactly native args (1,0).

    417EE0 compares signed WORD player+10 to team+4 DWORD, then tests
    player+14 bit4. Only on source success does 4EA3C0 get called on the
    *separate source pointer player+248*. It computes
    (BYTE status+3)&0x1f; exact == arg1=1 increments EAX count.
    The actual outer 407770(1) additionally requires this count == 1,
    independent of its 403640/407220 EDI==11 check.
    """
    raw=original_team_record
    if type(raw) is not bytes or len(raw)<0x298:
        raise Original406BE0SourceError("actual source team through +294 required")
    base=original_global_875640_player_array_address
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original406BE0SourceError("native 875640 player-array base required")
    count=unpack_from("<i",raw,0x294)[0]
    club_key=unpack_from("<I",raw,0x4)[0]
    users=original_ordered_player_records
    if type(users) is not tuple:
        raise Original406BE0SourceError("original per-roster player tuples required")
    if count<=0:
        if users:
            raise Original406BE0SourceError("no original 417EE0 callbacks reached")
        return SourceOriginal406BE0Count(club_key,count,0,(),(),())
    if len(raw)<0x244+2*count or len(users)!=count:
        raise Original406BE0SourceError("full source roster WORD order and records required")
    reached_gate=[]
    reached_status=[]
    matched=[]
    for index,receipt in enumerate(users):
        if type(receipt) is not SourceOriginal406BE0Player:
            raise Original406BE0SourceError("source player receipt type required")
        pid=unpack_from("<H",raw,0x244+2*index)[0]
        expected=base+pid*0x250
        if (expected>0xffffffff or
            type(receipt.original_roster_word_id) is not int or
            receipt.original_roster_word_id!=pid or
            type(receipt.original_player_record_native_pointer) is not int or
            receipt.original_player_record_native_pointer!=expected):
            raise Original406BE0SourceError("original 875640+WORD*0x250 pointer and roster order required")
        player=receipt.original_player_record_bytes
        if type(player) is not bytes or len(player)<0x24c:
            raise Original406BE0SourceError("original player +248 status pointer required")
        # For actual 406BE0(1,0), the original excluded-player pointer is
        # zero, so nonzero original base+id*0x250 cannot equal exclusion.
        reached_gate.append(pid)
        sign_word=unpack_from("<h",player,0x10)[0]
        source_kind_key=sign_word & 0xffffffff
        eligible=(club_key==source_kind_key and
                  (unpack_from("<I",player,0x14)[0]&0x10)!=0)
        status=receipt.original_4ea3c0_status_record_if_417ee0_true
        if not eligible:
            if status is not None:
                raise Original406BE0SourceError("unreached native 4EA3C0 status provided")
            continue
        pointer=unpack_from("<I",player,0x248)[0]
        if not pointer or type(status) is not bytes or len(status)<4:
            raise Original406BE0SourceError("native 4EA3C0 status pointer and bytes required")
        reached_status.append(pid)
        if status[3]&0x1f==1:
            matched.append(pid)
    return SourceOriginal406BE0Count(
        club_key,count,len(matched),tuple(reached_gate),
        tuple(reached_status),tuple(matched),
    )


@dataclass(frozen=True)
class SourceOriginal407770Arg1From406BE0:
    """Source-derived role-one count and outer 407770(1) comparison only."""
    original_406be0_count: SourceOriginal406BE0Count
    original_407770_arg1_receipt: object
    live_native_match_executed: bool = False
    live_game_state_modified: bool = False


def source_original_407770_arg1_with_406be0_original_player_bytes(
    *, original_team_record: bytes,
    original_global_875640_player_array_address: int,
    original_ordered_player_records: tuple[SourceOriginal406BE0Player, ...],
    original_reached_403640_al: bool,
    original_team_name_first_byte_if_reached: int | None,
    original_reached_407220_edi_if_reached: int | None,
) -> SourceOriginal407770Arg1From406BE0:
    """Source-compose 406BE0(1,0) return with 407770 arg1, not live match.

    This only visits 406BE0 on the source 407770 team+294 >=11 path.
    The remaining 407220 branch is not derived: require independently
    reached actual EDI whenever original 403640 / '!' paths skip it.
    """
    if type(original_team_record) is not bytes or len(original_team_record)<0x298:
        raise Original406BE0SourceError("original roster record required")
    if unpack_from("<i",original_team_record,0x294)[0]<11:
        raise Original406BE0SourceError("407770 roster<11 path never reaches 406BE0")
    count=source_original_406be0_arg1_one_arg2_zero_roster_count(
        original_team_record=original_team_record,
        original_global_875640_player_array_address=original_global_875640_player_array_address,
        original_ordered_player_records=original_ordered_player_records)
    from original_native_407770_roster_eligibility import (
        source_original_407770_reached_roster_gate,
    )
    outer=source_original_407770_reached_roster_gate(
        original_team_record=original_team_record,
        original_407770_argument=1,
        original_reached_403640_al_if_arg1=original_reached_403640_al,
        original_team_name_first_byte_if_reached=original_team_name_first_byte_if_reached,
        original_reached_407220_edi_if_arg1=original_reached_407220_edi_if_reached,
        original_reached_406be0_eax_if_arg1=count.source_return_eax,
    )
    return SourceOriginal407770Arg1From406BE0(count,outer)
