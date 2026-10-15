"""Original 5DAA47/5DACC0 stage-two team-factor QWORD class selection.

Both original 5DAA0B first-side and 5DAC89 second-side scoring
phases take team+0x14 native category, multiply by 108,
add original 874BE0 global class records base and CALL 410FF0
with output from 4F3B10. Original source EAX0..5 dispatches
to native constants 0.9,0.8,0.7,0.6,0.5,0.5 and out-of-range
falls back 0.5. This factor feeds later 5DA250/FPU processing
but does not constitute actual goals, RNG or saved state.
"""
from dataclasses import dataclass
from struct import unpack_from,pack


class OriginalStageTwoFactorSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalStageTwoFactor:
    original_side: int
    original_team_pointer: int
    original_native_team_class14: int
    original_874be0_class_table_base: int
    original_410ff0_reached_class_pointer: int
    original_410ff0_return_eax: int
    original_qword_factor: bytes
    original_source_jump_va: int
    original_lookup_executed: bool = False
    original_5da250_calculator_executed: bool = False
    game_state_mutated: bool = False


def source_original_5daa47_or_5dacc0_team_factor(
    *,
    original_side:int,
    original_team_pointer:int,
    original_team_record:bytes,
    original_874be0_global_class_table_pointer:int,
    original_410ff0_reached_ecx_class_pointer:int,
    original_410ff0_return_eax:int,
) -> SourceOriginalStageTwoFactor:
    if type(original_side) is not int or original_side not in (1,2):
        raise OriginalStageTwoFactorSourceError("source original first/second phase required")
    team=original_team_record
    if (type(original_team_pointer) is not int or not 0<original_team_pointer<=0xffffffff
        or type(team) is not bytes or len(team)<0x18
        or type(original_874be0_global_class_table_pointer) is not int
        or not 0<original_874be0_global_class_table_pointer<=0xffffffff
        or type(original_410ff0_reached_ecx_class_pointer) is not int
        or not 0<original_410ff0_reached_ecx_class_pointer<=0xffffffff
        or type(original_410ff0_return_eax) is not int
        or not 0<=original_410ff0_return_eax<=0xffffffff):
        raise OriginalStageTwoFactorSourceError("actual original club/class/410FF0 native source receipts required")
    idx=unpack_from('<I',team,0x14)[0]
    p=original_874be0_global_class_table_pointer+idx*108
    if not 0<p<=0xffffffff or p!=original_410ff0_reached_ecx_class_pointer:
        raise OriginalStageTwoFactorSourceError("original 874BE0 +108*team14 class owner mismatch/overflow")
    enum=original_410ff0_return_eax
    result=(.9,.8,.7,.6,.5,.5)[enum] if enum<=5 else .5
    return SourceOriginalStageTwoFactor(
        original_side,original_team_pointer,idx,
        original_874be0_global_class_table_pointer,p,enum,
        pack('<d',result),
        (0x5daa53,0x5daa60,0x5daa75,0x5daa8b,0x5daa98,0x5daaad)[enum]
             if original_side==1 and enum<=5 else
        (0x5dacd1,0x5dacde,0x5dacf4,0x5dad09,0x5dad16,0x5dad2c)[enum]
             if original_side==2 and enum<=5 else
        0x5daac3 if original_side==1 else 0x5dad41,
    )
