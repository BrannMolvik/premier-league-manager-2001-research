"""Original 409F74..40A158 second XI slot-filling pass and retry decision.

Canonical original private PE SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
static x86 trace only. This second pass fills slots remaining -1 from
the first strict 409D79 pass. It does NOT call 4EA300 status role getters:
it scores any source unmasked/unselected player for that role. It has
original 407DF0/41C7E0/41B970/668350 and 874BE0 conditional branches.
Its fallback 40A105 4037B0 manager gate may retry the ENTIRE two-pass
workflow with original modeflag reset0, not reuse this projected XI.
No original callback/GameState/score/calendar executes here.
"""
from dataclasses import dataclass
from struct import unpack_from
from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_409c90_first_pass_xi import (
    SourceOriginal409C90FirstPass, Original409C90FirstPassSourceError,
)


class Original409C90SecondPassSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal409C90SecondPassCandidate:
    original_roster_index: int
    original_reached_407df0_eax_if_bit11: int | None = None
    original_reached_41c7e0_eax_if_scored: int | None = None
    original_reached_668350_eax_if_scored: int | None = None


@dataclass(frozen=True)
class SourceOriginal409C90SecondPassRole:
    original_role_entry8_from_876cb8: bytes
    original_ordered_candidate_facts_if_unfilled:
        tuple[SourceOriginal409C90SecondPassCandidate,...] | None = None
    original_874be0_word_if_chosen_bit11_mode1: int | None = None


@dataclass(frozen=True)
class SourceOriginal409C90SecondPass:
    original_source_first_pass: SourceOriginal409C90FirstPass
    source_original_selected_roster_indices11: tuple[int,...]
    source_second_pass_newly_selected_roster_indices11: tuple[int,...]
    source_used_mask_after_both_passes: bytes
    source_special_count_after_both_passes: int
    original_first_unfillable_second_pass_slot: int | None
    original_unfilled_40a105_reached_4037b0_human_al: bool | None
    source_409c90_should_retry_at_409ca5_with_mode0: bool
    source_409c90_has_eleven_selected_slots: bool
    original_40a1bb_assignment_not_executed: bool = True
    original_live_game_state_modified: bool = False


def _num(x,a,b,name):
    if type(x) is not int or not a<=x<=b:
        raise Original409C90SecondPassSourceError(f"original {name} numeric value required")
    return x


