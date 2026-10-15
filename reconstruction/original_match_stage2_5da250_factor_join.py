"""Source join: original 410FF0 class factor stored at both 5DA250 call sites.

5DAA53..5DAAC3 (first team) and 5DACD1..5DAD41 (opponent) write
QWORD factor into local original ESP+18. Original stage1 5DAAE5
and stage2 5DAD62 then issue native 5DA250 calls, having built
their separate argument QWORDs from original metrics and status.

Require a real original stage ESP snapshot, source actual 410FF0 team
and factor, and previously recovered 5DA250 argument owner. This is
a source ownership join, NOT an attempt to compute the x87 result,
native world RNG, or final match score. Native call's ECX is ESI
context on both stages, while stage2 coefficient was for opponent EBX.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_match_5daa47_stage_two_factor import SourceOriginalStageTwoFactor
from original_match_four_5da250_argument_source import (
    OriginalFourStage5DA250Arguments,
    source_original_four_stage_5da250_arguments,
)


class OriginalScoredFactorJoinError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalScoreStage5DA250FactorJoin:
    original_stage: int
    source_class_factor: SourceOriginalStageTwoFactor
    source_original_arguments: OriginalFourStage5DA250Arguments
    original_qword_factor_at_esp18: bytes
    native_5da250_argument_execution_proven: bool = False
    actual_original_5da250_executed: bool = False
    original_game_state_modified: bool = False


def source_original_5daa_or_5dad_scored_factor_to_5da250(
    *,
    original_scoring_stage: int,
    original_coefficient_team_pointer: int,
    original_class_factor: SourceOriginalStageTwoFactor,
    original_stage_stack_before_argument_pushes: bytes,
    original_4037b0_human_gate: bool,
    original_selected_user_694_record_if_human: bytes | None,
    original_5e48d0_stored_qword_if_directly_copied_to_b: bytes | None,
) -> SourceOriginalScoreStage5DA250FactorJoin:
    stage=original_scoring_stage
    factor=original_class_factor
    s=original_stage_stack_before_argument_pushes
    if (type(stage) is not int or stage not in (1,2) or
            type(factor) is not SourceOriginalStageTwoFactor or
            factor.original_side!=stage or
            type(original_coefficient_team_pointer) is not int or
            not 0<original_coefficient_team_pointer<=0xffffffff or
            factor.original_team_pointer!=original_coefficient_team_pointer or
            type(s) is not bytes or len(s)<0x40):
        raise OriginalScoredFactorJoinError(
            "actual first ESI / second EBX source team and reached score-stage stack required")
    original_stack_factor=s[0x18:0x20]
    if original_stack_factor!=factor.original_qword_factor:
        raise OriginalScoredFactorJoinError(
            "native original class 410FF0 factor differs from pre-5DA250 stack QWORD")
    try:
        args=source_original_four_stage_5da250_arguments(
            source_stage=stage,
            original_stage_stack_before_argument_pushes=s,
            original_4037b0_human_gate=original_4037b0_human_gate,
            original_selected_user_694_record_if_human=original_selected_user_694_record_if_human,
            original_5e48d0_stored_qword_if_directly_copied_to_b=(
                original_5e48d0_stored_qword_if_directly_copied_to_b),
        )
    except ValueError as exc:
        raise OriginalScoredFactorJoinError(str(exc)) from exc
    if args.source_5da250_call_site!=(0x5dab07 if stage==1 else 0x5dad84):
        raise OriginalScoredFactorJoinError("reached source 5DA250 call site drift")
    return SourceOriginalScoreStage5DA250FactorJoin(stage,factor,args,original_stack_factor)
