"""Bounded original native 0x4085D0 world branch before player mutations.

Source: canonical private footballmanager.exe, SHA-256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This faithfully classifies original source read-only exits and explicitly
halts before 0x4182F0/0x4EA350 can mutate native players/club objects.
No native callbacks, RNG, GameState writes or events are executed.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from


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
