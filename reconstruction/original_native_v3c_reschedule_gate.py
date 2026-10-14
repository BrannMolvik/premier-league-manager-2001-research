"""Source-qualified original LeagueMatch v3C reschedule gate and first calendar route.

Exact verified original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
STATIC only. These are read-only receipts of 0x511429..0x511456 and
0x5127A0..0x51283D, NOT reconstructed event generation or match completion.

Original v3C 0x511370 sets bit0 at +44, then always calls 0x5112E0.
If that first competition-owned virtual +0x30 returned AL nonzero,
original may invoke source mutating side/team callbacks *before* 0x511429.
At 0x511429, match +44 bit5 skips reschedule; otherwise 0x5112E0
is called AGAIN, and AL==0 enters 0x5127A0. Regardless of gate,
0x512710 and 0x512230 run, followed by extensive other world effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    source_original_leaguematch_process_owners_for_native_record,
)

SOURCE_COMMON_V3C_VA = 0x511370
SOURCE_COMPETITION_V30_BRIDGE_VA = 0x5112E0
SOURCE_V3C_RESCHEDULE_GATE_VA = 0x511429
SOURCE_NATIVE_RESCHEDULE_VA = 0x5127A0
SOURCE_NATIVE_RESCHEDULE_CALENDAR_SELECT_VA = 0x510300
SOURCE_NATIVE_DATE_EVENT_SEARCH_VA = 0x615D10
SOURCE_FOLLOWING_V3C_CALLBACK_VAS = (0x512710, 0x512230)
SOURCE_MATCH_BIT0_STARTED = 1
SOURCE_MATCH_BIT5_SKIP_RESCHEDULE = 0x20
SOURCE_MATCH_COMPETITION_OWNER_PTR_OFFSET = 0x4C
SOURCE_PRIMARY_EVENT_REGISTRY_VA = 0x947AF0
SOURCE_SECONDARY_EVENT_REGISTRY_VA = 0x947AD8
SOURCE_GLOBAL_DATE_INDEX_VA = 0x9847FC


class OriginalV3CRescheduleGateError(ValueError):
    """Original match pointer, reached virtual result or world input missing."""


@dataclass(frozen=True)
class OriginalV3CRescheduleGateReceipt:
    original_source_vtable_va: int
    source_v3c_owner_va: int
    original_match_at_511429: bytes
    original_competition_owner_pointer: int
    first_5112e0_return_al: int
    source_prior_side_world_branch_may_have_executed: bool
    native_flag_bit5_skipped_second_call: bool
    second_5112e0_return_al: int | None
    original_5127a0_called: bool
    subsequent_source_callbacks: tuple[int, ...] = SOURCE_FOLLOWING_V3C_CALLBACK_VAS
    prior_world_effects_proven: bool = False
    native_match_completion_proven: bool = False


@dataclass(frozen=True)
class OriginalV3CFirstCalendarLookupReceipt:
    original_source_vtable_va: int
    original_date_global_index: int
    first_requested_date_index: int
    native_calendar_registry_va: int
    native_processing_owner_first_pointer: int
    native_615d10_argument_3: int = 1
    native_615d10_reached: bool = True
    native_615d10_return_value_known: bool = False
    event_inserted_or_rescheduled_proven: bool = False


def _reached_competition_virtual30_eax(value: int | None, name: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise OriginalV3CRescheduleGateError(
            f"actual reached {name} EAX uint32 required")
    return value & 0xFF


def source_original_v3c_511429_reschedule_gate(
    *,
    original_native_match_at_gate: bytes,
    original_first_5112e0_virtual30_eax: int,
    original_second_5112e0_virtual30_eax: int | None = None,
) -> OriginalV3CRescheduleGateReceipt:
    """Determine original 0x511429 bit5/competition-v30 conditional ONLY.

    Inputs must come from actual original reachability at the 0x511429
    boundary AFTER first 0x5112E0 call, optional side getter and world
    callbacks, and first v3C bit0 store. Source 0x5112E0 dereferences the
    *competition owner* at match+4C, calls its virtual+30 and ANDs EAX FF.
    It is NOT LeagueMatch's own virtual+30 or symbolic fixture_kind.
    """
    record = original_native_match_at_gate
    if type(record) is not bytes or len(record) < 0x50:
        raise OriginalV3CRescheduleGateError(
            "original match bytes through competition pointer +4C required")
    try:
        owners = source_original_leaguematch_process_owners_for_native_record(
            original_match_record=record)
    except OriginalLeagueMatchProcessOwnerError as exc:
        raise OriginalV3CRescheduleGateError(str(exc)) from exc
    if owners.virtual3c_cleanup_va not in (0x511370, 0x5132E0, 0x5136E0):
        raise OriginalV3CRescheduleGateError(
            "native original LeagueMatch v3C must reach common 0x511370")

    flags = unpack_from("<I", record, 0x44)[0]
    if not flags & SOURCE_MATCH_BIT0_STARTED:
        raise OriginalV3CRescheduleGateError(
            "original 0x511381 first flag bit0 store must precede this gate")
    competition_ptr = unpack_from(
        "<I", record, SOURCE_MATCH_COMPETITION_OWNER_PTR_OFFSET)[0]
    if not competition_ptr:
        raise OriginalV3CRescheduleGateError(
            "reached native competition owner at match+4C must be nonnull")
    first = _reached_competition_virtual30_eax(
        original_first_5112e0_virtual30_eax, "initial 0x5112E0")
    if flags & SOURCE_MATCH_BIT5_SKIP_RESCHEDULE:
        if original_second_5112e0_virtual30_eax is not None:
            raise OriginalV3CRescheduleGateError(
                "native bit5 skips second competition virtual30; extra result invalid")
        second = None
        reschedule = False
    else:
        second = _reached_competition_virtual30_eax(
            original_second_5112e0_virtual30_eax, "second 0x5112E0")
        reschedule = second == 0

    return OriginalV3CRescheduleGateReceipt(
        original_source_vtable_va=owners.source_vtable_va,
        source_v3c_owner_va=owners.virtual3c_cleanup_va,
        original_match_at_511429=record,
        original_competition_owner_pointer=competition_ptr,
        first_5112e0_return_al=first,
        source_prior_side_world_branch_may_have_executed=bool(first),
        native_flag_bit5_skipped_second_call=bool(
            flags & SOURCE_MATCH_BIT5_SKIP_RESCHEDULE),
        second_5112e0_return_al=second,
        original_5127a0_called=reschedule,
    )


def source_original_5127a0_first_calendar_request(
    *, original_gate: OriginalV3CRescheduleGateReceipt,
    original_processing_owner_at_reschedule: bytes,
    original_reached_global_date_index_9847fc: int,
) -> OriginalV3CFirstCalendarLookupReceipt:
    """One exact first-pass 0x5127A0 -> 0x510300 -> 0x615D10 call receipt.

    First of two source passes, EBX=0, original 0x5127B7 reads DWORD
    [processing owner+0] as argument 1. 0x512822 reads global date
    0x9847FC and passes (date + 1) as argument 2, literal 1 as
    argument 3, and 0x510300 chooses registry from match+0C bit0.
    The subsequent 0x615D10 and 0x512841+ effects are NOT modeled.
    """
    if not isinstance(original_gate, OriginalV3CRescheduleGateReceipt):
        raise OriginalV3CRescheduleGateError(
            "reached source v3C reschedule gate receipt required")
    if not original_gate.original_5127a0_called:
        raise OriginalV3CRescheduleGateError(
            "native 0x5127A0 was skipped; cannot invent calendar call")
    record = original_gate.original_match_at_511429
    if type(record) is not bytes or len(record) < 0x50:
        raise OriginalV3CRescheduleGateError("original reached match owner missing")
    source_owner = original_processing_owner_at_reschedule
    if type(source_owner) is not bytes or len(source_owner) < 4:
        raise OriginalV3CRescheduleGateError(
            "actual native processing owner initial DWORD required")
    first_ptr = unpack_from("<I", source_owner)[0]
    if not first_ptr:
        raise OriginalV3CRescheduleGateError(
            "original processing owner first team/event pointer must be nonnull")
    date = original_reached_global_date_index_9847fc
    if type(date) is not int or not 0 <= date <= 0xFFFFFFFF:
        raise OriginalV3CRescheduleGateError(
            "actual original global date-index DWORD required")
    match_type_bit0 = unpack_from("<I", record, 0x0C)[0] & 1
    registry = (SOURCE_PRIMARY_EVENT_REGISTRY_VA if match_type_bit0
                else SOURCE_SECONDARY_EVENT_REGISTRY_VA)
    return OriginalV3CFirstCalendarLookupReceipt(
        original_source_vtable_va=original_gate.original_source_vtable_va,
        original_date_global_index=date,
        first_requested_date_index=(date + 1) & 0xFFFFFFFF,
        native_calendar_registry_va=registry,
        native_processing_owner_first_pointer=first_ptr,
    )
