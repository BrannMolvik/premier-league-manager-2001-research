"""Bounded candidate-only native FM2001 Button@ease control-flow inspection.

The two seed vtable *addresses* and known code-entry addresses come from
prior canonical executable research. This tool uses file-backed PE mapping
to recover their raw slots, then optional Capstone LINEAR DECODE to locate
near direct branch byte candidates in .text. These are inspection leads,
never a reconstructed control-flow graph, verified xrefs, original hover
state transitions or proof of a Button@ease-specific vtable.

Original executable must be canonical hash-gated via OriginalPE32.parse.
Reports containing original instruction/pointer data remain private and
outside Git; no original source bytes are bundled for hosted tests.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct

from gate13_button_source_trace import OriginalPE32, OriginalPETraceError


# These are recovered first-screen CLASS vtables, NOT a claim that either
# is the shared Button@ease vtable or that particular slots have meanings.
SCREEN_VTABLE_SEEDS = (
    ("PStartMenu class vtable", 0x7C64E0),
    ("TeamSelect class vtable", 0x7C7650),
)

# These code-entry addresses were independently established before this tool.
SOURCE_CODE_SEEDS = (
    ("PStartMenu control setup", 0x4C1BA0),
    ("PStartMenu event dispatch", 0x4C3770),
    ("TeamSelect Back/Start setup", 0x4D885F),
    ("Button atlas initialization", 0x5F4500),
    ("Button@ease setup", 0x652FD0),
    ("Zurich bitmap font loader", 0x657650),
)


@dataclass(frozen=True)
class RawVTableCandidate:
    """Only sequential raw values at a previously evidenced vtable address."""
    seed: str
    seed_va: int
    entry_index: int
    entry_va: int
    value: int
    mapped_section: str | None
    plausible_text_pointer: bool


def screen_vtable_candidates(
    pe: OriginalPE32,
    *,
    seeds: tuple[tuple[str, int], ...] = SCREEN_VTABLE_SEEDS,
    entries_per_seed: int = 12,
) -> tuple[RawVTableCandidate, ...]:
    """Inspect a limited number of slots without guessing their function roles.

    Reading ceases on the same section's file-backed boundary. No adjacent
    unrelated virtual memory can be mistaken for continued vtable entries.
    """
    if type(entries_per_seed) is not int or not 1 <= entries_per_seed <= 64:
        raise OriginalPETraceError("Vtable inspection requires 1..64 slots")
    found = []
    for seed_label, seed_va in seeds:
        section, start_offset = pe.section_for_va(seed_va)
        if section.name == ".text":
            raise OriginalPETraceError(
                f"{seed_label}: original vtable seed unexpectedly maps to code"
            )
        remaining = min(
            entries_per_seed, (section.file_backed_size - start_offset) // 4
        )
        for i in range(remaining):
            entry_va = seed_va + i * 4
            raw_value = struct.unpack("<I", pe.read(entry_va, 4))[0]
            mapped = None
            try:
                target, _ = pe.section_for_va(raw_value)
                mapped = target.name
            except OriginalPETraceError:
                pass
            found.append(RawVTableCandidate(
                seed=seed_label,
                seed_va=seed_va,
                entry_index=i,
                entry_va=entry_va,
                value=raw_value,
                mapped_section=mapped,
                plausible_text_pointer=mapped == ".text",
            ))
    return tuple(found)


def linear_direct_branch_candidates(
    pe: OriginalPE32,
    *,
    targets: tuple[tuple[str, int], ...] = SOURCE_CODE_SEEDS,
    max_candidates: int = 128,
) -> tuple[dict, ...]:
    """Find candidate *direct* call/jump targets in linearly decoded PE code.

    Linear disassembly can cross inline data or wrong instruction boundaries.
    Every returned branch is explicitly UNCONFIRMED until CFG/manual review.
    Indirect register or vtable calls are intentionally excluded.
    """
    if type(max_candidates) is not int or max_candidates < 1:
        raise OriginalPETraceError("max_candidates must be positive")
    by_va: dict[int, list[str]] = {}
    for label, va in targets:
        if type(va) is not int or not 0 <= va < 2**32:
            raise OriginalPETraceError("Direct-branch seed must be uint32")
        by_va.setdefault(va, []).append(label)
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, CS_GRP_CALL, CS_GRP_JUMP, Cs
        from capstone.x86 import X86_OP_IMM
    except ImportError as exc:
        raise OriginalPETraceError(
            'Direct-branch candidates require pip install "capstone>=5,<6"'
        ) from exc

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    result = []
    for section in pe.sections:
        if section.name != ".text":
            continue
        start = section.raw_offset
        blob = pe.data[start:start + section.file_backed_size]
        section_va = pe.image_base + section.virtual_address
        for insn in engine.disasm(blob, section_va):
            if not (insn.group(CS_GRP_CALL) or insn.group(CS_GRP_JUMP)):
                continue
            if len(insn.operands) != 1 or insn.operands[0].type != X86_OP_IMM:
                continue
            target_va = insn.operands[0].imm & 0xFFFFFFFF
            if target_va not in by_va:
                continue
            result.append({
                "candidate_instruction_va": insn.address,
                "candidate_target_va": target_va,
                "candidate_target_labels": tuple(by_va[target_va]),
                "candidate_mnemonic": insn.mnemonic,
                "candidate_bytes": bytes(insn.bytes).hex(),
                "section": section.name,
                "classification": "linear_disassembly_only_unconfirmed_code_edge",
            })
            if len(result) >= max_candidates:
                return tuple(result)
    return tuple(result)


def extended_button_candidate_report(
    pe: OriginalPE32,
    *,
    vtable_seeds: tuple[tuple[str, int], ...] = SCREEN_VTABLE_SEEDS,
    code_seeds: tuple[tuple[str, int], ...] = SOURCE_CODE_SEEDS,
    entries_per_seed: int = 12,
    search_direct_branches: bool = False,
) -> dict:
    """Prepare one bounded private analysis aid with explicit evidentiary limits."""
    slots = screen_vtable_candidates(
        pe, seeds=vtable_seeds, entries_per_seed=entries_per_seed
    )
    plausible = [
        (f"{slot.seed} sequential slot {slot.entry_index} candidate", slot.value)
        for slot in slots if slot.plausible_text_pointer
    ]
    result = {
        "source_sha256": pe.sha256,
        "evidence_limit": (
            "Unconfirmed sequential class-vtable pointer candidates and "
            "optional linear-disassembly near direct-edge candidates only. "
            "Shared Button@ease vtable identity, native states, all indirect "
            "calls and Zurich glyph origins remain unverified."
        ),
        "seed_vtables": [
            {"seed": label, "seed_va": va}
            for label, va in vtable_seeds
        ],
        "raw_vtable_slots": [
            {
                "seed": item.seed,
                "entry_index": item.entry_index,
                "entry_va": item.entry_va,
                "value": item.value,
                "mapped_section": item.mapped_section,
                "plausible_text_pointer": item.plausible_text_pointer,
            }
            for item in slots
        ],
        "linear_direct_branch_candidates": None,
    }
    if search_direct_branches:
        result["linear_direct_branch_candidates"] = list(
            linear_direct_branch_candidates(
                pe, targets=tuple(code_seeds) + tuple(plausible)
            )
        )
    return result
