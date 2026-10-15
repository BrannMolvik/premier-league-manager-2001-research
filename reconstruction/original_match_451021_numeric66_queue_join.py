"""Source-matched 451021 -> 5DC890 numeric 0x66 -> 5DD1F0 records.

The original 45100E pushes EDX whose low WORD came from [ESI+D8]+4.
4139D0 internally pushes global+9C4 for a DIFFERENT registered user
lookup; its plain RET leaves the numeric argument for 5DC890.
The original 5DC8D4 0x66 branch copies two input triples and calls
5DD1F0 exactly once. These inputs must be independently sourced from
41C580/404410 and the actual reader queue; no live score is inferred.
"""
from dataclasses import dataclass

from original_match_451021_indexed_owner import (
    SourceOriginal451021IndexedOwner,
    source_original_451021_reader_5db450_writer_snapshot,
)
from original_match_5dd1f0_queue_query import (
    Original5DD1F0LinkedPayload,SourceOriginal5DD1F0QueryReceipt,
    source_original_5dd1f0_queue_readback,
)


class Original451021Numeric66SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal451021Numeric66Records:
    indexed_native_user_queue_source: SourceOriginal451021IndexedOwner
    original_source_5dd1f0_record_selection: SourceOriginal5DD1F0QueryReceipt
    original_native_5dc890_selector_word: int = 0x66
    original_source_dispatch_branch: int = 0x5DC8DA
    original_5dd1f0_call_site: int = 0x5DC910
    original_native_dispatch_executed: bool = False
    original_source_query_values_independently_reached: bool = False
    original_native_x87_total_executed: bool = False
    original_game_state_updated: bool = False


def source_original_451021_match_numeric_66_queue_records(
    *,
    original_reader_writer_owner_kwargs: dict,
    original_queue_pointer_at_5dc890: int,
    original_queue_owner_bytes_at_5dd1f0: bytes,
    original_linked_payload_nodes_at_5dd1f0: tuple[Original5DD1F0LinkedPayload, ...],
    original_lower_range_triple_at_5dc890: tuple[int,int,int],
    original_upper_range_triple_at_5dc890: tuple[int,int,int],
) -> SourceOriginal451021Numeric66Records:
    if type(original_reader_writer_owner_kwargs) is not dict:
        raise Original451021Numeric66SourceError('actual source owner arguments required')
    owner=source_original_451021_reader_5db450_writer_snapshot(
        **original_reader_writer_owner_kwargs)
    if owner.original_reader_dispatch_selector_word_from_d8 != 0x66:
        raise Original451021Numeric66SourceError(
            'only original 5DC890 numeric selector 0x66 direct-call branch supported')
    ptr=original_queue_pointer_at_5dc890
    if type(ptr) is not int or ptr!=owner.original_reader_queue_pointer:
        raise Original451021Numeric66SourceError(
            '5DC890 reached queue pointer must be 45101A original indexed slot')
    result=source_original_5dd1f0_queue_readback(
        original_queue_owner_bytes=original_queue_owner_bytes_at_5dd1f0,
        original_linked_payload_nodes=original_linked_payload_nodes_at_5dd1f0,
        original_query_type_dword=0x66,
        original_signed_lower_triple=original_lower_range_triple_at_5dc890,
        original_signed_upper_triple=original_upper_range_triple_at_5dc890,
    )
    return SourceOriginal451021Numeric66Records(owner,result)
