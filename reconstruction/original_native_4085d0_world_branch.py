"""Bounded original native 0x4085D0 world branch before player mutations.

Source: canonical private footballmanager.exe, SHA-256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This faithfully classifies original source read-only exits and explicitly
halts before 0x4182F0/0x4EA350 can mutate native players/club objects.
No native callbacks, RNG, GameState writes or events are executed.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into, unpack_from

from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt


class Original4085D0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original4085D0ReachedWorld:
    original_team_owner_pointer: int
    original_team_owner_record: bytes
    original_player_pointer: int
    original_player_at_entry: bytes
    original_407060_eax: int | None = None
    original_4ea3c0_source_object_pointer: int | None = None
    original_4ea3c0_source_object: bytes | None = None
    original_406be0_eax: int | None = None
    original_5f0d20_eax: int | None = None


@dataclass(frozen=True)
class Original4085D0ReadOnlyReceipt:
    original_player_pointer: int
    original_team_owner_pointer: int
    original_417ee0_return_eax: int
    original_407060_teammate_count: int | None
    original_4ea3c0_source_category: int | None
    original_406be0_teammate_count: int | None
    original_5f0d20_category_capacity_floor: int | None
    original_4085d0_return_if_no_mutation: int | None
    original_would_reach_mutating_4182f0_then_4ea350: bool
    source_read_only_branch_complete: bool
    native_callbacks_invoked: bool = False
    live_game_state_updated: bool = False


def _nonnull(v: int, name: str) -> int:
    if type(v) is not int or not 0<v<=0xffffffff:
        raise Original4085D0SourceError(f"actual original {name} nonnull pointer required")
    return v


def _count(v: int | None, name: str, *, minimum=0, maximum=40) -> int:
    if type(v) is not int or not minimum<=v<=maximum:
        raise Original4085D0SourceError(f"actual reached {name} source count required")
    return v


def source_original_4085d0_world_branch_from_reached(
    reached: Original4085D0ReachedWorld,
) -> Original4085D0ReadOnlyReceipt:
    """Follow source 4085D0..408659 up to (but not through) writes.

    417EE0: signed WORD player+10 equals team+4 and player+14 bit4 set,
    returning 1 before 407060. Otherwise 407060 counts source roster
    eligible teammates for bit4; >=11 returns 0. With count <11,
    4EA3C0 reads (player+248 object)+3 low5, 406BE0 counts other source
    players in this category and 5F0D20 reads global category capacity+1.
    Comparison eligible_count < capacity reaches mutating 4182F0 and 4EA350.
    This model refuses to invent those native mutations.
    """
    if not isinstance(reached,Original4085D0ReachedWorld):
        raise Original4085D0SourceError("source reached world object required")
    team_ptr=_nonnull(reached.original_team_owner_pointer,"team owner")
    player_ptr=_nonnull(reached.original_player_pointer,"player")
    team=reached.original_team_owner_record
    player=reached.original_player_at_entry
    if type(team) is not bytes or len(team)<8:
        raise Original4085D0SourceError("original team owner bytes through+4 required")
    if type(player) is not bytes or len(player)<0x18:
        raise Original4085D0SourceError("original player bytes through+14 required")
    idx=unpack_from("<h",player,0x10)[0]
    current_team_owner_key=unpack_from("<i",team,4)[0]
    status_flags=unpack_from("<I",player,0x14)[0]
    early=int(idx==current_team_owner_key and bool(status_flags&0x10))
    callbacks=(
        reached.original_407060_eax,
        reached.original_4ea3c0_source_object_pointer,
        reached.original_4ea3c0_source_object,
        reached.original_406be0_eax,
        reached.original_5f0d20_eax,
    )
    if early:
        if any(x is not None for x in callbacks):
            raise Original4085D0SourceError("native 417EE0 early exit skips all downstream reads")
        return Original4085D0ReadOnlyReceipt(
            player_ptr,team_ptr,1,None,None,None,None,1,False,True)
    teammates=_count(reached.original_407060_eax,"407060 teammate")
    if teammates>=11:
        if any(x is not None for x in callbacks[1:]):
            raise Original4085D0SourceError("407060 >=11 skips category/capacity callbacks")
        return Original4085D0ReadOnlyReceipt(
            player_ptr,team_ptr,0,teammates,None,None,None,0,False,True)
    if type(player) is not bytes or len(player)<0x24c:
        raise Original4085D0SourceError("original player+248 source-category pointer required")
    source_ptr=unpack_from("<I",player,0x248)[0]
    if not source_ptr or _nonnull(reached.original_4ea3c0_source_object_pointer,
                                  "reached 4EA3C0 object")!=source_ptr:
        raise Original4085D0SourceError("player+248 original 4EA3C0 object pointer mismatch")
    obj=reached.original_4ea3c0_source_object
    if type(obj) is not bytes or len(obj)<4:
        raise Original4085D0SourceError("actual source category bytes through+3 required")
    category=obj[3]&0x1f
    peer_count=_count(reached.original_406be0_eax,"406BE0 peer")
    floor=_count(reached.original_5f0d20_eax,"5F0D20 category capacity",minimum=1,maximum=0xffffffff)
    would_mutate=peer_count<floor
    return Original4085D0ReadOnlyReceipt(
        player_ptr,team_ptr,0,teammates,category,peer_count,floor,
        None if would_mutate else 0,would_mutate,not would_mutate)



@dataclass(frozen=True)
class Original4085D0PlayerCategoryWriteProjection:
    original_player_id: int
    original_player_at_exit: bytes
    original_category_object_after_4ea350: bytes
    original_406be0_written_category_count: int
    original_native_4182f0_role_swap_executed: bool = False
    original_native_41edf0_club_balance_executed: bool = False
    native_4085d0_executed: bool = False
    live_game_state_updated: bool = False


def source_original_4085d0_qualified_mutating_leaf(
    reached: Original4085D0ReachedWorld,
    original_registered_417340: Original417340RegisteredUserReceipt,
) -> Original4085D0PlayerCategoryWriteProjection:
    """Reconstruct a truly bounded native 4085D0 successful writing route.

    Original 4182F0 unconditionally sets player+14 bit4; 418160 clears
    bit5. When +174 bit0 is clear, 418180 bypasses its 418220 role swap;
    418170 clears +174 bit1. Next 417340 registered-manager check uses
    precisely that post-mask player record. If registered-user matches,
    or player+14 bit13 is set, optional native 41EDF0 is skipped.
    Afterwards 4EA350 replaces the low nibble of category+4 with
    native 406BE0 peer count low nibble. This returns immutable source
    records only; it does NOT alter live player state or execute callbacks.
    """
    r=source_original_4085d0_world_branch_from_reached(reached)
    if not r.original_would_reach_mutating_4182f0_then_4ea350:
        raise Original4085D0SourceError("original 4085D0 did not reach mutating 4182F0")
    src=reached.original_player_at_entry
    if type(src) is not bytes or len(src)<0x178:
        raise Original4085D0SourceError("original player bytes through+174 for 4182F0 required")
    original_reserve=unpack_from("<I",src,0x174)[0]
    if original_reserve&1:
        raise Original4085D0SourceError("original 418180 reaches unqualified 418220 role-swap callback")
    staged=bytearray(src)
    flags=(unpack_from("<I",staged,0x14)[0]|0x10)&0xffffffdf
    pack_into("<I",staged,0x14,flags)
    pack_into("<I",staged,0x174,original_reserve&0xfffffffd)
    if (not isinstance(original_registered_417340,Original417340RegisteredUserReceipt)
            or original_registered_417340.native_callback_executed
            or original_registered_417340.live_game_state_updated
            or original_registered_417340.original_native_player_at_call != bytes(staged)):
        raise Original4085D0SourceError("original post-mutation 417340 player/predicate mismatch")
    if original_registered_417340.original_417340_return_al not in (0,1):
        raise Original4085D0SourceError("qualified native 417340 low AL 0/1 required")
    if original_registered_417340.original_417340_return_al==0 and not(flags&(1<<13)):
        raise Original4085D0SourceError("unqualified original 41EDF0 club-counter mutation reached")
    target=reached.original_4ea3c0_source_object
    if type(target) is not bytes or len(target)<5:
        raise Original4085D0SourceError("actual source category bytes through +4 required")
    after=bytearray(target)
    assert r.original_406be0_teammate_count is not None
    after[4]=(after[4]&0xf0)|(r.original_406be0_teammate_count&0x0f)
    return Original4085D0PlayerCategoryWriteProjection(
        original_player_id=unpack_from("<H",staged,4)[0],
        original_player_at_exit=bytes(staged),
        original_category_object_after_4ea350=bytes(after),
        original_406be0_written_category_count=r.original_406be0_teammate_count,
    )
