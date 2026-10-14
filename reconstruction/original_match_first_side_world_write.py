"""Bounded original 0x5DB7D0–0x5DB9EC first-side persistent-world tail.

Source: private original footballmanager.exe SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3, static original PE only. Actual source first-side and processing-context bytes at the reached instruction are required. This is a source projection, not an original callback execution, a normal match or GameState write.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from


class OriginalFirstSideWorldWriteError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalFirstSideWorldWriteReceipt:
    original_first_side_after_bounded_tail: bytes
    original_processing_context_at_tail: bytes
    original_local_flag_at_5db7d0: int
    source_first_side_writes_skipped: bool
    updated_first_side_offsets: tuple[int, ...]
    original_5da2f0_callback_executed: bool = False
    live_game_state_updated: bool = False
    original_match_completed: bool = False


_SOURCE_WEIGHTS_821100 = (50, 100, 200, 300, 500)


def _u32(value, label):
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise OriginalFirstSideWorldWriteError(label + " must be native DWORD")
    return value


def _i32(value):
    value &= 0xffffffff
    return value - 0x100000000 if value & 0x80000000 else value


def _dw(record, offset):
    return unpack_from("<I", record, offset)[0]


def source_original_5db7d0_first_side_world_tail(
    *,
    original_first_side_before_tail: bytes,
    original_processing_context_at_tail: bytes,
    original_local_flag_at_5db7d0: int,
    original_stack_cap_div10_input_if_reached: int | None,
) -> SourceOriginalFirstSideWorldWriteReceipt:
    """Project exact conditional native history/stat suffix, not live execution.

    Native 5DB7D0 checks local flag; a nonzero flag skips ALL first-side
    stores. On flag0, source shifts the two five-DWORD history strips,
    stores +148/+160, performs signed 32-bit IMUL with unsigned division
    and weights [50,100,200,300,500] for +144, applies the original
    unsigned lower bound floor(cap_word/10) and the INT_MAX clamp, then
    conditionally updates +124/+128/+12C/+130 and +E8 bits7/8/9.
    668350 converts the native mean with x87 FISTP truncation.
    """
    first=original_first_side_before_tail
    context=original_processing_context_at_tail
    if type(first) is not bytes or len(first) < 0x178:
        raise OriginalFirstSideWorldWriteError(
            "reached source first-side object bytes through +177 required")
    if type(context) is not bytes or len(context) < 0xDA0:
        raise OriginalFirstSideWorldWriteError(
            "reached source match context bytes through +D9F required")
    flag=original_local_flag_at_5db7d0
    if type(flag) is not int or flag not in (0,1):
        raise OriginalFirstSideWorldWriteError("reached 5DB7D0 byte flag required")
    if flag:
        if original_stack_cap_div10_input_if_reached is not None:
            raise OriginalFirstSideWorldWriteError(
                "original 5DB8F1 cap is unreachable on 5DB7D0 skip")
        return SourceOriginalFirstSideWorldWriteReceipt(first,context,flag,True,())
    capword=_u32(original_stack_cap_div10_input_if_reached,
                  "reached original stack+10 cap")
    total=_dw(context,0xD84)
    firstpart=_dw(context,0xD8C)
    secondpart=_dw(context,0xD90)
    if (firstpart+secondpart)&0xffffffff != total:
        raise OriginalFirstSideWorldWriteError(
            "original same-call D84 != D8C + D90 owner components")
    after=bytearray(first)
    eax=0x174
    for _ in range(5):
        pack_into("<I",after,eax,_dw(after,eax-4))
        pack_into("<I",after,eax-0x18,_dw(after,eax-0x1c))
        eax-=4
    pack_into("<I",after,0x148,firstpart)
    pack_into("<I",after,0x160,total)
    count=_dw(after,0x144)
    if not count:
        count=1
        pack_into("<I",after,0x144,1)
    delta_sum=0
    for offset,weight in zip((0x148,0x14c,0x150,0x154,0x158),
                             _SOURCE_WEIGHTS_821100):
        product=_i32(((_dw(after,offset)-count)&0xffffffff)*weight)
        term=abs(product)//count
        delta_sum=(delta_sum+(-term if product<0 else term))&0xffffffff
    candidate=(count+delta_sum)&0xffffffff
    minimum=capword//10
    pack_into("<I",after,0x144,
              minimum if candidate<minimum or candidate>0x7fffffff else candidate)
    touched=[0x144,0x148,0x14c,0x150,0x154,0x158,0x15c,
             0x160,0x164,0x168,0x16c,0x170,0x174]
    flags=_dw(after,0xE8)
    if total>_dw(after,0x124) or not flags&0x80:
        pack_into("<I",after,0x124,total)
        touched.append(0x124)
        flags|=0x80
    if total<_dw(after,0x128) or not flags&0x100:
        pack_into("<I",after,0x128,total)
        touched.append(0x128)
        flags|=0x100
    if not flags&0x200:
        after[0x130]=1
        pack_into("<I",after,0x12c,total)
    else:
        oldcount=after[0x130]
        newcount=(oldcount+1)&0xff
        if not newcount:
            raise OriginalFirstSideWorldWriteError(
                "native x87 division by wrapped zero mean counter unresolved")
        product=(oldcount*_dw(after,0x12c))&0xffffffff
        # Native FILD loads a signed QWORD with zero upper DWORD.
        accumulator=product+_i32(total)
        mean=int(accumulator/newcount)  # 668350 FISTP truncates to zero
        after[0x130]=newcount
        pack_into("<I",after,0x12c,mean&0xffffffff)
    touched.extend((0x12c,0x130))
    flags|=0x200
    pack_into("<I",after,0xE8,flags)
    touched.append(0xE8)
    return SourceOriginalFirstSideWorldWriteReceipt(
        bytes(after),context,flag,False,tuple(sorted(touched)))
