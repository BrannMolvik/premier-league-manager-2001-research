"""Original PostponedEvent PResults 4A7210 virtual qualification through wrapper.

Original 510BA0 links old LeagueMatch event+8 to NEW wrapper and stores
wrapper+14=underlying event. Wrapper vtable 7C9FE8:
 +0C=5140B0 tail-dispatches underlying event v+0C
 +10=5140F0 tail-dispatches underlying event v+10
 +18=514100 tail-dispatches underlying event v+18
Thus PResults +0C comes from underlying LeagueMatch, but the subsequent
PResults event+8 filter reads the WRAPPER's +8, not old match+8.
When wrapper+8==0, payload+44 comes from underlying match via v+18.
Do not confuse linked old event (event+8 nonzero) with new wrapper.

Private original PE SHA 833bf95e..b7cc3 is statically inspected only.
No original execution, calendar callback mutation, GameState or UI occurs.
"""
from struct import unpack_from

from original_presults_native_event_work import (
    OriginalPResultsEventSourceError,
    OriginalPResultsNativePreCountNode,
)
from original_presults_native_leaguematch_vtables import (
    source_original_league_match_native_precount_node_4a7210,
)

SOURCE_ORIGINAL_POSTPONED_WRAPPER_VTABLE = 0x7C9FE8
SOURCE_WRAPPER_V0C_VA = 0x5140B0
SOURCE_WRAPPER_V10_VA = 0x5140F0
SOURCE_WRAPPER_V18_VA = 0x514100
SOURCE_WRAPPER_UNDERLYING_EVENT_OFFSET = 0x14


def source_original_postponed_wrapper_precount_node_4a7210(
    *,
    original_wrapper_event_pointer: int,
    original_wrapper_record_before_v0c: bytes,
    original_underlying_match_event_pointer: int,
    original_underlying_match_record_before_v0c: bytes,
    original_first_club_virtual_result_pointer: int | None,
    original_second_club_virtual_result_pointer: int | None,
    original_special_owner_record_via_plus54: bytes | None,
    original_wrapper_record_after_reached_v0c: bytes | None,
    original_underlying_match_record_after_reached_v0c: bytes | None,
) -> OriginalPResultsNativePreCountNode:
    ptr=original_wrapper_event_pointer
    underlying=original_underlying_match_event_pointer
    before=original_wrapper_record_before_v0c
    match=original_underlying_match_record_before_v0c
    if (type(ptr) is not int or not 0<ptr<=0xffffffff
            or type(underlying) is not int or not 0<underlying<=0xffffffff
            or ptr==underlying
            or type(before) is not bytes or len(before)<0x1c
            or type(match) is not bytes or len(match)<0x58):
        raise OriginalPResultsEventSourceError(
            "source native wrapper and underlying original LeagueMatch records required")
    if (unpack_from("<I",before)[0]!=SOURCE_ORIGINAL_POSTPONED_WRAPPER_VTABLE
            or unpack_from("<I",before,SOURCE_WRAPPER_UNDERLYING_EVENT_OFFSET)[0]!=underlying
            or unpack_from("<I",match,8)[0]!=ptr):
        raise OriginalPResultsEventSourceError(
            "native 510BA0 wrapper+14/old match+8 link identity mismatch")
    # Delegate ONLY source v+0C through underlying original LeagueMatch.
    # Its own original event+8 is the link pointer and is deliberately NOT
    # treated as the wrapper's subsequent event+8 filter.
    underlying_node=source_original_league_match_native_precount_node_4a7210(
        original_event_object_pointer=underlying,
        original_match_record_before_v0c=match,
        original_first_club_virtual_result_pointer=(
            original_first_club_virtual_result_pointer),
        original_second_club_virtual_result_pointer=(
            original_second_club_virtual_result_pointer),
        original_special_owner_record_via_plus54=(
            original_special_owner_record_via_plus54),
        original_match_record_after_reached_v0c=(
            original_underlying_match_record_after_reached_v0c),
    )
    if not underlying_node.source_virtual_0c_nonzero:
        if original_wrapper_record_after_reached_v0c is not None:
            raise OriginalPResultsEventSourceError(
                "original wrapper event+8 skipped because underlying v+0C false")
        return OriginalPResultsNativePreCountNode(ptr,False)
    after=original_wrapper_record_after_reached_v0c
    payload=original_underlying_match_record_after_reached_v0c
    if (type(after) is not bytes or len(after)<0x1c
            or unpack_from("<I",after)[0]!=SOURCE_ORIGINAL_POSTPONED_WRAPPER_VTABLE
            or unpack_from("<I",after,SOURCE_WRAPPER_UNDERLYING_EVENT_OFFSET)[0]!=underlying
            or type(payload) is not bytes or len(payload)<0x48):
        raise OriginalPResultsEventSourceError(
            "source wrapper state AFTER v+0C and underlying payload required")
    event8=unpack_from("<I",after,8)[0]
    return OriginalPResultsNativePreCountNode(
        ptr,True,event8,None if event8 else unpack_from("<I",payload,0x44)[0])
