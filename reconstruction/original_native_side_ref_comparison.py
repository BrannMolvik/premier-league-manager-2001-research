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
