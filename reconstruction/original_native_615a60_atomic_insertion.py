"""Original 0x510BA0 -> 0x615A60 native calendar insertion, atomic projection.

Verified original footballmanager.exe private SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
STATIC source 0x510BA0, 0x510300, 0x510380, 0x514100,
0x615890 and 0x615A60 only. This model neither allocates native
memory nor calls source virtual getters / changes live GameState.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from
from typing import Sequence

from original_native_615890_slot_window import Original615890ReachedWindow


class OriginalNativeCalendarInsertionError(ValueError):
    pass


NATIVE_PRIMARY_CALENDAR_VA = 0x947AD8
NATIVE_SECONDARY_CALENDAR_VA = 0x947AF0
NATIVE_ALLOCATED_LINK_NODE_VTABLE_VA = 0x7C9FE8
NATIVE_ALLOCATED_LINK_NODE_V18_VA = 0x514100
NATIVE_DAY_GLOBAL_VA = 0x9847FC


@dataclass(frozen=True)
class OriginalNativeCalendarInsertionReceipt:
    source_calendar_va: int
    source_selected_calendar_va: int
    original_inserted_node_pointer: int
    original_outer_node_pointer: int
    original_requested_index: int
    original_first_search_index: int
    original_reached_search_indices: tuple[int, ...]
    original_selected_slot_index: int
    original_old_slot_head_pointer: int
    original_inserted_node_native_signed_index: int
    projected_source_slot_vector: bytes
    projected_inserted_node_record: bytes
    native_world_write_committed: bool = False
    original_virtual_callbacks_executed: bool = False
    native_match_completion_proven: bool = False


def _signed32(u: int) -> int:
    return u if u < 0x80000000 else u - 0x100000000


def _int32(value: int, name: str) -> int:
    if type(value) is not int or not -(1 << 31) <= value < (1 << 31):
        raise OriginalNativeCalendarInsertionError(name + " must be signed int32")
    return value


def _ptr(value: int, name: str) -> int:
    if type(value) is not int or not 0 < value <= 0xFFFFFFFF:
        raise OriginalNativeCalendarInsertionError(name + " must be nonzero uint32")
    return value


def _registry(raw: bytes, name: str) -> tuple[int, int, int]:
    if type(raw) is not bytes or len(raw) < 0x10:
        raise OriginalNativeCalendarInsertionError(name + " original +0/+4/+8/+C bytes required")
    base = unpack_from("<I", raw, 0)[0]
    count = unpack_from("<i", raw, 4)[0]
    offset = unpack_from("<i", raw, 8)[0]
    if not base or base & 3 or count <= 0 or count > 0x100000 or offset < 0:
        raise OriginalNativeCalendarInsertionError(name + " source slot base/count/day offset invalid")
    if base + count * 4 > 0x100000000:
        raise OriginalNativeCalendarInsertionError(name + " source slot pointer exceeds 32 bits")
    return base, count, offset


def source_original_615a60_atomic_link_projection(
    *,
    original_source_calendar_va: int,
    original_source_calendar_record: bytes,
    original_selected_calendar_record: bytes,
    original_source_slot_vector: bytes,
    original_global_day_9847fc: int,
    original_outer_node_pointer: int,
    original_outer_node_after_510ba0: bytes,
    original_inserted_link_pointer: int,
    original_inserted_link_after_510380: bytes,
    original_reached_virtual18_event_pointer: int,
    original_event_record_after_virtual18: bytes,
    original_reached_615890_windows: Sequence[Original615890ReachedWindow],
    max_searches: int = 4096,
) -> OriginalNativeCalendarInsertionReceipt:
    """Project *only* the 0x615A60 source slot/head/inserted-node writes.

    0x510BA0 supplies outer node+0x10 + 7 as initial index. Original
    0x615A60 clamps it against (global 0x9847FC - calendar+8 + 1),
    repeatedly invokes 0x615890 until its first false result, and on
    each true callback starts the next query at matched_index + 2.

    When the last 0x615890 returns false, 0x615A60 reads original new
    link v+0x18 (0x514100 forwarding outer v+0x18), calls 0x510300
    with that reached event, and writes new link+0x10 from the slot
    pointer difference against the *selected event's* registry base.
    This can differ from the source insertion registry. It then writes
    new link+4 = old slot head and source slot head = link pointer.
    Native allocator/virtual callbacks may mutate memory separately;
    this projection never asserts those effects were reproduced.
    """
    if original_source_calendar_va not in (
        NATIVE_PRIMARY_CALENDAR_VA, NATIVE_SECONDARY_CALENDAR_VA
    ) or type(original_source_calendar_va) is not int:
        raise OriginalNativeCalendarInsertionError(
            "source 510300 registry identity must be original primary/secondary VA")
    base, count, day_offset = _registry(
        original_source_calendar_record, "source calendar")
    selected_base, _selected_count, _selected_offset = _registry(
        original_selected_calendar_record, "event selected calendar")
    slots = original_source_slot_vector
    if type(slots) is not bytes or len(slots) != count * 4:
        raise OriginalNativeCalendarInsertionError(
            "exact source calendar pointer vector count*4 required")
    current_day = _int32(original_global_day_9847fc, "source day global 0x9847FC")
    sourceptr = _ptr(original_outer_node_pointer, "outer native node pointer")
    linkptr = _ptr(original_inserted_link_pointer, "new original link pointer")
    if sourceptr == linkptr:
        raise OriginalNativeCalendarInsertionError("inserted link cannot own itself")
    source_node = original_outer_node_after_510ba0
    link = original_inserted_link_after_510380
    if type(source_node) is not bytes or len(source_node) < 0x14 or not unpack_from("<I", source_node)[0]:
        raise OriginalNativeCalendarInsertionError("original outer source node through +0x10 required")
    if type(link) is not bytes or len(link) < 0x1C:
        raise OriginalNativeCalendarInsertionError("actual original allocated 0x1C link required")
    if unpack_from("<I", source_node, 8)[0] != linkptr:
        raise OriginalNativeCalendarInsertionError(
            "original 0x510BA0 source node+8 must link new native allocation")
    if unpack_from("<I", link)[0] != NATIVE_ALLOCATED_LINK_NODE_VTABLE_VA:
        raise OriginalNativeCalendarInsertionError(
            "actual original 0x510BA0 allocated link vtable required")
    if unpack_from("<I", link, 0x14)[0] != sourceptr:
        raise OriginalNativeCalendarInsertionError(
            "0x510BA0 new link+14 must own outer node pointer")
    if unpack_from("<I", link, 0x08)[0] or unpack_from("<I", link, 0x10)[0] != 0xFFFFFFFF:
        raise OriginalNativeCalendarInsertionError(
            "actual 0x510380 freshly constructed link+8 zero/+10 -1 required")
    if unpack_from("<I", link, 0x0C)[0] & 1 != int(
        original_source_calendar_va == NATIVE_SECONDARY_CALENDAR_VA):
        raise OriginalNativeCalendarInsertionError(
            "0x510380 inserted link selector disagrees with original source registry")
    eventptr = _ptr(original_reached_virtual18_event_pointer, "reached link v18 event pointer")
    event = original_event_record_after_virtual18
    if type(event) is not bytes or len(event) < 0x10:
        raise OriginalNativeCalendarInsertionError(
            "actual reached virtual+18 event selector DWORD+0x0C required")
    selected_va = (NATIVE_SECONDARY_CALENDAR_VA
                   if event[0x0C] & 1 else NATIVE_PRIMARY_CALENDAR_VA)
    if selected_va == original_source_calendar_va:
        if selected_base != base:
            raise OriginalNativeCalendarInsertionError(
                "same source event calendar must retain identical original slot base")
    # Require the exact selector VA's original record via caller provenance;
    # merely supplying a made-up arbitrary pointer is not owner identity.
    # For cross-calendar event, selected source base can differ.
    if type(original_reached_615890_windows) not in (tuple, list):
        raise OriginalNativeCalendarInsertionError(
            "ordered original 0x615890 callback receipts required")
    if type(max_searches) is not int or not 1 <= max_searches <= 100000:
        raise OriginalNativeCalendarInsertionError("positive bounded native search count required")
    if not original_reached_615890_windows or len(original_reached_615890_windows) > max_searches:
        raise OriginalNativeCalendarInsertionError(
            "native original 0x615890 loop must terminate within caller bound")
    original_idx = _signed32(unpack_from("<I", source_node, 0x10)[0])
    request = original_idx + 7
    lower = current_day - day_offset + 1
    if not -0x80000000 <= request <= 0x7FFFFFFF or not -0x80000000 <= lower <= 0x7FFFFFFF:
        raise OriginalNativeCalendarInsertionError(
            "native initial signed index arithmetic overflow")
    start = max(request, lower)
    if start < 0 or start > 0x7FFFFFFD:
        raise OriginalNativeCalendarInsertionError(
            "source native first slot index unqualified signed negative/overflow")
    cursor = start
    queries = []
    for i, receipt in enumerate(original_reached_615890_windows):
        if not isinstance(receipt, Original615890ReachedWindow):
            raise OriginalNativeCalendarInsertionError(
                "source native 0x615890 receipt class required")
        expected_begin = cursor - 1 if cursor else 0
        expected_end = min(cursor + 2, count)
        if (receipt.first_source_index != expected_begin or
                receipt.end_exclusive_index != expected_end or
                receipt.original_returned_eax != int(receipt.first_matched_index is not None)):
            raise OriginalNativeCalendarInsertionError(
                "original reached 615890 receipt disagrees with actual input window")
        if receipt.first_matched_index is not None:
            if (receipt.first_matched_index not in receipt.called_615790_indices or
                    not expected_begin <= receipt.first_matched_index < expected_end or
                    i == len(original_reached_615890_windows)-1):
                raise OriginalNativeCalendarInsertionError(
                    "native successful window requires source first match and a next search")
            cursor = receipt.first_matched_index + 2
            if cursor > 0x7FFFFFFD:
                raise OriginalNativeCalendarInsertionError("source +2 cursor signed overflow")
        elif i != len(original_reached_615890_windows)-1:
            raise OriginalNativeCalendarInsertionError(
                "source 615A60 stops at first false window; extra source calls invalid")
        queries.append(cursor if receipt.first_matched_index is None
                       else cursor - 2)
    if not 0 <= cursor < count:
        raise OriginalNativeCalendarInsertionError(
            "native source 615A60 final slot outside valid supplied source vector")
    chosen_slot_va = base + 4 * cursor
    if chosen_slot_va > 0xFFFFFFFF:
        raise OriginalNativeCalendarInsertionError("native chosen slot address overflow")
    old = unpack_from("<I", slots, cursor * 4)[0]
    if old == linkptr or any(
        unpack_from("<I", slots, j * 4)[0] == linkptr for j in range(count)):
        raise OriginalNativeCalendarInsertionError(
            "new native allocation pointer is already a calendar list head")
    # Source 0x615ABE subtracts the event-selected 0x510300 calendar
    # vector base, then arithmetic SAR2 to put a signed index in link+10.
    # Never replace it with the source registry index when bases differ.
    delta = (chosen_slot_va - selected_base) & 0xFFFFFFFF
    native_idx = _signed32(delta) >> 2
    staged_link = bytearray(link)
    staged_slots = bytearray(slots)
    pack_into("<I", staged_link, 0x10, native_idx & 0xFFFFFFFF)
    pack_into("<I", staged_link, 4, old)
    pack_into("<I", staged_slots, cursor*4, linkptr)
    return OriginalNativeCalendarInsertionReceipt(
        source_calendar_va=original_source_calendar_va,
        source_selected_calendar_va=selected_va,
        original_inserted_node_pointer=linkptr,
        original_outer_node_pointer=sourceptr,
        original_requested_index=request,
        original_first_search_index=start,
        original_reached_search_indices=tuple(queries),
        original_selected_slot_index=cursor,
        original_old_slot_head_pointer=old,
        original_inserted_node_native_signed_index=native_idx,
        projected_source_slot_vector=bytes(staged_slots),
        projected_inserted_node_record=bytes(staged_link),
    )
