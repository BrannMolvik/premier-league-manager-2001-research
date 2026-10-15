"""Read-only source join: original human scored-stage 5DA250 argument A.

Original FILD signed DWORD user+694+0xC (stages1/2) or +0x8
(stages3/4), then FSUB exact entered-stage 5E48D0 coefficient.
Only emits PC24/PC53/PC64-EXACT dyadic results. No native runtime,
unproven x87 rounding, match score, or GameState.
"""
from dataclasses import dataclass
from fractions import Fraction
from struct import pack, unpack, unpack_from
from original_match_40cbc0_5e48d0_b_join import OriginalScoredStageFreshCallbackSource

class OriginalScoredHumanAError(ValueError):
    pass

@dataclass(frozen=True)
class OriginalScoredHumanA:
    original_stage: int
    original_user_694_stat_offset: int
    original_reached_stat_signed_dword: int
    original_callback_b_qword: bytes
    original_5da250_a_qword: bytes
    original_fild_fsub_site: int
    all_x87_precision_modes_exact: bool=True
    original_native_executed: bool=False
    game_state_updated: bool=False

_FILD_SITES=(0x5DA9CB,0x5DAC6C,0x5DAEEA,0x5DB168)

def source_exact_original_human_5da250_a(
    *, original_stage_callback: OriginalScoredStageFreshCallbackSource,
    original_selected_user_694_record_if_human: bytes
) -> OriginalScoredHumanA:
    c=original_stage_callback
    if type(c) is not OriginalScoredStageFreshCallbackSource or not c.original_human_gate:
        raise OriginalScoredHumanAError('actually reached human original callback required')
    stage=c.original_stage
    if type(stage) is not int or stage not in (1,2,3,4):
        raise OriginalScoredHumanAError('original scored stage 1..4 required')
    offset=0xC if stage<=2 else 0x8
    u=original_selected_user_694_record_if_human
    if type(u) is not bytes or len(u)<offset+4:
        raise OriginalScoredHumanAError('native selected user+694 bytes required')
    stat=unpack_from('<i',u,offset)[0]
    coeff_qword=c.original_5e48d0_qword
    if type(coeff_qword) is not bytes or len(coeff_qword)!=8:
        raise OriginalScoredHumanAError('native stage QWORD required')
    # FILD integer is exact on x87; FSUB may be PC24 sensitive.
    exact=Fraction(stat)-Fraction.from_float(unpack('<d',coeff_qword)[0])
    n=abs(exact.numerator)
    while n and n%2==0:
        n//=2
    if n.bit_length()>24:
        raise OriginalScoredHumanAError('native x87 PC24 rounding unresolved for this stat')
    result=pack('<d',float(exact))
    if Fraction.from_float(unpack('<d',result)[0])!=exact:
        raise OriginalScoredHumanAError('computed A not bit-exact binary64')
    return OriginalScoredHumanA(stage,offset,stat,coeff_qword,result,_FILD_SITES[stage-1])

from original_native_5da250_fpu_branch_source import source_original_5da250_finite_prethreshold_path

@dataclass(frozen=True)
class OriginalHumanStage5DA250LiteralSource:
    original_stage: int
    original_prethreshold_path: str
    native_literal_st0_qword_if_source_proven: bytes|None
    native_computed_result_unresolved: bool
    native_original_executed: bool=False
    live_match_state_updated: bool=False

def source_original_human_5da250_literal_if_proven(
    *, original_exact_human_a: OriginalScoredHumanA
) -> OriginalHumanStage5DA250LiteralSource:
    """Exact original direct QWORD returns only; never fabricate ratio branch."""
    r=original_exact_human_a
    if type(r) is not OriginalScoredHumanA or not r.all_x87_precision_modes_exact:
        raise OriginalScoredHumanAError('PC-independent source-qualified original A required')
    path=source_original_5da250_finite_prethreshold_path(
        original_esp4_qword=r.original_5da250_a_qword,
        original_espc_qword=r.original_callback_b_qword)
    if path=='5da25f-direct-literal-0p1':
        native=pack('<d',0.1)
    elif path=='5da2d6-direct-literal-2p0':
        native=pack('<d',2.0)
    else:
        native=None
    return OriginalHumanStage5DA250LiteralSource(
        r.original_stage,path,native,native is None)
