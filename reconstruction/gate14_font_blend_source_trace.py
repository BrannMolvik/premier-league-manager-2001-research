"""Private checksum-gated trace for FM2001 glyph compositing.

The source-backed FastView PossessionFigures text path is already known to use
generic text rendering at 0x64F090 and the EA font draw routine at 0x657280.
Pairwise native draw order now proves that PossessionFigures are painted after
PossessionDiagram, but masked overlap pixels cannot be flattened until the
font's 8-bit alpha/compositing rule over an existing destination is recovered.

This tool captures only bounded source windows around those already-qualified
anchors. It does not infer standard alpha-over, color-channel layout, blending,
destination reads, or any complete FastView composition rule. Generated
disassembly must remain private.
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


class Gate14FontBlendTraceError(OriginalPETraceError):
    pass


GENERIC_TEXT_DRAW_VA = 0x64F090
NATIVE_COLOR_SETTER_VA = 0x650480
FONT_DRAW_VA = 0x657280
FONT_LOADER_VA = 0x657650
POSSESSION_TEXT_STYLE_SELECTOR_VA = 0x527BA0
POSSESSION_TEXT_FONT_OBJECT_VA = 0x9197E0
POSSESSION_TEXT_FONT_WRAPPER_VA = 0x87BE90

FONT_BLEND_TRACE_WINDOWS = (
    ("generic text draw", GENERIC_TEXT_DRAW_VA, 0x240),
    ("native text/control color setter", NATIVE_COLOR_SETTER_VA, 0x100),
    ("EA font draw", FONT_DRAW_VA, 0x260),
    ("EA font loader", FONT_LOADER_VA, 0x160),
    ("generic text style selector", POSSESSION_TEXT_STYLE_SELECTOR_VA, 0x80),
)


def font_blend_trace_report(
    pe: OriginalPE32,
    *,
    windows=None,
    with_disassembly: bool = True,
) -> dict:
    """Collect bounded glyph-render evidence without promoting blend semantics."""
    if type(with_disassembly) is not bool:
        raise Gate14FontBlendTraceError("with_disassembly must be boolean")
    if windows is None:
        windows = FONT_BLEND_TRACE_WINDOWS

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14FontBlendTraceError(
                "font blend windows must be (label, start_va, requested_size)"
            )
        label, start_va, requested_size = item
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate14FontBlendTraceError("invalid font blend trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14FontBlendTraceError(
                f"{label}: expected source-qualified code in .text"
            )
        raw = pe.bounded_window(start_va, requested_size)
        inspected.append(
            {
                "label": label,
                "start_va": start_va,
                "requested_size": requested_size,
                "actual_window_bytes": len(raw),
                "section": section.name,
                "raw_hex": raw.hex(),
                "linear_disassembly_only": (
                    tuple(disassemble_window(raw, start_va))
                    if with_disassembly
                    else None
                ),
                "classification": "bounded_font_render_window_not_cfg_proof",
            }
        )

    return {
        "source_sha256": pe.sha256,
        "generic_text_draw_va": GENERIC_TEXT_DRAW_VA,
        "native_color_setter_va": NATIVE_COLOR_SETTER_VA,
        "font_draw_va": FONT_DRAW_VA,
        "font_loader_va": FONT_LOADER_VA,
        "style_selector_va": POSSESSION_TEXT_STYLE_SELECTOR_VA,
        "font_object_va": POSSESSION_TEXT_FONT_OBJECT_VA,
        "font_wrapper_va": POSSESSION_TEXT_FONT_WRAPPER_VA,
        "windows": tuple(inspected),
        "glyph_alpha_source_recovered": True,
        "possession_pairwise_draw_order_recovered": True,
        "glyph_destination_read_recovered": False,
        "glyph_alpha_blend_rule_recovered": False,
        "native_color_channel_layout_recovered": False,
        "cross_component_pixels_resolvable": False,
        "complete_fastview_frame_recovered": False,
        "evidence_limit": (
            "The 8-bit font atlas and text-after-diagram pairwise order are "
            "source-backed. These bounded code windows do not yet prove how "
            "non-binary glyph alpha combines with an existing destination, "
            "whether the destination is read, or a general native color layout."
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
    parser.add_argument("--no-disassembly", action="store_true")
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = font_blend_trace_report(
        pe,
        with_disassembly=not args.no_disassembly,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 font blend trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
