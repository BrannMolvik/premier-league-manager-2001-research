"""Original 5DAB97/5DAE12 x87 score bound -> native TLS 64D540 join.

Both scoring sides source:
 original stage ratio at ESP+10 compared to double 1.0,
 if ratio > 1: ST0 clamp / ((ratio-1)*1000+100),
 else: ST0 clamp * exact binary64 0.01,
 668350 truncates result to native signed integer EAX,
 EDI=max(1,EAX), then 64D540(EDI) reads actual 66D553 thread TLS.

The caller MUST supply the independently reached native 668350 EAX.
Native x87 internal 80-bit rounding is not simulated. A rational
binary64-input formula is a consistency check only when its result
is safely far from an integer truncation boundary. Do not guess
source FPU state, global seed, native score RNG chronology, match
state, or actual original callbacks.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from struct import unpack,unpack_from

from original_native_66d553_tls_initial_state import (
    SourceOriginal66D553TLSRecord,
)
from original_match_5dabca_score_rng_join import (
    SourceOriginalBoundedScoreSideRng,
    source_original_5dabca_5dae45_score_rng_from_reached_bound,
)


class OriginalScoringFpuBoundSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalScoringFpuBoundTlsJoin:
    original_scoring_side: int
    original_native_branch_va: int
    original_stage_ratio_qword: bytes
    original_fpu_clamped_score_qword: bytes
    original_float_formula_value: float
    original_native_668350_eax_signed: int
    original_source_float_truncation_consistency_verified: bool
    original_native_rng_projection: SourceOriginalBoundedScoreSideRng
    actual_original_x87_executed: bool = False
    actual_native_rng_consumed: bool = False
    live_game_state_updated: bool = False


def source_original_5dab97_fpu_bound_to_66d553_tls_rand(
    *, original_scoring_side: int,
    original_native_stage_ratio_qword_at_esp10: bytes,
    original_native_clamped_fpu_st0_qword_before_5dab97: bytes,
    original_independently_reached_668350_signed_eax: int,
    original_reached_66d553_thread_record: SourceOriginal66D553TLSRecord,
) -> SourceOriginalScoringFpuBoundTlsJoin:
    side=original_scoring_side
    if type(side) is not int or side not in (1,2):
        raise OriginalScoringFpuBoundSourceError("original first or second native scored stage required")
    stage=original_native_stage_ratio_qword_at_esp10
    clamped=original_native_clamped_fpu_st0_qword_before_5dab97
    if type(stage) is not bytes or len(stage)!=8 or type(clamped) is not bytes or len(clamped)!=8:
        raise OriginalScoringFpuBoundSourceError("independently reached double stage and native clamped ST0 QWORDs required")
    x=unpack('<d',stage)[0]
    y=unpack('<d',clamped)[0]
    if not isfinite(x) or not isfinite(y) or abs(x)>10**8 or abs(y)>10**8:
        raise OriginalScoringFpuBoundSourceError(
            "original 80-bit source operation not qualified for nonfinite/large input")
    eax=original_independently_reached_668350_signed_eax
    if type(eax) is not int or not -(1<<31)<=eax<1<<31:
        raise OriginalScoringFpuBoundSourceError("original first 668350 signed EAX observation required")
    # Rational arithmetic uses exact binary64 SOURCE input bits. The actual
    # native intermediate remains 80-bit FPU, which can round differently
    # close to integer boundaries: those cases are deliberately unqualified.
    if x>1:
        divisor=(Fraction.from_float(x)-1)*1000+100
        if divisor<=0:
            raise OriginalScoringFpuBoundSourceError("original positive x87 large-stage denominator required")
        result=Fraction.from_float(y)/divisor
        branch=0x5DABA8 if side==1 else 0x5DAE23
    else:
        original_001=Fraction.from_float(unpack('<d',bytes.fromhex('7b14ae47e17a843f'))[0])
        # Source original constant at 7BD600 is the binary64 0.01.
        result=Fraction.from_float(y)*original_001
        branch=0x5DABC2 if side==1 else 0x5DAE3D
    trunc_result=(abs(result.numerator)//result.denominator)*(-1 if result<0 else 1)
    near_integer=abs(result-trunc_result)<Fraction(1,10**9) or (
        abs(result-trunc_result-(-1 if result<0 else 1))<Fraction(1,10**9))
    if result==0:
        if eax!=0:
            raise OriginalScoringFpuBoundSourceError("exact zero original FPU result must truncate to EAX zero")
    elif near_integer:
        raise OriginalScoringFpuBoundSourceError(
            "original x87 80-bit rounding near integer threshold not proved; "
            "source calculator path remains fail closed")
    elif trunc_result!=eax:
        raise OriginalScoringFpuBoundSourceError(
            "observed first original 668350 result contradicts source x87 bound away from integer boundary")
    tls=original_reached_66d553_thread_record
    if (type(tls) is not SourceOriginal66D553TLSRecord or
        type(tls.original_tls_record_pointer) is not int or
        not 0<tls.original_tls_record_pointer<=0xffffffff or
        type(tls.source_record_before_first_reached_66951c) is not bytes or
        len(tls.source_record_before_first_reached_66951c)<0x18 or
        unpack_from('<I',tls.source_record_before_first_reached_66951c,0x14)[0]
          !=tls.original_seed_at_plus14):
        raise OriginalScoringFpuBoundSourceError("actual source-qualified 66D553 thread RNG receipt required")
    rng=source_original_5dabca_5dae45_score_rng_from_reached_bound(
        original_source_scored_side=side,
        original_first_668350_reached_eax_signed=eax,
        original_66d553_tls_record_pointer=tls.original_tls_record_pointer,
        original_66d553_tls_record_before_66951c=tls.source_record_before_first_reached_66951c)
    return SourceOriginalScoringFpuBoundTlsJoin(
        side,branch,stage,clamped,float(result),eax,not near_integer,rng)
