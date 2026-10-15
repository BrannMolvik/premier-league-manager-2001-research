"""Source-bounded full original 40CBC0 coefficient dispatch/store journey.

Eight original 40CFA0 jump targets. 26 and 33 return after one native
4FA520 category and their own QWORD stores; 24/31/40/66/73 fall
through successive named entrypoints and end at 40CF31. Every native
4FA520 call's actual result must be independently supplied, not
synthesized from the first or assumed stable. Repeated categories that
disagree fail closed because context mutation is unresolved.

All reached source constants are exactly binary-representable doubles;
FSTP and FST QWORD store bytes can therefore be projected here
without fabricating x87 precision. No original call or GUI executes.
"""
from dataclasses import dataclass
from struct import pack

from original_native_40cbc0_full_category_join import (
    SourceOriginal40CBC0FullCategoryReceipt,
)

class Original40CBC0AllPathSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal40CBC0QWORDStore:
    native_branch_entry_va: int
    source_first_qword_after: bytes
    source_second_qword_after: bytes

@dataclass(frozen=True)
class SourceOriginal40CBC0AllPathReceipt:
    original_entry_target: int
    native_category: int
    original_reached_category_calls: int
    original_intermediate_output_store_order: tuple[SourceOriginal40CBC0QWORDStore,...]
    original_first_qword_after: bytes
    original_second_qword_after: bytes
    original_any_coefficient_written: bool
    original_40cbc0_executed: bool = False
    original_5da2f0_match_executed: bool = False
    live_game_state_updated: bool = False

_ENTRY_STAGES={
    0x40cbf2:(0x40cbf2,),
    0x40ccc9:(0x40ccc9,),
    0x40cd5d:(0x40cd5d,0x40cdb3,0x40ce09,0x40ce83,0x40ceda,0x40cf31),
    0x40cdb3:(0x40cdb3,0x40ce09,0x40ce83,0x40ceda,0x40cf31),
    0x40ce09:(0x40ce09,0x40ce83,0x40ceda,0x40cf31),
    0x40ce83:(0x40ce83,0x40ceda,0x40cf31),
    0x40ceda:(0x40ceda,0x40cf31),
    0x40cf31:(0x40cf31,),
}
_ORIGINAL_MAIN_VALUES=(30.,20.,16.,12.,9.)
_ORIGINAL_CASE33_VALUES=(20.,15.,10.)
_ORIGINAL_CASE40_VALUES=(25.,17.)
_ORIGINAL_CASE73_VALUES=(16.,12.)
_ORIGINAL_CASE66_VALUES=(20.,16.,12.,9.,9.)
_ORIGINAL_CASE24_VALUES=(15.,10.)
_ORIGINAL_CASE31_VALUES=(17.,12.)

def source_original_40cbc0_all_dispatch_coefficients(
    *,
    original_first_native_category_receipt: SourceOriginal40CBC0FullCategoryReceipt,
    original_actual_categories_for_each_4fa520_call: tuple[int,...],
    original_ebp8_first_qword_pointer: int,
    original_ebpc_second_qword_pointer: int,
    original_first_qword_before: bytes,
    original_second_qword_before: bytes,
) -> SourceOriginal40CBC0AllPathReceipt:
    record=original_first_native_category_receipt
    if type(record) is not SourceOriginal40CBC0FullCategoryReceipt:
        raise Original40CBC0AllPathSourceError("complete original first category owner source receipt required")
    source=record.source_first_side_route_and_category
    target=source.first_side_dispatch.original_selected_jump_target
    stages=_ENTRY_STAGES.get(target)
    if stages is None:
        raise Original40CBC0AllPathSourceError("original native dispatch target unknown")
    categories=original_actual_categories_for_each_4fa520_call
    original_category=source.original_source_category.original_4fa520_returned_category
    if (type(categories) is not tuple or len(categories)!=len(stages) or
            type(original_category) is not int or not 0<=original_category<=0xffffffff or
            any(type(x) is not int or x!=original_category for x in categories)):
        raise Original40CBC0AllPathSourceError(
            "actual native per-stage 4FA520 category changes or missing reached calls")
    p=original_ebp8_first_qword_pointer
    q=original_ebpc_second_qword_pointer
    if (type(p) is not int or type(q) is not int or
        not 0<p<=0xffffffff or not 0<q<=0xffffffff or p==q):
        raise Original40CBC0AllPathSourceError("two distinct original 40CBC0 native QWORD output owners required")
    first=original_first_qword_before
    second=original_second_qword_before
    if type(first) is not bytes or len(first)!=8 or type(second) is not bytes or len(second)!=8:
        raise Original40CBC0AllPathSourceError("actual reached original QWORD output bytes required")
    writes=[]
    for stage in stages:
        base=None
        if stage==0x40cbf2:
            if original_category<=4: base=_ORIGINAL_MAIN_VALUES[original_category]
        elif stage==0x40ccc9:
            if original_category<=2: base=_ORIGINAL_CASE33_VALUES[original_category]
        elif stage==0x40cd5d:
            if original_category<=1: base=_ORIGINAL_CASE40_VALUES[original_category]
        elif stage==0x40cdb3:
            if original_category<=1: base=_ORIGINAL_CASE73_VALUES[original_category]
        elif stage==0x40ce09:
            if original_category<=4: base=_ORIGINAL_CASE66_VALUES[original_category]
        elif stage==0x40ce83:
            if original_category<=1: base=_ORIGINAL_CASE24_VALUES[original_category]
        elif stage==0x40ceda:
            if original_category<=1: base=_ORIGINAL_CASE31_VALUES[original_category]
        elif stage==0x40cf31:
            if original_category<=4:
                base=_ORIGINAL_MAIN_VALUES[original_category]*0.5
        if base is not None:
            # All source bases integers or exact halves, and 0.75 is
            # 3/4. Native x87 80-bit and Python IEEE754 agree exactly.
            first=pack("<d",base)
            second=pack("<d",base*0.75)
            writes.append(SourceOriginal40CBC0QWORDStore(stage,first,second))
    return SourceOriginal40CBC0AllPathReceipt(
        target,original_category,len(stages),tuple(writes),first,second,bool(writes))
