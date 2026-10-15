"""Bounded source-only original four scoring-stage 64D540 call-site reach.

Four x87 AH gates determine which stages execute. Each entered stage has
one original 64D540 call after its signed 668350 EDI clamp. The actual
per-thread RNG owner/snapshot must be supplied independently for EVERY
reached call; other original callbacks might consume the same RNG between
these calls, so this function NEVER chains presumed contiguous seeds.
"""
from dataclasses import dataclass
from original_match_four_stage_guard_source import source_original_four_stage_guard_dispatch
from original_native_64d540_rand_step import (
    SourceOriginal64D540DrawReceipt,source_original_66951c_then_64d540_scaled_draw,
)

class OriginalFourStageRngReachError(ValueError):
    pass

_STAGE_CALLS=(0x5dabed,0x5dae68,0x5db0e9,0x5db364)

@dataclass(frozen=True)
class SourceOriginalFourStageRngReachReceipt:
    original_four_stage_guard_ah: tuple[int,int,int,int]
    original_stage_rng_call_addresses_if_reached: tuple[int|None,int|None,int|None,int|None]
    original_stage_rng_draws_if_reached: tuple[SourceOriginal64D540DrawReceipt|None,SourceOriginal64D540DrawReceipt|None,SourceOriginal64D540DrawReceipt|None,SourceOriginal64D540DrawReceipt|None]
    original_intermittent_rng_consumption_qualified: bool=False
    actual_original_rng_callbacks_executed: bool=False
    live_game_state_updated: bool=False


def source_original_four_stage_rng_reach(
    *, original_native_x87_ah_at_four_stage_guards: tuple[int,int,int,int],
    original_native_668350_eax_at_each_reached_clamp: tuple[int|None,int|None,int|None,int|None],
    original_66d553_rng_owner_pointer: int,
    original_rng_owner_bytes_before_each_reached_call: tuple[bytes|None,bytes|None,bytes|None,bytes|None],
) -> SourceOriginalFourStageRngReachReceipt:
    guard=source_original_four_stage_guard_dispatch(
        reached_native_x87_status_ah=original_native_x87_ah_at_four_stage_guards)
    eaxs=original_native_668350_eax_at_each_reached_clamp
    owners=original_rng_owner_bytes_before_each_reached_call
    if type(eaxs) is not tuple or type(owners) is not tuple or len(eaxs)!=4 or len(owners)!=4:
        raise OriginalFourStageRngReachError('all four source-stage reached EAX and owner slots required')
    calls=[]
    results=[]
    for i,(skipped,eax,snapshot) in enumerate(zip(guard.native_stage_skipped,eaxs,owners)):
        if skipped:
            if eax is not None or snapshot is not None:
                raise OriginalFourStageRngReachError('skipped stage cannot have native 64D540 call receipt')
            calls.append(None)
            results.append(None)
            continue
        if type(eax) is not int or not 0<=eax<=0xffffffff or type(snapshot) is not bytes:
            raise OriginalFourStageRngReachError('reached original FISTP EAX and thread snapshot required')
        signed=eax if eax<0x80000000 else eax-0x100000000
        original_edi=max(1,signed)
        draw=source_original_66951c_then_64d540_scaled_draw(
            original_66d553_rng_owner_pointer=original_66d553_rng_owner_pointer,
            original_rng_owner_before_66951c=snapshot,
            original_64d540_reached_signed_argument=original_edi,
        )
        calls.append(_STAGE_CALLS[i]);results.append(draw)
    return SourceOriginalFourStageRngReachReceipt(
        guard.reached_native_ah_bytes,tuple(calls),tuple(results))
