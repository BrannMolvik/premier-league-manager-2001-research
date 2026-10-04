"""Private checksum-gated trace for FM2001 glyph compositing.

The source-backed FastView text path is known to use generic text rendering at
0x64F090 and EA font draw routine 0x657280. Canonical source tracing now also
closes the packed 16-bit destination-read blend used by that glyph path.

The pure primitive in this module mirrors only the source-proven non-color-key
packed-pixel arithmetic. It deliberately does not choose runtime RGB masks,
convert modern RGBA planes back to the native surface format, or resolve any
FastView overlap pixel.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
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
FONT_GLYPH_DRAW_VA = 0x6570F0
FONT_GLYPH_PACKED16_BLIT_VA = 0x658BC0
FONT_LOADER_VA = 0x657650
POSSESSION_TEXT_STYLE_SELECTOR_VA = 0x527BA0
POSSESSION_TEXT_FONT_OBJECT_VA = 0x9197E0
POSSESSION_TEXT_FONT_WRAPPER_VA = 0x87BE90

NATIVE_PIXEL_MASK_SETUP_VA = 0x656320
NATIVE_RED_MASK_SOURCE_OFFSET = 0x10
NATIVE_GREEN_MASK_SOURCE_OFFSET = 0x14
NATIVE_BLUE_MASK_SOURCE_OFFSET = 0x18
NATIVE_RED_MASK_GLOBAL_VA = 0x9848DC
NATIVE_GREEN_MASK_GLOBAL_VA = 0x9848D8
NATIVE_BLUE_MASK_GLOBAL_VA = 0x9848D4
NATIVE_COLOR_KEY_GLOBAL_VA = 0x87B680

# Three orientation branches in 0x658BC0 duplicate the same alpha load/blend
# primitive. These anchors document the actual destination-read path.
GLYPH_ALPHA_LOAD_VAS = (0x658D05, 0x658E3A, 0x658F82)
GLYPH_DESTINATION_READ_VAS = (0x658D2C, 0x658E63, 0x658FA9)
GLYPH_ALPHA_ZERO_BRANCH_VAS = (0x658D14, 0x658E4B, 0x658F91)
GLYPH_ALPHA_FULL_BRANCH_VAS = (0x658D1C, 0x658E53, 0x658F99)

FONT_BLEND_TRACE_WINDOWS = (
    ("generic text draw", GENERIC_TEXT_DRAW_VA, 0x240),
    ("native text/control color setter", NATIVE_COLOR_SETTER_VA, 0x100),
    ("EA font draw", FONT_DRAW_VA, 0x260),
    ("EA glyph draw/dispatch", FONT_GLYPH_DRAW_VA, 0x190),
    ("EA packed-16 glyph blit", FONT_GLYPH_PACKED16_BLIT_VA, 0x530),
    ("native RGB mask setup", NATIVE_PIXEL_MASK_SETUP_VA, 0x70),
    ("EA font loader", FONT_LOADER_VA, 0x160),
    ("generic text style selector", POSSESSION_TEXT_STYLE_SELECTOR_VA, 0x80),
)


@dataclass(frozen=True)
class Native16PixelMasks:
    """One runtime 16-bit RGB mask set accepted by the source primitive."""

    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        values = (self.red, self.green, self.blue)
        if any(type(value) is not int or not 0 < value <= 0xFFFF for value in values):
            raise Gate14FontBlendTraceError(
                "native RGB masks must be non-zero uint16 values"
            )
        if self.red & self.green or self.red & self.blue or self.green & self.blue:
            raise Gate14FontBlendTraceError(
                "native RGB masks must be pairwise disjoint"
            )


def blend_native_font_pixel16(
    destination_pixel: int,
    source_color: int,
    glyph_alpha: int,
    masks: Native16PixelMasks,
) -> int:
    """Mirror the source packed-16 intermediate-alpha arithmetic.

    0x658BC0 has explicit alpha-0 and alpha-255 endpoint branches. For alpha
    1..254, each runtime RGB mask is blended independently as:

      ((destination & mask) * (256 - alpha)
       + (source & mask) * alpha) >> 8

    then masked and merged back into the destination word. Bits outside the
    three supplied masks are preserved in the intermediate-alpha branch.

    The original routine also has color-key guards around this arithmetic.
    Their exact font-call applicability remains deliberately outside this pure
    primitive, so callers may not treat this function alone as a complete
    FastView overlap compositor.
    """
    if type(destination_pixel) is not int or not 0 <= destination_pixel <= 0xFFFF:
        raise Gate14FontBlendTraceError(
            "destination_pixel must be a uint16"
        )
    if type(source_color) is not int or not 0 <= source_color <= 0xFFFF:
        raise Gate14FontBlendTraceError("source_color must be a uint16")
    if type(glyph_alpha) is not int or not 0 <= glyph_alpha <= 0xFF:
        raise Gate14FontBlendTraceError("glyph_alpha must be a uint8")
    if type(masks) is not Native16PixelMasks:
        raise Gate14FontBlendTraceError(
            "masks must be an exact Native16PixelMasks"
        )

    if glyph_alpha == 0:
        return destination_pixel
    if glyph_alpha == 0xFF:
        return source_color

    inverse_alpha = 0x100 - glyph_alpha
    result = destination_pixel
    for mask in (masks.red, masks.green, masks.blue):
        destination_channel = result & mask
        source_channel = source_color & mask
        blended = (
            destination_channel * inverse_alpha
            + source_channel * glyph_alpha
        ) >> 8
        blended &= mask
        result = (result & (~mask & 0xFFFF)) | blended
    return result & 0xFFFF


def classify_font_blend_dataflow_candidates(
    pe: OriginalPE32,
    *,
    windows=None,
) -> tuple[dict, ...]:
    """Classify bounded font-render memory access candidates.

    The access direction reported here comes only from Capstone instruction
    metadata. Source adjudication outside this helper is still required before
    assigning object identity or semantics to a candidate.
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
                        "bounded_linear_font_dataflow_candidate_not_object_identity_proof"
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
    """Collect bounded glyph-render evidence with the recovered blend boundary."""
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
        "font_glyph_draw_va": FONT_GLYPH_DRAW_VA,
        "font_glyph_packed16_blit_va": FONT_GLYPH_PACKED16_BLIT_VA,
        "font_loader_va": FONT_LOADER_VA,
        "style_selector_va": POSSESSION_TEXT_STYLE_SELECTOR_VA,
        "font_object_va": POSSESSION_TEXT_FONT_OBJECT_VA,
        "font_wrapper_va": POSSESSION_TEXT_FONT_WRAPPER_VA,
        "native_pixel_mask_setup_va": NATIVE_PIXEL_MASK_SETUP_VA,
        "native_rgb_mask_source_offsets": {
            "red": NATIVE_RED_MASK_SOURCE_OFFSET,
            "green": NATIVE_GREEN_MASK_SOURCE_OFFSET,
            "blue": NATIVE_BLUE_MASK_SOURCE_OFFSET,
        },
        "native_rgb_mask_globals": {
            "red": NATIVE_RED_MASK_GLOBAL_VA,
            "green": NATIVE_GREEN_MASK_GLOBAL_VA,
            "blue": NATIVE_BLUE_MASK_GLOBAL_VA,
        },
        "native_color_key_global_va": NATIVE_COLOR_KEY_GLOBAL_VA,
        "glyph_alpha_load_vas": GLYPH_ALPHA_LOAD_VAS,
        "glyph_destination_read_vas": GLYPH_DESTINATION_READ_VAS,
        "glyph_alpha_zero_branch_vas": GLYPH_ALPHA_ZERO_BRANCH_VAS,
        "glyph_alpha_full_branch_vas": GLYPH_ALPHA_FULL_BRANCH_VAS,
        "windows": tuple(inspected),
        "font_dataflow_candidates_classified": bool(classify_dataflow_candidates),
        "bounded_font_dataflow_candidates_not_object_identity_proof": (
            classify_font_blend_dataflow_candidates(pe, windows=windows)
            if classify_dataflow_candidates
            else ()
        ),
        "glyph_alpha_source_recovered": True,
        "possession_pairwise_draw_order_recovered": True,
        "glyph_destination_read_recovered": True,
        "glyph_alpha_blend_rule_recovered": True,
        "runtime_rgb_mask_source_recovered": True,
        "native_color_channel_layout_recovered": False,
        "font_color_key_applicability_recovered": False,
        "cross_component_pixels_resolvable": False,
        "complete_fastview_frame_recovered": False,
        "evidence_limit": (
            "The source now proves the packed-16 glyph destination read, alpha "
            "0/255 endpoints, mask-wise intermediate formula with denominator "
            "256, and that RGB masks are populated from the runtime surface "
            "pixel-format fields. It does not yet bind the actual runtime mask "
            "values for the target Windows surface, prove the font-call color-key "
            "boundary, or provide an exact modern-RGBA to native-pixel round trip. "
            "No FastView overlap pixel is therefore promoted."
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
            "font blend analysis"
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
