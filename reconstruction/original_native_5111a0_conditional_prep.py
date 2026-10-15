"""Original 5111A0 conditional 4037B0 -> 511170 -> 409B50 reachability.

Private original PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Original static source ONLY: no native 511170, 4037B0, 409B50,
405A20, 510CD0 or side world mutation is executed by this module.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_leaguematch_native_process_owners import (
    source_original_leaguematch_process_owners_for_native_record,
    OriginalLeagueMatchProcessOwnerError,
)

class Original5111A0ConditionalSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal5111A0SideConditional:
    original_side_index: int
    original_native_team_pointer: int
    original_4037b0_checked: bool
    original_4037b0_human_al_if_reached: bool | None
    original_511170_v18_eax_nonzero_if_reached: bool | None
    original_511170_second_4f3dc0_eax_if_needed: int | None
    original_409b50_reached_args_if_needed: tuple[int,int,int] | None
    native_511170_executed: bool = False
    native_409b50_executed: bool = False

@dataclass(frozen=True)
class SourceOriginal5111A0ConditionalBeforeBothSorts:
    original_match_vtable_va: int
    original_match_flags44: int
    original_409b50_skipped_due_to_bit5: bool
    original_side_conditional_receipts: tuple[SourceOriginal5111A0SideConditional,...]
    source_mandatory_405a20_order: tuple[int,int]
    original_all_5111a0_callbacks_executed: bool = False
    live_world_modified: bool = False

def source_original_5111a0_conditional_nonhuman_409b50_plan(
    *, original_match_record_at_5111a0: bytes,
    original_processing_context_at_5111a0: bytes,
    original_first_team_record_at_5111a0: bytes,
    original_second_team_record_at_5111a0: bytes,
    original_first_match_4c_pointer_if_nonhuman_reached: int | None,
    original_second_match_4c_pointer_if_nonhuman_reached: int | None,
    original_first_match_4c_owner_record_if_nonhuman_reached: bytes | None,
    original_second_match_4c_owner_record_if_nonhuman_reached: bytes | None,
    original_first_4037b0_human_al_if_reached: bool | None,
    original_second_4037b0_human_al_if_reached: bool | None,
    original_first_511170_v18_nonzero_if_needed: bool | None,
    original_second_511170_v18_nonzero_if_needed: bool | None,
    original_first_511170_second_4f3dc0_pointer_if_needed: int | None,
    original_second_511170_second_4f3dc0_pointer_if_needed: int | None,
) -> SourceOriginal5111A0ConditionalBeforeBothSorts:
    """Original 5111AB..511215 and unconditional 511235/51125E order.

    If match+44 bit0x20, skip ALL 4037B0/511170/409B50.
    Otherwise 4037B0 on each team; non-human branches push
    [match+4C owner]+1C, team+294, 511170 output to 409B50. The
    511170 callee fetches match+4C -> 4F3DC0 -> virtual+18; if
    v18 returns zero, EAX=0, otherwise source calls 4F3DC0 AGAIN
    after mutable v18 and returns that actual independently reached
    node pointer. The two original teams then each run 405A20
    UNCONDITIONALLY, regardless of these branches.
    """
    match=original_match_record_at_5111a0
    context=original_processing_context_at_5111a0
    if type(match) is not bytes or len(match)<0x50:
        raise Original5111A0ConditionalSourceError("original LeagueMatch record through +4C required")
    if type(context) is not bytes or len(context)<0x5b4:
        raise Original5111A0ConditionalSourceError("source match processing context+5B0 required")
    try:
        owner=source_original_leaguematch_process_owners_for_native_record(original_match_record=match)
    except OriginalLeagueMatchProcessOwnerError as e:
        raise Original5111A0ConditionalSourceError("original LeagueMatch vtable must be authentic") from e
    pointer=unpack_from("<I",match,0x4c)[0]
    flags=unpack_from("<I",match,0x44)[0]
    source_teams=(unpack_from("<I",context,0)[0],unpack_from("<I",context,0x5b0)[0])
    if any(p==0 for p in source_teams) or source_teams[0]==source_teams[1]:
        raise Original5111A0ConditionalSourceError("original context must own distinct team pointers")
    teams=(original_first_team_record_at_5111a0,original_second_team_record_at_5111a0)
    if any(type(t) is not bytes or len(t)<0x298 for t in teams):
        raise Original5111A0ConditionalSourceError("both original team records through signed roster count required")
    # 409B50 for side0 may mutate match+4C or its object before side1.
    # Read the reached owner and +1C separately at the exact call site;
    # never reuse a pre-callback snapshot as if both sides share it.
    owners=(
        original_first_match_4c_owner_record_if_nonhuman_reached,
        original_second_match_4c_owner_record_if_nonhuman_reached,
    )
    pointers=(
        original_first_match_4c_pointer_if_nonhuman_reached,
        original_second_match_4c_pointer_if_nonhuman_reached,
    )
    human=(original_first_4037b0_human_al_if_reached,
           original_second_4037b0_human_al_if_reached)
    v18=(original_first_511170_v18_nonzero_if_needed,
         original_second_511170_v18_nonzero_if_needed)
    nodes=(original_first_511170_second_4f3dc0_pointer_if_needed,
           original_second_511170_second_4f3dc0_pointer_if_needed)
    skip=bool(flags&0x20)
    if skip and any(v is not None for v in human+v18+nodes+owners+pointers):
        raise Original5111A0ConditionalSourceError("bit5 branch skips all source 4037B0 and 511170")
    receipts=[]
    for i in range(2):
        if skip:
            receipts.append(SourceOriginal5111A0SideConditional(i,source_teams[i],False,None,None,None,None))
            continue
        if type(human[i]) is not bool:
            raise Original5111A0ConditionalSourceError("actual source 4037B0 human AL on both teams required")
        if human[i]:
            if (v18[i] is not None or nodes[i] is not None or
                    owners[i] is not None or pointers[i] is not None):
                raise Original5111A0ConditionalSourceError("human team skips 511170 and 409B50")
            receipts.append(SourceOriginal5111A0SideConditional(i,source_teams[i],True,True,None,None,None))
            continue
        if (type(pointers[i]) is not int or not 0<pointers[i]<=0xffffffff or
                type(owners[i]) is not bytes or len(owners[i])<0x20):
            raise Original5111A0ConditionalSourceError(
                "actual native match+4C pointer and owner+1C at this reached side required")
        if i==0 and pointers[i]!=pointer:
            raise Original5111A0ConditionalSourceError(
                "first nonhuman side match+4C owner not from original match entry")
        match_arg=unpack_from("<I",owners[i],0x1c)[0]
        if type(v18[i]) is not bool:
            raise Original5111A0ConditionalSourceError("source 511170 reached vtable+18 return required")
        if v18[i]:
            n=nodes[i]
            if type(n) is not int or not 0<n<=0xffffffff:
                raise Original5111A0ConditionalSourceError("post-v18 original second 4F3DC0 actual pointer required")
        else:
            if nodes[i] is not None:
                raise Original5111A0ConditionalSourceError("v18 false skips the second 4F3DC0")
            n=0
        count=unpack_from("<I",teams[i],0x294)[0]
        receipts.append(SourceOriginal5111A0SideConditional(
            i,source_teams[i],True,False,v18[i],nodes[i],(n,count,match_arg)))
    return SourceOriginal5111A0ConditionalBeforeBothSorts(
        owner.source_vtable_va,flags,skip,tuple(receipts),source_teams)


@dataclass(frozen=True)
class SourceOriginal5111A0BoundedPreparationPlan:
    conditional_source: SourceOriginal5111A0ConditionalBeforeBothSorts
    first_405a20_source_sort: object
    second_405a20_source_sort: object
    two_selected_pointer_arrays: object
    original_reached_action_sites_in_order: tuple[int,...]
    native_original_5111a0_executed: bool = False
    native_world_and_sort_mutated: bool = False
    original_game_state_modified: bool = False


def source_original_5111a0_conditional_sorts_and_selected_tail(
    *, original_conditional_source: SourceOriginal5111A0ConditionalBeforeBothSorts,
    original_native_match_record_at_entry: bytes,
    original_processing_context_at_entry: bytes,
    original_first_team_native_pointer_at_405a20: int,
    original_second_team_native_pointer_at_405a20: int,
    original_first_team_record_actual_at_405a20: bytes,
    original_second_team_record_actual_at_405a20: bytes,
    original_first_405a20_source_sort: object,
    original_second_405a20_source_sort: object,
    original_global_875640_player_array_address: int,
    original_first_407770_zero_gate_nonzero: bool,
    original_second_407770_zero_gate_nonzero: bool,
) -> SourceOriginal5111A0BoundedPreparationPlan:
    """Full bounded SOURCE sequencing of native 5111A0, not its execution.

    Independently reached post-409B50 first/second 405A20 snapshots are
    mandatory. Do NOT just copy old 5111A0 pre-mutation team bytes,
    since original 409B50 / 409C90 can update team/player state.
    Never use this receipt as a live match or original save write.
    """
    from original_native_405a20_sort_roster import SourceOriginal405A20NativeRosterSort
    from original_native_510cd0_selected_roster import (
        source_original_5111a0_two_source_selection_arrays)
    c=original_conditional_source
    if type(c) is not SourceOriginal5111A0ConditionalBeforeBothSorts:
        raise Original5111A0ConditionalSourceError("original conditional source receipt mandatory")
    if (type(original_native_match_record_at_entry) is not bytes or
        len(original_native_match_record_at_entry)<0x50 or
        unpack_from("<I",original_native_match_record_at_entry,0)[0]!=c.original_match_vtable_va or
        unpack_from("<I",original_native_match_record_at_entry,0x44)[0]!=c.original_match_flags44):
        raise Original5111A0ConditionalSourceError("source entry match/flags identity drift")
    ctx=original_processing_context_at_entry
    if (type(ctx) is not bytes or len(ctx)<0x5b4 or
            tuple(unpack_from("<I",ctx,p)[0] for p in (0,0x5b0)) !=
            c.source_mandatory_405a20_order):
        raise Original5111A0ConditionalSourceError("source player context team ownership drift")
    expected=c.source_mandatory_405a20_order
    if (type(original_first_team_native_pointer_at_405a20) is not int or
        type(original_second_team_native_pointer_at_405a20) is not int or
        (original_first_team_native_pointer_at_405a20,
         original_second_team_native_pointer_at_405a20)!=expected):
        raise Original5111A0ConditionalSourceError(
            "actual original reached 405A20 native team pointers required")
    if (type(original_first_405a20_source_sort) is not SourceOriginal405A20NativeRosterSort or
        type(original_second_405a20_source_sort) is not SourceOriginal405A20NativeRosterSort):
        raise Original5111A0ConditionalSourceError("two native source sort receipts required")
    # Two independent actual post-409B50, pre-sort native team snapshots:
    # do not swap an unrelated team's receipt merely because it has the
    # same bytes/layout or because a Python sort returns a valid shape.
    source_teams=(original_first_team_record_actual_at_405a20,
                  original_second_team_record_actual_at_405a20)
    sorts=(original_first_405a20_source_sort,original_second_405a20_source_sort)
    for actual,receipt in zip(source_teams,sorts):
        if (type(actual) is not bytes or len(actual)<0x298 or
                actual!=receipt.original_team_roster_before_405a20):
            raise Original5111A0ConditionalSourceError(
                "actual independently reached 405A20 native team snapshot must match sort receipt")
    if (type(original_first_407770_zero_gate_nonzero) is not bool or
        type(original_second_407770_zero_gate_nonzero) is not bool or
        not original_first_407770_zero_gate_nonzero or
        not original_second_407770_zero_gate_nonzero):
        raise Original5111A0ConditionalSourceError("5111A0 never reached without two 407770(0) positives")
    try:
        tail=source_original_5111a0_two_source_selection_arrays(
            original_match_record=original_native_match_record_at_entry,
            original_first_407770_zero_gate_nonzero=True,
            original_second_407770_zero_gate_nonzero=True,
            original_first_405a20_source_sort=original_first_405a20_source_sort,
            original_second_405a20_source_sort=original_second_405a20_source_sort,
            original_global_875640_player_array_address=original_global_875640_player_array_address)
    except (ValueError, TypeError) as e:
        raise Original5111A0ConditionalSourceError(
            "native sort/selection source identity or pointer validation failed") from e
    actions=[]
    for side in c.original_side_conditional_receipts:
        if side.original_4037b0_checked:
            actions.append((0x5111B7,0x5111E5)[side.original_side_index])
            if side.original_409b50_reached_args_if_needed is not None:
                actions.append((0x5111D2,0x511204)[side.original_side_index])
                actions.append((0x5111DA,0x511210)[side.original_side_index])
    actions += [0x511235,0x51125E,0x51126C,0x511287]
    return SourceOriginal5111A0BoundedPreparationPlan(
        c,original_first_405a20_source_sort,original_second_405a20_source_sort,
        tail,tuple(actions))
