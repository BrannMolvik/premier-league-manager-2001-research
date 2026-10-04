"""Private checksum-gated sender trace for FM2001 AudioHooks::0x5DBFC0.

The numeric AudioHooks switch and its literal menus.bnk slot routing are already
source-backed. Recovery 278 extends the sender boundary beyond direct CALLs:
the canonical implementation is installed as vtable slot 0 of a global
AudioHooks object, so ordinary senders load global 0x984810 and call that slot
indirectly.

This tool reports only source structure and numeric arguments. It does not name
events, UI actions, match actions, or audio samples.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    require_private_output_path,
)
from gate14_audiohooks_menu_dispatch import AUDIO_HOOKS_DISPATCH_VA


class Gate14AudioHooksCallerTraceError(OriginalPETraceError):
    pass


AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA = 0x984810
AUDIO_HOOKS_VTABLE_VA = 0x7D73EC
AUDIO_HOOKS_VTABLE_SLOT0_TARGET_VA = AUDIO_HOOKS_DISPATCH_VA
AUDIO_HOOKS_INSTALL_VTABLE_VA = 0x5DC2B6
AUDIO_HOOKS_INSTALL_GLOBAL_PTR_VA = 0x5DC2BC
AUDIO_HOOKS_ARGUMENT_BYTES = 0x0C
AUDIO_HOOKS_EVENT_STACK_OFFSET = 0x04
AUDIO_HOOKS_STATE_STACK_OFFSET = 0x08
AUDIO_HOOKS_THIRD_STACK_OFFSET = 0x0C

# Exact canonical callsites where all three AudioHooks stack operands are
# immediate literals immediately before the slot-0 indirect call.
# Tuple fields are: callsite, event arg1, state arg2, third arg3.
SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS = (
    (0x468720, 1, 1, 0),
    (0x468781, 1, 1, 0),
    (0x47AD13, 13, 0, 0),
    (0x4B6822, 1, 1, 0),
    (0x4B6868, 1, 1, 0),
    (0x4B9297, 1, 2, 0),
    (0x4B994F, 1, 1, 0),
    (0x4B9AC0, 1, 1, 0),
    (0x4D707F, 19, 0, 0),
    (0x5EC1BC, 11, 0, 0),
)

# These sender sites source the event dynamically from a preceding virtual
# control method. The two arguments retained below that result are exact:
# state arg2 is 0..8 and third arg3 is 0x40. State 8 has two distinct callsites.
SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS = (
    (0x64F7FE, 0, 0x40),
    (0x64F88B, 1, 0x40),
    (0x64F923, 2, 0x40),
    (0x64F9BE, 3, 0x40),
    (0x64FA4B, 4, 0x40),
    (0x64FAE3, 5, 0x40),
    (0x64FC31, 6, 0x40),
    (0x64FC91, 7, 0x40),
    (0x64FD1B, 8, 0x40),
    (0x64FD8B, 8, 0x40),
)


@dataclass(frozen=True)
class AudioHooksCallingConvention:
    event_stack_offset: int = AUDIO_HOOKS_EVENT_STACK_OFFSET
    state_stack_offset: int = AUDIO_HOOKS_STATE_STACK_OFFSET
    third_stack_offset: int = AUDIO_HOOKS_THIRD_STACK_OFFSET
    callee_pop_bytes: int = AUDIO_HOOKS_ARGUMENT_BYTES
    third_argument_read_by_dispatcher: bool = False
    semantic_event_binding_recovered: bool = False

    def __post_init__(self) -> None:
        if (
            self.event_stack_offset != 4
            or self.state_stack_offset != 8
            or self.third_stack_offset != 12
            or self.callee_pop_bytes != 12
        ):
            raise Gate14AudioHooksCallerTraceError(
                "AudioHooks calling convention must retain the source stack contract"
            )
        if self.third_argument_read_by_dispatcher:
            raise Gate14AudioHooksCallerTraceError(
                "0x5DBFC0 does not read its third stack argument"
            )
        if self.semantic_event_binding_recovered:
            raise Gate14AudioHooksCallerTraceError(
                "numeric sender recovery cannot promote event semantics"
            )


SOURCE_CALLING_CONVENTION = AudioHooksCallingConvention()


def _load_capstone():
    try:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_OP_REG
    except ImportError as exc:
        raise Gate14AudioHooksCallerTraceError(
            'Capstone missing: install locally with pip install "capstone>=5,<6"'
        ) from exc
    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    return engine, X86_OP_IMM, X86_OP_MEM, X86_OP_REG


def _instruction_record(insn) -> dict:
    return {
        "va": int(insn.address),
        "size": int(insn.size),
        "bytes": bytes(insn.bytes).hex(),
        "mnemonic": insn.mnemonic,
        "operands": insn.op_str,
    }


def _nearby_push_candidates(
    instructions,
    call_index: int,
    *,
    context_instructions: int,
    immediate_type: int,
    register_type: int,
) -> tuple[dict, ...]:
    start = max(0, call_index - context_instructions)
    preceding = instructions[start:call_index]
    output = []
    for distance, insn in enumerate(reversed(preceding), start=1):
        if insn.mnemonic != "push" or len(insn.operands) != 1:
            continue
        operand = insn.operands[0]
        row = {
            "instruction_va": int(insn.address),
            "distance_from_call_instructions": distance,
            "classification": (
                "nearby_push_operand_candidate_not_argument_or_semantic_proof"
            ),
        }
        if operand.type == immediate_type:
            row["operand_kind"] = "immediate"
            row["immediate_value"] = int(operand.imm) & 0xFFFFFFFF
        elif operand.type == register_type:
            row["operand_kind"] = "register"
            row["register_name"] = insn.reg_name(operand.reg)
        else:
            row["operand_kind"] = "other"
        output.append(row)
    return tuple(output)


def direct_audiohooks_call_candidates(
    pe: OriginalPE32,
    *,
    target_va: int = AUDIO_HOOKS_DISPATCH_VA,
    context_instructions: int = 8,
    max_candidates: int = 512,
) -> tuple[dict, ...]:
    """Retain the older direct-CALL scan as a negative/auxiliary evidence path."""
    if type(target_va) is not int or not 0 <= target_va < 1 << 32:
        raise Gate14AudioHooksCallerTraceError("target_va must be uint32")
    if type(context_instructions) is not int or context_instructions < 1:
        raise Gate14AudioHooksCallerTraceError(
            "context_instructions must be a positive integer"
        )
    if type(max_candidates) is not int or max_candidates < 1:
        raise Gate14AudioHooksCallerTraceError(
            "max_candidates must be a positive integer"
        )

    engine, X86_OP_IMM, _X86_OP_MEM, X86_OP_REG = _load_capstone()
    output = []
    for section in pe.sections:
        if section.name != ".text":
            continue
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        start_va = pe.image_base + section.virtual_address
        instructions = tuple(engine.disasm(blob, start_va))
        for index, insn in enumerate(instructions):
            if (
                insn.mnemonic != "call"
                or len(insn.operands) != 1
                or insn.operands[0].type != X86_OP_IMM
                or (int(insn.operands[0].imm) & 0xFFFFFFFF) != target_va
            ):
                continue
            context_start = max(0, index - context_instructions)
            context_end = min(len(instructions), index + 2)
            output.append(
                {
                    "callsite_va": int(insn.address),
                    "target_va": target_va,
                    "section": section.name,
                    "bounded_linear_context": tuple(
                        _instruction_record(item)
                        for item in instructions[context_start:context_end]
                    ),
                    "nearby_push_operands_not_argument_proof": (
                        _nearby_push_candidates(
                            instructions,
                            index,
                            context_instructions=context_instructions,
                            immediate_type=X86_OP_IMM,
                            register_type=X86_OP_REG,
                        )
                    ),
                    "classification": (
                        "decoded_direct_audiohooks_call_candidate_not_cfg_or_semantic_proof"
                    ),
                }
            )
            if len(output) >= max_candidates:
                return tuple(output)
    return tuple(output)


def _absolute_global_load(insn, *, global_va: int, mem_type: int, reg_type: int):
    """Return destination register id for MOV reg,[absolute global], else None."""
    if insn.mnemonic != "mov" or len(insn.operands) != 2:
        return None
    dst, src = insn.operands
    if dst.type != reg_type or src.type != mem_type:
        return None
    mem = src.mem
    if mem.base or mem.index or (int(mem.disp) & 0xFFFFFFFF) != global_va:
        return None
    return int(dst.reg)


def virtual_audiohooks_call_candidates(
    pe: OriginalPE32,
    *,
    global_va: int = AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA,
    context_instructions: int = 16,
    max_candidates: int = 512,
) -> tuple[dict, ...]:
    """Find global-object -> vtable slot-0 indirect sender candidates.

    This identifies the mechanical virtual-call shape only. It does not by
    itself promote CFG reachability or event semantics.
    """
    if type(global_va) is not int or not 0 <= global_va < 1 << 32:
        raise Gate14AudioHooksCallerTraceError("global_va must be uint32")
    if type(context_instructions) is not int or context_instructions < 3:
        raise Gate14AudioHooksCallerTraceError(
            "context_instructions must be at least three"
        )
    if type(max_candidates) is not int or max_candidates < 1:
        raise Gate14AudioHooksCallerTraceError(
            "max_candidates must be a positive integer"
        )

    engine, X86_OP_IMM, X86_OP_MEM, X86_OP_REG = _load_capstone()
    output = []
    for section in pe.sections:
        if section.name != ".text":
            continue
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        start_va = pe.image_base + section.virtual_address
        instructions = tuple(engine.disasm(blob, start_va))

        for index, insn in enumerate(instructions):
            object_reg = _absolute_global_load(
                insn,
                global_va=global_va,
                mem_type=X86_OP_MEM,
                reg_type=X86_OP_REG,
            )
            if object_reg is None:
                continue

            vtable_regs: set[int] = set()
            end = min(len(instructions), index + context_instructions + 1)
            for cursor in range(index + 1, end):
                item = instructions[cursor]
                if item.mnemonic == "mov" and len(item.operands) == 2:
                    dst, src = item.operands
                    if (
                        dst.type == X86_OP_REG
                        and src.type == X86_OP_MEM
                        and src.mem.base == object_reg
                        and not src.mem.index
                        and src.mem.disp == 0
                    ):
                        vtable_regs.add(int(dst.reg))

                if item.mnemonic != "call" or len(item.operands) != 1:
                    continue
                operand = item.operands[0]
                if (
                    operand.type != X86_OP_MEM
                    or int(operand.mem.base) not in vtable_regs
                    or operand.mem.index
                    or operand.mem.disp != 0
                ):
                    continue

                context_start = max(0, cursor - context_instructions)
                context_end = min(len(instructions), cursor + 2)
                output.append(
                    {
                        "global_load_va": int(insn.address),
                        "callsite_va": int(item.address),
                        "global_va": global_va,
                        "vtable_slot_byte_offset": 0,
                        "bounded_linear_context": tuple(
                            _instruction_record(row)
                            for row in instructions[context_start:context_end]
                        ),
                        "nearby_push_operands_not_argument_proof": (
                            _nearby_push_candidates(
                                instructions,
                                cursor,
                                context_instructions=context_instructions,
                                immediate_type=X86_OP_IMM,
                                register_type=X86_OP_REG,
                            )
                        ),
                        "classification": (
                            "decoded_global_audiohooks_slot0_call_candidate_not_cfg_or_semantic_proof"
                        ),
                    }
                )
                if len(output) >= max_candidates:
                    return tuple(output)
                break
    return tuple(output)


def audiohooks_caller_trace_report(
    pe: OriginalPE32,
    *,
    context_instructions: int = 16,
    max_candidates: int = 512,
) -> dict:
    direct = direct_audiohooks_call_candidates(
        pe,
        context_instructions=max(8, min(context_instructions, 64)),
        max_candidates=max_candidates,
    )
    virtual = virtual_audiohooks_call_candidates(
        pe,
        context_instructions=context_instructions,
        max_candidates=max_candidates,
    )
    return {
        "source_sha256": pe.sha256,
        "dispatcher_va": AUDIO_HOOKS_DISPATCH_VA,
        "audiohooks_global_object_ptr_va": AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA,
        "audiohooks_vtable_va": AUDIO_HOOKS_VTABLE_VA,
        "audiohooks_vtable_slot0_target_va": AUDIO_HOOKS_VTABLE_SLOT0_TARGET_VA,
        "audiohooks_install_vtable_va": AUDIO_HOOKS_INSTALL_VTABLE_VA,
        "audiohooks_install_global_ptr_va": AUDIO_HOOKS_INSTALL_GLOBAL_PTR_VA,
        "calling_convention": {
            "event_stack_offset": SOURCE_CALLING_CONVENTION.event_stack_offset,
            "state_stack_offset": SOURCE_CALLING_CONVENTION.state_stack_offset,
            "third_stack_offset": SOURCE_CALLING_CONVENTION.third_stack_offset,
            "callee_pop_bytes": SOURCE_CALLING_CONVENTION.callee_pop_bytes,
            "third_argument_read_by_dispatcher": (
                SOURCE_CALLING_CONVENTION.third_argument_read_by_dispatcher
            ),
        },
        "direct_candidate_count": len(direct),
        "direct_call_candidates_not_cfg_proof": direct,
        "virtual_candidate_count": len(virtual),
        "global_slot0_call_candidates_not_cfg_proof": virtual,
        "source_closed_literal_virtual_senders": SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS,
        "source_closed_dynamic_control_senders": SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS,
        "rtti_vtable_global_path_recovered": True,
        "calling_convention_recovered": True,
        "event_argument_position_recovered": True,
        "state_argument_position_recovered": True,
        "third_argument_position_recovered": True,
        "third_argument_unused_by_dispatcher_recovered": True,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "evidence_limit": (
            "The AudioHooks RTTI/vtable/global-object path, three-stack-argument "
            "convention, literal numeric sender tuples, and dynamic-control sender "
            "shape are source-backed. Numeric event IDs are not human-readable "
            "event names, computed event results are not guessed, and decoded "
            "audio is not sample-meaning evidence."
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
    parser.add_argument("--context-instructions", type=int, default=16)
    parser.add_argument("--max-candidates", type=int, default=512)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = audiohooks_caller_trace_report(
        pe,
        context_instructions=args.context_instructions,
        max_candidates=args.max_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 AudioHooks caller trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
