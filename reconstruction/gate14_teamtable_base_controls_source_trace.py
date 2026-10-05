"""Private checksum-gated source trace for the six TeamTable base controls.

The nested-order contract already proves that TeamTable owns exactly six
visible base controls before its parameterized PlayerRow children. Their
individual control kinds, construction callsites, argument semantics, geometry,
resources and pixels are not yet source-qualified.

This tool inspects only a bounded TeamTable constructor neighborhood and records
decoded direct calls to already-known generic control constructors plus the
PlayerRow constructor. A decoded call remains a discovery candidate only. It is
not proof that the call constructs one of the six base controls or of the
caller's arguments, role, registration order or visible pixels.

Generated executable bytes/disassembly must remain private outside Git.
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


class Gate14TeamTableBaseTraceError(OriginalPETraceError):
    pass


TEAM_TABLE_CONSTRUCTOR_VA = 0x524EC0
TEAM_PLAYERROW_CONSTRUCTOR_VA = 0x525DB0
TEAM_TABLE_BASE_CONTROL_COUNT = 6

GENERIC_PANEL_CONSTRUCTOR_VA = 0x527350
GENERIC_PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
GENERIC_TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960

TEAM_TABLE_BASE_TRACE_WINDOWS = (
    (
        "TeamTable constructor / base-control construction neighborhood",
        TEAM_TABLE_CONSTRUCTOR_VA,
        0x1200,
    ),
)

KNOWN_CONTROL_TARGETS = (
    ("generic_panel", GENERIC_PANEL_CONSTRUCTOR_VA),
    ("generic_picture_control", GENERIC_PICTURE_CONTROL_CONSTRUCTOR_VA),
    ("generic_text_control", GENERIC_TEXT_CONTROL_CONSTRUCTOR_VA),
    ("player_row", TEAM_PLAYERROW_CONSTRUCTOR_VA),
)


@dataclass(frozen=True)
class TeamTableDirectCallCandidate:
    owner_window: str
    callsite_va: int
    target_name: str
    target_va: int
    preceding_linear_context_not_argument_proof: tuple[dict, ...]
    classification: str = (
        "decoded_direct_teamtable_call_candidate_not_base_control_or_argument_proof"
    )


def _load_capstone():
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM
    except ImportError as exc:
        raise Gate14TeamTableBaseTraceError(
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


def direct_known_control_calls(
    pe: OriginalPE32,
    *,
    windows=TEAM_TABLE_BASE_TRACE_WINDOWS,
    targets=KNOWN_CONTROL_TARGETS,
    context_instructions: int = 12,
) -> tuple[TeamTableDirectCallCandidate, ...]:
    """Find direct calls to known control constructors in bounded TeamTable code."""
    if type(context_instructions) is not int or not 1 <= context_instructions <= 64:
        raise Gate14TeamTableBaseTraceError(
            "context_instructions must be within 1..64"
        )

    normalized_targets: dict[int, str] = {}
    for item in tuple(targets):
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not item[0]
            or type(item[1]) is not int
            or not 0 <= item[1] < 1 << 32
        ):
            raise Gate14TeamTableBaseTraceError(
                "targets must be (non-empty name, uint32 VA) pairs"
            )
        name, va = item
        if va in normalized_targets:
            raise Gate14TeamTableBaseTraceError(
                "known constructor target VAs must be unique"
            )
        normalized_targets[va] = name

    engine, immediate_type = _load_capstone()
    output = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14TeamTableBaseTraceError(
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
            raise Gate14TeamTableBaseTraceError(
                "invalid TeamTable base-control trace window"
            )

        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14TeamTableBaseTraceError(
                f"{label}: expected source-qualified code window in .text"
            )
        blob = pe.bounded_window(start_va, requested_size)
        instructions = tuple(engine.disasm(blob, start_va))
        for index, insn in enumerate(instructions):
            if (
                insn.mnemonic != "call"
                or len(insn.operands) != 1
                or insn.operands[0].type != immediate_type
            ):
                continue
            target_va = int(insn.operands[0].imm) & 0xFFFFFFFF
            target_name = normalized_targets.get(target_va)
            if target_name is None:
                continue
            context_start = max(0, index - context_instructions)
            output.append(
                TeamTableDirectCallCandidate(
                    owner_window=label,
                    callsite_va=int(insn.address),
                    target_name=target_name,
                    target_va=target_va,
                    preceding_linear_context_not_argument_proof=tuple(
                        _instruction_record(value)
                        for value in instructions[context_start:index]
                    ),
                )
            )

    return tuple(output)


def teamtable_base_trace_report(
    pe: OriginalPE32,
    *,
    windows=TEAM_TABLE_BASE_TRACE_WINDOWS,
    targets=KNOWN_CONTROL_TARGETS,
    context_instructions: int = 12,
    with_disassembly: bool = False,
) -> dict:
    """Collect bounded source candidates without promoting the six base controls."""
    if type(with_disassembly) is not bool:
        raise Gate14TeamTableBaseTraceError("with_disassembly must be boolean")

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14TeamTableBaseTraceError(
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
            raise Gate14TeamTableBaseTraceError(
                "invalid TeamTable base-control trace window"
            )
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14TeamTableBaseTraceError(
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

    calls = direct_known_control_calls(
        pe,
        windows=windows,
        targets=targets,
        context_instructions=context_instructions,
    )
    return {
        "source_sha256": pe.sha256,
        "team_table_constructor_va": TEAM_TABLE_CONSTRUCTOR_VA,
        "team_playerrow_constructor_va": TEAM_PLAYERROW_CONSTRUCTOR_VA,
        "source_closed_team_table_base_control_count": TEAM_TABLE_BASE_CONTROL_COUNT,
        "known_control_targets": tuple(
            {"name": name, "target_va": va}
            for name, va in tuple(targets)
        ),
        "windows": tuple(inspected),
        "direct_known_control_calls_not_base_control_proof": tuple(
            {
                "owner_window": item.owner_window,
                "callsite_va": item.callsite_va,
                "target_name": item.target_name,
                "target_va": item.target_va,
                "preceding_linear_context_not_argument_proof": (
                    item.preceding_linear_context_not_argument_proof
                ),
                "classification": item.classification,
            }
            for item in calls
        ),
        "team_table_base_control_count_recovered": True,
        "team_table_base_control_identities_recovered": False,
        "team_table_base_control_constructor_calls_adjudicated": False,
        "team_table_base_control_registration_order_recovered": False,
        "team_table_base_control_geometry_recovered": False,
        "team_table_base_control_resources_recovered": False,
        "team_table_base_control_text_semantics_recovered": False,
        "team_table_base_control_pixels_rasterized": False,
        "complete_team_table": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
        "evidence_limit": (
            "Bounded canonical TeamTable constructor bytes and decoded direct calls "
            "to already-known generic control constructors only. Candidate calls are "
            "not proof that a call belongs to one of the six base controls, nor of "
            "argument positions, control roles, registration order, geometry, "
            "resources, text semantics, pixels, complete TeamTable output or Gate 14."
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
    report = teamtable_base_trace_report(
        pe,
        context_instructions=args.context_instructions,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 TeamTable base-control trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
