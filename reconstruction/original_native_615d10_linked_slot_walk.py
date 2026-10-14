"""Native 0x615D10 calendar date scan with source-reached mutable slot snapshots.

Original private verified footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
The 0x615D10 outer loop calls 0x615C50, which can mutate SideRef
getters and node world. This source projection uses actual reached
per-step original registry snapshots, slot-head and returned EAX pointer;
it does not invent those callbacks or publish a real GameState mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_v3c_calendar_second_pass import (
    OriginalNative615D10DateWindow,
    source_original_615d10_calendar_date_window,
)
from original_native_v3c_reschedule_gate import OriginalV3CRescheduleGateError


class Original615D10SlotWalkError(ValueError):
    pass


@dataclass(frozen=True)
class Original615D10ReachedStep:
    original_registry_at_slot_call: bytes
    original_slot_head_pointer: int
    original_reached_615c50_eax: int
    original_registry_after_zero_result: bytes | None = None


@dataclass(frozen=True)
class Original615D10SlotWalkReceipt:
    original_calendar_registry_va: int
    original_requested_date_index: int
    original_reached_slot_indices: tuple[int, ...]
    original_reached_slot_addresses: tuple[int, ...]
    original_returned_native_node_pointer: int
    source_outer_scan_complete: bool = True
    original_615c50_mutating_callbacks_reconstructed: bool = False
    native_match_world_updated: bool = False


def _header(raw: bytes, owner: str) -> tuple[int, int, int]:
    if type(raw) is not bytes or len(raw) < 0x0C:
        raise Original615D10SlotWalkError(
            owner + " original registry bytes through +8 required")
    return (unpack_from("<I",raw,0)[0],
            unpack_from("<i",raw,4)[0],
            unpack_from("<I",raw,8)[0])


def _uint(value: int, owner: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise Original615D10SlotWalkError(owner + " original uint32 required")
    return value


def source_original_615d10_linked_slot_walk_from_reached(
    *, original_date_window: OriginalNative615D10DateWindow,
    original_reached_slot_calls: tuple[Original615D10ReachedStep, ...],
    max_slots: int = 4096,
) -> Original615D10SlotWalkReceipt:
    """Source 0x615D1A..0x615D52 outer loop, no invented 0x615C50 effects.

    Original date-base subtraction runs only once. On every iteration
    0x615D2E reloads registry+0 slot-vector base and invokes 0x615C50;
    after a zero return 0x615D44 reloads registry+4 signed count, THEN
    increments slot index and decides whether to continue. Distinct
    post-callback registry records are needed to source-qualify mutation.
    """
    window=original_date_window
    if not isinstance(window,OriginalNative615D10DateWindow):
        raise Original615D10SlotWalkError(
            "typed original 615D10 reached date window required")
    if type(original_reached_slot_calls) is not tuple:
        raise Original615D10SlotWalkError(
            "ordered original 615C50 reached step tuple required")
    if type(max_slots) is not int or not 1 <= max_slots <= 1_000_000:
        raise Original615D10SlotWalkError("bounded source slot count required")
    if window.negative_source_slot_index_unqualified or (
            window.null_original_slot_vector_unqualified):
        raise Original615D10SlotWalkError(
            "negative source calendar slot / null pointer unqualified")
    if not window.source_would_enter_615c50_search:
        if original_reached_slot_calls:
            raise Original615D10SlotWalkError(
                "original 615D10 skips 615C50 when date outside calendar")
        return Original615D10SlotWalkReceipt(
            window.original_calendar_registry_va,
            window.original_requested_date_index, (), (), 0)
    if not original_reached_slot_calls or len(original_reached_slot_calls)>max_slots:
        raise Original615D10SlotWalkError(
            "actual bounded reached original 615C50 slot calls required")
    idx=window.source_date_delta_signed
    prev_after=None
    indices=[]
    addresses=[]
    result=0
    done=False
    for step in original_reached_slot_calls:
        if not isinstance(step,Original615D10ReachedStep):
            raise Original615D10SlotWalkError(
                "actual source 615C50 reached step type required")
        base,count,datebase=_header(step.original_registry_at_slot_call,
                                     "at 615C50")
        if not base or base&3:
            raise Original615D10SlotWalkError(
                "original calendar slot base pointer invalid")
        if not indices:
            if ((base,count,datebase) != (
                 window.source_calendar_slots_base_pointer,
                 window.source_calendar_capacity_signed,
                 window.source_calendar_date_base_raw)):
                raise Original615D10SlotWalkError(
                    "first reached 615D10 registry does not match original window")
        elif prev_after is not None and (
                step.original_registry_at_slot_call[:12]!=prev_after[:12]):
            raise Original615D10SlotWalkError(
                "registry changed between native 615D10 iterations without source callback")
        if not 0 <= idx < count:
            raise Original615D10SlotWalkError(
                "reached original 615C50 index outside current signed registry count")
        slotaddr=base+idx*4
        if slotaddr > 0xFFFFFFFF:
            raise Original615D10SlotWalkError(
                "original slot pointer address overflow")
        _uint(step.original_slot_head_pointer,"reached slot head")
        eax=_uint(step.original_reached_615c50_eax,"reached 615C50 EAX")
        if not step.original_slot_head_pointer and eax:
            raise Original615D10SlotWalkError(
                "original empty 615C50 slot cannot return a node")
        indices.append(idx)
        addresses.append(slotaddr)
        if eax:
            if step.original_registry_after_zero_result is not None:
                raise Original615D10SlotWalkError(
                    "original 615D10 stops on nonzero EAX without reading count")
            result=eax
            done=True
            break
        after=step.original_registry_after_zero_result
        if after is None:
            raise Original615D10SlotWalkError(
                "original 615D10 zero return rereads registry signed count")
        beforebase,postcount,postdate=_header(after,"post-615C50 count")
        if beforebase != base and not beforebase:
            raise Original615D10SlotWalkError(
                "original calendar registry base became null after callback")
        idx+=1
        prev_after=after
        if idx >= postcount:
            done=True
            break
    if not done or len(indices) != len(original_reached_slot_calls):
        raise Original615D10SlotWalkError(
            "missing or surplus source reached 615C50 callbacks")
    return Original615D10SlotWalkReceipt(
        window.original_calendar_registry_va,
        window.original_requested_date_index,tuple(indices),
        tuple(addresses),result)
