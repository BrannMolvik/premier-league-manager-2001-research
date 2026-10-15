"""Original first/second match-score 668350 bound clamp -> 64D540 RNG.

5DABCA (first) / 5DAE45 (second) use original 668350
to truncate an already-computed native x87 value. Its EAX is NOT
computable from the known class coefficient alone. On the reached
original source path, native MOV EDI,EAX; CMP EDI,1; JGE; else EDI=1.
Original 5DABED / 5DAE68 then push EDI and CALL 64D540,
whose exact per-thread CRT-rand step is separately source-proven.

Only accept actual reached first 668350 return EAX and actual
66D553 TLS record before RNG. This joins the real bound; no guessed
5DA250 return, native FPU state, other 668350 call or RNG ordering.
"""
from dataclasses import dataclass

from original_match_64d540_tls_score_rng import (
    SourceOriginalMatch64D540NativeRand,
    source_original_64d540_bounded_tls_match_rng,
)


class OriginalScoreBoundSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalBoundedScoreSideRng:
    source_score_side: int
    original_first_668350_return_eax_signed: int
    original_positive_clamped_edi_bound: int
    original_first_truncate_call_va: int
    original_score_rng_source: SourceOriginalMatch64D540NativeRand
    native_original_first_fpu_truncate_executed: bool = False
    original_64d540_executed: bool = False
    saved_match_world_modified: bool = False


def source_original_5dabca_5dae45_score_rng_from_reached_bound(
    *,
    original_source_scored_side: int,
    original_first_668350_reached_eax_signed: int,
    original_66d553_tls_record_pointer: int,
    original_66d553_tls_record_before_66951c: bytes,
) -> SourceOriginalBoundedScoreSideRng:
    side=original_source_scored_side
    val=original_first_668350_reached_eax_signed
    if type(side) is not int or side not in (1,2):
        raise OriginalScoreBoundSourceError(
            "only native first 5DABCA or second 5DAE45 scoring side")
    if type(val) is not int or not -(1<<31)<=val<=(1<<31)-1:
        raise OriginalScoreBoundSourceError(
            "actual source 668350 native signed int32 EAX required")
    bound=max(1,val)
    rng=source_original_64d540_bounded_tls_match_rng(
        original_reached_score_call_site=0x5dabed if side==1 else 0x5dae68,
        original_66d553_tls_record_pointer=original_66d553_tls_record_pointer,
        original_66d553_tls_record_before_66951c=(
            original_66d553_tls_record_before_66951c),
        original_64d540_reached_positive_bound=bound,
    )
    return SourceOriginalBoundedScoreSideRng(side,val,bound,
        0x5dabca if side==1 else 0x5dae45,rng)
