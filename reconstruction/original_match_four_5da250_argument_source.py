"""Read-only source receipt for four native 5DA250 actual call arguments.

Does not emulate original x87 calculation, callbacks, or GameState.
Stack bytes are independently reached before stage-specific argument PUSHes.
"""
from dataclasses import dataclass
from struct import unpack_from

class OriginalFourStage5DA250ArgumentError(ValueError):
    pass

# Stage: first PUSH site, 5DA250 CALL, human branch, user+694 stat offset.
_STAGE = {
    1: (0x5DAAE5, 0x5DAB07, 0x5DA9BA, 0xC),
    2: (0x5DAD62, 0x5DAD84, 0x5DAC4D, 0xC),
    3: (0x5DAFE1, 0x5DB003, 0x5DAECB, 0x8),
    4: (0x5DB25E, 0x5DB280, 0x5DB149, 0x8),
}

@dataclass(frozen=True)
class OriginalFourStage5DA250Arguments:
    source_stage: int
    source_first_push_site: int
    source_5da250_call_site: int
    source_human_branch_site: int
    native_first_qword_a: bytes
    native_second_qword_b: bytes
    original_human_club_gate: bool
    human_user_694_signed_dword_if_reached: int | None
    source_b_owner: str
    actual_original_x87_executed: bool = False
    live_game_state_updated: bool = False

def source_original_four_stage_5da250_arguments(
    *, source_stage: int,
    original_stage_stack_before_argument_pushes: bytes,
    original_4037b0_human_gate: bool,
    original_selected_user_694_record_if_human: bytes | None,
    original_5e48d0_stored_qword_if_directly_copied_to_b: bytes | None,
) -> OriginalFourStage5DA250Arguments:
    if type(source_stage) is not int or source_stage not in _STAGE:
        raise OriginalFourStage5DA250ArgumentError('actual original scored stage 1..4 required')
    s = original_stage_stack_before_argument_pushes
    if type(s) is not bytes or len(s) < 0x40:
        raise OriginalFourStage5DA250ArgumentError('native original stage ESP+0x30..+0x3F snapshot required')
    if type(original_4037b0_human_gate) is not bool:
        raise OriginalFourStage5DA250ArgumentError('actual source 4037B0 human test required')
    a, b = s[0x30:0x38], s[0x38:0x40]
    entry, call, gate, stat_offset = _STAGE[source_stage]
    human = original_4037b0_human_gate
    stat = None
    if human:
        user = original_selected_user_694_record_if_human
        if type(user) is not bytes or len(user) < stat_offset + 4:
            raise OriginalFourStage5DA250ArgumentError('reached native selected user+694 DWORD required')
        stat = unpack_from('<i', user, stat_offset)[0]
    else:
        if original_selected_user_694_record_if_human is not None:
            raise OriginalFourStage5DA250ArgumentError('unreached human user+694 record supplied')
        if a != b'\x00' * 8:
            raise OriginalFourStage5DA250ArgumentError('nonhuman branch directly writes zero to A')
    callback = original_5e48d0_stored_qword_if_directly_copied_to_b
    if source_stage == 1 or human:
        if type(callback) is not bytes or len(callback) != 8:
            raise OriginalFourStage5DA250ArgumentError('direct source B setter requires actual 5E48D0 QWORD')
        if b != callback:
            raise OriginalFourStage5DA250ArgumentError('B differs from original reached 5E48D0 FSTP')
        b_owner = 'stage-5e48d0-direct'
    else:
        if callback is not None:
            raise OriginalFourStage5DA250ArgumentError('nonhuman stage2-4 does not copy fresh callback into B')
        b_owner = 'stage-stack-retained-origin-unresolved'
    return OriginalFourStage5DA250Arguments(source_stage, entry, call, gate,
        a, b, human, stat, b_owner)
