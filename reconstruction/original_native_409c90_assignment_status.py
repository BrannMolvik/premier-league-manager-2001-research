"""Original 409C90 selected-player status mutations, SOURCE PREFIX ONLY.

Owner-authorized footballmanager.exe (4,714,541 bytes,
SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3)
was statically inspected, never run/committed. Native 409C90 has extensive
mutable selection/score loops and nested callbacks; these prefix snapshots
do NOT execute it or certify GameState, SaveLoad or match score.
"""
from dataclasses import dataclass
from struct import pack_into,unpack_from


class Original409C90SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal4EA3StatusWrites:
    source_status_pointer: int
    original_status_before: bytes
    original_reached_4ea330_role_byte: int
    original_reached_4ea350_position_byte: int
    source_status_after_two_stores: bytes
    native_4ea330_executed: bool = False
    native_4ea350_executed: bool = False
    original_live_game_state_modified: bool = False


def source_original_4ea330_then_4ea350_status_writes(
    *, original_source_status_pointer: int,
    original_source_status_record_before: bytes,
    original_4ea330_reached_role_argument_byte: int,
    original_4ea350_reached_position_argument_byte: int,
) -> SourceOriginal4EA3StatusWrites:
    """Exact original low five bits at status+3 and low four at status+4.

    Source native 4EA330:
      byte3 := (byte3 & 0xE0) | (argument & 0x1F)
    Source native 4EA350:
      byte4 := (byte4 & 0xF0) | (argument & 0x0F)
    Called in this order for one actually reached 409C90 selected player
    at 40A21E and 40A234. No callback is run by this projection.
    """
    p=original_source_status_pointer
    b=original_source_status_record_before
    role=original_4ea330_reached_role_argument_byte
    pos=original_4ea350_reached_position_argument_byte
    if type(p) is not int or not 0<p<=0xffffffff:
        raise Original409C90SourceError("actual source player+248 status pointer required")
    if type(b) is not bytes or len(b)<5:
        raise Original409C90SourceError("original status bytes through +4 required")
    if any(type(x) is not int or not 0<=x<=255 for x in (role,pos)):
        raise Original409C90SourceError("reached original source BYTE arguments required")
    out=bytearray(b)
    out[3]=(b[3]&0xe0)|(role&0x1f)
    out[4]=(b[4]&0xf0)|(pos&0x0f)
    return SourceOriginal4EA3StatusWrites(p,b,role,pos,bytes(out))


@dataclass(frozen=True)
class SourceOriginal4182F0FirstFlagWrite:
    source_native_player_pointer: int
    source_player_before: bytes
    source_player_after_first_flag14_bit4_store: bytes
    original_other_4182f0_callbacks_executed: bool = False
    native_4182f0_executed: bool = False
    live_game_state_modified: bool = False


def source_original_4182f0_initial_player_flag14_bit4_store(
    *, original_native_player_pointer: int,original_native_player_record_before: bytes,
) -> SourceOriginal4182F0FirstFlagWrite:
    """Only 4182F3 player+14 |=0x10, not full native 4182F0 transaction.

    Original immediately calls 418160,418180,418170,417340 and may call
    41EDF0; these side effects remain unresolved and MUST NOT be dropped
    from real GameState while claiming source-original roster changes.
    """
    p=original_native_player_pointer
    b=original_native_player_record_before
    if type(p) is not int or not 0<p<=0xffffffff:
        raise Original409C90SourceError("actual native player pointer required")
    if type(b) is not bytes or len(b)<0x18:
        raise Original409C90SourceError("actual original player flags+14 DWORD required")
    out=bytearray(b)
    pack_into("<I",out,0x14,unpack_from("<I",b,0x14)[0]|0x10)
    return SourceOriginal4182F0FirstFlagWrite(p,b,bytes(out))


@dataclass(frozen=True)
class SourceOriginal409C90SelectedPlayerPrefix:
    original_40a1f8_native_stack_cmp_equal_one: bool
    original_player_status_pointer: int
    original_native_player_pointer: int
    role_and_position_status_source_writes: SourceOriginal4EA3StatusWrites
    player_flag_bit4_first_source_store: SourceOriginal4182F0FirstFlagWrite
    native_409c90_executed: bool = False
    native_4ea330_4ea350_4182f0_executed: bool = False
    complete_original_mutable_world_qualified: bool = False
    live_game_state_modified: bool = False


