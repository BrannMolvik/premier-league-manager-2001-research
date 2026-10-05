"""Private checksum-gated trace for Gate-17 sporting-objective progression.

The clean-room runtime already carries a bounded same-Premier-League objective
transition, but non-PL TeamSelect scopes remain fail-closed because the original
annual sporting-objective owner and broader promotion/relegation classification
routes have not been fully source-adjudicated.

This tracer gathers bounded canonical executable windows and decoded direct-CALL
candidates around source anchors already persisted in the repository. It does
not infer non-PL objective semantics, promotion/relegation classification,
annual owner chronology, or full-scope readiness.

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
from gate17_secondary_owner_source_trace import decoded_direct_call_candidates


class Gate17SportingObjectiveProgressionTraceError(OriginalPETraceError):
    pass


ANNUAL_COMPETITION_TRANSITION_VA = 0x4A8628
SPORTING_OBJECTIVE_PROGRESS_VA = 0x5E1C00
SPORTING_OBJECTIVE_BRANCH_VA = 0x5E0310
SPORTING_OBJECTIVE_CLASSIFICATION_COMPARE_VA = 0x5E07E4
ANNUAL_OBJECTIVE_EVALUATION_CALLER_VA = 0x426220
ANNUAL_OBJECTIVE_EVALUATION_VA = 0x5E1D90
DBRUSER_SACKING_REASON_SETTER_VA = 0x42C6C0

OBJECTIVE_PROGRESSION_GATE_OFFSET = 0x68
OBJECTIVE_PROGRESSION_STATE_OFFSET = 0x9C

SPORTING_OBJECTIVE_TRACE_WINDOWS = (
    (
        "annual competition transition",
        ANNUAL_COMPETITION_TRANSITION_VA,
        0x240,
    ),
    (
        "sporting objective progression",
        SPORTING_OBJECTIVE_PROGRESS_VA,
        0x340,
    ),
    (
        "sporting objective branch family",
        SPORTING_OBJECTIVE_BRANCH_VA,
        0x600,
    ),
    (
        "competition classification comparison",
        SPORTING_OBJECTIVE_CLASSIFICATION_COMPARE_VA,
        0x180,
    ),
    (
        "annual objective evaluation caller",
        ANNUAL_OBJECTIVE_EVALUATION_CALLER_VA,
        0x160,
    ),
    (
        "annual objective evaluation",
        ANNUAL_OBJECTIVE_EVALUATION_VA,
        0x260,
    ),
    (
        "DBRUser sacking reason setter",
        DBRUSER_SACKING_REASON_SETTER_VA,
        0x100,
    ),
)

SPORTING_OBJECTIVE_DIRECT_CALL_TARGETS = (
    ("sporting_objective_progression", SPORTING_OBJECTIVE_PROGRESS_VA),
    ("sporting_objective_branch", SPORTING_OBJECTIVE_BRANCH_VA),
    (
        "sporting_objective_classification_compare",
        SPORTING_OBJECTIVE_CLASSIFICATION_COMPARE_VA,
    ),
    ("annual_objective_evaluation", ANNUAL_OBJECTIVE_EVALUATION_VA),
    ("dbruser_sacking_reason_setter", DBRUSER_SACKING_REASON_SETTER_VA),
)


def _validate_windows(windows) -> tuple[tuple[str, int, int], ...]:
    rows = tuple(windows)
    for item in rows:
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate17SportingObjectiveProgressionTraceError(
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
            raise Gate17SportingObjectiveProgressionTraceError(
                "invalid sporting-objective source trace window"
            )
    return rows


def sporting_objective_progression_trace_report(
    pe: OriginalPE32,
    *,
    windows=SPORTING_OBJECTIVE_TRACE_WINDOWS,
    call_targets=SPORTING_OBJECTIVE_DIRECT_CALL_TARGETS,
    max_matches: int = 512,
    with_disassembly: bool = False,
) -> dict:
    """Collect neutral annual-progression evidence without widening semantics."""
    if type(with_disassembly) is not bool:
        raise Gate17SportingObjectiveProgressionTraceError(
            "with_disassembly must be boolean"
        )
    if type(max_matches) is not int or not 1 <= max_matches <= 4096:
        raise Gate17SportingObjectiveProgressionTraceError(
            "max_matches must be within 1..4096"
        )

    inspected = []
    for label, start_va, requested_size in _validate_windows(windows):
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate17SportingObjectiveProgressionTraceError(
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

    direct_call_candidates = []
    for item in tuple(call_targets):
        if not isinstance(item, tuple) or len(item) != 2:
            raise Gate17SportingObjectiveProgressionTraceError(
                "call targets must be (name, target_va)"
            )
        label, target_va = item
        if not isinstance(label, str) or not label or type(target_va) is not int:
            raise Gate17SportingObjectiveProgressionTraceError(
                "invalid sporting-objective direct-call target"
            )
        direct_call_candidates.append(
            {
                "target_name": label,
                "target_va": target_va,
                "decoded_direct_calls_not_sporting_progression_semantic_proof": (
                    decoded_direct_call_candidates(
                        pe,
                        target_va,
                        max_matches=max_matches,
                    )
                ),
            }
        )

    return {
        "source_sha256": pe.sha256,
        "source_contract": {
            "annual_competition_transition_va": ANNUAL_COMPETITION_TRANSITION_VA,
            "sporting_objective_progress_va": SPORTING_OBJECTIVE_PROGRESS_VA,
            "sporting_objective_branch_va": SPORTING_OBJECTIVE_BRANCH_VA,
            "sporting_objective_classification_compare_va": (
                SPORTING_OBJECTIVE_CLASSIFICATION_COMPARE_VA
            ),
            "annual_objective_evaluation_caller_va": (
                ANNUAL_OBJECTIVE_EVALUATION_CALLER_VA
            ),
            "annual_objective_evaluation_va": ANNUAL_OBJECTIVE_EVALUATION_VA,
            "dbruser_sacking_reason_setter_va": DBRUSER_SACKING_REASON_SETTER_VA,
            "objective_progression_gate_offset": OBJECTIVE_PROGRESSION_GATE_OFFSET,
            "objective_progression_state_offset": OBJECTIVE_PROGRESSION_STATE_OFFSET,
            "same_premier_league_slice_recovered": True,
            "annual_evaluation_year_gate_recovered": True,
        },
        "windows": tuple(inspected),
        "direct_call_candidates": tuple(direct_call_candidates),
        "annual_sporting_owner_chronology_recovered": False,
        "non_pl_objective_branch_table_recovered": False,
        "promotion_relegation_classification_semantics_recovered": False,
        "non_pl_progression_gate_update_recovered": False,
        "non_pl_sporting_objective_progression_ready": False,
        "all_playable_scope_sporting_progression_ready": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
        "evidence_limit": (
            "Bounded canonical source windows and decoded direct CALL candidates "
            "only. Repository evidence already closes the same-Premier-League "
            "sporting slice, the +0x68 progression gate, +0x9C progression state "
            "and the year-gated 0x5E1D90 evaluator. Candidate callers and bounded "
            "windows do not prove annual owner chronology, broader non-PL objective "
            "branches, promotion/relegation classification semantics, non-PL gate "
            "updates, all-scope sporting progression, full-scope readiness or "
            "Gate 17 completion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument("--max-matches", type=int, default=512)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = sporting_objective_progression_trace_report(
        pe,
        max_matches=args.max_matches,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-17 sporting-objective trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
