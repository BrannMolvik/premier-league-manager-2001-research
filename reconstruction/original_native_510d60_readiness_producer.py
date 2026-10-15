"""Original LeagueMatch 510D60 +34 readiness gate and 511120 wrapper AL.

Original canonical PE source 510EE2/510EF2 independently invokes
407770(0) for first/second context+0 and +5B0 team, and only when
BOTH returned nonzero does source 510F06 enter mutable preparation.

After prep, 510FF2/511007 independently invokes 407770(1) on
first and second. Zero at early group returns AL0 at 511106;
zero in second group returns AL0 at 5110EE. Otherwise 5110E7
returns AL1 after other 4139E0/4037B0/408170 source effects.
The 511120 wrapper calls this 510D60 first and returns saved BL
unchanged after other kind-related writes. No native callbacks,
GameState effects or source original process are executed here.

This is ONLY branch reachability, not a shortcut to fabricate
post-callback match context, fixture eligibility, side owners
or original 512D80 fallback execution.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    source_original_leaguematch_process_owners_for_native_record,
    source_original_wrapped_prepare_511120_post_base,
)


class Original510D60ReadinessSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal510D60NativeReadiness:
    original_native_match_vtable: int
    original_first_team_pointer: int
    original_second_team_pointer: int
    reached_original_zero_arg_checks: tuple[bool, bool | None]
    reached_original_one_arg_checks: tuple[bool | None, bool | None]
    original_510d60_exit_va: int
    original_510d60_return_al_nonzero: bool
    original_false_exit_zeroes_context_5a4_b54: bool
    original_mutable_preparation_5111a0_reached: bool
    source_wrapped_511120_required: bool
    actual_407770_callbacks_executed: bool = False
    original_context_mutation_executed: bool = False
    native_match_readiness_executed: bool = False
    game_state_modified: bool = False


def source_original_510d60_actual_four_team_guard_results(
    *,
    original_native_match_record_before_v34: bytes,
    original_processing_context_after_native_team_getters: bytes,
    original_first_team_407770_zero_arg_eax_nonzero: bool,
    original_second_team_407770_zero_arg_eax_nonzero_if_reached: bool | None,
    original_first_team_407770_one_arg_eax_nonzero_if_reached: bool | None,
    original_second_team_407770_one_arg_eax_nonzero_if_reached: bool | None,
) -> SourceOriginal510D60NativeReadiness:
    try:
        owner=source_original_leaguematch_process_owners_for_native_record(
            original_match_record=original_native_match_record_before_v34)
    except OriginalLeagueMatchProcessOwnerError as exc:
        raise Original510D60ReadinessSourceError(str(exc)) from exc
    if owner.virtual34_prepare_va not in (0x510D60,0x511120):
        raise Original510D60ReadinessSourceError("unqualified original LeagueMatch native virtual34")
    ctx=original_processing_context_after_native_team_getters
    if type(ctx) is not bytes or len(ctx)<0x5b4:
        raise Original510D60ReadinessSourceError(
            "actual source original processing context team pointers required")
    first,second=unpack_from('<I',ctx,0)[0],unpack_from('<I',ctx,0x5b0)[0]
    if not first or not second or first==second:
        raise Original510D60ReadinessSourceError(
            "native 510D60 distinct nonnull team pointers required")
    checks=(original_first_team_407770_zero_arg_eax_nonzero,
            original_second_team_407770_zero_arg_eax_nonzero_if_reached,
            original_first_team_407770_one_arg_eax_nonzero_if_reached,
            original_second_team_407770_one_arg_eax_nonzero_if_reached)
    if type(checks[0]) is not bool:
        raise Original510D60ReadinessSourceError("first original 407770(0) AL source result required")
    if not checks[0]:
        if any(v is not None for v in checks[1:]):
            raise Original510D60ReadinessSourceError(
                "first zero-argument source FALSE branches before any other 407770 callback")
        return SourceOriginal510D60NativeReadiness(
            owner.source_vtable_va,first,second,(False,None),(None,None),
            0x511106,False,True,False,owner.source_wrapped_prepare)
    if type(checks[1]) is not bool:
        raise Original510D60ReadinessSourceError("second original 407770(0) reached result required")
    if not checks[1]:
        if any(v is not None for v in checks[2:]):
            raise Original510D60ReadinessSourceError(
                "second zero-argument source FALSE skips both one-argument checks")
        return SourceOriginal510D60NativeReadiness(
            owner.source_vtable_va,first,second,(True,False),(None,None),
            0x511106,False,True,False,owner.source_wrapped_prepare)
    if type(checks[2]) is not bool:
        raise Original510D60ReadinessSourceError("first source 407770(1) reached result required after 5111A0")
    if not checks[2]:
        if checks[3] is not None:
            raise Original510D60ReadinessSourceError(
                "original first source 407770(1) FALSE skips second")
        return SourceOriginal510D60NativeReadiness(
            owner.source_vtable_va,first,second,(True,True),(False,None),
            0x5110EE,False,True,True,owner.source_wrapped_prepare)
    if type(checks[3]) is not bool:
        raise Original510D60ReadinessSourceError(
            "second original source 407770(1) reached result required")
    return SourceOriginal510D60NativeReadiness(
        owner.source_vtable_va,first,second,(True,True),(True,checks[3]),
        0x5110E4 if checks[3] else 0x5110EE,
        bool(checks[3]),not checks[3],True,owner.source_wrapped_prepare)


@dataclass(frozen=True)
class SourceOriginal511120WrappedNativeReadiness:
    source_510d60_base_readiness: SourceOriginal510D60NativeReadiness
    source_511120_wrapper_projection: object
    source_final_v34_return_al_nonzero: bool
    actual_original_510d60_or_511120_executed: bool=False
    original_world_preparation_completed: bool=False


def source_original_511120_preserves_510d60_native_readiness(
    *,
    original_base_readiness:SourceOriginal510D60NativeReadiness,
    original_native_match_record_at_511120:bytes,
    original_reached_virtual28_kind:int,
    original_reached_513e80_result:int|None=None,
    original_reached_513e70_result:int|None=None,
)->SourceOriginal511120WrappedNativeReadiness:
    source=original_base_readiness
    if type(source) is not SourceOriginal510D60NativeReadiness or not source.source_wrapped_511120_required:
        raise Original510D60ReadinessSourceError(
            "source 511120 wrapper requires original wrapped 510D60 owner")
    try:
        projected=source_original_wrapped_prepare_511120_post_base(
            original_match_record=original_native_match_record_at_511120,
            original_base_510d60_al_nonzero=source.original_510d60_return_al_nonzero,
            original_native_kind_from_virtual28=original_reached_virtual28_kind,
            original_reached_513e80_result=original_reached_513e80_result,
            original_reached_513e70_result=original_reached_513e70_result,
        )
    except OriginalLeagueMatchProcessOwnerError as exc:
        raise Original510D60ReadinessSourceError(str(exc)) from exc
    if unpack_from('<I',original_native_match_record_at_511120,0)[0]!=source.original_native_match_vtable:
        raise Original510D60ReadinessSourceError(
            "original wrapper match object differs from source base-readiness owner")
    if projected.returned_al_nonzero!=source.original_510d60_return_al_nonzero:
        raise Original510D60ReadinessSourceError("native 511167 saved BL returned different source AL")
    return SourceOriginal511120WrappedNativeReadiness(
        source,projected,source.original_510d60_return_al_nonzero)
