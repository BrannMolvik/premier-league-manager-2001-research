"""Private checksum-gated Gate-14 PictureControl renderer trace.

The remaining FastView raster gaps include cross-component draw/z-order and the
generic PictureControl source/destination-rectangle behavior needed for dynamic
PlayerRow energy bars. This tool records only already-known source anchors and
bounded candidate evidence from the canonical original PE.

It does not assign virtual-slot semantics, vtable extent, draw order, scaling,
cropping, blending, child-registration direction, or FastView visibility rules.
All emitted executable bytes/disassembly must remain private.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import struct

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    disassemble_window,
    require_private_output_path,
)


class Gate14PictureControlTraceError(OriginalPETraceError):
    pass


PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
PICTURE_CONTROL_VFTABLE_VA = 0x7CAA5C
GENERIC_PANEL_CONSTRUCTOR_VA = 0x527350
GENERIC_CONTROL_DRAW_NEIGHBORHOOD_VA = 0x64F090
FASTVIEW_PANEL_CONSTRUCTOR_VA = 0x51F490
FASTVIEW_TOP_TICKER_WINDOW_VA = 0x51FD40
FASTVIEW_POSSESSION_CHILD_WINDOW_VA = 0x520690
PLAYER_ROW_ENERGY_RECT_WRITER_VA = 0x526680

# Bounded inspection ranges only, not exact function boundaries.
PICTURE_CONTROL_TRACE_WINDOWS = (
    (
        "FastViewPanel constructor head / 800x600 generic panel setup",
        FASTVIEW_PANEL_CONSTRUCTOR_VA,
        0x120,
    ),
    (
        "FastViewPanel top/ticker PictureControl construction",
        FASTVIEW_TOP_TICKER_WINDOW_VA,
        0x140,
    ),
    (
        "FastViewPanel PossessionDiagram child construction",
        FASTVIEW_POSSESSION_CHILD_WINDOW_VA,
        0x90,
    ),
    (
        "Generic panel constructor used by FastViewPanel",
        GENERIC_PANEL_CONSTRUCTOR_VA,
        0x180,
    ),
    (
        "Generic PictureControl constructor",
        PICTURE_CONTROL_CONSTRUCTOR_VA,
        0x180,
    ),
    (
        "Generic text/control draw neighborhood",
        GENERIC_CONTROL_DRAW_NEIGHBORHOOD_VA,
        0x180,
    ),
    (
        "PlayerRow EventPlayerUpdateEnergy rectangle writer",
        PLAYER_ROW_ENERGY_RECT_WRITER_VA,
        0x120,
    ),
)


@dataclass(frozen=True)
class PictureControlVtableSlotCandidate:
    slot_index: int
    slot_offset: int
    target_va: int
    target_section: str | None
    candidate_method_window_bytes: int
    linear_disassembly_only: tuple[dict, ...] | None
    classification: str = "bounded_picturecontrol_vtable_slot_candidate_only"


def picturecontrol_vtable_slot_candidates(
    pe: OriginalPE32,
    *,
    vtable_va: int = PICTURE_CONTROL_VFTABLE_VA,
    max_slots: int = 24,
    method_window_bytes: int = 0x80,
    with_disassembly: bool = False,
) -> tuple[PictureControlVtableSlotCandidate, ...]:
    """Read a bounded number of possible PictureControl vtable entries.

    The known RTTI-backed vtable address is source evidence. The requested slot
    count is only an analyst inspection bound; this helper does not claim that
    every retained entry belongs to the same complete vtable or that any slot is
    a draw method.
    """
    if type(vtable_va) is not int or not 0 <= vtable_va < 1 << 32:
        raise Gate14PictureControlTraceError("vtable_va must be uint32")
    if type(max_slots) is not int or not 1 <= max_slots <= 128:
        raise Gate14PictureControlTraceError("max_slots must be within 1..128")
    if type(method_window_bytes) is not int or not 1 <= method_window_bytes <= 0x1000:
        raise Gate14PictureControlTraceError(
            "method_window_bytes must be within 1..4096"
        )
    if type(with_disassembly) is not bool:
        raise Gate14PictureControlTraceError("with_disassembly must be boolean")

    vtable_section, _ = pe.section_for_va(vtable_va)
    if vtable_section.name == ".text":
        raise Gate14PictureControlTraceError(
            "PictureControl vtable candidate must not reside in .text"
        )

    output = []
    for slot_index in range(max_slots):
        slot_va = vtable_va + slot_index * 4
        try:
            raw = pe.read(slot_va, 4)
        except OriginalPETraceError:
            break
        target_va = struct.unpack("<I", raw)[0]

        target_section_name = None
        method_bytes = 0
        decoded = None
        try:
            target_section, _ = pe.section_for_va(target_va)
        except OriginalPETraceError:
            target_section = None

        if target_section is not None:
            target_section_name = target_section.name
            if target_section.name == ".text":
                blob = pe.bounded_window(target_va, method_window_bytes)
                method_bytes = len(blob)
                if with_disassembly:
                    decoded = tuple(disassemble_window(blob, target_va))

        output.append(
            PictureControlVtableSlotCandidate(
                slot_index=slot_index,
                slot_offset=slot_index * 4,
                target_va=target_va,
                target_section=target_section_name,
                candidate_method_window_bytes=method_bytes,
                linear_disassembly_only=decoded,
            )
        )

    return tuple(output)


def picturecontrol_trace_report(
    pe: OriginalPE32,
    *,
    windows=PICTURE_CONTROL_TRACE_WINDOWS,
    vtable_va: int = PICTURE_CONTROL_VFTABLE_VA,
    max_slots: int = 24,
    method_window_bytes: int = 0x80,
    with_disassembly: bool = False,
) -> dict:
    """Collect bounded source evidence without renderer-semantic promotion."""
    if type(with_disassembly) is not bool:
        raise Gate14PictureControlTraceError("with_disassembly must be boolean")

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14PictureControlTraceError(
                "trace windows must be (label, start_va, requested_size)"
            )
        label, start_va, requested_size = item
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate14PictureControlTraceError("invalid PictureControl trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14PictureControlTraceError(
                f"{label}: expected source-qualified code window in .text"
            )
        blob = pe.bounded_window(start_va, requested_size)
        inspected.append(
            {
                "label": label,
                "start_va": start_va,
                "requested_size": requested_size,
                "actual_window_bytes": len(blob),
                "section": section.name,
                "raw_hex": blob.hex(),
                "linear_disassembly_only": (
                    tuple(disassemble_window(blob, start_va))
                    if with_disassembly
                    else None
                ),
                "classification": "bounded_source_window_not_function_boundary",
            }
        )

    slots = picturecontrol_vtable_slot_candidates(
        pe,
        vtable_va=vtable_va,
        max_slots=max_slots,
        method_window_bytes=method_window_bytes,
        with_disassembly=with_disassembly,
    )

    return {
        "source_sha256": pe.sha256,
        "picturecontrol_constructor_va": PICTURE_CONTROL_CONSTRUCTOR_VA,
        "picturecontrol_vtable_va": vtable_va,
        "known_picturecontrol_rtti": ".?AVPictureControl@@",
        "windows": tuple(inspected),
        "picturecontrol_vtable_slot_candidates": tuple(
            {
                "slot_index": item.slot_index,
                "slot_offset": item.slot_offset,
                "target_va": item.target_va,
                "target_section": item.target_section,
                "candidate_method_window_bytes": item.candidate_method_window_bytes,
                "linear_disassembly_only": item.linear_disassembly_only,
                "classification": item.classification,
            }
            for item in slots
        ),
        "raw_vtable_pointer_byte_occurrences_not_proven_xrefs": (
            pe.pointer_byte_candidates(vtable_va)
        ),
        "cross_component_z_order_recovered": False,
        "picturecontrol_resize_pixels_recovered": False,
        "child_registration_order_recovered": False,
        "evidence_limit": (
            "Known source anchors, bounded bytes/disassembly, raw vtable-pointer "
            "occurrences and bounded candidate vtable slots only. No virtual-slot "
            "role, vtable extent, CFG reachability, child registration direction, "
            "draw/z-order, source-rectangle crop/stretch rule, alpha behavior, "
            "visibility policy or complete FastView frame is proven."
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
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument("--max-vtable-slots", type=int, default=24)
    parser.add_argument("--method-window-bytes", type=int, default=0x80)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = picturecontrol_trace_report(
        pe,
        max_slots=args.max_vtable_slots,
        method_window_bytes=args.method_window_bytes,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 PictureControl trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
