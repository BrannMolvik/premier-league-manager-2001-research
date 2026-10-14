"""Original 0x405080 team availability count for optional 0x41A5B0.

Native original static 0x405080..0x4050ED reads signed team+294 count,
ushort player IDs from +244, global 0x875640 pool at 592 bytes per player,
and each source player DWORD+14. It excludes a player if any status bits
0, 1, 6 or 8 are set. This immutable model does NOT call 0x405080,
0x417270 or 0x41A5B0, nor write any reconstructed GameState.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


class Original405080SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original405080ReachedPlayer:
    original_player_pointer: int
    original_player_record_at_count: bytes


@dataclass(frozen=True)
class Original405080AvailabilityReceipt:
    original_team_pointer: int
    original_875640_pool_base_if_reached: int | None
    original_roster_ids: tuple[int, ...]
    original_player_status_14_by_id: tuple[tuple[int,int], ...]
    original_405080_eligible_count: int
    original_405080_excluded_count: int
    original_native_callback_executed: bool = False
    live_game_state_updated: bool = False


def source_original_405080_available_roster_from_reached(
    *,
    original_team_pointer: int,
    original_team_record: bytes,
    original_875640_pool_base_if_reached: int | None,
    original_reached_roster_player_records: tuple[Original405080ReachedPlayer,...],
) -> Original405080AvailabilityReceipt:
    if type(original_team_pointer) is not int or not 0<original_team_pointer<=0xffffffff:
        raise Original405080SourceError("actual original 405080 team pointer required")
    team=original_team_record
    if type(team) is not bytes or len(team)<0x298:
        raise Original405080SourceError("original team bytes through +294 count required")
    count=unpack_from("<i",team,0x294)[0]
    if not 0<=count<=40:
        raise Original405080SourceError("source signed team roster count outside 0..40")
    if type(original_reached_roster_player_records) is not tuple or len(original_reached_roster_player_records)!=count:
        raise Original405080SourceError("actual original 405080 player records incomplete or extra")
    if count==0:
        if original_875640_pool_base_if_reached is not None:
            raise Original405080SourceError("zero-roster 405080 skips native pool base")
        return Original405080AvailabilityReceipt(original_team_pointer,None,(),(),0,0)
    base=original_875640_pool_base_if_reached
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original405080SourceError("actual reached global 875640 pool pointer required")
    roster=[]
    flags=[]
    seen=set()
    excluded=0
    for i,src in enumerate(original_reached_roster_player_records):
        pid=unpack_from("<H",team,0x244+2*i)[0]
        if pid in seen:
            raise Original405080SourceError("duplicate original native roster ID")
        seen.add(pid)
        if not isinstance(src,Original405080ReachedPlayer):
            raise Original405080SourceError("actual original per-player source record required")
        expected=base+592*pid
        if (expected>0xffffffff or type(src.original_player_pointer) is not int
            or src.original_player_pointer!=expected):
            raise Original405080SourceError("original pool base+592×ID pointer mismatch")
        raw=src.original_player_record_at_count
        if type(raw) is not bytes or len(raw)<0x18:
            raise Original405080SourceError("actual source DBRPlayer +14 status required")
        if unpack_from("<H",raw,4)[0]!=pid:
            raise Original405080SourceError("original source pool player+4 identity mismatch")
        status=unpack_from("<I",raw,0x14)[0]
        roster.append(pid)
        flags.append((pid,status))
        if status & ((1<<0)|(1<<1)|(1<<6)|(1<<8)):
            excluded+=1
    return Original405080AvailabilityReceipt(
        original_team_pointer=original_team_pointer,
        original_875640_pool_base_if_reached=base,
        original_roster_ids=tuple(roster),
        original_player_status_14_by_id=tuple(flags),
        original_405080_eligible_count=count-excluded,
        original_405080_excluded_count=excluded,
    )
