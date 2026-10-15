"""Native 5130C2 v+34-false fallback 512D80 two random6 scores.

Source original 512D80 sets global byte 8774C4=1, calls CRT-backed
64D540(6) TWICE with no intervening native RNG consumer, writes
processing-context +D4C/+D50 DWORDs, applies actual team 407770
eligibility and then 516040/050/060/070 special-condition overrides.
513010 then jumps to v38 and v3c (but these downstream callbacks
are NOT executed here). This is source-only immutable projection, NOT
a reconstructed live match engine or permission to fabricate its v34
result, team eligibility or global special flags.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_native_66d553_tls_initial_state import SourceOriginal66D553TLSRecord
from original_native_64d540_rand_step import (
    SourceOriginal64D540DrawReceipt,source_original_66951c_then_64d540_scaled_draw,
)


class Original512D80SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original512D80SpecialGate:
    native_gate_function_va: int
    original_reached_gate_al_nonzero: bool
    original_reached_first_team_human_al_if_needed: bool | None
    original_reached_second_team_human_al_if_needed: bool | None
    original_reached_registry0_club_pointer_if_needed: int | None


@dataclass(frozen=True)
class SourceOriginal512D80FallbackScores:
    original_context_pointer: int
    original_first_team_pointer: int
    original_second_team_pointer: int
    original_original_v34_false_reached: bool
    original_global_8774c4_write_one: bool
    first_64d540_six: SourceOriginal64D540DrawReceipt
    second_64d540_six: SourceOriginal64D540DrawReceipt
    original_first_score_context_d4c: int
    original_second_score_context_d50: int
    original_override_path_sites: tuple[int,...]
    native_407770_or_5160xx_callbacks_executed: bool = False
    native_original_rng_executed: bool = False
    native_v38_v3c_executed: bool = False
    live_game_state_updated: bool = False


def source_original_512d80_fallback_random_scores(
    *, original_v34_at_5130c2_returned_false: bool,
    original_context_pointer: int,
    original_context_record_before_512d80: bytes,
    original_tls_record_source: SourceOriginal66D553TLSRecord,
    original_first_team_407770_eax_nonzero: bool,
    original_second_team_407770_eax_nonzero: bool,
    original_four_special_gates: tuple[Original512D80SpecialGate,...],
) -> SourceOriginal512D80FallbackScores:
    if type(original_v34_at_5130c2_returned_false) is not bool or original_v34_at_5130c2_returned_false:
        raise Original512D80SourceError("actual original v+34 FALSE 5130C2 branch required")
    if type(original_context_pointer) is not int or not 0<original_context_pointer<=0xffffffff:
        raise Original512D80SourceError("original 512D80 processing context pointer required")
    raw=original_context_record_before_512d80
    if type(raw) is not bytes or len(raw)<0xd54:
        raise Original512D80SourceError("source original context through +D50 required")
    first=unpack_from('<I',raw,0)[0]
    second=unpack_from('<I',raw,0x5b0)[0]
    if not first or not second or first==second:
        raise Original512D80SourceError("two distinct nonzero original source team pointers required")
    for flag in (original_first_team_407770_eax_nonzero,
                 original_second_team_407770_eax_nonzero):
        if type(flag) is not bool:
            raise Original512D80SourceError("both reached 407770 team-selection flags required")
    tls=original_tls_record_source
    if (type(tls) is not SourceOriginal66D553TLSRecord or
        not 0<tls.original_tls_record_pointer<=0xffffffff or
        type(tls.source_record_before_first_reached_66951c) is not bytes or
        len(tls.source_record_before_first_reached_66951c)<0x18 or
        unpack_from('<I',tls.source_record_before_first_reached_66951c,0x14)[0]!=
            tls.original_seed_at_plus14):
        raise Original512D80SourceError("actual 66D553 thread TLS source state required")
    draw1=source_original_66951c_then_64d540_scaled_draw(
        original_66d553_rng_owner_pointer=tls.original_tls_record_pointer,
        original_rng_owner_before_66951c=tls.source_record_before_first_reached_66951c,
        original_64d540_reached_signed_argument=6)
    # Native 512D80 uses two adjacent 64D540(6) calls, with only score
    # store/PUSH between them: no independent RNG call can intervene.
    draw2=source_original_66951c_then_64d540_scaled_draw(
        original_66d553_rng_owner_pointer=tls.original_tls_record_pointer,
        original_rng_owner_before_66951c=draw1.original_owner_after_source_step,
        original_64d540_reached_signed_argument=6)
    home=draw1.source_scaled_truncate_result if original_first_team_407770_eax_nonzero else 0
    away=draw2.source_scaled_truncate_result if original_second_team_407770_eax_nonzero else 0
    gates=original_four_special_gates
    if (type(gates) is not tuple or len(gates)!=4 or
        any(type(g) is not Original512D80SpecialGate for g in gates)):
        raise Original512D80SourceError("source original 516040/050/060/070 four reached gates required")
    trace=[]
    for index,(g,expected_va) in enumerate(zip(
            gates,(0x516040,0x516050,0x516060,0x516070))):
        if type(g.native_gate_function_va) is not int or g.native_gate_function_va!=expected_va or type(g.original_reached_gate_al_nonzero) is not bool:
            raise Original512D80SourceError("native 516040/50/60/70 order and AL statuses required")
        human1=g.original_reached_first_team_human_al_if_needed
        human2=g.original_reached_second_team_human_al_if_needed
        owner=g.original_reached_registry0_club_pointer_if_needed
        if not g.original_reached_gate_al_nonzero:
            if any(x is not None for x in (human1,human2,owner)):
                raise Original512D80SourceError("unreached special source side inputs supplied")
            continue
        if index<2:
            if type(human1) is not bool or owner is not None or (
                 human1 and human2 is not None) or (
                 not human1 and type(human2) is not bool):
                raise Original512D80SourceError("exact reached 4037B0 first/second manager source branches required")
            if human1:
                home,away=(1,0) if index==0 else (0,1)
                trace.append((0x512DED,0x512E2A)[index])
            elif human2:
                home,away=(0,1) if index==0 else (1,0)
                trace.append((0x512E0A,0x512E47)[index])
        else:
            if human1 is not None or human2 is not None or type(owner) is not int or not 0<owner<=0xffffffff:
                raise Original512D80SourceError("native registry index0+50 team pointer required, not simulated human test")
            if owner==first:
                home,away=(1,0) if index==2 else (0,1)
                trace.append((0x512E77,0x512ED4)[index-2])
            elif owner==second:
                home,away=(0,1) if index==2 else (1,0)
                trace.append((0x512EA4,0x512F03)[index-2])
    return SourceOriginal512D80FallbackScores(
        original_context_pointer,first,second,True,True,
        draw1,draw2,home,away,tuple(trace))


@dataclass(frozen=True)
class SourceOriginal512D80ThroughV38V3CPrefix:
    original_fallback_scores: SourceOriginal512D80FallbackScores
    original_processing_context_after_512d80: bytes
    original_v38_then_v3c_prefix: object
    native_original_callbacks_executed: bool = False
    original_v3c_world_effects_completed: bool = False
    live_game_state_modified: bool = False


def source_original_5130c2_false_through_fallback_v38_v3c_prefix(
    *,
    original_native_match_record_before_v38: bytes,
    original_processing_context_actual_after_512d80_callbacks: bytes,
    **original_512d80_reached_args,
) -> SourceOriginal512D80ThroughV38V3CPrefix:
    """Source v34-false -> 512D80 -> 5112A0 score latch -> 511370 bit0.

    The full native v3c body and any 513570 event walk remain unresolved.
    This only composes a true ZERO-event prefix, and cannot be published
    into a running GameState as a complete original match.
    """
    from original_native_match_v3c_entry import (
        source_original_v38_then_v3c_zero_event_prefix,
    )
    from original_leaguematch_native_process_owners import OriginalLeagueMatchProcessOwnerError
    fallback=source_original_512d80_fallback_random_scores(
        **original_512d80_reached_args)
    # 407770/5160xx callbacks may mutate the processing context and
    # competition/event world; never reuse the earlier context as if none
    # of those original calls ran. Require an INDEPENDENTLY reached
    # post-512D80 context, including both event counters and actual scores.
    context=original_processing_context_actual_after_512d80_callbacks
    if type(context) is not bytes or len(context)<0xd54:
        raise Original512D80SourceError(
            "actual source context AFTER all 512D80 callbacks required")
    if (unpack_from('<I',context,0)[0]!=fallback.original_first_team_pointer or
        unpack_from('<I',context,0x5b0)[0]!=fallback.original_second_team_pointer):
        raise Original512D80SourceError(
            "source team pointers changed after 512D80 callbacks; unresolved original owner effects")
    if (unpack_from('<I',context,0xd4c)[0]!=fallback.original_first_score_context_d4c or
        unpack_from('<I',context,0xd50)[0]!=fallback.original_second_score_context_d50):
        raise Original512D80SourceError(
            "native post-512D80 source score differs from projected RNG/override write")
    if (unpack_from('<I',context,0xd0c)[0]!=0 or
        unpack_from('<I',context,0xd10)[0]!=0):
        raise Original512D80SourceError(
            "original source 513570 v38 event lists nonzero; cannot skip actual event callbacks")
    try:
        prefix=source_original_v38_then_v3c_zero_event_prefix(
            original_native_match_record_before_v38=original_native_match_record_before_v38,
            original_processing_context_after_match=context,
        )
    except OriginalLeagueMatchProcessOwnerError as exc:
        raise Original512D80SourceError(
            "original native v38/v3c world prefix requires authentic source LeagueMatch owner") from exc
    return SourceOriginal512D80ThroughV38V3CPrefix(fallback,context,prefix)
