"""Original 40CBC0 category 0x42 four sequential enum stages, QWORD outputs.

Original 40CBD4 dispatches team+14 type0x42 to 40CE09.
It then ALWAYS reaches 40CE83, 40CEDA, 40CF31 regardless of whether
a prior stage wrote output QWORDs. The four 4FA520 results are distinct
reached callbacks. Each stage may overwrite the pair; a final enum >4
preserves the LAST valid prior write, not a made-up default.
Source outputs initialized by original 5DA8D9 to QWORD zero.
No native callbacks/RNG/world state executed by this source projection.
"""
from dataclasses import dataclass
from struct import unpack_from


class OriginalMatch40CBC0Type42Error(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal40CBC0Type42Output:
    original_team_pointer: int
    original_source_team_key_pointer: int
    source_four_4fa520_enums: tuple[int,int,int,int]
    source_qwords_initial: tuple[float,float]
    first_original_qword_output: float
    second_original_qword_output: float
    original_last_write_stage: int | None
    original_4056d0_4fa520_callbacks_executed: bool = False
    original_native_40cbc0_executed: bool = False
    original_match_state_written: bool = False


def source_original_40cbc0_team_type42_output_pair(
    *,
    original_team_pointer:int,
    original_team_record:bytes,
    original_reached_4056d0_source_key_pointer:int,
    original_reached_four_4fa520_selector_dwords:tuple[int,int,int,int],
    original_preexisting_first_qword:float=0.0,
    original_preexisting_second_qword:float=0.0,
) -> SourceOriginal40CBC0Type42Output:
    if (type(original_team_pointer) is not int or
        not 0<original_team_pointer<=0xffffffff or
        type(original_team_record) is not bytes or len(original_team_record)<0x18 or
        type(original_reached_4056d0_source_key_pointer) is not int or
        not 0<original_reached_4056d0_source_key_pointer<=0xffffffff or
        unpack_from('<I',original_team_record,0x14)[0]!=0x42 or
        unpack_from('<I',original_team_record,0x10)[0]!=
            original_reached_4056d0_source_key_pointer):
        raise OriginalMatch40CBC0Type42Error("original 40CE09 type0x42 team/key ownership required")
    values=original_reached_four_4fa520_selector_dwords
    if (type(values) is not tuple or len(values)!=4 or
        any(type(x) is not int or not 0<=x<=0xffffffff for x in values)):
        raise OriginalMatch40CBC0Type42Error("four actually reached original 4FA520 full enum DWORDs required")
    for val in (original_preexisting_first_qword,original_preexisting_second_qword):
        if type(val) is not float or val!=0.0:
            raise OriginalMatch40CBC0Type42Error(
                "source 5DA8D9 initialized QWORD zero required; no invented previous outputs")
    a=b=0.0
    latest=None
    for stage,enum in enumerate(values):
        scalar=None
        if stage==0:
            scalar=(20.,16.,12.,9.,9.)[enum] if enum<=4 else None
        elif stage==1:
            scalar=(15.,10.)[enum] if enum<=1 else None
        elif stage==2:
            scalar=(17.,12.)[enum] if enum<=1 else None
        elif enum<=4:
            scalar=(30.,20.,16.,12.,9.)[enum]*0.5
        if scalar is not None:
            a=scalar
            b=scalar*0.75
            latest=stage
    return SourceOriginal40CBC0Type42Output(
        original_team_pointer,original_reached_4056d0_source_key_pointer,
        values,(0.,0.),a,b,latest)
