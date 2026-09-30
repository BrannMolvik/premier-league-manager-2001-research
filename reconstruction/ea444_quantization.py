"""Recover the original EA444 fixed-point coefficient scale table from the PE.

The original routine 0x6864CF..0x6864FE converts 64 source values located
at 0x7DABF0 into the live 0x9FBD80 table. It uses signed IMUL 0x80000,
SHL high-word 16, SHR low-word 16, and ADC with the shifted-out low
word's bit 15. This is rounded (source*8) in 16.16 fixed point, not
a guessed standard JPEG quantization matrix.

The caller also seeds its dither RNG. Extracting the immutable source
table here intentionally does not advance or substitute that game RNG.
This module does not implement the remaining inverse transform or pixels.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct

from ea444_tables import CANONICAL_EXE_SHA256

ORIGINAL_QUANT_VA = 0x7DABF0
ORIGINAL_QUANT_COUNT = 64
ORIGINAL_QUANT_BYTE_COUNT = ORIGINAL_QUANT_COUNT * 4
ORIGINAL_QUANT_SHA256 = (
    "6fb2af66cb6a51e4b3fa7da9bacab417fa40f180aa0c18c85adb2550c04c89eb"
)


class EA444QuantizationError(ValueError):
    """Original quantization table is inaccessible or inconsistent."""


def original_imul_scale(value: int) -> int:
    """Reproduce lower 32 bits of original x86 IMUL/SHL/SHR/ADC sequence."""
    if not -(1 << 31) <= value < (1 << 31):
        raise EA444QuantizationError("Source coefficient must be signed int32")
    product = value * 0x80000
    lo = product & 0xFFFFFFFF
    hi = (product >> 32) & 0xFFFFFFFF
    carry = (lo >> 15) & 1  # CF after SHR EAX,16
    result = ((lo >> 16) + ((hi << 16) & 0xFFFFFFFF) + carry) & 0xFFFFFFFF
    return result - (1 << 32) if result & 0x80000000 else result


@dataclass(frozen=True)
class EA444Quantization:
    original_source: tuple[int, ...]
    fixed_point: tuple[int, ...]

    @classmethod
    def from_source_bytes(cls, source: bytes) -> "EA444Quantization":
        if len(source) != ORIGINAL_QUANT_BYTE_COUNT:
            raise EA444QuantizationError("Original EA444 matrix must contain 64 int32s")
        if sha256(source).hexdigest() != ORIGINAL_QUANT_SHA256:
            raise EA444QuantizationError(
                "Quantization source differs from verified original executable"
            )
        original = struct.unpack("<64i", source)
        if any(value <= 0 for value in original):
            raise EA444QuantizationError("Original EA444 scale values must be positive")
        return cls(original, tuple(original_imul_scale(x) for x in original))

    def scaled_coefficient(self, position: int, raw: int) -> int:
        """Mirror original signed low-dword multiplication at 0x7B9040/AC write."""
        if not 0 <= position < ORIGINAL_QUANT_COUNT:
            raise EA444QuantizationError("Coefficient position outside 8x8 block")
        if not -(1 << 31) <= raw < (1 << 31):
            raise EA444QuantizationError("Raw coefficient must be signed int32")
        result = (self.fixed_point[position] * raw) & 0xFFFFFFFF
        return result - (1 << 32) if result & 0x80000000 else result


def quantization_from_verified_executable(executable: bytes) -> EA444Quantization:
    """Verify exact original PE, then find the VA within its .rdata section."""
    if sha256(executable).hexdigest() != CANONICAL_EXE_SHA256:
        raise EA444QuantizationError("Executable is not the verified FM2001 original")
    if executable[:2] != b"MZ":
        raise EA444QuantizationError("Missing original PE MZ signature")
    pe = struct.unpack_from("<I", executable, 0x3C)[0]
    if pe + 24 > len(executable) or executable[pe:pe+4] != bytes((80, 69, 0, 0)):
        raise EA444QuantizationError("Missing canonical PE signature")
    count = struct.unpack_from("<H", executable, pe + 6)[0]
    optional_size = struct.unpack_from("<H", executable, pe + 20)[0]
    optional = pe + 24
    if struct.unpack_from("<H", executable, optional)[0] != 0x10B:
        raise EA444QuantizationError("Expected PE32 original executable")
    base = struct.unpack_from("<I", executable, optional + 28)[0]
    table_rva = ORIGINAL_QUANT_VA - base
    sections = optional + optional_size
    for i in range(count):
        entry = sections + i * 40
        if entry + 40 > len(executable):
            raise EA444QuantizationError("Truncated section table")
        if executable[entry:entry+8].rstrip(bytes(1)) != b".rdata":
            continue
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", executable, entry + 8
        )
        delta = table_rva - virtual_address
        if (0 <= delta and delta + ORIGINAL_QUANT_BYTE_COUNT <= raw_size
                and delta + ORIGINAL_QUANT_BYTE_COUNT <= virtual_size
                and raw_offset + delta + ORIGINAL_QUANT_BYTE_COUNT <= len(executable)):
            start = raw_offset + delta
            return EA444Quantization.from_source_bytes(
                executable[start:start + ORIGINAL_QUANT_BYTE_COUNT]
            )
    raise EA444QuantizationError(
        "Expected original quantization table missing from .rdata"
    )


def quantization_from_verified_exe_path(path: Path) -> EA444Quantization:
    return quantization_from_verified_executable(Path(path).read_bytes())
