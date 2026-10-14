"""Source-only 5DC650 optional-reference branches -> allocated native event FIFO.

Does not invoke 5E48D0/5E43B0, 42C6C0, 4139D0, native FPU,
allocation, 617D70, or a running original executable. Input is actually
reached source bytes AFTER owner+0x10 and callback preparation. 0x5DC701
and 0x5DC7EB write an EH-stack state marker, NOT a proven event type.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into
from original_native_5dc510_event_tail import (
    SourceOriginal5DC510EventTailReceipt,
    source_original_5dc510_record_tail_append,
    Original5DC510EventTailError,
)

class Original5DC650EventTailError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal5DC650EventTailReceipt:
    original_5dc672_edi_pointer: int
    original_5dc650_path: str
    original_staged_5e43b0_conversion_result: bytes
    original_source_fifo_projection: SourceOriginal5DC510EventTailReceipt
    original_callbacks_executed: bool = False
    original_live_world_committed: bool = False

def _native_dword(v: int, name: str, allow_zero: bool = True) -> int:
    if type(v) is not int or not 0 <= v <= 0xffffffff or (not allow_zero and not v):
        raise Original5DC650EventTailError(name+' actual native uint32/pointer required')
    return v

def source_original_5dc650_reached_record_and_fifo(
    *, original_edi_pointer_at_5dc672: int,
    original_reached_event_conversion_5e43b0_bytes: bytes,
    original_reached_esp50_word: int,
    original_reached_esp58_dword: int,
    original_reached_esp5c_dword: int,
    original_reached_esp60_dword: int,
    original_owner_pointer_at_5dc854: int,
    original_owner_at_5dc854: bytes,
    original_payload_pointer_allocated: int,
    original_payload_20_bytes_before_stores: bytes,
    original_wrapper_pointer_allocated: int,
    original_wrapper_0c_bytes_before_stores: bytes,
    original_old_tail_wrapper_if_nonempty: bytes | None,
    original_old_tail_pointer_if_nonempty: int | None,
) -> SourceOriginal5DC650EventTailReceipt:
    """Project only an ALREADY-REACHED post-5E43B0 successful-allocation tail.

    For EDI nonnull the source first reaches 5DC707..5DC760; null EDI
    reaches 5DC7F5..5DC84D. Both copy an actual 16-byte 5E43B0 result
    into payload+0..+F, reached word into +10, three reached dwords
    into +14/+18/+1C. Allocator padding +12/+13 remains untouched.
    Each optionally returns before allocation based on dynamic x87 compare,
    +0x54 original callback, and other user getter; none proven here.
    """
    edi=_native_dword(original_edi_pointer_at_5dc672,'source EDI')
    converted=original_reached_event_conversion_5e43b0_bytes
    if type(converted) is not bytes or len(converted)!=16:
        raise Original5DC650EventTailError('actual sixteen native 5E43B0 bytes required')
    word=original_reached_esp50_word
    if type(word) is not int or not 0 <= word <= 0xffff:
        raise Original5DC650EventTailError('source ESP+50 WORD required')
    arguments=bytearray(0x24)
    arguments[:16]=converted
    pack_into('<H',arguments,16,word)
    for offset,value,label in ((20,original_reached_esp58_dword,'ESP+58'),
                               (24,original_reached_esp5c_dword,'ESP+5C'),
                               (28,original_reached_esp60_dword,'ESP+60')):
        pack_into('<I',arguments,offset,_native_dword(value,label))
    try:
        fifo=source_original_5dc510_record_tail_append(
            original_owner_pointer=_native_dword(original_owner_pointer_at_5dc854,'queue owner',False),
            original_owner_at_5dc5d9=original_owner_at_5dc854,
            original_payload_pointer_allocated=original_payload_pointer_allocated,
            original_payload_20_bytes_before_stores=original_payload_20_bytes_before_stores,
            original_wrapper_pointer_allocated=original_wrapper_pointer_allocated,
            original_wrapper_0c_bytes_before_stores=original_wrapper_0c_bytes_before_stores,
            original_original_args_ebp8_to_ebp28=bytes(arguments),
            original_old_tail_wrapper_if_nonempty=original_old_tail_wrapper_if_nonempty,
            original_old_tail_pointer_if_nonempty=original_old_tail_pointer_if_nonempty,
        )
    except Original5DC510EventTailError as exc:
        raise Original5DC650EventTailError('native 5DC650 617D70 owner or buffer unqualified') from exc
    return SourceOriginal5DC650EventTailReceipt(
        edi,'edi-nonnull-5dc707' if edi else 'edi-null-5dc7f5',converted,fifo)
