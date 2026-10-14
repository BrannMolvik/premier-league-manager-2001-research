"""Original 5DB389–5DB3AE x87-to-int and conditional 5DB4C4 addend.

Each source operand is a reached QWORD native stack snapshot at its FLD site.
668350 temporarily sets x87 RC=truncate, FISTP QWORD, restores prior CW;
the original caller uses returned EAX low32. This projects source input bytes,
does not execute the original native callbacks, heap, queue, GUI or GameState.
"""
from dataclasses import dataclass
from math import isfinite,trunc
from struct import unpack

class OriginalNativeComponentInputError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginalMatchComponentInputReceipt:
    native_low32_conversion_results: tuple[int,int,int,int]
    original_ebx_at_5db396: int
    original_edi_at_5db3ae: int
    original_human_694_addend_at_5db4c4: int | None
    original_ebx_at_5db6fa: int
    original_ecx_at_5db704: int
    original_668350_callbacks_executed: bool = False
    live_game_state_updated: bool = False

def _native_668350_low32(source_qword: bytes, label: str) -> int:
    if type(source_qword) is not bytes or len(source_qword)!=8:
        raise OriginalNativeComponentInputError(label+' needs native IEEE754 QWORD')
    floating=unpack('<d',source_qword)[0]
    if not isfinite(floating):
        raise OriginalNativeComponentInputError(label+' invalid/NaN FPU source unknown')
    integer=trunc(floating)
    if not -(1<<63)<=integer<(1<<63):
        raise OriginalNativeComponentInputError(label+' signed FISTP QWORD overflow')
    return integer & 0xffffffff

def source_original_5db389_four_float_components(
    *, original_5db37c_esp68_qword: bytes,
    original_5db385_esp60_qword: bytes,
    original_5db390_esp50_qword: bytes,
    original_5db39f_esp58_qword: bytes,
    original_5db4c4_human_reached: bool,
    original_user_694_owner_pointer_if_reached: int | None,
    original_reached_user_694_record_if_reached: bytes | None,
) -> SourceOriginalMatchComponentInputReceipt:
    values=tuple(_native_668350_low32(x,n) for x,n in (
        (original_5db37c_esp68_qword,'5DB37C'),
        (original_5db385_esp60_qword,'5DB385'),
        (original_5db390_esp50_qword,'5DB390'),
        (original_5db39f_esp58_qword,'5DB39F')))
    ebx=(values[0]+values[1])&0xffffffff
    edi=(values[2]+values[3])&0xffffffff
    human=original_5db4c4_human_reached
    if type(human) is not bool:
        raise OriginalNativeComponentInputError('actual 5DB4C4 source reachability required')
    extra=None
    if human:
        p=original_user_694_owner_pointer_if_reached
        raw=original_reached_user_694_record_if_reached
        if (type(p) is not int or not 0<p<=0xffffffff or
                type(raw) is not bytes or len(raw)<4):
            raise OriginalNativeComponentInputError('actual reached first-user +694 owner DWORD required')
        extra=int.from_bytes(raw[:4],'little')
        ebx=(ebx+extra)&0xffffffff
    elif original_user_694_owner_pointer_if_reached is not None or original_reached_user_694_record_if_reached is not None:
        raise OriginalNativeComponentInputError('unreached human +694 source addend')
    return SourceOriginalMatchComponentInputReceipt(
        values,(values[0]+values[1])&0xffffffff,edi,extra,ebx,edi)
