"""Evidence-only parser for the original EAUK proprietary .444 graphic header.

Source: 1,354 first-hand Joliet images on the authorized FM2001 disc. The
original binary's Loader444 decodes the 8-byte header at 0x68598A and maps
the next three bytes to display-channel masks at 0x6868E0. A downstream
decoder at 0x7B95D0/0x7BB960 works on 8x8 image tiles.

IMPORTANT: this parses source geometry; it does NOT decode compressed pixels,
claim the meaning of the first flag byte, or assign animations to UI controls.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


ORIGINAL_DESCRIPTOR = bytes.fromhex("64 ff 00 ff")
EA444_HEADER_BYTES = 8
BLOCK_EDGE_PIXELS = 8


class EA444FormatError(ValueError):
    """Unrecognized or structurally incomplete original EAUK graphic."""


@dataclass(frozen=True)
class EA444Header:
    width: int
    height: int
    descriptor: bytes
    payload_size: int

    @property
    def rgb_triplet(self) -> tuple[int, int, int]:
        """Source bytes +5..+7 passed to the original display-mask converter."""
        return tuple(self.descriptor[1:4])

    @property
    def padded_size(self) -> tuple[int, int]:
        edge = BLOCK_EDGE_PIXELS
        return (
            (self.width + edge - 1) // edge * edge,
            (self.height + edge - 1) // edge * edge,
        )

    @property
    def encoded_block_count(self) -> int:
        w, h = self.padded_size
        return (w // BLOCK_EDGE_PIXELS) * (h // BLOCK_EDGE_PIXELS)


def parse_ea444_header(
    data: bytes,
    *,
    require_original_descriptor: bool = True,
) -> EA444Header:
    if len(data) < EA444_HEADER_BYTES:
        raise EA444FormatError("EA444 file ends inside the 8-byte header")
    width, height = struct.unpack_from("<HH", data)
    if not width or not height:
        raise EA444FormatError("EA444 pixel dimensions must be nonzero")
    descriptor = data[4:8]
    if require_original_descriptor and descriptor != ORIGINAL_DESCRIPTOR:
        raise EA444FormatError(
            f"EA444 descriptor {descriptor.hex()} differs from original disc"
        )
    if len(data) == EA444_HEADER_BYTES:
        raise EA444FormatError("EA444 file has no encoded image payload")
    return EA444Header(width, height, descriptor, len(data)-EA444_HEADER_BYTES)


def parse_ea444_file(path: Path) -> EA444Header:
    return parse_ea444_header(Path(path).read_bytes())