def source_original_409c90_one_selected_player_source_prefix(
    *,original_40a1f8_reached_stack_eax: int,
    original_native_player_pointer: int,
    original_native_player_record_at_40a211: bytes,
    original_native_player_status_record_at_40a21d: bytes,
    original_876cb8_reached_role_dword: int,
    original_876cbc_reached_position_byte: int,
) -> SourceOriginal409C90SelectedPlayerPrefix:
    """True native 40A1F8 == 1 branch only, before 4182F0 other callbacks.

    The first status writer gets full DWORD 876CB8 but consumes only
    the low input BYTE, and subsequent position writer consumes BYTE
    876CBC. Original player+248 is status owner; do not substitute
    player base bytes for its separately addressed status record.
    """
    if type(original_40a1f8_reached_stack_eax) is not int or original_40a1f8_reached_stack_eax!=1:
        raise Original409C90SourceError("original reached 40A1F8 EAX==1 required")
    player=original_native_player_record_at_40a211
    if type(player) is not bytes or len(player)<0x24c:
        raise Original409C90SourceError("original player+248 status pointer required")
    status_pointer=unpack_from("<I",player,0x248)[0]
    role=original_876cb8_reached_role_dword
    pos=original_876cbc_reached_position_byte
    if type(role) is not int or not 0<=role<=0xffffffff:
        raise Original409C90SourceError("exact source original 876CB8 role DWORD required")
    out=source_original_4ea330_then_4ea350_status_writes(
        original_source_status_pointer=status_pointer,
        original_source_status_record_before=original_native_player_status_record_at_40a21d,
        original_4ea330_reached_role_argument_byte=role&0xff,
        original_4ea350_reached_position_argument_byte=pos,
    )
    flags=source_original_4182f0_initial_player_flag14_bit4_store(
        original_native_player_pointer=original_native_player_pointer,
        original_native_player_record_before=player,
    )
    return SourceOriginal409C90SelectedPlayerPrefix(True,status_pointer,original_native_player_pointer,out,flags)


@dataclass(frozen=True)
class SourceOriginal41FA50ClubKeyPredicate:
    original_player_signed_word10: int
    original_player_signed_word72_if_reached: int | None
    source_original_return_eax: int
    native_41fa50_executed: bool = False


def source_original_41fa50_player_club_link_predicate(
    *, original_player_record: bytes,
    original_global_8755d0_dword: int,
    original_reached_club_key_dword: int,
) -> SourceOriginal41FA50ClubKeyPredicate:
    """Native 41FA50 returns one iff player+10 is neither source key
    and player's signed WORD+72 exactly equals source club key.
    If player+10 equals global 8755D0 or club key, 41FA50 returns 0
    BEFORE reaching player+72 comparison. This source input alone
    does NOT mean 409C90 called 4181B0 on the player.
    """
    p=original_player_record
    for name,k in (("global 8755D0",original_global_8755d0_dword),
                   ("source club key",original_reached_club_key_dword)):
        if type(k) is not int or not 0<=k<=0xffffffff:
            raise Original409C90SourceError(f"actual original {name} DWORD required")
    if type(p) is not bytes or len(p)<0x74:
        raise Original409C90SourceError("original player signed WORD+10 and+72 required")
    a=unpack_from("<h",p,0x10)[0]
    if a==(original_global_8755d0_dword if original_global_8755d0_dword<0x80000000
           else original_global_8755d0_dword-0x100000000) or (
        a==(original_reached_club_key_dword if original_reached_club_key_dword<0x80000000
           else original_reached_club_key_dword-0x100000000)):
        return SourceOriginal41FA50ClubKeyPredicate(a,None,0)
    b=unpack_from("<h",p,0x72)[0]
    return SourceOriginal41FA50ClubKeyPredicate(a,b,int((b&0xffffffff)==original_reached_club_key_dword))


@dataclass(frozen=True)
class SourceOriginal4181B0ResetNo418220:
    original_player_native_pointer: int
    original_status_pointer: int
    original_player_before: bytes
    original_status_before: bytes
    source_player_after_literal_stores: bytes
    source_status_after_4ea370: bytes
    original_418220_called: bool = False
    original_native_4181b0_executed: bool = False
    live_game_state_modified: bool = False


