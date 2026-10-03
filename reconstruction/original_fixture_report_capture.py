"""Exact scalar projection of 0x60B7F0 from a native calculator snapshot.

This is deliberately NOT a complete 0xF4 captured report, nor an adapter from
scores/NormalMatchResult. Caller-supplied native memory remains private. The
unresolved helper-produced fields and variable arrays are not zero-filled.
"""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LiveReportCompletionScalars:
    """Producer-retained calendar and D4C/D50, NOT a complete report.

    0x632550 -> 0x64CCD0 supplies the three calendar dwords. 0x60BA80
    consumes the live score accumulators, not a semantic/result score lookup.
    Other setup/caption/referee fields remain mandatory unresolved inputs.
    """
    calendar: tuple[int, int, int]
    scores: tuple[int, int]

    def __post_init__(self):
        if (type(self.calendar) is not tuple or len(self.calendar) != 3
                or any(type(v) is not int for v in self.calendar)
                or not 0 <= self.calendar[0] <= 8099):
            raise ValueError('Report calendar requires supported native date components')
        year, month, day = self.calendar
        lengths = (31, 29 if year >= 4 and year % 4 == 0 else 28,
                   31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        if not 1 <= month <= 12 or not 1 <= day <= lengths[month - 1]:
            raise ValueError('Invalid native report calendar components')
        if (type(self.scores) is not tuple or len(self.scores) != 2
                or any(type(v) is not int or not 0 <= v <= 0x7FFFFFFF for v in self.scores)):
            raise ValueError('Report scores require explicit live accumulator outputs')

    @classmethod
    def from_calculation(cls, played_on: date, scores: tuple[int, int]):
        if type(played_on) is not date:
            raise ValueError('Report date must be the calculation setup date')
        elapsed = (played_on - date(1900, 1, 1)).days
        if elapsed < 0:
            raise ValueError('Pre-1900 native report dates are not supported')
        # 0x64CCD0: OLE serial minus 2; special non-leap first four years,
        # then 1461-day cycles. This deliberately does NOT apply Gregorian
        # century rules to the native calendar tuple.
        if elapsed < 1460:
            year, remainder = divmod(elapsed, 365)
            leap = False
        else:
            cycles, remainder = divmod(elapsed - 1460, 1461)
            year = 4 + 4 * cycles
            leap = remainder < 366
            if not leap:
                extra_years, remainder = divmod(remainder - 366, 365)
                year += 1 + extra_years
        lengths = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        month = 1
        for length in lengths:
            if remainder < length:
                break
            remainder -= length
            month += 1
        return cls((year, month, remainder + 1), scores)

    @property
    def native_score_nibbles(self) -> int:
        return (self.scores[0] & 15) | ((self.scores[1] & 15) << 4)


# (destination record offset, calculator offset, copied byte width).
# +0x98/+0x9A copy the low word of their source dwords.
NATIVE_CAPTURE_SCALAR_COPIES = (
    (0x30, 0xD84, 4), (0x34, 0xD88, 4),
    (0x38, 0xD8C, 4), (0x3C, 0xD90, 4),
    (0x40, 0xD9C, 1), (0x94, 0xB68, 4),
    (0x98, 0xFE0, 2), (0x9A, 0xFE4, 2),
    (0xA0, 0xD46, 1), (0xA1, 0xD45, 1), (0xA2, 0xD44, 1),
)

# 0x632570 is a pointer getter (calculator +0xFEC), not a synthesized
# statistical summary. 0x60B7F0 copies its three dwords in this order.
NATIVE_CAPTURE_HELPER_SCALAR_COPIES = (
    (0x24, 0xFEC, 4), (0x28, 0xFF0, 4), (0x2C, 0xFF4, 4),
    (0x9C, 0x1154, 4),  # direct copy in 0x60B8D0
)


@dataclass(frozen=True)
class NativeCapturedScalar:
    report_offset: int
    calculator_offset: int
    value: bytes


def capture_gate_report_scalars(receipts) -> tuple[NativeCapturedScalar, ...]:
    """Project source-backed D84/D88/D8C/D90 without inventing D9C.

    The live gate path already owns the exact three attendance outputs and the
    completion-time seating-price scalar. This helper converts only those four
    proven values to the byte-exact direct-copy representation consumed by the
    eventual complete report assembler.
    """
    from gate_receipts import GateReceiptResult

    if type(receipts) is not GateReceiptResult:
        raise ValueError("Gate report scalars require a GateReceiptResult")
    if receipts.report_seating_price is None:
        raise ValueError("Gate report D88 requires the retained seating price")

    values = (
        (0x30, 0xD84, int(receipts.total_attendance)),
        (0x34, 0xD88, int(receipts.report_seating_price)),
        (0x38, 0xD8C, int(receipts.home_attendance)),
        (0x3C, 0xD90, int(receipts.visiting_attendance)),
    )
    if any(value < 0 or value > 0xFFFFFFFF for _, _, value in values):
        raise ValueError("Gate report scalar is outside unsigned dword range")
    return tuple(
        NativeCapturedScalar(destination, source, value.to_bytes(4, "little"))
        for destination, source, value in values
    )


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


def copy_native_capture_helper_scalars(calculator: bytes) -> tuple[NativeCapturedScalar, ...]:
    """Copy newly resolved helper fields without manufacturing their producers."""
    if type(calculator) is not bytes or len(calculator) < 0x1158:
        raise ValueError('Native calculator snapshot is mutable or truncated')
    return tuple(
        NativeCapturedScalar(destination, source, calculator[source:source + width])
        for destination, source, width in NATIVE_CAPTURE_HELPER_SCALAR_COPIES
    )


@dataclass(frozen=True)
class NativeCapturedPossession:
    triplets: bytes  # report +0xB4; count +0xB0 = len(triplets) // 3
    averages: bytes  # report +0x20/+0x21/+0x22


@dataclass(frozen=True)
class NativeCapturedGoal:
    player_index: int
    minute: int
    inversion: int


def capture_finalized_native_goals(records):
    """0x60BD90 consumes finalized native fields, stopping at kind 9.

    +4 selects the destination side, +8 the side-local participant, +0 the
    low-byte minute and +20 its low-bit inversion flag. No score totals or
    semantic own-goal reinterpretation supply these fields.
    """
    from native_compact_match import NativeCompactRecord
    if (type(records) is not tuple or any(type(r) is not NativeCompactRecord for r in records)
            or not any(r.kind == 7 for r in records)):
        raise ValueError('Goal capture requires a complete finalized native stream')
    if tuple(r.minute for r in records) != tuple(sorted(r.minute for r in records)):
        raise ValueError('Goal capture requires finalized native link order')
    goals = ([], [])
    for record in records:
        if record.kind == 9:
            break
        if 0 <= record.kind <= 4 and record.field(0x24) in (0, 3):
            side = record.field(4)
            if side not in (0, 1):
                raise ValueError('Invalid native goal destination side')
            goals[side].append(NativeCapturedGoal(record.field(8) & 0xFF,
                                                  record.minute & 0xFF,
                                                  record.field(0x20) & 1))
    return tuple(tuple(side) for side in goals)


def _captured_possession(triplets: bytes) -> NativeCapturedPossession:
    count = len(triplets) // 3
    second = sum(triplets[1::3]) // count
    third = sum(triplets[2::3]) // count
    return NativeCapturedPossession(triplets,
                                   bytes((second, third, (100 - second - third) & 0xFF)))


def capture_completed_possession_rows(
    rows: tuple[tuple[int, bytes], ...],
) -> NativeCapturedPossession:
    """Capture live normalized calculator rows, not a score-derived snapshot.

    Row minute identifies the exact calculator-array index (minute // 5).
    Require every ordinary / extra-time row in source order. The excluded
    boundary indices are never manufactured. An incomplete sequence rejects.
    Each row is territory / side-0 / neutral, matching the three native arrays.
    """
    normal = tuple(range(5, 45, 5)) + tuple(range(50, 90, 5))
    extra = (95, 100, 110, 115)
    if (type(rows) is not tuple or any(
            type(row) is not tuple or len(row) != 2
            or type(row[0]) is not int or type(row[1]) is not bytes
            or len(row[1]) != 3 or any(value > 100 for value in row[1])
            or row[1][1] + row[1][2] > 100 for row in rows)):
        raise ValueError('Capture requires immutable normalized calculator rows')
    minutes = tuple(row[0] for row in rows)
    if minutes not in (normal, normal + extra):
        raise ValueError('Capture requires complete source-ordered possession rows')
    groups = (rows[:8], rows[8:16])
    if minutes == normal + extra:
        groups += (rows[16:18], rows[18:20])
    triplets = bytes(
        (sum(row[1][component] for row in group) & 0xFFFFFFFF) // len(group)
        for group in groups for component in range(3)
    )
    return _captured_possession(triplets)


def copy_native_capture_possession(calculator: bytes) -> NativeCapturedPossession:
    """Exact 0x631270/0x631290 -> 0x60BBC0 capture, NOT five-minute rows.

    Native +0xFF8 equal to 18 selects two groups; any other value selects four.
    The first two groups average eight entries each, the last two average two.
    Boundary entries 0/9/18/21 are excluded by the source address ranges.
    This remains a snapshot projection, not a report constructor.
    """
    if type(calculator) is not bytes or len(calculator) < 0x112C:
        raise ValueError('Native calculator snapshot is mutable or truncated')

    def dword(offset):
        return int.from_bytes(calculator[offset:offset + 4], 'little')

    groups = ((1, 8), (10, 8), (19, 2), (22, 2))
    count = 2 if dword(0xFF8) == 18 else 4
    triplets = bytearray()
    for start, length in groups[:count]:
        for base in (0x100C, 0x106C, 0x10CC):
            total = sum(dword(base + index * 4)
                        for index in range(start, start + length)) & 0xFFFFFFFF
            triplets.append((total // length) & 0xFF)
    # 0x60BC84 discards the first component sum. Only the second/third
    # components are averaged; the last stored byte is their remainder.
    return _captured_possession(bytes(triplets))
