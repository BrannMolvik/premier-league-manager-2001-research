"""Original source 0x5127A0 per-side row -> 0x4197C0 and 0x41A490.

Private canonical footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Bounded read-only source projections, not a source-complete native 4197C0
callback or a live GameState change. Every input is actually reached original
processing-owner/player memory; no native getters or random draws are executed.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from


class OriginalRowIncidentSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original5127A0RowCall:
    pass_index: int
    row_index: int
    source_current_team_pointer: int
    source_opponent_team_pointer: int
    source_player_pointer: int
    source_4197c0_arg1: int
    source_4197c0_arg2: int
    source_4197c0_arg3: int
    source_41a5b0_called_after_row: bool
    original_4197c0_world_callback_executed: bool = False


@dataclass(frozen=True)
class Original41A490AccumulatorReceipt:
    source_row: Original5127A0RowCall
    original_player_144_at_entry: int
    source_increment_capped: int
    original_player_144_at_417340_or_return: int
    projected_player_record_at_417340_or_return: bytes
    native_417340_callback_outstanding: bool
    live_game_state_updated: bool = False


def source_original_5127a0_row_from_reached(
    *, original_processing_owner_record: bytes,
    original_pass_index: int, original_row_index: int,
) -> Original5127A0RowCall:
    """Extract reached native row exactly from 0x5127AF..0x5128CD.

    First owner EBX=0 has active row count +5A4, row vector +4,
    per-row bytes +4C, current pointer +0, opponent +5B0.
    Second owner EBX=1 has row count +B54, vector +5B4,
    per-row bytes +5FC, current pointer +5B0, opponent +0.
    The emitted 4197C0 stack args are row+48, row+49, opponent, match.
    The latter match pointer is implicit in the enclosing native call.
    """
    owner = original_processing_owner_record
    if type(original_pass_index) is not int or original_pass_index not in (0, 1):
        raise OriginalRowIncidentSourceError("original EBX pass must be 0 or 1")
    if type(original_row_index) is not int or original_row_index < 0:
        raise OriginalRowIncidentSourceError("original source row index required")
    if type(owner) is not bytes or len(owner) < 0xb58:
        raise OriginalRowIncidentSourceError("actual source processing owner bytes through +B54 required")
    count_offset = 0x5a4 if original_pass_index == 0 else 0xb54
    count = unpack_from("<i",owner,count_offset)[0]
    if not 0 <= count <= 18 or not original_row_index < count:
        raise OriginalRowIncidentSourceError("original row index outside source 18-row side")
    first_team = unpack_from("<I",owner,0)[0]
    second_team = unpack_from("<I",owner,0x5b0)[0]
    if not first_team or not second_team:
        raise OriginalRowIncidentSourceError("original two actual team-owner pointers required")
    vector_base = 0x4 if original_pass_index == 0 else 0x5b4
    row_base = 0x4c if original_pass_index == 0 else 0x5fc
    playerptr = unpack_from("<I",owner,vector_base+4*original_row_index)[0]
    if not playerptr:
        raise OriginalRowIncidentSourceError("original native row player pointer must be nonzero")
    b= row_base + 0x48 + 0x4c*original_row_index
    # row+48, +49, +4A are unsigned bytes. 5128B2..5128B8
    # pushes match, opponent, arg2, arg1 in precisely this order.
    arg1,arg2,flag=owner[b],owner[b+1],owner[b+2]
    return Original5127A0RowCall(
        pass_index=original_pass_index, row_index=original_row_index,
        source_current_team_pointer=first_team if original_pass_index == 0 else second_team,
        source_opponent_team_pointer=second_team if original_pass_index == 0 else first_team,
        source_player_pointer=playerptr,
        source_4197c0_arg1=arg1, source_4197c0_arg2=arg2,
        source_4197c0_arg3=second_team if original_pass_index == 0 else first_team,
        source_41a5b0_called_after_row=bool(flag),
    )


def source_original_41a490_accumulator_at_callback_boundary(
    *, original_reached_row: Original5127A0RowCall,
    original_player_at_41a490: bytes,
    original_41a490_reached: bool,
) -> Original41A490AccumulatorReceipt:
    """Source leaf 0x41A490..0x41A4BE, BEFORE optional native 417340.

    Only callable when 0x4197C0 non-UEFA branch actually saw competition
    v+0x30 EAX nonzero. Previous 0x4085D0, v18, 417EE0 and source
    world callbacks may have mutated the player; require actual snapshot at
    this entry, never reuse an earlier row/player snapshot as if unchanged.
    Args are unsigned source row bytes; native LEA arg1+2*arg2 is capped
    to 2 (signed CMP/JLE). New player byte +0x144 wraps modulo 256.
    Native calls 0x417340 only if the RESULT byte >1 unsigned.
    """
    if original_41a490_reached is not True:
        raise OriginalRowIncidentSourceError("actual original 41A490 reached callback required")
    row=original_reached_row
    if not isinstance(row,Original5127A0RowCall):
        raise OriginalRowIncidentSourceError("typed original 5127A0 row call required")
    raw=original_player_at_41a490
    if type(raw) is not bytes or len(raw)<0x145:
        raise OriginalRowIncidentSourceError("actual player bytes through +144 at 41A490 required")
    for name, value in (
        ("row arg1", row.source_4197c0_arg1),
        ("row arg2", row.source_4197c0_arg2),
    ):
        if type(value) is not int or not 0 <= value <= 255:
            raise OriginalRowIncidentSourceError(
                f"actual original unsigned {name} byte required")
    if (type(row.source_player_pointer) is not int or
            not 0 < row.source_player_pointer <= 0xffffffff or
            row.source_4197c0_arg3 != row.source_opponent_team_pointer):
        raise OriginalRowIncidentSourceError(
            "reached original row player/opponent pointer identity required")
    old=raw[0x144]
    increment=min(2, row.source_4197c0_arg1+2*row.source_4197c0_arg2)
    new=(old+increment)&0xff
    projected=bytearray(raw)
    projected[0x144]=new
    return Original41A490AccumulatorReceipt(
        source_row=row,original_player_144_at_entry=old,
        source_increment_capped=increment,
        original_player_144_at_417340_or_return=new,
        projected_player_record_at_417340_or_return=bytes(projected),
        native_417340_callback_outstanding=new>1,
    )
