"""Bounded private FastView owner-constructor call candidate tracer.

Gate 14 already has one source-closed cross-component draw-order relation:
PossessionDiagram is registered before PossessionFigures text in the same
forward-traversed parent draw array. Remaining overlap groups need additional
owner/registration evidence, especially around FastViewTeam and score/table
families.

This tool does not infer those relations. It linearly decodes only a bounded
FastViewPanel owner neighborhood and records direct CALL candidates to a small
set of already source-qualified constructor targets. A matching direct call is
still not proof of a function boundary, CFG reachability, the receiver/parent
object, child registration, or draw order. Private manual adjudication is
required before gate14_fastview_draw_order.py may gain another relation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    require_private_output_path,
)
from gate14_fastview_team import FASTVIEW_TEAM_CONSTRUCTOR_VA


class Gate14FastViewOwnerOrderTraceError(OriginalPETraceError):
    pass


FASTVIEW_PANEL_CONSTRUCTOR_VA = 0x51F490
FASTVIEW_PANEL_SETUP_VA = 0x51FA70
FASTVIEW_TEAM_OWNER_CALLSITE_VA = 0x520E67

# Recovery 274's canonical private replay showed that the earlier 0x520900
# upper bound stopped before the FastViewTeam owner call. Keep this as a
# bounded setup-region inspection range rather than claiming exact CFG extent.
FASTVIEW_OWNER_NEIGHBORHOOD_START_VA = FASTVIEW_PANEL_SETUP_VA
FASTVIEW_OWNER_NEIGHBORHOOD_END_VA = 0x5211F9

PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
POSSESSION_DIAGRAM_CONSTRUCTOR_VA = 0x5227D0
POSSESSION_FIGURES_CONSTRUCTOR_VA = 0x51E7E0

# These five callsites are persisted source evidence and calibrate a private
# report. Recovery 274 added the FastViewTeam call after a checksum-gated
# canonical executable pass. They do not by themselves establish global z-order.
KNOWN_REFERENCE_CALLSITES = (
    ("top_bar_picture_control", 0x51FDA3, PICTURE_CONTROL_CONSTRUCTOR_VA),
    ("ticker_picture_control", 0x51FE31, PICTURE_CONTROL_CONSTRUCTOR_VA),
    ("possession_diagram", 0x5206CD, POSSESSION_DIAGRAM_CONSTRUCTOR_VA),
    ("possession_figures", 0x520802, POSSESSION_FIGURES_CONSTRUCTOR_VA),
    ("fastview_team", FASTVIEW_TEAM_OWNER_CALLSITE_VA, FASTVIEW_TEAM_CONSTRUCTOR_VA),
)

# Only source-qualified constructor targets.
OWNER_TARGETS = (
    ("picture_control", PICTURE_CONTROL_CONSTRUCTOR_VA),
    ("possession_diagram", POSSESSION_DIAGRAM_CONSTRUCTOR_VA),
    ("possession_figures", POSSESSION_FIGURES_CONSTRUCTOR_VA),
    ("fastview_team", FASTVIEW_TEAM_CONSTRUCTOR_VA),
)


@dataclass(frozen=True)
class FastViewOwnerCallCandidate:
    callsite_va: int
    target_name: str
    target_va: int
    section: str
    bounded_linear_context: tuple[dict, ...]
    classification: str = (
        "decoded_direct_owner_constructor_call_candidate_not_cfg_parent_or_draw_order_proof"
    )


def _load_capstone():
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM
    except ImportError as exc:
        raise Gate14FastViewOwnerOrderTraceError(
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


def fastview_owner_call_candidates(
    pe: OriginalPE32,
    *,
    start_va: int = FASTVIEW_OWNER_NEIGHBORHOOD_START_VA,
    end_va: int = FASTVIEW_OWNER_NEIGHBORHOOD_END_VA,
    context_instructions: int = 5,
    targets=OWNER_TARGETS,
) -> tuple[FastViewOwnerCallCandidate, ...]:
    """Find direct CALL candidates to known constructors in one bounded region."""
    if (
        type(start_va) is not int
        or type(end_va) is not int
        or not 0 <= start_va < end_va < 1 << 32
    ):
        raise Gate14FastViewOwnerOrderTraceError(
            "FastView owner trace bounds must be an increasing uint32 range"
        )
    if type(context_instructions) is not int or context_instructions < 1:
        raise Gate14FastViewOwnerOrderTraceError(
            "context_instructions must be a positive integer"
        )

    normalized_targets = {}
    for item in tuple(targets):
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not item[0]
            or type(item[1]) is not int
            or not 0 <= item[1] < 1 << 32
        ):
            raise Gate14FastViewOwnerOrderTraceError(
                "targets must be (non-empty name, uint32 VA) pairs"
            )
        name, va = item
        if va in normalized_targets:
            raise Gate14FastViewOwnerOrderTraceError(
                "constructor target VAs must be unique"
            )
        normalized_targets[va] = name

    section, _ = pe.section_for_va(start_va)
    end_section, _ = pe.section_for_va(end_va - 1)
    if section.name != ".text" or end_section.name != ".text":
        raise Gate14FastViewOwnerOrderTraceError(
            "FastView owner trace bounds must remain inside .text"
        )

    blob = pe.read(start_va, end_va - start_va)
    engine, X86_OP_IMM = _load_capstone()
    instructions = tuple(engine.disasm(blob, start_va))
    output = []

    for index, insn in enumerate(instructions):
        if (
            insn.mnemonic != "call"
            or len(insn.operands) != 1
            or insn.operands[0].type != X86_OP_IMM
        ):
            continue
        target_va = int(insn.operands[0].imm) & 0xFFFFFFFF
        target_name = normalized_targets.get(target_va)
        if target_name is None:
            continue
        context_start = max(0, index - context_instructions)
        context_end = min(len(instructions), index + 2)
        output.append(
            FastViewOwnerCallCandidate(
                callsite_va=int(insn.address),
                target_name=target_name,
                target_va=target_va,
                section=section.name,
                bounded_linear_context=tuple(
                    _instruction_record(item)
                    for item in instructions[context_start:context_end]
                ),
            )
        )

    return tuple(output)


def fastview_owner_order_trace_report(
    pe: OriginalPE32,
    *,
    start_va: int = FASTVIEW_OWNER_NEIGHBORHOOD_START_VA,
    end_va: int = FASTVIEW_OWNER_NEIGHBORHOOD_END_VA,
    context_instructions: int = 5,
) -> dict:
    """Package neutral constructor-call candidates for private adjudication."""
    candidates = fastview_owner_call_candidates(
        pe,
        start_va=start_va,
        end_va=end_va,
        context_instructions=context_instructions,
    )
    observed = {(item.callsite_va, item.target_va) for item in candidates}
    reference_rows = tuple(
        {
            "name": name,
            "callsite_va": callsite_va,
            "target_va": target_va,
            "decoded_in_this_report": (callsite_va, target_va) in observed,
            "status": "persisted_source_reference_only",
        }
        for name, callsite_va, target_va in KNOWN_REFERENCE_CALLSITES
    )
    fastview_team_owner_callsite_recovered = (
        FASTVIEW_TEAM_OWNER_CALLSITE_VA,
        FASTVIEW_TEAM_CONSTRUCTOR_VA,
    ) in observed
    return {
        "source_sha256": pe.sha256,
        "fastview_panel_constructor_va": FASTVIEW_PANEL_CONSTRUCTOR_VA,
        "fastview_panel_setup_va": FASTVIEW_PANEL_SETUP_VA,
        "bounded_owner_neighborhood": {
            "start_va": start_va,
            "end_va_exclusive": end_va,
            "classification": "bounded_linear_neighborhood_not_function_boundary",
        },
        "known_reference_callsites": reference_rows,
        "candidate_count": len(candidates),
        "direct_owner_constructor_call_candidates": tuple(
            {
                "callsite_va": item.callsite_va,
                "target_name": item.target_name,
                "target_va": item.target_va,
                "section": item.section,
                "bounded_linear_context": item.bounded_linear_context,
                "classification": item.classification,
            }
            for item in candidates
        ),
        "fastview_team_owner_callsite_recovered": (
            fastview_team_owner_callsite_recovered
        ),
        "same_parent_registration_recovered_for_new_pairs": False,
        "additional_pairwise_draw_order_recovered": False,
        "global_fastview_z_order_recovered": False,
        "cross_component_blend_rule_recovered": False,
        "complete_fastview_frame_recovered": False,
        "evidence_limit": (
            "Decoded direct CALL candidates inside a bounded FastView owner "
            "setup region only. The exact 0x520E67 -> 0x524920 FastViewTeam "
            "call may be source-recovered without proving CFG-wide reachability, "
            "constructor parent registration, "
            "child registration into the FastViewPanel draw array, ordering "
            "across nested component arrays, pixel blend behavior, or any new "
            "pairwise/global z-order relation."
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
    parser.add_argument("--context-instructions", type=int, default=5)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = fastview_owner_order_trace_report(
        pe,
        context_instructions=args.context_instructions,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 FastView owner-order trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
