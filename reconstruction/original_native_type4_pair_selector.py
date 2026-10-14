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
