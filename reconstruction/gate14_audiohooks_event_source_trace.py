"""Private checksum-gated caller trace for FM2001 AudioHooks::0x5DBFC0.

The numeric AudioHooks switch and its literal menus.bnk slot routing are already
source-backed. What remains unresolved is which native senders construct each
numeric event id and state value.

This tool scans only the canonical PE .text section for decoded direct CALL
candidates whose target is the recovered AudioHooks dispatcher. For each
candidate it records a bounded instruction context and nearby PUSH operands.

A decoded direct CALL in linear section disassembly is still not proof of CFG
reachability, calling convention, argument position, event meaning, UI meaning,
match meaning, or sample meaning. Generated executable bytes/disassembly must
remain private.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    require_private_output_path,
)
from gate14_audiohooks_menu_dispatch import AUDIO_HOOKS_DISPATCH_VA


class Gate14AudioHooksCallerTraceError(OriginalPETraceError):
    pass


def _load_capstone():
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM, X86_OP_REG
    except ImportError as exc:
        raise Gate14AudioHooksCallerTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc
    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    return engine, X86_OP_IMM, X86_OP_REG


def _instruction_record(insn) -> dict:
    return {
        "va": int(insn.address),
        "size": int(insn.size),
        "bytes": bytes(insn.bytes).hex(),
        "mnemonic": insn.mnemonic,
        "operands": insn.op_str,
    }


def _nearby_push_candidates(
    instructions,
    call_index: int,
    *,
    context_instructions: int,
    immediate_type: int,
    register_type: int,
) -> tuple[dict, ...]:
    """Record nearby PUSH operands without assigning argument semantics."""
    start = max(0, call_index - context_instructions)
    preceding = instructions[start:call_index]
    output = []
    for distance, insn in enumerate(reversed(preceding), start=1):
        if insn.mnemonic != "push" or len(insn.operands) != 1:
            continue
        operand = insn.operands[0]
        row = {
            "instruction_va": int(insn.address),
            "distance_from_call_instructions": distance,
            "classification": (
                "nearby_push_operand_candidate_not_argument_or_semantic_proof"
            ),
        }
        if operand.type == immediate_type:
            row["operand_kind"] = "immediate"
            row["immediate_value"] = int(operand.imm) & 0xFFFFFFFF
        elif operand.type == register_type:
            row["operand_kind"] = "register"
            row["register_name"] = insn.reg_name(operand.reg)
        else:
            row["operand_kind"] = "other"
        output.append(row)
    return tuple(output)


def direct_audiohooks_call_candidates(
    pe: OriginalPE32,
    *,
    target_va: int = AUDIO_HOOKS_DISPATCH_VA,
    context_instructions: int = 8,
    max_candidates: int = 512,
) -> tuple[dict, ...]:
    """Find decoded direct CALL candidates to the recovered dispatcher."""
    if type(target_va) is not int or not 0 <= target_va < 1 << 32:
        raise Gate14AudioHooksCallerTraceError("target_va must be uint32")
    if type(context_instructions) is not int or context_instructions < 1:
        raise Gate14AudioHooksCallerTraceError(
            "context_instructions must be a positive integer"
        )
    if type(max_candidates) is not int or max_candidates < 1:
        raise Gate14AudioHooksCallerTraceError(
            "max_candidates must be a positive integer"
        )

    engine, X86_OP_IMM, X86_OP_REG = _load_capstone()
    output = []

    for section in pe.sections:
        if section.name != ".text":
            continue
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        start_va = pe.image_base + section.virtual_address
        instructions = tuple(engine.disasm(blob, start_va))

        for index, insn in enumerate(instructions):
            if (
                insn.mnemonic != "call"
                or len(insn.operands) != 1
                or insn.operands[0].type != X86_OP_IMM
                or (int(insn.operands[0].imm) & 0xFFFFFFFF) != target_va
            ):
                continue

            context_start = max(0, index - context_instructions)
            context_end = min(len(instructions), index + 2)
            output.append(
                {
                    "callsite_va": int(insn.address),
                    "target_va": target_va,
                    "section": section.name,
                    "bounded_linear_context": tuple(
                        _instruction_record(item)
                        for item in instructions[context_start:context_end]
                    ),
                    "nearby_push_operands_not_argument_proof": (
                        _nearby_push_candidates(
                            instructions,
                            index,
                            context_instructions=context_instructions,
                            immediate_type=X86_OP_IMM,
                            register_type=X86_OP_REG,
                        )
                    ),
                    "classification": (
                        "decoded_direct_audiohooks_call_candidate_not_cfg_or_semantic_proof"
                    ),
                }
            )
            if len(output) >= max_candidates:
                return tuple(output)

    return tuple(output)


def audiohooks_caller_trace_report(
    pe: OriginalPE32,
    *,
    context_instructions: int = 8,
    max_candidates: int = 512,
) -> dict:
    """Package neutral direct-caller candidates for private adjudication."""
    candidates = direct_audiohooks_call_candidates(
        pe,
        context_instructions=context_instructions,
        max_candidates=max_candidates,
    )
    return {
        "source_sha256": pe.sha256,
        "dispatcher_va": AUDIO_HOOKS_DISPATCH_VA,
        "candidate_count": len(candidates),
        "direct_call_candidates_not_cfg_proof": candidates,
        "direct_caller_cfg_recovered": False,
        "calling_convention_recovered": False,
        "event_argument_position_recovered": False,
        "state_argument_position_recovered": False,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "evidence_limit": (
            "Decoded direct CALL targets and bounded preceding PUSH operands only. "
            "Linear .text disassembly does not prove CFG reachability, function "
            "boundaries, calling convention, argument positions, event meanings, "
            "UI/match semantics, or sample meanings. Private manual source "
            "adjudication is required before any semantic binding is promoted."
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
    parser.add_argument("--context-instructions", type=int, default=8)
    parser.add_argument("--max-candidates", type=int, default=512)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = audiohooks_caller_trace_report(
        pe,
        context_instructions=args.context_instructions,
        max_candidates=args.max_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 AudioHooks caller trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
