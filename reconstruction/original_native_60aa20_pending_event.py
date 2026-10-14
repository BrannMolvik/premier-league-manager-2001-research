"""Bounded original 606540 -> 60AA20 nonhuman pending player event.

The original 60AA20 human-owner branch can invoke 4D1190, native virtual
and RNG(5) to REDUCE duration; that branch is deliberately not modeled.
This is exact source byte projection ONLY for both original 417340 checks
returning AL=0, where 606540 skips manager notification and 60AA20
skips RNG(5). Its final 613EC0 native pending event insertion and lifetime
remain unexecuted: projection is not live GameState or delivered Inbox.

Private footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into,unpack_from

from original_native_605f90_dispatch import Original606540PreHumanReceipt
from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt


class Original60AA20SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original60AA20NonhumanReached:
    """Require both actually reached original read-only manager predicates."""
    original_606540_predispatch: Original606540PreHumanReceipt
    original_descriptor_at_60aa20: bytes
    original_descriptor_pointer: int
    original_player_at_60aa20: bytes
    original_registered_606540_proof: Original417340RegisteredUserReceipt
    original_registered_60aa20_proof: Original417340RegisteredUserReceipt
    original_raw_global_calendar_day_9847fc: int


@dataclass(frozen=True)
class Original60AA20PendingEventCandidate:
    """Original 7D7760 envelope; NOT yet inserted or delivered by Python."""
    original_event_vtable: int
    original_player_id: int
    original_due_day_raw: int
    original_subtype_status_5: int
    original_native_event_required: bool = True
    native_wrapper_allocated: bool = False
    original_947aa8_pending_queue_changed: bool = False
    original_delivery_verified: bool = False


@dataclass(frozen=True)
class Original60AA20NonhumanReceipt:
    original_player_id: int
    original_player_after_41a860_and_60aa20: bytes
    original_descriptor_after_60aa20: bytes
    original_pending_event_candidate: Original60AA20PendingEventCandidate
    original_duration_after_native_mitigation: int
    original_native_rng5_draws: int
    native_41a860_callback_executed: bool = False
    native_613ec0_callback_executed: bool = False
    live_game_state_updated: bool = False


def source_original_60aa20_nonhuman_pending_from_reached(
    reached: Original60AA20NonhumanReached,
) -> Original60AA20NonhumanReceipt:
    """Source 60AA20..60ABE7 with provably skipped human mitigation.

    Native 41A860 ORs player+14 bit0. Descriptor+0 receives original
    calendar raw day + 7*duration (DWORD wrapping). Native player+77
    reduces by source 606540 schedule base BYTE or clamps to one using
    signed comparison against the original base. Player+22 increments
    +1/+4/+8 by descriptor+5 original event type 0/1/2/3, wraps BYTE.

    Original 60AB77..60ABDD allocates 20-byte event type 7D7760, +4 due
    day, +8=1, +C pointer to 4-byte player ID, +10 event status, then
    queues at 947AA8 via 613EC0. The projection only returns what
    SHOULD be queued; no allocation or delivery has actually happened.
    """
    if not isinstance(reached,Original60AA20NonhumanReached):
        raise Original60AA20SourceError("actual original 60AA20 source input required")
    stage=reached.original_606540_predispatch
    if (not isinstance(stage,Original606540PreHumanReceipt) or
            stage.live_game_state_updated or
            not stage.original_handler_417340_callback_outstanding or
            not stage.original_60aa20_descriptor_schedule_callback_outstanding):
        raise Original60AA20SourceError("qualified original 606540 source stage required")
    pid=stage.original_player_id
    p=reached.original_player_at_60aa20
    if type(p) is not bytes or len(p)<0x250 or unpack_from("<H",p,4)[0]!=pid:
        raise Original60AA20SourceError("actual native player through+24C and +4 identity required")
    descriptor=reached.original_descriptor_at_60aa20
    if (type(descriptor) is not bytes or len(descriptor)!=12 or
        descriptor!=stage.original_source_descriptor_before_417340):
        raise Original60AA20SourceError("native 606540 descriptor changed on alleged nonhuman no-callback path")
    ptr=reached.original_descriptor_pointer
    if type(ptr) is not int or not 0<ptr<=0xffffffff or unpack_from("<I",p,0x24c)[0]!=ptr:
        raise Original60AA20SourceError("native player+24C descriptor pointer identity mismatch")
    if (unpack_from("<I",descriptor,8)[0]!=pid or
            descriptor[4]!=stage.original_subtype or
            descriptor[5] not in (0,1,2,3)):
        raise Original60AA20SourceError("native descriptor subtype and player ID mismatch")
    for label,proof in (
        ("606540",reached.original_registered_606540_proof),
        ("60AA20",reached.original_registered_60aa20_proof),
    ):
        if (not isinstance(proof,Original417340RegisteredUserReceipt) or
                proof.native_callback_executed or proof.live_game_state_updated or
                proof.original_native_player_at_call!=p or
                proof.original_native_player_id!=pid or
                proof.original_417340_return_al!=0):
            raise Original60AA20SourceError(f"actual original {label} nonhuman predicate required")
    date=reached.original_raw_global_calendar_day_9847fc
    if type(date) is not int or not 0<=date<=0xffffffff:
        raise Original60AA20SourceError("actual original raw 9847FC calendar DWORD required")
    duration=stage.original_schedule_delta_from_rng
    base=stage.original_schedule_base_from_mutable_source
    if (type(duration) is not int or not 1<=duration<=0x7fffffff
            or type(base) is not int or not -0x80000000<=base<=0x7fffffff):
        raise Original60AA20SourceError("source 606540 duration and mutable base required")
    due=(date+7*duration)&0xffffffff
    updated=bytearray(p)
    # Source 41A860 updates native status+14 first.
    pack_into("<I",updated,0x14,unpack_from("<I",p,0x14)[0]|1)
    previous_77=p[0x77]
    updated[0x77]=((previous_77-(base&0xff))&0xff) if previous_77>base else 1
    # 60AB2F jump-table: status0->+1, 1->+4, 2/3->+8.
    status=descriptor[5]
    updated[0x22]=(p[0x22]+(1 if status==0 else 4 if status==1 else 8))&0xff
    next_descriptor=bytearray(descriptor)
    pack_into("<I",next_descriptor,0,due)
    event=Original60AA20PendingEventCandidate(
        original_event_vtable=0x7d7760,
        original_player_id=pid,
        original_due_day_raw=due,
        original_subtype_status_5=status,
    )
    return Original60AA20NonhumanReceipt(
        pid,bytes(updated),bytes(next_descriptor),event,
        duration,original_native_rng5_draws=0,
    )
