"""Source original 5DA785 two-team signed grid distance and 5DA883 weighting.

Original 5DA785 reads first team+20/+24 (ESI), opposite team+20 from
EDI and +24 from saved ESP+44 opposing-team pointer (the original
5DA30C result of match-context+28 getter). For each coordinate:
  signed IDIV 1000 -> remainder; signed magic 0x1B4E81B5 /2^38
  with sign compensation == trunc(remainder/600);
  signed magic 0x68DB8BAD /2^44 == trunc(value/10000);
  coord = trunc(value/10000) + trunc(remainder/600).
Then calculate sum of squared signed coordinate differences;
native x87 FILD signed DWORD, FSQRT and 668350 FISTP QWORD with
truncating rounding mode produce a nonnegative int distance.

The native fixed-width arithmetic could overflow; reject input pairs
whose intermediary signed differences or sum would wrap/raise x87
indefinite, rather than inventing behavior. This is a score INPUT
factor and not a football result, RNG or GameState mutation.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isqrt
from struct import unpack_from


class OriginalMatchGridDistanceSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal5DA785GridDistance:
    original_first_team_pointer: int
    original_opponent_team_pointer: int
    original_first_team_xy20_24_signed: tuple[int,int]
    original_opponent_team_xy20_24_signed: tuple[int,int]
    source_first_coordinate_cells: tuple[int,int]
    source_opponent_coordinate_cells: tuple[int,int]
    source_absolute_coordinate_differences: tuple[int,int]
    original_integer_squares_sum: int
    original_668350_truncated_fsqrtdistance: int
    original_5112f0_guard_called: bool
    original_native_math_executed: bool = False
    match_result_written: bool = False


@dataclass(frozen=True)
class SourceOriginal5DA889DistanceMultiplier:
    original_truncated_distance: int
    original_reached_5112f0_al_nonzero: bool | None
    source_first_fpu_multiplier: float
    source_second_fpu_multiplier: float
    original_5112f0_callback_executed: bool = False
    original_fpu_state_mutated: bool = False


def _signed_trunc(value:int, divisor:int)->int:
    return value//divisor if value>=0 else -((-value)//divisor)


def _cell(v:int)->int:
    """Signed x86 IDIV(1000), then original magic divisions by 600,10000."""
    remainder=v-_signed_trunc(v,1000)*1000
    return _signed_trunc(v,10000)+_signed_trunc(remainder,600)


def source_original_5da785_team_grid_distance(
    *,
    original_first_team_pointer:int,
    original_first_team_record:bytes,
    original_opponent_from_5da30a_pointer:int,
    original_opponent_reached_esp44_pointer_at_5da7fb:int,
    original_opponent_team_record:bytes,
)->SourceOriginal5DA785GridDistance:
    a=original_first_team_pointer
    b=original_opponent_from_5da30a_pointer
    c=original_opponent_reached_esp44_pointer_at_5da7fb
    if any(type(p) is not int or not 0<p<=0xffffffff for p in (a,b,c)) or b!=c or a==b:
        raise OriginalMatchGridDistanceSourceError(
            "distinct source teams and actual saved opposing ESP+44 pointer required")
    r0=original_first_team_record
    r1=original_opponent_team_record
    if type(r0) is not bytes or len(r0)<0x28 or type(r1) is not bytes or len(r1)<0x28:
        raise OriginalMatchGridDistanceSourceError("source team+20/+24 bytes required")
    first=tuple(unpack_from("<i",r0,offset)[0] for offset in (0x20,0x24))
    other=tuple(unpack_from("<i",r1,offset)[0] for offset in (0x20,0x24))
    x=tuple(_cell(t) for t in first)
    y=tuple(_cell(t) for t in other)
    diff=tuple(abs(i-j) for i,j in zip(x,y))
    if any(d>0x7fffffff for d in diff):
        raise OriginalMatchGridDistanceSourceError("native coordinate delta signed overflow")
    square=sum(d*d for d in diff)
    if square>0x7fffffff:
        raise OriginalMatchGridDistanceSourceError(
            "original signed fild/sqrt squared-sum overflows: source fail-closed")
    dist=isqrt(square)
    return SourceOriginal5DA785GridDistance(a,b,first,other,x,y,diff,square,dist,dist!=0)


def source_original_5da889_distance_multiplier(
    *,
    original_grid_distance:SourceOriginal5DA785GridDistance,
    original_5112f0_al_nonzero_if_reached:bool|None,
)->SourceOriginal5DA889DistanceMultiplier:
    r=original_grid_distance
    if type(r) is not SourceOriginal5DA785GridDistance:
        raise OriginalMatchGridDistanceSourceError("original grid-distance receipt required")
    if r.original_668350_truncated_fsqrtdistance==0:
        if original_5112f0_al_nonzero_if_reached is not None:
            raise OriginalMatchGridDistanceSourceError(
                "original 5DA887 zero bypasses callback 5112F0")
        factor=1.5
    elif type(original_5112f0_al_nonzero_if_reached) is not bool:
        raise OriginalMatchGridDistanceSourceError("native 5112F0 AL required for nonzero distance")
    elif original_5112f0_al_nonzero_if_reached:
        factor=1.5
    elif r.original_668350_truncated_fsqrtdistance==1:
        factor=1.2
    else:
        factor=1.0
    return SourceOriginal5DA889DistanceMultiplier(
        r.original_668350_truncated_fsqrtdistance,
        original_5112f0_al_nonzero_if_reached,factor,factor)
