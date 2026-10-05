"""Private checksum-gated trace for Gate-17 fresh-objective RNG ownership.

The fresh chairman-objective branch table is already source-closed. Deterministic
non-PL branches can be materialized, while RNG-bearing branches remain blocked
because the exact shared MSVC CRT state at the 0x5DF670 objective-setup event is
not yet connected.

This tracer gathers bounded canonical executable windows and neutral direct-CALL
candidates around the setup/generator/shared-CRT seam. It does not infer caller
chronology, entry RNG state, or RNG-bearing objective outcomes.
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


class Gate17ObjectiveRngCallerTraceError(OriginalPETraceError):
    pass


DBRUSER_CONSTRUCTOR_VA = 0x425680
OBJECTIVE_SETUP_VA = 0x5DF670
FRESH_OBJECTIVE_GENERATOR_VA = 0x5DFD30
SHARED_CRT_BOUNDED_RNG_VA = 0x64D540
HIERARCHY_CLASS_HELPER_VA = 0x4FA520
FIRST_CLASS_HELPER_VA = 0x4FA570
LAST_CLASS_EQUAL_HELPER_VA = 0x4FA590
PROMOTION_PLAYOFF_STATUS_HELPER_VA = 0x4F88C0

OBJECTIVE_RNG_BOUND = 100
OBJECTIVE_RNG_LOWER_BRANCH_MAX = 50
OBJECTIVE_SETUP_SLOT_COUNT = 3

OBJECTIVE_RNG_TRACE_WINDOWS = (
    ("DBRUser fresh constructor", DBRUSER_CONSTRUCTOR_VA, 0x240),
    ("chairman objective setup", OBJECTIVE_SETUP_VA, 0x300),
    ("fresh objective candidate generator", FRESH_OBJECTIVE_GENERATOR_VA, 0x500),
    ("shared CRT bounded RNG", SHARED_CRT_BOUNDED_RNG_VA, 0x100),
    ("hierarchy class helper", HIERARCHY_CLASS_HELPER_VA, 0x100),
    ("first class helper", FIRST_CLASS_HELPER_VA, 0x80),
    ("last class equality helper", LAST_CLASS_EQUAL_HELPER_VA, 0x80),
    ("promotion playoff status helper", PROMOTION_PLAYOFF_STATUS_HELPER_VA, 0x300),
)

OBJECTIVE_RNG_DIRECT_CALL_TARGETS = (
    ("objective_setup", OBJECTIVE_SETUP_VA),
    ("fresh_objective_generator", FRESH_OBJECTIVE_GENERATOR_VA),
    ("shared_crt_bounded_rng", SHARED_CRT_BOUNDED_RNG_VA),
    ("hierarchy_class_helper", HIERARCHY_CLASS_HELPER_VA),
    ("first_class_helper", FIRST_CLASS_HELPER_VA),
    ("last_class_equal_helper", LAST_CLASS_EQUAL_HELPER_VA),
    ("promotion_playoff_status_helper", PROMOTION_PLAYOFF_STATUS_HELPER_VA),
)


def _validate_windows(windows) -> tuple[tuple[str, int, int], ...]:
    rows = tuple(windows)
    for item in rows:
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate17ObjectiveRngCallerTraceError(
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
            raise Gate17ObjectiveRngCallerTraceError(
                "invalid objective RNG source trace window"
            )
    return rows


def objective_rng_caller_trace_report(
    pe: OriginalPE32,
    *,
    windows=OBJECTIVE_RNG_TRACE_WINDOWS,
    call_targets=OBJECTIVE_RNG_DIRECT_CALL_TARGETS,
    max_matches: int = 512,
    with_disassembly: bool = False,
) -> dict:
    """Collect bounded caller evidence without inventing shared CRT state."""
    if type(with_disassembly) is not bool:
        raise Gate17ObjectiveRngCallerTraceError(
            "with_disassembly must be boolean"
        )
    if type(max_matches) is not int or not 1 <= max_matches <= 4096:
        raise Gate17ObjectiveRngCallerTraceError(
            "max_matches must be within 1..4096"
        )

    inspected = []
    for label, start_va, requested_size in _validate_windows(windows):
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate17ObjectiveRngCallerTraceError(
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
            raise Gate17ObjectiveRngCallerTraceError(
                "call targets must be (name, target_va)"
            )
        label, target_va = item
        if not isinstance(label, str) or not label or type(target_va) is not int:
            raise Gate17ObjectiveRngCallerTraceError(
                "invalid objective RNG direct-call target"
            )
        direct_call_candidates.append(
            {
                "target_name": label,
                "target_va": target_va,
                "decoded_direct_calls_not_objective_rng_semantic_proof": (
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
            "dbruser_constructor_va": DBRUSER_CONSTRUCTOR_VA,
            "objective_setup_va": OBJECTIVE_SETUP_VA,
            "fresh_objective_generator_va": FRESH_OBJECTIVE_GENERATOR_VA,
            "shared_crt_bounded_rng_va": SHARED_CRT_BOUNDED_RNG_VA,
            "hierarchy_class_helper_va": HIERARCHY_CLASS_HELPER_VA,
            "first_class_helper_va": FIRST_CLASS_HELPER_VA,
            "last_class_equal_helper_va": LAST_CLASS_EQUAL_HELPER_VA,
            "promotion_playoff_status_helper_va": PROMOTION_PLAYOFF_STATUS_HELPER_VA,
            "objective_rng_bound": OBJECTIVE_RNG_BOUND,
            "objective_rng_lower_branch_max_inclusive": (
                OBJECTIVE_RNG_LOWER_BRANCH_MAX
            ),
            "objective_setup_slot_count": OBJECTIVE_SETUP_SLOT_COUNT,
            "fresh_branch_table_recovered": True,
            "deterministic_non_pl_branches_materializable": True,
            "rng_bearing_branches_require_shared_crt_state": True,
        },
        "windows": tuple(inspected),
        "direct_call_candidates": tuple(direct_call_candidates),
        "objective_setup_callers_classified": False,
        "objective_setup_entry_crt_state_recovered": False,
        "rng_bearing_branch_draw_position_recovered": False,
        "fresh_objective_rng_replay_ready": False,
        "all_playable_scope_fresh_objectives_ready": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
        "evidence_limit": (
            "Bounded canonical source windows and decoded direct CALL candidates "
            "only. The fresh branch table, helper inputs, RNG(100) bound and inclusive "
            "<=50 split are already source-closed. Candidate callers do not prove the "
            "ordinary objective-setup owner chronology, exact shared CRT state on entry, "
            "RNG draw index within the process stream, all-scope objective readiness, "
            "full-scope readiness or Gate 17 completion."
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
    report = objective_rng_caller_trace_report(
        pe,
        max_matches=args.max_matches,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-17 objective RNG caller trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
