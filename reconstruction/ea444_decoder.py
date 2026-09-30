"""Source-backed decoder for the original FM2001 EAUK .444 graphics.

This follows Loader444's original 8x8 tile stream: three independently
compressed direct-color component blocks, each dequantized and transformed by
the recovered inverse transform, followed by the original per-tile 64-bit
color-key mask when descriptor bit 0 is clear. Samples are signed 16.16 and the
legacy 16-bit path indexes its clamp tables with arithmetic sample >> 16.
Masked pixels carry the source header's RGB color key and are represented here
with alpha 0 as the modern equivalent of the legacy color-key blit.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_bits import EA444BitReader, reader_for_ea444
from ea444_coefficients import read_coefficient_block
from ea444_header import EA444Header
from ea444_inverse_transform import EA444TransformConstants, inverse_8x8
from ea444_quantization import EA444Quantization
from ea444_quantized_block import make_quantized_block
from ea444_tables import EA444Tables


class EA444DecodeError(ValueError):
    pass


@dataclass(frozen=True)
class EA444DecodedImage:
    width: int
    height: int
    rgba: bytes
    consumed_bits: int
    transparent_pixels: int

    def __post_init__(self):
        if len(self.rgba) != self.width * self.height * 4:
            raise EA444DecodeError("RGBA byte count does not match image geometry")


def _sample_u8(value: int) -> int:
    value >>= 16
    return 0 if value < 0 else 255 if value > 255 else value


def _decode_component(
    reader: EA444BitReader,
    tables: EA444Tables,
    quant: EA444Quantization,
    transform: EA444TransformConstants,
) -> tuple[int, ...]:
    compressed = read_coefficient_block(reader, tables)
    fixed = make_quantized_block(compressed, quant).signed_fixed
    return inverse_8x8(fixed, transform)


def _read_transparency_rows(reader: EA444BitReader, header: EA444Header) -> bytes:
    if header.descriptor[0] & 1:
        return bytes(8)
    if not reader.read(1):
        return bytes(8)
    first = reader.read(32).to_bytes(4, "big")
    second = reader.read(32).to_bytes(4, "big")
    return first + second


def decode_ea444(
    source: bytes,
    *,
    tables: EA444Tables,
    quant: EA444Quantization,
) -> EA444DecodedImage:
    header, reader = reader_for_ea444(source)
    transform = EA444TransformConstants.from_tables(tables)
    if header.descriptor[0] & 0x80:
        raise EA444DecodeError(
            "Original fourth-component EA444 path is not yet supported"
        )

    output = bytearray(header.width * header.height * 4)
    transparent = 0
    padded_width, padded_height = header.padded_size
    key_r, key_g, key_b = header.rgb_triplet

    for tile_y in range(0, padded_height, 8):
        for tile_x in range(0, padded_width, 8):
            red = _decode_component(reader, tables, quant, transform)
            green = _decode_component(reader, tables, quant, transform)
            blue = _decode_component(reader, tables, quant, transform)
            mask_rows = _read_transparency_rows(reader, header)

            for y in range(8):
                py = tile_y + y
                if py >= header.height:
                    continue
                row_mask = mask_rows[y]
                for x in range(8):
                    px = tile_x + x
                    if px >= header.width:
                        continue
                    index = y * 8 + x
                    masked = bool(row_mask & (0x80 >> x))
                    if masked:
                        r, g, b, a = key_r, key_g, key_b, 0
                        transparent += 1
                    else:
                        r = _sample_u8(red[index])
                        g = _sample_u8(green[index])
                        b = _sample_u8(blue[index])
                        a = 255
                    dest = (py * header.width + px) * 4
                    output[dest:dest + 4] = bytes((r, g, b, a))

    return EA444DecodedImage(
        header.width,
        header.height,
        bytes(output),
        reader.bit_position,
        transparent,
    )


def decode_ea444_file(
    path: Path,
    *,
    tables: EA444Tables,
    quant: EA444Quantization,
) -> EA444DecodedImage:
    return decode_ea444(Path(path).read_bytes(), tables=tables, quant=quant)
