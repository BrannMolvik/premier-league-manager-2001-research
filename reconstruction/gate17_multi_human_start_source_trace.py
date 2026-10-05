"""Private checksum-gated trace for Gate-17 multi-human Start handoff.

Canonical TeamSelect research already proves that selecting clubs appends users,
Start consumes the existing global user list, each user retains its selected
club at +0x5B4, and the original hard global simultaneous-user cap is six.

This tracer gathers bounded canonical executable windows, raw occurrences of the
global user-count address, and decoded direct CALL candidates around the
Start/user-list continuation seam. It deliberately does not infer multi-human
runtime ordering, simultaneous human fixture dispatch, or save/reload behavior.

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


class Gate17MultiHumanStartTraceError(OriginalPETraceError):
    pass


TEAMSELECT_SELECTION_HANDLER_VA = 0x4D8E90
TEAMSELECT_START_EVENT_VA = 0x4DA480
TEAMSELECT_START_CONTINUATION_VA = 0x4C41C0
TEAMSELECT_SATURATION_VA = 0x4DA4D0

USER_LOOKUP_CURRENT_VA = 0x4139D0
USER_LOOKUP_INDEXED_VA = 0x413B10
USER_CREATE_APPEND_VA = 0x413BB0
USER_REMOVE_VA = 0x413B80
USER_REMOVE_FINAL_VA = 0x413DB0

GLOBAL_USER_COUNT_VA = 0x8755E4
USER_SELECTED_CLUB_POINTER_OFFSET = 0x5B4
ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS = 6

MULTI_HUMAN_TRACE_WINDOWS = (
    ("TeamSelect selection handler", TEAMSELECT_SELECTION_HANDLER_VA, 0x300),
    ("TeamSelect Start event", TEAMSELECT_START_EVENT_VA, 0x90),
    ("TeamSelect Start continuation", TEAMSELECT_START_CONTINUATION_VA, 0x300),
    ("TeamSelect saturation check", TEAMSELECT_SATURATION_VA, 0x90),
    ("User current resolver", USER_LOOKUP_CURRENT_VA, 0x100),
    ("User indexed resolver", USER_LOOKUP_INDEXED_VA, 0x100),
    ("User append/create", USER_CREATE_APPEND_VA, 0x180),
    ("User removal", USER_REMOVE_VA, 0x120),
)

MULTI_HUMAN_DIRECT_CALL_TARGETS = (
    ("teamselect_start_continuation", TEAMSELECT_START_CONTINUATION_VA),
    ("user_lookup_current", USER_LOOKUP_CURRENT_VA),
    ("user_lookup_indexed", USER_LOOKUP_INDEXED_VA),
    ("user_create_append", USER_CREATE_APPEND_VA),
    ("user_remove", USER_REMOVE_VA),
    ("user_remove_final", USER_REMOVE_FINAL_VA),
)

MULTI_HUMAN_GLOBAL_TARGETS = (
    ("global_user_count", GLOBAL_USER_COUNT_VA),
)


def _validate_windows(windows) -> tuple[tuple[str, int, int], ...]:
    rows = tuple(windows)
    for item in rows:
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate17MultiHumanStartTraceError(
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
            raise Gate17MultiHumanStartTraceError(
                "invalid multi-human source trace window"
            )
    return rows


def multi_human_start_trace_report(
    pe: OriginalPE32,
    *,
    windows=MULTI_HUMAN_TRACE_WINDOWS,
    globals_to_find=MULTI_HUMAN_GLOBAL_TARGETS,
    call_targets=MULTI_HUMAN_DIRECT_CALL_TARGETS,
    max_matches: int = 512,
    with_disassembly: bool = False,
) -> dict:
    """Collect bounded evidence without promoting multi-human runtime semantics."""
    if type(with_disassembly) is not bool:
        raise Gate17MultiHumanStartTraceError(
            "with_disassembly must be boolean"
        )
    if type(max_matches) is not int or not 1 <= max_matches <= 4096:
        raise Gate17MultiHumanStartTraceError(
            "max_matches must be within 1..4096"
        )

    inspected = []
    for label, start_va, requested_size in _validate_windows(windows):
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate17MultiHumanStartTraceError(
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

    global_candidates = []
    for item in tuple(globals_to_find):
        if not isinstance(item, tuple) or len(item) != 2:
            raise Gate17MultiHumanStartTraceError(
                "global targets must be (name, target_va)"
            )
        label, target_va = item
        if not isinstance(label, str) or not label or type(target_va) is not int:
            raise Gate17MultiHumanStartTraceError(
                "invalid multi-human global target"
            )
        global_candidates.append(
            {
                "target_name": label,
                "target_va": target_va,
                "byte_occurrences_not_proven_xrefs": pe.pointer_byte_candidates(
                    target_va,
                    max_matches=max_matches,
                ),
            }
        )

    direct_call_candidates = []
    for item in tuple(call_targets):
        if not isinstance(item, tuple) or len(item) != 2:
            raise Gate17MultiHumanStartTraceError(
                "call targets must be (name, target_va)"
            )
        label, target_va = item
        if not isinstance(label, str) or not label or type(target_va) is not int:
            raise Gate17MultiHumanStartTraceError(
                "invalid multi-human direct-call target"
            )
        direct_call_candidates.append(
            {
                "target_name": label,
                "target_va": target_va,
                "decoded_direct_calls_not_handoff_semantic_proof": (
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
            "teamselect_start_event_va": TEAMSELECT_START_EVENT_VA,
            "teamselect_start_continuation_va": TEAMSELECT_START_CONTINUATION_VA,
            "teamselect_saturation_va": TEAMSELECT_SATURATION_VA,
            "global_user_count_va": GLOBAL_USER_COUNT_VA,
            "user_selected_club_pointer_offset": USER_SELECTED_CLUB_POINTER_OFFSET,
            "source_proven_hard_user_cap": ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS,
            "selection_appends_users_recovered": True,
            "start_consumes_existing_user_list_recovered": True,
        },
        "windows": tuple(inspected),
        "global_candidates": tuple(global_candidates),
        "direct_call_candidates": tuple(direct_call_candidates),
        "ordered_multi_user_start_iteration_recovered": False,
        "shared_multi_human_runtime_owner_recovered": False,
        "simultaneous_human_fixture_dispatch_order_recovered": False,
        "multi_human_save_serialization_recovered": False,
        "multi_human_save_reload_continuation_recovered": False,
        "multi_human_gameplay_supported": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
        "evidence_limit": (
            "Bounded canonical source windows, raw address occurrences and decoded "
            "direct CALL candidates only. Existing source research proves user append, "
            "selected-club retention, Start consumption of the existing user list and "
            "the hard six-user cap. Candidate references do not prove ordered Start "
            "handoff across all users, shared runtime ownership, simultaneous human "
            "fixture ordering, multi-human serialization/reload, full-scope readiness "
            "or Gate 17 completion."
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
    report = multi_human_start_trace_report(
        pe,
        max_matches=args.max_matches,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-17 multi-human Start trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
