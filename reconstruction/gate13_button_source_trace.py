"""Prepare bounded, checksum-gated original Button@ease_2001 PE32 trace windows.

This read-only tool does not claim that byte occurrences are verified xrefs or
that a linear disassembly proves native idle/hover/pressed frame semantics.
It supplies reproducible exact-VA source windows and *candidate* global
pointer-byte occurrences for subsequent control-flow/vtable adjudication.
The default CLI accepts only the independently verified canonical executable.
No proprietary source bytes or disassembly reports belong in Git.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import struct

from ea444_tables import CANONICAL_EXE_SHA256


class OriginalPETraceError(ValueError):
    pass


@dataclass(frozen=True)
class PESection:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int

    @property
    def file_backed_size(self) -> int:
        return min(self.virtual_size or self.raw_size, self.raw_size)


@dataclass(frozen=True)
class OriginalPE32:
    data: bytes
    sha256: str
    image_base: int
    sections: tuple[PESection, ...]

    @classmethod
    def parse(
        cls, data: bytes, *, expected_sha256: str = CANONICAL_EXE_SHA256
    ) -> "OriginalPE32":
        actual_sha = sha256(data).hexdigest()
        if actual_sha != expected_sha256:
            raise OriginalPETraceError("Not the expected original executable hash")
        if len(data) < 0x40 or data[:2] != b"MZ":
            raise OriginalPETraceError("Missing PE MZ header")
        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_offset + 24 > len(data) or data[pe_offset:pe_offset + 4] != b"PE\x00\x00":
            raise OriginalPETraceError("Missing PE signature")
        machine, count = struct.unpack_from("<HH", data, pe_offset + 4)
        opt_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
        opt_offset = pe_offset + 24
        if machine != 0x14C or count <= 0 or opt_size < 32:
            raise OriginalPETraceError("Expected 32-bit i386 PE section table")
        if opt_offset + opt_size > len(data) or (
            struct.unpack_from("<H", data, opt_offset)[0] != 0x10B
        ):
            raise OriginalPETraceError("Expected valid PE32 optional header")
        image_base = struct.unpack_from("<I", data, opt_offset + 28)[0]
        section_offset = opt_offset + opt_size
        if section_offset + count * 40 > len(data):
            raise OriginalPETraceError("Truncated PE section directory")

        sections = []
        for index in range(count):
            off = section_offset + index * 40
            name = data[off:off + 8].rstrip(b"\x00").decode("ascii", "replace")
            virtual_size, virtual, raw_size, raw_offset = struct.unpack_from(
                "<IIII", data, off + 8
            )
            if not virtual or raw_offset + raw_size > len(data):
                raise OriginalPETraceError(f"Invalid PE section: {name}")
            sections.append(PESection(name, virtual, virtual_size, raw_offset, raw_size))
        return cls(data, actual_sha, image_base, tuple(sections))

    def section_for_va(self, va: int) -> tuple[PESection, int]:
        if type(va) is not int:
            raise OriginalPETraceError("Trace address must be an integer VA")
        rva = va - self.image_base
        for section in self.sections:
            delta = rva - section.virtual_address
            if 0 <= delta < section.file_backed_size:
                return section, delta
        raise OriginalPETraceError(f"VA 0x{va:08X} has no file-backed PE section")

    def read(self, va: int, size: int) -> bytes:
        if type(size) is not int or size < 0:
            raise OriginalPETraceError("Read size must be a nonnegative integer")
        section, delta = self.section_for_va(va)
        if delta + size > section.file_backed_size:
            raise OriginalPETraceError("Trace window crosses a PE section boundary")
        offset = section.raw_offset + delta
        return self.data[offset:offset + size]

    def bounded_window(self, va: int, desired_size: int) -> bytes:
        if desired_size <= 0:
            raise OriginalPETraceError("Trace window must be nonempty")
        section, delta = self.section_for_va(va)
        return self.read(va, min(desired_size, section.file_backed_size - delta))

    def pointer_byte_candidates(
        self, target_va: int, *, max_matches: int = 256
    ) -> tuple[dict, ...]:
        """Find raw little-endian occurrences; NOT validated x86 references."""
        if type(target_va) is not int or not 0 <= target_va < 1 << 32:
            raise OriginalPETraceError("Pointer candidate target must be uint32")
        if type(max_matches) is not int or max_matches < 1:
            raise OriginalPETraceError("max_matches must be positive")
        needle = struct.pack("<I", target_va)
        found = []
        for section in self.sections:
            blob = self.data[
                section.raw_offset:section.raw_offset + section.file_backed_size
            ]
            pos = 0
            while True:
                offset = blob.find(needle, pos)
                if offset < 0:
                    break
                found.append({
                    "candidate_va": self.image_base + section.virtual_address + offset,
                    "section": section.name,
                    "classification": "unaligned_raw_byte_candidate_only",
                })
                if len(found) >= max_matches:
                    return tuple(found)
                pos = offset + 1
        return tuple(found)


# Previously source-traced entry points only. Each window is a bounded
# inspection range, NOT a claim about exact function boundaries.
KNOWN_BUTTON_WINDOWS = (
    ("PStartMenu control creation", 0x4C1BA0, 0x140),
    ("PStartMenu event dispatch", 0x4C3770, 0x100),
    ("TeamSelect Back/Start setup", 0x4D885F, 0x110),
    ("Original button atlas initialization", 0x5F4500, 0x120),
    ("Shared Button@ease_2001 setup", 0x652FD0, 0x200),
    ("Zurich bitmap font source loader", 0x657650, 0x120),
)

# These values are established by earlier source research, not new vtables.
CANDIDATE_GLOBAL_TARGETS = (
    ("PStartMenu button atlas global", 0x946590),
    ("Common button font global", 0x9197E0),
    ("PStartMenu vtable", 0x7C64E0),
    ("TeamSelect vtable", 0x7C7650),
)


def disassemble_window(blob: bytes, va: int) -> list[dict]:
    """Optional analyst aid: linear decode only; no automatic CFG claims."""
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
    except ImportError as exc:
        raise OriginalPETraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc
    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    return [
        {
            "va": insn.address, "size": insn.size,
            "bytes": bytes(insn.bytes).hex(),
            "mnemonic": insn.mnemonic, "operands": insn.op_str,
        }
        for insn in engine.disasm(blob, va)
    ]


def button_trace_report(
    pe: OriginalPE32, *, with_disassembly: bool = False,
    windows: tuple[tuple[str, int, int], ...] = KNOWN_BUTTON_WINDOWS,
    globals_to_find: tuple[tuple[str, int], ...] = CANDIDATE_GLOBAL_TARGETS,
) -> dict:
    inspected = []
    for label, start_va, requested_size in windows:
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise OriginalPETraceError(
                f"{label}: expected previously traced code to reside in .text"
            )
        raw = pe.bounded_window(start_va, requested_size)
        record = {
            "label": label, "start_va": start_va, "section": section.name,
            "window_bytes": len(raw), "raw_hex": raw.hex(),
            "linear_disassembly_only": (
                disassemble_window(raw, start_va) if with_disassembly else None
            ),
        }
        inspected.append(record)
    candidates = [
        {
            "target_name": label, "target_va": va,
            "byte_occurrences_not_proven_xrefs": pe.pointer_byte_candidates(va),
        }
        for label, va in globals_to_find
    ]
    return {
        "source_sha256": pe.sha256, "image_base": pe.image_base,
        "evidence_limit": (
            "Exact source bytes and raw pointer-byte occurrences only. "
            "Manual CFG/vtable/text-rendering trace is required to prove "
            "button-state index transitions or glyph positioning."
        ),
        "windows": inspected, "global_candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True,
                        help="Private JSON result outside the Git repository")
    parser.add_argument("--disassemble", action="store_true",
                        help="Include candidate linear Capstone disassembly")
    args = parser.parse_args()
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = button_trace_report(pe, with_disassembly=args.disassemble)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Original Button trace windows saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
