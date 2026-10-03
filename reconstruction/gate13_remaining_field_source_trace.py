"""Checksum-gated candidate scanner for unresolved Gate-13 club/setup fields.

This utility does not recover semantics by itself. It linearly disassembles only
file-backed .text from the canonical executable and records x86 memory operands
whose displacement exactly matches one of the still-open native fields:

- DBRClub +0x130 legacy attendance-counter state;
- DBRClub +0x13C / +0x140 visiting-capacity fields;
- participant/kit +0x76 secondary/loan-shirt selector.

A displacement hit is only a candidate instruction. Register provenance,
object type, read/write direction, control-flow reachability, and lifecycle
meaning still require private manual CFG/data-flow adjudication before any
runtime behavior may be promoted.

Private reports containing original instruction bytes must remain outside Git.
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


REMAINING_GATE13_FIELDS = (
    ("DBRClub legacy attendance-counter candidate", 0x130),
    ("DBRClub visiting-capacity candidate A", 0x13C),
    ("DBRClub visiting-capacity candidate B", 0x140),
    ("secondary/loan shirt selector candidate", 0x76),
)


class Gate13RemainingFieldTraceError(OriginalPETraceError):
    pass


def linear_memory_displacement_candidates(
    pe: OriginalPE32,
    *,
    fields: tuple[tuple[str, int], ...] = REMAINING_GATE13_FIELDS,
    max_candidates: int = 512,
) -> tuple[dict, ...]:
    """Return candidate x86 memory operands matching exact field displacements."""
    if type(max_candidates) is not int or max_candidates < 1:
        raise Gate13RemainingFieldTraceError("max_candidates must be positive")

    by_disp: dict[int, list[str]] = {}
    for label, displacement in fields:
        if (
            not isinstance(label, str)
            or not label
            or type(displacement) is not int
            or not 0 <= displacement < 2**31
        ):
            raise Gate13RemainingFieldTraceError(
                "field seeds require nonempty labels and nonnegative int32 displacements"
            )
        by_disp.setdefault(displacement, []).append(label)

    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86 import X86_OP_MEM
    except ImportError as exc:
        raise Gate13RemainingFieldTraceError(
            'Field candidate scan requires pip install "capstone>=5,<6"'
        ) from exc

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    found: list[dict] = []

    for section in pe.sections:
        if section.name != ".text":
            continue
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        section_va = pe.image_base + section.virtual_address

        for insn in engine.disasm(blob, section_va):
            for operand_index, operand in enumerate(insn.operands):
                if operand.type != X86_OP_MEM:
                    continue
                disp = int(operand.mem.disp)
                if disp not in by_disp:
                    continue
                found.append(
                    {
                        "candidate_instruction_va": int(insn.address),
                        "candidate_operand_index": int(operand_index),
                        "candidate_displacement": disp,
                        "candidate_field_labels": tuple(by_disp[disp]),
                        "candidate_mnemonic": insn.mnemonic,
                        "candidate_operands": insn.op_str,
                        "candidate_bytes": bytes(insn.bytes).hex(),
                        "base_register": (
                            insn.reg_name(operand.mem.base)
                            if operand.mem.base
                            else None
                        ),
                        "index_register": (
                            insn.reg_name(operand.mem.index)
                            if operand.mem.index
                            else None
                        ),
                        "scale": int(operand.mem.scale),
                        "section": section.name,
                        "classification": (
                            "linear_disassembly_only_unconfirmed_memory_operand"
                        ),
                    }
                )
                if len(found) >= max_candidates:
                    return tuple(found)
    return tuple(found)


def remaining_field_trace_report(
    pe: OriginalPE32,
    *,
    fields: tuple[tuple[str, int], ...] = REMAINING_GATE13_FIELDS,
    max_candidates: int = 512,
) -> dict:
    candidates = linear_memory_displacement_candidates(
        pe,
        fields=fields,
        max_candidates=max_candidates,
    )
    counts = {
        f"0x{displacement:X}": sum(
            1
            for item in candidates
            if item["candidate_displacement"] == displacement
        )
        for _, displacement in fields
    }
    return {
        "source_sha256": pe.sha256,
        "requested_field_displacements": [
            {"label": label, "displacement": displacement}
            for label, displacement in fields
        ],
        "candidate_count": len(candidates),
        "candidate_counts_by_displacement": counts,
        "candidate_memory_operands_not_proven_field_accesses": candidates,
        "source_semantics_recovered": False,
        "gate13_closed": False,
        "evidence_limit": (
            "Linear x86 decode plus exact memory-displacement equality only. "
            "A hit does not prove DBRClub/participant object type, read versus "
            "write direction, reachable control flow, initialization, capacity "
            "semantics, shirt semantics, or lifecycle ownership. Manual private "
            "CFG/data-flow review against the canonical executable is required."
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
    parser.add_argument("--max-candidates", type=int, default=512)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = remaining_field_trace_report(
        pe,
        max_candidates=args.max_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-13 remaining-field trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
