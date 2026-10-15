"""Original 41B970 multiplier, 41E1D0 max role and 409C90 source score.

Actual original owner-authorized PE SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
static analysis only, never executed or shipped in repository.

Do not infer native 41C7E0 outcomes, x87 668350 conversion, or mutable
4182F0/41EDF0 effects from present-day prototype ratings. These are
bounded read-only projections requiring independently observed reached
native callback results. No game world or save is changed here.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from


class Original409C90ScoreSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal41B970FpuFactor:
    original_native_player_at_call: bytes
    original_native_player_kind_byte192: int
    original_source_factor_double: float
    original_source_constant_va: int
    original_41b970_executed: bool = False


# From exact canonical shipped .data 0x822268,270,278,280,288 and
# 41B9A8 role enum jump table: kind0->984,1->98B,2->9A0,3->992,4->999.
_41B970_SOURCES=((0.9,0x822268),(0.95,0x822270),(1.0,0x822278),
                 (1.05,0x822280),(1.1,0x822288))


def source_original_41b970_player_morale_factor(
    *, original_native_player_at_41b970: bytes,
) -> SourceOriginal41B970FpuFactor:
    p=original_native_player_at_41b970
    if type(p) is not bytes or len(p)<=0x192:
        raise Original409C90ScoreSourceError(
            "original 41B970 player BYTE+0x192 at-call source record required")
    kind=p[0x192]
    factor,va=_41B970_SOURCES[kind] if kind<5 else (1.0,0x822278)
    return SourceOriginal41B970FpuFactor(p,kind,factor,va)


@dataclass(frozen=True)
class SourceOriginal41E1D0MaxStatusScore:
    original_player_at_call: bytes
    original_status_at_call: bytes
    original_source_status_pointer: int
    source_reached_41c7e0_arguments: tuple[int,...]
    source_reached_41c7e0_eax_if_called: tuple[int|None,int|None,int|None]
    original_return_eax: int
    native_41e1d0_or_41c7e0_executed: bool = False


def source_original_41e1d0_max_status_role_score(
    *, original_player_record_at_41e1d0: bytes,
    original_status_record_at_41e1d0: bytes,
    original_reached_41c7e0_signed_eax_per_nonzero_role:
        tuple[int|None,int|None,int|None],
) -> SourceOriginal41E1D0MaxStatusScore:
    """Native 41E1D0 loops 3 calls 4EA300(i) and, only for nonzero
    role codes, calls 41C7E0(player,role). EAX := max(0, scores);
    negative or tied candidates never lower winner.
    """
    p=original_player_record_at_41e1d0
    s=original_status_record_at_41e1d0
    scores=original_reached_41c7e0_signed_eax_per_nonzero_role
    if type(p) is not bytes or len(p)<0x24c or type(s) is not bytes or len(s)<3:
        raise Original409C90ScoreSourceError(
            "actual original player through+248 and separate source status bytes mandatory")
    owner=unpack_from("<I",p,0x248)[0]
    if owner==0:
        raise Original409C90ScoreSourceError("native status player+248 pointer must be nonzero")
    if type(scores) is not tuple or len(scores)!=3:
        raise Original409C90ScoreSourceError("exact original 3-slot source callback tuple required")
    used=[]
    best=0
    for i in range(3):
        role=s[i]
        result=scores[i]
        if role==0:
            if result is not None:
                raise Original409C90ScoreSourceError("original 41C7E0 skipped for zero status role")
            continue
        if type(result) is not int or not -0x80000000<=result<=0x7fffffff:
            raise Original409C90ScoreSourceError("reached 41C7E0 original signed EAX required")
        used.append(role)
        if result>best:best=result
    return SourceOriginal41E1D0MaxStatusScore(
        p,s,owner,tuple(used),scores,best)


@dataclass(frozen=True)
class SourceOriginal409C90PostSelectionContribution:
    original_native_slot_index: int
    original_native_player_pointer_at_scoring: int
    original_409c90_plus90_mode_dword: int
    original_player_after_source_assignment_at_call: bytes
    original_role_dword_from_876cb8: int
    original_previous_team_score_accumulator_signed: int
    original_native_score_subcall_return_signed_eax: int
    original_team_score_accumulator_after_source_add_signed: int
    original_mode1_max_score_if_reached: SourceOriginal41E1D0MaxStatusScore|None
    original_mode1_factor_if_reached: SourceOriginal41B970FpuFactor|None
    native_original_409c90_callbacks_executed: bool = False
    live_game_state_modified: bool = False


def source_original_409c90_selected_slot_score_contribution(
    *, original_slot_index: int,
    original_native_player_pointer_at_scoring: int,
    original_409c90_plus90_mode_dword: int,
    original_native_player_at_post_assignment_scoring: bytes,
    original_role_dword_from_original_876cb8: int,
    original_team_score_accumulator_before: int,
    original_reached_41e1d0_receipt_if_mode1: SourceOriginal41E1D0MaxStatusScore|None,
    original_reached_41b970_receipt_if_mode1: SourceOriginal41B970FpuFactor|None,
    original_reached_668350_eax_if_mode1: int|None,
    original_reached_41c7e0_eax_if_other_mode: int|None,
) -> SourceOriginal409C90PostSelectionContribution:
    """Native 40A1F8 literal mode1 invokes 41E1D0 then 41B970,
    fild signed32 EAX -> x87 multiply -> 668350 truncates toward
    zero and stores EAX before adding to team+34 accumulator.

    Other native modes call 41C7E0 once for original role DWORD
    and add its signed EAX without 41B970 or 668350.

    For mode1 the exact 668350 signed32 low-EAX must be observed
    independently from original x87; do not guess Python floats.
    """
    i=original_slot_index
    mode=original_409c90_plus90_mode_dword
    p=original_native_player_at_post_assignment_scoring
    role=original_role_dword_from_original_876cb8
    previous=original_team_score_accumulator_before
    if type(i) is not int or not 0<=i<11:
        raise Original409C90ScoreSourceError("original selected XI slot 0..10 required")
    if (type(original_native_player_pointer_at_scoring) is not int or
            not 0<original_native_player_pointer_at_scoring<=0xffffffff):
        raise Original409C90ScoreSourceError(
            "actual native original 875640 indexed player pointer at scoring mandatory")
    if type(mode) is not int or not 0<=mode<=0xffffffff:
        raise Original409C90ScoreSourceError("actual original 409C90 +90 mode DWORD required")
    if type(p) is not bytes or len(p)<0x24c or unpack_from("<I",p,0x248)[0]==0:
        raise Original409C90ScoreSourceError("at-call actual post-assignment source player+248 required")
    if type(role) is not int or not 0<=role<=0xffffffff:
        raise Original409C90ScoreSourceError("source 876CB8 role DWORD required")
    if type(previous) is not int or not -0x80000000<=previous<=0x7fffffff:
        raise Original409C90ScoreSourceError("actual signed32 team+34 accumulator required")
    scored=original_reached_41e1d0_receipt_if_mode1
    factor=original_reached_41b970_receipt_if_mode1
    product=original_reached_668350_eax_if_mode1
    other=original_reached_41c7e0_eax_if_other_mode
    if mode==1:
        if (type(scored) is not SourceOriginal41E1D0MaxStatusScore or
            type(factor) is not SourceOriginal41B970FpuFactor or
            scored.original_player_at_call!=p or factor.original_native_player_at_call!=p or
            other is not None or
            type(product) is not int or not -0x80000000<=product<=0x7fffffff):
            raise Original409C90ScoreSourceError(
                "source mode1 requires reached same-player 41E1D0/41B970 and original 668350 EAX")
        value=product
    else:
        if scored is not None or factor is not None or product is not None or (
                type(other) is not int or not -0x80000000<=other<=0x7fffffff):
            raise Original409C90ScoreSourceError(
                "source other mode calls only 41C7E0 with original role and player")
        value=other
    u=(previous+value)&0xffffffff
    signed=u if u<0x80000000 else u-0x100000000
    return SourceOriginal409C90PostSelectionContribution(
        i,original_native_player_pointer_at_scoring,mode,p,role,previous,value,signed,scored,factor)


@dataclass(frozen=True)
class SourceOriginal409C90FinalTeamScoreWrite:
    original_team_source_before_40a2a4: bytes
    original_team_source_after_40a2a4_literal_store: bytes
    original_selected_original_word_ids_in_slot_order: tuple[int,...]
    original_40a1f8_mode_dword: int
    source_original_eleven_postselection_scores: tuple[SourceOriginal409C90PostSelectionContribution,...]
    original_accumulator_final_signed32: int
    native_40a2a4_executed: bool = False
    source_409b50_team_plus1d8_executed: bool = False
    live_game_state_modified: bool = False


def source_original_409c90_exact_eleven_score_to_team_plus34(
    *, original_complete_source_second_pass: object,
    original_native_team_at_40a2a4: bytes,
    original_global_875640_player_array_base_at_scoring: int,
    original_40a1f8_mode_dword: int,
    original_eleven_reached_scores: tuple[SourceOriginal409C90PostSelectionContribution,...],
) -> SourceOriginal409C90FinalTeamScoreWrite:
    """Actual original 40A1D0 loops 11 selected WORD roster IDs,
    accumulates mode-specific score into local +2C signed32, and
    40A2A4 writes that DWORD to source native team+34. Never runs
    the original 41E1D0/41C7E0/4182F0 or GameState.
    """
    from original_native_409c90_second_pass_xi import SourceOriginal409C90SecondPass
    c=original_complete_source_second_pass
    team=original_native_team_at_40a2a4
    mode=original_40a1f8_mode_dword
    results=original_eleven_reached_scores
    if (type(c) is not SourceOriginal409C90SecondPass or
        not c.source_409c90_has_eleven_selected_slots or
        c.source_409c90_should_retry_at_409ca5_with_mode0):
        raise Original409C90ScoreSourceError(
            "original 40A158 assignment only reached after a complete eleven-player XI")
    if type(team) is not bytes or len(team)<0x298:
        raise Original409C90ScoreSourceError("full original team at 40A2A4 required")
    if (type(mode) is not int or not 0<=mode<=0xffffffff or
            type(results) is not tuple or len(results)!=11):
        raise Original409C90ScoreSourceError("original mode and eleven score receipts required")
    base=original_global_875640_player_array_base_at_scoring
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original409C90ScoreSourceError("actual original native player-array base mandatory")
    n=unpack_from("<i",team,0x294)[0]
    if n<11 or n>360:
        raise Original409C90ScoreSourceError("actual original reached 40A1D0 roster count >=11 required")
    if (unpack_from("<I",team,4)[0]!=c.original_source_first_pass.original_native_team_key or
        tuple(unpack_from("<H",team,0x244+i*2)[0] for i in range(n))!=
             c.original_source_first_pass.original_native_roster_word_ids_at_first_pass):
        raise Original409C90ScoreSourceError(
            "original source native team+4 and roster WORD ID owner changed after XI selection")
    chosen=c.source_original_selected_roster_indices11
    selected_ids=[]
    accumulator=0
    for i,(idx,contribution) in enumerate(zip(chosen,results)):
        if (type(idx) is not int or not 0<=idx<n or
                type(contribution) is not SourceOriginal409C90PostSelectionContribution or
                contribution.original_native_slot_index!=i or
                contribution.original_409c90_plus90_mode_dword!=mode or
                contribution.original_previous_team_score_accumulator_signed!=accumulator or
                contribution.original_role_dword_from_876cb8!=unpack_from(
                    "<I",c.original_source_first_pass.source_formation_role_entries11[i],0)[0]):
            raise Original409C90ScoreSourceError(
                "eleven original selected source roster indices/mode or score accumulation drift")
        pid=unpack_from("<H",team,0x244+idx*2)[0]
        p=contribution.original_player_after_source_assignment_at_call
        expected=base+pid*0x250
        if (expected>0xffffffff or
            contribution.original_native_player_pointer_at_scoring!=expected or
            unpack_from("<H",p,4)[0]!=pid or
            contribution.original_team_score_accumulator_after_source_add_signed!=
                ((accumulator+contribution.original_native_score_subcall_return_signed_eax
                  +0x80000000)&0xffffffff)-0x80000000):
            raise Original409C90ScoreSourceError(
                "original 875640 selected player ID or signed32 score source changed")
        selected_ids.append(pid)
        accumulator=contribution.original_team_score_accumulator_after_source_add_signed
    out=bytearray(team)
    from struct import pack_into
    pack_into("<i",out,0x34,accumulator)
    return SourceOriginal409C90FinalTeamScoreWrite(
        team,bytes(out),tuple(selected_ids),mode,results,accumulator)
