"""Original source-only fourth-stage 5DB348 EDI bound -> 64D540 RNG join.

Intermediate x87 5DA250, user modifier, 668350 EAX are REQUIRED native
observations, not calculated or assumed. No original native RNG call or
live GameState effects are performed by this source projection.
"""
from dataclasses import dataclass
from original_match_stage4_coefficient_player_source import (
    SourceOriginalStageFourCoefficientReceipt,
    source_original_stage_four_coefficient_player,
)
from original_native_64d540_rand_step import (
    SourceOriginal64D540DrawReceipt,
    source_original_66951c_then_64d540_scaled_draw,
)

class OriginalStageFourRngSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginalStageFourRngJoinReceipt:
    original_stage4_coefficient_player: SourceOriginalStageFourCoefficientReceipt
    original_reached_668350_eax_at_5db346: int
    original_edi_signed_clamped_at_5db35b: int
    original_source_rng_step: SourceOriginal64D540DrawReceipt
    original_native_5da250_executed: bool = False
    live_game_state_updated: bool = False


def source_original_fourth_stage_to_rand(
    *, original_reached_stage4_coefficient_input: dict,
    original_reached_668350_eax_at_5db346: int,
    original_66951c_rng_owner_pointer: int,
    original_66951c_rng_owner_before: bytes,
) -> SourceOriginalStageFourRngJoinReceipt:
    if type(original_reached_stage4_coefficient_input) is not dict:
        raise OriginalStageFourRngSourceError('source 5DB185 input required')
    eax=original_reached_668350_eax_at_5db346
    if type(eax) is not int or not 0 <= eax <= 0xffffffff:
        raise OriginalStageFourRngSourceError('actual 5DB346 native EAX required')
    # CMP EDI, 1; JGE 5DB352 is a signed comparison; else MOV EDI,1.
    signed=eax if eax < 0x80000000 else eax-0x100000000
    edi=max(signed,1)
    coeff=source_original_stage_four_coefficient_player(**original_reached_stage4_coefficient_input)
    rng=source_original_66951c_then_64d540_scaled_draw(
        original_66d553_rng_owner_pointer=original_66951c_rng_owner_pointer,
        original_rng_owner_before_66951c=original_66951c_rng_owner_before,
        original_64d540_reached_signed_argument=edi,
    )
    return SourceOriginalStageFourRngJoinReceipt(coeff,eax,edi,rng)
