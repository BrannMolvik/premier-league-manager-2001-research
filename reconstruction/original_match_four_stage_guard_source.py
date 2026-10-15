"""Original 5DA981..5DB110 four independently optional native match stages.

Each reached original FNSTSW AH bit0x40 determines source branch. This does
NOT classify an input score as mathematical zero, execute x87/5DA250/64D540,
or update any GameState. A nonzero branch rejoins the next guard after its
side-effecting scoring work, which is deliberately not represented here.
"""
from dataclasses import dataclass

class OriginalMatchStageGuardError(ValueError):
    pass

_GUARD_BRANCHES=(
    (0x5da981,0x5dac05,0x5da987),
    (0x5dac14,0x5dae80,0x5dac1a),
    (0x5dae92,0x5db101,0x5dae98),
    (0x5db110,0x5db37c,0x5db116),
)

@dataclass(frozen=True)
class SourceOriginalFourStageGuardReceipt:
    reached_native_ah_bytes: tuple[int,int,int,int]
    native_stage_entries: tuple[int,int,int,int]
    native_zero_status_destinations: tuple[int,int,int,int]
    native_stage_skipped: tuple[bool,bool,bool,bool]
    common_after_stages: int = 0x5db37c
    actual_original_stage_executed: bool = False
    live_game_state_updated: bool = False

def source_original_four_stage_guard_dispatch(*, reached_native_x87_status_ah: tuple[int,int,int,int]) -> SourceOriginalFourStageGuardReceipt:
    if (type(reached_native_x87_status_ah) is not tuple or len(reached_native_x87_status_ah)!=4 or
            any(type(x) is not int or not 0<=x<=255 for x in reached_native_x87_status_ah)):
        raise OriginalMatchStageGuardError("four actual native x87 FNSTSW AH source bytes required")
    skip=tuple(bool(x&0x40) for x in reached_native_x87_status_ah)
    selected=tuple(skipped if s else enter
                   for s,(_,skipped,enter) in zip(skip,_GUARD_BRANCHES))
    return SourceOriginalFourStageGuardReceipt(
        reached_native_x87_status_ah,selected,
        tuple(row[1] for row in _GUARD_BRANCHES),skip)
