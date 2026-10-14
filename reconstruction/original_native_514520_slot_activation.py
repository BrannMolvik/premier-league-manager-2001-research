"""Read-only original 0x514520 native dated-event node activation decisions.

Canonical private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3;
STATIC disassembly only. 0x615C50 may invoke this after event/side flags.
The original calls the node virtual+18, potentially embedded SideRef v0
for event+14 and event+28. These can mutate the node+8/world; this model
requires the actual first getter's reached node+8 state to choose whether
the second getter ran, and NEVER fabricates either getter's effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


SOURCE_NATIVE_EVENT_SLOT_ACTIVATION_VA = 0x514520
SOURCE_NATIVE_EVENT_SLOT_FIRST_SIDE_V0_CALL_VA = 0x514550
SOURCE_NATIVE_EVENT_SLOT_SECOND_SIDE_V0_CALL_VA = 0x51455F
SOURCE_NATIVE_NODE_STATE_OFFSET = 0x08
SOURCE_NATIVE_EVENT_FLAGS_OFFSET = 0x44
SOURCE_NATIVE_FIRST_SIDE_REF_OFFSET = 0x14
SOURCE_NATIVE_SECOND_SIDE_REF_OFFSET = 0x28


class OriginalNative514520SourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalNative514520ActivationReceipt:
    original_branch: str
    original_event_virtual18_called: bool
    original_first_embedded_side_v0_called: bool
    original_second_embedded_side_v0_called: bool
    source_first_side_node_state_reached: int | None
    native_original_world_effects_reconstructed: bool = False
    native_gameplay_completion_proven: bool = False


def source_original_514520_reached_slot_activation(
    *, original_node_record_at_entry: bytes,
    original_reached_virtual18_event_pointer: int | None = None,
    original_event_record_after_virtual18: bytes | None = None,
    original_reached_node_state_after_first_embedded_side_v0: int | None = None,
) -> OriginalNative514520ActivationReceipt:
    """Mirror source 0x514524..0x514561 control flow, not callback effects.

    Native slot +8 nonzero returns before virtual18; otherwise it invokes
    node virtual18. Event null or bit5/bit6 abort before embedded side
    getters. It always calls event+14 SideRef v0 first on the remaining
    path, checks original node+8, and calls event+28 SideRef v0 ONLY if
    that actual reached first-side post-state is zero. No second post-state
    check occurs before original 514520 returns.
    """
    node=original_node_record_at_entry
    if type(node) is not bytes or len(node)<0x0C or not unpack_from("<I",node)[0]:
        raise OriginalNative514520SourceError(
            "actual original native slot node/vtable through +8 required")
    already=unpack_from("<I",node,SOURCE_NATIVE_NODE_STATE_OFFSET)[0]
    supplied=(original_reached_virtual18_event_pointer,
              original_event_record_after_virtual18,
              original_reached_node_state_after_first_embedded_side_v0)
    if already:
        if any(x is not None for x in supplied):
            raise OriginalNative514520SourceError(
                "native node+8 already set skips all original virtual callbacks")
        return OriginalNative514520ActivationReceipt(
            "already_activated_return",False,False,False,None)
    event_ptr=original_reached_virtual18_event_pointer
    if type(event_ptr) is not int or not 0<=event_ptr<=0xFFFFFFFF:
        raise OriginalNative514520SourceError(
            "actual reached source node v+18 EAX uint32 required")
    if event_ptr==0:
        if any(x is not None for x in supplied[1:]):
            raise OriginalNative514520SourceError(
                "null native v18 result skips event and embedded SideRef")
        return OriginalNative514520ActivationReceipt(
            "null_event_return",True,False,False,None)
    event=original_event_record_after_virtual18
    if type(event) is not bytes or len(event)<0x48:
        raise OriginalNative514520SourceError(
            "actual original event bytes through flags +44 required")
    flags=unpack_from("<I",event,SOURCE_NATIVE_EVENT_FLAGS_OFFSET)[0]
    if flags&0x20 or flags&0x40:
        if supplied[2] is not None:
            raise OriginalNative514520SourceError(
                "source event bit5/bit6 gate skips embedded SideRef callbacks")
        return OriginalNative514520ActivationReceipt(
            "event_flags_exclude_activation",True,False,False,None)
    if not unpack_from("<I",event,SOURCE_NATIVE_FIRST_SIDE_REF_OFFSET)[0]:
        raise OriginalNative514520SourceError(
            "actual original embedded first SideRef vtable pointer required")
    reached=original_reached_node_state_after_first_embedded_side_v0
    if type(reached) is not int or not 0<=reached<=0xFFFFFFFF:
        raise OriginalNative514520SourceError(
            "actual node+8 state AFTER first embedded SideRef v0 required")
    if reached:
        return OriginalNative514520ActivationReceipt(
            "first_side_v0_activated_node_skip_second",True,True,False,reached)
    if not unpack_from("<I",event,SOURCE_NATIVE_SECOND_SIDE_REF_OFFSET)[0]:
        raise OriginalNative514520SourceError(
            "actual original embedded second SideRef vtable pointer required")
    return OriginalNative514520ActivationReceipt(
        "first_side_zero_invoke_second_side_v0",True,True,True,0)


SOURCE_REACHED_EMBEDDED_SIDEREF_VTABLE_VA = 0x7C4D50
SOURCE_REACHED_TEMP_STANDALONE_SIDEREF_VTABLE_VA = 0x7C4D60
SOURCE_REACHED_EMBEDDED_SIDEREF_V0_VA = 0x510320
SOURCE_REACHED_STANDALONE_SIDEREF_V0_VA = 0x4F28A0


@dataclass(frozen=True)
class OriginalNativeEmbeddedSideV0Owner:
    original_source_side_offset: int
    original_source_vtable_va: int
    original_source_virtual0_va: int
    source_world_mutation_proven: bool = False


def source_original_514520_side_v0_owner_for_reached_event(
    *, original_reached_event_record: bytes,
    original_side_offset: int,
) -> OriginalNativeEmbeddedSideV0Owner:
    """Identify known original source v+0 owner without executing it.

    From canonical .rdata vtables 0x7C4D50 -> 0x510320, and
    0x7C4D60 -> 0x4F28A0. This does not claim a standalone SideRef
    would normally be embedded at +14/+28, nor return its club pointer.
    An unrecognized vtable has no source-qualified virtual dispatch.
    """
    if type(original_side_offset) is not int or original_side_offset not in (
            SOURCE_NATIVE_FIRST_SIDE_REF_OFFSET,
            SOURCE_NATIVE_SECOND_SIDE_REF_OFFSET):
        raise OriginalNative514520SourceError(
            "reached native source SideRef must be event+14 or event+28")
    rec=original_reached_event_record
    if type(rec) is not bytes or len(rec)<original_side_offset+4:
        raise OriginalNative514520SourceError(
            "actual reached source event SideRef vtable DWORD required")
    vtable=unpack_from("<I",rec,original_side_offset)[0]
    native={
        SOURCE_REACHED_EMBEDDED_SIDEREF_VTABLE_VA:
            SOURCE_REACHED_EMBEDDED_SIDEREF_V0_VA,
        SOURCE_REACHED_TEMP_STANDALONE_SIDEREF_VTABLE_VA:
            SOURCE_REACHED_STANDALONE_SIDEREF_V0_VA,
    }.get(vtable)
    if native is None:
        raise OriginalNative514520SourceError(
            "original embedded/standalone SideRef vtable has no verified v0 owner")
    return OriginalNativeEmbeddedSideV0Owner(original_side_offset,vtable,native)
