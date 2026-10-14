"""Source-only 5DB6FA–5DB7C3 match-context suffix, nonzero native components.

Canonical original private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Original FILD zero-high QWORD, FLD ST0, FDIVRP ST(1),ST(0) divides a
nonzero number by itself, 1.0. Zero/NaN FPU status is unresolved and must
fail closed. This receipt never executes original callbacks, builds original
components, mutates GameState or completes a normal match.
"""
from dataclasses import dataclass
from struct import pack_into

class OriginalContextTailSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginalContextTailReceipt:
    native_context_after_reached_stores: bytes
    first_component: int
    second_component: int
    source_context_d84: int
    source_context_d94: int
    source_context_d98: int
    source_context_d9c: int
    original_native_calculator_executed: bool = False
    live_game_state_updated: bool = False

def source_original_5db6fa_two_component_context_tail(
    *, original_processing_object_pointer_at_entry: int,
    original_reached_processing_pointer_at_5db70c: int,
    original_context_before_5db6fa: bytes,
    original_ebx_component_at_5db6fc: int,
    original_ecx_component_at_5db704: int,
) -> SourceOriginalContextTailReceipt:
    def native_u32(value,name,nonzero=False):
        if type(value) is not int or not 0 <= value <= 0xffffffff or (nonzero and value==0):
            raise OriginalContextTailSourceError(name+' original native uint32 required')
        return value
    p=native_u32(original_processing_object_pointer_at_entry,'original owner',True)
    if native_u32(original_reached_processing_pointer_at_5db70c,'reached processor',True)!=p:
        raise OriginalContextTailSourceError('5DB70C reached EDI differs from native match processor')
    raw=original_context_before_5db6fa
    if type(raw) is not bytes or len(raw)<0xda0:
        raise OriginalContextTailSourceError('actual original context+D9C bytes required')
    ebx=native_u32(original_ebx_component_at_5db6fc,'source EBX',True)
    ecx=native_u32(original_ecx_component_at_5db704,'source ECX',True)
    total=(ebx+ecx)&0xffffffff
    if not total:
        raise OriginalContextTailSourceError('original wrapped zero D84 source-owner division unresolved')
    after=bytearray(raw)
    # Original 5DB70F..5DB726 native DWORD D84, D8C, D90.
    # Original positive FILD QWORD + FLD ST0 / FDIVRP ratios are both 1.0;
    # 0x821118=0.3, 0x821128=0.7; both classify literal 2.
    # 5DBDE0: min(4, ((((2+2)&u32)>>1)+2)&u32) => 4.
    for offset,val in ((0xd84,total),(0xd8c,ebx),(0xd90,ecx),
                       (0xd94,2),(0xd98,2),(0xd9c,4)):
        pack_into('<I',after,offset,val)
    return SourceOriginalContextTailReceipt(bytes(after),ebx,ecx,total,2,2,4)
