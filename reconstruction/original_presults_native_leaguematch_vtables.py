"""Shipped original LeagueMatch vtables and PResults pre-count method owners.

Static proof: owner-authorized original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
No original process execution, original binary distribution or GUI claim.

Original class constructors 0x5104D0/0x510500/0x510520/0x5105A0/
0x5105D0/0x510600/0x510640/0x510680 select vtables whose
virtual+0x0C is either 0x510AD0 or 0x510B00.
All known listed original vtables have virtual+0x18=0x6559A0,
which returns ECX (the LeagueMatch object itself), not a separate
payload. This matters to PResults 0x4A7210 payload+0x44 filtering.
"""
from __future__ import annotations

from struct import unpack_from

from original_presults_native_event_work import (
    OriginalPResultsEventSourceError,
    OriginalPResultsNativePreCountNode,
)

SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON = frozenset((
    0x7C4C24, 0x7C4CE4, 0x7C9D9C,
    0x7C9E14, 0x7C9E80, 0x7C9EF8,
))
SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE = 0x7C9F70
SOURCE_ORIGINAL_LEAGUE_MATCH_GENERIC_V0C_VA = 0x510AD0
SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_V0C_VA = 0x510B00
SOURCE_ORIGINAL_LEAGUE_MATCH_EVENT_PROCESS_V10_VA = 0x513010
SOURCE_ORIGINAL_LEAGUE_MATCH_PAYLOAD_SELF_V18_VA = 0x6559A0
SOURCE_ORIGINAL_LEAGUE_MATCH_INIT_VA = 0x510380
SOURCE_ORIGINAL_LEAGUE_MATCH_PROCESSED_FLAG_SET_VA = 0x512F20
SOURCE_ORIGINAL_LEAGUE_MATCH_FLAG5 = 0x20
SOURCE_ORIGINAL_LEAGUE_MATCH_RECORD_FLAG_OFFSET = 0x44
SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_OWNER_POINTER_OFFSET = 0x54
SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_OWNER_FLAG_OFFSET = 0x44


def source_original_league_match_native_precount_node_4a7210(
    *, original_event_object_pointer: int,
    original_match_record_before_v0c: bytes,
    original_first_club_virtual_result_pointer: int | None,
    original_second_club_virtual_result_pointer: int | None,
    original_special_owner_record_via_plus54: bytes | None,
    original_match_record_after_reached_v0c: bytes | None,
) -> OriginalPResultsNativePreCountNode:
    """Materialize exact original LeagueMatch virtual+0x0C path as PResults node.

    Normal 0x510AD0 returns 0 if native match+0x44 bit5 set, then
    calls Side0 virtual+0; null skips Side1 (and returns0), else
    Side1 virtual+0; returns1 iff both club pointers are nonnull.

    Specialized vtable0x7C9F70 calls 0x510B00, which calls 0x510AD0;
    only when it returns1 does it read source (match+0x54)
    object+0x44 bit0, using that bit as the ultimate result.

    For v+0x0C NONZERO, original PResults 0x4A7210 then reads event+8;
    if zero calls virtual+0x18 which is exactly source 0x6559A0
    return-this, so the final bit6 predicate reads match+0x44
    AFTER any original Side getter effects. A caller must provide
    authentic post-virtual record bytes. Missing/unreached source
    values are not synthesized from club names, competition kind
    or current managerial team.
    """
    if (type(original_event_object_pointer) is not int
        or not 0<original_event_object_pointer<=0xFFFFFFFF
        or type(original_match_record_before_v0c) is not bytes
        or len(original_match_record_before_v0c)<0x58):
        raise OriginalPResultsEventSourceError(
            "actual original native LeagueMatch source record through +0x54 required")
    record=original_match_record_before_v0c
    vt=unpack_from("<I",record,0)[0]
    if vt not in SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON and vt!=SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE:
        raise OriginalPResultsEventSourceError(
            "original native LeagueMatch vtable must be source-verified")
    initial_flags=unpack_from("<I",record,SOURCE_ORIGINAL_LEAGUE_MATCH_RECORD_FLAG_OFFSET)[0]
    if initial_flags & SOURCE_ORIGINAL_LEAGUE_MATCH_FLAG5:
        if (original_first_club_virtual_result_pointer is not None or
            original_second_club_virtual_result_pointer is not None or
            original_special_owner_record_via_plus54 is not None or
            original_match_record_after_reached_v0c is not None):
            raise OriginalPResultsEventSourceError(
                "original bit5 skips both Side club virtual methods and post-event payload")
        eligible=False
    else:
        first=original_first_club_virtual_result_pointer
        second=original_second_club_virtual_result_pointer
        if type(first) is not int or not 0<=first<=0xFFFFFFFF:
            raise OriginalPResultsEventSourceError(
                "source LeagueMatch Side0 virtual+0 result required")
        if not first:
            if (second is not None or
                original_special_owner_record_via_plus54 is not None or
                original_match_record_after_reached_v0c is not None):
                raise OriginalPResultsEventSourceError(
                    "native null Side0 skips Side1 and remaining virtual callbacks")
            eligible=False
        else:
            if type(second) is not int or not 0<=second<=0xFFFFFFFF:
                raise OriginalPResultsEventSourceError(
                    "source LeagueMatch Side1 virtual+0 result required")
            eligible=bool(second)
            if not eligible:
                if (original_special_owner_record_via_plus54 is not None or
                    original_match_record_after_reached_v0c is not None):
                    raise OriginalPResultsEventSourceError(
                        "native null Side1 skips specialized owner and PResults fields")
            elif vt==SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE:
                if (unpack_from("<I",record,
                                 SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_OWNER_POINTER_OFFSET)[0]==0
                    or type(original_special_owner_record_via_plus54) is not bytes
                    or len(original_special_owner_record_via_plus54)<0x48):
                    raise OriginalPResultsEventSourceError(
                        "source special native match+0x54 owner+0x44 required")
                eligible=bool(unpack_from(
                    "<I",original_special_owner_record_via_plus54,
                    SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_OWNER_FLAG_OFFSET)[0]&1)
                if not eligible and original_match_record_after_reached_v0c is not None:
                    raise OriginalPResultsEventSourceError(
                        "special owner bit0 false skips PResults node+8")
            elif original_special_owner_record_via_plus54 is not None:
                raise OriginalPResultsEventSourceError(
                    "normal original LeagueMatch vtable does not visit special owner+0x54")
    if not eligible:
        return OriginalPResultsNativePreCountNode(
            original_event_object_pointer,False)
    after=original_match_record_after_reached_v0c
    if type(after) is not bytes or len(after)<0x48:
        raise OriginalPResultsEventSourceError(
            "original reached event+8 and source payload-after-virtual bytes required")
    if len(after)>=4 and unpack_from("<I",after,0)[0]!=vt:
        raise OriginalPResultsEventSourceError(
            "original event vtable identity changed without source proof")
    event8=unpack_from("<I",after,8)[0]
    return OriginalPResultsNativePreCountNode(
        original_event_object_pointer,True,event8,
        (None if event8 else unpack_from("<I",after,0x44)[0]))
