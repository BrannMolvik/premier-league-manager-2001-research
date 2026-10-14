"""Source-only native 4FA510 -> 4F8FF0 -> 410FF0 category producer.

Original private footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Requires the reached object pointer, signed object+20 indexing into 876C50,
global 874BE0 group, 410FF0 group+48/4C and actual ordered member DWORDs.
No native original executed, no 4FA520 category mutation, no GameState.
"""
from dataclasses import dataclass
from struct import unpack_from


class Original4FA510GroupSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal4FA510GroupReceipt:
    original_source_object_pointer: int
    original_signed_20_slot: int
    original_group_field_at_876c50_plus24: int
    original_4f8ff0_group_pointer: int
    original_410ff0_group_member_count_signed: int
    original_410ff0_member_pointer_or_zero: int
    original_4fa510_returned_eax: int
    original_native_4fa510_executed: bool = False
    original_native_410ff0_executed: bool = False
    live_game_state_updated: bool = False


def _ptr(value, label, zero=False):
    if type(value) is not int or not 0<=value<=0xffffffff or (not zero and not value):
        raise Original4FA510GroupSourceError(label + ' native pointer/DWORD required')
    return value


def source_original_4fa510_group_category(
    *, original_4fa510_ecx_object_pointer: int,
    original_4fa510_object_bytes: bytes,
    original_global_876c50_base_pointer: int,
    original_reached_876c50_index_slot_pointer: int,
    original_reached_index_slot_dword: bytes,
    original_global_874be0_groups_base_pointer: int,
    original_reached_410ff0_group_pointer: int,
    original_reached_410ff0_group_record: bytes,
    original_reached_410ff0_member_array_pointer_if_positive: int | None,
    original_reached_410ff0_member_dwords_if_positive: bytes | None,
) -> SourceOriginal4FA510GroupReceipt:
    native=_ptr(original_4fa510_ecx_object_pointer,'4FA510 object')
    obj=original_4fa510_object_bytes
    if type(obj) is not bytes or len(obj)<0x22:
        raise Original4FA510GroupSourceError('actual reached object+20 signed WORD required')
    slot=unpack_from('<h',obj,0x20)[0]
    base=_ptr(original_global_876c50_base_pointer,'876C50 bucket base')
    slotptr=_ptr(original_reached_876c50_index_slot_pointer,'indexed field slot')
    expected=(base+((slot<<6)&0xffffffff)+0x24)&0xffffffff
    if slotptr!=expected:
        raise Original4FA510GroupSourceError('4F8FFD indexed native owner address differs')
    record=original_reached_index_slot_dword
    if type(record) is not bytes or len(record)!=4:
        raise Original4FA510GroupSourceError('actual reached 876C50 indexed field DWORD required')
    field=unpack_from('<I',record,0)[0]
    groups=_ptr(original_global_874be0_groups_base_pointer,'874BE0 groups base')
    reached=_ptr(original_reached_410ff0_group_pointer,'410FF0 native category group')
    calculated=(groups+((field*108)&0xffffffff))&0xffffffff
    if reached!=calculated:
        raise Original4FA510GroupSourceError('4F8FF0 group pointer not 874BE0 plus 108*field')
    group=original_reached_410ff0_group_record
    if type(group) is not bytes or len(group)<0x50:
        raise Original4FA510GroupSourceError('actual 410FF0 group+48/+4C bytes required')
    count=unpack_from('<i',group,0x4c)[0]
    if count<=0:
        if (original_reached_410ff0_member_array_pointer_if_positive is not None or
            original_reached_410ff0_member_dwords_if_positive is not None):
            raise Original4FA510GroupSourceError('410FF0 count<=0 never reads member list')
        index=0xffffffff
        array_pointer=0
    else:
        if count>65536:
            raise Original4FA510GroupSourceError('native count beyond bounded source projection')
        array_pointer=unpack_from('<I',group,0x48)[0]
        claimed=_ptr(original_reached_410ff0_member_array_pointer_if_positive,'410FF0 members')
        if not array_pointer or claimed!=array_pointer:
            raise Original4FA510GroupSourceError('410FF0 member array pointer changed')
        members=original_reached_410ff0_member_dwords_if_positive
        if type(members) is not bytes or len(members)!=count*4:
            raise Original4FA510GroupSourceError('complete reached 410FF0 member DWORD bytes required')
        index=0xffffffff
        for i in range(count):
            if unpack_from('<I',members,i*4)[0]==native:
                index=i
                break
    return SourceOriginal4FA510GroupReceipt(
        native,slot,field,calculated,count,array_pointer,index)
