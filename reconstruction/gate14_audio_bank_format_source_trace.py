"""Private checksum-gated trace for FM2001 BNK loading/playback format.

Executable ownership is already source-backed for four core banks and their
playback paths. Actual modern playback remains blocked because the BNK sample
table/header/codec structure has not been source-closed.

This tool packages only the already-proven loader and playback neighborhoods for
private analysis. It does not infer a file signature, sample count, offsets,
codec, channels, sample rate, sample names, music semantics, or event mapping.
Generated executable bytes/disassembly must remain private.
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
from gate14_audio_bank_ownership import (
    ADVICE_PLAYBACK_VA,
    AUDIO_INIT_MENUS_GAME_VA,
    BANK_LOADER_VA,
    GENERIC_SFX_CALLBACK_VA,
    MAIN_AUDIO_BANK_INIT_VA,
    MENUS_PLAYBACK_VA,
    PLAYER_CALLS_LOADER_VA,
    ADVICE_LOADER_VA,
)


class Gate14AudioBankFormatTraceError(OriginalPETraceError):
    pass


BANK_FORMAT_TRACE_WINDOWS = (
    ("shared BNK loader", BANK_LOADER_VA, 0x180),
    ("menus/game bank initialization", AUDIO_INIT_MENUS_GAME_VA, 0x100),
    ("playercalls bank initialization", PLAYER_CALLS_LOADER_VA, 0xC0),
    ("Advice bank initialization", ADVICE_LOADER_VA, 0xC0),
    ("main audio-bank initialization", MAIN_AUDIO_BANK_INIT_VA, 0x180),
    ("menus bank playback helper", MENUS_PLAYBACK_VA, 0x100),
    ("generic runtime SFX callback", GENERIC_SFX_CALLBACK_VA, 0x140),
    ("Advice bank playback helper", ADVICE_PLAYBACK_VA, 0x90),
)


def classify_bnk_window_dataflow_candidates(
    pe: OriginalPE32,
    *,
    windows=None,
) -> tuple[dict, ...]:
    """Classify bounded loader/playback instructions without assigning format semantics.

    Each retained record is still only a linear-disassembly candidate. The
    classifier exposes direct CALL targets, immediate operands and memory
    operands so private manual analysis can focus on record-layout/file-I/O
    operations. It does not infer field meanings, sample-table ownership, codec,
    or control-flow reachability.
    """
    if windows is None:
        windows = BANK_FORMAT_TRACE_WINDOWS
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM, X86_OP_MEM
    except ImportError as exc:
        raise Gate14AudioBankFormatTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    output: list[dict] = []

    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14AudioBankFormatTraceError(
                "BNK trace windows must be (label, start_va, requested_size)"
            )
        label, start_va, requested_size = item
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate14AudioBankFormatTraceError("invalid BNK trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14AudioBankFormatTraceError(
                f"{label}: expected source-qualified code in .text"
            )
        raw = pe.bounded_window(start_va, requested_size)

        for insn in engine.disasm(raw, start_va):
            immediates: list[int] = []
            memory_operands: list[dict] = []
            for operand in insn.operands:
                if operand.type == X86_OP_IMM:
                    immediates.append(int(operand.imm) & 0xFFFFFFFF)
                elif operand.type == X86_OP_MEM:
                    memory_operands.append(
                        {
                            "base": (
                                insn.reg_name(operand.mem.base)
                                if operand.mem.base
                                else None
                            ),
                            "index": (
                                insn.reg_name(operand.mem.index)
                                if operand.mem.index
                                else None
                            ),
                            "scale": int(operand.mem.scale),
                            "displacement": int(operand.mem.disp),
                            "operand_size": int(operand.size),
                        }
                    )

            direct_call_target = None
            if (
                insn.mnemonic == "call"
                and len(insn.operands) == 1
                and insn.operands[0].type == X86_OP_IMM
            ):
                direct_call_target = int(insn.operands[0].imm) & 0xFFFFFFFF

            if not immediates and not memory_operands and direct_call_target is None:
                continue

            output.append(
                {
                    "window_label": label,
                    "instruction_va": int(insn.address),
                    "instruction_size": int(insn.size),
                    "bytes": bytes(insn.bytes).hex(),
                    "mnemonic": insn.mnemonic,
                    "operands": insn.op_str,
                    "direct_call_target_candidate": direct_call_target,
                    "immediate_candidates": tuple(immediates),
                    "memory_operand_candidates": tuple(memory_operands),
                    "classification": (
                        "bounded_linear_bnk_dataflow_candidate_not_cfg_or_format_proof"
                    ),
                }
            )

    return tuple(output)


def shared_bnk_memory_displacement_candidates(
    candidates: tuple[dict, ...],
    *,
    minimum_distinct_windows: int = 2,
) -> tuple[dict, ...]:
    """Group recurring bounded memory displacements across distinct trace windows.

    Repetition across loader/playback neighborhoods is useful triage evidence for
    a possible shared object/record field, but it is not object-identity or field-
    meaning proof. The grouping intentionally ignores stack/frame-pointer based
    operands because equal local-stack offsets across unrelated functions are not
    meaningful cross-window evidence.
    """
    if type(candidates) is not tuple:
        raise Gate14AudioBankFormatTraceError(
            "BNK dataflow candidates must be an exact tuple"
        )
    if (
        type(minimum_distinct_windows) is not int
        or minimum_distinct_windows < 2
    ):
        raise Gate14AudioBankFormatTraceError(
            "minimum_distinct_windows must be an integer >= 2"
        )

    grouped: dict[tuple[int, int], dict] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise Gate14AudioBankFormatTraceError(
                "BNK dataflow candidate must be a mapping"
            )
        label = candidate.get("window_label")
        instruction_va = candidate.get("instruction_va")
        memory_operands = candidate.get("memory_operand_candidates", ())
        if not isinstance(label, str) or not label or type(instruction_va) is not int:
            raise Gate14AudioBankFormatTraceError(
                "BNK dataflow candidate identity is malformed"
            )
        if type(memory_operands) not in (tuple, list):
            raise Gate14AudioBankFormatTraceError(
                "memory_operand_candidates must be a tuple/list"
            )

        for operand in memory_operands:
            if not isinstance(operand, dict):
                raise Gate14AudioBankFormatTraceError(
                    "memory operand candidate must be a mapping"
                )
            base = operand.get("base")
            displacement = operand.get("displacement")
            operand_size = operand.get("operand_size")
            if base in {"esp", "ebp"}:
                continue
            if type(displacement) is not int or type(operand_size) is not int:
                raise Gate14AudioBankFormatTraceError(
                    "memory operand displacement/size must be integers"
                )
            key = (displacement, operand_size)
            entry = grouped.setdefault(
                key,
                {
                    "displacement": displacement,
                    "operand_size": operand_size,
                    "window_labels": set(),
                    "base_registers": set(),
                    "instruction_vas": set(),
                },
            )
            entry["window_labels"].add(label)
            if isinstance(base, str) and base:
                entry["base_registers"].add(base)
            entry["instruction_vas"].add(instruction_va)

    output = []
    for (displacement, operand_size), entry in grouped.items():
        labels = tuple(sorted(entry["window_labels"]))
        if len(labels) < minimum_distinct_windows:
            continue
        output.append(
            {
                "displacement": displacement,
                "operand_size": operand_size,
                "distinct_window_count": len(labels),
                "window_labels": labels,
                "base_registers": tuple(sorted(entry["base_registers"])),
                "instruction_vas": tuple(sorted(entry["instruction_vas"])),
                "classification": (
                    "shared_bnk_memory_displacement_candidate_not_object_or_field_proof"
                ),
            }
        )

    return tuple(
        sorted(
            output,
            key=lambda item: (
                -item["distinct_window_count"],
                item["displacement"],
                item["operand_size"],
            ),
        )
    )


def audio_bank_format_trace_report(
    pe: OriginalPE32,
    *,
    windows=None,
    with_disassembly: bool = True,
    classify_dataflow_candidates: bool = False,
) -> dict:
    """Collect bounded BNK loader/playback evidence without format promotion."""
    if type(with_disassembly) is not bool:
        raise Gate14AudioBankFormatTraceError("with_disassembly must be boolean")
    if type(classify_dataflow_candidates) is not bool:
        raise Gate14AudioBankFormatTraceError(
            "classify_dataflow_candidates must be boolean"
        )
    if windows is None:
        windows = BANK_FORMAT_TRACE_WINDOWS

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14AudioBankFormatTraceError(
                "BNK trace windows must be (label, start_va, requested_size)"
            )
        label, start_va, requested_size = item
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate14AudioBankFormatTraceError("invalid BNK trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14AudioBankFormatTraceError(
                f"{label}: expected source-qualified code in .text"
            )
        raw = pe.bounded_window(start_va, requested_size)
        inspected.append(
            {
                "label": label,
                "start_va": start_va,
                "requested_size": requested_size,
                "actual_window_bytes": len(raw),
                "section": section.name,
                "raw_hex": raw.hex(),
                "linear_disassembly_only": (
                    tuple(disassemble_window(raw, start_va))
                    if with_disassembly
                    else None
                ),
                "classification": "bounded_bnk_loader_window_not_cfg_or_format_proof",
            }
        )

    return {
        "source_sha256": pe.sha256,
        "windows": tuple(inspected),
        "dataflow_candidates_classified": bool(classify_dataflow_candidates),
        "bounded_dataflow_candidates_not_format_proof": (
            classify_bnk_window_dataflow_candidates(pe, windows=windows)
            if classify_dataflow_candidates
            else ()
        ),
        "shared_memory_displacement_candidates_not_field_proof": (
            shared_bnk_memory_displacement_candidates(
                classify_bnk_window_dataflow_candidates(pe, windows=windows)
            )
            if classify_dataflow_candidates
            else ()
        ),
        "bank_loader_va": BANK_LOADER_VA,
        "bank_ownership_recovered": True,
        "playback_entrypoints_recovered": True,
        "bank_header_layout_recovered": False,
        "sample_table_layout_recovered": False,
        "sample_offsets_recovered": False,
        "sample_codec_recovered": False,
        "sample_rate_channels_recovered": False,
        "sample_names_recovered": False,
        "modern_sample_decode_ready": False,
        "bank_role_semantics_recovered": False,
        "event_binding_recovered": False,
        "evidence_limit": (
            "Bank ownership and selected playback entrypoints are source-backed. "
            "These bounded windows do not prove BNK field meanings; optional "
            "instruction/dataflow candidates also do not prove CFG reachability, "
            "sample table layout, codec parameters, exact sample semantics, or "
            "modern decode."
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
    parser.add_argument("--no-disassembly", action="store_true")
    parser.add_argument(
        "--classify-dataflow-candidates",
        action="store_true",
        help=(
            "Classify bounded direct-call, immediate and memory operands for "
            "manual format analysis; still not CFG or BNK-format proof"
        ),
    )
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = audio_bank_format_trace_report(
        pe,
        with_disassembly=not args.no_disassembly,
        classify_dataflow_candidates=args.classify_dataflow_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 BNK format trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
