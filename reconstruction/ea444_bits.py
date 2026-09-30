"""Original EAUK .444 tile-bitstream access, verified against Loader444.

The canonical executable's x86 tile routines at 0x7B95D0 and 0x7BB960
access the bitstream as native little-endian dwords but consume each dword
from its most-significant bit first (SHLD EAX, EDX, CL; SHR EAX, 24).
The payload begins after the verified 8-byte image header. This recovers
*bit-order*, not compression symbols, dequantization, or reconstructed pixels.
"""
from __future__ import annotations

from dataclasses import dataclass

from ea444_header import EA444FormatError, EA444Header, parse_ea444_header


class EA444BitstreamError(ValueError):
    pass


@dataclass
class EA444BitReader:
    payload: bytes
    bit_position: int = 0

    def __post_init__(self):
        if len(self.payload) % 4:
            raise EA444BitstreamError('Original EA444 payload must be dword-aligned')
        if not 0 <= self.bit_position <= len(self.payload) * 8:
            raise EA444BitstreamError('Bit offset is outside the payload')

    @property
    def bits_remaining(self) -> int:
        return len(self.payload) * 8 - self.bit_position

    def read(self, width: int) -> int:
        """Read 1..32 bits in the original reverse-byte-within-word order."""
        if not 1 <= width <= 32:
            raise EA444BitstreamError('Bit width must be 1..32')
        if width > self.bits_remaining:
            raise EA444BitstreamError('Compressed tile bitstream ended early')
        position = self.bit_position
        word_pos, shift = divmod(position, 32)
        start = word_pos * 4
        hi = int.from_bytes(self.payload[start:start + 4], 'little')
        val = (hi << shift) & 0xFFFFFFFF
        if shift and start + 4 < len(self.payload):
            lo = int.from_bytes(self.payload[start + 4:start + 8], 'little')
            val |= lo >> (32 - shift)
        self.bit_position += width
        return (val >> (32 - width)) & ((1 << width) - 1)


def reader_for_ea444(source: bytes) -> tuple[EA444Header, EA444BitReader]:
    header = parse_ea444_header(source)
    return header, EA444BitReader(source[8:])
