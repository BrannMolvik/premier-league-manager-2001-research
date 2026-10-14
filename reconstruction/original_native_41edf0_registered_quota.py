"""Original 0x41EDF0 registered-club quota after 4182F0 status clearing.

Private original executable footballmanager.exe SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Source-exact immutable projection, NOT native execution, original save
compatibility, or live GameState mutation. Distinguish registered
player+0x72 from current team player+0x10.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into,unpack_from


class Original41EDF0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original41EDF0Reached:
    original_player_at_call: bytes
    original_874b90_club_array_base: int | None = None
    original_874b94_default_club_pointer: int | None = None
    original_registered_club_pointer: int | None = None
    original_registered_club_record: bytes | None = None


@dataclass(frozen=True)
class Original41EDF0QuotaReceipt:
    original_player_id: int
    original_source_registered_club_index_signed: int | None
    original_source_registered_club_pointer: int | None
    original_player_after_41edf0: bytes
    original_registered_club_after_41edf0: bytes | None
    original_registered_club_counter_before: int | None
    original_registered_club_counter_after: int | None
    original_status_bit12_cleared: bool
    original_registered_club_counter_decremented: bool
    native_callback_executed: bool = False
    live_game_state_updated: bool = False


def _ptr(value: int | None, name: str) -> int:
    if type(value) is not int or not 0<value<=0xffffffff:
        raise Original41EDF0SourceError(f"original {name} nonnull uint32 required")
    return value


def source_original_41edf0_registered_quota_from_reached(
    original: Original41EDF0Reached,
) -> Original41EDF0QuotaReceipt:
    """Static 41EDF0..41EE5F exactly, including negative signed owners.

    Source player+14 bit12 zero returns immediately without touching
    +72 club/global owners. Otherwise bit12 is cleared in player+14,
    then original reads BOTH globals 874B90/874B94, selecting default
    874B94 if signed player+72<0 or indexed 874B90+680*index.
    Native signed registered club DWORD+1A8>0 is decremented by ONE.
    Zero or negative quota is preserved after player status clears.
    """
    if not isinstance(original,Original41EDF0Reached):
        raise Original41EDF0SourceError("typed actually reached original 41EDF0 context required")
    p=original.original_player_at_call
    if type(p) is not bytes or len(p)<0x18:
        raise Original41EDF0SourceError("actual original source player bytes through+14 required")
    flags=unpack_from("<I",p,0x14)[0]
    if not(flags & (1<<12)):
        if any(v is not None for v in (
            original.original_874b90_club_array_base,
            original.original_874b94_default_club_pointer,
            original.original_registered_club_pointer,
            original.original_registered_club_record,
        )):
            raise Original41EDF0SourceError("native status-bit12 zero skips registered-club source reads")
        return Original41EDF0QuotaReceipt(
            unpack_from("<H",p,4)[0],None,None,p,None,None,None,False,False)
    if len(p)<0x74:
        raise Original41EDF0SourceError("original status-positive player bytes through registered +72 required")
    base=_ptr(original.original_874b90_club_array_base,"874B90 indexed-club base")
    fallback=_ptr(original.original_874b94_default_club_pointer,"874B94 default-club")
    index=unpack_from("<h",p,0x72)[0]
    selected=fallback if index<0 else base+index*680
    if not 0<selected<=0xffffffff:
        raise Original41EDF0SourceError("source indexed registered club pointer overflow/zero")
    if _ptr(original.original_registered_club_pointer,"reached registered club")!=selected:
        raise Original41EDF0SourceError("original registered player+72 club pointer identity mismatch")
    club=original.original_registered_club_record
    if type(club) is not bytes or len(club)<0x1ac:
        raise Original41EDF0SourceError("native registered club bytes through+1A8 required")
    old=unpack_from("<i",club,0x1a8)[0]
    new=old-1 if old>0 else old
    after_club=bytearray(club)
    pack_into("<i",after_club,0x1a8,new)
    after_p=bytearray(p)
    pack_into("<I",after_p,0x14,flags&~(1<<12))
    return Original41EDF0QuotaReceipt(
        unpack_from("<H",p,4)[0],index,selected,bytes(after_p),
        bytes(after_club),old,new,True,old>0)
