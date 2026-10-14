"""Original native 0x4F2830 SideRef comparison after reached virtual getters.

Source is owner-authorized private footballmanager.exe 4,714,541 B,
SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Original executable inspected STATICALLY ONLY. This is source result evaluation
after actual SideRef vtable+0 getter calls; it does not emulate getter effects.

Original LeagueMatch vtable+0 0x510A80 invokes the comparison match's
vtable+4=0x510A40 for each original SideRef, and v+4 invokes
0x4F2830 against Side0 and Side1. Both native virtual getters can
resolve and mutate their SideRefs before comparing. Do not substitute
a node_kind, club name, symbolic fixture equality or guessed getter EAX.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


SOURCE_ORIGINAL_SIDE_COMPARATOR_VA=0x4F2830
SOURCE_ORIGINAL_LEAGUEMATCH_V0_VA=0x510A80
SOURCE_ORIGINAL_LEAGUEMATCH_V4_VA=0x510A40
SOURCE_ORIGINAL_SIDE_CACHE_PTR_OFFSET=0x04
SOURCE_ORIGINAL_SIDE_OWNER_PTR_OFFSET=0x08
SOURCE_ORIGINAL_SIDE_TYPE_WORD_OFFSET=0x0C
SOURCE_ORIGINAL_SIDE_SELECTOR_WORD_OFFSET=0x0E


class OriginalNativeSideRefCompareSourceError(ValueError):
    """Original SideRef post-virtual bytes/return value not source-qualified."""


@dataclass(frozen=True)
class OriginalNativeSideRefCompareReceipt:
    original_left_getter_eax: int
    original_right_getter_eax: int
    source_resolved_left_nonzero: bool
    source_right_getter_was_called: bool
    source_compared_resolved_cache_pointer: bool
    source_original_v4_or_v0_comparison_result: bool


def source_original_reached_side_ref_compare_4f2830(
    *,
    original_left_side_after_reached_getter: bytes,
    original_right_side_after_reached_getter: bytes,
    original_reached_left_virtual0_eax: int,
    original_reached_right_virtual0_eax: int,
) -> OriginalNativeSideRefCompareReceipt:
    """Source 0x4F2830 exact post-getter equality decision.

    Calls left SideRef virtual+0 first, then right SideRef virtual+0.
    If left getter EAX is nonzero, compares LEFT cached DWORD+0x04
    with RIGHT getter EAX (not LEFT getter EAX). If left getter is
    zero and right getter nonzero, immediately returns false.
    When both getters return zero, compares literal left/right
    native WORD+0x0C, DWORD+0x08, WORD+0x0E in this order.

    The source mutating getters may resolve competition selectors and
    write caches. This function MUST receive actual after-getter bytes
    and actual reached EAX values, never re-evaluate from a Python
    ClubRef label. Its return is not a live native virtual dispatch.
    """
    left=original_left_side_after_reached_getter
    right=original_right_side_after_reached_getter
    a=original_reached_left_virtual0_eax
    b=original_reached_right_virtual0_eax
    if (type(left) is not bytes or type(right) is not bytes or
        len(left)<0x10 or len(right)<0x10 or
        type(a) is not int or type(b) is not int or
        not 0<=a<=0xFFFFFFFF or not 0<=b<=0xFFFFFFFF):
        raise OriginalNativeSideRefCompareSourceError(
            "actual source SideRef post-getter records and returned DWORDs required")
    if a:
        equal=unpack_from("<I",left,SOURCE_ORIGINAL_SIDE_CACHE_PTR_OFFSET)[0]==b
        return OriginalNativeSideRefCompareReceipt(a,b,True,True,True,equal)
    if b:
        return OriginalNativeSideRefCompareReceipt(a,b,False,True,False,False)
    same_type=unpack_from("<H",left,SOURCE_ORIGINAL_SIDE_TYPE_WORD_OFFSET)[0]==unpack_from(
        "<H",right,SOURCE_ORIGINAL_SIDE_TYPE_WORD_OFFSET)[0]
    same_owner=unpack_from("<I",left,SOURCE_ORIGINAL_SIDE_OWNER_PTR_OFFSET)[0]==unpack_from(
        "<I",right,SOURCE_ORIGINAL_SIDE_OWNER_PTR_OFFSET)[0]
    same_selector=unpack_from("<H",left,SOURCE_ORIGINAL_SIDE_SELECTOR_WORD_OFFSET)[0]==unpack_from(
        "<H",right,SOURCE_ORIGINAL_SIDE_SELECTOR_WORD_OFFSET)[0]
    return OriginalNativeSideRefCompareReceipt(
        a,b,False,True,False,same_type and same_owner and same_selector)



@dataclass(frozen=True)
class OriginalNativeLeagueMatchSideConflictReceipt:
    source_original_method_va: int
    original_source_match_vtable_va: int
    source_first_side_comparison_returned_nonzero: bool
    source_second_side_comparison_was_reached: bool
    source_original_method_eax: int


def source_original_leaguematch_virtual04_510a40_from_reached_comparisons(
    *,
    original_native_match_record: bytes,
    original_first_reached_4f2830_receipt: OriginalNativeSideRefCompareReceipt,
    original_second_reached_4f2830_receipt: OriginalNativeSideRefCompareReceipt | None,
) -> OriginalNativeLeagueMatchSideConflictReceipt:
    """Source original v+4 0x510A40, two SideRef checks in exact order.

    Calls original 0x4F2830 on match Side0 (+0x14). If nonzero,
    v+4 returns one and SKIPS Side1 (+0x28). Otherwise invokes
    original 0x4F2830 on Side1 and returns its nonzero status
    normalized to one. This only combines real reached comparison
    receipts from *this* owner; it does not invoke SideRef getters.
    Original match v+0 0x510A80 dispatches this +0x04 method on
    the comparison owner for its two own SideRefs. No original
    vtable dispatch or match simulation occurs here.
    """
    from original_leaguematch_native_process_owners import (
        SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
    )
    rec=original_native_match_record
    first=original_first_reached_4f2830_receipt
    second=original_second_reached_4f2830_receipt
    if (type(rec) is not bytes or len(rec)<4 or
        unpack_from("<I",rec,0)[0] not in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS or
        type(first) is not OriginalNativeSideRefCompareReceipt):
        raise OriginalNativeSideRefCompareSourceError(
            "original native LeagueMatch v+4 owner and first reached Side comparison required")
    if first.source_original_v4_or_v0_comparison_result:
        if second is not None:
            raise OriginalNativeSideRefCompareSourceError(
                "original v+4 first-side true skips Side1 virtual comparison")
        return OriginalNativeLeagueMatchSideConflictReceipt(
            SOURCE_ORIGINAL_LEAGUEMATCH_V4_VA,unpack_from("<I",rec,0)[0],
            True,False,1)
    if type(second) is not OriginalNativeSideRefCompareReceipt:
        raise OriginalNativeSideRefCompareSourceError(
            "original v+4 first-side false must reach Side1 0x4F2830")
    return OriginalNativeLeagueMatchSideConflictReceipt(
        SOURCE_ORIGINAL_LEAGUEMATCH_V4_VA,unpack_from("<I",rec,0)[0],
        False,True,int(second.source_original_v4_or_v0_comparison_result))


def source_original_leaguematch_virtual00_510a80_from_reached_v4(
    *,
    original_native_match_record: bytes,
    original_first_reached_comparison_v4_eax: int,
    original_second_reached_comparison_v4_eax: int | None,
) -> int:
    """Original v+0 0x510A80 calls comparison-owner v+4 for Side0 then Side1.

    The source 0x510A90 tests the reached first returned DWORD; if
    nonzero, skips 0x510A9F entirely and returns one. Otherwise
    calls reached v+4 for the second SideRef, returns EAX=1 iff
    that second result was nonzero. Existing match pointers/Side
    getter effects must come from actual original source elsewhere.
    """
    from original_leaguematch_native_process_owners import (
        SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
    )
    r=original_native_match_record
    a=original_first_reached_comparison_v4_eax
    b=original_second_reached_comparison_v4_eax
    if (type(r) is not bytes or len(r)<4 or
        unpack_from("<I",r,0)[0] not in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS or
        type(a) is not int or not 0<=a<=0xFFFFFFFF):
        raise OriginalNativeSideRefCompareSourceError(
            "original source match v+0 and reached first v+4 EAX required")
    if a:
        if b is not None:
            raise OriginalNativeSideRefCompareSourceError(
                "source native v+0 first v+4 nonzero skips second v+4")
        return 1
    if type(b) is not int or not 0<=b<=0xFFFFFFFF:
        raise OriginalNativeSideRefCompareSourceError(
            "original source v+0 second reached comparison v+4 EAX required")
    return int(bool(b))
