"""Private checksum-gated discovery of executable-embedded FM2001 .bnk strings.

This tool is intentionally an evidence collector, not an audio semantic mapper.
It accepts only the canonical original executable through OriginalPE32, finds
null-terminated printable ASCII strings whose suffix is .bnk, and records raw
little-endian pointer-byte occurrences to each string VA.

A raw pointer-byte occurrence is NOT a validated x86 reference, loader call,
bank role, sample mapping, menu-music binding, or match-event binding. Those
require later control-flow adjudication against the private original bytes.

No proprietary executable bytes or trace output belong in Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    require_private_output_path,
)


BNK_SUFFIX = b".bnk"
MAX_EMBEDDED_STRING_BYTES = 1024


class Gate14AudioBankTraceError(OriginalPETraceError):
    pass


def _printable_ascii(value: int) -> bool:
    return 0x20 <= value <= 0x7E


def embedded_bnk_string_candidates(
    pe: OriginalPE32,
    *,
    max_strings: int = 512,
    max_pointer_candidates: int = 256,
) -> tuple[dict, ...]:
    """Return neutral embedded .bnk string candidates and raw pointer hits."""
    if type(max_strings) is not int or max_strings < 1:
        raise Gate14AudioBankTraceError("max_strings must be positive")
    if type(max_pointer_candidates) is not int or max_pointer_candidates < 1:
        raise Gate14AudioBankTraceError("max_pointer_candidates must be positive")

    found: list[dict] = []
    needle = BNK_SUFFIX + b"\x00"
    for section in pe.sections:
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        lower = blob.lower()
        search_at = 0
        while True:
            suffix_at = lower.find(needle, search_at)
            if suffix_at < 0:
                break
            end = suffix_at + len(BNK_SUFFIX)
            start = suffix_at
            while (
                start > 0
                and end - (start - 1) <= MAX_EMBEDDED_STRING_BYTES
                and _printable_ascii(blob[start - 1])
            ):
                start -= 1

            raw = blob[start:end]
            if (
                raw
                and len(raw) <= MAX_EMBEDDED_STRING_BYTES
                and all(_printable_ascii(value) for value in raw)
                and raw.lower().endswith(BNK_SUFFIX)
            ):
                string_va = pe.image_base + section.virtual_address + start
                found.append(
                    {
                        "string_va": string_va,
                        "section": section.name,
                        "embedded_text": raw.decode("ascii"),
                        "classification": (
                            "embedded_null_terminated_ascii_bnk_candidate_only"
                        ),
                        "raw_pointer_byte_candidates_not_proven_xrefs": (
                            pe.pointer_byte_candidates(
                                string_va,
                                max_matches=max_pointer_candidates,
                            )
                        ),
                    }
                )
                if len(found) >= max_strings:
                    return tuple(found)
            search_at = suffix_at + len(needle)
    return tuple(found)


def decoded_text_operand_reference_candidates(
    pe: OriginalPE32,
    string_va: int,
    raw_pointer_candidates,
    *,
    max_instruction_bytes: int = 15,
) -> tuple[dict, ...]:
    """Narrow raw .text pointer hits to x86 operand-reference candidates.

    x86 is variable-length, so a raw four-byte pointer occurrence does not prove
    an instruction boundary. For each .text occurrence this helper tries every
    possible instruction start within the architectural 15-byte maximum and
    retains only decodes that:

    * fully contain the four exact pointer bytes;
    * expose an immediate or memory-displacement operand equal to string_va.

    These remain candidate references, not CFG/reachability/loader proof.
    """
    if type(string_va) is not int or not 0 <= string_va < 1 << 32:
        raise Gate14AudioBankTraceError("string_va must be uint32")
    if type(max_instruction_bytes) is not int or not 1 <= max_instruction_bytes <= 15:
        raise Gate14AudioBankTraceError(
            "max_instruction_bytes must be within x86 architectural limit 1..15"
        )
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM, X86_OP_MEM
    except ImportError as exc:
        raise Gate14AudioBankTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    needle = struct.pack("<I", string_va)
    found: list[dict] = []
    seen: set[tuple[int, str]] = set()

    for raw_candidate in tuple(raw_pointer_candidates):
        if not isinstance(raw_candidate, dict):
            raise Gate14AudioBankTraceError(
                "raw pointer candidate must be a mapping"
            )
        candidate_va = raw_candidate.get("candidate_va")
        section_name = raw_candidate.get("section")
        if type(candidate_va) is not int:
            raise Gate14AudioBankTraceError(
                "raw pointer candidate VA must be an integer"
            )
        if section_name != ".text":
            continue
        section, delta = pe.section_for_va(candidate_va)
        if section.name != ".text":
            continue

        max_back = min(max_instruction_bytes - 1, delta)
        for back in range(max_back + 1):
            start_va = candidate_va - back
            section_at_start, start_delta = pe.section_for_va(start_va)
            if section_at_start.name != ".text":
                continue
            available = section_at_start.file_backed_size - start_delta
            blob = pe.read(start_va, min(max_instruction_bytes, available))
            decoded = tuple(engine.disasm(blob, start_va, count=1))
            if len(decoded) != 1:
                continue
            insn = decoded[0]
            if insn.address != start_va:
                continue
            end_va = insn.address + insn.size
            if not (
                insn.address <= candidate_va
                and candidate_va + len(needle) <= end_va
            ):
                continue
            pointer_offset = candidate_va - insn.address
            if bytes(insn.bytes)[pointer_offset:pointer_offset + 4] != needle:
                continue

            kinds: list[str] = []
            for operand in insn.operands:
                if (
                    operand.type == X86_OP_IMM
                    and (int(operand.imm) & 0xFFFFFFFF) == string_va
                ):
                    kinds.append("immediate")
                elif (
                    operand.type == X86_OP_MEM
                    and (int(operand.mem.disp) & 0xFFFFFFFF) == string_va
                ):
                    kinds.append("memory_displacement")
            for kind in dict.fromkeys(kinds):
                key = (int(insn.address), kind)
                if key in seen:
                    continue
                seen.add(key)
                found.append(
                    {
                        "instruction_va": int(insn.address),
                        "instruction_size": int(insn.size),
                        "pointer_candidate_va": int(candidate_va),
                        "reference_kind": kind,
                        "bytes": bytes(insn.bytes).hex(),
                        "mnemonic": insn.mnemonic,
                        "operands": insn.op_str,
                        "classification": (
                            "decoded_text_operand_reference_candidate_not_cfg_proof"
                        ),
                    }
                )

    return tuple(
        sorted(
            found,
            key=lambda item: (
                item["instruction_va"],
                item["pointer_candidate_va"],
                item["reference_kind"],
            ),
        )
    )


def audio_bank_trace_report(
    pe: OriginalPE32,
    *,
    max_strings: int = 512,
    max_pointer_candidates: int = 256,
    classify_text_operands: bool = False,
) -> dict:
    candidates = embedded_bnk_string_candidates(
        pe,
        max_strings=max_strings,
        max_pointer_candidates=max_pointer_candidates,
    )
    if type(classify_text_operands) is not bool:
        raise Gate14AudioBankTraceError(
            "classify_text_operands must be boolean"
        )
    if classify_text_operands:
        candidates = tuple(
            {
                **candidate,
                "decoded_text_operand_candidates_not_cfg_proof": (
                    decoded_text_operand_reference_candidates(
                        pe,
                        int(candidate["string_va"]),
                        candidate[
                            "raw_pointer_byte_candidates_not_proven_xrefs"
                        ],
                    )
                ),
            }
            for candidate in candidates
        )
    return {
        "source_sha256": pe.sha256,
        "candidate_count": len(candidates),
        "embedded_bnk_candidates": candidates,
        "text_operand_candidates_classified": bool(classify_text_operands),
        "bank_semantics_recovered": False,
        "bank_event_bindings_recovered": False,
        "evidence_limit": (
            "Embedded null-terminated .bnk strings and raw pointer-byte "
            "occurrences only, optionally narrowed to decoded x86 operand "
            "reference candidates. Neither raw hits nor decoded candidates "
            "prove CFG reachability, loader calls, bank roles, sample indices, "
            "menu/login music, or match-event sound bindings."
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
    parser.add_argument("--max-strings", type=int, default=512)
    parser.add_argument("--max-pointer-candidates", type=int, default=256)
    parser.add_argument(
        "--classify-text-operands",
        action="store_true",
        help=(
            "Narrow raw .text pointer hits to decoded immediate/memory operand "
            "reference candidates; still not CFG or loader proof"
        ),
    )
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = audio_bank_trace_report(
        pe,
        max_strings=args.max_strings,
        max_pointer_candidates=args.max_pointer_candidates,
        classify_text_operands=args.classify_text_operands,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 audio-bank trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
