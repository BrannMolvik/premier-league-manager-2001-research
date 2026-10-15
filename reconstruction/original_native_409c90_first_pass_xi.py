"""Original 409D79..409F5E first (strict role-match) eleven-slot selector.

Canonical private original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
statically disassembled only. CRITICAL SOURCE CORRECTION: the preliminary
409D5E mask is a SKIP/EXCLUSION mask, not an eligibility-true mask.
At 409DDA and 409DE2 a nonzero byte SKIPS a player.

The bounded source projector uses original slot role DWORD from 876CB8,
actual status first-three bytes for 4EA300(0/1/2) and independently
reached original 407DF0, 41C7E0, 41B970/668350 outcomes; no dynamic
callback or actual original x87 score is executed/inferred by the port.
Strict > source tie handling and mode1 bit11 count are reproduced.
Only original first pass is modeled; second-pass fallbacks, player
status mutations, team+34/+1D8, v34/match and SaveLoad remain unexecuted.
"""
from dataclasses import dataclass
from struct import unpack_from
from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_409c90_initial_availability import SourceOriginal409C90InitialMask


class Original409C90FirstPassSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal409C90FirstPassCandidate:
    original_roster_index: int
    original_reached_407df0_eax_if_bit11: int | None = None
    original_reached_status_bytes_if_4ea300_called: bytes | None = None
    original_reached_41c7e0_eax_if_scored: int | None = None
    original_reached_668350_eax_if_scored: int | None = None


@dataclass(frozen=True)
class SourceOriginal409C90FirstPassRole:
    original_role_entry8_from_876cb8: bytes
    original_ordered_candidate_facts: tuple[SourceOriginal409C90FirstPassCandidate,...]
    original_874be0_roster_word_if_selected_bit11_and_mode1: int | None = None


@dataclass(frozen=True)
class SourceOriginal409C90FirstPass:
    original_native_team_key: int
    original_reached_first_mask: bytes
    source_original_selection_indices11: tuple[int,...]
    source_used_mask_after_first_pass: bytes
    original_special_count_before: int
    source_special_count_after_first_pass: int
    source_best_scores11: tuple[int,...]
    original_strict_second_pass_still_required: bool = True
    original_41c7e0_41b970_668350_callbacks_executed: bool = False
    original_world_mutated: bool = False
    live_game_state_modified: bool = False


def _source_int(value, lo, hi, field):
    if type(value) is not int or not lo<=value<=hi:
        raise Original409C90FirstPassSourceError(f"source {field} native integer required")
    return value


