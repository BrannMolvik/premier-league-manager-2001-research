"""Original source-specific queued user event: different tick vs drain callbacks.

Private original footballmanager.exe SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
No private executable is run by this source-only projection.

Native subtype event vtable 0x7BD564, its successful 0x7BD9B8 payload:
* 0x614080 queue drain invokes record +0x04 (0x40DFB0=>0), then
  record +0x18 (0x404610 -> payload+0x24=>0), and removes event.
* 0x613EE0 time-qualified loop invokes record +0x10 (0x5CFA20),
  which calls payload+0x3C (0x651E20=>1) then 0x413020 on true.
  That registered-human handler MAY enqueue another event; its live
  human list and branches are unknown.

The event built by 0x413020 stores global tick+1 at 0x413330.
These functions NEVER prove an event existed during a particular drain.
"""
from __future__ import annotations
from dataclasses import dataclass
from original_teamselect_queue_lifecycle import OriginalQueueObservedEvent

EVENT_VTABLE = 0x7BD564
PAYLOAD_VTABLE = 0x7BD9B8
SCHEDULED_EVENT_RECORD_SITE = 0x413330
QUEUE_DRAIN_VA = 0x614080
TIME_QUALIFIED_PROCESSOR_VA = 0x613EE0

class OriginalRegisteredHumanEventError(ValueError):
    pass

@dataclass(frozen=True)
class OriginalRegisteredHumanTimedCall:
    native_event_identity: int
    source_event_due_tick: int
    source_current_tick: int
    record_virtual10_invoked: bool
    payload_virtual3c_returned_true: bool
    registered_human_handler_413020_called: bool
    actual_followup_event_enqueued_verified: bool = False


def _source_event_id(native_event_identity: int,
                     native_event_vtable: int,
                     native_payload_vtable: int) -> None:
    if type(native_event_identity) is not int or native_event_identity < 0:
        raise OriginalRegisteredHumanEventError("Require known source event identity")
    if (type(native_event_vtable) is not int or native_event_vtable != EVENT_VTABLE
            or type(native_payload_vtable) is not int
            or native_payload_vtable != PAYLOAD_VTABLE):
        raise OriginalRegisteredHumanEventError("Require original specific successful user-event vtables")


def source_registered_human_event_queue_drain_trace(
    native_event_identity: int,
    *, native_event_vtable: int, native_payload_vtable: int,
) -> OriginalQueueObservedEvent:
    """Only the concrete subtype's vft return values; not queue membership.

    Caller MUST separately establish this event actually appears in the
    original observed owner+4 list. If present in 0x614080, the event's
    vft+4=>0 and vft+18=>payload+24=>0 cause removal. +0x10 does NOT run.
    """
    _source_event_id(native_event_identity,native_event_vtable,native_payload_vtable)
    return OriginalQueueObservedEvent(native_event_identity,0,None,0)


def project_source_registered_human_event_timed_call(
    native_event_identity: int, *, native_event_vtable: int,
    native_payload_vtable: int, native_event_due_tick: int,
    source_current_tick: int,
) -> OriginalRegisteredHumanTimedCall:
    """Only 0x613EE0 due-time test and type-qualified virtual call.

    0x613F00 signed DWORD compare skips event when due_tick > now.
    When due, vft+0x10 0x5CFA20 observes successful payload+0x3C
    returning one and invokes 0x413020. This DOES NOT prove 0x413020
    finds a matching human or enqueues anything; it might return early.
    """
    _source_event_id(native_event_identity,native_event_vtable,native_payload_vtable)
    if (type(native_event_due_tick) is not int or type(source_current_tick) is not int
            or not -(1<<31) <= native_event_due_tick < (1<<31)
            or not -(1<<31) <= source_current_tick < (1<<31)):
        raise OriginalRegisteredHumanEventError("Require native signed 32-bit due/current ticks")
    due=native_event_due_tick <= source_current_tick
    return OriginalRegisteredHumanTimedCall(
        native_event_identity,native_event_due_tick,source_current_tick,
        due,due,due,
    )


def source_new_registered_human_event_due_tick(global_event_tick: int) -> int:
    """0x413327..0x413330 stores original global 0x9847FC tick+1.

    Disallow signed32 rollover: source's signed due-time compare makes
    boundary ordering ambiguous without further native wrap analysis.
    """
    if (type(global_event_tick) is not int
            or not -(1<<31) <= global_event_tick < (1<<31)-1):
        raise OriginalRegisteredHumanEventError("Require signed tick without overflow")
    return global_event_tick+1
