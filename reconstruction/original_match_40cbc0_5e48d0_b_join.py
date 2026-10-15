"""Read-only join: original 40CBC0 output QWORD -> four 5E48D0 stage callbacks.

Limited to reached finite source coefficients and actual 87AD88 zero/one.
No native execution, stage-gate inference, GameState or x87 generalization.
"""
from dataclasses import dataclass
from struct import pack, unpack
from original_native_40cbc0_all_paths import SourceOriginal40CBC0AllPathReceipt

class Original40CBC05E48D0JoinError(ValueError):
    pass

_FIRST_QWORD_COEFFICIENTS = frozenset(
    pack('<d', x) for x in (30.,25.,20.,17.,16.,15.,12.,10.,9.,8.,6.,4.5))
_ZERO_QWORD = b'\x00'*8
_ONE_QWORD = pack('<d',1.)
_INPUT_READ_SITES = (0x5DA987,0x5DAC1A,0x5DAE98,0x5DB116)
_CONSTRUCTOR_SITES = (0x5DA995,0x5DAC28,0x5DAEA6,0x5DB124)
_DIRECT_B_WRITE_SITES = (0x5DA9AD,0x5DAC57,0x5DAED5,0x5DB153)

@dataclass(frozen=True)
class OriginalScoredStageFreshCallbackSource:
    original_stage: int
    original_input_slot: str
    original_input_read_site: int
    original_5e43b0_construct_site: int
    original_coefficient_qword: bytes
    original_factor_before_constructor: bytes
    original_factor_after_constructor: bytes
    original_5e48d0_qword: bytes
    direct_native_b_store_site_if_reached: int|None
    original_human_gate: bool
    original_native_executed: bool=False
    game_state_updated: bool=False

def source_original_40cbc0_callback_to_stage_b(
    *, original_40cbc0_coefficients: SourceOriginal40CBC0AllPathReceipt,
    original_stage: int, original_scored_stage_entered: bool,
    original_4037b0_human_club: bool,
    original_87ad88_qword_before_constructor: bytes
) -> OriginalScoredStageFreshCallbackSource:
    """Proven *conditional* callback; nonhuman stage2–4 does NOT write B.

    Caller supplies independently established 40CBC0 output, stage entry
    and actual factor-memory state. Under input exactly 0 or 1, original
    6596A0 chooses 1 and 5E4410 FMUL 1 has exact binary finite result.
    """
    r=original_40cbc0_coefficients
    if type(r) is not SourceOriginal40CBC0AllPathReceipt:
        raise Original40CBC05E48D0JoinError('source-owned 40CBC0 receipt required')
    if type(original_stage) is not int or original_stage not in (1,2,3,4):
        raise Original40CBC05E48D0JoinError('original scored stage 1..4 required')
    if type(original_scored_stage_entered) is not bool or not original_scored_stage_entered:
        raise Original40CBC05E48D0JoinError('independently reached original stage required')
    if type(original_4037b0_human_club) is not bool:
        raise Original40CBC05E48D0JoinError('original human-club gate required')
    first,second=r.original_first_qword_after,r.original_second_qword_after
    if type(first) is not bytes or len(first)!=8 or type(second) is not bytes or len(second)!=8:
        raise Original40CBC05E48D0JoinError('native 40CBC0 output QWORDs required')
    if type(r.original_any_coefficient_written) is not bool:
        raise Original40CBC05E48D0JoinError('source 40CBC0 write flag required')
    if r.original_any_coefficient_written:
        if first not in _FIRST_QWORD_COEFFICIENTS or second!=pack('<d',unpack('<d',first)[0]*0.75):
            raise Original40CBC05E48D0JoinError('pair not in original exact 40CBC0 coefficient constants')
    elif first!=_ZERO_QWORD or second!=_ZERO_QWORD:
        raise Original40CBC05E48D0JoinError('original caller zero-initialized both output QWORDs')
    factor=original_87ad88_qword_before_constructor
    if type(factor) is not bytes or factor not in (_ZERO_QWORD,_ONE_QWORD):
        raise Original40CBC05E48D0JoinError('factor not proved zero or source-selected one')
    use_first=original_stage in (1,2)
    raw=first if use_first else second
    writes_b=original_stage==1 or original_4037b0_human_club
    return OriginalScoredStageFreshCallbackSource(
        original_stage, '40cbc0-ebp8-first' if use_first else '40cbc0-ebpc-second',
        _INPUT_READ_SITES[original_stage-1],_CONSTRUCTOR_SITES[original_stage-1],
        raw,factor,_ONE_QWORD,raw,
        _DIRECT_B_WRITE_SITES[original_stage-1] if writes_b else None,
        original_4037b0_human_club)
