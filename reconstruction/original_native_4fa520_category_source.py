"""Reached original 4FA520 source category remapping used by 40CBC0.

4FA520 calls 4FA510 (4F8FF0->410FF0), then reads source global
876C50 at signed WORD object+20 times 64 plus 0x24. When that owner
field is 0x21, 4FA510 result 3->2 or 4->3; otherwise unchanged.
No original callbacks, memory dereference, match calculation or port mutation.
"""
from dataclasses import dataclass
from struct import unpack_from


class Original4FA520SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal4FA520CategoryReceipt:
    original_object_pointer: int
    original_signed_object_20_slot: int
    original_reached_source_slot_pointer: int
    original_reached_source_slot_dword: int
    original_4fa510_raw_category: int
    original_4fa520_returned_category: int
    original_4fa510_executed: bool = False
    original_4fa520_executed: bool = False
    live_game_state_updated: bool = False


def _native_ptr(v, name):
    if type(v) is not int or not 0 < v <= 0xffffffff:
        raise Original4FA520SourceError(name+" native source pointer required")
    return v


def source_original_4fa520_signed_slot_category(
    *,
    original_4fa520_ecx_object_pointer: int,
    original_4fa520_object_record: bytes,
    original_global_876c50_base_pointer: int,
    original_reached_slot_pointer: int,
    original_reached_slot_dword_record: bytes,
    original_4fa510_returned_eax: int,
) -> SourceOriginal4FA520CategoryReceipt:
    obj=_native_ptr(original_4fa520_ecx_object_pointer,"object")
    base=_native_ptr(original_global_876c50_base_pointer,"876C50 global")
    reached=_native_ptr(original_reached_slot_pointer,"4FA537 slot")
    data=original_4fa520_object_record
    if type(data) is not bytes or len(data)<0x22:
        raise Original4FA520SourceError("native object+20 signed WORD bytes required")
    slot=unpack_from("<h",data,0x20)[0]
    # Original MOVSX word then SHL 6, both in 32-bit address arithmetic.
    computed=(base + ((slot<<6)&0xffffffff) + 0x24)&0xffffffff
    if not computed or reached!=computed:
        raise Original4FA520SourceError("4FA537 original signed slot address mismatch")
    raw=original_reached_slot_dword_record
    if type(raw) is not bytes or len(raw)!=4:
        raise Original4FA520SourceError("actual reached global 876C50 indexed DWORD required")
    field=unpack_from("<I",raw,0)[0]
    native=original_4fa510_returned_eax
    if type(native) is not int or not 0<=native<=0xffffffff:
        raise Original4FA520SourceError("native 4FA510 category result required")
    result=({3:2,4:3}.get(native,native) if field==0x21 else native)
    return SourceOriginal4FA520CategoryReceipt(obj,slot,computed,field,native,result)
