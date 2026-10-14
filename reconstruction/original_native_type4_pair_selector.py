"""Bounded original 0x4F2A78 -> 0x4FAF70 Type4 SideRef pair selection.

Owner-authorized original footballmanager.exe, 4,714,541 bytes,
SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
STATIC x86 source only. Never runs the original, resolves a club pointer, or
assumes this source branch has already mutated its original League owner.

This gives the *source SideRef pointer selected* by the original pair table,
NOT the final resolved club pointer or original 0x510320 registration effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

SOURCE_ORIGINAL_TYPE4_GETTER_BRANCH = 0x4F2A78
SOURCE_ORIGINAL_TYPE4_PREPARE = 0x4FAEA0
SOURCE_ORIGINAL_TYPE4_PAIR_LOOKUP = 0x4FAF70
SOURCE_ORIGINAL_TYPE4_LEFT_ARRAY_OFFSET = 0x74
SOURCE_ORIGINAL_TYPE4_RIGHT_ARRAY_OFFSET = 0x7C
SOURCE_ORIGINAL_TYPE4_SIDEREF_VTABLE = 0x7C4D50


class OriginalType4PairSourceError(ValueError):
    """Original Type4 native owner, reached gate or post-gate pairs unknown."""


@dataclass(frozen=True)
class OriginalType4PairSelectionReceipt:
    source_original_gate_4faea0_al: int
    source_original_pair_family_offset: int | None
    source_original_pair_index: int | None
    source_original_pair_member_index: int | None
    source_original_selected_sidereference_pointer: int | None


@dataclass(frozen=True)
class OriginalType4OwnerGateReceipt:
    source_half_team_count_trunc_toward_zero: int
    source_gate_threshold_half_times_half_minus_one: int
    source_owner_raw_68: int
    source_owner_raw_78: int | None
    source_4faea0_al_if_no_mutating_callback: int | None
    source_requires_mutating_split_array_initialization: bool


def source_original_type4_owner_read_only_gate_4faea0(
    *, original_native_league_owner_record_before_gate: bytes,
) -> OriginalType4OwnerGateReceipt:
    """Source original 0x4FAEA0 entry and conditional initialization gate.

    The original obtains signed owner+0x3C team count, divides by two
    rounded toward zero, then checks signed (half-1)*half >= owner+0x68.
    The owner+0x68 field is intentionally *not* named completed games,
    remaining fixtures or a ranking: only the reached comparison is proven.

    If the condition is false, original returns AL0 without accessing
    owner+0x78/array bytes. If true and owner+0x78 is already nonzero,
    source returns AL1 without mutating initializer calls. Otherwise it
    walks owner+0x6C/+0x70, calls 0x4F40B0, populates +0x74/+0x7C,
    and invokes original 0x617500 twice. That branch remains UNRESOLVED;
    no AL1 is emitted by this helper without executing its state effects.
    """
    r=original_native_league_owner_record_before_gate
    if type(r) is not bytes or len(r)<0x84:
        raise OriginalType4PairSourceError(
            "actual original League owner record through +0x80 required")
    teams=unpack_from("<i",r,0x3C)[0]
    raw68=unpack_from("<i",r,0x68)[0]
    # The actual shipped Scottish split uses a positive, bounded team count.
    # Native signed multiply overflow and nonsensical owner states need a
    # separate source contract, not Python unbounded-integer approximations.
    if teams<4 or teams>65535:
        raise OriginalType4PairSourceError(
            "source native signed team count outside qualified positive owner range")
    half=teams//2
    threshold=half*(half-1)
    if threshold>0x7FFFFFFF:
        raise OriginalType4PairSourceError(
            "original signed gate arithmetic overflows qualified source domain")
    if threshold<raw68:
        return OriginalType4OwnerGateReceipt(
            half,threshold,raw68,None,0,False)
    raw78=unpack_from("<i",r,0x78)[0]
    if raw78!=0:
        return OriginalType4OwnerGateReceipt(
            half,threshold,raw68,raw78,1,False)
    return OriginalType4OwnerGateReceipt(
        half,threshold,raw68,raw78,None,True)



@dataclass(frozen=True)
class OriginalType4PreSortPairsReceipt:
    source_original_half_team_count: int
    source_original_base_pair_count: int
    source_original_top_pairs_74_before_617500: tuple[tuple[int, int], ...]
    source_original_bottom_pairs_7c_before_617500: tuple[tuple[int, int], ...]
    source_original_cross_half_pair_count: int
    source_original_617500_sort_and_side_effects_unresolved: bool


def source_original_type4_classify_reached_pairs_before_617500_4faea0(
    *,
    original_native_league_owner_record_before_gate: bytes,
    original_source_6c_pairs_before_gate: tuple[tuple[int, int], ...],
    original_reached_4f40b0_rank_pair_eax_in_iteration_order: tuple[tuple[int, int], ...],
) -> OriginalType4PreSortPairsReceipt:
    """Read-only classification into the source +0x74 and +0x7C buckets.

    Original 0x4FAEDB..0x4FAF4C calls 0x4F40B0 TWICE per original
    owner+0x6C pair; it records +0x74 when *both* returned signed ranks
    are less than floor(team_count/2), +0x7C when both are >= it,
    and appends neither when the pair crosses halves. Input ranks
    MUST be the actual reached original 0x4F40B0 results. That getter
    itself invokes 0x4F4940 and searches a mutable ranked owner array.

    The classification below is before the two original 0x617500 calls
    that can re-order/change these arrays. This function returns only
    the source PRE-SORT pointer sequence, NOT an authenticated final
    current team matchup or live native SideRef. It may not execute
    0x4FAEA0 or replace original registration/world mutations.
    """
    owner=original_native_league_owner_record_before_gate
    pairs=original_source_6c_pairs_before_gate
    ranks=original_reached_4f40b0_rank_pair_eax_in_iteration_order
    readiness=source_original_type4_owner_read_only_gate_4faea0(
        original_native_league_owner_record_before_gate=owner)
    if not readiness.source_requires_mutating_split_array_initialization:
        raise OriginalType4PairSourceError(
            "source 4FAEA0 cannot enter pair classification at this owner stage")
    n=unpack_from("<i",owner,0x70)[0]
    owner_source_pair_ptr=unpack_from("<I",owner,0x6C)[0]
    if (n<0 or n>0x10000 or type(pairs) is not tuple or type(ranks) is not tuple or
        len(pairs)!=n or len(ranks)!=n or (n>0 and owner_source_pair_ptr==0)):
        raise OriginalType4PairSourceError(
            "actual original owner+6C/+70 pairs and reached 4F40B0 rank calls required")
    for pair,rank_pair in zip(pairs,ranks):
        if (type(pair) is not tuple or len(pair)!=2 or
            any(type(p) is not int or not 0<p<=0xFFFFFFFF for p in pair) or
            type(rank_pair) is not tuple or len(rank_pair)!=2 or
            any(type(index) is not int or not -0x80000000<=index<=0x7FFFFFFF
                for index in rank_pair)):
            raise OriginalType4PairSourceError(
                "actual native pair SideRef pointers and reached signed ranking outputs required")
    threshold=readiness.source_half_team_count_trunc_toward_zero
    top=[]
    bottom=[]
    cross=0
    for pair,(first_rank,second_rank) in zip(pairs,ranks):
        first_bottom=first_rank>=threshold
        second_bottom=second_rank>=threshold
        if first_bottom and second_bottom:
            bottom.append(pair)
        elif not first_bottom and not second_bottom:
            top.append(pair)
        else:
            cross+=1
    return OriginalType4PreSortPairsReceipt(
        threshold,n,tuple(top),tuple(bottom),cross,True)


def source_original_type4_pair_selection_4f2a78_4faf70(
    *,
    original_embedded_side_ref_before_getter: bytes,
    original_reached_4faea0_al: int,
    original_owner_pairs_74_after_gate: tuple[tuple[int, int], ...] | None,
    original_owner_pairs_7c_after_gate: tuple[tuple[int, int], ...] | None,
) -> OriginalType4PairSelectionReceipt:
    """Select the exact source pointer after the actual 0x4FAEA0 gate.

    Original 0x4F2A78 calls 0x4FAEA0 on native SideRef+8 owner; when
    AL==0 it returns without calling 0x4FAF70. When AL!=0 it splits
    unsigned SideRef selector WORD+0x0E into:
      first argument selector&1: 1 uses owner+0x74, 0 uses +0x7C;
      second argument (selector>>1)&1: 1 chooses pair element0, 0 element1;
      third argument selector>>2: zero-based pair index.
    Original 0x4FAF70 does not itself check bounds. This *safe replay*
    rejects invalid index/source pointers rather than dereferencing them.
    Actual original 0x4FAEA0 may CREATE or MODIFY owner arrays; the
    caller must supply real post-gate arrays, not Python fixture guesses.
    No original 0x4FAF70 call, derived SideRef getter or cache mutation
    occurs in this function.
    """
    r = original_embedded_side_ref_before_getter
    g = original_reached_4faea0_al
    if (type(r) is not bytes or len(r) < 0x14 or
        unpack_from("<I", r, 0)[0] != SOURCE_ORIGINAL_TYPE4_SIDEREF_VTABLE or
        unpack_from("<I", r, 4)[0] != 0 or
        unpack_from("<I", r, 8)[0] == 0 or
        unpack_from("<H", r, 0x0C)[0] != 4 or
        type(g) is not int or g not in (0, 1)):
        raise OriginalType4PairSourceError(
            "original uncached embedded type4 SideRef, owner and reached 4FAEA0 AL required")
    if g == 0:
        # Short-circuit before touching the tables or original selector.
        return OriginalType4PairSelectionReceipt(0, None, None, None, None)
    arrays = (original_owner_pairs_74_after_gate, original_owner_pairs_7c_after_gate)
    if any(type(rows) is not tuple or
           any(type(pair) is not tuple or len(pair) != 2 or
               any(type(p) is not int or not 0 < p <= 0xFFFFFFFF for p in pair)
               for pair in rows)
           for rows in arrays):
        raise OriginalType4PairSourceError(
            "original League owner post-4FAEA0 pair arrays required, with real SideRef pointers")
    selector = unpack_from("<H", r, 0x0E)[0]
    family = SOURCE_ORIGINAL_TYPE4_LEFT_ARRAY_OFFSET if selector & 1 else SOURCE_ORIGINAL_TYPE4_RIGHT_ARRAY_OFFSET
    index = selector >> 2
    member = 0 if (selector >> 1) & 1 else 1
    rows = arrays[0] if selector & 1 else arrays[1]
    if index >= len(rows):
        raise OriginalType4PairSourceError(
            "original post-gate pair index unavailable; cannot infer native out-of-bounds data")
    return OriginalType4PairSelectionReceipt(
        1, family, index, member, rows[index][member])
