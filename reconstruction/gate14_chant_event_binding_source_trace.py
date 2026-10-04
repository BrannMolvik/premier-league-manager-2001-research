"""Private candidate-only trace for direct callers of chant enqueue.

The chant runtime's pool selection and timing are source-closed through enqueue
routine 0x723360, but the match-event/owner path that chooses selector 0/1/2 is
still unresolved. This tool reuses the repository's Capstone direct-edge
scanner to find only direct CALL candidates targeting the proven enqueue entry.

Linear disassembly is not CFG proof. Returned caller addresses are inspection
leads only and must not be promoted to event semantics, selector meanings,
sample meanings, or audio readiness without manual canonical-source review.
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
from gate13_button_vtable_xref_candidates import linear_direct_branch_candidates
from gate14_chant_runtime_pool_selection import ENQUEUE_VA


class Gate14ChantEventBindingTraceError(OriginalPETraceError):
    pass


CALL_WINDOW_BEFORE = 0x60
CALL_WINDOW_AFTER = 0xA0


def chant_enqueue_call_candidates(
    pe: OriginalPE32,
    *,
    max_candidates: int = 128,
    include_private_windows: bool = True,
) -> tuple[dict, ...]:
    """Return unconfirmed direct CALL candidates to the chant enqueue routine."""
    if type(include_private_windows) is not bool:
        raise Gate14ChantEventBindingTraceError(
            "include_private_windows must be boolean"
        )
    raw = linear_direct_branch_candidates(
        pe,
        targets=(("chant enqueue", ENQUEUE_VA),),
        max_candidates=max_candidates,
    )
    output = []
    for candidate in raw:
        if candidate.get("candidate_mnemonic") != "call":
            continue
        record = {
            **candidate,
            "classification": (
                "linear_direct_call_candidate_to_chant_enqueue_not_cfg_or_event_proof"
            ),
            "private_context_start_va": None,
            "private_context_raw_hex": None,
        }
        if include_private_windows:
            call_va = int(candidate["candidate_instruction_va"])
            section, delta = pe.section_for_va(call_va)
            if section.name != ".text":
                raise Gate14ChantEventBindingTraceError(
                    "direct enqueue caller candidate must remain in .text"
                )
            before = min(CALL_WINDOW_BEFORE, delta)
            start_va = call_va - before
            raw_window = pe.bounded_window(
                start_va,
                CALL_WINDOW_BEFORE + CALL_WINDOW_AFTER,
            )
            record["private_context_start_va"] = start_va
            record["private_context_raw_hex"] = raw_window.hex()
        output.append(record)
    return tuple(output)


def chant_event_binding_trace_report(
    pe: OriginalPE32,
    *,
    max_candidates: int = 128,
    include_private_windows: bool = True,
) -> dict:
    callers = chant_enqueue_call_candidates(
        pe,
        max_candidates=max_candidates,
        include_private_windows=include_private_windows,
    )
    return {
        "source_sha256": pe.sha256,
        "chant_enqueue_va": ENQUEUE_VA,
        "direct_call_candidate_count": len(callers),
        "direct_call_candidates_not_cfg_proof": callers,
        "enqueue_runtime_recovered": True,
        "caller_cfg_recovered": False,
        "match_event_binding_recovered": False,
        "selector_event_meaning_recovered": False,
        "chant_meaning_recovered": False,
        "audio_ready": False,
        "evidence_limit": (
            "Direct CALL candidates to the source-qualified enqueue entry only. "
            "Linear decode and bounded caller bytes do not prove CFG reachability, "
            "owner class, event identity, selector meaning, chant semantics, or "
            "that a candidate executes during match presentation."
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
    parser.add_argument("--max-candidates", type=int, default=128)
    parser.add_argument("--no-context-windows", action="store_true")
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = chant_event_binding_trace_report(
        pe,
        max_candidates=args.max_candidates,
        include_private_windows=not args.no_context_windows,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 chant enqueue caller trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
