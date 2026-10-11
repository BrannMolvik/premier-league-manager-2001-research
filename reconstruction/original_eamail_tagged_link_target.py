"""Source-bounded original EAMPlayer typed P/C link INDEX lookup.

Canonical original PE SHA-256 833bf95e...b7cc3:
- 0x471C60 receives eCText child ID2 selector, delegates record+0x1C
  typed descriptor to 0x5CF7B0, then uses typed flag and returned index
  to route player 0x605DC0 or club 0x604900.
- 0x5CF7B0 reads CP1252 P/C selector, native descriptor three DWORDs,
  outputs kind1 player (P, slot+4), kind0 club (C). For C type1,
  descriptor+4 indexes original table 0x875628 stride64 and field+0x24;
  C type2/type17 uses descriptor+8; other types use descriptor+4.
  Unsupported selector returns -1; parent also suppresses -1 result.

Only *raw source integer indices* are resolved here. A caller must prove
the original native record's three descriptor DWORDs and the original
table lookup before calling. No player/club object, screen, hit rectangle,
mouseover or detail return can be inferred from the index alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


NATIVE_EAM_LINK_RESOLVER_VA = 0x5CF7B0
NATIVE_EAM_ROW_LINK_DISPATCH_VA = 0x471C60
NATIVE_EAM_PLAYER_DETAILS_VA = 0x605DC0
NATIVE_EAM_CLUB_DETAILS_VA = 0x604900
NATIVE_EAM_ASSOC_TABLE_GLOBAL_VA = 0x875628
NATIVE_EAM_ASSOC_TABLE_STRIDE = 64
NATIVE_EAM_ASSOC_TABLE_CLUB_WORD_OFFSET = 0x24


class OriginalEAMLinkSourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalEAMRawLinkTarget:
    source_kind: str  # player | club, no fabricated modern target object
    original_signed_index: int
    native_resolver_va: int = NATIVE_EAM_LINK_RESOLVER_VA
    native_detail_gui_verified: bool = False


def _native_i32(number: int, label: str) -> int:
    if type(number) is not int or not -(1 << 31) <= number < (1 << 31):
        raise OriginalEAMLinkSourceError(label + " must be source-signed DWORD")
    return number


def original_eam_typed_link_index(
    source_selector_byte: int,
    *,
    verified_descriptor_type: int | None = None,
    verified_descriptor_word4: int | None = None,
    verified_descriptor_word8: int | None = None,
    qualified_original_assoc_table_club_at_index: Callable[[int], int] | None = None,
) -> OriginalEAMRawLinkTarget | None:
    """Exact static 0x5CF7B0 typed descriptor branch; no GUI action.

    A type1 C reference depends on a distinct live native DBR table.
    Missing its *original* index resolver is a qualification error, never
    the user's currently selected club or a convenience fallback.
    """
    if type(source_selector_byte) is not int or not 0 <= source_selector_byte <= 255:
        raise OriginalEAMLinkSourceError("Native inline selector must be a byte")
    if source_selector_byte not in (ord("P"), ord("C")):
        return None  # original 0x5CF7BF branches before reading descriptor
    if source_selector_byte == ord("P"):
        # P reads descriptor+4 only; demand neither type nor +8.
        link_kind = "player"
        index = _native_i32(verified_descriptor_word4, "Original descriptor +4")
    else:
        kind = _native_i32(verified_descriptor_type, "Original descriptor kind")
        link_kind = "club"
        if kind == 1:
            ref4 = _native_i32(verified_descriptor_word4, "Original descriptor +4")
            if ref4 < 0 or qualified_original_assoc_table_club_at_index is None:
                raise OriginalEAMLinkSourceError(
                    "Original type1 club reference needs qualified 0x875628 association table"
                )
            if not callable(qualified_original_assoc_table_club_at_index):
                raise OriginalEAMLinkSourceError("Native association lookup must be callable")
            index = _native_i32(
                qualified_original_assoc_table_club_at_index(ref4),
                "Original association table club +0x24",
            )
        elif kind in (2, 17):
            index = _native_i32(verified_descriptor_word8, "Original descriptor +8")
        else:
            index = _native_i32(verified_descriptor_word4, "Original descriptor +4")
    # Parent 0x471CB3 explicitly drops native -1 result. A different
    # negative club result can still select original fallback 0x874B94,
    # but this layer deliberately never constructs that source club object.
    if index == -1:
        return None
    return OriginalEAMRawLinkTarget(link_kind, index)
