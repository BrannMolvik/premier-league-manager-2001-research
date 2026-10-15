"""Original 5DA9AD first scoring stage's context+0xD88 write.

Original first scoring stage 5DA995 -> 5E43B0 -> 5E48D0 yields
QWORD at stack+0x38. Source 5DA9B3 then selects 4037B0
managed-club membership. For managed club it reads actual original
matched registered user+694 pointer and +0x0C DWORD, writes the
integer unmodified to match context+0xD88, and independently stores
double (that integer minus original 5E48D0 output) at stack+0x30.
For unmanaged club it calls 668350 with 5E48D0 double in x87 ST0
to truncate toward zero, and writes resulting int32 to +0xD88.
This stage is not original final match score, no native callbacks
run, and no GameState is written by source projection.
"""
from dataclasses import dataclass
from math import isfinite,trunc
from struct import pack,unpack_from

from original_match_40cbc0_5e48d0_b_join import OriginalScoredStageFreshCallbackSource
from original_match_5da2f0_team_inputs import OriginalMatch4037B0TeamOwner


class OriginalFirstStageD88SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original5DA9ADD88SourceProjection:
    original_native_context_pointer: int
    original_stage_a_source_double: float
    original_native_4037b0_human: bool
    original_context_d88_signed_int: int
    original_human_difference_stack30_qword: bytes | None
    original_d88_store_va: int
    original_store_executed: bool = False
    game_state_modified: bool = False


def source_original_5da9ad_first_stage_d88(
    *,
    original_stage1_5e48d0:OriginalScoredStageFreshCallbackSource,
    original_4037b0_registered_club:OriginalMatch4037B0TeamOwner,
    original_context_pointer_from_ebp0c:int,
    original_context_record_before_d88:bytes,
    original_actual_registered_user_pointer_if_human:int|None,
    original_reached_user_694_owner_pointer_if_human:int|None,
    original_reached_user_694_owner_record_if_human:bytes|None,
    original_reached_user_record_if_human:bytes|None,
)->Original5DA9ADD88SourceProjection:
    p=original_context_pointer_from_ebp0c
    if type(p) is not int or not 0<p<=0xffffffff:
        raise OriginalFirstStageD88SourceError("source original [EBP+C] match context pointer required")
    if (type(original_context_record_before_d88) is not bytes or
        len(original_context_record_before_d88)<0xd8c):
        raise OriginalFirstStageD88SourceError("original match context through +D88 required")
    stage=original_stage1_5e48d0
    if (type(stage) is not OriginalScoredStageFreshCallbackSource or
        stage.original_stage!=1 or not stage.original_human_gate==(
            original_4037b0_registered_club.source_4037b0_return_al!=0)
        or stage.direct_native_b_store_site_if_reached!=0x5da9ad or
        stage.original_5e43b0_construct_site!=0x5da995 or
        type(stage.original_5e48d0_qword) is not bytes or
        len(stage.original_5e48d0_qword)!=8 or
        type(original_4037b0_registered_club) is not OriginalMatch4037B0TeamOwner):
        raise OriginalFirstStageD88SourceError("source qualified original 5DA9AD first scoring callback required")
    score=unpack_from("<d",stage.original_5e48d0_qword)[0]
    if not isfinite(score) or abs(score)>=2**31:
        raise OriginalFirstStageD88SourceError(
            "native 668350 int32 conversion or finite human subtraction not source-safe")
    human=stage.original_human_gate
    if human:
        uid=original_actual_registered_user_pointer_if_human
        owner=original_reached_user_694_owner_pointer_if_human
        user=original_reached_user_record_if_human
        body=original_reached_user_694_owner_record_if_human
        if (type(uid) is not int or uid!=original_4037b0_registered_club.source_matching_registered_user_pointer
            or type(owner) is not int or not 0<owner<=0xffffffff
            or type(user) is not bytes or len(user)<0x698
            or unpack_from("<I",user,0x694)[0]!=owner
            or type(body) is not bytes or len(body)<0x10):
            raise OriginalFirstStageD88SourceError("actual original 403850 registered user+694 owner+0C required")
        raw=unpack_from("<i",body,0xc)[0]
        diff=pack("<d",float(raw)-score)
        return Original5DA9ADD88SourceProjection(p,score,True,raw,diff,0x5da9e4)
    if any(x is not None for x in (
        original_actual_registered_user_pointer_if_human,
        original_reached_user_694_owner_pointer_if_human,
        original_reached_user_694_owner_record_if_human,
        original_reached_user_record_if_human,
    )):
        raise OriginalFirstStageD88SourceError("native unmanaged 5DA9EC bypasses manager+694 fields")
    return Original5DA9ADD88SourceProjection(p,score,False,trunc(score),None,0x5daa05)