def source_original_4181b0_reset_bit0_clear_branch(
    *, original_player_native_pointer: int,
    original_player_record_before: bytes,
    original_status_record_before: bytes,
) -> SourceOriginal4181B0ResetNo418220:
    """Native original 4181B0→418150/160/180/170→4EA370 complete
    known literal stores only when player+174 bit0 is CLEAR.

    418180 conditionally calls 418220 if bit0 SET; that branch mutates
    further player/status world and is NOT source-closed here.
    Original 4EA370 sets status+3 low five bits from status+0 and
    clears status+4 low four bits, preserving upper status bits.
    """
    player=original_player_record_before
    status=original_status_record_before
    ptr=original_player_native_pointer
    if type(ptr) is not int or not 0<ptr<=0xffffffff:
        raise Original409C90SourceError("original native player pointer required")
    if type(player) is not bytes or len(player)<0x24c:
        raise Original409C90SourceError("original player through +248 status owner required")
    if type(status) is not bytes or len(status)<5:
        raise Original409C90SourceError("actual status bytes through+4 required")
    status_ptr=unpack_from("<I",player,0x248)[0]
    if not status_ptr:
        raise Original409C90SourceError("native player+248 status pointer missing")
    flag174=unpack_from("<I",player,0x174)[0]
    if flag174&1:
        raise Original409C90SourceError(
            "original 418180 calls unresolved 418220 when player+174 bit0 true")
    out=bytearray(player)
    flag14=unpack_from("<I",player,0x14)[0]
    pack_into("<I",out,0x14,flag14 & ~0x30)
    pack_into("<I",out,0x174,flag174 & ~2)
    st=bytearray(status)
    st[3]=(st[3]&0xe0)|(st[0]&0x1f)
    st[4]=st[4]&0xf0
    return SourceOriginal4181B0ResetNo418220(
        ptr,status_ptr,player,status,bytes(out),bytes(st))


@dataclass(frozen=True)
class SourceOriginal409C90PreSelectionPlayerReset:
    original_41fa50_source_decision: SourceOriginal41FA50ClubKeyPredicate
    original_4181b0_reset_if_reached: SourceOriginal4181B0FullReset | None
    native_original_409c90_executed: bool = False
    original_mutable_roster_world_completed: bool = False
    live_game_state_modified: bool = False


def source_original_409c90_reached_41fa50_then_optional_4181b0(
    *, original_native_player_pointer: int,
    original_player_record_before_41fa50: bytes,
    original_global_8755d0_dword: int,
    original_team_club_key_dword: int,
    original_reached_status_record_for_4181b0_if_called: bytes | None,
) -> SourceOriginal409C90PreSelectionPlayerReset:
    """Original 40A18C 41FA50 then 40A1A8 4181B0 iff EAX==0.

    4181B0 full player/status reset, including its conditional native
    418220 saved role/position exchange, is source-qualified by the
    independently verified 4EA3C0/D0/330/350 leaf calls.
    When 41FA50 returns1, NO 4181B0 nor status record read is reached.
    This is a source-typed plan; original roster status is NOT committed.
    """
    result=source_original_41fa50_player_club_link_predicate(
        original_player_record=original_player_record_before_41fa50,
        original_global_8755d0_dword=original_global_8755d0_dword,
        original_reached_club_key_dword=original_team_club_key_dword,
    )
    if result.source_original_return_eax:
        if original_reached_status_record_for_4181b0_if_called is not None:
            raise Original409C90SourceError(
                "original 41FA50 true skips 4181B0; unvisited status supplied")
        return SourceOriginal409C90PreSelectionPlayerReset(result,None)
    if original_reached_status_record_for_4181b0_if_called is None:
        raise Original409C90SourceError("original 4181B0 reached status record mandatory")
    reset=source_original_4181b0_full_player_reset(
        original_player_native_pointer=original_native_player_pointer,
        original_player_record_before=original_player_record_before_41fa50,
        original_status_record_before=original_reached_status_record_for_4181b0_if_called)
    return SourceOriginal409C90PreSelectionPlayerReset(result,reset)


@dataclass(frozen=True)
class SourceOriginal418220Exchange:
    original_player_native_pointer: int
    original_source_status_pointer: int
    source_player_before: bytes
    source_status_before: bytes
    original_status_role_low5_before: int
    original_status_position_low4_before: int
    original_player_saved_role_byte_before: int
    original_player_saved_position_byte_before: int
    source_player_after_418220: bytes
    source_status_after_418220: bytes
    native_418220_executed: bool = False
    original_world_committed: bool = False


