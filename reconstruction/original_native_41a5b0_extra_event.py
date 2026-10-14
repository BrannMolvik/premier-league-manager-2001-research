"""Original row+0x4A optional 0x41A5B0: source conditional player event.

Canonical private original footballmanager.exe SHA-256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Read-only branch decision: does not allocate 12-byte 605F70 object, write
native player+24C, invoke 605F90/417380, mutate GameState or send mail.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from struct import unpack_from

from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt
from original_native_405080_available_roster import Original405080AvailabilityReceipt


class Original41A5B0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original41A5B0Reached:
    """Original player snapshot MUST be after 4197C0's mutable callbacks."""
    original_player_after_row_at_call: bytes
    original_native_row_player_pointer: int
    original_registered_417340_owner_proof: Original417340RegisteredUserReceipt
    # Only if 417340 AL is zero, 417270 -> 405080 is reached.
    original_405080_current_club_pointer: int | None = None
    original_405080_eligible_count: int | None = None
    original_822228_reached_threshold_float: float | None = None
    original_405080_source_proof: Original405080AvailabilityReceipt | None = None
    # Only if allocation branch reached, original reads GLOBAL threshold.
    original_global_821814_player77_threshold: int | None = None


@dataclass(frozen=True)
class Original41A5B0ExtraEventReceipt:
    original_player_id: int
    original_native_row_player_pointer: int
    original_player_after_row_at_call: bytes
    original_registered_human_al: int
    original_405080_eligible_count_reached: int | None
    original_822228_source_threshold_reached: float | None
    original_417ff0_low_status_bit_checked: bool
    original_417ff0_return_al: int | None
    original_would_allocate_605f70_and_store_player24c: bool
    original_605f90_subtype_if_allocated: int | None
    source_branch_complete_without_world_effects: bool
    original_native_callback_executed: bool = False
    live_game_state_updated: bool = False


def source_original_41a5b0_optional_extra_from_reached(
    reached: Original41A5B0Reached,
) -> Original41A5B0ExtraEventReceipt:
    """Classify original 41A5C9..41A66C, refusing unqualified world effects.

    417340 tests manager ownership. If AL=0: 417270 selects current club,
    then 405080 counts eligible players, fild/fcomp float GLOBAL 822228
    source literal 14.0; count <14 skips next stage. If AL=1, that
    original count getter is NOT called. Only after reaching 417FF0 does
    player+14 low bit0 block new event allocation.

    Reached allocation branch uses original 821814 signed32 threshold vs
    unsigned BYTE player+77 and chooses 605F90 subtype 1 if lower,
    otherwise subtype 0. Original 605F70 allocation, player+24C write,
    subsequent 605F90 owner/registered human effects are unimplemented.
    """
    if not isinstance(reached,Original41A5B0Reached):
        raise Original41A5B0SourceError("typed actual original 41A5B0 call required")
    pointer=reached.original_native_row_player_pointer
    if type(pointer) is not int or not 0<pointer<=0xffffffff:
        raise Original41A5B0SourceError(
            "actual original 4197C0 row player pointer required")
    p=reached.original_player_after_row_at_call
    if type(p) is not bytes or len(p)<0x78:
        raise Original41A5B0SourceError(
            "actual original post-4197C0 player through +77 required")
    proof=reached.original_registered_417340_owner_proof
    if (not isinstance(proof,Original417340RegisteredUserReceipt)
        or proof.native_callback_executed or proof.live_game_state_updated
        or proof.original_native_player_at_call!=p
        or proof.original_417340_return_al not in (0,1)):
        raise Original41A5B0SourceError(
            "actual 417340 registered-human proof must match post-row player bytes")
    registered=proof.original_417340_return_al
    if registered:
        if (reached.original_405080_current_club_pointer is not None
            or reached.original_405080_eligible_count is not None
            or reached.original_822228_reached_threshold_float is not None
            or reached.original_405080_source_proof is not None):
            raise Original41A5B0SourceError(
                "original registered-human path skips 417270/405080 count")
        can_continue=True
        count=None
    else:
        source_ptr=reached.original_405080_current_club_pointer
        count=reached.original_405080_eligible_count
        float_threshold=reached.original_822228_reached_threshold_float
        count_proof=reached.original_405080_source_proof
        if count_proof is not None:
            if (not isinstance(count_proof, Original405080AvailabilityReceipt)
                or count_proof.original_native_callback_executed
                or count_proof.live_game_state_updated
                or count_proof.original_team_pointer!=proof.original_source_club_pointer):
                raise Original41A5B0SourceError("forged 405080 source count/team owner proof")
            if count is not None and count!=count_proof.original_405080_eligible_count:
                raise Original41A5B0SourceError("405080 reached count disagrees with native source")
            count=count_proof.original_405080_eligible_count
            current_pid=unpack_from("<H",p,4)[0]
            if current_pid in count_proof.original_roster_ids:
                flags_by_id=dict(count_proof.original_player_status_14_by_id)
                if flags_by_id.get(current_pid)!=unpack_from("<I",p,0x14)[0]:
                    raise Original41A5B0SourceError(
                        "post-row player+14 flags differ from reached 405080 source pool")
        if (type(source_ptr) is not int
            or source_ptr!=proof.original_source_club_pointer
            or type(count) is not int or not 0<=count<=40
            or type(float_threshold) is not float
            or not isfinite(float_threshold)):
            raise Original41A5B0SourceError(
                "actual original 417270 club pointer and 405080 count required")
        # Native image initially stores 14.0 at 822228; this is a
        # mutable .data global. Require the ACTUAL reached float and
        # test the source FPU C0 less-than branch against that value.
        can_continue=count>=float_threshold
    bit0=None
    block=False
    if can_continue:
        bit0=p[0x14]&1
        block=bool(bit0)
    allocate=can_continue and not block
    threshold=reached.original_global_821814_player77_threshold
    subtype=None
    if allocate:
        if type(threshold) is not int or not -0x80000000<=threshold<=0x7fffffff:
            raise Original41A5B0SourceError(
                "actual original reached 821814 signed32 player77 threshold required")
        subtype=1 if p[0x77]<threshold else 0
    elif threshold is not None:
        raise Original41A5B0SourceError(
            "source original allocation/global 821814 threshold skipped")
    return Original41A5B0ExtraEventReceipt(
        original_player_id=unpack_from("<H",p,4)[0],
        original_native_row_player_pointer=pointer,
        original_player_after_row_at_call=p,
        original_registered_human_al=registered,
        original_405080_eligible_count_reached=count,
        original_822228_source_threshold_reached=(
            None if registered else float_threshold),
        original_417ff0_low_status_bit_checked=can_continue,
        original_417ff0_return_al=bit0,
        original_would_allocate_605f70_and_store_player24c=allocate,
        original_605f90_subtype_if_allocated=subtype,
        source_branch_complete_without_world_effects=not allocate,
    )
