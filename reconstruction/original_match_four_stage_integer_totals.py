"""Source-only 5DB37C four scored QWORDs to original pre-human DWORD pairs.
Actual native stage stack and guard inputs are independently supplied.
668350 temporarily truncates x87 FISTP signed64; 5DB394/5DB3AA add
low EAX results as 32-bit values. Does not execute original/GameState.
"""
from dataclasses import dataclass
from math import isfinite, trunc
from struct import unpack_from

class OriginalFourStageIntegerTotalError(ValueError):
    pass

_STAGE_SLOT_OFFSETS=(0x60,0x58,0x68,0x50)
_ORIGINAL_668350_CALLS=(0x5DB380,0x5DB38B,0x5DB39A,0x5DB3A5)

@dataclass(frozen=True)
class SourceOriginalFourStageIntegerTotal:
    original_entered_stage_guards: tuple[bool,bool,bool,bool]
    original_stage_qwords: tuple[bytes,bytes,bytes,bytes]
    original_stage_converted_s64: tuple[int,int,int,int]
    original_pre_human_ebx_first_and_third_u32: int
    original_pre_human_edi_fourth_and_second_u32: int
    original_668350_call_sites: tuple[int,int,int,int]=_ORIGINAL_668350_CALLS
    original_native_executed: bool=False
    original_context_written: bool=False

def source_original_5db37c_four_stage_integer_totals(
    *,original_stage_stack_at_5db37c: bytes,
    original_entered_stage_guards: tuple[bool,bool,bool,bool]
)->SourceOriginalFourStageIntegerTotal:
    s=original_stage_stack_at_5db37c
    if type(s) is not bytes or len(s)<0x70:
        raise OriginalFourStageIntegerTotalError('reached original stack S+0x50..0x6f required')
    gates=original_entered_stage_guards
    if type(gates) is not tuple or len(gates)!=4 or any(type(g) is not bool for g in gates):
        raise OriginalFourStageIntegerTotalError('independently reached original stage guards required')
    raw=tuple(s[off:off+8] for off in _STAGE_SLOT_OFFSETS)
    for i,(entered,qword) in enumerate(zip(gates,raw),1):
        if not entered and qword!=bytes(8):
            raise OriginalFourStageIntegerTotalError(f'skipped stage{i} has nonzero original initialized QWORD')
    values=[]
    for i,qword in enumerate(raw,1):
        value=unpack_from('<d',qword)[0]
        if not isfinite(value):
            raise OriginalFourStageIntegerTotalError(f'nonfinite original stage{i} FISTP unresolved')
        converted=trunc(value)
        if not -(1<<63)<=converted<(1<<63):
            raise OriginalFourStageIntegerTotalError(f'original stage{i} signed64 FISTP overflow')
        values.append(converted)
    ebx=(values[2]+values[0])&0xffffffff
    edi=(values[3]+values[1])&0xffffffff
    return SourceOriginalFourStageIntegerTotal(gates,raw,tuple(values),ebx,edi)
