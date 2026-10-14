"""Original 0x615C50 one-node predicate for native 0x615D10 date search.

Canonical original SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
static source only. Native 0x615D10 invokes 0x615C50 with arguments
(actual original team pointer, 0, 1, 0, 0). The predicate calls
original virtual+0x18, 0x4F2CB0 plus virtual+0x04, and sometimes
0x514520 (which can execute embedded SideRef getters and mutate world).
No original source callback is invoked or guessed here.

This model deliberately covers only ONE reached slot-node candidate, and
does not resolve its mutable next-pointer, original 0x615D10 date search,
0x5127A0 mutation, native match completion or GUI.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_v3c_calendar_second_pass import (
    OriginalNative615D10DateWindow,
)
from original_native_v3c_reschedule_gate import (
    OriginalV3CRescheduleGateError,
)


SOURCE_NATIVE_SLOT_FILTER_VA = 0x615C50
SOURCE_NATIVE_SLOT_FILTER_RETURN_VA = 0x615CF8
SOURCE_NATIVE_SLOT_EVENT_V18_OFFSET = 0x18
SOURCE_NATIVE_SLOT_EVENT_V4_OFFSET = 0x04
SOURCE_NATIVE_CANDIDATE_SIDE_REF_CONSTRUCTION_VA = 0x4F2CB0
SOURCE_NATIVE_NODE_WORLD_CALLBACK_VA = 0x514520
SOURCE_NATIVE_NODE_NEXT_POINTER_OFFSET = 0x04
SOURCE_NATIVE_NODE_STATE_POINTER_OFFSET = 0x08
SOURCE_NATIVE_EVENT_FLAGS_OFFSET = 0x44
SOURCE_NATIVE_FLAG_STARTED = 0x01
SOURCE_NATIVE_FLAG_IGNORE_ALTERNATE_COLLECTION = 0x20
SOURCE_NATIVE_FLAG_SKIP_EVENT = 0x40


@dataclass(frozen=True)
class OriginalNative615C50Candidate:
    reached_node_pointer: int
    source_candidate_decision: str
    original_returned_slot_node_pointer: int | None
    original_node_link_traversal_outstanding: bool
    source_virtual_side_effects_proven: bool
    source_mutable_virtuals_may_have_executed: bool
    native_615d10_complete: bool = False
    native_event_world_complete: bool = False


def _uint32(value: int, name: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise OriginalV3CRescheduleGateError(
            f"actual reached original {name} uint32 required")
    return value


def source_original_615c50_reached_node_candidate(
    *,
    original_reached_date_window: OriginalNative615D10DateWindow,
    original_slot_head_node_pointer: int,
    original_node_record_at_virtual18: bytes | None = None,
    original_reached_virtual18_event_pointer: int | None = None,
    original_event_record_after_virtual18: bytes | None = None,
    original_reached_virtual4_comparison_eax: int | None = None,
    original_node_record_after_virtual4: bytes | None = None,
    original_reached_node_state_after_514520: int | None = None,
) -> OriginalNative615C50Candidate:
    """Classify one source node, stopping before all unprovided native effects.

    When source reaches +0x615C50, EDI points at the slot's first node.
    A null head returns EAX=0. A nonnull head calls original virtual18
    BEFORE inspecting event flags. Both event/SideRef virtuals may mutate
    node/world state, so a distinct original snapshot AFTER virtual4 is
    required before checking node+8. 0x514520 is separately mutating;
    require its actual node+8 post-call result, not a guess.
    """
    window=original_reached_date_window
    if not isinstance(window, OriginalNative615D10DateWindow):
        raise OriginalV3CRescheduleGateError(
            "native original 615D10 reached date-window receipt required")
    if (not window.source_would_enter_615c50_search or
            window.negative_source_slot_index_unqualified or
            window.null_original_slot_vector_unqualified):
        raise OriginalV3CRescheduleGateError(
            "original 615C50 node not source-safe/reached for this calendar window")
    pointer=_uint32(original_slot_head_node_pointer,"slot head pointer")
    optional=(original_node_record_at_virtual18,
              original_reached_virtual18_event_pointer,
              original_event_record_after_virtual18,
              original_reached_virtual4_comparison_eax,
              original_node_record_after_virtual4,
              original_reached_node_state_after_514520)
    if pointer == 0:
        if any(value is not None for value in optional):
            raise OriginalV3CRescheduleGateError(
                "empty original date slot skips all virtual/event callbacks")
        return OriginalNative615C50Candidate(
            0,"empty_slot_returns_zero",None,False,False,False)
    node=original_node_record_at_virtual18
    if type(node) is not bytes or len(node)<0x0C or not unpack_from("<I",node)[0]:
        raise OriginalV3CRescheduleGateError(
            "original reached slot node/vtable bytes through +8 required")
    event_ptr=_uint32(original_reached_virtual18_event_pointer,
                      "node virtual+18 event return")
    if event_ptr == 0:
        if any(value is not None for value in optional[2:]):
            raise OriginalV3CRescheduleGateError(
                "native virtual18 null skips downstream event/SideRef callbacks")
        return OriginalNative615C50Candidate(
            pointer,"null_event_virtual18_advance_node",None,True,False,True)
    event=original_event_record_after_virtual18
    if type(event) is not bytes or len(event)<0x48:
        raise OriginalV3CRescheduleGateError(
            "actual reached event bytes through +44 after virtual18 required")
    flags=unpack_from("<I",event,SOURCE_NATIVE_EVENT_FLAGS_OFFSET)[0]

    def early_skip(reason: str)->OriginalNative615C50Candidate:
        if any(value is not None for value in optional[3:]):
            raise OriginalV3CRescheduleGateError(
                "native skipped virtual4 or node followup; extra reached result invalid")
        return OriginalNative615C50Candidate(
            pointer,reason,None,True,False,True)

    # Original caller 615D10 passes arg4=0. Compare its bool with bit5.
    if flags & SOURCE_NATIVE_FLAG_IGNORE_ALTERNATE_COLLECTION:
        return early_skip("event_flag_bit5_excludes_source_calendar_search")
    compare=_uint32(original_reached_virtual4_comparison_eax,
                    "event virtual+4 team-side comparison EAX")
    if compare == 0:
        if any(value is not None for value in optional[4:]):
            raise OriginalV3CRescheduleGateError(
                "source virtual4 comparison failed; later node effects not reached")
        return OriginalNative615C50Candidate(
            pointer,"event_virtual4_side_mismatch_advance_node",
            None,True,False,True)
    after=original_node_record_after_virtual4
    if type(after) is not bytes or len(after)<0x0C:
        raise OriginalV3CRescheduleGateError(
            "actual original node bytes after virtual4 through +8 required")
    if unpack_from("<I",after,0x08)[0]:
        reason="original_node_plus8_already_nonzero_advance"
    elif flags & SOURCE_NATIVE_FLAG_SKIP_EVENT:
        reason="event_flag_bit6_excludes_candidate"
    elif flags & SOURCE_NATIVE_FLAG_STARTED:
        # Caller 615D10's last 615C50 argument is ZERO, so bit0 nodes
        # cannot use the alternative direct-return branch.
        reason="event_flag_bit0_excludes_615d10_caller"
    else:
        later=_uint32(original_reached_node_state_after_514520,
                      "actual node+8 state after mutating 0x514520")
        if later == 0:
            return OriginalNative615C50Candidate(
                pointer,"original_514520_returned_candidate",
                pointer,False,False,True)
        reason="original_514520_mutated_node_plus8_advance"
        return OriginalNative615C50Candidate(
            pointer,reason,None,True,False,True)
    if original_reached_node_state_after_514520 is not None:
        raise OriginalV3CRescheduleGateError(
            "original 0x514520 skipped; extra reached node result invalid")
    return OriginalNative615C50Candidate(
        pointer,reason,None,True,False,True)
