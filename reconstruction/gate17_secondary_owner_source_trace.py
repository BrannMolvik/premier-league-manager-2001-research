"""Private checksum-gated source trace for Gate-17 secondary schedule ownership.

The repository already proves that League::0x4F3B70 selects the secondary
ScheduleContainer when DBRCompetition runtime +0x38 equals 2 or 3, that global
0x947AF0 is constructed with mode byte 1, and that new-game startup invokes
0x616620 on that container after primary 0x947AD8.

What is still missing for playable procedural-secondary TeamSelect scopes is
the live owner contract: ordinary runtime traversal, season continuation,
human-match dispatch and save/reload ownership. This read-only tracer gathers
bounded canonical executable windows, raw global-address occurrences and
decoded direct-CALL candidates around the already-proven schedule-container
seam. It deliberately does not promote any candidate into live semantics.

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


class Gate17SecondaryOwnerTraceError(OriginalPETraceError):
    pass


SCHEDULE_CONTAINER_SELECTOR_VA = 0x4F3B50
LEAGUE_SCHEDULE_MODE_SELECTOR_VA = 0x4F3B70
PRIMARY_SCHEDULE_CONTAINER_GLOBAL_VA = 0x947AD8
SECONDARY_SCHEDULE_CONTAINER_GLOBAL_VA = 0x947AF0
PRIMARY_CONTAINER_CONSTRUCTOR_VA = 0x615670
SECONDARY_CONTAINER_CONSTRUCTOR_VA = 0x6156C0
SCHEDULE_CONTAINER_BASE_CONSTRUCTOR_VA = 0x615700
SCHEDULE_CONTAINER_INSERT_VA = 0x615950
SCHEDULE_CONTAINER_FINAL_SHUFFLE_VA = 0x615BE0
SCHEDULE_CONTAINER_RUNTIME_TRAVERSAL_VA = 0x615C10
SCHEDULE_CONTAINER_BUILD_VA = 0x616620
SCHEDULE_CONTAINER_LATER_FINALIZATION_VA = 0x616A70
NEW_GAME_SCHEDULE_SETUP_VA = 0x4F7F08

SECONDARY_OWNER_TRACE_WINDOWS = (
    ("League schedule-container selector", SCHEDULE_CONTAINER_SELECTOR_VA, 0x80),
    ("ScheduleContainer global constructors", 0x615650, 0x140),
    ("ScheduleContainer insertion", SCHEDULE_CONTAINER_INSERT_VA, 0x240),
    ("ScheduleContainer final shuffle", SCHEDULE_CONTAINER_FINAL_SHUFFLE_VA, 0x80),
    ("ScheduleContainer runtime traversal candidate", SCHEDULE_CONTAINER_RUNTIME_TRAVERSAL_VA, 0x220),
    ("ScheduleContainer startup builder", SCHEDULE_CONTAINER_BUILD_VA, 0x300),
    ("ScheduleContainer later finalization candidate", SCHEDULE_CONTAINER_LATER_FINALIZATION_VA, 0x200),
    ("New-game primary/secondary setup", 0x4F7EE0, 0x80),
)

SECONDARY_OWNER_DIRECT_CALL_TARGETS = (
    ("schedule_container_selector", SCHEDULE_CONTAINER_SELECTOR_VA),
    ("schedule_container_insert", SCHEDULE_CONTAINER_INSERT_VA),
    ("schedule_container_final_shuffle", SCHEDULE_CONTAINER_FINAL_SHUFFLE_VA),
    ("schedule_container_runtime_traversal", SCHEDULE_CONTAINER_RUNTIME_TRAVERSAL_VA),
    ("schedule_container_build", SCHEDULE_CONTAINER_BUILD_VA),
    ("schedule_container_later_finalization", SCHEDULE_CONTAINER_LATER_FINALIZATION_VA),
)

SECONDARY_OWNER_GLOBAL_TARGETS = (
    ("primary_schedule_container_global", PRIMARY_SCHEDULE_CONTAINER_GLOBAL_VA),
    ("secondary_schedule_container_global", SECONDARY_SCHEDULE_CONTAINER_GLOBAL_VA),
)


def _load_capstone():
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM
    except ImportError as exc:
        raise Gate17SecondaryOwnerTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc
    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    return engine, X86_OP_IMM


def decoded_direct_call_candidates(
    pe: OriginalPE32,
    target_va: int,
    *,
    max_matches: int = 512,
) -> tuple[dict, ...]:
    """Return decoded direct CALL sites only; caller semantics remain unresolved."""
    if type(target_va) is not int or not 0 <= target_va < 1 << 32:
        raise Gate17SecondaryOwnerTraceError("target_va must be uint32")
    if type(max_matches) is not int or not 1 <= max_matches <= 4096:
        raise Gate17SecondaryOwnerTraceError("max_matches must be within 1..4096")

    engine, immediate_type = _load_capstone()
    rows = []
    for section in pe.sections:
        if section.name != ".text":
            continue
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        start_va = pe.image_base + section.virtual_address
        for insn in engine.disasm(blob, start_va):
            if (
                insn.mnemonic == "call"
                and len(insn.operands) == 1
                and insn.operands[0].type == immediate_type
                and (int(insn.operands[0].imm) & 0xFFFFFFFF) == target_va
            ):
                rows.append(
                    {
                        "callsite_va": int(insn.address),
                        "target_va": target_va,
                        "section": section.name,
                        "classification": (
                            "decoded_direct_call_candidate_not_lifecycle_semantic_proof"
                        ),
                    }
                )
                if len(rows) >= max_matches:
                    return tuple(rows)
    return tuple(rows)


def secondary_owner_trace_report(
    pe: OriginalPE32,
    *,
    windows=SECONDARY_OWNER_TRACE_WINDOWS,
    globals_to_find=SECONDARY_OWNER_GLOBAL_TARGETS,
    call_targets=SECONDARY_OWNER_DIRECT_CALL_TARGETS,
    max_matches: int = 512,
    with_disassembly: bool = False,
) -> dict:
    """Collect bounded evidence while keeping every missing runtime claim false."""
    if type(with_disassembly) is not bool:
        raise Gate17SecondaryOwnerTraceError("with_disassembly must be boolean")

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate17SecondaryOwnerTraceError(
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
            raise Gate17SecondaryOwnerTraceError("invalid secondary-owner trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate17SecondaryOwnerTraceError(
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
    for label, target_va in tuple(globals_to_find):
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

    call_candidates = []
    for label, target_va in tuple(call_targets):
        call_candidates.append(
            {
                "target_name": label,
                "target_va": target_va,
                "decoded_direct_calls_not_lifecycle_semantic_proof": (
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
        "selector_contract": {
            "selector_va": SCHEDULE_CONTAINER_SELECTOR_VA,
            "league_mode_selector_va": LEAGUE_SCHEDULE_MODE_SELECTOR_VA,
            "primary_global_va": PRIMARY_SCHEDULE_CONTAINER_GLOBAL_VA,
            "secondary_global_va": SECONDARY_SCHEDULE_CONTAINER_GLOBAL_VA,
            "secondary_mode_values": (2, 3),
            "secondary_container_mode_byte": 1,
            "source_contract_already_recovered": True,
        },
        "windows": tuple(inspected),
        "global_candidates": tuple(global_candidates),
        "direct_call_candidates": tuple(call_candidates),
        "secondary_startup_container_identity_recovered": True,
        "secondary_match_insertion_routing_recovered": True,
        "live_secondary_runtime_owner_recovered": False,
        "live_secondary_daily_execution_binding_recovered": False,
        "secondary_season_continuation_recovered": False,
        "secondary_human_match_dispatch_recovered": False,
        "secondary_save_serialization_recovered": False,
        "secondary_save_reload_continuation_recovered": False,
        "procedural_secondary_scope_playable": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
        "evidence_limit": (
            "Bounded canonical source windows, raw address occurrences and decoded "
            "direct CALL candidates only. Existing source research already proves "
            "the mode-2/3 selector, secondary global identity, startup builder and "
            "match insertion routing. Candidate references do not prove ordinary "
            "daily execution, season ownership, human dispatch, serialization, "
            "save/reload continuation, playable procedural-secondary scope, full "
            "original scope, external Windows evidence or Gate 17 completion."
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
    report = secondary_owner_trace_report(
        pe,
        max_matches=args.max_matches,
        with_disassembly=args.disassemble,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-17 secondary-owner source trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
