"""Join the ORIGINAL 513244 first-side owner to the 5DB7D0 mutable tail.

This pure source projection requires independently reached native bytes.
It does not execute 5DA2F0/v+18, produce real match state or mutate GameState.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_match_first_side_human_owner import (
    source_original_5da2f0_first_side_human_owner,
    SourceOriginalFirstSideHumanOwnerReceipt,
)
from original_match_first_side_world_write import (
    source_original_5db7d0_first_side_world_tail,
    SourceOriginalFirstSideWorldWriteReceipt,
)


class OriginalFirstSideJoinedWorldError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalFirstSideJoinedWorldReceipt:
    source_human_selector: SourceOriginalFirstSideHumanOwnerReceipt
    source_tail: SourceOriginalFirstSideWorldWriteReceipt
    original_first_side_pointer: int
    original_5da5f4_final_virtual18_nonzero: bool
    actual_original_callbacks_executed: bool = False
    live_match_state_committed: bool = False


def source_original_5da2f0_first_side_joined_world(
    *,
    original_source_owner_call: dict,
    original_first_side_pointer_at_5db7d0: int,
    original_first_side_before_5db7d0: bytes,
    original_processing_context_at_5db7d0: bytes,
    original_5da5f4_final_virtual18_nonzero: bool,
    original_stack_cap_div10_input_if_reached: int | None,
) -> SourceOriginalFirstSideJoinedWorldReceipt:
    """Join independently reached stages by native owner pointer and club+4.

    Native 5DA5F4 final virtual+18 AL=0 reaches 5DA746 and retains the
    zero-initialized local flag; AL!=0 takes 5DA5FF through 5DA705 and
    sets that local flag to one. 5DB7D0 then skips the entire first-side
    persistent write tail iff the flag is nonzero. No callback is executed.
    """
    if type(original_source_owner_call) is not dict:
        raise OriginalFirstSideJoinedWorldError("typed source owner call required")
    owner=source_original_5da2f0_first_side_human_owner(**original_source_owner_call)
    if (type(original_first_side_pointer_at_5db7d0) is not int or
            original_first_side_pointer_at_5db7d0!=owner.original_side_club_pointer):
        raise OriginalFirstSideJoinedWorldError("original first-side pointer changed")
    club=original_first_side_before_5db7d0
    if type(club) is not bytes or len(club)<0x178:
        raise OriginalFirstSideJoinedWorldError("original first-side record through+177 required")
    if unpack_from("<I",club,4)[0]!=owner.original_full_dword_club_key:
        raise OriginalFirstSideJoinedWorldError("original first-side club+4 identity changed")
    callback=original_5da5f4_final_virtual18_nonzero
    if type(callback) is not bool:
        raise OriginalFirstSideJoinedWorldError("actual 5DA5F4 final virtual+18 AL required")
    tail=source_original_5db7d0_first_side_world_tail(
        original_first_side_before_tail=club,
        original_processing_context_at_tail=original_processing_context_at_5db7d0,
        original_local_flag_at_5db7d0=int(callback),
        original_stack_cap_div10_input_if_reached=original_stack_cap_div10_input_if_reached,
    )
    if tail.source_first_side_writes_skipped is not callback:
        raise OriginalFirstSideJoinedWorldError("source callback/skip result contradictory")
    return SourceOriginalFirstSideJoinedWorldReceipt(
        owner,tail,owner.original_side_club_pointer,callback)
