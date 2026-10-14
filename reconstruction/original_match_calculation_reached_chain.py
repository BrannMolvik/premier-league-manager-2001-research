"""Original source 5DB389 FISTP input -> 5DB6FA context -> first-side tail.

Requires independently reached final native EBX/ECX and the source processing
and first-side owners; never use a guessed modern simulation score. All
callbacks/native queues, GUI and real GameState remain unexecuted.
"""
from dataclasses import dataclass
from original_native_5db389_component_inputs import (
    SourceOriginalMatchComponentInputReceipt,
    source_original_5db389_four_float_components,
)
from original_match_context_to_side_world import (
    SourceOriginalMatchContextAndSideReceipt,
    source_original_5db6fa_context_then_first_side,
)

class OriginalNativeReachedCalculationError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginalNativeReachedCalculationReceipt:
    original_source_four_float_components: SourceOriginalMatchComponentInputReceipt
    original_source_context_and_side_world: SourceOriginalMatchContextAndSideReceipt
    original_native_fpu_callbacks_executed: bool = False
    original_native_match_executed: bool = False
    live_game_state_committed: bool = False

def source_original_5db389_through_5db6fa_joined_source(
    *, original_four_float_source_input: dict,
    original_actual_final_ebx_at_5db6fc: int,
    original_actual_final_ecx_at_5db704: int,
    original_context_side_stage_input: dict,
) -> SourceOriginalNativeReachedCalculationReceipt:
    if type(original_four_float_source_input) is not dict or type(original_context_side_stage_input) is not dict:
        raise OriginalNativeReachedCalculationError('complete reached source input dictionaries required')
    floats=source_original_5db389_four_float_components(**original_four_float_source_input)
    ebx=original_actual_final_ebx_at_5db6fc
    ecx=original_actual_final_ecx_at_5db704
    if (type(ebx) is not int or type(ecx) is not int or
        not 0<=ebx<=0xffffffff or not 0<=ecx<=0xffffffff or
        ebx!=floats.original_ebx_at_5db6fa or
        ecx!=floats.original_ecx_at_5db704 or
        original_context_side_stage_input.get('original_ebx_component_at_5db6fc')!=ebx or
        original_context_side_stage_input.get('original_ecx_component_at_5db704')!=ecx):
        raise OriginalNativeReachedCalculationError(
            'native 668350 source and actual final 5DB6FA processing operands disagree')
    world=source_original_5db6fa_context_then_first_side(**original_context_side_stage_input)
    # Source CFG 5DB3B2 (4037B0 full-key human) and 5DB3C5
    # (original local +0F conditional skip) are the ONLY predecessors
    # of 5DB4BE -> 5DB4C4. A human +694 addend cannot be inferred
    # from a score, league participant, generic manager or other path.
    first_side=world.source_first_side.source_human_selector
    skipped=world.source_first_side.original_5da5f4_final_virtual18_nonzero
    source_reaches_addend=first_side.original_4037b0_full_key_human and not skipped
    staged_addend=floats.original_human_694_addend_at_5db4c4 is not None
    if staged_addend != source_reaches_addend:
        raise OriginalNativeReachedCalculationError(
            'original 5DB4C4 human +694 addend branch contradicts first-side and skip flags')
    if source_reaches_addend:
        # At 5DB4BE the original re-reads the SAME masked-first human
        # selected by 403850. The reached +694 owner must match source
        # registry identity, not a different user's mutable stat record.
        observed_pointer=original_four_float_source_input.get(
            'original_user_694_owner_pointer_if_reached')
        if (type(observed_pointer) is not int or
            observed_pointer != first_side.original_selected_user_694_pointer):
            raise OriginalNativeReachedCalculationError(
                'original 5DB4BE selected human +694 owner pointer mismatch')
    return SourceOriginalNativeReachedCalculationReceipt(floats,world)
