"""Read-only original 0x513659..0x5136B6 bit2 tail with reached callbacks.

Original footballmanager.exe private SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
The original native 0x513F00/0x513ED0 execute virtual+48/+4C
getters (and possibly a linked +54 match owner), not simple field loads.
This module requires actual *reached* return values. It does not execute
the original random function 0x64D540, alter the caller's world or claim
that 0x513010, v38 wrapper, or v3C and PResults are completed.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_v38_score_stage import OriginalV38PreRngScoreStage


class OriginalV38Bit2TailError(ValueError):
    """Missing reached original return or incoherent native owner context."""


@dataclass(frozen=True)
class OriginalV38Bit2ReachedReceipt:
    original_native_match_vtable: int
    bit2_branch_entered: bool
    original_composite_getters_equal: bool | None
    optional_linked_owner_getters_equal: bool | None
    original_rng_called: bool
    projected_match_record_after_bit2: bytes
    native_match_completion_proven: bool = False


def _require_eax(value: int | None, name: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise OriginalV38Bit2TailError(
            f"actual reached original {name} EAX uint32 required")
    return value


def source_original_513570_bit2_reached_tail(
    *, original_stage: OriginalV38PreRngScoreStage,
    original_context: bytes,
    original_reached_513f00_eax: int | None = None,
    original_reached_513ed0_eax: int | None = None,
    original_reached_linked_v4c_eax: int | None = None,
    original_reached_self_v4c_eax: int | None = None,
    original_reached_64d540_2_eax: int | None = None,
) -> OriginalV38Bit2ReachedReceipt:
    """Bounded native branch after first event/score stage.

    Source 0x513659 checks match+44 bit2; if set, 0x513F00/ED0
    composite virtual results must match. If original context+D14 is
    nonzero, source calls linked match+54 v4C and self v4C, requiring
    those results to match too. Only then original 0x64D540(2) is
    called, whose returned EAX nonzero increments match+5A, else +5B.
    Counters are UINT8 and wrap, but no score WORD adjustment occurs
    here. Side effects of virtual methods and RNG state are *not*
    modeled or published.
    """
    if not isinstance(original_stage, OriginalV38PreRngScoreStage):
        raise OriginalV38Bit2TailError("source-qualified native pre-RNG stage required")
    record = original_stage.projected_match_record
    if type(record) is not bytes or len(record) < 0x5C:
        raise OriginalV38Bit2TailError("native match record through +5B required")
    if type(original_context) is not bytes or len(original_context) < 0xD52:
        raise OriginalV38Bit2TailError("actual same original context through +D50 required")
    first = unpack_from("<I", original_context, 0xD0C)[0]
    second = unpack_from("<I", original_context, 0xD10)[0]
    if (first, second) != (
        original_stage.original_primary_event_count,
        original_stage.original_secondary_event_count,
    ):
        raise OriginalV38Bit2TailError("reached native context event counts changed since score stage")
    if (first or second) and unpack_from("<I", original_context, 0xB60)[0] != (
            original_stage.original_head_pointer):
        raise OriginalV38Bit2TailError("reached native event-head owner changed since score stage")

    flags_bit2 = bool(record[0x44] & 4)
    should_enter = bool((first or second) and flags_bit2)
    if should_enter != original_stage.requires_513659_bit2_resolution:
        raise OriginalV38Bit2TailError("native pre-RNG stage bit2 gate inconsistent")
    extra = (
        original_reached_513f00_eax, original_reached_513ed0_eax,
        original_reached_linked_v4c_eax, original_reached_self_v4c_eax,
        original_reached_64d540_2_eax,
    )
    if not should_enter:
        if any(value is not None for value in extra):
            raise OriginalV38Bit2TailError(
                "source skips all bit2 getters/RNG; extra reached outputs invalid")
        return OriginalV38Bit2ReachedReceipt(
            original_stage.original_vtable_va, False, None, None, False, record)

    a = _require_eax(original_reached_513f00_eax, "0x513F00")
    b = _require_eax(original_reached_513ed0_eax, "0x513ED0")
    if a != b:
        if any(value is not None for value in extra[2:]):
            raise OriginalV38Bit2TailError(
                "source skips linked getters/RNG when composite helpers differ")
        return OriginalV38Bit2ReachedReceipt(
            original_stage.original_vtable_va, True, False, None, False, record)

    optional_owner_equal = None
    linked_required = unpack_from("<I", original_context, 0xD14)[0] != 0
    if linked_required:
        if not unpack_from("<I", record, 0x54)[0]:
            raise OriginalV38Bit2TailError(
                "original +D14 requests linked match+54 owner but pointer is null")
        linked_result = _require_eax(
            original_reached_linked_v4c_eax, "linked virtual+0x4C")
        self_result = _require_eax(
            original_reached_self_v4c_eax, "match virtual+0x4C")
        optional_owner_equal = linked_result == self_result
        if not optional_owner_equal:
            if original_reached_64d540_2_eax is not None:
                raise OriginalV38Bit2TailError(
                    "source skips RNG when linked getter results differ")
            return OriginalV38Bit2ReachedReceipt(
                original_stage.original_vtable_va, True, True, False, False, record)
    elif (original_reached_linked_v4c_eax is not None or
          original_reached_self_v4c_eax is not None):
        raise OriginalV38Bit2TailError(
            "source skips optional v4C getter comparison when +D14 is zero")

    _require_eax(original_reached_64d540_2_eax, "0x64D540(2)")
    offset = 0x5A if original_reached_64d540_2_eax else 0x5B
    staged = bytearray(record)
    staged[offset] = (staged[offset] + 1) & 0xFF
    return OriginalV38Bit2ReachedReceipt(
        original_stage.original_vtable_va, True, True,
        optional_owner_equal, True, bytes(staged),
    )
