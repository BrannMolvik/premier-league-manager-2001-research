"""Exact scalar projection of 0x60B7F0 from a native calculator snapshot.

This is deliberately NOT a complete 0xF4 captured report, nor an adapter from
scores/NormalMatchResult. Caller-supplied native memory remains private. The
unresolved helper-produced fields and variable arrays are not zero-filled.
"""
from dataclasses import dataclass


# (destination record offset, calculator offset, copied byte width).
# +0x98/+0x9A copy the low word of their source dwords.
NATIVE_CAPTURE_SCALAR_COPIES = (
    (0x30, 0xD84, 4), (0x34, 0xD88, 4),
    (0x38, 0xD8C, 4), (0x3C, 0xD90, 4),
    (0x40, 0xD9C, 1), (0x94, 0xB68, 4),
    (0x98, 0xFE0, 2), (0x9A, 0xFE4, 2),
    (0xA0, 0xD46, 1), (0xA1, 0xD45, 1), (0xA2, 0xD44, 1),
)


@dataclass(frozen=True)
class NativeCapturedScalar:
    report_offset: int
    calculator_offset: int
    value: bytes


def copy_native_capture_scalars(calculator: bytes) -> tuple[NativeCapturedScalar, ...]:
    """Read only the proven direct copies; never manufacture missing bytes."""
    if type(calculator) is not bytes:
        raise ValueError('Native calculator snapshot must be immutable bytes')
    required = max(offset + width for _, offset, width in NATIVE_CAPTURE_SCALAR_COPIES)
    if len(calculator) < required:
        raise ValueError('Native calculator snapshot is truncated')
    return tuple(
        NativeCapturedScalar(destination, source, calculator[source:source + width])
        for destination, source, width in NATIVE_CAPTURE_SCALAR_COPIES
    )
