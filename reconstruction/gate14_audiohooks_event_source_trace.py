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

# Independently source-closed Button@ease_2001 RTTI/vtable path used by the
# dynamic 0x64F7xx AudioHooks sender family.
BUTTON_EASE_DECORATED_RTTI = ".?AVButton@ease_2001@@"
BUTTON_EASE_TYPE_DESCRIPTOR_VA = 0x81AD90
BUTTON_EASE_VTABLE_VA = 0x7BF4CC
BUTTON_EASE_SLOT0_EVENT_SELECTOR_VA = 0x6528A0
BUTTON_EASE_INPUT_VA = 0x64F7A0
BUTTON_EASE_EVENT_IDS = (2, 10)
BUTTON_EASE_EVENT_SELECTOR_OBJECT_FIELD = 0x34
BUTTON_EASE_EVENT_SELECTOR_WORD_FIELD = 0x4A
# Independently source-closed by GATE13_BUTTON_NATIVE_TRACE.md as the active
# Button@ease animation group index.
BUTTON_EASE_NATIVE_GROUP_FIELD = BUTTON_EASE_EVENT_SELECTOR_WORD_FIELD
BUTTON_EASE_NATIVE_GROUP_LENGTHS = (11, 11, 1)
BUTTON_EASE_DISABLED_GROUP = 2
BUTTON_EASE_EVENT_SELECTOR_VIRTUAL_OFFSET = 0xA8
BUTTON_EASE_EVENT_SELECTOR_VIRTUAL_TARGET_VA = 0x5D62F0

# Recovery 279: source-closed class/method context for the literal event-13
# sender at 0x47AD13. Both row classes share vtable slot 11 -> 0x47ACF0.
P_TITLE_MENU_ROW_DECORATED_RTTI = ".?AVPTitleMenuRow@@"
P_TITLE_MENU_ROW_TYPE_DESCRIPTOR_VA = 0x81CDB0
P_TITLE_MENU_ROW_VTABLE_VA = 0x7C3A80
P_CHILD_MENU_ROW_DECORATED_RTTI = ".?AVPChildMenuRow@@"
P_CHILD_MENU_ROW_TYPE_DESCRIPTOR_VA = 0x81CDF0
P_CHILD_MENU_ROW_VTABLE_VA = 0x7C3A20
MENU_ROW_EVENT13_VIRTUAL_SLOT_INDEX = 11
MENU_ROW_EVENT13_VIRTUAL_SLOT_OFFSET = 0x2C
MENU_ROW_EVENT13_METHOD_VA = 0x47ACF0
MENU_ROW_EVENT13_INCOMING_OBJECT_FIELD_OFFSET = 0x20
MENU_ROW_EVENT13_REQUIRED_FIELD_VALUE = 2
MENU_ROW_EVENT13_AUDIOHOOKS_TUPLE = (13, 0, 0)

# Recovery 279: source-closed PTeamOrders2K class context for the literal
# event-19 sender at 0x4D707F. Vtable slots 2 and 4 both reach helper 0x4D6FA0.
P_TEAM_ORDERS_2K_DECORATED_RTTI = ".?AVPTeamOrders2K@@"
P_TEAM_ORDERS_2K_TYPE_DESCRIPTOR_VA = 0x81DE68
P_TEAM_ORDERS_2K_VTABLE_VA = 0x7C6FE0
P_TEAM_ORDERS_2K_SLOT2_INDEX = 2
P_TEAM_ORDERS_2K_SLOT2_OFFSET = 0x08
P_TEAM_ORDERS_2K_SLOT2_METHOD_VA = 0x4D7600
P_TEAM_ORDERS_2K_SLOT4_INDEX = 4
P_TEAM_ORDERS_2K_SLOT4_OFFSET = 0x10
P_TEAM_ORDERS_2K_SLOT4_METHOD_VA = 0x4D6770
P_TEAM_ORDERS_2K_EVENT19_HELPER_VA = 0x4D6FA0
P_TEAM_ORDERS_2K_EVENT19_GUARD_HELPER_VA = 0x64E5B0
P_TEAM_ORDERS_2K_EVENT19_CALLSITE_VA = 0x4D707F
P_TEAM_ORDERS_2K_EVENT19_AUDIOHOOKS_TUPLE = (19, 0, 0)
P_TEAM_ORDERS_2K_EVENT19_HELPER_CALLSITES = (
    0x4D6F2D,
    0x4D6F61,
    0x4D6F91,
    0x4D7945,
)
P_TEAM_ORDERS_2K_EVENT19_INDEX_MIN = 0
P_TEAM_ORDERS_2K_EVENT19_INDEX_MAX = 9
P_TEAM_ORDERS_2K_EVENT19_SOURCE_BLOCK_OFFSET = 0x96C
P_TEAM_ORDERS_2K_EVENT19_SOURCE_BLOCK_STRIDE = 0x20
P_TEAM_ORDERS_2K_EVENT19_GUARD_OBJECT_OFFSET = 0xAD4

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

