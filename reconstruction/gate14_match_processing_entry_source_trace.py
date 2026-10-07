"""Private checksum-gated caller trace for FM2001 match processing 0x513010.

Persisted first-hand source research proves that 0x513010 is the normal
match-processing router and that its later branch dispatches accepted Match
Detail modes to the native 3D/FastView/Quick Match presentation paths.

What remains unresolved is the ordinary management-side entry into that
routine. This read-only tracer intentionally does less than a decompiler or
CFG recovery: it linearly scans canonical .text for decoded direct CALL/JMP
candidates whose immediate target is 0x513010, then preserves a bounded source
window around each candidate for later manual control-flow adjudication.

A returned candidate is NOT proof of a real runtime edge, function ownership,
fixture/date semantics, management-panel ownership, pointer/control binding, or
a user-visible launch action. Linear disassembly can cross inline data or an
incorrect instruction boundary, and indirect/vtable callers are not searched.

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
from gate13_button_vtable_xref_candidates import linear_direct_branch_candidates


class Gate14MatchProcessingEntryTraceError(OriginalPETraceError):
    pass


MATCH_PROCESSING_ROUTER_VA = 0x513010
DEFAULT_CONTEXT_BEFORE = 0x30
DEFAULT_CONTEXT_AFTER = 0x60


def _bounded_context(
    pe: OriginalPE32,
    candidate_va: int,
    *,
    before: int,
    after: int,
) -> tuple[int, bytes]:
    if type(candidate_va) is not int:
        raise Gate14MatchProcessingEntryTraceError("candidate VA must be an integer")
    if type(before) is not int or type(after) is not int:
        raise Gate14MatchProcessingEntryTraceError("context sizes must be integers")
    if before < 0 or after <= 0 or before > 0x1000 or after > 0x1000:
        raise Gate14MatchProcessingEntryTraceError(
            "context sizes must stay within bounded 0x000..0x1000 / 0x001..0x1000"
        )

    section, delta = pe.section_for_va(candidate_va)
    if section.name != ".text":
        raise Gate14MatchProcessingEntryTraceError(
            "match-processing entry candidate must reside in .text"
        )
    section_start = pe.image_base + section.virtual_address
    start_va = max(section_start, candidate_va - before)
    start_delta = start_va - section_start
    desired_end_delta = min(
        section.file_backed_size,
        delta + after,
    )
    size = desired_end_delta - start_delta
    if size <= 0:
        raise Gate14MatchProcessingEntryTraceError(
            "bounded candidate context resolved to an empty window"
        )
    return start_va, pe.read(start_va, size)


def match_processing_entry_trace_report(
    pe: OriginalPE32,
    *,
    router_va: int = MATCH_PROCESSING_ROUTER_VA,
    context_before: int = DEFAULT_CONTEXT_BEFORE,
    context_after: int = DEFAULT_CONTEXT_AFTER,
    with_disassembly: bool = False,
    max_candidates: int = 128,
) -> dict:
    """Return direct-edge candidates only, preserving every unresolved boundary."""
    if type(router_va) is not int or not 0 <= router_va < 1 << 32:
        raise Gate14MatchProcessingEntryTraceError("router_va must be uint32")
    if type(with_disassembly) is not bool:
        raise Gate14MatchProcessingEntryTraceError("with_disassembly must be boolean")
    if type(max_candidates) is not int or isinstance(max_candidates, bool) or max_candidates < 1:
        raise Gate14MatchProcessingEntryTraceError("max_candidates must be positive")

    try:
        edges = linear_direct_branch_candidates(
            pe,
            targets=(("normal match-processing router", router_va),),
            max_candidates=max_candidates,
        )
    except OriginalPETraceError as exc:
        raise Gate14MatchProcessingEntryTraceError(str(exc)) from exc

    candidates = []
    for edge in edges:
        candidate_va = int(edge["candidate_instruction_va"])
        start_va, blob = _bounded_context(
            pe,
            candidate_va,
            before=context_before,
            after=context_after,
        )
        candidates.append(
            {
                "candidate_instruction_va": candidate_va,
                "candidate_target_va": int(edge["candidate_target_va"]),
                "candidate_mnemonic": edge["candidate_mnemonic"],
                "candidate_bytes": edge["candidate_bytes"],
                "context_start_va": start_va,
                "context_window_bytes": len(blob),
                "context_raw_hex": blob.hex(),
                "context_linear_disassembly_only": (
                    tuple(disassemble_window(blob, start_va))
                    if with_disassembly
                    else None
                ),
                "classification": (
                    "direct_linear_decode_candidate_not_runtime_or_management_entry_proof"
                ),
            }
        )

    return {
        "source_sha256": pe.sha256,
        "match_processing_router_va": router_va,
        "direct_candidate_count": len(candidates),
        "direct_candidates": tuple(candidates),
        "direct_candidate_scan_completed": True,
        "direct_callers_adjudicated": False,
        "indirect_or_vtable_callers_scanned": False,
        "management_owner_recovered": False,
        "fixture_start_condition_recovered": False,
        "management_ui_entry_trigger_recovered": False,
        "match_processing_entry_route_recovered": False,
        "gate14_complete": False,
        "evidence_limit": (
            "Canonical checksum-gated PE mapping plus linear direct CALL/JMP "
            "candidate discovery only. Candidate edges and bounded context require "
            "manual CFG/ownership adjudication. Indirect/vtable callers, native "
            "fixture/date conditions, management control ownership and the "
            "user-visible match-launch trigger remain unresolved."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument(
        "--context-before",
        type=lambda value: int(value, 0),
        default=DEFAULT_CONTEXT_BEFORE,
    )
    parser.add_argument(
        "--context-after",
        type=lambda value: int(value, 0),
        default=DEFAULT_CONTEXT_AFTER,
    )
    parser.add_argument("--max-candidates", type=int, default=128)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = match_processing_entry_trace_report(
        pe,
        context_before=args.context_before,
        context_after=args.context_after,
        with_disassembly=args.disassemble,
        max_candidates=args.max_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 match-processing entry trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
