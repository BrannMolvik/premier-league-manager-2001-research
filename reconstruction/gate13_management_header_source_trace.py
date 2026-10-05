"""Read-only Gate-13 management-header source trace.

This tool exists only to close the fixed Gate-13 header slice without guessing.
It reads the canonical original PE and, optionally, the three exact source
resources. It writes a private JSON receipt outside Git. It never patches the
executable, imports assets, edits repository files, or promotes raw candidates
to semantics.

The bounded addresses are already established in GATE13_FIXED_CLOSURE_SLICE.md.
Raw windows/descriptors remain analyst evidence until manually adjudicated.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    disassemble_window,
    require_private_output_path,
)


HEADER_ART = (
    {
        "role": "left_anim",
        "source_path": "FM2001_Art/Generic/Background_buttons/back_4_anim.444",
        "sha256": "867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69",
        "size": (30, 4845),
        "destination_rect": (599, 0, 30, 95),
    },
    {
        "role": "right_state",
        "source_path": "FM2001_Art/Generic/Background_buttons/back_4.444",
        "sha256": "710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb",
        "size": (70, 380),
        "destination_rect": (629, 0, 70, 95),
    },
)
HEADER_FONT_PATH = "Fonts/Zurich_XCn_BT_24pixel.fnt"

HEADER_WINDOWS = (
    ("management header compound constructor", 0x4313B0, 0x180),
    ("management header caption setup", 0x431480, 0x120),
    ("header resource loader xrefs", 0x5FA640, 0x280),
    ("Zurich 24px font loader/binding", 0x604554, 0x180),
    ("header font-object loader continuation", 0x6047F0, 0x180),
    # The larger English window spans the same contiguous loader run down to
    # the already-source-mapped 0x9820A8 family.  This is still only bounded
    # source evidence; the caption index is promoted only after manual
    # instruction-by-instruction adjudication.
    ("English caption loader xref", 0x64AA80, 0x500),
    # Ordinary management text controls required by the fixed Gate-13 closure
    # slice.  These entry points are already proven by the Squad/League Tables
    # presentation research; the trace only exposes their raw font/style
    # arguments so aliases can be qualified without guessing.
    ("PLeagueTableRow visible text setup", 0x446930, 0x800),
    ("PSquadPlayerRow visible text setup", 0x489530, 0x800),
    ("PSCFRow visible text setup", 0x489B40, 0x600),
    ("shared ordinary eCText setup", 0x6503F0, 0x180),
    # Cover the existing family of source-qualified Zurich wrapper bindings so
    # any object pushed by the row setup windows can be matched to its exact
    # original .fnt path.  This remains private receipt evidence only.
    ("management font wrapper binding family", 0x603F00, 0xA00),
    ("shared picture source-frame mapper", 0x652780, 0x160),
    ("shared picture setup core", 0x6528D0, 0x100),
    ("shared header picture/control setup", 0x652940, 0x180),
    ("shared header text setup", 0x652980, 0x180),
    ("shared picture state selector continuation", 0x652A90, 0x120),
    ("shared picture update predicate", 0x652F80, 0x120),
)
HEADER_DATA_OBJECTS = (
    ("left header descriptor", 0x943A90, 0x40),
    ("right header descriptor", 0x943AD0, 0x40),
    ("header font object", 0x8B0760, 0x40),
    ("English caption global", 0x9820F4, 0x20),
)
POINTER_TARGETS = (
    ("left header descriptor", 0x943A90),
    ("right header descriptor", 0x943AD0),
    ("header font object", 0x8B0760),
    ("English caption global", 0x9820F4),
)


class Gate13ManagementHeaderTraceError(OriginalPETraceError):
    pass


def _bounded_record(pe: OriginalPE32, label: str, va: int, size: int,
                    *, with_disassembly: bool) -> dict:
    section, _ = pe.section_for_va(va)
    raw = pe.bounded_window(va, size)
    return {
        "label": label,
        "start_va": va,
        "section": section.name,
        "window_bytes": len(raw),
        "raw_hex": raw.hex(),
        "linear_disassembly_only": (
            disassemble_window(raw, va) if with_disassembly and section.name == ".text"
            else None
        ),
        "classification": "bounded_source_window_not_function_boundary",
    }


def _optional_data_record(pe: OriginalPE32, label: str, va: int, size: int) -> dict:
    try:
        section, _ = pe.section_for_va(va)
        raw = pe.bounded_window(va, size)
    except OriginalPETraceError as exc:
        return {
            "label": label,
            "start_va": va,
            "file_backed": False,
            "reason": str(exc),
        }
    words = [
        struct.unpack_from("<I", raw, offset)[0]
        for offset in range(0, len(raw) - (len(raw) % 4), 4)
    ]
    return {
        "label": label,
        "start_va": va,
        "file_backed": True,
        "section": section.name,
        "window_bytes": len(raw),
        "raw_hex": raw.hex(),
        "u32_words": words,
        "classification": "raw_descriptor_or_global_bytes_only",
    }


def _resource_record(root: Path, spec: dict) -> dict:
    path = root / spec["source_path"]
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if len(raw) < 4:
        raise Gate13ManagementHeaderTraceError(
            f"{spec['source_path']} is too short for an EA444 header"
        )
    dimensions = struct.unpack_from("<HH", raw, 0)
    expected_size = tuple(spec["size"])
    if dimensions != expected_size:
        raise Gate13ManagementHeaderTraceError(
            f"{spec['source_path']} geometry {dimensions} != {expected_size}"
        )
    if digest != spec["sha256"]:
        raise Gate13ManagementHeaderTraceError(
            f"{spec['source_path']} SHA-256 does not match the qualified source"
        )
    return {
        "role": spec["role"],
        "source_path": spec["source_path"],
        "size_bytes": len(raw),
        "sha256": digest,
        "dimensions": list(dimensions),
        "destination_rect": list(spec["destination_rect"]),
        "verified": True,
    }


def inspect_source_resources(source_root: Path) -> dict:
    root = Path(source_root)
    art = tuple(_resource_record(root, spec) for spec in HEADER_ART)
    font = root / HEADER_FONT_PATH
    font_raw = font.read_bytes()
    return {
        "header_art": art,
        "font": {
            "source_path": HEADER_FONT_PATH,
            "size_bytes": len(font_raw),
            "sha256": sha256(font_raw).hexdigest(),
            "classification": "exact_source_identity_only_font_alias_semantics_pending",
        },
    }


def management_header_trace_report(
    pe: OriginalPE32,
    *,
    source_root: Path | None = None,
    with_disassembly: bool = False,
) -> dict:
    windows = tuple(
        _bounded_record(pe, label, va, size, with_disassembly=with_disassembly)
        for label, va, size in HEADER_WINDOWS
    )
    data_objects = tuple(
        _optional_data_record(pe, label, va, size)
        for label, va, size in HEADER_DATA_OBJECTS
    )
    pointer_candidates = tuple({
        "target_name": label,
        "target_va": va,
        "byte_occurrences_not_proven_xrefs": pe.pointer_byte_candidates(va),
    } for label, va in POINTER_TARGETS)
    return {
        "source_sha256": pe.sha256,
        "image_base": pe.image_base,
        "known_geometry": {
            "compound_rect": [599, 0, 100, 95],
            "left_child_local_rect": [0, 0, 30, 95],
            "right_child_local_rect": [30, 0, 70, 95],
            "caption_local_rect": [32, 62, 70, 30],
            "caption_style": 10,
        },
        "windows": windows,
        "data_objects": data_objects,
        "pointer_candidates": pointer_candidates,
        "resources": (
            inspect_source_resources(source_root) if source_root is not None else None
        ),
        "conclusions_intentionally_not_promoted": {
            "left_child_frame_selector": None,
            "right_child_frame_selector": None,
            "left_child_update_owner": None,
            "right_child_update_owner": None,
            "caption_english_loader_index": None,
            "ordinary_management_text_font_aliases": None,
        },
        "evidence_limit": (
            "Exact canonical-PE bounded bytes/disassembly, file-backed descriptor "
            "dwords, raw pointer-byte candidates, and exact source-asset identities "
            "only. Frame/state semantics, update ownership, localization index and "
            "font aliases require manual control-flow/data-flow adjudication."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disassemble", action="store_true")
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = management_header_trace_report(
        pe,
        source_root=args.source_root,
        with_disassembly=args.disassemble,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-13 management-header trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())