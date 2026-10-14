"""Original source 0x615950 linked insertion, qualified match event slot.

Source: owner-private footballmanager.exe 4,714,541 B SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
STATIC inspection only, no original program run. Models reached date
slot only, NOT 0x64CCD0/0x615890 date search or live native allocation.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from,pack_into

from original_presults_native_leaguematch_vtables import (
    SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON,
    SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE,
)
from original_native_loaded_event_link import (
    SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
    SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA,
)

SOURCE_ORIGINAL_DATE_INSERT_VA=0x615950
SOURCE_ORIGINAL_DATE_SEARCH_VA=0x615890
SOURCE_ORIGINAL_EVENT_COLLECTION_FROM_ID_VA=0x510300
SOURCE_ORIGINAL_DATE_INSERT_INDEX_WRITE_VA=0x615A43
SOURCE_ORIGINAL_DATE_INSERT_NEXT_WRITE_VA=0x615A48
SOURCE_ORIGINAL_DATE_INSERT_HEAD_WRITE_VA=0x615A4B


class OriginalNativeDatedEventInsertionSourceError(ValueError):
    """Actual original native owner/slot or source event class missing."""


@dataclass(frozen=True)
class OriginalNativeDatedEventInsertReceipt:
    original_selected_collection_pointer: int
    original_native_event_pointer: int
    original_native_event_id_dword_0c: int
    original_native_event_date_bucket_index_10: int
    original_source_slot_prior_head_event_pointer: int
    original_source_slot_new_head_event_pointer: int
    original_native_event_record_after_insert: bytes


def source_original_leaguematch_insert_into_reached_native_date_bucket_615950(
    *, original_source_match_event_pointer: int,
    original_source_match_record_before_insert: bytes,
    original_reached_dated_collection_pointer: int,
    original_reached_collection_base_bucket_pointer: int,
    original_reached_date_bucket_slot_pointer: int,
    original_reached_source_collection_bucket_count: int,
    original_reached_slot_prior_head_pointer: int,
) -> OriginalNativeDatedEventInsertReceipt:
    """Exact reached direct writes, not source date search or live native heap.

    Original 0x615A26..0x615A4B dereferences date-bucket slot from EDI
    source collection, calls match virtual+0x18 returning match itself,
    calls 0x510300 on source event+0x0C bit0 to select registry owner,
    writes native event+0x10 = (slot-source_collection[0])/4,
    event+0x04 = old slot head, then slot head = new native event.
    This API requires actually sourced slots and pointer identities.
    A reconstructed fixture date or token cannot stand in for these.
    """
    r=original_source_match_record_before_insert
    eventptr=original_source_match_event_pointer
    owner=original_reached_dated_collection_pointer
    base=original_reached_collection_base_bucket_pointer
    slot=original_reached_date_bucket_slot_pointer
    count=original_reached_source_collection_bucket_count
    old=original_reached_slot_prior_head_pointer
    if type(r) is not bytes or len(r)<0x14:
        raise OriginalNativeDatedEventInsertionSourceError(
            "native original LeagueMatch record through +0x10 required")
    vt=unpack_from("<I",r,0)[0]
    if vt not in SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON and vt!=SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE:
        raise OriginalNativeDatedEventInsertionSourceError(
            "actual original return-this LeagueMatch vtable required")
    if (type(eventptr) is not int or not 0<eventptr<=0xFFFFFFFF or
        type(owner) is not int or owner not in (
            SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
            SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA) or
        any(type(x) is not int or not 0<=x<=0xFFFFFFFF for x in (base,slot,old,count)) or
        base==0 or slot==0 or count==0):
        raise OriginalNativeDatedEventInsertionSourceError(
            "actual original dated collection base, slot and source pointers required")
    ident=unpack_from("<I",r,0x0C)[0]
    chosen=(SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA if ident&1 else
            SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA)
    if chosen!=owner:
        raise OriginalNativeDatedEventInsertionSourceError(
            "reached collection mismatches event+0x0C source owner 0x510300")
    difference=slot-base
    if difference<0 or difference&3 or difference//4>=count or base+count*4>0x100000000:
        raise OriginalNativeDatedEventInsertionSourceError(
            "original date bucket slot is outside source collection array")
    index=difference//4
    if index>0x7FFFFFFF:
        raise OriginalNativeDatedEventInsertionSourceError(
            "native signed source array index outside qualified range")
    after=bytearray(r)
    pack_into("<I",after,4,old)
    pack_into("<I",after,0x10,index)
    return OriginalNativeDatedEventInsertReceipt(
        owner,eventptr,ident,index,old,eventptr,bytes(after))
