"""Parser and alpha rasterizer for the original EAUK FM2001 .fnt format.

Recovered from canonical font loader 0x657650. The loader reads five uint32
header values, then exactly 0xE0 (224) fixed records. Each record contains four
uint32 glyph metrics followed by 224 signed byte pair-spacing values. The
remaining bytes are a one-byte-per-pixel horizontal glyph atlas whose dimensions
are the first two header values.

Character records correspond to CP1252 byte values 32..255.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct


HEADER = struct.Struct("<5I")
GLYPH_COUNT = 0xE0
PAIR_COUNT = GLYPH_COUNT
GLYPH_RECORD_SIZE = 16 + PAIR_COUNT


class EAFontError(ValueError):
    pass


@dataclass(frozen=True)
class EAGlyph:
    codepoint: int
    atlas_x: int
    width: int
    height: int
    draw_y: int
    pair_adjustments: tuple[int, ...]

    def pair_adjustment(self, next_codepoint: int) -> int:
        index = int(next_codepoint) - 32
        if not 0 <= index < PAIR_COUNT:
            raise EAFontError(f"Unsupported next CP1252 byte: {next_codepoint}")
        return self.pair_adjustments[index]


@dataclass(frozen=True)
class EATextMask:
    width: int
    height: int
    alpha: bytes


@dataclass(frozen=True)
class EAFont:
    atlas_width: int
    atlas_height: int
    header_value_2: int
    header_value_3: int
    header_value_4: int
    glyphs: tuple[EAGlyph, ...]
    atlas_alpha: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "EAFont":
        if len(data) < HEADER.size:
            raise EAFontError("EA font is shorter than its 20-byte header")
        width, height, value2, value3, value4 = HEADER.unpack_from(data)
        if width <= 0 or height <= 0:
            raise EAFontError("EA font atlas dimensions must be positive")
        records_bytes = GLYPH_COUNT * GLYPH_RECORD_SIZE
        expected = HEADER.size + records_bytes + width * height
        if len(data) != expected:
            raise EAFontError(
                f"EA font is {len(data)} bytes, expected exactly {expected}"
            )

        glyphs = []
        cursor = HEADER.size
        for index in range(GLYPH_COUNT):
            atlas_x, glyph_width, glyph_height, draw_y = struct.unpack_from(
                "<4I", data, cursor
            )
            if atlas_x + glyph_width > width:
                raise EAFontError(
                    f"Glyph {index + 32} exceeds atlas width"
                )
            if glyph_height > height:
                raise EAFontError(
                    f"Glyph {index + 32} exceeds source atlas height"
                )
            pair_raw = struct.unpack_from("<224b", data, cursor + 16)
            glyphs.append(
                EAGlyph(
                    codepoint=index + 32,
                    atlas_x=atlas_x,
                    width=glyph_width,
                    height=glyph_height,
                    draw_y=draw_y,
                    pair_adjustments=tuple(pair_raw),
                )
            )
            cursor += GLYPH_RECORD_SIZE

        atlas = bytes(data[cursor:])
        return cls(
            atlas_width=width,
            atlas_height=height,
            header_value_2=value2,
            header_value_3=value3,
            header_value_4=value4,
            glyphs=tuple(glyphs),
            atlas_alpha=atlas,
        )

    def glyph_for_byte(self, codepoint: int) -> EAGlyph:
        index = int(codepoint) - 32
        if not 0 <= index < GLYPH_COUNT:
            raise EAFontError(f"Unsupported CP1252 byte: {codepoint}")
        return self.glyphs[index]

    def glyph_alpha(self, codepoint: int) -> bytes:
        glyph = self.glyph_for_byte(codepoint)
        if glyph.width == 0 or glyph.height == 0:
            return b""
        output = bytearray(glyph.width * glyph.height)
        for y in range(glyph.height):
            source = y * self.atlas_width + glyph.atlas_x
            target = y * glyph.width
            output[target:target + glyph.width] = self.atlas_alpha[
                source:source + glyph.width
            ]
        return bytes(output)

    @staticmethod
    def _encode(text: str) -> bytes:
        try:
            encoded = text.encode("cp1252", errors="strict")
        except UnicodeEncodeError as exc:
            raise EAFontError("Text is not representable by original CP1252 font") from exc
        if any(value < 32 for value in encoded):
            raise EAFontError("Original single-line renderer rejects control characters")
        return encoded

    def measure_text(self, text: str) -> int:
        encoded = self._encode(text)
        width = 0
        for index, value in enumerate(encoded):
            glyph = self.glyph_for_byte(value)
            width += glyph.width
            if index + 1 < len(encoded):
                width += glyph.pair_adjustment(encoded[index + 1])
        return width

    def render_text_alpha(self, text: str) -> EATextMask:
        """Rasterize source glyph alpha with recovered pair spacing.

        Glyph source pixels always begin at atlas y=0; per-character draw_y is
        the vertical placement within the text/button line. The required output
        height is derived from the actual selected glyphs rather than guessed
        from the filename.
        """
        encoded = self._encode(text)
        if not encoded:
            return EATextMask(0, 0, b"")
        glyphs = [self.glyph_for_byte(value) for value in encoded]
        width = self.measure_text(text)
        height = max(glyph.draw_y + glyph.height for glyph in glyphs)
        output = bytearray(width * height)

        x = 0
        for index, (value, glyph) in enumerate(zip(encoded, glyphs)):
            bitmap = self.glyph_alpha(value)
            for y in range(glyph.height):
                src = y * glyph.width
                dst = (glyph.draw_y + y) * width + x
                for px in range(glyph.width):
                    # Glyphs normally do not overlap; max preserves exact alpha
                    # if negative kerning does overlap source bounding boxes.
                    alpha = bitmap[src + px]
                    if alpha > output[dst + px]:
                        output[dst + px] = alpha
            x += glyph.width
            if index + 1 < len(encoded):
                x += glyph.pair_adjustment(encoded[index + 1])

        return EATextMask(width, height, bytes(output))
