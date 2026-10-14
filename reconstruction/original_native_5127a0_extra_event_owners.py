"""Bind original 41A5B0 event gating to source-qualified 5127A0 row owners.

The optional callback occurs immediately after original 4197C0 only when
raw owner row+4A is nonzero. These are source-order and identity invariants
only. Actual original 605F70 native allocation / 605F90 world update and
match completion remain unresolved and MUST not be marked finished.
"""
from __future__ import annotations
from dataclasses import dataclass

from original_native_5127a0_combined_owner import Original5127A0CombinedOwnerReceipt
from original_native_41a5b0_extra_event import Original41A5B0ExtraEventReceipt


class Original5127A0ExtraEventOwnerError(ValueError):
    pass


@dataclass(frozen=True)
class Original5127A0ExtraEventOwnerReceipt:
    source_original_5127a0_owner: Original5127A0CombinedOwnerReceipt
    original_qualifying_extra_events: tuple[
        tuple[Original41A5B0ExtraEventReceipt,...],
        tuple[Original41A5B0ExtraEventReceipt,...],
    ]
    original_first_side_extra_count: int
    original_second_side_extra_count: int
    original_world_allocations_outstanding: int
    original_extra_rows_have_no_mutating_world_effects: bool
    native_callbacks_executed: bool = False
    live_game_state_updated: bool = False
    match_finished: bool = False


def source_original_5127a0_qualified_optional_extra_events(
    *,
    source_original_owner: Original5127A0CombinedOwnerReceipt,
    original_reached_extra_by_side: tuple[
        tuple[Original41A5B0ExtraEventReceipt,...],
        tuple[Original41A5B0ExtraEventReceipt,...],
    ],
) -> Original5127A0ExtraEventOwnerReceipt:
    if (not isinstance(source_original_owner,Original5127A0CombinedOwnerReceipt)
        or source_original_owner.source_native_callbacks_executed
        or source_original_owner.live_game_state_updated
        or source_original_owner.finished_match_journey):
        raise Original5127A0ExtraEventOwnerError(
            "source-only two-owner 5127A0 original ID/order qualification required")
    if type(original_reached_extra_by_side) is not tuple or len(original_reached_extra_by_side)!=2:
        raise Original5127A0ExtraEventOwnerError("exact two native source extra owner lists required")
    both_maps=(source_original_owner.first_side,source_original_owner.second_side)
    all_flags=source_original_owner.original_row_extra_required
    if type(all_flags) is not tuple or len(all_flags)!=2:
        raise Original5127A0ExtraEventOwnerError("original matched raw row+4A flags required")
    allocations=0
    counts=[]
    for i,(mapped,flags,extras) in enumerate(zip(both_maps,all_flags,original_reached_extra_by_side)):
        if type(extras) is not tuple:
            raise Original5127A0ExtraEventOwnerError("original extra source callbacks tuple required")
        if (type(flags) is not tuple or
            len(flags)!=len(mapped.native_row_ids) or
            len(mapped.native_row_ids)!=len(mapped.native_row_pointers)):
            raise Original5127A0ExtraEventOwnerError("original two-owner row count provenance invalid")
        required=[
            (pid,ptr)
            for pid,ptr,flag in zip(mapped.native_row_ids,mapped.native_row_pointers,flags)
            if flag is True
        ]
        if len(extras)!=len(required):
            raise Original5127A0ExtraEventOwnerError(
                "original row+4A requires exactly its ordered 41A5B0 callbacks")
        for event,(pid,pointer) in zip(extras,required):
            if (not isinstance(event,Original41A5B0ExtraEventReceipt)
                or event.original_native_callback_executed
                or event.live_game_state_updated
                or event.original_player_id!=pid
                or event.original_native_row_player_pointer!=pointer):
                raise Original5127A0ExtraEventOwnerError(
                    "actual reached post-row 41A5B0 player identity/pointer mismatch")
            if (event.original_would_allocate_605f70_and_store_player24c
                == event.source_branch_complete_without_world_effects):
                raise Original5127A0ExtraEventOwnerError(
                    "source extra event allocation/branch completeness contradictory")
            if event.original_would_allocate_605f70_and_store_player24c:
                allocations+=1
        counts.append(len(required))
    return Original5127A0ExtraEventOwnerReceipt(
        source_original_owner,original_reached_extra_by_side,
        counts[0],counts[1],allocations,allocations==0,
    )
