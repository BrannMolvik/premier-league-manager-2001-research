"""Native 5DA5D9 encounter owner selection and source tier constants.

After team input branch 5DA5CF, original accesses match-context+0x4C
and uses owner v+0x18; if false and owner+4 nonzero it selects the
alternate link, then calls v+18 again. The true path reads selected
owner+0x3C and subtracts native match-context v+0x60 return.
Four original world constants at 0x821088/8C/90 are 30,20,15; the
fallback is 15-1. These are INPUT tier integers, not final scores
or source-discovered RNG outputs. False v+0x18 routes to 5DA746.
"""
from dataclasses import dataclass
from struct import unpack_from


class OriginalMatchEncounterSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal5DA5D9Encounter:
    initial_encounter_pointer: int
    selected_encounter_pointer: int
    source_fallback_plus4_selected: bool
    original_selected_v18_alive: bool
    source_next_branch_va: int
    original_source_tier_constant: int | None
    source_level_difference: int | None
    native_original_callbacks_executed: bool = False
    source_fpu_ratios_executed: bool = False
    game_state_updated: bool = False


def source_original_5da5d9_encounter_and_tier(
    *,
    original_match_context_record:bytes,
    original_initial_encounter_pointer:int,
    original_initial_encounter_record:bytes,
    original_initial_encounter_v18_return_eax:int,
    original_selected_encounter_pointer:int,
    original_selected_encounter_record:bytes,
    original_second_selected_v18_return_eax:int,
    original_match_context_v60_return_eax:int|None,
) -> SourceOriginal5DA5D9Encounter:
    ctx=original_match_context_record
    initial=original_initial_encounter_record
    selected=original_selected_encounter_record
    p0=original_initial_encounter_pointer
    p1=original_selected_encounter_pointer
    if type(ctx) is not bytes or len(ctx)<0x50 or type(initial) is not bytes or len(initial)<8:
        raise OriginalMatchEncounterSourceError("actual original match/encounter source bytes required")
    def pointer(n,label):
        if type(n) is not int or not 0<n<=0xffffffff:
            raise OriginalMatchEncounterSourceError("actual "+label+" source pointer required")
    pointer(p0,"initial")
    pointer(p1,"selected")
    if unpack_from('<I',ctx,0x4c)[0]!=p0:
        raise OriginalMatchEncounterSourceError("native context+4C selected encounter mismatch")
    for name,value in (("initial v18",original_initial_encounter_v18_return_eax),
                       ("selected v18",original_second_selected_v18_return_eax)):
        if type(value) is not int or not 0<=value<=0xffffffff:
            raise OriginalMatchEncounterSourceError(name+" reached exact EAX required")
    alternate=unpack_from('<I',initial,4)[0]
    expected=alternate if not original_initial_encounter_v18_return_eax and alternate else p0
    if p1!=expected:
        raise OriginalMatchEncounterSourceError("native original v18/+4 encounter selection differs")
    if type(selected) is not bytes or len(selected)<0x40:
        raise OriginalMatchEncounterSourceError("selected encounter+3C bytes required")
    if p1==p0 and selected[:8]!=initial[:8]:
        raise OriginalMatchEncounterSourceError("same encountered object changed pointer/vtable header without source mutation")
    if not original_second_selected_v18_return_eax:
        if original_match_context_v60_return_eax is not None:
            raise OriginalMatchEncounterSourceError("original false v18 skips match v+60")
        return SourceOriginal5DA5D9Encounter(p0,p1,p1!=p0,False,0x5DA746,None,None)
    shift=original_match_context_v60_return_eax
    if type(shift) is not int or not 0<=shift<=0xffffffff:
        raise OriginalMatchEncounterSourceError("native v+60 reached return DWORD required")
    encounter=unpack_from('<I',selected,0x3c)[0]
    # Native subtraction 2^32 wraps and DEC creates same unsigned
    # equality guards for 2,3,4; all other cases map to (15-1).
    diff=(encounter-shift)&0xffffffff
    tier={2:30,3:20,4:15}.get(diff,14)
    return SourceOriginal5DA5D9Encounter(p0,p1,p1!=p0,True,0x5DA5FF,tier,diff)
