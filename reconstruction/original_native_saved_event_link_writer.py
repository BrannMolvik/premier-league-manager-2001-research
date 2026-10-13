"""Original event reference SaveLoad writer symmetry, source 0x5107F0.

Original disc-root executable SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
read-only PE verification. The original saves two distinct date-calendar
collections, but no complete save file parser or native process is created.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_native_loaded_event_link import (
    SOURCE_ORIGINAL_EVENT_NULL_LINK_SENTINEL,
    SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
    SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA,
    SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE,
)


class OriginalSavedEventLinkSourceError(ValueError):
    """Event registry writer or its source input not qualified."""


SOURCE_ORIGINAL_EVENT_BASE_WRITE_VA = 0x5107F0
SOURCE_ORIGINAL_EVENT_SAVED_LINK_INDEX_BYTECODE_VA = 0x510810
SOURCE_ORIGINAL_EVENT_SOURCE_CALENDAR_SAVE_VA = 0x616470
SOURCE_ORIGINAL_EVENT_SOURCE_CALENDAR_LOAD_VA = 0x616500

# Both full calendars are saved, then restored, in this exact original
# source order; these are independently addressable original global owners.
SOURCE_ORIGINAL_BOTH_CALENDAR_SAVE_CALLS = (
    (0x50DC6E,SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA),
    (0x50DCA9,SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA),
)
SOURCE_ORIGINAL_BOTH_CALENDAR_LOAD_CALLS = (
    (0x50E0A4,SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA),
    (0x50E0C1,SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA),
)

SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE = {
    0x7C9FE8:0x510840,0x7C4C24:0x510850,
    0x7C9D9C:0x5108B0,0x7C9E80:0x5108B0,
    0x7C9EF8:0x5108B0,0x7C9F70:0x5108B0,
    0x7C9E14:0x510850,
}


@dataclass(frozen=True)
class OriginalSavedEventBaseLinkReceipt:
    original_source_event_vtable: int
    original_source_virtual20_write_va: int
    original_serialized_event_dword_10: int
    original_serialized_link_reference_index: int
    original_link_target_present: bool
    source_index_collides_with_null_sentinel: bool


def source_original_saved_event_link_index_5107f0(
    *, original_native_source_event_record: bytes,
    original_native_link_target_event_record: bytes | None,
) -> OriginalSavedEventBaseLinkReceipt:
    """Original base +0x20 writer: raw +0x10, then target-ID>>1.

    Native 0x5107F0 first writes its own event+0x10 DWORD. If event+8
    is NULL, it writes 0xFFFFFFFF as saved link index. Otherwise it
    obtains target event+0x0C ID and applies SIGNED 32-bit SAR, 1.
    It writes only the index, never a 32-bit raw process pointer.
    Source serialization does NOT validate the target's collection
    matches the origin; no cross-collection link support inferred.
    """
    source=original_native_source_event_record
    allowed=SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE
    if type(source) is not bytes or len(source)<0x14:
        raise OriginalSavedEventLinkSourceError("actual original source event record required")
    vt=unpack_from("<I",source,0)[0]
    method=allowed.get(vt)
    if method is None or vt not in SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE:
        raise OriginalSavedEventLinkSourceError("source original event v+0x20 not authenticated")
    target=original_native_link_target_event_record
    if target is None:
        saved_index=SOURCE_ORIGINAL_EVENT_NULL_LINK_SENTINEL
        linked=False
    else:
        if type(target) is not bytes or len(target)<0x10:
            raise OriginalSavedEventLinkSourceError("original link target+0x0C id required")
        target_vtable=unpack_from("<I",target,0)[0]
        if target_vtable not in allowed:
            raise OriginalSavedEventLinkSourceError(
                "original linked target class not verified in source loader family")
        target_id=unpack_from("<I",target,0x0C)[0]
        signed=target_id-0x100000000 if target_id & 0x80000000 else target_id
        saved_index=(signed>>1)&0xFFFFFFFF
        linked=True
    return OriginalSavedEventBaseLinkReceipt(
        vt,method,unpack_from("<I",source,0x10)[0],saved_index,linked,
        linked and saved_index==SOURCE_ORIGINAL_EVENT_NULL_LINK_SENTINEL)
