"""Source-only 5DC510 0x20 record→0x0C wrapper→617D70 owner FIFO append.

The original 5DC510/+10 FPU owner change, 5DC650, heap allocation, native
queue mutation and original program execution are NOT performed. Never alias
this selected user+670 owner's queue to registered-user+6B4 Inbox mail.
Private original executable SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into, unpack_from


class Original5DC510EventTailError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal5DC510EventTailReceipt:
    owner_after_append: bytes
    new_native_payload_after_stores: bytes
    new_native_wrapper_after_append: bytes
    old_tail_after_append_if_reached: bytes | None
    original_new_payload_pointer: int
    original_new_wrapper_pointer: int
    original_native_allocation_executed: bool = False
    original_5dc650_executed: bool = False
    original_live_queue_mutated: bool = False
    live_game_state_updated: bool = False


def _ptr(value, label):
    if type(value) is not int or not 0 < value <= 0xffffffff:
        raise Original5DC510EventTailError(label+" original native pointer required")
    return value


def _dw(record, offset):
    return unpack_from("<I",record,offset)[0]


def source_original_5dc510_record_tail_append(
    *, original_owner_pointer: int, original_owner_at_5dc5d9: bytes,
    original_payload_pointer_allocated: int,
    original_payload_20_bytes_before_stores: bytes,
    original_wrapper_pointer_allocated: int,
    original_wrapper_0c_bytes_before_stores: bytes,
    original_original_args_ebp8_to_ebp28: bytes,
    original_old_tail_wrapper_if_nonempty: bytes | None,
    original_old_tail_pointer_if_nonempty: int | None,
) -> SourceOriginal5DC510EventTailReceipt:
    """Exact reached native 5DC5D9..5DC63A and 617D70 queue stores.

    EBP+8/+C/+10/+14 are DWORDs at payload offsets 0/4/8/C.
    EBP+18 is WORD at payload+10; EBP+1C/+20/+24 are DWORDs at
    payload+14/+18/+1C. Original malloc padding +12/+13 is UNKNOWN
    and remains unchanged. EBP+28 is used earlier in a separate FPU
    callback but is not stored into the allocated event payload.
    Two original allocation successes must be independently reached.
    """
    owner_pointer=_ptr(original_owner_pointer,"owner")
    payload_pointer=_ptr(original_payload_pointer_allocated,"0x20 allocation")
    wrapper_pointer=_ptr(original_wrapper_pointer_allocated,"0x0c allocation")
    if len({owner_pointer,payload_pointer,wrapper_pointer})!=3:
        raise Original5DC510EventTailError("source allocated pointer aliases")
    owner=original_owner_at_5dc5d9
    payload=original_payload_20_bytes_before_stores
    wrapper=original_wrapper_0c_bytes_before_stores
    args=original_original_args_ebp8_to_ebp28
    if (type(owner) is not bytes or len(owner)<12 or
            type(payload) is not bytes or len(payload)!=0x20 or
            type(wrapper) is not bytes or len(wrapper)!=0x0c or
            type(args) is not bytes or len(args)<0x24):
        raise Original5DC510EventTailError(
            "reached original owner, allocated records and EBP args required")
    first,last=_dw(owner,4),_dw(owner,8)
    if (not first)!=(not last) or (last and (last==wrapper_pointer or first==wrapper_pointer)):
        raise Original5DC510EventTailError("source owner queue head/tail contradiction")
    old_tail=original_old_tail_wrapper_if_nonempty
    if last:
        if _ptr(original_old_tail_pointer_if_nonempty,"old tail")!=last:
            raise Original5DC510EventTailError("old tail pointer identity drift")
        if type(old_tail) is not bytes or len(old_tail)!=0x0c or _dw(old_tail,4)!=0:
            raise Original5DC510EventTailError("reached terminal old native wrapper required")
    elif old_tail is not None or original_old_tail_pointer_if_nonempty is not None:
        raise Original5DC510EventTailError("old tail not reached in empty native source owner")
    record=bytearray(payload)
    for arg_offset,record_offset in (
        (0,0),(4,4),(8,8),(12,12),(20,20),(24,24),(28,28)
    ):
        pack_into("<I",record,record_offset,_dw(args,arg_offset))
    pack_into("<H",record,16,unpack_from("<H",args,16)[0])
    node=bytearray(wrapper)
    pack_into("<III",node,0,payload_pointer,0,last)
    result_owner=bytearray(owner)
    pack_into("<I",result_owner,8,wrapper_pointer)
    if last==0:
        pack_into("<I",result_owner,4,wrapper_pointer)
    prev=None
    if last:
        prev_bytes=bytearray(old_tail)
        pack_into("<I",prev_bytes,4,wrapper_pointer)
        prev=bytes(prev_bytes)
    return SourceOriginal5DC510EventTailReceipt(
        bytes(result_owner),bytes(record),bytes(node),prev,
        payload_pointer,wrapper_pointer)
