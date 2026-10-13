"""Original procedural League +0x3C emitter/Scottish final-cycle hook.

SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
original footballmanager.exe, STATIC private source analysis only.
Original 0x6172C3..0x617313 invokes League vtable+0x3C. Generic
0x616FC0 allocates 0x50, calls 0x5104F0, resolves owner 0x4F3B50
and inserts native match via 0x615950. Scottish 0x6170A0 may hold
the final partial cycle as pair data or delegate to 0x616FC0.

Receipts describe reached native operations and the date-array index,
not actual allocated event object, date array contents, serial/registry,
original +8/+0x44 flags, v+0x10 simulation or GUI acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_native_schedule_producer_source import (
    OriginalNativeScheduleConstructorEvidence,
    source_original_schedule_constructor_for_verified_producer,
)


SOURCE_ORIGINAL_PROCEDURAL_MATCH_GENERATOR_VA = 0x6170F0
SOURCE_ORIGINAL_PROCEDURAL_EMITTER_VA = 0x616FC0
SOURCE_ORIGINAL_PROCEDURAL_VIRTUAL_3C_CALL_VA = 0x617310
SOURCE_ORIGINAL_SCOTTISH_OVERRIDE_VA = 0x6170A0
SOURCE_ORIGINAL_SCOTTISH_FINAL_CYCLE_BRANCH_VA = 0x6170AF
SOURCE_ORIGINAL_MATCH_ALLOC_SIZE = 0x50
SOURCE_ORIGINAL_MATCH_CONSTRUCTOR_VA = 0x5104F0
SOURCE_ORIGINAL_MATCH_CONSTRUCTOR_CALLSITE_VA = 0x617047
SOURCE_ORIGINAL_MATCH_DATE_OWNER_VA = 0x4F3B50
SOURCE_ORIGINAL_MATCH_DATE_INSERT_VA = 0x615950
SOURCE_ORIGINAL_MATCH_DATE_INDEX_OFFSET = 0x60
SOURCE_ORIGINAL_SIGNED_INDEX_MAX = 0x7FFFFFFF


class OriginalProceduralEventEmitterSourceError(ValueError):
    """Unreached/malformed original procedural emitter input."""


@dataclass(frozen=True)
class OriginalProceduralEventEmitReceipt:
    original_date_array_index: int | None
    original_native_constructor_class: OriginalNativeScheduleConstructorEvidence | None
    source_defers_scottish_final_cycle_to_pair_buffer: bool
    source_match_constructor_called: bool
    source_date_owner_lookup_va: int | None
    source_date_bucket_insertion_va: int | None


def source_original_procedural_event_emitter_616fc0(
    *,
    original_team_count_plus_3c: int,
    original_cycle_index: int,
    original_pair_round_index: int,
    original_scottish_override_active: bool,
    original_scottish_616f40_reported_cycle_count: int | None = None,
) -> OriginalProceduralEventEmitReceipt:
    """Source 0x6170A0 final-cycle holdback or original 0x616FC0 emit.

    0x6170A0 reads original 0x616F40 result, compares given cycle index
    with reported cycle_count-1. If equal, it adds the pair to
    League+0x6C buffer and does NOT invoke 0x616FC0. Otherwise it
    delegates; ordinary League virtual+0x3C calls 0x616FC0 directly.
    Actual emitted native date-array index, 0x617057..0x61706E, is
       (original League+0x3C team_count - 1) * cycle + pair_round.
    Date array League+0x60 is 8-byte records, but no date is inferred
    here without actual original source contents.
    """
    if type(original_team_count_plus_3c) is not int or not 2<=original_team_count_plus_3c<=0x7FFFFFFF:
        raise OriginalProceduralEventEmitterSourceError(
            "original team count is required for source League date offset")
    for idx in (original_cycle_index,original_pair_round_index):
        if type(idx) is not int or not 0<=idx<=0x7FFFFFFF:
            raise OriginalProceduralEventEmitterSourceError(
                "source nonnegative 32-bit original cycle/round index required")
    if original_pair_round_index>=original_team_count_plus_3c-1:
        raise OriginalProceduralEventEmitterSourceError(
            "original schedule-round index exceeds one round-robin cycle")
    if type(original_scottish_override_active) is not bool:
        raise OriginalProceduralEventEmitterSourceError(
            "source League virtual+0x3C dispatch owner must be explicit")
    if original_scottish_override_active:
        count=original_scottish_616f40_reported_cycle_count
        if type(count) is not int or not 1<=count<=0x7FFFFFFF:
            raise OriginalProceduralEventEmitterSourceError(
                "actual source Scottish 0x616F40 cycle count required")
        holdback=(original_cycle_index==count-1)
    else:
        if original_scottish_616f40_reported_cycle_count is not None:
            raise OriginalProceduralEventEmitterSourceError(
                "original ordinary League does not call Scottish 0x6170A0 override")
        holdback=False
    if holdback:
        return OriginalProceduralEventEmitReceipt(None,None,True,False,None,None)
    index=(original_team_count_plus_3c-1)*original_cycle_index+original_pair_round_index
    if index>SOURCE_ORIGINAL_SIGNED_INDEX_MAX:
        raise OriginalProceduralEventEmitterSourceError(
            "original 32-bit signed date-array index overflow is unqualified")
    clazz=source_original_schedule_constructor_for_verified_producer(
        source_emission_kind="league_match",
        original_source_producer_va=SOURCE_ORIGINAL_PROCEDURAL_EMITTER_VA,
        original_native_constructor_callsite_va=SOURCE_ORIGINAL_MATCH_CONSTRUCTOR_CALLSITE_VA)
    return OriginalProceduralEventEmitReceipt(
        index,clazz,False,True,
        SOURCE_ORIGINAL_MATCH_DATE_OWNER_VA,SOURCE_ORIGINAL_MATCH_DATE_INSERT_VA)