# Remaining non-control sender sites whose stack values are source-closed by
# local register/data-flow rather than three immediate PUSHes. Tuple fields:
# callsite, possible event ids, state arg2, third arg3, derivation class.
SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS = (
    (0x4B95F4, (1,), 1, 0, "arg3_zeroed_register"),
    (0x5EB69B, (23, 25), 0, 0, "event_two_value_branch"),
    (0x5EBA8A, (24, 26), 0, 0, "event_two_value_branch"),
    (0x5EBC7B, (32,), 0, 0, "state_and_arg3_zeroed_register"),
    (0x5EBE61, (32,), 0, 0, "state_and_arg3_zeroed_register"),
    (0x5EC02B, (31,), 0, 0, "state_and_arg3_zeroed_register"),
    (0x5ED5E5, (17, 18), 0, 0, "event_two_value_branch"),
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


def button_ease_audiohooks_event_id(
    object_field_34_non_null: bool,
    word_field_4a: int,
) -> int:
    """Reproduce Button@ease slot-0's source-closed numeric event selection.

    No semantic meaning is assigned to either object field or to event 2/10.
    """
    if type(object_field_34_non_null) is not bool:
        raise Gate14AudioHooksCallerTraceError(
            "Button +0x34 presence must be explicit boolean"
        )
    if type(word_field_4a) is not int or not 0 <= word_field_4a <= 0xFFFF:
        raise Gate14AudioHooksCallerTraceError(
            "Button +0x4A value must be uint16"
        )
    if not object_field_34_non_null:
        return 2
    return 2 if word_field_4a == 2 else 10


def menu_row_event13_should_send(
    incoming_object_non_null: bool,
    incoming_field_20: int,
) -> bool:
    """Mirror only 0x47ACF0's source-closed numeric send predicate.

    The incoming object's class/field meaning is deliberately unresolved. The
    method sends AudioHooks numeric tuple (13,0,0) only when the incoming
    object is non-null and its dword at +0x20 equals 2.
    """
    if type(incoming_object_non_null) is not bool:
        raise Gate14AudioHooksCallerTraceError(
            "incoming object presence must be explicit boolean"
        )
    if type(incoming_field_20) is not int or not 0 <= incoming_field_20 < 1 << 32:
        raise Gate14AudioHooksCallerTraceError(
            "incoming +0x20 value must be uint32"
        )
    return incoming_object_non_null and incoming_field_20 == 2


def pteamorders2k_event19_should_send(
    guard_helper_return_al: int,
    second_argument: int,
) -> bool:
    """Mirror only 0x4D6FA0's source-closed numeric event-19 predicate.

    Source closes the predicate, not the semantic meaning of helper 0x64E5B0,
    the second argument, or AudioHooks event 19.
    """
    if (
        type(guard_helper_return_al) is not int
        or not 0 <= guard_helper_return_al <= 0xFF
    ):
        raise Gate14AudioHooksCallerTraceError(
            "PTeamOrders2K guard helper return must be uint8"
        )
    if type(second_argument) is not int or not 0 <= second_argument < 1 << 32:
        raise Gate14AudioHooksCallerTraceError(
            "PTeamOrders2K second helper argument must be uint32"
        )
    return guard_helper_return_al == 0 and (second_argument & 0xFF) != 0


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
        "source_closed_dynamic_control_event_ids": BUTTON_EASE_EVENT_IDS,
        "source_closed_derived_virtual_senders": SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS,
        "menu_row_event13_source_contract": {
            "classes": (
                {
                    "decorated_rtti": P_TITLE_MENU_ROW_DECORATED_RTTI,
                    "type_descriptor_va": P_TITLE_MENU_ROW_TYPE_DESCRIPTOR_VA,
                    "vtable_va": P_TITLE_MENU_ROW_VTABLE_VA,
                },
                {
                    "decorated_rtti": P_CHILD_MENU_ROW_DECORATED_RTTI,
                    "type_descriptor_va": P_CHILD_MENU_ROW_TYPE_DESCRIPTOR_VA,
                    "vtable_va": P_CHILD_MENU_ROW_VTABLE_VA,
                },
            ),
            "shared_virtual_slot_index": MENU_ROW_EVENT13_VIRTUAL_SLOT_INDEX,
            "shared_virtual_slot_offset": MENU_ROW_EVENT13_VIRTUAL_SLOT_OFFSET,
            "shared_method_va": MENU_ROW_EVENT13_METHOD_VA,
            "incoming_object_field_offset": MENU_ROW_EVENT13_INCOMING_OBJECT_FIELD_OFFSET,
            "required_field_value": MENU_ROW_EVENT13_REQUIRED_FIELD_VALUE,
            "audiohooks_numeric_tuple": MENU_ROW_EVENT13_AUDIOHOOKS_TUPLE,
            "incoming_field_semantics_recovered": False,
            "event_semantics_recovered": False,
        },
        "pteamorders2k_event19_source_contract": {
            "decorated_rtti": P_TEAM_ORDERS_2K_DECORATED_RTTI,
            "type_descriptor_va": P_TEAM_ORDERS_2K_TYPE_DESCRIPTOR_VA,
            "vtable_va": P_TEAM_ORDERS_2K_VTABLE_VA,
            "vtable_paths": (
                {
                    "slot_index": P_TEAM_ORDERS_2K_SLOT2_INDEX,
                    "slot_offset": P_TEAM_ORDERS_2K_SLOT2_OFFSET,
                    "method_va": P_TEAM_ORDERS_2K_SLOT2_METHOD_VA,
                },
                {
                    "slot_index": P_TEAM_ORDERS_2K_SLOT4_INDEX,
                    "slot_offset": P_TEAM_ORDERS_2K_SLOT4_OFFSET,
                    "method_va": P_TEAM_ORDERS_2K_SLOT4_METHOD_VA,
                },
            ),
            "shared_helper_va": P_TEAM_ORDERS_2K_EVENT19_HELPER_VA,
            "helper_callsites": P_TEAM_ORDERS_2K_EVENT19_HELPER_CALLSITES,
            "guard_helper_va": P_TEAM_ORDERS_2K_EVENT19_GUARD_HELPER_VA,
            "audiohooks_callsite_va": P_TEAM_ORDERS_2K_EVENT19_CALLSITE_VA,
            "audiohooks_numeric_tuple": P_TEAM_ORDERS_2K_EVENT19_AUDIOHOOKS_TUPLE,
            "clamped_index_range": (
                P_TEAM_ORDERS_2K_EVENT19_INDEX_MIN,
                P_TEAM_ORDERS_2K_EVENT19_INDEX_MAX,
            ),
            "source_block_offset": P_TEAM_ORDERS_2K_EVENT19_SOURCE_BLOCK_OFFSET,
            "source_block_stride": P_TEAM_ORDERS_2K_EVENT19_SOURCE_BLOCK_STRIDE,
            "guard_object_offset": P_TEAM_ORDERS_2K_EVENT19_GUARD_OBJECT_OFFSET,
            "numeric_predicate": (
                "send only when 0x64E5B0 returns AL==0 and the original "
                "second helper argument has a nonzero low byte"
            ),
            "guard_helper_semantics_recovered": False,
            "second_argument_semantics_recovered": False,
            "event_semantics_recovered": False,
        },
        "button_ease_source_contract": {
            "decorated_rtti": BUTTON_EASE_DECORATED_RTTI,
            "type_descriptor_va": BUTTON_EASE_TYPE_DESCRIPTOR_VA,
            "vtable_va": BUTTON_EASE_VTABLE_VA,
            "slot0_event_selector_va": BUTTON_EASE_SLOT0_EVENT_SELECTOR_VA,
            "input_va": BUTTON_EASE_INPUT_VA,
            "event_ids": BUTTON_EASE_EVENT_IDS,
            "object_field_offset": BUTTON_EASE_EVENT_SELECTOR_OBJECT_FIELD,
            "word_field_offset": BUTTON_EASE_EVENT_SELECTOR_WORD_FIELD,
            "native_group_field_offset": BUTTON_EASE_NATIVE_GROUP_FIELD,
            "native_group_lengths": BUTTON_EASE_NATIVE_GROUP_LENGTHS,
            "disabled_group": BUTTON_EASE_DISABLED_GROUP,
            "native_group_semantics_recovered": True,
            "virtual_offset": BUTTON_EASE_EVENT_SELECTOR_VIRTUAL_OFFSET,
            "virtual_target_va": BUTTON_EASE_EVENT_SELECTOR_VIRTUAL_TARGET_VA,
            "numeric_rule": "event=2 if +0x34 is null or +0x4A==2; otherwise event=10",
            "event_semantics_recovered": False,
        },
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
            "convention, literal/derived numeric sender tuples, Button@ease "
            "dynamic-control event set {2,10}, the shared PTitleMenuRow/"
            "PChildMenuRow event-13 sender method, and the PTeamOrders2K event-19 "
            "numeric sender predicate are source-backed. Numeric event IDs "
            "are not human-readable "
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
