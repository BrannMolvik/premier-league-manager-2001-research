"""Original reached 5DB6FA context then conditional 5DB7D0 first-side tail.

A source-only joined projection. It does not resolve original EBX/ECX
producers, execute original callbacks/native 617D70 queues, calculate a
playable match, or update GameState.
"""
from dataclasses import dataclass
from original_native_5db6fa_context_tail import (
    SourceOriginalContextTailReceipt,
    source_original_5db6fa_two_component_context_tail,
)
from original_match_first_side_joined_world import (
    SourceOriginalFirstSideJoinedWorldReceipt,
    source_original_5da2f0_first_side_joined_world,
)

@dataclass(frozen=True)
class SourceOriginalMatchContextAndSideReceipt:
    source_native_context: SourceOriginalContextTailReceipt
    source_first_side: SourceOriginalFirstSideJoinedWorldReceipt
    original_native_match_executed: bool = False
    original_world_state_committed: bool = False

def source_original_5db6fa_context_then_first_side(
    *, original_processing_object_pointer_at_entry: int,
    original_reached_processing_pointer_at_5db70c: int,
    original_processing_context_before_5db6fa: bytes,
    original_ebx_component_at_5db6fc: int,
    original_ecx_component_at_5db704: int,
    original_source_owner_call: dict,
    original_first_side_pointer_at_5db7d0: int,
    original_first_side_before_5db7d0: bytes,
    original_5da5f4_final_virtual18_nonzero: bool,
    original_stack_cap_div10_input_if_reached: int | None,
) -> SourceOriginalMatchContextAndSideReceipt:
    context=source_original_5db6fa_two_component_context_tail(
        original_processing_object_pointer_at_entry=original_processing_object_pointer_at_entry,
        original_reached_processing_pointer_at_5db70c=original_reached_processing_pointer_at_5db70c,
        original_context_before_5db6fa=original_processing_context_before_5db6fa,
        original_ebx_component_at_5db6fc=original_ebx_component_at_5db6fc,
        original_ecx_component_at_5db704=original_ecx_component_at_5db704,
    )
    side=source_original_5da2f0_first_side_joined_world(
        original_source_owner_call=original_source_owner_call,
        original_first_side_pointer_at_5db7d0=original_first_side_pointer_at_5db7d0,
        original_first_side_before_5db7d0=original_first_side_before_5db7d0,
        original_processing_context_at_5db7d0=context.native_context_after_reached_stores,
        original_5da5f4_final_virtual18_nonzero=original_5da5f4_final_virtual18_nonzero,
        original_stack_cap_div10_input_if_reached=original_stack_cap_div10_input_if_reached,
    )
    return SourceOriginalMatchContextAndSideReceipt(context,side)
