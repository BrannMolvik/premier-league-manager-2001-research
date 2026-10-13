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
