"""Original LeagueMatch vtable owners and reached native +0x34 preparation.

Source: owner-private SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
original footballmanager.exe, STATIC disassembly only. This module DOES NOT
execute source callbacks or invoke an original process. The actual 0x510D60
preparation effects, subsequent match simulation, GUI and world writes remain
unintegrated. The supported seven LeagueMatch classes were independently
authenticated against the original .rdata, not inferred from fixture kinds.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


class OriginalLeagueMatchProcessOwnerError(ValueError):
    """Original vtable, reached result or owner pointer is not qualified."""


SOURCE_LEAGUEMATCH_EXECUTE_V10_VA = 0x513010
SOURCE_LEAGUEMATCH_GENERIC_PREPARE_V34_VA = 0x510D60
SOURCE_LEAGUEMATCH_WRAPPED_PREPARE_V34_VA = 0x511120
SOURCE_LEAGUEMATCH_WRAPPED_SPECIAL_KIND = 5
SOURCE_LEAGUEMATCH_SPECIAL_OUTPUT_VAS = (0x513E80, 0x513E70)

# vtable: (virtual+0x28, +0x30, +0x34, +0x38, +0x3C, +0x44)
# These are native original method ADDRESSES; do not call them in Python.
SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS = {
    0x7C4C24: (0x651E20, 0x651980, 0x510D60, 0x5112A0, 0x5132E0, 0x513F70),
    0x7C4CE4: (0x668766, 0x651980, 0x510D60, 0x5112A0, 0x511370, 0x513F70),
    0x7C9D9C: (0x6CE1E0, 0x5112C0, 0x511120, 0x5136C0, 0x5136E0, 0x514000),
    0x7C9E14: (0x650250, 0x651980, 0x510D60, 0x5112A0, 0x511370, 0x513F70),
    0x7C9E80: (0x6CE1F0, 0x5112C0, 0x511120, 0x5136C0, 0x5136E0, 0x514000),
    0x7C9EF8: (0x6CECB0, 0x5112C0, 0x511120, 0x5136C0, 0x5136E0, 0x514000),
    0x7C9F70: (0x650010, 0x5112C0, 0x511120, 0x5136C0, 0x5136E0, 0x514000),
}


@dataclass(frozen=True)
class OriginalLeagueMatchNativeProcessOwners:
    source_vtable_va: int
    virtual28_kind_va: int
    virtual30_owner_va: int
    virtual34_prepare_va: int
    virtual38_cleanup_va: int
    virtual3c_cleanup_va: int
    virtual44_owner_va: int

    @property
    def source_wrapped_prepare(self) -> bool:
        return self.virtual34_prepare_va == SOURCE_LEAGUEMATCH_WRAPPED_PREPARE_V34_VA


@dataclass(frozen=True)
class OriginalLeagueMatchWrappedPrepareReceipt:
    """Bounded ORIGINAL +0x34 wrapper writes AFTER real 0x510D60 execution.

    Do not interpret the return as a completed match. Original 0x511120
    calls 0x510D60 FIRST, then virtual+0x28, and may add two +0xD2x
    slots regardless of the earlier return. When 0x510D60 returned AL
    nonzero, it also copies match+0x50 into context+0xD24.
    """
    original_base_510d60_al_nonzero: bool
    original_native_kind_from_virtual28: int
    original_written_context_dwords: tuple[tuple[int, int], ...]
    returned_al_nonzero: bool


def source_original_leaguematch_process_owners_for_native_record(
    *, original_match_record: bytes,
) -> OriginalLeagueMatchNativeProcessOwners:
    """Require actual original vtable DWORD; node_kind strings cannot qualify."""
    if type(original_match_record) is not bytes or len(original_match_record) < 4:
        raise OriginalLeagueMatchProcessOwnerError("original native match vtable DWORD required")
    vtable = unpack_from("<I", original_match_record)[0]
    owners = SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.get(vtable)
    if owners is None:
        raise OriginalLeagueMatchProcessOwnerError(
            "original LeagueMatch process owner unknown; refuse invented dispatch")
    return OriginalLeagueMatchNativeProcessOwners(vtable, *owners)


def source_original_wrapped_prepare_511120_post_base(
    *, original_match_record: bytes,
    original_base_510d60_al_nonzero: bool,
    original_native_kind_from_virtual28: int,
    original_reached_513e80_result: int | None = None,
    original_reached_513e70_result: int | None = None,
) -> OriginalLeagueMatchWrappedPrepareReceipt:
    """Original 0x511120 additional source writes only, not 0x510D60 itself.

    The source vtable+0x34 MUST be this wrapper. Caller supplies actual
    native 0x510D60 return and actual vtable+0x28 result; no assumption
    about source side getters or node kinds is made.
    """
    owner = source_original_leaguematch_process_owners_for_native_record(
        original_match_record=original_match_record)
    if not owner.source_wrapped_prepare or len(original_match_record) < 0x58:
        raise OriginalLeagueMatchProcessOwnerError(
            "original wrapper match record through +0x54 and actual wrapper vtable required")
    if type(original_base_510d60_al_nonzero) is not bool:
        raise OriginalLeagueMatchProcessOwnerError("reached original 0x510D60 AL result required")
    kind = original_native_kind_from_virtual28
    if type(kind) is not int or not 0 <= kind <= 0xFFFFFFFF:
        raise OriginalLeagueMatchProcessOwnerError("actual vtable+0x28 DWORD result required")
    values = (original_reached_513e80_result, original_reached_513e70_result)
    if kind == SOURCE_LEAGUEMATCH_WRAPPED_SPECIAL_KIND:
        if not unpack_from("<I", original_match_record, 0x54)[0]:
            raise OriginalLeagueMatchProcessOwnerError(
                "source special native match+0x54 owner missing")
        if any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in values):
            raise OriginalLeagueMatchProcessOwnerError(
                "actual reached source 0x513E80 and 0x513E70 DWORD results required")
        writes = ((0xD28, values[0]), (0xD2C, values[1]))
    else:
        if any(v is not None for v in values):
            raise OriginalLeagueMatchProcessOwnerError(
                "source 0x513E80/0x513E70 skipped when vtable+0x28 is not 5")
        writes = ()
    if original_base_510d60_al_nonzero:
        writes += ((0xD24, unpack_from("<I", original_match_record, 0x50)[0]),)
    return OriginalLeagueMatchWrappedPrepareReceipt(
        original_base_510d60_al_nonzero, kind, writes,
        original_base_510d60_al_nonzero)




@dataclass(frozen=True)
class SourceOriginal510D60ReadinessGateReturn:
    """ONLY original v+34 four reached 407770 gate branches and final AL.

    The game executes many intermediate native callbacks, not reproduced here.
    Boolean inputs are independently observed original callback outcomes, not
    a new eligibility algorithm or input from a reconstructed fixture.
    """
    original_match_vtable: int
    reached_gate_addresses: tuple[int, ...]
    reached_gate_nonzero: tuple[bool, ...]
    original_base_510d60_al_nonzero: bool
    original_base_exit_va: int
    source_zeroed_context_dword_offsets: tuple[int, ...]
    original_511120_wrapper_post_base: OriginalLeagueMatchWrappedPrepareReceipt | None
    native_original_407770_callbacks_executed: bool = False
    original_510d60_all_other_callbacks_executed: bool = False
    original_complete_v34_context_mutations_proven: bool = False
    live_game_state_modified: bool = False


def source_original_510d60_four_readiness_gate_return(
    *, original_match_record: bytes,
    original_first_team_407770_zero_nonzero: bool,
    original_second_team_407770_zero_nonzero_if_reached: bool | None,
    original_first_team_407770_one_nonzero_if_reached: bool | None,
    original_second_team_407770_one_nonzero_if_reached: bool | None,
    original_reached_513e80_result_if_wrapped_kind5: int | None = None,
    original_reached_513e70_result_if_wrapped_kind5: int | None = None,
) -> SourceOriginal510D60ReadinessGateReturn:
    """Static original 510EE5 -> 510EF9 -> 510FFA -> 51100F gate order.

    Source 510D60 returns AL=0 on the *first* reached zero EAX (and
    writes zero to context+5A4/+B54); after four nonzero gates it returns
    AL=1. First pair uses 407770(0), second pair uses 407770(1).
    Native callbacks between pairs and their context/world effects remain
    unresolved and MUST NOT be inferred from this branch projection.
    Wrapped 511120 independently executes 513E80/513E70 when kind=5
    irrespective of base AL, then copies match+50 to context+D24 only
    when base AL=1. Neither source path advances any portable match.
    """
    owner = source_original_leaguematch_process_owners_for_native_record(
        original_match_record=original_match_record)
    kind = SOURCE_LEAGUEMATCH_LITERAL_V28_KINDS.get(owner.virtual28_kind_va)
    if kind is None:
        raise OriginalLeagueMatchProcessOwnerError(
            "v28 diagnostic 668766 unknown: cannot source-project 511120")
    flags = (
        original_first_team_407770_zero_nonzero,
        original_second_team_407770_zero_nonzero_if_reached,
        original_first_team_407770_one_nonzero_if_reached,
        original_second_team_407770_one_nonzero_if_reached,
    )
    addresses = (0x510EE5, 0x510EF9, 0x510FFA, 0x51100F)
    reached = []
    for index, flag in enumerate(flags):
        if index > 0 and len(reached) != index:
            if any(x is not None for x in flags[index:]):
                raise OriginalLeagueMatchProcessOwnerError(
                    "original 407770 gate supplied after unreachable early return")
            break
        if type(flag) is not bool:
            raise OriginalLeagueMatchProcessOwnerError(
                "actual reached original 407770 EAX nonzero boolean required")
        reached.append(flag)
        if not flag:
            if any(x is not None for x in flags[index+1:]):
                raise OriginalLeagueMatchProcessOwnerError(
                    "unreached original 407770 outcomes cannot be supplied")
            break
    if not reached:
        raise OriginalLeagueMatchProcessOwnerError("original first gate not reached")
    success = len(reached) == 4 and all(reached)
    # The two failure epilogues independently zero the same slots.
    epilogue = 0x5110E7 if success else (
        0x511115 if len(reached) <= 2 else 0x5110FF)
    zeroed = () if success else (0x5A4, 0xB54)
    wrapper = None
    special = (original_reached_513e80_result_if_wrapped_kind5,
               original_reached_513e70_result_if_wrapped_kind5)
    if owner.source_wrapped_prepare:
        wrapper = source_original_wrapped_prepare_511120_post_base(
            original_match_record=original_match_record,
            original_base_510d60_al_nonzero=success,
            original_native_kind_from_virtual28=kind,
            original_reached_513e80_result=special[0],
            original_reached_513e70_result=special[1],
        )
    elif any(x is not None for x in special):
        raise OriginalLeagueMatchProcessOwnerError(
            "direct 510D60 has no reached 511120 513E8x calls")
    return SourceOriginal510D60ReadinessGateReturn(
        owner.source_vtable_va,
        addresses[:len(reached)], tuple(reached), success,
        epilogue, zeroed, wrapper,
    )


SOURCE_LEAGUEMATCH_PRIMARY_EVENT_V30_VA = 0x651980
SOURCE_LEAGUEMATCH_CONDITIONAL_SECONDARY_V30_VA = 0x5112C0
SOURCE_LEAGUEMATCH_EVENT_BIT2 = 0x04


def source_original_leaguematch_native_virtual30_low_byte(
    *, original_match_record: bytes,
    original_reached_virtual28_kind: int | None = None,
) -> int:
    """Source exact original vtable+0x30 return AL for a native match.

    0x651980 unconditionally XOR AL,AL and never calls virtual+0x28.
    0x5112C0 DOES call virtual+0x28, then returns AL=1 iff kind==2
    AND original match byte+0x44 bit2 is clear. Neither function proves
    that a particular reconstructed schedule record is an original
    runtime match owner passed into 0x4F3B50.
    """
    owners = source_original_leaguematch_process_owners_for_native_record(
        original_match_record=original_match_record)
    v30 = owners.virtual30_owner_va
    if v30 == SOURCE_LEAGUEMATCH_PRIMARY_EVENT_V30_VA:
        if original_reached_virtual28_kind is not None:
            raise OriginalLeagueMatchProcessOwnerError(
                "source 0x651980 skips virtual+0x28; extra reached result invalid")
        return 0
    if v30 != SOURCE_LEAGUEMATCH_CONDITIONAL_SECONDARY_V30_VA:
        raise OriginalLeagueMatchProcessOwnerError(
            "original native vtable+0x30 owner not source-qualified")
    if type(original_match_record) is not bytes or len(original_match_record)<0x48:
        raise OriginalLeagueMatchProcessOwnerError("source native match+0x44 flag DWORD required")
    kind=original_reached_virtual28_kind
    if type(kind) is not int or not 0<=kind<=0xFFFFFFFF:
        raise OriginalLeagueMatchProcessOwnerError(
            "original vtable+0x28 reached actual kind required")
    flags44=unpack_from("<I",original_match_record,0x44)[0]
    return int(kind==2 and not flags44 & SOURCE_LEAGUEMATCH_EVENT_BIT2)


def source_original_match_owned_event_collection_4f3b50(
    *, original_match_record: bytes,
    original_reached_virtual28_kind: int | None = None,
) -> int:
    """Qualified LeagueMatch owner only: +0x30 AL -> 0x4F3B50 collection.

    The result must not be installed on every PrimaryScheduleShadowEntry:
    matching an ORIGINAL runtime LeagueMatch vtable and its reached kind
    are prerequisites. Other native owner classes need separate proof.
    """
    from original_schedule_event_native_constructor import (
        source_original_event_collection_selector_4f3b50,
    )
    al=source_original_leaguematch_native_virtual30_low_byte(
        original_match_record=original_match_record,
        original_reached_virtual28_kind=original_reached_virtual28_kind)
    return source_original_event_collection_selector_4f3b50(
        original_owner_virtual30_result_eax=al)


# Six original LeagueMatch virtual+0x28 functions return literal MOV EAX,N; RET.
# Original 0x668766 instead calls the diagnostic 0x66ABCF with 0x19.
# Its returned match kind is NOT established, so fail closed on that owner.
SOURCE_LEAGUEMATCH_LITERAL_V28_KINDS = {
    0x651E20: 1, 0x6CE1E0: 2, 0x650250: 6,
    0x6CE1F0: 3, 0x6CECB0: 4, 0x650010: 5,
}


@dataclass(frozen=True)
class SourceOriginal510D60CounterWrites:
    """Only reached 510DC2..510E64 native-context literal writes."""

    original_match_vtable: int
    original_virtual28_literal_kind: int
    original_flags44: int
    original_context_d0c: int
    original_context_d10: int
    original_context_d14: int
    original_context_d18: int
    original_base_510d60_executed: bool = False
    live_game_state_updated: bool = False

    @property
    def source_context_stores(self) -> tuple[tuple[int, int], ...]:
        return ((0xD0C, self.original_context_d0c),
                (0xD10, self.original_context_d10),
                (0xD14, self.original_context_d14),
                (0xD18, self.original_context_d18),
                (0xD24, 0xFFFFFFFF),
                (0xD28, 0xFFFFFFFF),
                (0xD2C, 0xFFFFFFFF))


def source_original_510d60_two_event_counter_writes(
    *, original_match_record: bytes,
) -> SourceOriginal510D60CounterWrites:
    """Read-only native 510D60 v34 literal context writes, not a match.

    The original twice calls vtable+0x28 at 510DBF/510DEC. Six
    source-authenticated v28 functions are constant returns, therefore
    both original kind results are identical and known for these six.
    Class 7C4CE4's v28=668766 diagnostic is deliberately unresolved.
    This routine does not run original other context writes, RNG,
    callback return AL, GUI or GameState persistence.
    """
    owner = source_original_leaguematch_process_owners_for_native_record(
        original_match_record=original_match_record)
    if type(original_match_record) is not bytes or len(original_match_record) < 0x48:
        raise OriginalLeagueMatchProcessOwnerError(
            "reached original match record +44 flags through+47 required")
    kind = SOURCE_LEAGUEMATCH_LITERAL_V28_KINDS.get(owner.virtual28_kind_va)
    if kind is None:
        raise OriginalLeagueMatchProcessOwnerError(
            "original v28 kind is non-literal diagnostic; source result unresolved")
    flags = unpack_from("<I", original_match_record, 0x44)[0]
    first = 0 if kind == 2 and not flags & 0x04 else (flags >> 1) & 1
    second = 1 if kind == 3 and not flags & 0x04 else (flags >> 2) & 1
    # 510E1A third v+28 call sets context+D14 iff kind==5;
    # 510E2B sets context+D18 from match+44 bit3. Original
    # 510E55..510E64 sets three DWORD sentinels, later wrapped
    # class 511120 may overwrite some after base 510D60 returns.
    return SourceOriginal510D60CounterWrites(
        owner.source_vtable_va, kind, flags, first, second,
        int(kind == 5), (flags >> 3) & 1,
    )
