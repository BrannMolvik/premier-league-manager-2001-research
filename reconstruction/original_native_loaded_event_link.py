"""Source original 0x510900 post-construction loaded-event reference restoration.

Private SHA256 source 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Only original 0x616100 → 0x6163E0 → 0x616500 native save loader
families (0..6) and reached common +0x24 load callbacks qualified.
No native execution, parser, runtime state mutation or live progress.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

from original_native_serialized_event_loader import (
    SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH,
)


class OriginalLoadedEventLinkSourceError(ValueError):
    """Native post-load reference link is not source-qualified."""


SOURCE_ORIGINAL_EVENT_BASE_LOAD_VA = 0x510900
SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA = 0x947AD8
SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA = 0x947AF0
SOURCE_ORIGINAL_EVENT_SELECTOR_FROM_EVENT_ID_VA = 0x510300
SOURCE_ORIGINAL_EVENT_NULL_LINK_SENTINEL = 0xFFFFFFFF
SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE = {
    0x7C9FE8: 0x510960,
    0x7C4C24: 0x510970,
    0x7C9D9C: 0x5109D0,
    0x7C9E80: 0x5109D0,
    0x7C9EF8: 0x5109D0,
    0x7C9F70: 0x5109D0,
    0x7C9E14: 0x510970,
}


@dataclass(frozen=True)
class OriginalLoadedEventBaseLinkReceipt:
    source_event_vtable_va: int
    source_virtual24_load_va: int
    source_event_id_dword_0c: int
    source_event_registry_collection_va: int | None
    source_saved_link_registry_index: int
    source_resolved_link_pointer_dword_08: int
    source_after_base_load_event_record: bytes


def source_original_loaded_event_base_link_510900(
    *, original_native_post_constructor_record: bytes,
    original_saved_event_dword_10: int,
    original_saved_link_registry_index: int,
    original_source_selected_registry_pointer_entries: tuple[int, ...] | None,
) -> OriginalLoadedEventBaseLinkReceipt:
    """Source exact base +0x24 loader's direct writes at 0x510900.

    It reads source saved event+0x10 DWORD first, then a *separate*
    serialized registry index. Index FFFFFFFF writes event+8=0
    without any registry dereference. Otherwise it calls 0x510300
    on this event, selects 0x947AD8 or 0x947AF0 by original event
    ID+0x0C bit0, reads selected collection's registry at +0x10
    and uses the saved index as DWORD offset, writing event+8.
    Original later virtual+0x24 subclass callbacks ALSO restore
    flag/side/extra fields. They are NOT in this receipt.
    """
    r=original_native_post_constructor_record
    if type(r) is not bytes or len(r)<0x14:
        raise OriginalLoadedEventLinkSourceError(
            "original native event record through +0x10 required")
    vt=unpack_from("<I",r,0)[0]
    method=SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE.get(vt)
    if method is None:
        raise OriginalLoadedEventLinkSourceError(
            "source serialized event native vtable/load callback not qualified")
    if any(type(x) is not int or not 0<=x<=0xFFFFFFFF for x in (
        original_saved_event_dword_10,original_saved_link_registry_index
    )):
        raise OriginalLoadedEventLinkSourceError(
            "authentic saved original base-event DWORD fields required")
    ident=unpack_from("<I",r,0x0C)[0]
    index=original_saved_link_registry_index
    entries=original_source_selected_registry_pointer_entries
    if index==SOURCE_ORIGINAL_EVENT_NULL_LINK_SENTINEL:
        if entries is not None:
            raise OriginalLoadedEventLinkSourceError(
                "source null sentinel bypasses selected registry dereference")
        selected=None
        pointer=0
    else:
        selected=(SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA if ident & 1
                  else SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA)
        if (type(entries) is not tuple or not 0<=index<len(entries) or
            any(type(value) is not int or not 0<=value<=0xFFFFFFFF for value in entries)):
            raise OriginalLoadedEventLinkSourceError(
                "actual source selected registry pointer table including saved index required")
        pointer=entries[index]
    after=bytearray(r)
    pack_into("<I",after,0x10,original_saved_event_dword_10)
    pack_into("<I",after,8,pointer)
    return OriginalLoadedEventBaseLinkReceipt(
        vt,method,ident,selected,index,pointer,bytes(after))



SOURCE_ORIGINAL_LOADED_MATCH_BASIC_V24_VA = 0x510970
SOURCE_ORIGINAL_LOADED_MATCH_EXTENDED_V24_VA = 0x5109D0


@dataclass(frozen=True)
class OriginalLoadedLeagueMatchFieldReceipt:
    """Exact post-0x510900 source class +0x24 saved-field writes only."""
    source_match_vtable: int
    original_source_virtual24_load_va: int
    source_saved_match_flags44_dword: int
    source_native_match_after_field_load: bytes


def source_original_loaded_leaguematch_saved_fields_510970_5109d0(
    *, original_native_record_after_base_load: bytes,
    original_saved_match_flags44_dword: int,
    original_saved_halfword_3c: int,
    original_saved_halfword_3e: int,
    original_saved_halfword_40: int,
    original_saved_dword_48: int,
    original_saved_extended_four_bytes_58_to_5b: bytes | None = None,
) -> OriginalLoadedLeagueMatchFieldReceipt:
    """Original 0x510970 and 0x5109D0 verified source direct reads.

    Source 0x510970 calls 0x510900 first, then restores +0x44
    DWORD, +0x3C/+0x3E/+0x40 WORDs, and +0x48 DWORD. Source
    0x5109D0 calls 0x510970 first, then restores +0x58..0x5B
    four consecutive bytes. This is a saved-record boundary only;
    a subsequent native match callback can mutate these flags.
    """
    r=original_native_record_after_base_load
    if type(r) is not bytes or len(r)<4:
        raise OriginalLoadedEventLinkSourceError("authentic native match record required")
    vt=unpack_from("<I",r,0)[0]
    method=SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE.get(vt)
    if method not in (
        SOURCE_ORIGINAL_LOADED_MATCH_BASIC_V24_VA,
        SOURCE_ORIGINAL_LOADED_MATCH_EXTENDED_V24_VA,
    ):
        raise OriginalLoadedEventLinkSourceError(
            "original vtable does not have source-qualified LeagueMatch field loader")
    extended=method==SOURCE_ORIGINAL_LOADED_MATCH_EXTENDED_V24_VA
    if len(r)<(0x5C if extended else 0x4C):
        raise OriginalLoadedEventLinkSourceError(
            "original source match scratch missing saved-field offsets")
    ints=(original_saved_match_flags44_dword,original_saved_dword_48)
    halfs=(original_saved_halfword_3c,original_saved_halfword_3e,
           original_saved_halfword_40)
    if (any(type(i) is not int or not 0<=i<=0xFFFFFFFF for i in ints)
            or any(type(i) is not int or not 0<=i<=0xFFFF for i in halfs)):
        raise OriginalLoadedEventLinkSourceError(
            "real original stored DWORD/WORD field values required")
    extra=original_saved_extended_four_bytes_58_to_5b
    if extended:
        if type(extra) is not bytes or len(extra)!=4:
            raise OriginalLoadedEventLinkSourceError(
                "source extended original four saved bytes required")
    elif extra is not None:
        raise OriginalLoadedEventLinkSourceError(
            "source basic +0x24 loader does not reach four extended fields")
    after=bytearray(r)
    pack_into("<I",after,0x44,original_saved_match_flags44_dword)
    for addr,value in zip((0x3C,0x3E,0x40),halfs):
        pack_into("<H",after,addr,value)
    pack_into("<I",after,0x48,original_saved_dword_48)
    if extended:
        after[0x58:0x5C]=extra
    return OriginalLoadedLeagueMatchFieldReceipt(
        vt,method,original_saved_match_flags44_dword,bytes(after))
