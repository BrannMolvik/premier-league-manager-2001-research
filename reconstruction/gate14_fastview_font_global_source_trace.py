"""Read-only, hash-gated leads for the unresolved FastView TextControl fonts.

A raw little-endian pointer occurrence is NOT an instruction-aligned xref,
write, initializer, pointed font object, or resolved .fnt filename. This tool
preserves bounded original-source bytes for private manual adjudication only.
Never commit its private output or any original executable/disc bytes.
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


class Gate14FontGlobalTraceError(OriginalPETraceError):
    pass


# Source-verified dispatcher 0x527BA0 (Recovery 406).
# Indices 1 and 3 already have separate verified font-loader traces.
FONT_WRAPPER_TARGETS = (
    (0, 0x87BEA0),
    (1, 0x87BE90),
    (2, 0x87BE80),
    (3, 0x87BE30),
    (4, 0x87BDF0),
)

# Exact decoded direct TextControl call instruction VAs, not a claim that
# surrounding raw bytes form a complete instruction-aligned function.
OWNER_CALLSITES = (
    ("ScoreComposite text 1", 0x51A8C1),
    ("ScoreComposite text 2", 0x51A93C),
    ("ScoreComposite text 3", 0x51A9D2),
    ("ScoreComposite text 4", 0x51AA83),
    ("LeagueTable row", 0x51D8FB),
    ("LeagueTable heading", 0x51DDF3),
)


def _bounded_private_context(pe: OriginalPE32, va: int, before: int, after: int) -> dict:
    section, offset = pe.section_for_va(va)
    first = max(0, offset - before)
    last = min(section.file_backed_size, offset + after)
    start_va = pe.image_base + section.virtual_address + first
    return {
        "start_va": start_va,
        "target_va": va,
        "end_va_exclusive": pe.image_base + section.virtual_address + last,
        "section": section.name,
        "raw_hex": pe.read(start_va, last - first).hex(),
        "classification": "bounded_unaligned_bytes_only_not_a_decoded_xref",
    }



def linear_font_wrapper_instruction_candidates(
    pe: OriginalPE32,
    *,
    targets=FONT_WRAPPER_TARGETS,
    max_candidates_per_target: int = 64,
) -> tuple[dict, ...]:
    """Opt-in decoded .text leads, never validated xrefs or initializer proof.

    Linear decoding from a section start may cross inline data or false
    instruction boundaries. Only literal immediates and register-free absolute
    memory operands are considered; indexed/register-relative displacements
    are not mistaken for addresses of global font wrappers.
    """
    if (
        type(max_candidates_per_target) is not int
        or not 1 <= max_candidates_per_target <= 1024
    ):
        raise Gate14FontGlobalTraceError("linear candidate limit must be 1..1024")
    targets = tuple(targets)
    by_address: dict[int, int] = {}
    seen_indices: set[int] = set()
    for index, address in targets:
        if type(index) is not int or not 0 <= index <= 4:
            raise Gate14FontGlobalTraceError("font selector index must be 0..4")
        if type(address) is not int or not 0 <= address < (1 << 32):
            raise Gate14FontGlobalTraceError("font wrapper address must be uint32")
        if index in seen_indices or address in by_address:
            raise Gate14FontGlobalTraceError("duplicate selector or wrapper address")
        seen_indices.add(index)
        by_address[address] = index

    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import (
            X86_OP_IMM,
            X86_OP_MEM,
            X86_REG_INVALID,
        )
    except ImportError as exc:
        raise Gate14FontGlobalTraceError(
            'Linear candidate scan requires pip install "capstone>=5,<6"'
        ) from exc

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    engine.skipdata = True
    collected = {index: [] for index, _ in targets}
    counts = {index: 0 for index, _ in targets}
    for section in pe.sections:
        if section.name != ".text":
            continue
        start = section.raw_offset
        blob = pe.data[start:start + section.file_backed_size]
        va = pe.image_base + section.virtual_address
        for insn in engine.disasm(blob, va):
            # Capstone skipdata records are not decoded x86 instructions.
            if insn.id == 0:
                continue
            matched: dict[int, str] = {}
            for operand in insn.operands:
                address = None
                kind = None
                if operand.type == X86_OP_IMM:
                    address = int(operand.imm) & 0xFFFFFFFF
                    kind = "literal_immediate"
                elif (
                    operand.type == X86_OP_MEM
                    and operand.mem.base == X86_REG_INVALID
                    and operand.mem.index == X86_REG_INVALID
                ):
                    address = int(operand.mem.disp) & 0xFFFFFFFF
                    kind = "register_free_absolute_memory"
                if address in by_address:
                    matched[by_address[address]] = kind
            for index, kind in matched.items():
                counts[index] += 1
                if counts[index] <= max_candidates_per_target:
                    collected[index].append({
                        "candidate_instruction_va": int(insn.address),
                        "candidate_mnemonic": insn.mnemonic,
                        "candidate_operands": insn.op_str,
                        "candidate_bytes": bytes(insn.bytes).hex(),
                        "operand_kind": kind,
                        "classification": (
                            "linear_decoded_candidate_not_verified_xref_or_write"
                        ),
                    })
    return tuple({
        "selector_index": index,
        "wrapper_target_va": address,
        "candidates": tuple(collected[index]),
        "candidate_limit_reached": counts[index] > max_candidates_per_target,
        "verified_xref_or_initializer": False,
    } for index, address in targets)


def font_global_candidate_report(
    pe: OriginalPE32,
    *,
    targets=FONT_WRAPPER_TARGETS,
    callsites=OWNER_CALLSITES,
    max_candidates_per_target: int = 64,
    context_radius: int = 40,
    scan_linear_wrapper_candidates: bool = False,
) -> dict:
    """Prepare private evidence leads; intentionally make no font/value claim."""
    if type(max_candidates_per_target) is not int or not 1 <= max_candidates_per_target <= 1024:
        raise Gate14FontGlobalTraceError("max_candidates_per_target must be 1..1024")
    if type(context_radius) is not int or not 0 <= context_radius <= 256:
        raise Gate14FontGlobalTraceError("context_radius must be 0..256")
    if type(scan_linear_wrapper_candidates) is not bool:
        raise Gate14FontGlobalTraceError("linear candidate scan switch must be boolean")

    targets = tuple(targets)
    callsites = tuple(callsites)
    if len({int(i) for i, _ in targets}) != len(targets):
        raise Gate14FontGlobalTraceError("duplicate font selector index")

    wrapper_records = []
    for index, address in targets:
        if type(index) is not int or not 0 <= index <= 4:
            raise Gate14FontGlobalTraceError("font selector index must be 0..4")
        if type(address) is not int or not 0 <= address < 1 << 32:
            raise Gate14FontGlobalTraceError("font wrapper address must be uint32")
        hits = pe.pointer_byte_candidates(
            address, max_matches=max_candidates_per_target + 1
        )
        truncated = len(hits) > max_candidates_per_target
        examples = []
        for item in hits[:max_candidates_per_target]:
            va = item["candidate_va"]
            evidence = _bounded_private_context(
                pe, va, context_radius, 4 + context_radius
            )
            examples.append({
                "candidate_va": va,
                "candidate_section": item["section"],
                "context": evidence,
                "classification": "raw_pointer_byte_occurrence_not_a_proven_reference",
            })
        wrapper_records.append({
            "selector_index": index,
            "wrapper_target_va": address,
            "candidates": tuple(examples),
            "candidate_limit_reached": truncated,
            "reference_or_initializer_proven": False,
            "font_file_identity_proven_by_this_trace": False,
        })

    caller_records = []
    for label, va in callsites:
        if not isinstance(label, str) or not label:
            raise Gate14FontGlobalTraceError("callsite label must be nonempty")
        if type(va) is not int or not 0 <= va < 1 << 32:
            raise Gate14FontGlobalTraceError("callsite VA must be uint32")
        section, _ = pe.section_for_va(va)
        if section.name != ".text":
            raise Gate14FontGlobalTraceError("callsite must be in original .text")
        caller_records.append({
            "owner": label,
            "source_known_callsite_va": va,
            "context": _bounded_private_context(pe, va, 96, 24),
            "arg4_text_producer_verified_by_this_trace": False,
            "owner_font_selector_value_verified_by_this_trace": False,
        })

    return {
        "source_sha256": pe.sha256,
        "dispatcher_source_va": 0x527BA0,
        "linear_font_wrapper_candidates_not_xrefs": (
            linear_font_wrapper_instruction_candidates(
                pe, targets=targets, max_candidates_per_target=max_candidates_per_target
            ) if scan_linear_wrapper_candidates else None
        ),
        "font_wrapper_raw_candidates": tuple(wrapper_records),
        "text_constructor_caller_contexts": tuple(caller_records),
        "league_table_selector_zero_from_prior_verified_disassembly": True,
        "selector_zero_font_object_and_filename_resolved": False,
        "score_owner_variable_selector_values_resolved": False,
        "league_table_text_producers_resolved": False,
        "new_source_font_pixels_rasterized": False,
        "gate13_complete": False,
        "gate14_complete": False,
        "evidence_limit": (
            "These are original PE raw-byte pointer candidates and bounded "
            "callsite neighborhoods, not aligned source xrefs, writes, "
            "initializer/object/dataflow evidence, user-visible values, "
            "font identities, raster pixels, or runtime acceptance."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-candidates-per-target", type=int, default=64)
    parser.add_argument("--context-radius", type=int, default=40)
    parser.add_argument("--scan-linear-wrapper-candidates", action="store_true")
    args = parser.parse_args()
    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = font_global_candidate_report(
        pe,
        max_candidates_per_target=args.max_candidates_per_target,
        context_radius=args.context_radius,
        scan_linear_wrapper_candidates=args.scan_linear_wrapper_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private FastView font-global candidate report saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
