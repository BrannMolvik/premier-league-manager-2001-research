from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct

EXPECTED_FM2001_EXE_SHA256 = "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"

ATTACK_MATRIX_VA = 0x83B838
DEFENCE_MATRIX_VA = 0x83E2B8
TACTIC_STYLES = 4
RUNTIME_ROLES = 20
PLAYER_SKILLS = 17
MATRIX_VALUE_COUNT = TACTIC_STYLES * RUNTIME_ROLES * PLAYER_SKILLS


@dataclass(frozen=True)
class MatchCoefficientMatrices:
    attack: tuple[tuple[tuple[float, ...], ...], ...]
    defence: tuple[tuple[tuple[float, ...], ...], ...]

    @classmethod
    def from_executable(
        cls,
        executable: str | Path,
        *,
        verify_hash: bool = True,
    ) -> "MatchCoefficientMatrices":
        data = Path(executable).read_bytes()

        if verify_hash:
            digest = sha256(data).hexdigest()
            if digest != EXPECTED_FM2001_EXE_SHA256:
                raise ValueError(
                    "footballmanager.exe hash does not match the analyzed FM2001 release"
                )

        return cls(
            attack=_read_matrix(data, ATTACK_MATRIX_VA),
            defence=_read_matrix(data, DEFENCE_MATRIX_VA),
        )


def _read_matrix(data: bytes, absolute_va: int):
    file_offset = _absolute_va_to_file_offset(data, absolute_va)
    byte_count = MATRIX_VALUE_COUNT * 8
    end = file_offset + byte_count
    if end > len(data):
        raise ValueError("coefficient matrix exceeds executable size")

    flat = struct.unpack_from(f"<{MATRIX_VALUE_COUNT}d", data, file_offset)

    styles = []
    for style in range(TACTIC_STYLES):
        roles = []
        for role in range(RUNTIME_ROLES):
            start = (style * RUNTIME_ROLES + role) * PLAYER_SKILLS
            roles.append(tuple(flat[start:start + PLAYER_SKILLS]))
        styles.append(tuple(roles))
    return tuple(styles)


def _absolute_va_to_file_offset(data: bytes, absolute_va: int) -> int:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError("not a PE executable")

    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if pe_offset + 24 > len(data) or data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise ValueError("invalid PE header")

    number_of_sections = struct.unpack_from("<H", data, pe_offset + 6)[0]
    optional_header_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    optional_header = pe_offset + 24

    if optional_header + optional_header_size > len(data):
        raise ValueError("truncated PE optional header")

    magic = struct.unpack_from("<H", data, optional_header)[0]
    if magic != 0x10B:
        raise ValueError("expected a 32-bit PE executable")

    image_base = struct.unpack_from("<I", data, optional_header + 28)[0]
    rva = int(absolute_va) - image_base
    if rva < 0:
        raise ValueError("VA is below the executable image base")

    section_table = optional_header + optional_header_size
    for index in range(number_of_sections):
        off = section_table + index * 40
        if off + 40 > len(data):
            raise ValueError("truncated PE section table")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", data, off + 8
        )
        span = max(virtual_size, raw_size)
        if virtual_address <= rva < virtual_address + span:
            file_offset = raw_pointer + (rva - virtual_address)
            if file_offset >= len(data):
                raise ValueError("VA resolves outside executable file data")
            return file_offset

    raise ValueError(f"VA 0x{absolute_va:X} does not belong to a PE section")
