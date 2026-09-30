"""Faithful original FM2001 EA444 two-pass inverse 8x8 transform.

Transcribed from the canonical Loader444 routines 0x7B9360 (first pass) and
0x7B94C0 (second pass). Integer operations use signed 32-bit x86 wrap; the
odd-part constants are the exact initialized TQIA_DAT float32 values. The x87
path runs under the program's normal 0x027F control word (extended precision,
round-to-nearest/even). This module stops at transformed component samples;
RGB packing/clipping/dithering remains a separate Loader444 stage.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from ea444_tables import EA444Tables

MASK32 = 0xFFFFFFFF
SQRT_HALF_Q31 = 0x5A82799A
TQIA_TRANSFORM_RAW = bytes.fromhex("9a79825ad48b0a3f753da73f15efc33e")


class EA444InverseTransformError(ValueError):
    pass


def _i32(value: int) -> int:
    value &= MASK32
    return value - (1 << 32) if value & 0x80000000 else value


def _add(a: int, b: int) -> int:
    return _i32(_i32(a) + _i32(b))


def _sub(a: int, b: int) -> int:
    return _i32(_i32(a) - _i32(b))


def _imul_sqrt_half(value: int) -> int:
    """Mirror IMUL 0x5A82799A; ADD EAX,EAX; ADC EDX,EDX."""
    product = _i32(value) * _i32(SQRT_HALF_Q31)
    low = product & MASK32
    high = (product >> 32) & MASK32
    doubled_low = low + low
    carry = 1 if doubled_low > MASK32 else 0
    return _i32((high + high + carry) & MASK32)


def _float32_fraction(raw: bytes) -> Fraction:
    if len(raw) != 4:
        raise EA444InverseTransformError("Expected one float32 source constant")
    bits = int.from_bytes(raw, "little")
    sign = -1 if bits >> 31 else 1
    exponent = (bits >> 23) & 0xFF
    fraction = bits & 0x7FFFFF
    if exponent in (0, 0xFF):
        raise EA444InverseTransformError(
            "EA444 transform constant is not finite normal float32"
        )
    significand = (1 << 23) | fraction
    power = exponent - 127 - 23
    result = Fraction(sign * significand, 1)
    return result * (1 << power) if power >= 0 else result / (1 << -power)


def _round_nearest_even(value: Fraction) -> int:
    numerator, denominator = value.numerator, value.denominator
    sign = -1 if numerator < 0 else 1
    numerator = abs(numerator)
    quotient, remainder = divmod(numerator, denominator)
    twice = remainder * 2
    if twice > denominator or (twice == denominator and quotient & 1):
        quotient += 1
    return sign * quotient


def _fistp_i32(value: Fraction) -> int:
    rounded = _round_nearest_even(value)
    if not -(1 << 31) <= rounded < (1 << 31):
        return -(1 << 31)
    return rounded


def _fistp_i64_low_i32(value: Fraction) -> int:
    rounded = _round_nearest_even(value)
    if not -(1 << 63) <= rounded < (1 << 63):
        rounded = -(1 << 63)
    return _i32(rounded)


@dataclass(frozen=True)
class EA444TransformConstants:
    odd_1: Fraction
    odd_2: Fraction
    odd_3: Fraction

    @classmethod
    def from_tables(cls, tables: EA444Tables) -> "EA444TransformConstants":
        raw = tables.raw_section[0x10:0x20]
        if raw != TQIA_TRANSFORM_RAW:
            raise EA444InverseTransformError(
                "Original TQIA_DAT inverse-transform constants differ from canonical source"
            )
        if int.from_bytes(raw[:4], "little") != SQRT_HALF_Q31:
            raise EA444InverseTransformError(
                "Original fixed-point transform constant changed"
            )
        return cls(
            _float32_fraction(raw[4:8]),
            _float32_fraction(raw[8:12]),
            _float32_fraction(raw[12:16]),
        )


def _inverse_1d_general(
    source: tuple[int, ...],
    constants: EA444TransformConstants,
    *,
    second_pass: bool,
) -> tuple[int, ...]:
    if len(source) != 8:
        raise EA444InverseTransformError(
            "EA444 inverse pass requires exactly 8 values"
        )
    s = tuple(_i32(value) for value in source)

    odd35_sum = _add(s[3], s[5])
    a = _sub(s[5], s[3])
    odd17_sum = _add(s[7], s[1])
    b = _sub(s[1], s[7])
    odd_total = _add(odd35_sum, odd17_sum)
    odd_difference = _sub(odd17_sum, odd35_sum)

    mix = Fraction(a + b)
    fp_a = Fraction(a) * constants.odd_1 + mix * constants.odd_3
    fp_b = Fraction(b) * constants.odd_2 - mix * constants.odd_3
    if second_pass:
        rounded_a = _fistp_i64_low_i32(fp_a)
        rounded_b = _fistp_i64_low_i32(fp_b)
    else:
        rounded_a = _fistp_i32(fp_a)
        rounded_b = _fistp_i32(fp_b)

    odd_rot = _imul_sqrt_half(odd_difference)
    odd_a = _add(rounded_a, odd_rot)
    odd_b = _add(odd_rot, rounded_b)
    odd_c = _add(rounded_b, odd_total)

    even26_sum = _add(s[6], s[2])
    even26_difference = _sub(s[2], s[6])
    even04_sum = _add(s[4], s[0])
    even04_difference = _sub(s[0], s[4])
    even_rot = _imul_sqrt_half(even26_difference)
    even26_rotated = _add(even26_sum, even_rot)
    even_left = _add(even_rot, even04_difference)
    even_right = _sub(even04_difference, even_rot)
    even_sum = _add(even26_rotated, even04_sum)
    even_difference = _sub(even04_sum, even26_rotated)

    return tuple(_i32(value) for value in (
        _add(even_sum, odd_c),
        _add(odd_b, even_left),
        _add(even_right, odd_a),
        _add(even_difference, rounded_a),
        _sub(even_difference, rounded_a),
        _sub(even_right, odd_a),
        _sub(even_left, odd_b),
        _sub(even_sum, odd_c),
    ))


def inverse_first_pass_1d(
    source: tuple[int, ...], constants: EA444TransformConstants
) -> tuple[int, ...]:
    """Mirror 0x7B9360, including its seven-AC-zero shortcut."""
    if len(source) != 8:
        raise EA444InverseTransformError("EA444 first pass requires 8 values")
    source = tuple(_i32(value) for value in source)
    if all(value == 0 for value in source[1:]):
        return (source[0],) * 8
    return _inverse_1d_general(source, constants, second_pass=False)


def inverse_second_pass_1d(
    source: tuple[int, ...], constants: EA444TransformConstants
) -> tuple[int, ...]:
    """Mirror 0x7B94C0; its x87 stores qwords then reads their low dwords."""
    return _inverse_1d_general(source, constants, second_pass=True)


def inverse_8x8(
    grid: tuple[int, ...], constants: EA444TransformConstants
) -> tuple[int, ...]:
    """Mirror 8 first passes, the 36-byte scratch stride, and 8 second passes."""
    if len(grid) != 64:
        raise EA444InverseTransformError(
            "EA444 component grid must contain 64 values"
        )
    source_rows = [tuple(grid[row * 8:(row + 1) * 8]) for row in range(8)]
    first = [inverse_first_pass_1d(row, constants) for row in source_rows]
    scratch_rows = [
        tuple(first[column][row] for column in range(8))
        for row in range(8)
    ]
    transformed = [
        inverse_second_pass_1d(row, constants) for row in scratch_rows
    ]
    return tuple(value for row in transformed for value in row)
