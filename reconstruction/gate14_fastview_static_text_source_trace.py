"""Private checksum-gated source trace for omitted FastView score/table text.

The repository already source-closes the geometry and source order of static
ScoreCompositeNormal and LeagueTable TextControls, but deliberately does not
claim their semantic values, style/font/color arguments or raster pixels.

This tool narrows the next private-source pass to the exact constructors that
own those visible controls and the generic TextControl implementation. It emits
bounded source windows plus decoded direct-CALL candidates to the generic
TextControl constructor. Candidate callsites and preceding instructions remain
linear-disassembly evidence only: no argument position, style, text meaning,
font, color, control value or raster fidelity is promoted automatically.

Generated executable bytes/disassembly must remain private outside Git.
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


class Gate14FastViewStaticTextTraceError(OriginalPETraceError):
    pass


SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA = 0x51A730
LEAGUE_TABLE_ROW_CONSTRUCTOR_VA = 0x51D730
LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA = 0x51DCB0
GENERIC_TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960
GENERIC_TEXT_STYLE_SELECTOR_VA = 0x527BA0
GENERIC_TEXT_DRAW_VA = 0x64F090

# Inspection ranges only, not complete function-boundary claims.
STATIC_TEXT_TRACE_WINDOWS = (
    (
        "ScoreComposite shared base visible-control construction",
        SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA,
        0x400,
    ),
    (
        "LeagueTable Row visible-control construction",
        LEAGUE_TABLE_ROW_CONSTRUCTOR_VA,
        0x580,
    ),
    (
        "LeagueTable Heading visible-control construction",
        LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA,
        0x350,
    ),
    (
        "Generic TextControl constructor",
        GENERIC_TEXT_CONTROL_CONSTRUCTOR_VA,
        0x240,
    ),
    (
        "Generic TextControl style selector",
        GENERIC_TEXT_STYLE_SELECTOR_VA,
        0x100,
    ),
    (
        "Generic text draw neighborhood",
        GENERIC_TEXT_DRAW_VA,
        0x180,
    ),
)


def _load_capstone():
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM
    except ImportError as exc:
        raise Gate14FastViewStaticTextTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc
    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    return engine, X86_OP_IMM


def _instruction_record(insn) -> dict:
    return {
        "va": int(insn.address),
        "size": int(insn.size),
        "bytes": bytes(insn.bytes).hex(),
        "mnemonic": insn.mnemonic,
        "operands": insn.op_str,
    }


def direct_text_constructor_calls(
    pe: OriginalPE32,
    *,
    windows=STATIC_TEXT_TRACE_WINDOWS[:3],
    target_va: int = GENERIC_TEXT_CONTROL_CONSTRUCTOR_VA,
    context_instructions: int = 12,
) -> tuple[dict, ...]:
    """Find decoded direct calls to TextControl in the bounded owner windows."""
    if type(target_va) is not int or not 0 <= target_va < 1 << 32:
        raise Gate14FastViewStaticTextTraceError("target_va must be uint32")
    if type(context_instructions) is not int or not 1 <= context_instructions <= 64:
        raise Gate14FastViewStaticTextTraceError(
            "context_instructions must be within 1..64"
        )

    engine, immediate_type = _load_capstone()
    output = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14FastViewStaticTextTraceError(
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
            raise Gate14FastViewStaticTextTraceError("invalid static-text trace window")

        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14FastViewStaticTextTraceError(
                f"{label}: expected source-qualified code window in .text"
            )
        blob = pe.bounded_window(start_va, requested_size)
        instructions = tuple(engine.disasm(blob, start_va))
        for index, insn in enumerate(instructions):
            if (
                insn.mnemonic != "call"
                or len(insn.operands) != 1
                or insn.operands[0].type != immediate_type
                or (int(insn.operands[0].imm) & 0xFFFFFFFF) != target_va
            ):
                continue
            context_start = max(0, index - context_instructions)
            output.append(
                {
                    "owner_window": label,
                    "callsite_va": int(insn.address),
                    "target_va": target_va,
                    "preceding_linear_context_not_argument_proof": tuple(
                        _instruction_record(value)
                        for value in instructions[context_start:index]
                    ),
                    "call_instruction": _instruction_record(insn),
                    "classification": (
                        "decoded_direct_textcontrol_call_candidate_"
                        "not_argument_or_semantic_proof"
                    ),
                }
            )
    return tuple(output)


def static_text_trace_report(
    pe: OriginalPE32,
    *,
    windows=STATIC_TEXT_TRACE_WINDOWS,
    text_owner_windows=STATIC_TEXT_TRACE_WINDOWS[:3],
    target_va: int = GENERIC_TEXT_CONTROL_CONSTRUCTOR_VA,
    context_instructions: int = 12,
    with_disassembly: bool = False,
) -> dict:
    """Collect exact bounded evidence without promoting missing text semantics."""
    if type(with_disassembly) is not bool:
        raise Gate14FastViewStaticTextTraceError(
            "with_disassembly must be boolean"
        )

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14FastViewStaticTextTraceError(
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
            raise Gate14FastViewStaticTextTraceError(
                "invalid static-text trace window"
            )
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14FastViewStaticTextTraceError(
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

    calls = direct_text_constructor_calls(
        pe,
        windows=text_owner_windows,
        target_va=target_va,
        context_instructions=context_instructions,
    )
    return {
        "source_sha256": pe.sha256,
        "score_composite_base_constructor_va": SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA,
        "league_table_row_constructor_va": LEAGUE_TABLE_ROW_CONSTRUCTOR_VA,
        "league_table_heading_constructor_va": LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA,
        "generic_textcontrol_constructor_va": target_va,
        "generic_text_style_selector_va": GENERIC_TEXT_STYLE_SELECTOR_VA,
        "generic_text_draw_va": GENERIC_TEXT_DRAW_VA,
        "windows": tuple(inspected),
        "direct_textcontrol_calls_not_argument_proof": calls,
        "static_text_control_geometry_recovered": True,
        "static_text_source_order_recovered": True,
        "argument_positions_recovered": False,
        "user_facing_semantics_recovered": False,
        "final_text_values_recovered": False,
        "font_style_color_recovered": False,
        "pixels_rasterized": False,
        "score_subpanel_complete_pixels_recovered": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
        "evidence_limit": (
            "Bounded canonical source windows and decoded direct TextControl calls "
            "only. Linear predecessor instructions are not proof of argument "
            "positions, text values/meaning, style, font, color, runtime update "
            "semantics, pixels, complete score-subpanel output or Gate 14."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument("--context-instructions", type=int, default=12)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = static_text_trace_report(
        pe,
        context_instructions=args.context_instructions,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 FastView static-text trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