def source_original_409c90_first_pass_eleven_strict_role_slots(
    *, original_team_record_at_first_pass: bytes,
    original_global_875640_native_player_base: int,
    original_mask_receipt_after_409d5e: SourceOriginal409C90InitialMask,
    original_ordered_player_records_at_first_pass: tuple[SourceOriginal406BE0Player,...],
    original_first_pass_esp14_special_count: int,
    original_first_pass_esp94_mode_flag: int,
    original_eleven_role_source_inputs: tuple[SourceOriginal409C90FirstPassRole,...],
) -> SourceOriginal409C90FirstPass:
    """Source first pass 11 slots, without the second pass or GameState.

    The native first-used array is zeroed at 409CBE; the exclusion mask
    from 409D5E remains separate. Every slot scans every native roster
    entry in original WORD order. Skip if EITHER byte mask nonzero.
    The source player+14 bit11 407DF0 branch is an UNSIGNED
    current-count >= returned-EAX skip. Then original 4EA300
    status[0], status[1], status[2] are checked IN ORDER against role
    DWORD. On first matching status, score is actual reached 668350
    signed EAX for 41C7E0 role * 41B970 factor; zero gets 1.
    Only score strictly greater than best0 replaces index. A chosen
    source player is marked used in the first byte array. When
    selected bit11 and modeflag1, a nonzero reached global
    874BE0 word incremented source special-count at 409F43.
    """
    team=original_team_record_at_first_pass
    mask=original_mask_receipt_after_409d5e
    rows=original_ordered_player_records_at_first_pass
    n=len(rows) if type(rows) is tuple else -1
    if type(team) is not bytes or len(team)<0x298:
        raise Original409C90FirstPassSourceError("original native team record through +294 mandatory")
    if type(mask) is not SourceOriginal409C90InitialMask or type(rows) is not tuple:
        raise Original409C90FirstPassSourceError("real source 409D5E mask and ordered players required")
    if (mask.original_reached_roster_count!=n or
        mask.original_club_key_dword!=unpack_from("<I",team,4)[0] or
        mask.original_team_class_byte74!=team[0x74] or
        len(mask.source_mask_bytes)!=n or
        mask.original_roster_word_ids_in_order!=tuple(
            unpack_from("<H",team,0x244+2*i)[0] for i in range(n))):
        raise Original409C90FirstPassSourceError("source team+4, +74 and roster/mask identity mismatch")
    if len(team)<0x244+2*n or n>360:
        raise Original409C90FirstPassSourceError("source roster/count capacity invalid")
    base=_source_int(original_global_875640_native_player_base,1,0xffffffff,"875640 base")
    for i,row in enumerate(rows):
        pid=unpack_from("<H",team,0x244+2*i)[0]
        ptr=base+pid*0x250
        if (type(row) is not SourceOriginal406BE0Player or
            row.original_roster_word_id!=pid or ptr>0xffffffff or
            row.original_player_record_native_pointer!=ptr or
            type(row.original_player_record_bytes) is not bytes or
            len(row.original_player_record_bytes)<0x24c):
            raise Original409C90FirstPassSourceError("native 875640 player pointer and full record required")
    count=_source_int(original_first_pass_esp14_special_count,0,0x7fffffff,
                      "current 409D79 special count")
    mode=_source_int(original_first_pass_esp94_mode_flag,0,0xffffffff,
                     "409F1A native mode flag")
    roles=original_eleven_role_source_inputs
    if type(roles) is not tuple or len(roles)!=11:
        raise Original409C90FirstPassSourceError("exact original 11-slot formation role receipts required")
    used=bytearray(n)
    chosen=[]
    scores=[]
    for slot,rule in enumerate(roles):
        if type(rule) is not SourceOriginal409C90FirstPassRole:
            raise Original409C90FirstPassSourceError("original slot role receipt type required")
        if (type(rule.original_role_entry8_from_876cb8) is not bytes or
            len(rule.original_role_entry8_from_876cb8)!=8):
            raise Original409C90FirstPassSourceError("exact original 876CB8 role-table 8-byte entry mandatory")
        role=unpack_from("<I",rule.original_role_entry8_from_876cb8,0)[0]
        facts=rule.original_ordered_candidate_facts
        if type(facts) is not tuple or len(facts)!=n:
            raise Original409C90FirstPassSourceError("complete native roster scan by role mandatory")
        best=-1
        best_score=0
        for i,(row,fact) in enumerate(zip(rows,facts)):
            if (type(fact) is not SourceOriginal409C90FirstPassCandidate or
                    type(fact.original_roster_index) is not int or
                    fact.original_roster_index!=i):
                raise Original409C90FirstPassSourceError("original role roster-index order drift")
            remaining=(fact.original_reached_407df0_eax_if_bit11,
                       fact.original_reached_status_bytes_if_4ea300_called,
                       fact.original_reached_41c7e0_eax_if_scored,
                       fact.original_reached_668350_eax_if_scored)
            if mask.source_mask_bytes[i] or used[i]:
                if any(v is not None for v in remaining):
                    raise Original409C90FirstPassSourceError("masked/already selected native candidate skips callbacks")
                continue
            p=row.original_player_record_bytes
            bit11=bool(unpack_from("<I",p,0x14)[0]&0x800)
            limit=fact.original_reached_407df0_eax_if_bit11
            if bit11:
                lim=_source_int(limit,0,0xffffffff,"reached 407DF0 EAX")
                # Original 409E09 is unsigned JAE.
                if count>=lim:
                    if any(v is not None for v in remaining[1:]):
                        raise Original409C90FirstPassSourceError("407DF0 source cutoff skips 4EA300/score")
                    continue
            elif limit is not None:
                raise Original409C90FirstPassSourceError("original 407DF0 skipped when player bit11 false")
            status=fact.original_reached_status_bytes_if_4ea300_called
            if (type(status) is not bytes or len(status)<3 or
                unpack_from("<I",p,0x248)[0]==0):
                raise Original409C90FirstPassSourceError(
                    "reached 4EA300 original status record and pointer required")
            matches=(status[0]==role or status[1]==role or status[2]==role)
            result=fact.original_reached_668350_eax_if_scored
            src_score=fact.original_reached_41c7e0_eax_if_scored
            if not matches:
                if src_score is not None or result is not None:
                    raise Original409C90FirstPassSourceError(
                        "original 4EA300(0/1/2) no-role match skips 41C7E0 and x87")
                continue
            _source_int(src_score,-0x80000000,0x7fffffff,"reached 41C7E0 EAX")
            e=_source_int(result,-0x80000000,0x7fffffff,"reached 668350 x87 truncate EAX")
            score=1 if e==0 else e
            # Native jle at 409E8F keeps first earlier roster ID on tie.
            if score>best_score:
                best=i
                best_score=score
        chosen.append(best)
        scores.append(best_score)
        word=rule.original_874be0_roster_word_if_selected_bit11_and_mode1
        if best<0:
            if word is not None:
                raise Original409C90FirstPassSourceError("no selected player skips 874BE0 bonus read")
            continue
        used[best]=1
        source_player=rows[best].original_player_record_bytes
        if bool(unpack_from("<I",source_player,0x14)[0]&0x800) and mode==1:
            w=_source_int(word,0,0xffff,"reached 874BE0 WORD at club+14 indexed table")
            if w:
                count+=1
        elif word is not None:
            raise Original409C90FirstPassSourceError(
                "original bit11/mode flag not both true skips 874BE0 indexed WORD")
    return SourceOriginal409C90FirstPass(
        unpack_from("<I",team,4)[0],mask.source_mask_bytes,tuple(chosen),
        bytes(used),original_first_pass_esp14_special_count,count,tuple(scores))
