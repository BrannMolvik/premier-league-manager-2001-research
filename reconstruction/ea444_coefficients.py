"""Source-derived partial original EA444 coefficient-block parser.

Implements the 8-bit scale/DC token and bounded AC run/sign/escape path
at canonical 0x7B91C7..0x7B9354, using the *original* executable's
Huffman and coefficient permutation tables. Returned AC values are
UNQUANTIZED; component traversal, original quantization, IDCT,
clipping and display packing still require reconstruction.
"""
from __future__ import annotations

from dataclasses import dataclass

from ea444_bits import EA444BitReader
from ea444_tables import EA444Tables


class EA444CoefficientError(ValueError):
    pass


@dataclass(frozen=True)
class EA444CoefficientBlock:
    scale_code: int
    coefficients: tuple[tuple[int, int], ...]
    consumed_bits: int
    termination: str


def _peek17(reader: EA444BitReader) -> int:
    # Native code prefetches another dword for lookahead at packet end.
    # Padding affects LOOKAHEAD ONLY; actual consumed bits remain bounded.
    padded = EA444BitReader(reader.payload + bytes(4), reader.bit_position)
    return padded.read(17)


def read_coefficient_block(
    reader: EA444BitReader,
    tables: EA444Tables,
) -> EA444CoefficientBlock:
    """Reproduce one original component's scale and sparse signed AC stream."""
    start = reader.bit_position
    scale = reader.read(8)
    rank = 63
    coefficients = []
    for _ in range(65):
        entry = tables.lookup(_peek17(reader))
        if entry is None:
            return EA444CoefficientBlock(
                scale, tuple(coefficients), reader.bit_position-start,
                "short-end-marker",
            )
        reader.read(entry.bit_length)
        if entry.end_of_block:
            return EA444CoefficientBlock(
                scale, tuple(coefficients), reader.bit_position-start,
                "table-end-marker",
            )
        if entry.escaped:
            raw = reader.read(14)
            rank -= raw >> 8
            amplitude = raw & 0xFF
            if amplitude == 0:
                amplitude = reader.read(8)
            elif amplitude == 0x80:
                amplitude = reader.read(8) - 256
            elif amplitude > 0x80:
                amplitude -= 256
            if not 0 <= rank <= 63:
                raise EA444CoefficientError(
                    f"Escaped run overran coefficient grid: {rank}"
                )
            coefficients.append((tables.zigzag[rank], amplitude))
            rank -= 1
        else:
            rank -= entry.run_code
            negative = reader.read(1)
            if not 0 <= rank+1 <= 63:
                raise EA444CoefficientError(
                    f"AC run overran coefficient grid: {rank}"
                )
            coefficients.append((
                tables.zigzag[rank+1],
                -entry.amplitude if negative else entry.amplitude,
            ))
    raise EA444CoefficientError(
        "Coefficient stream did not terminate within 64 entries"
    )
