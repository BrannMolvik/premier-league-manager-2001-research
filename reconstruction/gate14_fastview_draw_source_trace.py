"""Private bounded source trace for unresolved FastView child/draw ordering.

This tool prepares exact checksum-gated executable windows around already-known
FastViewPanel, generic Panel, PictureControl, and generic control draw code.
It is an evidence collector only. Linear disassembly and raw pointer-byte hits
must not be promoted to child-list direction, paint order, z-order, clipping,
or complete-frame semantics without manual control-flow/data-flow adjudication.

No proprietary executable bytes or generated trace output belong in Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    disassemble_window,
    require_private_output_path,
)


class Gate14FastViewDrawTraceError(OriginalPETraceError):
    pass


# These are already established source neighborhoods from canonical Gate-14
# research. Window sizes are inspection bounds, not function-boundary claims.
FASTVIEW_DRAW_WINDOWS = (
    ("FastViewPanel constructor", 0x51F490, 0x500),
    ("Generic Panel constructor", 0x527350, 0x80),
    ("Generic PictureControl constructor", 0x527730, 0x180),
    ("Generic text/control draw neighborhood", 0x64F090, 0x180),
)

# PictureControl vtable is source-closed by RTTI. The FastViewPanel constructor
# address is included as a code target only to help find candidate owner links.
FASTVIEW_DRAW_TARGETS = (
    ("PictureControl vtable", 0x7CAA5C),
    ("FastViewPanel constructor", 0x51F490),
    ("Generic Panel constructor", 0x527350),
    ("PictureControl constructor", 0x527730),
    ("Generic control draw neighborhood", 0x64F090),
)


def fastview_draw_trace_report(
    pe: OriginalPE32,
    *,
    with_disassembly: bool = True,
    windows=FASTVIEW_DRAW_WINDOWS,
    targets=FASTVIEW_DRAW_TARGETS,
) -> dict:
    """Return only bounded candidate evidence for later manual adjudication."""
    if type(with_disassembly) is not bool:
        raise Gate14FastViewDrawTraceError("with_disassembly must be boolean")

    inspected = []
    for label, start_va, requested_size in tuple(windows):
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate14FastViewDrawTraceError("invalid FastView draw trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14FastViewDrawTraceError(
                f"{label}: expected source-qualified code in .text"
            )
        raw = pe.bounded_window(start_va, requested_size)
        inspected.append(
            {
                "label": label,
                "start_va": start_va,
                "section": section.name,
                "window_bytes": len(raw),
                "raw_hex": raw.hex(),
                "linear_disassembly_only": (
                    disassemble_window(raw, start_va)
                    if with_disassembly
                    else None
                ),
            }
        )

    target_candidates = []
    for label, target_va in tuple(targets):
        if not isinstance(label, str) or not label or type(target_va) is not int:
            raise Gate14FastViewDrawTraceError("invalid FastView draw trace target")
        target_candidates.append(
            {
                "target_name": label,
                "target_va": target_va,
                "raw_pointer_byte_candidates_not_proven_xrefs": (
                    pe.pointer_byte_candidates(target_va)
                ),
            }
        )

    return {
        "source_sha256": pe.sha256,
        "windows": tuple(inspected),
        "target_candidates": tuple(target_candidates),
        "child_list_direction_recovered": False,
        "cross_component_z_order_recovered": False,
        "picture_control_resize_semantics_recovered": False,
        "complete_fastview_frame_recovered": False,
        "evidence_limit": (
            "Bounded source bytes, optional linear disassembly, and raw pointer-"
            "byte candidates only. This report does not prove function boundaries, "
            "CFG reachability, child-list insertion/traversal direction, paint "
            "order, z-order, clipping/scaling, or complete FastView composition."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Private JSON evidence path outside the Git repository",
    )
    parser.add_argument(
        "--no-disassembly",
        action="store_true",
        help="Collect bounded bytes and raw pointer candidates only",
    )
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = fastview_draw_trace_report(
        pe,
        with_disassembly=not args.no_disassembly,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 FastView draw trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
