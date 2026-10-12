"""Source-limited original 0x947AA8 event-list lifecycle, without event execution.

Native 0x613E40 initializes the owner to enabled1, no nodes, processing0.
0x614080 drains queued events unless owner+0x0C is active: in that case
it sets deferred owner+0x10=1 and immediately returns. When processing,
each event's original vft+0x04 is queried once (twice if first result !=0),
then vft+0x18 is invoked once; returned zero unlinks the node, nonzero
retains it. It snapshots node.next before invoking callbacks.

Source 0x4DA4A5 -> 0x4C41C0 at TeamSelect Continue invokes 0x4E9830
with the ACTUAL owner+0x04 head, destroying all remaining nodes and
clearing original owner+0x04/+0x08, before 0x413830 competitions.

This is a read-only control-flow projection of supplied observed callback
outcomes. It cannot execute real polymorphic events, call the shared CRT,
mutate DBRUser/staff or claim normal startup queue population. A genuine
native callback may enqueue/reenter before a snapshot; that behavior must be
source-backed separately before integrating into the live GameState.
"""
from __future__ import annotations
from dataclasses import dataclass


class OriginalQueueLifecycleError(ValueError):
    """Unqualified native queue state or observed event callback result."""


@dataclass(frozen=True)
class OriginalQueueObservedEvent:
    source_event_identity: int
    first_virtual4_result: int
    repeated_virtual4_result: int | None
    virtual18_result: int


@dataclass(frozen=True)
class OriginalQueueOwnerProjection:
    enabled_flag: int
    source_event_identities: tuple[int, ...]
    processing_flag: int
    deferred_flag: int


@dataclass(frozen=True)
class OriginalQueueDrainProjection:
    owner: OriginalQueueOwnerProjection
    virtual_call_order: tuple[tuple[int, int], ...]
    removed_event_identities: tuple[int, ...]
    kept_event_identities: tuple[int, ...]


def original_queue_new_owner() -> OriginalQueueOwnerProjection:
    """Actual original 0x613E40 4-DWORD owner initialization."""
    return OriginalQueueOwnerProjection(1, (), 0, 0)


def _require_owner(owner: OriginalQueueOwnerProjection) -> None:
    if type(owner) is not OriginalQueueOwnerProjection:
        raise OriginalQueueLifecycleError("Expected original queue owner")
    if (owner.enabled_flag not in (0, 1)
            or owner.processing_flag not in (0, 1)
            or owner.deferred_flag not in (0, 1)
            or any(type(i) is not int or i < 0 for i in owner.source_event_identities)
            or len(set(owner.source_event_identities)) != len(owner.source_event_identities)):
        raise OriginalQueueLifecycleError("Source queue state is inconsistent")


def project_original_queue_drain(
    owner: OriginalQueueOwnerProjection,
    observed_events: tuple[OriginalQueueObservedEvent, ...],
) -> OriginalQueueDrainProjection:
    """Model only known callback-result branches; do not invoke callbacks.

    0x614080 defers when processing_flag=1, without inspecting nodes.
    Otherwise the input is a complete trace of callback results, already
    observed by a separate source-qualified native object model. No CRT
    draws are implied by this projection or suppressed within callbacks.
    """
    _require_owner(owner)
    if type(observed_events) is not tuple:
        raise OriginalQueueLifecycleError("Require the original ordered event trace")
    if owner.processing_flag:
        if observed_events:
            raise OriginalQueueLifecycleError("No callbacks run while queue is processing")
        return OriginalQueueDrainProjection(
            OriginalQueueOwnerProjection(
                owner.enabled_flag, owner.source_event_identities, 1, 1
            ), (), (), owner.source_event_identities
        )
    if (len(observed_events) != len(owner.source_event_identities)
            or any(type(ev) is not OriginalQueueObservedEvent
                   or ev.source_event_identity != expected
                   for ev, expected in zip(observed_events, owner.source_event_identities))):
        raise OriginalQueueLifecycleError("Original queue observation is incomplete or reordered")
    calls = []
    removed = []
    retained = []
    for ev in observed_events:
        for value in (ev.first_virtual4_result, ev.virtual18_result):
            if type(value) is not int:
                raise OriginalQueueLifecycleError("Original vtable result must be native integer")
        if ev.first_virtual4_result == 0:
            if ev.repeated_virtual4_result is not None:
                raise OriginalQueueLifecycleError("Native callback+4 not repeated after zero")
        elif type(ev.repeated_virtual4_result) is not int:
            raise OriginalQueueLifecycleError("Native callback+4 repeats for nonzero")
        calls.append((ev.source_event_identity, 0x04))
        if ev.first_virtual4_result != 0:
            calls.append((ev.source_event_identity, 0x04))
        calls.append((ev.source_event_identity, 0x18))
        (retained if ev.virtual18_result != 0 else removed).append(ev.source_event_identity)
    result_owner = OriginalQueueOwnerProjection(
        owner.enabled_flag, tuple(retained), 0, owner.deferred_flag
    )
    return OriginalQueueDrainProjection(
        result_owner, tuple(calls), tuple(removed), tuple(retained)
    )


def project_original_teamselect_continue_clear(
    owner: OriginalQueueOwnerProjection,
) -> OriginalQueueDrainProjection:
    """0x4C426E..0x4C4275 -> 0x4E9830 destroys remaining queued nodes.

    Caller MUST supply the real owner head as the original does. This
    reports the object identities passed to native deleting destructors;
    it does not execute their native destructor side effects, and it
    preserves unrelated owner processing/deferred flags.
    """
    _require_owner(owner)
    return OriginalQueueDrainProjection(
        OriginalQueueOwnerProjection(
            owner.enabled_flag, (), owner.processing_flag, owner.deferred_flag
        ), (), owner.source_event_identities, ()
    )
