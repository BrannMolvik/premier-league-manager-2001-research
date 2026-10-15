"""Source chain of actual 510D60 v34 FALSE -> 512D80 -> v38/v3c prefix.

Only accepts the exact ORIGINAL reached native 407770 readiness chain,
source TLS, all fallback special AL callbacks and ACTUAL post-fallback
match context; never treats a modern selected XI/fixture as native AL.
Wrapper 511120 returns original saved 510D60 AL unchanged.

All source outputs are read-only; no original executable, original
events, GameState simulation, score publishing or GUI interaction.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_native_510d60_readiness_producer import (
    Original510D60ReadinessSourceError,
    SourceOriginal510D60NativeReadiness,
    SourceOriginal511120WrappedNativeReadiness,
)
from original_match_512d80_fallback_scores import (
    SourceOriginal512D80ThroughV38V3CPrefix,
    source_original_5130c2_false_through_fallback_v38_v3c_prefix,
    Original512D80SourceError,
)


class Original510D60ToFallbackSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalReadinessFallbackV38V3CPrefix:
    original_base_510d60_readiness: SourceOriginal510D60NativeReadiness
    original_wrapped_511120_if_reached: SourceOriginal511120WrappedNativeReadiness | None
    source_original_512d80_fallback: SourceOriginal512D80ThroughV38V3CPrefix
    original_5130c2_branch_to_512d80_proven_by_source: bool = True
    original_match_calculation_executed: bool = False
    original_v3c_calendar_world_completed: bool = False
    original_live_game_state_modified: bool = False


def source_original_reached_v34_false_fallback_to_world_prefix(
    *,
    original_native_510d60_readiness: SourceOriginal510D60NativeReadiness,
    original_native_wrapped_511120_if_reached: SourceOriginal511120WrappedNativeReadiness | None,
    original_native_match_record_before_v38: bytes,
    original_original_context_before_512d80: bytes,
    original_processing_context_actual_after_512d80_callbacks: bytes,
    original_tls_record_source,
    original_first_team_407770_eax_nonzero_at_512db4: bool,
    original_second_team_407770_eax_nonzero_at_512dca: bool,
    original_four_special_gates,
) -> SourceOriginalReadinessFallbackV38V3CPrefix:
    ready=original_native_510d60_readiness
    wrapped=original_native_wrapped_511120_if_reached
    match=original_native_match_record_before_v38
    before=original_original_context_before_512d80
    if type(ready) is not SourceOriginal510D60NativeReadiness or (
        ready.original_510d60_return_al_nonzero or
        ready.original_510d60_exit_va not in (0x5110EE,0x511106)):
        raise Original510D60ToFallbackSourceError(
            "native 5130C2 FALSE path requires reached original 510D60 AL0 source")
    if type(match) is not bytes or len(match)<0x60 or unpack_from('<I',match,0)[0]!=ready.original_native_match_vtable:
        raise Original510D60ToFallbackSourceError("original LeagueMatch score record differs from v34 source owner")
    if type(before) is not bytes or len(before)<0x5b4:
        raise Original510D60ToFallbackSourceError("actual original 512D80 context required")
    if (unpack_from('<I',before,0)[0]!=ready.original_first_team_pointer or
        unpack_from('<I',before,0x5b0)[0]!=ready.original_second_team_pointer):
        raise Original510D60ToFallbackSourceError(
            "original source team selection changed between v34/512D80; unsupported caller owner")
    if ready.source_wrapped_511120_required:
        if (type(wrapped) is not SourceOriginal511120WrappedNativeReadiness or
            wrapped.source_510d60_base_readiness != ready or
            wrapped.source_final_v34_return_al_nonzero):
            raise Original510D60ToFallbackSourceError(
                "actual 511120 wrapped return must preserve original 510D60 AL0 source")
    elif wrapped is not None:
        raise Original510D60ToFallbackSourceError(
            "original direct 510D60 v34 does not execute 511120 wrapper")
    try:
        p=source_original_5130c2_false_through_fallback_v38_v3c_prefix(
            original_native_match_record_before_v38=match,
            original_processing_context_actual_after_512d80_callbacks=(
                original_processing_context_actual_after_512d80_callbacks),
            original_v34_at_5130c2_returned_false=False,
            original_context_pointer=0x9000,  # overwritten via explicit native context below
            original_context_record_before_512d80=before,
            original_tls_record_source=original_tls_record_source,
            original_first_team_407770_eax_nonzero=(
                original_first_team_407770_eax_nonzero_at_512db4),
            original_second_team_407770_eax_nonzero=(
                original_second_team_407770_eax_nonzero_at_512dca),
            original_four_special_gates=original_four_special_gates,
        )
    except Original512D80SourceError as exc:
        raise Original510D60ToFallbackSourceError(str(exc)) from exc
    return SourceOriginalReadinessFallbackV38V3CPrefix(ready,wrapped,p)
