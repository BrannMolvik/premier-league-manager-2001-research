"""Inspect only the authenticated original FM2001 Resource.res directory.

The original Resource.res contains 28 named player/kit/media resources.
It is not a source-verified provider of Inbox boost_type_11.444.
This does not rule out other original providers, filename aliases or
runtime observations. No original executable is run.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import struct

ORIGINAL_RESOURCE_RES_SIZE = 2114750
ORIGINAL_RESOURCE_RES_SHA256 = (
    "7abd0213aacede533af438296ecc67271ada8c16b69f2aacd96df9b8d050bb38"
)
ORIGINAL_RESOURCE_RES_DIRECTORY_OFFSET = 0x20411C
ORIGINAL_RESOURCE_RES_DIRECTORY_COUNT = 28
_ENTRY = struct.Struct("<IIIII")


class OriginalResourceResIndexError(ValueError):
    """Invalid identity or structure in original Resource.res."""


@dataclass(frozen=True)
class OriginalResourceResEntry:
    name: str
    data_offset: int
    data_length: int


def original_resource_res_entries(raw: bytes) -> tuple[OriginalResourceResEntry, ...]:
    """Parse the original trailing index without loading any resource data.

    The header stores a directory offset. Each entry is five DWORDs plus
    an ASCII NUL-terminated name, aligned to four bytes except the final
    entry, which ends at EOF. A duplicated payload reference is allowed.
    """
    if not isinstance(raw, bytes):
        raise OriginalResourceResIndexError("Original Resource.res bytes required")
    if (len(raw) != ORIGINAL_RESOURCE_RES_SIZE
            or sha256(raw).hexdigest() != ORIGINAL_RESOURCE_RES_SHA256):
        raise OriginalResourceResIndexError("Original Resource.res identity mismatch")
    index, version, mode = struct.unpack_from("<III", raw)
    if (index, version, mode) != (ORIGINAL_RESOURCE_RES_DIRECTORY_OFFSET, 0x100, 2):
        raise OriginalResourceResIndexError("Original resource directory header mismatch")
    entries = []
    pos = index
    while pos < len(raw):
        if pos + _ENTRY.size >= len(raw):
            raise OriginalResourceResIndexError("Truncated resource directory entry")
        signature, next_offset, flags, size, data_offset = _ENTRY.unpack_from(raw, pos)
        end = raw.find(b"\x00", pos + _ENTRY.size)
        if end < 0:
            raise OriginalResourceResIndexError("Unterminated resource entry")
        try:
            name = raw[pos + _ENTRY.size:end].decode("ascii")
        except UnicodeDecodeError as exc:
            raise OriginalResourceResIndexError("Non-ASCII resource name") from exc
        name_end = end + 1
        next_pos = (name_end + 3) & ~3
        expected_next_offset = next_pos - index
        if (signature != 0xFFFFFFFF or flags != 0
                or next_offset not in (expected_next_offset, 0xFFFFFFFF)
                or (next_offset == 0xFFFFFFFF and name_end != len(raw))
                or not name or not (4 <= data_offset < index)
                or size <= 0 or data_offset + size > index):
            raise OriginalResourceResIndexError("Original resource entry record mismatch")
        entries.append(OriginalResourceResEntry(name, data_offset, size))
        pos = name_end if name_end == len(raw) else next_pos
        if len(entries) > ORIGINAL_RESOURCE_RES_DIRECTORY_COUNT:
            raise OriginalResourceResIndexError("Unexpected additional resource entry")
    if len(entries) != ORIGINAL_RESOURCE_RES_DIRECTORY_COUNT:
        raise OriginalResourceResIndexError("Incomplete original resource directory")
    return tuple(entries)
