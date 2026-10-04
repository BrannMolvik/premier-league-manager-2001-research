"""Source-closed ScoreComposite phase receiver registration/dispatch order.

The canonical executable constructs visible LeagueScores ScoreCompositeNormal
rows in source-row order. Each composite registers its typed phase receivers
into the matching sender's doubly-linked list through the same tail-insertion
primitive. Typed broadcasts traverse the list forward from sentinel->next.

This closes deterministic row callback order for one broadcast. It does NOT
create a universal aggregate order between all runtime phase icons and all
runtime phase text, because separate event broadcasts occur over time and each
row callback appends its own icon followed by its own text at the then-current
parent tail.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewPhaseReceiverOrderError(ValueError):
    pass


# LeagueScores row construction / receiver registration.
LEAGUE_SCORES_ROW_BUILD_LOOP_VA = 0x522E3A
LEAGUE_SCORES_SCORE_FACTORY_CALLSITE_VA = 0x522E6C
RECEIVER_LIST_APPEND_HELPER_VA = 0x5302C0
RECEIVER_NODE_DATA_COPY_VA = 0x530330

# ScoreCompositeNormal typed receiver subobject offsets.
SCORE_RECEIVER_HALF_TIME_OFFSET = 0x94
SCORE_RECEIVER_EXTRA_TIME_OFFSET = 0x98
SCORE_RECEIVER_PENALTIES_OFFSET = 0x9C
SCORE_RECEIVER_FULL_TIME_OFFSET = 0xA0

# Matching typed sender subobject offsets in the event owner.
SENDER_HALF_TIME_OFFSET = 0x40
SENDER_FULL_TIME_OFFSET = 0x50
SENDER_EXTRA_TIME_OFFSET = 0x60
SENDER_PENALTIES_OFFSET = 0x70

# Exact registration callsites in the LeagueScores source-row creation loop.
REGISTER_HALF_TIME_CALLSITE_VA = 0x522F5C
REGISTER_EXTRA_TIME_CALLSITE_VA = 0x522FAF
REGISTER_PENALTIES_CALLSITE_VA = 0x523002
REGISTER_FULL_TIME_CALLSITE_VA = 0x523055

# Sender list layout established by the typed sender constructors/destructors.
SENDER_LIST_SENTINEL_OFFSET = 0x08
SENDER_LIST_COUNT_OFFSET = 0x0C
RECEIVER_NODE_NEXT_OFFSET = 0x00
RECEIVER_NODE_PREV_OFFSET = 0x04
RECEIVER_NODE_OBJECT_OFFSET = 0x08
RECEIVER_CALLBACK_VTABLE_OFFSET = 0x04

# Representative exact forward-dispatch loops. The sender family uses the
# same sentinel-linked list contract; these addresses source-close forward
# head-to-tail traversal directly.
HALF_TIME_DISPATCH_LOOP_START_VA = 0x519A75
HALF_TIME_DISPATCH_LOOP_END_VA = 0x519AAE
EXTRA_TIME_DISPATCH_LOOP_START_VA = 0x519B00
EXTRA_TIME_DISPATCH_LOOP_END_VA = 0x519B1A
PENALTIES_DISPATCH_LOOP_START_VA = 0x519B5A
PENALTIES_DISPATCH_LOOP_END_VA = 0x519B74

# Per-row callback control creation order, already source-closed separately.
PHASE_ICON_CONSTRUCTOR_CALLSITE_VA = 0x51BB05
PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA = 0x51BB9A


@dataclass(frozen=True)
class PhaseReceiverFamily:
    event_name: str
    receiver_offset: int
    sender_offset: int
    registration_callsite_va: int

    def __post_init__(self) -> None:
        if not isinstance(self.event_name, str) or not self.event_name:
            raise FastViewPhaseReceiverOrderError("event name must be non-empty")
        for value in (
            self.receiver_offset,
            self.sender_offset,
            self.registration_callsite_va,
        ):
            if type(value) is not int or value < 0:
                raise FastViewPhaseReceiverOrderError(
                    "phase receiver source anchors must be non-negative integers"
                )


PHASE_RECEIVER_FAMILIES = (
    PhaseReceiverFamily(
        "EventHalfTime",
        SCORE_RECEIVER_HALF_TIME_OFFSET,
        SENDER_HALF_TIME_OFFSET,
        REGISTER_HALF_TIME_CALLSITE_VA,
    ),
    PhaseReceiverFamily(
        "EventExtraTime",
        SCORE_RECEIVER_EXTRA_TIME_OFFSET,
        SENDER_EXTRA_TIME_OFFSET,
        REGISTER_EXTRA_TIME_CALLSITE_VA,
    ),
    PhaseReceiverFamily(
        "EventPenalties",
        SCORE_RECEIVER_PENALTIES_OFFSET,
        SENDER_PENALTIES_OFFSET,
        REGISTER_PENALTIES_CALLSITE_VA,
    ),
    PhaseReceiverFamily(
        "EventFullTime",
        SCORE_RECEIVER_FULL_TIME_OFFSET,
        SENDER_FULL_TIME_OFFSET,
        REGISTER_FULL_TIME_CALLSITE_VA,
    ),
)


def source_row_registration_order(source_count: int) -> tuple[int, ...]:
    """Return the source-index order used while LeagueScores creates rows."""
    if type(source_count) is not int or not 1 <= source_count <= 12:
        raise FastViewPhaseReceiverOrderError(
            "LeagueScores receiver order requires one visible 1..12 row page"
        )
    return tuple(range(source_count))


def phase_broadcast_receiver_order(source_count: int) -> tuple[int, ...]:
    """Return callback row order for one typed phase-event broadcast.

    Tail insertion preserves construction order and sender traversal is
    head-to-tail, so one broadcast reaches rows in the same source order.
    """
    return source_row_registration_order(source_count)


def per_broadcast_control_append_sequence(
    source_count: int,
) -> tuple[tuple[str, int], ...]:
    """Model the native control-append order for one phase broadcast."""
    rows = phase_broadcast_receiver_order(source_count)
    return tuple(
        item
        for row in rows
        for item in (("icon", row), ("text", row))
    )


def aggregate_runtime_icon_text_order_recovered() -> bool:
    """Remain false across separate broadcasts.

    A later event may append another row's icon/text pair after controls created
    by an earlier event. The source closes per-broadcast row order, not one
    timeless family-wide all-icons/all-text edge.
    """
    return False


def phase_receiver_order_contract() -> dict:
    return {
        "row_build_loop_va": LEAGUE_SCORES_ROW_BUILD_LOOP_VA,
        "score_factory_callsite_va": LEAGUE_SCORES_SCORE_FACTORY_CALLSITE_VA,
        "receiver_list_append_helper_va": RECEIVER_LIST_APPEND_HELPER_VA,
        "receiver_node_data_copy_va": RECEIVER_NODE_DATA_COPY_VA,
        "sender_list_sentinel_offset": SENDER_LIST_SENTINEL_OFFSET,
        "sender_list_count_offset": SENDER_LIST_COUNT_OFFSET,
        "receiver_node_next_offset": RECEIVER_NODE_NEXT_OFFSET,
        "receiver_node_prev_offset": RECEIVER_NODE_PREV_OFFSET,
        "receiver_node_object_offset": RECEIVER_NODE_OBJECT_OFFSET,
        "receiver_callback_vtable_offset": RECEIVER_CALLBACK_VTABLE_OFFSET,
        "families": tuple(
            (
                family.event_name,
                family.receiver_offset,
                family.sender_offset,
                family.registration_callsite_va,
            )
            for family in PHASE_RECEIVER_FAMILIES
        ),
        "tail_insertion_recovered": True,
        "forward_sender_traversal_recovered": True,
        "source_row_registration_order_recovered": True,
        "per_broadcast_receiver_order_recovered": True,
        "per_callback_icon_before_text_recovered": True,
        "aggregate_runtime_icon_text_order_recovered": False,
        "flattened_runtime_phase_planes": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
