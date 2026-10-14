"""Exact reached original 40CF31 default coefficient QWORD stores.

40CF53 category >4 returns at 40CF95 without touching either output.
For 0..4 table at 40D01C chooses original 822040..822080 double
(30,20,16,12,9); x87 multiplies exact source 7BD6A8=0.5,
FST QWORD [esi], then 7BD558=0.75, FSTP QWORD [ebx].
These constants and products are all exactly IEEE754 representable.
No original FPU/callback/heap/GameState is executed.
"""
from dataclasses import dataclass
from struct import pack

from original_native_40cbc0_full_category_join import (
    SourceOriginal40CBC0FullCategoryReceipt,
)

class Original40CF31DefaultSourceError(ValueError):
    pass

_ORIGINAL_NATIVE_COEFFICIENTS=(30.0,20.0,16.0,12.0,9.0)
_ORIGINAL_NATIVE_FMUL_FIRST=0.5
_ORIGINAL_NATIVE_FMUL_SECOND=0.75

@dataclass(frozen=True)
class SourceOriginal40CF31DefaultWriteReceipt:
    original_native_category: int
    original_first_output_pointer: int
    original_second_output_pointer: int
    original_first_output_after: bytes
    original_second_output_after: bytes
    original_both_native_outputs_written: bool
    original_40cf31_executed: bool = False
    original_native_match_executed: bool = False
    live_game_state_updated: bool = False

def source_original_40cf31_default_coefficient_pair(
    *, original_reached_source_category: SourceOriginal40CBC0FullCategoryReceipt,
    original_40cbc0_ebp8_first_output_pointer: int,
    original_40cbc0_ebpc_second_output_pointer: int,
    original_first_output_before: bytes,
    original_second_output_before: bytes,
) -> SourceOriginal40CF31DefaultWriteReceipt:
    stage=original_reached_source_category
    if type(stage) is not SourceOriginal40CBC0FullCategoryReceipt:
        raise Original40CF31DefaultSourceError('complete reached native source category required')
    if stage.source_first_side_route_and_category.first_side_dispatch.original_selected_jump_target!=0x40cf31:
        raise Original40CF31DefaultSourceError('40CF31 default source path not reached')
    category=stage.source_first_side_route_and_category.original_source_category.original_4fa520_returned_category
    if type(category) is not int or not 0<=category<=0xffffffff:
        raise Original40CF31DefaultSourceError('source 4FA520 DWORD category required')
    p=original_40cbc0_ebp8_first_output_pointer
    q=original_40cbc0_ebpc_second_output_pointer
    if (type(p) is not int or type(q) is not int or not 0<p<=0xffffffff or
            not 0<q<=0xffffffff or p==q):
        raise Original40CF31DefaultSourceError('separate actual original 40CBC0 QWORD output pointers required')
    first=original_first_output_before
    second=original_second_output_before
    if type(first) is not bytes or len(first)!=8 or type(second) is not bytes or len(second)!=8:
        raise Original40CF31DefaultSourceError('native original two output QWORD snapshots required')
    if category>4:
        return SourceOriginal40CF31DefaultWriteReceipt(category,p,q,first,second,False)
    source=_ORIGINAL_NATIVE_COEFFICIENTS[category]
    # Original FST QWORD first and FSTP QWORD second. Exact 0.5/0.75
    # multipliers and integer/half-integer source constants => no x87
    # precision ambiguity for these only, not other dispatch branches.
    x=source*_ORIGINAL_NATIVE_FMUL_FIRST
    y=x*_ORIGINAL_NATIVE_FMUL_SECOND
    return SourceOriginal40CF31DefaultWriteReceipt(
        category,p,q,pack('<d',x),pack('<d',y),True)
