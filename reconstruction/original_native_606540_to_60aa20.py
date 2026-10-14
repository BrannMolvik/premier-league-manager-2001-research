"""Source-bounded original 606540(registered human FALSE) -> 60AA20.

Original static x86: 606618 calls 417340; 60661D JE 606CC1 skips
notification construction and calls 60AA20 at 606CCE. Subsequent 60AA20
requires its separately reached 417340 owner result, not an invented Inbox.
"""
from __future__ import annotations
from dataclasses import dataclass

from original_native_605f90_dispatch import (
    Original605F90PreDispatchReceipt, Original606540PreHumanReceipt,
)
from original_native_60aa20_pending_source import (
    Original60AA20Reached, Original60AA20Projection,
    Original60AA20SourceError, source_original_60aa20_project,
)


@dataclass(frozen=True)
class Original606540To60AA20NonhumanReached:
    predispatched_605f90: Original605F90PreDispatchReceipt
    prehuman_606540: Original606540PreHumanReceipt
    original_606540_417340_al: int
    original_60aa20_reached: Original60AA20Reached


def source_original_606540_nonhuman_pending_from_reached(
    reached: Original606540To60AA20NonhumanReached,
) -> Original60AA20Projection:
    """Reach the 60AA20 native source function only along the no-notice branch.

    The preceding 606540 native 417340 result must be exactly zero,
    eliminating unqualified notification constructors and queue writes.
    This projection still does not execute either native callback.
    """
    if not isinstance(reached, Original606540To60AA20NonhumanReached):
        raise Original60AA20SourceError("exact typed native 606540 continuation required")
    p = reached.predispatched_605f90
    h = reached.prehuman_606540
    n = reached.original_60aa20_reached
    if (not isinstance(p, Original605F90PreDispatchReceipt) or
            p.original_handler_choice.original_selected_handler_address != 0x606540 or
            p.original_native_handler_executed or p.live_game_state_updated or
            p.original_event_delivery_verified):
        raise Original60AA20SourceError("original selected handler 606540 required")
    if (not isinstance(h, Original606540PreHumanReceipt) or
            h.original_player_id != p.original_player_id or
            h.original_subtype != p.original_subtype or
            h.original_event_pending_or_delivered or h.live_game_state_updated or
            not h.original_handler_417340_callback_outstanding or
            not h.original_60aa20_descriptor_schedule_callback_outstanding):
        raise Original60AA20SourceError("matching outstanding pre-human original receipt required")
    expected_descriptor = bytearray(p.original_descriptor_at_subhandler_entry)
    if (len(expected_descriptor) != 12 or
            len(h.original_source_descriptor_before_417340) != 12):
        raise Original60AA20SourceError("original 606540 descriptor size required")
    expected_descriptor[5] = h.original_source_descriptor_before_417340[5]
    if bytes(expected_descriptor) != h.original_source_descriptor_before_417340:
        raise Original60AA20SourceError("606540 can change only descriptor+5 before 417340")
    if type(reached.original_606540_417340_al) is not int or reached.original_606540_417340_al != 0:
        raise Original60AA20SourceError("human 606540 notification branch not yet source-qualified")
    if (not isinstance(n, Original60AA20Reached) or
            n.player_id != p.original_player_id or
            n.descriptor_pointer != p.original_descriptor_pointer or
            n.descriptor_before != h.original_source_descriptor_before_417340 or
            n.duration_delta_arg != h.original_schedule_delta_from_rng or
            n.player77_decrement_base_arg != h.original_schedule_base_from_mutable_source or
            n.registered_417340_al != 0):
        raise Original60AA20SourceError("wrong native owner/descriptor/date args or changed nonhuman gate")
    return source_original_60aa20_project(n)
