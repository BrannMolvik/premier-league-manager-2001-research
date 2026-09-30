"""Extract original EA444 zigzag and entropy lookup tables read-only.

The original verified executable's TQIA_DAT section is mapped at VA
0xADB000. Its 64 coefficient-order entries live at +0xA0 and 160 packed
Huffman entries at +0x1A0. No replacement video-codec tables are guessed.
This recovers original lookup data, not yet complete pixel rendering.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct

CANONICAL_EXE_SHA256 = "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"
TQIA_VA = 0xADB000
TQIA_SIZE = 0x420
ZIGZAG_OFFSET = 0xA0
VLC_START_OFFSET = 0x1A0


class EA444TableError(ValueError):
    pass


@dataclass(frozen=True)
class EA444VLCEntry:
    amplitude: int
    run_code: int
    bit_length: int

    @property
    def end_of_block(self) -> bool:
        return self.run_code == 0x41

    @property
    def escaped(self) -> bool:
        return self.run_code > 0x41


@dataclass(frozen=True)
class EA444Tables:
    zigzag: tuple[int, ...]
    raw_section: bytes

    def __post_init__(self):
        if len(self.raw_section) != TQIA_SIZE:
            raise EA444TableError("Original EA444 table section must be 0x420 bytes")
        if len(self.zigzag) != 64 or set(self.zigzag) != set(range(64)):
            raise EA444TableError("Original EA444 coefficient permutation is invalid")
        entries = struct.unpack_from("<160I", self.raw_section, VLC_START_OFFSET)
        if any(not 1 <= (entry >> 16) <= 16 for entry in entries):
            raise EA444TableError("Original EA444 entropy table has illegal code lengths")

    @classmethod
    def from_section(cls, section: bytes) -> "EA444Tables":
        zigzag = struct.unpack_from("<64I", section, ZIGZAG_OFFSET)
        return cls(zigzag, section)

    def lookup(self, prefix17: int) -> EA444VLCEntry | None:
        """Mirror original executable 0x7B91E3..0x7B92C7 tiered lookup."""
        if not 0 <= prefix17 < 1 << 17:
            raise EA444TableError("Entropy prefix must be precisely 17 bits")
        if prefix17 >= 0x8000:
            offset = 0x190 + (prefix17 >> 13) * 4
        elif prefix17 >= 0x800:
            offset = 0x1C0 + (prefix17 >> 9) * 4
        elif prefix17 >= 0x400:
            offset = 0x2A0 + (prefix17 >> 7) * 4
        elif prefix17 >= 0x200:
            offset = 0x2A0 + (prefix17 >> 5) * 4
        elif prefix17 >= 0x100:
            offset = 0x2E0 + (prefix17 >> 4) * 4
        elif prefix17 >= 0x80:
            offset = 0x320 + (prefix17 >> 3) * 4
        elif prefix17 >= 0x40:
            offset = 0x360 + (prefix17 >> 2) * 4
        elif prefix17 >= 0x20:
            offset = 0x3A0 + (prefix17 >> 1) * 4
        else:
            return None
        if not VLC_START_OFFSET <= offset <= TQIA_SIZE-4:
            raise EA444TableError(f"Decoder selected outside source table: {offset:#x}")
        packed = struct.unpack_from("<I", self.raw_section, offset)[0]
        return EA444VLCEntry(packed & 0xff, (packed >> 8) & 0xff, packed >> 16)


def tables_from_original_executable(executable: bytes) -> EA444Tables:
    if sha256(executable).hexdigest() != CANONICAL_EXE_SHA256:
        raise EA444TableError("Executable differs from the verified FM2001 build")
    if executable[:2] != b"MZ" or len(executable) < 0x40:
        raise EA444TableError("Expected canonical PE32 MZ header")
    pe = struct.unpack_from("<I", executable, 0x3c)[0]
    if pe+24 > len(executable) or executable[pe:pe+4] != bytes((80, 69, 0, 0)):
        raise EA444TableError("Expected valid PE header")
    nsections = struct.unpack_from("<H", executable, pe+6)[0]
    opt_size = struct.unpack_from("<H", executable, pe+20)[0]
    opt = pe+24
    if struct.unpack_from("<H", executable, opt)[0] != 0x10b:
        raise EA444TableError("Expected canonical PE32 optional header")
    imagebase = struct.unpack_from("<I", executable, opt+28)[0]
    sections = opt+opt_size
    for i in range(nsections):
        entry = sections+i*40
        if entry+40 > len(executable):
            raise EA444TableError("Truncated PE section directory")
        name = executable[entry:entry+8].rstrip(bytes(1))
        if name != b"TQIA_DAT":
            continue
        virtual = struct.unpack_from("<I", executable, entry+12)[0]
        raw_size, raw_offset = struct.unpack_from("<II", executable, entry+16)
        if (imagebase+virtual != TQIA_VA or raw_size < TQIA_SIZE
                or raw_offset+TQIA_SIZE > len(executable)):
            raise EA444TableError("Canonical TQIA_DAT section VA/range does not match")
        return EA444Tables.from_section(executable[raw_offset:raw_offset+TQIA_SIZE])
    raise EA444TableError("Canonical TQIA_DAT decoder table section is missing")


def tables_from_verified_exe_path(path: Path) -> EA444Tables:
    return tables_from_original_executable(Path(path).read_bytes())
