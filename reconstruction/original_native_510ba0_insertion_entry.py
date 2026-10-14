"""Native 0x510BA0 calendar-node insertion entry, source-only.

Static original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This proves only branch eligibility and call sequence, not allocation success,
0x510380 object constructor, date insertion 0x615A60, native side effects
or any completion of the original fixture.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


class Original510BA0EntryError(ValueError):
    pass


@dataclass(frozen=True)
class Original510BA0EntryReceipt:
    original_branch: str
    original_node_virtual18_called: bool
    original_allocator_668140_called: bool
    original_requested_allocation_bytes: int
    original_510380_and_615a60_outstanding: bool
    native_world_effects_reconstructed: bool = False


def source_original_510ba0_calendar_node_insertion_entry(
    *, original_node_record: bytes,
    original_reached_virtual18_event_pointer: int | None = None,
    original_event_record_after_virtual18: bytes | None = None,
) -> Original510BA0EntryReceipt:
    """Source 0x510BA3..0x510BBD; strict actual reached owner values.

    node+8 nonzero skips virtual+18. Otherwise original virtual+18
    returns an event; original dereferences event+44 bit6 without a
    null guard. Caller must supply a nonzero reached source event pointer.
    If bit6 unset, original requests 0x1C bytes at 0x668140 and would
    construct/insert an event-linked object after the allocator returns.
    """
    node=original_node_record
    if type(node) is not bytes or len(node)<0x0C or not unpack_from("<I",node)[0]:
        raise Original510BA0EntryError(
            "actual original node vtable and state+8 through +0B required")
    state=unpack_from("<I",node,0x08)[0]
    if state:
        if (original_reached_virtual18_event_pointer is not None or
                original_event_record_after_virtual18 is not None):
            raise Original510BA0EntryError(
                "already-inserted node skips original v18 and allocation")
        return Original510BA0EntryReceipt("node_already_linked_return",False,False,0,False)
    pointer=original_reached_virtual18_event_pointer
    if type(pointer) is not int or not 0 < pointer <= 0xFFFFFFFF:
        raise Original510BA0EntryError(
            "actual nonnull original v18 event pointer required before native flags read")
    event=original_event_record_after_virtual18
    if type(event) is not bytes or len(event)<0x48:
        raise Original510BA0EntryError("actual original event through +44 required")
    flags=unpack_from("<I",event,0x44)[0]
    if flags & 0x40:
        return Original510BA0EntryReceipt("event_bit6_return",True,False,0,False)
    return Original510BA0EntryReceipt(
        "allocate_and_insert_unverified",True,True,0x1C,True)
