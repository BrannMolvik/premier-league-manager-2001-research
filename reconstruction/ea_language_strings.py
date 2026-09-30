"""Read EAUK's original FM2001 nul-terminated .str/.idx language resources.

Format verified first-hand against the authorized English.str and EnglishEAM.str
on 30 September 2026. Do not mistake .idx entries for byte offsets: they are
uint16 indices into the owning .str resource's uint32 offset table.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct


class EALanguageFormatError(ValueError):
    """The original language resource violates a verified format invariant."""


@dataclass(frozen=True)
class EAStringTable:
    strings: tuple[str, ...]
    offsets: tuple[int, ...]
    payload_size: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "EAStringTable":
        if len(data) < 8:
            raise EALanguageFormatError("STR header requires two little-endian u32 values")
        payload_size, count = struct.unpack_from("<II", data)
        if not count or payload_size < 2:
            raise EALanguageFormatError("STR has no usable string payload")
        end = 8 + payload_size
        if end > len(data) or count > (len(data) - end) // 4:
            raise EALanguageFormatError("STR payload/offset table exceeds file length")
        if end + count * 4 != len(data):
            raise EALanguageFormatError("STR includes extra bytes after its offset table")

        blob = data[8:end]
        offsets = struct.unpack_from(f"<{count}I", data, end)
        if offsets[0] != 0:
            raise EALanguageFormatError("First STR string must start at payload offset 0")
        parsed = []
        previous = -1
        for index, offset in enumerate(offsets):
            if offset <= previous or offset >= payload_size:
                raise EALanguageFormatError(
                    f"STR string {index} has an invalid/out-of-order offset"
                )
            if offset and blob[offset - 1] != 0:
                raise EALanguageFormatError(
                    f"STR string {index} is not at a nul-delimited boundary"
                )
            stop = blob.find(b"\x00", offset)
            if stop < 0:
                raise EALanguageFormatError(f"Unterminated STR string {index}")
            if index + 1 < count and stop + 1 != offsets[index + 1]:
                raise EALanguageFormatError(
                    f"STR string {index} does not end at the next entry"
                )
            try:
                parsed.append(blob[offset:stop].decode("cp1252"))
            except UnicodeDecodeError as exc:
                raise EALanguageFormatError(
                    f"STR string {index} contains invalid cp1252"
                ) from exc
            previous = offset
        if stop + 1 != len(blob):
            raise EALanguageFormatError("STR payload has unindexed trailing bytes")
        return cls(tuple(parsed), tuple(offsets), payload_size)

    def __getitem__(self, index: int) -> str:
        return self.strings[index]


@dataclass(frozen=True)
class EAStringIndex:
    string_ids: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes, strings: EAStringTable) -> "EAStringIndex":
        if not data or len(data) % 2:
            raise EALanguageFormatError("IDX must contain whole uint16 string indices")
        indices = struct.unpack(f"<{len(data) // 2}H", data)
        for position, value in enumerate(indices):
            if value >= len(strings.strings):
                raise EALanguageFormatError(
                    f"IDX entry {position} points beyond the STR string count"
                )
        return cls(tuple(indices))

    def resolve(self, strings: EAStringTable, entry: int) -> str:
        return strings[self.string_ids[entry]]


def parse_language_pair(str_bytes: bytes, idx_bytes: bytes
                        ) -> tuple[EAStringTable, EAStringIndex]:
    strings = EAStringTable.from_bytes(str_bytes)
    return strings, EAStringIndex.from_bytes(idx_bytes, strings)
