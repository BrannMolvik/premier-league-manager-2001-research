"""Original LeagueMatch 513010 / 513252 calculator and v38/v3c phase order.

Preserves reached dispatch facts from authorized native PE 833bf95e,
without pretending to execute match calculator 5DA2F0, its 3D/FastView
wrappers, the original v+38 score store, v+3C world changes, or UI.
If v+34 fails, 512D80 is reached and source *still* branches to the
common v38/v3c callback tail. A satisfied native v+34 alone is NOT
permission to call original calculator. Other source checks intervene.
"""
from __future__ import annotations
from dataclasses import dataclass


class OriginalMatchSourcePipelineError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalMatch513010PhasePlan:
    native_match_v34_context_ready: bool
    native_516080_branch_al_nonzero: bool | None
    native_flags44_after_human_preparation: int | None
    native_calculator_5da2f0_called: bool
    native_presentation_wrapper_va: int | None
    original_v38_callback_reached: bool = True
    original_v3c_callback_reached: bool = True
    original_match_world_calculated: bool = False
    original_presentation_invoked: bool = False
    original_game_state_written: bool = False
    original_win11_gui_verified: bool = False


def source_original_513010_v34_and_postcalc_phase_plan(
    *,
    original_5130c2_v34_al_nonzero: bool,
    original_reached_516080_al_nonzero: bool | None,
    original_reached_match_flags44_after_preparation: int | None,
    original_reached_match_v28_eax: int | None,
    original_mode_877530: int | None,
) -> SourceOriginalMatch513010PhasePlan:
    """Only reached native facts: cannot invent v+34/match human branch.

    Under v+34 true and 516080 false, 5130F4 tests match+44 bit4
    (human match) and bit5 (completed). If human & not completed,
    original modal/prep callbacks may mutate flags before 513238.
    This projection therefore requires actual post-preparation +44
    and reached v+28 return for calculator qualification. For a
    non-human or completed route source 632B20 runs and joins 513238;
    its *post*-callback flags need distinct evidence and are NOT
    represented by this bounded source plan.
    """
    ready=original_5130c2_v34_al_nonzero
    if type(ready) is not bool:
        raise OriginalMatchSourcePipelineError("original reached 5130C2 v+34 AL bool required")
    other=(original_reached_516080_al_nonzero,
           original_reached_match_flags44_after_preparation,
           original_reached_match_v28_eax,
           original_mode_877530)
    if not ready:
        if any(v is not None for v in other):
            raise OriginalMatchSourcePipelineError(
                "original v+34 false bypasses 516080 and all match/mode branches")
        return SourceOriginalMatch513010PhasePlan(False,None,None,False,None)
    guard=original_reached_516080_al_nonzero
    if type(guard) is not bool:
        raise OriginalMatchSourcePipelineError("original reached 516080 AL required")
    if guard:
        if any(v is not None for v in other[1:]):
            raise OriginalMatchSourcePipelineError(
                "original 516080 true skips modal/match-calculator source branches")
        return SourceOriginalMatch513010PhasePlan(True,True,None,False,None)
    flags=original_reached_match_flags44_after_preparation
    mode=original_mode_877530
    v28=original_reached_match_v28_eax
    if type(flags) is not int or not 0<=flags<=0xffffffff:
        raise OriginalMatchSourcePipelineError("original post-preparation +44 flag DWORD required")
    if not flags & 0x10 or flags & 0x20:
        raise OriginalMatchSourcePipelineError(
            "nonhuman or completed +44 flag source path needs distinct 632B20 effects")
    if type(v28) is not int or not 0<=v28<=0xffffffff:
        raise OriginalMatchSourcePipelineError("reached original match virtual+28 EAX required")
    if type(mode) is not int or mode not in (0,1,2,3):
        raise OriginalMatchSourcePipelineError("exact original match detail mode0–3 required")
    # Original v28==6 bypasses calculator but preserves v38/v3c tail.
    # Otherwise original 513238 retests possibly changed match+44 bit5.
    # Caller must supply final post-prep flag, no guessed success from v28.
    should_calculate=v28!=6 and not flags&0x20
    wrapper={0:0x533d80,1:0x533d80,2:0x5331c0,3:None}[mode] if should_calculate else None
    return SourceOriginalMatch513010PhasePlan(
        True,False,flags,should_calculate,wrapper)
