"""Source-only native 42B0E0 selected user+65C options and x87 term inputs.

The returned terms are original x87 INPUTS, not a calculated floating return.
Actual 5EE9A0/5EEB10 and x87 FILD/FMUL/FADD are deliberately not run.
"""
from dataclasses import dataclass
from struct import pack, unpack_from

class Original42B0E0HumanModifierError(ValueError):
    pass

_OPTION_IDS = (1, 4, 6)
_WEIGHTS = (0.08, 0.04, 0.05)

@dataclass(frozen=True)
class SourceOriginal42B0E0Term:
    original_source_option_id: int
    original_5ee9a0_present: bool
    original_5eeb10_eax_if_present: int | None
    native_signed_increment_if_present: int | None
    original_source_qword_coefficient: bytes

@dataclass(frozen=True)
class SourceOriginal42B0E0HumanTermsReceipt:
    original_selected_user_pointer: int
    original_source_option_owner_65c_pointer: int
    original_literal_base_0p9_qword: bytes
    original_terms: tuple[SourceOriginal42B0E0Term,...]
    original_5ee9a0_executed: bool=False
    original_5eeb10_executed: bool=False
    original_x87_result_computed: bool=False
    live_game_state_updated: bool=False


def source_original_42b0e0_human_modifier_terms(
    *, original_selected_user_pointer: int,
    original_selected_user_record_at_entry: bytes,
    original_5ee9a0_presence_for_options_1_4_6: tuple[bool,bool,bool],
    original_5eeb10_eax_for_present_options_1_4_6: tuple[int|None,int|None,int|None],
) -> SourceOriginal42B0E0HumanTermsReceipt:
    ptr=original_selected_user_pointer
    raw=original_selected_user_record_at_entry
    flags=original_5ee9a0_presence_for_options_1_4_6
    vals=original_5eeb10_eax_for_present_options_1_4_6
    if type(ptr) is not int or not 0<ptr<=0xffffffff:
        raise Original42B0E0HumanModifierError('actual source selected original user pointer required')
    if type(raw) is not bytes or len(raw)<0x660:
        raise Original42B0E0HumanModifierError('reached selected user+65C record required')
    owner=unpack_from('<I',raw,0x65c)[0]
    if owner==0:
        raise Original42B0E0HumanModifierError('native 42B0E0 option owner+65C was null')
    if type(flags) is not tuple or len(flags)!=3 or any(type(x) is not bool for x in flags):
        raise Original42B0E0HumanModifierError('actual three native option predicate receipts required')
    if type(vals) is not tuple or len(vals)!=3:
        raise Original42B0E0HumanModifierError('actual native option values/absence required')
    terms=[]
    for option,weight,present,value in zip(_OPTION_IDS,_WEIGHTS,flags,vals):
        if present:
            if type(value) is not int or not 0<=value<=0xffffffff:
                raise Original42B0E0HumanModifierError('reached 5EEB10 EAX DWORD required')
            increased=(value+1)&0xffffffff
            signed=increased if increased<0x80000000 else increased-0x100000000
        else:
            if value is not None:
                raise Original42B0E0HumanModifierError('5EEB10 unreached but result supplied')
            signed=None
        terms.append(SourceOriginal42B0E0Term(option,present,value, signed,pack('<d',weight)))
    return SourceOriginal42B0E0HumanTermsReceipt(ptr,owner,pack('<d',0.9),tuple(terms))