def source_original_418220_exact_role_position_exchange(
    *, original_native_player_pointer: int,
    original_player_record_before_418220: bytes,
    original_status_record_before_418220: bytes,
) -> SourceOriginal418220Exchange:
    """Native 418220 calls 4EA3C0/D0 getters then 4EA330/350 setters.

    It swaps old status[3] low5 and status[4] low4 with existing
    FULL saved player bytes+152/+153 (not with their masked values),
    writes new low status bits preserving status upper bits, and writes
    prior masked status values into the player saved bytes. This is an
    independent literal source projection; no original pointer is read.
    """
    p=original_native_player_pointer
    player=original_player_record_before_418220
    status=original_status_record_before_418220
    if type(p) is not int or not 0<p<=0xffffffff:
        raise Original409C90SourceError("actual 418220 player native pointer required")
    if type(player) is not bytes or len(player)<0x24c or type(status) is not bytes or len(status)<5:
        raise Original409C90SourceError("actual original 418220 player+248 and status+4 bytes required")
    status_ptr=unpack_from("<I",player,0x248)[0]
    if status_ptr==0:
        raise Original409C90SourceError("actual original player+248 status pointer required")
    old_role=status[3]&0x1f
    old_position=status[4]&0x0f
    saved_role=player[0x152]
    saved_position=player[0x153]
    out_player=bytearray(player)
    out_status=bytearray(status)
    out_status[3]=(status[3]&0xe0)|(saved_role&0x1f)
    out_status[4]=(status[4]&0xf0)|(saved_position&0x0f)
    out_player[0x152]=old_role
    out_player[0x153]=old_position
    return SourceOriginal418220Exchange(
        p,status_ptr,player,status,old_role,old_position,
        saved_role,saved_position,bytes(out_player),bytes(out_status))


@dataclass(frozen=True)
class SourceOriginal4181B0FullReset:
    original_player_native_pointer: int
    original_418220_was_reached: bool
    original_418220_source_exchange_if_reached: SourceOriginal418220Exchange | None
    original_player_before_reset: bytes
    original_status_before_reset: bytes
    source_player_after_reset: bytes
    source_status_after_reset: bytes
    native_original_4181b0_executed: bool = False
    live_game_state_modified: bool = False


def source_original_4181b0_full_player_reset(
    *, original_native_player_pointer: int,
    original_player_record_before: bytes,
    original_status_record_before: bytes,
) -> SourceOriginal4181B0FullReset:
    """Source-exact native 4181B0→150→160→180→170→4EA370.

    418180 invokes 418220 only if original player+174 bit0 is set,
    then clears bit0. 418170 always clears player+174 bit1.
    This emits exact separately owned player/status source snapshots;
    original callbacks are NOT executed and live state is NOT mutated.
    """
    p=original_player_record_before
    s=original_status_record_before
    if type(p) is not bytes or len(p)<0x24c or type(s) is not bytes or len(s)<5:
        raise Original409C90SourceError("actual original 4181B0 player and status records mandatory")
    if type(original_native_player_pointer) is not int or not 0<original_native_player_pointer<=0xffffffff:
        raise Original409C90SourceError("original player native pointer required")
    if unpack_from("<I",p,0x248)[0]==0:
        raise Original409C90SourceError("source original player status pointer missing")
    flags14=unpack_from("<I",p,0x14)[0]
    bits174=unpack_from("<I",p,0x174)[0]
    source_player=bytearray(p)
    pack_into("<I",source_player,0x14,flags14 & ~0x30)
    exchange=None
    source_status=s
    if bits174&1:
        exchange=source_original_418220_exact_role_position_exchange(
            original_native_player_pointer=original_native_player_pointer,
            original_player_record_before_418220=bytes(source_player),
            original_status_record_before_418220=s)
        source_player=bytearray(exchange.source_player_after_418220)
        source_status=exchange.source_status_after_418220
    # 418180 clears +174 bit0 iff the exchange was reached; 418170
    # clears bit1 unconditionally, preserving higher bits.
    pack_into("<I",source_player,0x174,bits174 & ~0x3)
    # 4EA370 reads the mutated status after 418220 if reached.
    status=bytearray(source_status)
    status[3]=(status[3]&0xe0)|(status[0]&0x1f)
    status[4]=status[4]&0xf0
    return SourceOriginal4181B0FullReset(
        original_native_player_pointer,bool(bits174&1),exchange,p,s,
        bytes(source_player),bytes(status))
