"""Clean-room reproduction of 0x5E4C60's generic PPreMatch shirt palette path.

The native game loads a 36x1280, 8-bit TeamNN.bmp template, rewrites bounded
palette ranges from club color-table entries, and copies nonzero indexed pixels
to its destination surface. This module reproduces the source RGB/alpha plane
before the legacy display-format packing performed by 0x5E4980.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct

from gate13_button_source_trace import OriginalPE32
from gate14_prematch_shirt_selection import (
    PREMATCH_KIT_CLASH_COLOR_COUNT,
    PrematchClubShirtState,
    PrematchSideKitContext,
)


class PrematchGenericShirtError(ValueError):
    pass


PREMATCH_GENERIC_SHIRT_RECOLOR_VA = 0x5E4C60
PREMATCH_GENERIC_SHIRT_COPY_VA = 0x5E4980
PREMATCH_GENERIC_SHIRT_GRADIENT_VA = 0x5E4B10
PREMATCH_GENERIC_SHIRT_COLOR_TABLE_VA = 0x834190
PREMATCH_GENERIC_SHIRT_COLOR_RECORD_BYTES = 8
PREMATCH_GENERIC_SHIRT_COLOR_TABLE_BYTES = (
    PREMATCH_KIT_CLASH_COLOR_COUNT * PREMATCH_GENERIC_SHIRT_COLOR_RECORD_BYTES
)

PREMATCH_GENERIC_SHIRT_SIZE = (36, 1280)
PREMATCH_GENERIC_SHIRT_FRAME_SIZE = (36, 32)
PREMATCH_GENERIC_SHIRT_FRAME_COUNT = 40
PREMATCH_GENERIC_SHIRT_BPP = 8

PREMATCH_PRIMARY_GRADIENT_RANGE = (1, 31)
PREMATCH_SECONDARY_GRADIENT_RANGE = (32, 63)
PREMATCH_NEUTRAL_GRADIENT_RANGE = (64, 79)


@dataclass(frozen=True)
class PrematchIndexedBmp:
    width: int
    height: int
    palette_rgb: tuple[tuple[int, int, int], ...]
    indices: bytes

    def __post_init__(self) -> None:
        if (self.width, self.height) != PREMATCH_GENERIC_SHIRT_SIZE:
            raise PrematchGenericShirtError(
                "generic shirt BMP must preserve native 36x1280 geometry"
            )
        if len(self.palette_rgb) != 256:
            raise PrematchGenericShirtError("generic shirt BMP must have 256 palette entries")
        if len(self.indices) != self.width * self.height:
            raise PrematchGenericShirtError("generic shirt index plane geometry mismatch")


@dataclass(frozen=True)
class PrematchGenericShirtAtlas:
    width: int
    height: int
    rgba: bytes
    source_template_index: int
    use_alternate: bool
    primary_color_id: int
    secondary_color_id: int
    source_rgb_recolor_recovered: bool = True
    legacy_display_packing_recovered: bool = False

    def __post_init__(self) -> None:
        if (self.width, self.height) != PREMATCH_GENERIC_SHIRT_SIZE:
            raise PrematchGenericShirtError("generic shirt atlas geometry drifted")
        if len(self.rgba) != self.width * self.height * 4:
            raise PrematchGenericShirtError("generic shirt RGBA geometry mismatch")
        if not self.source_rgb_recolor_recovered or self.legacy_display_packing_recovered:
            raise PrematchGenericShirtError(
                "generic shirt atlas cannot promote unresolved legacy display packing"
            )


def parse_prematch_generic_bmp(raw: bytes) -> PrematchIndexedBmp:
    if not isinstance(raw, bytes) or len(raw) < 1078:
        raise PrematchGenericShirtError("generic shirt BMP payload is unavailable")
    if raw[:2] != b"BM":
        raise PrematchGenericShirtError("generic shirt source is not a Windows BMP")
    declared_size = struct.unpack_from("<I", raw, 2)[0]
    pixel_offset = struct.unpack_from("<I", raw, 10)[0]
    dib_size = struct.unpack_from("<I", raw, 14)[0]
    width, signed_height = struct.unpack_from("<ii", raw, 18)
    planes, bpp = struct.unpack_from("<HH", raw, 26)
    compression = struct.unpack_from("<I", raw, 30)[0]
    colors_used = struct.unpack_from("<I", raw, 46)[0]

    if declared_size != len(raw):
        raise PrematchGenericShirtError("generic shirt BMP declared size mismatch")
    if dib_size != 40 or planes != 1 or bpp != PREMATCH_GENERIC_SHIRT_BPP:
        raise PrematchGenericShirtError("generic shirt BMP header differs from native format")
    if compression != 0:
        raise PrematchGenericShirtError("generic shirt BMP must be uncompressed BI_RGB")
    if width != PREMATCH_GENERIC_SHIRT_SIZE[0] or abs(signed_height) != PREMATCH_GENERIC_SHIRT_SIZE[1]:
        raise PrematchGenericShirtError("generic shirt BMP dimensions differ from native source")
    if colors_used not in (0, 256):
        raise PrematchGenericShirtError("generic shirt BMP palette count differs from native source")

    palette_offset = 14 + dib_size
    palette_end = palette_offset + 256 * 4
    if palette_end > len(raw) or pixel_offset < palette_end:
        raise PrematchGenericShirtError("generic shirt BMP palette is truncated")
    palette = tuple(
        (
            raw[palette_offset + index * 4 + 2],
            raw[palette_offset + index * 4 + 1],
            raw[palette_offset + index * 4 + 0],
        )
        for index in range(256)
    )

    height = abs(signed_height)
    stride = (width + 3) & ~3
    required_end = pixel_offset + stride * height
    if required_end > len(raw):
        raise PrematchGenericShirtError("generic shirt BMP pixel plane is truncated")

    rows = []
    bottom_up = signed_height > 0
    for output_y in range(height):
        source_y = height - 1 - output_y if bottom_up else output_y
        start = pixel_offset + source_y * stride
        rows.append(raw[start:start + width])
    return PrematchIndexedBmp(
        width=width,
        height=height,
        palette_rgb=palette,
        indices=b"".join(rows),
    )


def _signed_trunc_div(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise PrematchGenericShirtError("gradient denominator must be positive")
    if numerator >= 0:
        return numerator // denominator
    return -((-numerator) // denominator)


def _native_gradient(
    start_rgb: tuple[int, int, int],
    end_rgb: tuple[int, int, int],
    first_index: int,
    last_index: int,
) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    if not (0 <= first_index < last_index <= 255):
        raise PrematchGenericShirtError("invalid native palette gradient range")
    if any(not 0 <= value <= 255 for value in (*start_rgb, *end_rgb)):
        raise PrematchGenericShirtError("native palette endpoint is outside byte range")
    span = last_index - first_index
    steps = tuple(
        _signed_trunc_div(end - start, span)
        for start, end in zip(start_rgb, end_rgb, strict=True)
    )
    out = [(first_index, start_rgb)]
    for offset in range(1, span):
        out.append(
            (
                first_index + offset,
                tuple(
                    max(0, min(255, start + step * offset))
                    for start, step in zip(start_rgb, steps, strict=True)
                ),
            )
        )
    out.append((last_index, end_rgb))
    return tuple(out)


def _source_color_pair(table: bytes, color_id: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if not isinstance(table, bytes) or len(table) != PREMATCH_GENERIC_SHIRT_COLOR_TABLE_BYTES:
        raise PrematchGenericShirtError(
            "generic shirt color table must come from canonical executable"
        )
    if type(color_id) is not int or not 0 <= color_id < PREMATCH_KIT_CLASH_COLOR_COUNT:
        raise PrematchGenericShirtError("generic shirt color id is outside native table")
    start = color_id * PREMATCH_GENERIC_SHIRT_COLOR_RECORD_BYTES
    record = table[start:start + PREMATCH_GENERIC_SHIRT_COLOR_RECORD_BYTES]
    return (
        (record[0], record[1], record[2]),
        (record[4], record[5], record[6]),
    )


def prematch_generic_color_table_from_executable(executable: bytes) -> bytes:
    if not isinstance(executable, bytes) or not executable:
        raise PrematchGenericShirtError("canonical executable bytes are required")
    try:
        pe = OriginalPE32.parse(executable)
        table = pe.read(
            PREMATCH_GENERIC_SHIRT_COLOR_TABLE_VA,
            PREMATCH_GENERIC_SHIRT_COLOR_TABLE_BYTES,
        )
    except Exception as exc:
        raise PrematchGenericShirtError(
            "generic shirt color table is unavailable from canonical executable"
        ) from exc
    if len(table) != PREMATCH_GENERIC_SHIRT_COLOR_TABLE_BYTES:
        raise PrematchGenericShirtError("generic shirt color table length drifted")
    return table


def recolor_prematch_generic_shirt(
    bmp_raw: bytes,
    *,
    executable: bytes,
    club: PrematchClubShirtState,
    context: PrematchSideKitContext,
) -> PrematchGenericShirtAtlas:
    """Reproduce 0x5E4C60's indexed-palette rewrite before 16-bit display packing."""
    if type(club) is not PrematchClubShirtState:
        raise PrematchGenericShirtError("generic shirt recolor requires exact club state")
    if type(context) is not PrematchSideKitContext:
        raise PrematchGenericShirtError("generic shirt recolor requires exact side context")

    image = parse_prematch_generic_bmp(bmp_raw)
    table = prematch_generic_color_table_from_executable(executable)

    if context.use_alternate:
        primary_color = club.alternate_color_id
        secondary_color = club.alternate_secondary_color_id
    else:
        primary_color = club.primary_color_id
        secondary_color = club.primary_secondary_color_id

    palette = list(image.palette_rgb)
    for color_id, (first, last) in (
        (primary_color, PREMATCH_PRIMARY_GRADIENT_RANGE),
        (secondary_color, PREMATCH_SECONDARY_GRADIENT_RANGE),
    ):
        start_rgb, end_rgb = _source_color_pair(table, color_id)
        for index, rgb in _native_gradient(start_rgb, end_rgb, first, last):
            palette[index] = rgb

    for index, rgb in _native_gradient(
        (255, 255, 255),
        (0, 0, 0),
        *PREMATCH_NEUTRAL_GRADIENT_RANGE,
    ):
        palette[index] = rgb

    rgba = bytearray(image.width * image.height * 4)
    for pixel_index, palette_index in enumerate(image.indices):
        if palette_index == 0:
            continue
        red, green, blue = palette[palette_index]
        offset = pixel_index * 4
        rgba[offset:offset + 4] = bytes((red, green, blue, 255))

    return PrematchGenericShirtAtlas(
        width=image.width,
        height=image.height,
        rgba=bytes(rgba),
        source_template_index=context.generic_template_index,
        use_alternate=context.use_alternate,
        primary_color_id=primary_color,
        secondary_color_id=secondary_color,
    )


def prematch_generic_shirt_contract() -> dict:
    return {
        "recolor_va": PREMATCH_GENERIC_SHIRT_RECOLOR_VA,
        "copy_va": PREMATCH_GENERIC_SHIRT_COPY_VA,
        "gradient_va": PREMATCH_GENERIC_SHIRT_GRADIENT_VA,
        "color_table_va": PREMATCH_GENERIC_SHIRT_COLOR_TABLE_VA,
        "source_geometry": PREMATCH_GENERIC_SHIRT_SIZE,
        "frame_geometry": PREMATCH_GENERIC_SHIRT_FRAME_SIZE,
        "frame_count": PREMATCH_GENERIC_SHIRT_FRAME_COUNT,
        "primary_gradient_range": PREMATCH_PRIMARY_GRADIENT_RANGE,
        "secondary_gradient_range": PREMATCH_SECONDARY_GRADIENT_RANGE,
        "neutral_gradient_range": PREMATCH_NEUTRAL_GRADIENT_RANGE,
        "palette_index_zero_transparent": True,
        "source_rgb_recolor_recovered": True,
        "legacy_display_packing_recovered": False,
        "complete_marker_pixels_recovered": False,
        "gate14_complete": False,
    }
