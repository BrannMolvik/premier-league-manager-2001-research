"""Original source 0x4182F0/0x417340 starter human club and counter branch.

Owner-original SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
STATIC source read only. Real 0x417340 calls 0x417270 on player+0x10
to obtain a club pointer, then 0x4037B0 global human-registry membership.
This is distinct from 0x41EDF0's player+0x72 index into the SAME
global club array/fallback. Neither can be guessed from player name.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_fastview_native_player_registry import (
    SourceFastViewOriginalPlayerRegistryReference,
)
from original_fastview_native_player_roster_stage import (
    source_fastview_original_human_club_4037b0,
)
from original_fastview_player_world_writeback import (
    SourceFastViewStarterConditionalExternalResult,
    SourceFastViewPlayerDirectStatusStage,
    source_fastview_original_player_direct_status_stage_4182f0,
    source_fastview_original_starter_external_count_41edf0,
)

SOURCE_FASTVIEW_NATIVE_CLUB_POINTER_RESOLVER_VA = 0x417270
SOURCE_FASTVIEW_NATIVE_STARTER_HUMAN_PREDICATE_VA = 0x417340
SOURCE_FASTVIEW_NATIVE_HUMAN_CLUB_PREDICATE_VA = 0x4037B0
SOURCE_FASTVIEW_NATIVE_STARTER_EXTERNAL_COUNT_VA = 0x41EDF0
SOURCE_FASTVIEW_NATIVE_CLUB_REGISTRY_POINTER_GLOBAL_VA = 0x874B90
SOURCE_FASTVIEW_NATIVE_CLUB_FALLBACK_POINTER_GLOBAL_VA = 0x874B94
SOURCE_FASTVIEW_NATIVE_CLUB_STRIDE = 0x2A8
SOURCE_FASTVIEW_NATIVE_CLUB_ID_DWORD_OFFSET = 0x04
SOURCE_FASTVIEW_NATIVE_CLUB_COUNT_DWORD_OFFSET = 0x1A8


class SourceFastViewOriginalStarterWorldError(ValueError):
    """Original native source memory or pointer cannot be proven."""


@dataclass(frozen=True)
class SourceFastViewOriginalClubRegistry:
    """Actual original 0x874B90 contiguous clubs and 0x874B94 fallback."""
    original_live_club_array_bytes: bytes
    original_fallback_club_record_680: bytes

    def __post_init__(self):
        if (type(self.original_live_club_array_bytes) is not bytes
            or len(self.original_live_club_array_bytes) % SOURCE_FASTVIEW_NATIVE_CLUB_STRIDE
            or type(self.original_fallback_club_record_680) is not bytes
            or len(self.original_fallback_club_record_680) != SOURCE_FASTVIEW_NATIVE_CLUB_STRIDE):
            raise SourceFastViewOriginalStarterWorldError(
                "actual original global contiguous 680-byte clubs and fallback required")


@dataclass(frozen=True)
class SourceFastViewOriginalStarterHumanGate:
    original_player_id_word: int
    original_player_club_index10_signed: int
    original_player_count_index72_signed: int | None
    original_417340_human_owned: bool
    original_resolved_human_registry_ordinal: int | None
    original_player_direct_status: SourceFastViewPlayerDirectStatusStage
    source_external_result: SourceFastViewStarterConditionalExternalResult
    original_count_source_index: int | None
    original_count_source_before: int | None


def _signed_word(original_record: bytes, offset: int) -> int:
    v=unpack_from("<H",original_record,offset)[0]
    return v - 65536 if v&0x8000 else v


def _native_club_bytes(
    *, source_clubs: SourceFastViewOriginalClubRegistry,
    signed_index: int,
) -> bytes:
    if signed_index<0:
        return source_clubs.original_fallback_club_record_680
    array=source_clubs.original_live_club_array_bytes
    start=signed_index*SOURCE_FASTVIEW_NATIVE_CLUB_STRIDE
    if start+SOURCE_FASTVIEW_NATIVE_CLUB_STRIDE>len(array):
        raise SourceFastViewOriginalStarterWorldError(
            "native original club index beyond source-owned 0x874B90 records")
    return array[start:start+SOURCE_FASTVIEW_NATIVE_CLUB_STRIDE]


def source_fastview_original_starter_human_external_4182f0(
    *, original_player: SourceFastViewOriginalPlayerRegistryReference,
    original_clubs: SourceFastViewOriginalClubRegistry,
    original_human_registry_club_ids_in_link_order: tuple[int, ...],
) -> SourceFastViewOriginalStarterHumanGate:
    """Source-derived original starter status, 417340, conditional 41EDF0.

    4182F0 ORs status +0x14 bit0x10, clears bit0x20; resolves
    +0x174 pending flags (separate cache swap plan); calls 417340.
    417340 resolves original player WORD+0x10 via 417270 and delegates
    to 4037B0 native linked human registry membership. If HUMAN,
    41EDF0 is skipped; bit0x2000 also skips. Otherwise invokes
    41EDF0: when bit0x1000 CLEAR it does not read +0x72/count.
    When bit0x1000 SET, 41EDF0 clears it and selects a DIFFERENT
    signed player WORD+0x72 index for native club count DWORD+0x1A8.
    The original JLE checks a SIGNED positive count (not !=0).
    Returns values and intended external counter mutation, NEVER
    mutates an actual player/club/registry or advances an original match.
    """
    if type(original_player) is not SourceFastViewOriginalPlayerRegistryReference:
        raise SourceFastViewOriginalStarterWorldError(
            "authenticated original native player registry reference required")
    record=original_player.source_player_record_592
    if type(record) is not bytes or len(record)!=0x250:
        raise SourceFastViewOriginalStarterWorldError(
            "actual original 592-byte player record required")
    if type(original_clubs) is not SourceFastViewOriginalClubRegistry:
        raise SourceFastViewOriginalStarterWorldError(
            "original source club registry required")
    initial_status=unpack_from("<I",record,0x14)[0]
    initial_flags=unpack_from("<I",record,0x174)[0]
    direct=source_fastview_original_player_direct_status_stage_4182f0(
        source_flag14_dword=initial_status,source_flag174_dword=initial_flags,
        starting_eleven=True)
    owner10=_signed_word(record,0x10)
    club10=_native_club_bytes(source_clubs=original_clubs,signed_index=owner10)
    club_id=unpack_from("<I",club10,SOURCE_FASTVIEW_NATIVE_CLUB_ID_DWORD_OFFSET)[0]
    matching=source_fastview_original_human_club_4037b0(
        original_club_reference_dword=club_id,
        original_human_registry_club_ids_in_link_order=original_human_registry_club_ids_in_link_order)
    human=matching is not None
    if human or direct.native_flag14_after & 0x2000:
        external=SourceFastViewStarterConditionalExternalResult(
            direct.native_flag14_after,False,False,None,None)
        return SourceFastViewOriginalStarterHumanGate(
            original_player.original_player_id_word,owner10,None,human,
            matching,direct,external,None,None)
    if not (direct.native_flag14_after & 0x1000):
        external=SourceFastViewStarterConditionalExternalResult(
            direct.native_flag14_after,True,False,None,None)
        return SourceFastViewOriginalStarterHumanGate(
            original_player.original_player_id_word,owner10,None,human,
            matching,direct,external,None,None)
    owner72=_signed_word(record,0x72)
    selected=_native_club_bytes(source_clubs=original_clubs,signed_index=owner72)
    native_count=unpack_from("<I",selected,SOURCE_FASTVIEW_NATIVE_CLUB_COUNT_DWORD_OFFSET)[0]
    external=source_fastview_original_starter_external_count_41edf0(
        native_flag14_after_direct=direct.native_flag14_after,
        original_417340_result_byte=0,
        original_signed_club_index_word=owner72,
        native_selected_owner_count_dword=native_count)
    return SourceFastViewOriginalStarterHumanGate(
        original_player.original_player_id_word,owner10,owner72,human,
        matching,direct,external,owner72,native_count)
