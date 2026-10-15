"""Original 40CBC0 club-type 0x1A exact two QWORD match strength outputs.

Native original 40CBC0 computes a family-specific pair of QWORD outputs
before 5DA96C may consume one in the source match calculator.
Club type +0x14 == 0x1A dispatches original 40CBF2 then 4FA520
returned selector (0..4) through jump table 40CFF4. Output first:
30,20,16,12,9 as ORIGINAL global doubles; second=first*0.75.
This source ONLY covers type0x1A, not 0x18/1F/21/28/42/49 or
unknown classes. It does not execute native 4056D0/4056F0/4FA520,
world callbacks, RNG or GameState score writes.
"""
from dataclasses import dataclass
from struct import unpack_from


class OriginalMatch40CBC0SourceError(ValueError):
    pass


SOURCE_ORIGINAL_40CBC0_TYPE1A = 0x1A
SOURCE_ORIGINAL_40CBC0_ENTRY = 0x40CBF2
SOURCE_NATIVE_40CBC0_SUBSELECTOR_JUMP = (0x40CC24,0x40CC45,0x40CC66,0x40CC87,0x40CCA8)
SOURCE_NATIVE_40CBC0_BASE_DOUBLES = (30.0,20.0,16.0,12.0,9.0)
SOURCE_NATIVE_40CBC0_SECOND_RATIO = 0.75


@dataclass(frozen=True)
class SourceOriginal40CBC0Type1AOutput:
    original_team_pointer: int
    source_4056d0_lookup_key_pointer: int
    source_4fa520_selector_eax: int
    original_native_case_callsite: int
    first_original_qword_output: float
    second_original_qword_output: float
    original_4056d0_4fa520_callbacks_executed: bool = False
    original_native_40cbc0_executed: bool = False
    original_match_state_written: bool = False


def source_original_40cbc0_team_type1a_output_pair(
    *,
    original_team_pointer:int,
    original_team_record:bytes,
    original_reached_4056d0_source_key_pointer:int,
    original_reached_4fa520_selector_dword:int,
)->SourceOriginal40CBC0Type1AOutput:
    r=original_team_record
    ptr=original_team_pointer
    key=original_reached_4056d0_source_key_pointer
    val=original_reached_4fa520_selector_dword
    if (type(ptr) is not int or not 0<ptr<=0xffffffff
        or type(r) is not bytes or len(r)<0x18
        or type(key) is not int or not 0<key<=0xffffffff):
        raise OriginalMatch40CBC0SourceError("actual original team and 4056D0 key pointers required")
    if unpack_from("<I",r,0x14)[0]!=SOURCE_ORIGINAL_40CBC0_TYPE1A:
        raise OriginalMatch40CBC0SourceError("native 40CBF2 type0x1A branch NOT reached")
    if unpack_from("<I",r,0x10)[0]!=key:
        raise OriginalMatch40CBC0SourceError("original 40CBF2 +10 source lookup pointer mismatch")
    if type(val) is not int or not 0<=val<5:
        raise OriginalMatch40CBC0SourceError("native 4FA520 reached original enum0..4 required")
    primary=SOURCE_NATIVE_40CBC0_BASE_DOUBLES[val]
    return SourceOriginal40CBC0Type1AOutput(
        ptr,key,val,SOURCE_NATIVE_40CBC0_SUBSELECTOR_JUMP[val],
        primary,primary*SOURCE_NATIVE_40CBC0_SECOND_RATIO)
