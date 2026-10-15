"""Source-only original 5DB37C no-human, flag0 branch to 5DB6FA context.
Original 4037B0 false, byte [ESP+0xF] zero -> 5DB4CF -> 5DB6FA.
All QWORDs, guards, native context and owners are independent source inputs.
Does not execute original, human 5DC510, or GameState.
"""
from dataclasses import dataclass
from original_match_four_stage_integer_totals import (
    SourceOriginalFourStageIntegerTotal,
    source_original_5db37c_four_stage_integer_totals,
)
from original_native_5db6fa_context_tail import (
    SourceOriginalContextTailReceipt,
    source_original_5db6fa_two_component_context_tail,
)

class OriginalNonhumanStageContextJoinError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginalNonhumanStageContextJoin:
    source_four_stage_pairs: SourceOriginalFourStageIntegerTotal
    source_context_tail: SourceOriginalContextTailReceipt
    original_4037b0_no_human_gate: bool
    original_stack_flag_at_5db3b9: int
    direct_branch_5db3bd_to_5db4cf_to_5db6fa: bool=True
    original_native_match_executed: bool=False
    live_game_state_updated: bool=False

def source_original_5db37c_nonhuman_direct_context(
    *, original_stage_stack_at_5db37c: bytes,
    original_entered_stage_guards: tuple[bool,bool,bool,bool],
    original_4037b0_human_gate_at_5db3b2: bool,
    original_stack_flag_at_5db3b9: int,
    original_processing_object_pointer_at_entry: int,
    original_reached_processing_pointer_at_5db70c: int,
    original_context_before_5db6fa: bytes,
)->SourceOriginalNonhumanStageContextJoin:
    if type(original_4037b0_human_gate_at_5db3b2) is not bool or original_4037b0_human_gate_at_5db3b2:
        raise OriginalNonhumanStageContextJoinError('original 4037B0 false branch required')
    if type(original_stack_flag_at_5db3b9) is not int or original_stack_flag_at_5db3b9!=0:
        raise OriginalNonhumanStageContextJoinError('original 5DB4CF byte-zero branch required')
    pair=source_original_5db37c_four_stage_integer_totals(
        original_stage_stack_at_5db37c=original_stage_stack_at_5db37c,
        original_entered_stage_guards=original_entered_stage_guards)
    first=pair.original_pre_human_ebx_first_and_third_u32
    second=pair.original_pre_human_edi_fourth_and_second_u32
    if not first or not second:
        raise OriginalNonhumanStageContextJoinError('original zero component x87 state unresolved')
    context=source_original_5db6fa_two_component_context_tail(
        original_processing_object_pointer_at_entry=original_processing_object_pointer_at_entry,
        original_reached_processing_pointer_at_5db70c=original_reached_processing_pointer_at_5db70c,
        original_context_before_5db6fa=original_context_before_5db6fa,
        original_ebx_component_at_5db6fc=first,
        original_ecx_component_at_5db704=second)
    return SourceOriginalNonhumanStageContextJoin(pair,context,False,0)
