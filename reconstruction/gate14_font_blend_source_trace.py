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


def classify_font_blend_dataflow_candidates(
    pe: OriginalPE32,
    *,
    windows=None,
) -> tuple[dict, ...]:
    """Classify bounded font-render memory access candidates without blend promotion.

    The access direction reported here comes only from Capstone instruction
    metadata. A read/write operand is still not identified as a framebuffer,
    glyph-alpha source, color channel, or blend accumulator without manual
    object/data-flow adjudication.
    """
    if windows is None:
        windows = FONT_BLEND_TRACE_WINDOWS
    try:
        from capstone import CS_AC_READ, CS_AC_WRITE, CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM, X86_OP_MEM
    except ImportError as exc:
        raise Gate14FontBlendTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    output: list[dict] = []

    def access_name(flags: int) -> str:
        read = bool(flags & CS_AC_READ)
        write = bool(flags & CS_AC_WRITE)
        if read and write:
            return "read_write"
        if read:
            return "read"
        if write:
            return "write"
        return "unreported"

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

        for insn in engine.disasm(raw, start_va):
            memory_operands: list[dict] = []
            immediates: list[int] = []
            for operand_index, operand in enumerate(insn.operands):
                if operand.type == X86_OP_IMM:
                    immediates.append(int(operand.imm) & 0xFFFFFFFF)
                elif operand.type == X86_OP_MEM:
                    memory_operands.append(
                        {
                            "operand_index": int(operand_index),
                            "base": (
                                insn.reg_name(operand.mem.base)
                                if operand.mem.base
                                else None
                            ),
                            "index": (
                                insn.reg_name(operand.mem.index)
                                if operand.mem.index
                                else None
                            ),
                            "scale": int(operand.mem.scale),
                            "displacement": int(operand.mem.disp),
                            "operand_size": int(operand.size),
                            "access": access_name(int(operand.access)),
                        }
                    )
            if not memory_operands and not immediates:
                continue
            output.append(
                {
                    "window_label": label,
                    "instruction_va": int(insn.address),
                    "instruction_size": int(insn.size),
                    "bytes": bytes(insn.bytes).hex(),
                    "mnemonic": insn.mnemonic,
                    "operands": insn.op_str,
                    "immediate_candidates": tuple(immediates),
                    "memory_operand_candidates": tuple(memory_operands),
                    "classification": (
                        "bounded_linear_font_dataflow_candidate_not_framebuffer_or_blend_proof"
                    ),
                }
            )

    return tuple(output)


def font_blend_trace_report(
    pe: OriginalPE32,
    *,
    windows=None,
    with_disassembly: bool = True,
    classify_dataflow_candidates: bool = False,
) -> dict:
    """Collect bounded glyph-render evidence without promoting blend semantics."""
    if type(with_disassembly) is not bool:
        raise Gate14FontBlendTraceError("with_disassembly must be boolean")
    if type(classify_dataflow_candidates) is not bool:
        raise Gate14FontBlendTraceError(
            "classify_dataflow_candidates must be boolean"
        )
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
        "font_dataflow_candidates_classified": bool(classify_dataflow_candidates),
        "bounded_font_dataflow_candidates_not_blend_proof": (
            classify_font_blend_dataflow_candidates(pe, windows=windows)
            if classify_dataflow_candidates
            else ()
        ),
        "glyph_alpha_source_recovered": True,
        "possession_pairwise_draw_order_recovered": True,
        "glyph_destination_read_recovered": False,
        "glyph_alpha_blend_rule_recovered": False,
        "native_color_channel_layout_recovered": False,
        "cross_component_pixels_resolvable": False,
        "complete_fastview_frame_recovered": False,
        "evidence_limit": (
            "The 8-bit font atlas and text-after-diagram pairwise order are "
            "source-backed. These bounded code windows and optional memory-access "
            "candidates do not yet prove how non-binary glyph alpha combines with "
            "an existing destination, whether any candidate address is the "
            "framebuffer, or a general native color layout."
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
    parser.add_argument(
        "--classify-dataflow-candidates",
        action="store_true",
        help=(
            "Classify bounded memory access direction/immediates for manual "
            "font blend analysis; still not framebuffer or blend proof"
        ),
    )
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = font_blend_trace_report(
        pe,
        with_disassembly=not args.no_disassembly,
        classify_dataflow_candidates=args.classify_dataflow_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 font blend trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
