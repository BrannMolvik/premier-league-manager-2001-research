"""Source-bounded native 66951C state update followed by 64D540 scaled draw.

Requires actual 66D553 per-thread CRT RNG owner and reached signed argument;
does not execute any original native process, change real RNG/GameState or
invent seeds. Reference PE SHA256 833bf95e...7cc3, static inspection only.
"""
from dataclasses import dataclass
from struct import pack_into, unpack_from

class OriginalNative64D540SourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal64D540DrawReceipt:
    native_rng_owner_pointer: int
    original_owner_after_source_step: bytes
    original_seed_before: int
    original_seed_after: int
    original_66951c_unsigned15_output: int
    native_reached_signed_bound: int
    source_scaled_truncate_result: int
    native_rng_executed: bool = False
    live_game_state_updated: bool = False


def source_original_66951c_then_64d540_scaled_draw(
    *, original_66d553_rng_owner_pointer: int,
    original_rng_owner_before_66951c: bytes,
    original_64d540_reached_signed_argument: int,
) -> SourceOriginal64D540DrawReceipt:
    p=original_66d553_rng_owner_pointer
    arg=original_64d540_reached_signed_argument
    raw=original_rng_owner_before_66951c
    if type(p) is not int or not 0 < p <= 0xffffffff:
        raise OriginalNative64D540SourceError('reached 66D553 native owner pointer required')
    if type(arg) is not int or not -(1<<31) <= arg < (1<<31):
        raise OriginalNative64D540SourceError('actual 64D540 signed bound required')
    if type(raw) is not bytes or len(raw) < 0x18:
        raise OriginalNative64D540SourceError('actual per-thread owner through +17 required')
    seed=unpack_from('<I',raw,0x14)[0]
    after=(seed*0x343fd+0x269ec3)&0xffffffff
    output=(after>>16)&0x7fff
    # Original 64D540: FILD result, FIMUL signed argument, FMUL 1/32768,
    # then 668350 FISTP QWORD with RC=truncate, returned as low DWORD.
    product=output*arg
    scaled=(abs(product)//32768)*(-1 if product<0 else 1)
    next_bytes=bytearray(raw)
    pack_into('<I',next_bytes,0x14,after)
    return SourceOriginal64D540DrawReceipt(p,bytes(next_bytes),seed,after,output,arg,scaled)
