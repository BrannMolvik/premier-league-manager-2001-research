"""Private source-recovery tracer for original Current Form row and radio mouse path.

No original game binaries/disassembly belong in Git.  This tool must be run
against the authorized canonical 32-bit original executable, using a private
output path outside the repository.  Bounded source windows and decoded direct
calls are *inspection leads*, not proof of row coordinates or a mouse event.
The separate Codex NEXT/match lifecycle is outside this tool's scope.
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


class CurrentFormInputTraceError(OriginalPETraceError):
    """Private PE trace source/argument contract could not be established."""


# Source-backed entry points, NOT automatically complete function boundaries.
# Source paper trail: GATE13_LEAGUE_TABLES_CURRENT_FORM_SOURCE_RECOVERY518,
# GATE13_LEAGUE_TABLES_RESOURCES, GATE13_FMRADIOTEXTSM_INPUT_RECOVERY515.
CURRENT_FORM_INPUT_WINDOWS = (
    ("native sort1 alternate row 0x2B0 constructor", 0x4480A0, 0x590),
    ("source row factory and source0/source1 allocation", 0x447E00, 0x120),
    ("source list row factory", 0x447820, 0x110),
    ("PLeagueTables radio event switch", 0x448C40, 0x160),
    ("text widget source geometry/font constructor", 0x6503F0, 0x110),
    ("base widget source half-open rectangle", 0x64F380, 0x40),
    ("native six-symbol widget style setter", 0x651F60, 0x80),
    ("native fmRadioTextSm dispatch", 0x5D4AC0, 0x90),
    ("source event broadcast child iteration", 0x5D4790, 0x80),
    ("source child event/owner register", 0x5D48C0, 0x60),
    ("pointer owner current cache", 0x64FB20, 0x70),
    ("pointer owner sibling cache", 0x64FB80, 0x70),
    ("source rectangle compare and child pointer callback", 0x64FBE0, 0xB0),
    ("source rectangle clipping child traversal", 0x5D4680, 0xB0),
    ("MyWindow message loop candidate", 0x532B80, 0xB0),
)

# Inspect the root-to-child mouse chain. Direct edges DO NOT prove root
# WM_LBUTTON ordering, child acceptability, capture/occlusion or event15.
DIRECT_CALL_TARGETS = (
    ("form_row_constructor", 0x4480A0),
    ("generic_widget_source_geometry", 0x6503F0),
    ("generic_widget_source_bounds", 0x64F380),
    ("current_form_result_widget_style", 0x651F60),
    ("radio_event_broadcast", 0x5D4790),
    ("radio_child_callback", 0x5D4AC0),
    ("pointer_cache_current", 0x64FB20),
    ("pointer_cache_sibling", 0x64FB80),
    ("pointer_radio_rectangle", 0x64FBE0),
    ("table_event_switch", 0x448C40),
)
GLOBAL_POINTER_LEADS = (
    ("source_mouse_current_owner", 0x984814),
    ("source_mouse_sibling_owner", 0x984818),
    ("fmRadioTextSm_vtable", 0x7D6AB8),
    ("PLeagueTables_vtable", 0x7C00C8),
    ("native_form_win_text_slot", 0x9830F0),
    ("native_form_draw_text_slot", 0x9830EC),
    ("native_form_loss_text_slot", 0x9830E8),
)

CLASSIFICATION = "decoded_direct_call_candidate_not_control_flow_or_mouse_proof"


def decoded_direct_caller_leads(
    pe: OriginalPE32,
    targets=DIRECT_CALL_TARGETS,
    *,
    max_matches: int = 256,
) -> tuple[dict, ...]:
    """Single-pass decoded direct-CALL leads; indirect vtable dispatch omitted."""
    if type(max_matches) is not int or not 1 <= max_matches <= 4096:
        raise CurrentFormInputTraceError("max_matches must be 1..4096")
    names = [name for name, _ in targets]
    if len(names) != len(set(names)):
        raise CurrentFormInputTraceError("duplicate direct-call target names")
    requested = {}
    for name, va in targets:
        if not isinstance(name, str) or not name or type(va) is not int or not 0 <= va < 2**32:
            raise CurrentFormInputTraceError("bad direct-call target")
        requested.setdefault(va, []).append(name)
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
        from capstone.x86_const import X86_OP_IMM
    except ImportError as exc:
        raise CurrentFormInputTraceError(
            'Capstone required for caller scan: install "capstone>=5,<6"'
        ) from exc
    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    matches = {name: [] for name in names}
    for section in pe.sections:
        if section.name != ".text":
            continue
        blob = pe.data[section.raw_offset:section.raw_offset + section.file_backed_size]
        base = pe.image_base + section.virtual_address
        for insn in engine.disasm(blob, base):
            if (insn.mnemonic != "call"
                    or len(insn.operands) != 1
                    or insn.operands[0].type != X86_OP_IMM):
                continue
            target = int(insn.operands[0].imm) & 0xFFFFFFFF
            for label in requested.get(target, ()):
                if len(matches[label]) >= max_matches:
                    continue
                matches[label].append({
                    "callsite_va": int(insn.address),
                    "target_va": target,
                    "section": section.name,
                    "classification": CLASSIFICATION,
                })
    return tuple({
        "target_name": name,
        "target_va": va,
        "candidate_calls_not_mouse_or_widget_semantics": tuple(matches[name]),
    } for name, va in targets)


def current_form_input_source_report(
    pe: OriginalPE32,
    *,
    windows=CURRENT_FORM_INPUT_WINDOWS,
    globals_to_find=GLOBAL_POINTER_LEADS,
    call_targets=DIRECT_CALL_TARGETS,
    max_matches: int = 256,
    with_disassembly: bool = False,
    scan_direct_calls: bool = False,
) -> dict:
    """Collect hash-pinned private windows/call leads with NO capability promotion."""
    if type(with_disassembly) is not bool or type(scan_direct_calls) is not bool:
        raise CurrentFormInputTraceError("trace options must be boolean")
    if type(max_matches) is not int or not 1 <= max_matches <= 4096:
        raise CurrentFormInputTraceError("max_matches must be 1..4096")
    seen = set()
    inspected = []
    for item in windows:
        if not isinstance(item, tuple) or len(item) != 3:
            raise CurrentFormInputTraceError("source windows must be (label, VA, size)")
        label, va, size = item
        if (not isinstance(label, str) or not label or label in seen
                or type(va) is not int or type(size) is not int
                or size < 1 or size > 0x1000):
            raise CurrentFormInputTraceError("invalid or duplicate source window")
        seen.add(label)
        section, _ = pe.section_for_va(va)
        if section.name != ".text":
            raise CurrentFormInputTraceError("source window is not executable .text")
        blob = pe.bounded_window(va, size)
        inspected.append({
            "label": label, "start_va": va, "requested_size": size,
            "actual_window_bytes": len(blob), "section": section.name,
            "raw_hex": blob.hex(),
            "linear_disassembly_not_cfg": (
                tuple(disassemble_window(blob, va)) if with_disassembly else None
            ),
            "classification": "bounded_window_not_verified_function_boundaries",
        })

    pointer_leads = []
    seen = set()
    for name, va in globals_to_find:
        if (not isinstance(name, str) or not name or name in seen
                or type(va) is not int or not 0 <= va < 2**32):
            raise CurrentFormInputTraceError("invalid or duplicate global lead")
        seen.add(name)
        pointer_leads.append({
            "target_name": name, "target_va": va,
            "raw_occurrences_not_decoded_xrefs": pe.pointer_byte_candidates(
                va, max_matches=max_matches,
            ),
        })

    return {
        "source_sha256": pe.sha256,
        "original_contract": {
            "league_tables_sort_event_current_form": 15,
            "native_sort_current_form_state": 1,
            "alternate_form_row_constructor_va": 0x4480A0,
            "alternate_form_row_allocation_size": 0x2B0,
            "current_form_semantic_symbols": ("W", "D", "L", " "),
            "form_slot_count": 6,
            "source_only_before_this_trace": True,
        },
        "windows": tuple(inspected),
        "global_pointer_candidates": tuple(pointer_leads),
        "decoded_direct_call_candidates": (
            decoded_direct_caller_leads(pe, call_targets, max_matches=max_matches)
            if scan_direct_calls else None
        ),
        "six_widget_row_geometry_and_font_source_verified_by_this_trace": False,
        "root_wm_lbutton_to_radio_event15_source_verified_by_this_trace": False,
        "original_six_widget_rendering_integrated": False,
        "original_league_tables_mouse_input_integrated": False,
        "gate13_complete": False,
        "gate17_complete": False,
        "evidence_limit": (
            "Private hash-pinned bounded bytes, optional linear decode, raw "
            "global address occurrences and decoded direct CALLs only. An "
            "analyst must manually prove complete 0x4480A0 child constructors, "
            "parent origin, font/style/color, clip/scroll and event-source "
            "WM_LBUTTONDOWN/UP -> state/capture/occlusion -> broadcast -> "
            "fmRadioTextSm callback -> PLeagueTables event15. Raw rectangle "
            "matches do not authorize a click or original Current Form raster. "
            "No original executable is executed by this tool."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument("--scan-direct-calls", action="store_true")
    parser.add_argument("--max-matches", type=int, default=256)
    args = parser.parse_args()
    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    result = current_form_input_source_report(
        pe, max_matches=args.max_matches, with_disassembly=args.disassemble,
        scan_direct_calls=args.scan_direct_calls,
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Private League Current Form source leads saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
