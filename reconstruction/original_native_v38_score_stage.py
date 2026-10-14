"""Source-exact *read-only* first scoring stage of original 0x513570.

Private original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
The only source-qualified caller here is the wrapped LeagueMatch v+0x38
0x5136C0, which first invokes 0x5112A0. Its exact two WORD score\nloads from context+D4C/+D50 are included before 0x513570.

This function NEVER publishes effects to a live GameState, claims 0x513570
fully returned, proves an actual reachable original event world, or invokes
unknown 0x64D540 RNG / virtual callbacks after 0x513659. Native source
0x513570..0x513659 is modeled on caller-supplied *original* owner records.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from
from typing import Mapping

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    source_original_leaguematch_process_owners_for_native_record,
)
from original_native_v38_linked_event_source import (
    source_original_v38_event_kind_predicates,
)


class OriginalV38ScoreStageError(ValueError):
    """Missing/malformed source owner, linked event or unsupported pathway."""


@dataclass(frozen=True)
class OriginalV38PreRngScoreStage:
    original_vtable_va: int
    original_head_pointer: int
    original_primary_event_count: int
    original_secondary_event_count: int
    visited_event_pointers: tuple[int, ...]
    final_cursor_pointer: int
    projected_match_record: bytes
    requires_513659_bit2_resolution: bool
    prior_wrapper_5112a0_effects_proven: bool = True
    native_match_completion_proven: bool = False


def _signed_byte(value: int) -> int:
    return value if value < 0x80 else value - 0x100


def source_original_513570_pre_rng_score_stage(
    *, original_match_record: bytes, original_context: bytes,
    original_linked_events: Mapping[int, bytes],
    max_linked_nodes: int = 4096,
) -> OriginalV38PreRngScoreStage:
    """Reproduce only native 0x513577..0x513659 bounded event/score writes.

    The input graph maps actual nonzero original 32-bit pointers to original
    event bytes through +0x34. All DEREFERENCED nodes must exist, be typed
    bytes, and have a valid 0x38-byte record; unvisited registry entries are
    irrelevant. Missing/looping pointers are source-unqualified and fail
    BEFORE returning any partial staged score.
    """
    if type(original_match_record) is not bytes or len(original_match_record) < 0x5C:
        raise OriginalV38ScoreStageError("original native match bytes through +0x5B required")
    try:
        owner = source_original_leaguematch_process_owners_for_native_record(
            original_match_record=original_match_record)
    except OriginalLeagueMatchProcessOwnerError as exc:
        raise OriginalV38ScoreStageError(str(exc)) from exc
    if owner.virtual38_cleanup_va != 0x5136C0:
        raise OriginalV38ScoreStageError(
            "source 0x513570 is reached here only via wrapped original v38 0x5136C0")
    if type(original_context) is not bytes or len(original_context) < 0xD52:
        raise OriginalV38ScoreStageError("original context bytes through +D50 required for 0x5112A0")
    if not isinstance(original_linked_events, Mapping):
        raise OriginalV38ScoreStageError("original pointer-to-event mapping required")
    if type(max_linked_nodes) is not int or not 1 <= max_linked_nodes <= 1_000_000:
        raise OriginalV38ScoreStageError("bounded max_linked_nodes must be positive integer")

    primary = unpack_from("<I", original_context, 0xD0C)[0]
    secondary = unpack_from("<I", original_context, 0xD10)[0]
    head = unpack_from("<I", original_context, 0xB60)[0] if primary or secondary else 0
    cursor = head
    projected = bytearray(original_match_record)
    # v38 0x5136C0 calls 0x5112A0 BEFORE 0x513570: unconditional\n    # overwrite of the two stored score WORDs from original context.\n    pack_into("<H", projected, 0x3C, unpack_from("<H", original_context, 0xD4C)[0])\n    pack_into("<H", projected, 0x3E, unpack_from("<H", original_context, 0xD50)[0])\n    visited: list[int] = []
    traversed: set[int] = set()

    def event(pointer: int) -> bytes:
        if type(pointer) is not int or not 0 < pointer <= 0xFFFFFFFF:
            raise OriginalV38ScoreStageError("original event pointer must be nonzero uint32")
        try:
            record = original_linked_events[pointer]
        except (KeyError, TypeError) as exc:
            raise OriginalV38ScoreStageError(
                "reached original +0x34 event pointer missing from supplied graph") from exc
        if type(record) is not bytes or len(record) < 0x38:
            raise OriginalV38ScoreStageError("reached original linked event bytes through +34 required")
        if pointer not in traversed:
            if len(traversed) >= max_linked_nodes:
                raise OriginalV38ScoreStageError("source linked event walk exceeded caller bound")
            traversed.add(pointer)
            visited.append(pointer)
        return record

    def follow(pointer: int) -> int:
        return unpack_from("<I", event(pointer), 0x34)[0]

    # The actual original 0x513570 walks from +B60, and the secondary walk
    # continues the same cursor that the primary walk left behind.
    if primary:
        if cursor:
            searched: set[int] = set()
            while cursor:
                if cursor in searched:
                    raise OriginalV38ScoreStageError("cyclic original primary type8 search")
                searched.add(cursor)
                record = event(cursor)
                if source_original_v38_event_kind_predicates(original_event_record=record)[0]:
                    break
                cursor = follow(cursor)
            if cursor:
                scored: set[int] = set()
                while cursor:
                    if cursor in scored:
                        raise OriginalV38ScoreStageError("cyclic original primary score walk")
                    scored.add(cursor)
                    record = event(cursor)
                    is8, is7, is9, qualifying = (
                        source_original_v38_event_kind_predicates(original_event_record=record))
                    if is7 or is9:
                        break
                    if qualifying:
                        target = 0x59 if unpack_from("<I", record, 0x04)[0] else 0x58
                        projected[target] = (projected[target] + 1) & 0xFF
                    cursor = follow(cursor)
        for counter_offset, score_offset in ((0x58, 0x3C), (0x59, 0x3E)):
            score = unpack_from("<H", projected, score_offset)[0]
            score = (score - _signed_byte(projected[counter_offset])) & 0xFFFF
            pack_into("<H", projected, score_offset, score)
    else:
        if cursor:
            searched: set[int] = set()
            while cursor:
                if cursor in searched:
                    raise OriginalV38ScoreStageError("cyclic original secondary type9 search")
                searched.add(cursor)
                record = event(cursor)
                if source_original_v38_event_kind_predicates(original_event_record=record)[2]:
                    break
                cursor = follow(cursor)

    if secondary and cursor:
        # Source immediately stops this loop if the carried-forward cursor
        # points at type7, and does NOT restart at the original +B60 head.
        if not source_original_v38_event_kind_predicates(
                original_event_record=event(cursor))[1]:
            scored: set[int] = set()
            while cursor:
                if cursor in scored:
                    raise OriginalV38ScoreStageError("cyclic original secondary score walk")
                scored.add(cursor)
                record = event(cursor)
                if source_original_v38_event_kind_predicates(
                        original_event_record=record)[3]:
                    target = 0x5B if unpack_from("<I", record, 0x04)[0] else 0x5A
                    projected[target] = (projected[target] + 1) & 0xFF
                cursor = follow(cursor)

    return OriginalV38PreRngScoreStage(
        original_vtable_va=owner.source_vtable_va,
        original_head_pointer=head,
        original_primary_event_count=primary,
        original_secondary_event_count=secondary,
        visited_event_pointers=tuple(visited),
        final_cursor_pointer=cursor,
        projected_match_record=bytes(projected),
        requires_513659_bit2_resolution=bool((primary or secondary) and projected[0x44] & 4),
    )