def source_original_409c90_second_pass_fill_unmatched_eleven_slots(
    *, original_first_pass: SourceOriginal409C90FirstPass,
    original_team_record_at_second_pass: bytes,
    original_global_875640_player_base: int,
    original_ordered_players_at_second_pass: tuple[SourceOriginal406BE0Player,...],
    original_eleven_second_pass_roles: tuple[SourceOriginal409C90SecondPassRole,...],
    original_4037b0_human_al_if_any_slot_unfilled: bool | None = None,
) -> SourceOriginal409C90SecondPass:
    """Bounded actual 409F74→40A100 chooser; returned slot INDEX not ID.

    A native first-pass filled slot skips second pass entirely (409F93).
    For missing slot, original scans all native roster records in order:
    skip if original initial-mask BYTE!=0 or the used-mask BYTE!=0;
    then player+14 bit11 -> 407DF0 unsigned cutoff; no 4EA300 calls;
    actual 41C7E0 score for role, x87 factor and 668350 EAX,
    zero clamp to 1, strict > tie, no substitution of reconstructed
    player ratings. Source 40A105 if any role stays -1 frees the
    masks and invokes 4037B0; nonhuman AL0 and modeflag1 retries
    from original 409CA5 with modeflag reset0. This projection
    DOES NOT itself retry or simulate original native world changes.
    """
    first=original_first_pass
    t=original_team_record_at_second_pass
    rows=original_ordered_players_at_second_pass
    roles=original_eleven_second_pass_roles
    if type(first) is not SourceOriginal409C90FirstPass:
        raise Original409C90SecondPassSourceError("source first-pass receipt required")
    if type(t) is not bytes or len(t)<0x298 or type(rows) is not tuple:
        raise Original409C90SecondPassSourceError("original second pass team and player records required")
    n=len(rows)
    if (n>360 or len(t)<0x244+n*2 or
        t!=first.original_team_record_at_first_pass or
        tuple(unpack_from("<H",t,0x244+i*2)[0] for i in range(n))!=
            first.original_native_roster_word_ids_at_first_pass or
        unpack_from("<I",t,4)[0]!=first.original_native_team_key or
        len(first.source_used_mask_after_first_pass)!=n or
        len(first.original_reached_first_mask)!=n):
        raise Original409C90SecondPassSourceError("native team/candidate mask identity mismatch")
    base=_num(original_global_875640_player_base,1,0xffffffff,"875640 base")
    for i,row in enumerate(rows):
        pid=unpack_from("<H",t,0x244+i*2)[0]
        ptr=base+pid*0x250
        if (type(row) is not SourceOriginal406BE0Player or
            row.original_roster_word_id!=pid or
            row.original_player_record_native_pointer!=ptr or
            ptr>0xffffffff or type(row.original_player_record_bytes) is not bytes or
            len(row.original_player_record_bytes)<0x18):
            raise Original409C90SecondPassSourceError("native player 875640 stride/order mismatch")
    if type(roles) is not tuple or len(roles)!=11:
        raise Original409C90SecondPassSourceError("exact eleven role source inputs mandatory")
    if (len(first.source_original_selection_indices11)!=11 or
        len(first.source_formation_role_entries11)!=11):
        raise Original409C90SecondPassSourceError("first strict pass has incomplete 11 slots")
    prior=first.source_original_selection_indices11
    picked=[i for i in prior if i>=0]
    if (any(type(x) is not int or x < -1 or x>=n for x in prior) or
        len(picked)!=len(set(picked)) or
        any(b not in (0,1) for b in first.source_used_mask_after_first_pass) or
        any(first.source_used_mask_after_first_pass[i]!=int(i in picked) for i in range(n))):
        raise Original409C90SecondPassSourceError("first original slot indices/used-mask receipt inconsistent")
    used=bytearray(first.source_used_mask_after_first_pass)
    selected=list(first.source_original_selection_indices11)
    changed=[-1]*11
    count=first.source_special_count_after_first_pass
    aborted_slot=None
    for slot,rule in enumerate(roles):
        if type(rule) is not SourceOriginal409C90SecondPassRole:
            raise Original409C90SecondPassSourceError("original role source receipt required")
        if (type(rule.original_role_entry8_from_876cb8) is not bytes or
            rule.original_role_entry8_from_876cb8!=first.source_formation_role_entries11[slot]):
            raise Original409C90SecondPassSourceError("original 876CB8 formation role changed between passes")
        if aborted_slot is not None:
            # Native 409F9E and 40A072 jump directly to 40A105 when
            # this slot has no candidate; later slots never run.
            if (rule.original_ordered_candidate_facts_if_unfilled is not None or
                rule.original_874be0_word_if_chosen_bit11_mode1 is not None):
                raise Original409C90SecondPassSourceError(
                    "40A105 early abort makes every later role/candidate source unreachable")
            continue
        if selected[slot]>=0:
            if (rule.original_ordered_candidate_facts_if_unfilled is not None or
                rule.original_874be0_word_if_chosen_bit11_mode1 is not None):
                raise Original409C90SecondPassSourceError("already selected role skips second-pass callbacks")
            continue
        facts=rule.original_ordered_candidate_facts_if_unfilled
        if type(facts) is not tuple or len(facts)!=n:
            raise Original409C90SecondPassSourceError("original second-pass full roster scan required")
        best=-1
        best_score=0
        for i,(row,fact) in enumerate(zip(rows,facts)):
            if (type(fact) is not SourceOriginal409C90SecondPassCandidate or
                type(fact.original_roster_index) is not int or
                fact.original_roster_index!=i):
                raise Original409C90SecondPassSourceError("source roster index/candidate receipt mismatch")
            rest=(fact.original_reached_407df0_eax_if_bit11,
                  fact.original_reached_41c7e0_eax_if_scored,
                  fact.original_reached_668350_eax_if_scored)
            if first.original_reached_first_mask[i] or used[i]:
                if any(x is not None for x in rest):
                    raise Original409C90SecondPassSourceError("original masked/selected second-pass candidate skips callbacks")
                continue
            flags=unpack_from("<I",row.original_player_record_bytes,0x14)[0]
            limit=fact.original_reached_407df0_eax_if_bit11
            if flags&0x800:
                cap=_num(limit,0,0xffffffff,"reached 407DF0 unsigned EAX")
                if count>=cap:
                    if any(x is not None for x in rest[1:]):
                        raise Original409C90SecondPassSourceError("original 407DF0 cutoff skips scorer")
                    continue
            elif limit is not None:
                raise Original409C90SecondPassSourceError("407DF0 only on original player+14 bit11")
            eax_score=fact.original_reached_41c7e0_eax_if_scored
            x87=fact.original_reached_668350_eax_if_scored
            _num(eax_score,-0x80000000,0x7fffffff,"source 41C7E0 score")
            converted=_num(x87,-0x80000000,0x7fffffff,"source 668350 EAX")
            score=1 if converted==0 else converted
            if score>best_score:
                best=i
                best_score=score
        word=rule.original_874be0_word_if_chosen_bit11_mode1
        if best<0:
            if word is not None:
                raise Original409C90SecondPassSourceError("no selected second-pass player skips 874BE0")
            aborted_slot=slot
            continue
        selected[slot]=best
        changed[slot]=best
        used[best]=1
        flags=unpack_from("<I",rows[best].original_player_record_bytes,0x14)[0]
        if flags&0x800 and first.original_esp94_mode_flag==1:
            w=_num(word,0,0xffff,"actual source 874BE0 indexed WORD")
            if w:
                count+=1
        elif word is not None:
            raise Original409C90SecondPassSourceError("selected non-special roster skips original 874BE0")
    incomplete=aborted_slot is not None
    human=original_4037b0_human_al_if_any_slot_unfilled
    if incomplete:
        if type(human) is not bool:
            raise Original409C90SecondPassSourceError(
                "original 40A120 4037B0 human AL mandatory after missing eleven-slot selection")
    elif human is not None:
        raise Original409C90SecondPassSourceError(
            "complete selected eleven skips source 40A105 / 4037B0")
    retry=bool(incomplete and not human and first.original_esp94_mode_flag==1)
    return SourceOriginal409C90SecondPass(first,tuple(selected),tuple(changed),
        bytes(used),count,aborted_slot,human,retry,not incomplete)
