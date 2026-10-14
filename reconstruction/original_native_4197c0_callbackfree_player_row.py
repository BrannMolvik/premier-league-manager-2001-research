"""Original 0x4197C0 per-row player-state callback-free bounded journey.

Native source /mnt/data/footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Actual original 0x5128B2 pushes match, opponent, arg2, arg1 then calls
4197C0; competition virtual+18 is called TWICE; 5112E0 wraps owner
virtual+30 & 0xFF on the non-UEFA path. This models ONLY source-qualified
player bytes on a path where no player/world mutating auxiliary callbacks
are reached, never assumes general native match-world equivalence.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_native_5127a0_row_incident_source import (
    Original5127A0RowCall,
    source_original_41a490_accumulator_at_callback_boundary,
)
from original_native_41a250_uefa_producer import (
    Original41A250Reached,
    source_original_41a250_uefa_incident_from_reached,
)


class Original4197C0SafeRowError(ValueError):
    pass


@dataclass(frozen=True)
class Original4197C0SafeRowReached:
    original_row: Original5127A0RowCall
    original_player_at_entry: bytes
    original_player_after_competition_callbacks: bytes
    original_match_pointer: int
    original_match_record: bytes
    original_competition_owner_pointer: int
    # Original competition +18 VIRTUAL results are distinct calls, not cached.
    first_competition_v18_eax: int
    first_reached_category_34: int | None
    second_competition_v18_eax: int
    second_reached_category_34: int | None
    third_reached_uefa_owner_context_14: int | None
    original_5112e0_v30_eax: int | None


@dataclass(frozen=True)
class Original4197C0SafeRowReceipt:
    original_player_id: int
    original_player_after: bytes
    source_branch: str
    original_first_competition_v18_eax: int
    original_second_competition_v18_eax: int
    original_5112e0_masked_al: int | None
    source_41a490_accumulator_reached: bool
    source_41a250_uefa_reached: bool
    source_419916_discipline_continuation_reached: bool
    external_competition_virtual_world_effects_unverified: bool
    native_4197c0_executed: bool = False
    live_game_state_updated: bool = False


def _u32(v: int | None, name: str, *, allow_zero: bool = True) -> int:
    if type(v) is not int or not 0<=v<=0xffffffff or (not allow_zero and not v):
        raise Original4197C0SafeRowError(f"actual reached original {name} uint32 required")
    return v


def source_original_4197c0_callbackfree_player_row(
    reached: Original4197C0SafeRowReached,
) -> Original4197C0SafeRowReceipt:
    """Project only source rows with no outstanding native child callbacks.

    Arg2=0 prevents 4085D0 and FA+13B RNG incident; row+4A flag zero
    prevents the NEXT caller from later invoking 41A5B0.
    Repeated competition callbacks can mutate world, so require a distinct
    ACTUALLY REACHED post-competition player snapshot IDENTICAL to entry;
    this does not by itself prove external competition-world side effects.
    """
    if not isinstance(reached,Original4197C0SafeRowReached):
        raise Original4197C0SafeRowError("typed original reached 4197C0 row required")
    row=reached.original_row
    if (not isinstance(row,Original5127A0RowCall)
            or type(row.source_4197c0_arg1) is not int
            or not 0<=row.source_4197c0_arg1<=255
            or type(row.source_4197c0_arg2) is not int
            or row.source_4197c0_arg2!=0
            or row.source_41a5b0_called_after_row
            or row.source_4197c0_arg3!=row.source_opponent_team_pointer):
        raise Original4197C0SafeRowError(
            "source arg2=0, valid arg1/opponent and no extra 41A5B0 required")
    p=reached.original_player_at_entry
    post=reached.original_player_after_competition_callbacks
    if (type(p) is not bytes or type(post) is not bytes
            or len(p)<0x164 or post!=p):
        raise Original4197C0SafeRowError(
            "separately reached full native player before/after competition must match")
    _u32(row.source_player_pointer,"source player pointer",allow_zero=False)
    _u32(reached.original_match_pointer,"match pointer",allow_zero=False)
    m=reached.original_match_record
    if type(m) is not bytes or len(m)<0x50:
        raise Original4197C0SafeRowError("actually reached match+4C source owner required")
    _u32(reached.original_competition_owner_pointer,"competition owner",allow_zero=False)
    if unpack_from("<I",m,0x4c)[0]!=reached.original_competition_owner_pointer:
        raise Original4197C0SafeRowError("match+4C original competition root pointer mismatch")
    first=_u32(reached.first_competition_v18_eax,"first virtual+18 result")
    second=_u32(reached.second_competition_v18_eax,"second virtual+18 result")
    first_category=reached.first_reached_category_34
    second_category=reached.second_reached_category_34
    if (first==0 and first_category is not None) or (
        first!=0 and (type(first_category) is not int or
                       not 0<=first_category<=0xffffffff)):
        raise Original4197C0SafeRowError("first competition+34 getter reachability mismatch")
    if (second==0 and second_category is not None) or (
        second!=0 and (type(second_category) is not int or
                        not 0<=second_category<=0xffffffff)):
        raise Original4197C0SafeRowError("second competition+34 getter reachability mismatch")
    # Native 41982E optional 417EE0 runs only if both incident bytes zero
    # and original first +18/+34 was not the UEFA shortcut.
    if (row.source_4197c0_arg1==0 and p[0x13a]!=0 and
            not (first!=0 and first_category==1)):
        raise Original4197C0SafeRowError(
            "native 419840 early 417EE0 not part of callback-free source subset")
    uefa=second!=0 and second_category==1
    buf=bytearray(post)
    if uefa:
        _u32(reached.third_reached_uefa_owner_context_14,
             "third UEFA competition+14 owner context",allow_zero=False)
        if reached.original_5112e0_v30_eax is not None:
            raise Original4197C0SafeRowError("UEFA branch returns before 5112E0")
        if ((p[0x13d]+row.source_4197c0_arg1)&0xff)>2:
            raise Original4197C0SafeRowError(
                "original 41A250 would reach its 417340/event callback")
        projection=source_original_41a250_uefa_incident_from_reached(
            Original41A250Reached(
                original_row=row,original_native_player_at_entry=post,
                original_41a250_reached=True,
            )
        )
        if not projection.source_callback_free_leaf_complete:
            raise Original4197C0SafeRowError(
                "original 41A250 reaches unimplemented 417340 or event path")
        buf=bytearray(projection.original_source_player_at_second_gate_or_return)
        branch="UEFA_41A250"
        accumulator=False
        continuation=False
        v30=None
    else:
        if reached.third_reached_uefa_owner_context_14 is not None:
            raise Original4197C0SafeRowError("non-UEFA branch cannot fetch third +14")
        v30=_u32(reached.original_5112e0_v30_eax,"5112E0 returned masked AL")
        # Original 5112E0 itself ANDs EAX with 0xFF before returning.
        # Thus a reached return outside BYTE range is forged/incorrect.
        if v30>255:
            raise Original4197C0SafeRowError(
                "original 5112E0 already masked to 8-bit return")
        accumulator=bool(v30)
        if accumulator:
            acc=source_original_41a490_accumulator_at_callback_boundary(
                original_reached_row=row,
                original_player_at_41a490=bytes(buf),
                original_41a490_reached=True,
            )
            if acc.native_417340_callback_outstanding:
                raise Original4197C0SafeRowError(
                    "original 41A490 would invoke 417340: not a callback-free leaf")
            buf=bytearray(acc.projected_player_record_at_417340_or_return)
        continuation=row.source_4197c0_arg1!=0
        if continuation:
            # Original 419932 runs before 139/13A increments, and native
            # IDIV by 13 tests PRE-increment 139 % 13 == 12.
            if p[0x139]%13==12:
                raise Original4197C0SafeRowError(
                    "original 419938 card threshold/41A060/FA counter callback reached")
            next_139=(p[0x139]+row.source_4197c0_arg1)&0xff
            next_13a=(p[0x13a]+row.source_4197c0_arg1)&0xff
            if next_13a>=5:
                raise Original4197C0SafeRowError(
                    "original 419992 13A carry/4199E0/FA counter callback reached")
            buf[0x13c]=0
            buf[0x139]=next_139
            buf[0x13a]=next_13a
        branch="NON_UEFA_41A490" if accumulator else "NON_UEFA_NO_41A490"
    return Original4197C0SafeRowReceipt(
        original_player_id=unpack_from("<H",p,4)[0],
        original_player_after=bytes(buf),
        source_branch=branch,
        original_first_competition_v18_eax=first,
        original_second_competition_v18_eax=second,
        original_5112e0_masked_al=v30,
        source_41a490_accumulator_reached=accumulator,
        source_41a250_uefa_reached=uefa,
        source_419916_discipline_continuation_reached=continuation,
        external_competition_virtual_world_effects_unverified=True,
    )
