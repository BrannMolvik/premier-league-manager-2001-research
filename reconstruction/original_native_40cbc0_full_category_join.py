"""Full source-bound category index before original 40CBC0 coefficient branch.

Original club -> 4056D0 query -> 4F3B10 linked object -> 4F8FF0
category group -> 410FF0 matched member -> 4FA520 category remap.

No original routines, coefficient writers, save/loads or GUI execute.
"""
from dataclasses import dataclass
from original_native_4fa510_group_source import (
    SourceOriginal4FA510GroupReceipt,source_original_4fa510_group_category,
)
from original_native_40cbc0_query_category_join import (
    SourceOriginal40CBC0ReachedQueryCategoryReceipt,
    source_original_40cbc0_reached_query_category,
)

class Original40CBC0FullCategoryError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal40CBC0FullCategoryReceipt:
    source_native_group: SourceOriginal4FA510GroupReceipt
    source_first_side_route_and_category: SourceOriginal40CBC0ReachedQueryCategoryReceipt
    original_native_calculator_executed: bool = False
    original_coefficients_written: bool = False
    live_game_state_updated: bool = False

def source_original_40cbc0_full_linked_category(
    *, original_40cbc0_reached_query_category_inputs: dict,
    original_4fa510_group_source_inputs: dict,
) -> SourceOriginal40CBC0FullCategoryReceipt:
    if (type(original_40cbc0_reached_query_category_inputs) is not dict or
        type(original_4fa510_group_source_inputs) is not dict):
        raise Original40CBC0FullCategoryError('native source group and route dictionaries required')
    category_input=original_40cbc0_reached_query_category_inputs.get('original_4fa520_category_input')
    lookup_input=original_40cbc0_reached_query_category_inputs.get('original_4f3b10_lookup_input')
    if type(category_input) is not dict or type(lookup_input) is not dict:
        raise Original40CBC0FullCategoryError('native 4FA520 category and 4F3B10 owner stages required')
    group=source_original_4fa510_group_category(**original_4fa510_group_source_inputs)
    if (group.original_source_object_pointer!=category_input.get('original_4fa520_ecx_object_pointer') or
        group.original_4fa510_returned_eax!=category_input.get('original_4fa510_returned_eax') or
        group.original_signed_20_slot!=(int.from_bytes(category_input.get('original_4fa520_object_record',b'')[0x20:0x22],'little',signed=True)
             if type(category_input.get('original_4fa520_object_record')) is bytes else None) or
        group.original_group_field_at_876c50_plus24!=(int.from_bytes(category_input.get('original_reached_slot_dword_record',b''),'little')
             if type(category_input.get('original_reached_slot_dword_record')) is bytes else None) or
        original_4fa510_group_source_inputs.get('original_4fa510_object_bytes')!=category_input.get('original_4fa520_object_record') or
        original_4fa510_group_source_inputs.get('original_global_876c50_base_pointer')!=category_input.get('original_global_876c50_base_pointer') or
        original_4fa510_group_source_inputs.get('original_reached_876c50_index_slot_pointer')!=category_input.get('original_reached_slot_pointer') or
        original_4fa510_group_source_inputs.get('original_reached_index_slot_dword')!=category_input.get('original_reached_slot_dword_record')):
        raise Original40CBC0FullCategoryError('4FA510 category group source does not own reached 4FA520 input')
    route=source_original_40cbc0_reached_query_category(
        **original_40cbc0_reached_query_category_inputs)
    if route.native_linked_owner.original_found_object_pointer_or_zero!=group.original_source_object_pointer:
        raise Original40CBC0FullCategoryError('native 410FF0 member does not match selected 4F3B10 query owner')
    return SourceOriginal40CBC0FullCategoryReceipt(group,route)
