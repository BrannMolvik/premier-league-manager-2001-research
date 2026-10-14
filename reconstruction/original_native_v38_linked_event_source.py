"""Original 0x513570 v+0x38 nonzero-event entry: bounded read-only source gate.

Private verified footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Static disassembly only. This gate NEVER executes event callbacks, scores,
rescheduling, world changes or returns successful native completion.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


class NativeV38LinkedEventSourceError(ValueError):
    pass


@dataclass(frozen=True)
class NativeV38LinkedEventEntry:
    primary_event_count: int
    secondary_event_count: int
    initial_event_pointer: int
    first_dispatch: str
    needs_original_event_callback_resolution: bool
    native_completion_proven: bool = False


def source_native_513570_nonzero_event_entry(
    *, original_context: bytes,
) -> NativeV38LinkedEventEntry:
    """Conservatively classify first original 0x513570 control-flow boundary.

    0x513577 reads context+D0C, +D10; if both zero returns immediately at
    0x5136B6. Else 0x513591 reads +B60. With D0C nonzero and +B60 nonzero,
    0x51359F calls 0x6326B0 on original event pointer, then may walk +34.
    With D0C zero and +B60 nonzero, 0x51360E calls 0x6326E0.
    This model cannot infer event callbacks or native match completion.
    """
    if type(original_context) is not bytes or len(original_context) < 0xD14:
        raise NativeV38LinkedEventSourceError(
            "exact original context bytes through +D10 are required")
    primary = unpack_from("<I", original_context, 0xD0C)[0]
    secondary = unpack_from("<I", original_context, 0xD10)[0]
    if not primary and not secondary:
        return NativeV38LinkedEventEntry(
            primary, secondary, 0, "zero_event_fast_return", False)
    pointer = unpack_from("<I", original_context, 0xB60)[0]
    if primary and pointer:
        branch = "original_6326b0_and_linked_event_callbacks"
    elif primary:
        branch = "no_head_primary_score_subtract_then_secondary_gate"
    elif pointer:
        branch = "original_6326e0_and_linked_event_callbacks"
    else:
        branch = "no_head_secondary_gate"
    return NativeV38LinkedEventEntry(
        primary, secondary, pointer, branch, True)


def source_original_v38_event_kind_predicates(
    *, original_event_record: bytes,
) -> tuple[bool, bool, bool, bool]:
    """Native 0x6326B0/0x632680/0x6326E0/0x632940 exact event fields.

    The first three compare signed-independent event DWORD+28 with 8,7,9.
    0x632940 invokes 0x6328F0 (signed 0..4 +28) and 0x632910
    (+24 equals 0 or 3); both must pass. These four functions are pure
    predicates in verified static disassembly, not world-mutating callbacks.
    Native list ownership and when score writes are committed are separate.
    """
    if type(original_event_record) is not bytes or len(original_event_record) < 0x2C:
        raise NativeV38LinkedEventSourceError(
            "actual original event bytes through +28 are required")
    kind = unpack_from("<I", original_event_record, 0x28)[0]
    owner = unpack_from("<I", original_event_record, 0x24)[0]
    return (kind == 8, kind == 7, kind == 9,
            kind <= 4 and owner in (0, 3))
