"""Shipped original global DBRPlayer registry identity for FastView.

Original owner-approved footballmanager.exe SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
was statically inspected only. Native 0x416F60 initializes 0x875644
to the address of a 12-byte registry object 0x875638 with vtable
0x7BDA78 (first entry 0x416F90). Source 0x416F90 resolves an integer
player ID as 0x250 * id into object+8 contiguous player-record base.
It does not itself bounds-check. This module fails closed outside
source-supplied count and pointer boundaries; no native heap is read.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_fastview_two_sided_live_writeback import SourceFastViewTwoSideBlockState
from original_fastview_player_world_writeback import (
    SourceFastViewPlayerPreModalGlobals,
    SourceFastViewPlayerWriteIntent,
    source_fastview_original_player_field_pre_modal_capture_533bf0,
    source_fastview_native_postmodal_player_write_intents_533ca0,
)

SOURCE_FASTVIEW_PLAYER_REGISTRY_POINTER_GLOBAL_VA = 0x875644
SOURCE_FASTVIEW_PLAYER_REGISTRY_OBJECT_VA = 0x875638
SOURCE_FASTVIEW_PLAYER_REGISTRY_VTABLE_VA = 0x7BDA78
SOURCE_FASTVIEW_PLAYER_REGISTRY_CTOR_VA = 0x416F60
SOURCE_FASTVIEW_PLAYER_REGISTRY_GETTER_VA = 0x416F90
SOURCE_FASTVIEW_PLAYER_REGISTRY_SETUP_VA = 0x416FC0
SOURCE_FASTVIEW_PLAYER_RECORD_BYTES = 0x250
SOURCE_FASTVIEW_PLAYER_REGISTRY_COUNT_OFFSET = 4
SOURCE_FASTVIEW_PLAYER_REGISTRY_RECORD_POINTER_OFFSET = 8
SOURCE_FASTVIEW_PLAYER_SUBOBJECT_POINTER_OFFSET = 0x248
SOURCE_FASTVIEW_ORIGINAL_CLUB_PLAYER_IDS_OFFSET = 0x244
SOURCE_FASTVIEW_ORIGINAL_CLUB_PLAYER_COUNT_OFFSET = 0x294
SOURCE_FASTVIEW_ORIGINAL_CLUB_MIN_BYTES = 0x298
SOURCE_FASTVIEW_ORIGINAL_MATCH_SIDE_COUNT_OFFSETS = (0x5A4, 0xB54)


class SourceFastViewOriginalPlayerRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class SourceFastViewOriginalPlayerRegistry:
    original_native_registered_count_dword: int
    original_record_array_bytes: bytes

    def __post_init__(self):
        n=self.original_native_registered_count_dword
        records=self.original_record_array_bytes
        if (type(n) is not int or n<0 or n>0xFFFFFFFF or
                type(records) is not bytes or len(records)!=n*SOURCE_FASTVIEW_PLAYER_RECORD_BYTES):
            raise SourceFastViewOriginalPlayerRegistryError(
                "source player registry count and contiguous 592-byte records required")


@dataclass(frozen=True)
class SourceFastViewOriginalPlayerRegistryReference:
    side_index: int
    ordinal: int
    original_player_id_word: int
    source_player_record_592: bytes
    source_native_subobject_pointer_dword: int


def _resolve_original_registry_player(
    *, source_registry: SourceFastViewOriginalPlayerRegistry,
    side_index: int,
    ordinal: int,
    player_id_word: int,
) -> SourceFastViewOriginalPlayerRegistryReference:
    if type(source_registry) is not SourceFastViewOriginalPlayerRegistry:
        raise SourceFastViewOriginalPlayerRegistryError("original player registry required")
    if (type(side_index) is not int or side_index not in (0,1)
        or type(ordinal) is not int or not 0<=ordinal<=19
        or type(player_id_word) is not int or not 0<=player_id_word<=0xFFFF):
        raise SourceFastViewOriginalPlayerRegistryError("original side/ordinal/16-bit player id required")
    if player_id_word>=source_registry.original_native_registered_count_dword:
        raise SourceFastViewOriginalPlayerRegistryError(
            "original registry getter 0x416F90 would access outside registered count")
    offset=SOURCE_FASTVIEW_PLAYER_RECORD_BYTES*player_id_word
    record=source_registry.original_record_array_bytes[
        offset:offset+SOURCE_FASTVIEW_PLAYER_RECORD_BYTES]
    if len(record)!=SOURCE_FASTVIEW_PLAYER_RECORD_BYTES:
        raise SourceFastViewOriginalPlayerRegistryError("original native player record incomplete")
    sub=unpack_from("<I",record,SOURCE_FASTVIEW_PLAYER_SUBOBJECT_POINTER_OFFSET)[0]
    if sub==0:
        raise SourceFastViewOriginalPlayerRegistryError(
            "native +0x248 original subobject pointer is null, cannot dereference")
    return SourceFastViewOriginalPlayerRegistryReference(
        side_index,ordinal,player_id_word,record,sub)


def source_fastview_original_player_registry_get_416f90(
    *, source_registry: SourceFastViewOriginalPlayerRegistry, original_player_id_word: int,
) -> SourceFastViewOriginalPlayerRegistryReference:
    """Actual original vtable+0 player ID to 592-byte RECORD value, not heap deref."""
    return _resolve_original_registry_player(
        source_registry=source_registry,side_index=0,ordinal=0,
        player_id_word=original_player_id_word)


def source_fastview_original_pre_modal_registry_refs_533bf0(
    *, original_club_sides_before_modal: SourceFastViewTwoSideBlockState,
    source_registry: SourceFastViewOriginalPlayerRegistry,
) -> tuple[tuple[SourceFastViewOriginalPlayerRegistryReference, ...], ...]:
    """0x533BF0 reads original club+0x294 count, then WORD IDs at +0x244."""
    if type(original_club_sides_before_modal) is not SourceFastViewTwoSideBlockState:
        raise SourceFastViewOriginalPlayerRegistryError("two native original club sides required")
    out=[]
    for side,club in enumerate((
        original_club_sides_before_modal.first_side_bytes,
        original_club_sides_before_modal.second_side_bytes)):
        if len(club)<SOURCE_FASTVIEW_ORIGINAL_CLUB_MIN_BYTES:
            raise SourceFastViewOriginalPlayerRegistryError(
                "original source club record must contain count+0x294")
        count=unpack_from("<I",club,SOURCE_FASTVIEW_ORIGINAL_CLUB_PLAYER_COUNT_OFFSET)[0]
        if count>20:
            raise SourceFastViewOriginalPlayerRegistryError(
                "source original per-side attribute global has only 20 DWORD slots")
        rows=[]
        for ordinal in range(count):
            player_id=unpack_from("<H",club,
                    SOURCE_FASTVIEW_ORIGINAL_CLUB_PLAYER_IDS_OFFSET+2*ordinal)[0]
            rows.append(_resolve_original_registry_player(
                source_registry=source_registry,side_index=side,
                ordinal=ordinal,player_id_word=player_id))
        out.append(tuple(rows))
    return tuple(out)


def source_fastview_original_pre_modal_registry_capture_533bf0(
    *, original_club_sides_before_modal: SourceFastViewTwoSideBlockState,
    source_registry: SourceFastViewOriginalPlayerRegistry,
    original_subobject_bytes_by_native_pointer: dict[int, bytes],
    original_low5_globals_before: bytes,
    original_low4_globals_before: bytes,
) -> SourceFastViewPlayerPreModalGlobals:
    """Exact resolved IDs -> native +0x248 pointer -> source low5/low4 getter.

    External caller must supply real source-backed runtime pointer-to-subobject
    bytes, keyed by the EXACT DWORD pointer stored in each source record.
    A guessed world player ID/name cannot qualify a pointer; NULL or missing
    or malformed pointer target fails closed. This does not run native code.
    """
    if type(original_subobject_bytes_by_native_pointer) is not dict:
        raise SourceFastViewOriginalPlayerRegistryError(
            "original pointer-keyed subobject byte map required")
    for address,data in original_subobject_bytes_by_native_pointer.items():
        if (type(address) is not int or not 0<address<=0xFFFFFFFF or
                type(data) is not bytes or len(data)<5):
            raise SourceFastViewOriginalPlayerRegistryError(
                "authentic original 32-bit pointer and subobject getter bytes required")
    refs=source_fastview_original_pre_modal_registry_refs_533bf0(
        original_club_sides_before_modal=original_club_sides_before_modal,
        source_registry=source_registry)
    values=[]
    for side_rows in refs:
        one_side=[]
        for row in side_rows:
            found=original_subobject_bytes_by_native_pointer.get(
                row.source_native_subobject_pointer_dword)
            if found is None:
                raise SourceFastViewOriginalPlayerRegistryError(
                    "native original player subobject pointer target unresolved")
            one_side.append(found)
        values.append(tuple(one_side))
    return source_fastview_original_player_field_pre_modal_capture_533bf0(
        original_player_subobjects_by_side=(values[0],values[1]),
        original_low5_globals_before=original_low5_globals_before,
        original_low4_globals_before=original_low4_globals_before)


@dataclass(frozen=True)
class SourceFastViewOriginalPostModalResolvedPlayerIntent:
    source_native_player_intent: SourceFastViewPlayerWriteIntent
    source_player_record_592_before_write: bytes
    source_native_subobject_pointer_dword: int


def source_fastview_original_post_modal_registry_intents_533ca0(
    *, original_club_sides_after_modal: SourceFastViewTwoSideBlockState,
    original_match_object: bytes,
    source_registry: SourceFastViewOriginalPlayerRegistry,
    global_player_low5_dwords: bytes,
    global_player_low4_dwords: bytes,
) -> tuple[SourceFastViewOriginalPostModalResolvedPlayerIntent, ...]:
    """Source actual modal-edited ID→native record→subobject-pointer write list.

    Original 0x533CA0 uses match+0x5A4/+0xB54 counts (not club+0x294),
    copies 20 DWORD state blocks first, then visits the UPDATED 16-bit
    IDs from club+0x244. First11 vs remaining source methods and exact
    per-player global parameters come from existing proven 533CA0 intent.
    Immutable snapshots are NOT actual sequential native mutations; if
    a player ID repeats, the eventual runtime must process repeated effects
    in native ordinal order rather than applying all these snapshots at once.
    """
    if type(original_match_object) is not bytes or len(original_match_object)<0xB58:
        raise SourceFastViewOriginalPlayerRegistryError(
            "both original match-side DWORD roster counts required")
    native_counts=tuple(unpack_from("<I",original_match_object,o)[0]
                        for o in SOURCE_FASTVIEW_ORIGINAL_MATCH_SIDE_COUNT_OFFSETS)
    intents=source_fastview_native_postmodal_player_write_intents_533ca0(
        live_sides_after_modal=original_club_sides_after_modal,
        native_player_counts=native_counts,
        global_player_low5_dwords=global_player_low5_dwords,
        global_player_low4_dwords=global_player_low4_dwords)
    out=[]
    for intent in intents:
        ref=_resolve_original_registry_player(
            source_registry=source_registry,
            side_index=intent.side_index,ordinal=intent.player_ordinal,
            player_id_word=intent.source_player_id_word)
        out.append(SourceFastViewOriginalPostModalResolvedPlayerIntent(
            intent,ref.source_player_record_592,
            ref.source_native_subobject_pointer_dword))
    return tuple(out)
