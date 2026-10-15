"""Original 513010 calculator and v38/v3c tail source control flow.

Original canonical owner 833bf95e..b7cc3 only statically inspected.
5130C2 false: 512D80 cleanup, jump direct to 513294 v38/v3c.
5130C2 true: 516080 controls preparation path, NOT calculator gate.
513238 *post preparation* reads match+44 bit5: when clear, 513252
calls 5DA2F0, then 513257 *post calculator* reads match+44 bit4.
Only that final bit4 permits selected 0/1/2/3 presentation wrappers;
mode3 has no wrapper. All paths enter original v38 then v3c tail.
No original calculations, mutable callbacks, modal, or GUI occur here.
"""
from __future__ import annotations
from dataclasses import dataclass


class OriginalMatchSourcePipelineError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalMatch513010PhasePlan:
    source_v34_ready: bool
    source_516080_early_preparation_branch: bool | None
    original_match_flags44_at_513238: int | None
    original_match_flags44_after_5da2f0_at_513257: int | None
    original_512d80_cleanup_called: bool
    original_calculator_5da2f0_called: bool
    original_selected_mode: int | None
    original_presentation_wrapper_va: int | None
    original_3d_wrapper_variant: int | None = None
    original_v38_callback_reached: bool = True
    original_v3c_callback_reached: bool = True
    original_calculation_executed: bool = False
    native_original_presentation_invoked: bool = False
    original_saved_game_state_written: bool = False
    original_win11_gui_verified: bool = False


def source_original_513010_calculator_presentation_and_tail(
    *,
    original_5130c2_v34_al_nonzero: bool,
    original_reached_516080_al_nonzero: bool | None,
    original_match_flags44_after_preparation_at_513238: int | None,
    original_match_flags44_after_calculator_at_513257: int | None,
    original_reached_mode_877530_at_51325d: int | None,
) -> SourceOriginalMatch513010PhasePlan:
    ready=original_5130c2_v34_al_nonzero
    if type(ready) is not bool:
        raise OriginalMatchSourcePipelineError("reached original v+34 AL must be actual bool")
    later=(original_reached_516080_al_nonzero,
           original_match_flags44_after_preparation_at_513238,
           original_match_flags44_after_calculator_at_513257,
           original_reached_mode_877530_at_51325d)
    if not ready:
        if any(x is not None for x in later):
            raise OriginalMatchSourcePipelineError(
                "v+34 false bypasses original 516080, 513238, calculator and mode")
        return SourceOriginalMatch513010PhasePlan(
            False,None,None,None,True,False,None,None)
    prep=original_reached_516080_al_nonzero
    if type(prep) is not bool:
        raise OriginalMatchSourcePipelineError("source 516080 AL required after v+34 ready")
    before=original_match_flags44_after_preparation_at_513238
    if type(before) is not int or not 0<=before<=0xffffffff:
        raise OriginalMatchSourcePipelineError("actual native +44 at 513238 after callbacks required")
    calculator=not bool(before&0x20)
    after=original_match_flags44_after_calculator_at_513257
    mode=original_reached_mode_877530_at_51325d
    if not calculator:
        if after is not None or mode is not None:
            raise OriginalMatchSourcePipelineError(
                "bit5 completed skips 5DA2F0 and postcalculator mode access")
        return SourceOriginalMatch513010PhasePlan(
            True,prep,before,None,prep,False,None,None)
    if type(after) is not int or not 0<=after<=0xffffffff:
        raise OriginalMatchSourcePipelineError(
            "native postcalculator 513257 +44 flags required after actual 5DA2F0")
    if not after&0x10:
        if mode is not None:
            raise OriginalMatchSourcePipelineError(
                "postcalculator not human: 51325D does not read selected mode")
        wrapper=None
        variant=None
    else:
        if type(mode) is not int or mode not in (0,1,2,3):
            raise OriginalMatchSourcePipelineError(
                "original source reached presentation requires valid mode0–3")
        wrapper={0:0x533d80,1:0x533d80,2:0x5331c0,3:None}[mode]
        variant={0:0,1:1,2:None,3:None}[mode]
    return SourceOriginalMatch513010PhasePlan(
        True,prep,before,after,prep,True,mode,wrapper,variant)
