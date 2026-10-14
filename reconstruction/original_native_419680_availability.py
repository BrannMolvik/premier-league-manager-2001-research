"""Original native 0x419680 post-match player availability from 5127A0.

Canonical private original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Bounded source projection only; original 0x419680 not executed.
The native 5128EA..51292A roster loop invokes 419680 AFTER 4197C0 rows
with the same 615D10 calendar lookup pointer, which may be NULL.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into,unpack_from

from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt


class Original419680SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original419680Reached:
    original_player_at_entry: bytes
    original_calendar_lookup_pointer: int
    # Separate native player image AFTER the original ESI virtual+18
    # competition getter(s), never inferred from the entry copy.
    original_player_after_virtuals: bytes | None = None
    original_competition_v18_eax: int | None = None
    original_second_competition_34: int | None = None
    original_510a20_reached_date_raw: int | None = None
    original_417340_registered_owner_proof: Original417340RegisteredUserReceipt | None = None


@dataclass(frozen=True)
class Original419680AvailabilityReceipt:
    original_player_id: int
    original_player_after: bytes
    original_calendar_lookup_nonnull: bool
    original_league_uefa_source_owner_34_one: bool | None
    original_fa_due_date_checked: bool
    original_417340_eligibility_callback_reached: bool
    original_status_bit1_source_or_branch: bool
    original_419680_native_callback_executed: bool = False
    original_510a20_world_effects_unverified: bool = False
    original_competition_virtual_world_effects_unverified: bool = False
    live_game_state_updated: bool = False


def _u32(value: int | None, name: str) -> int:
    if type(value) is not int or not 0<=value<=0xffffffff:
        raise Original419680SourceError(f"actual original {name} uint32 required")
    return value


def _signed(value: int) -> int:
    return value-0x100000000 if value>=0x80000000 else value


def source_original_419680_availability_from_reached(
    reached: Original419680Reached,
) -> Original419680AvailabilityReceipt:
    """Project exact native 419680..41971C player+14 bit1 OR.

    NULL lookup: tests FA BYTE+13B only, without vtables or date.
    Nonnull: gets competition virtual18. If nonzero, fresh owner+34==1
    selects UEFA BYTE+13E and EARLY RETURN, not FA fallback. Otherwise
    tests FA BYTE+13B and signed DWORD +160<=date from native 510A20.
    If due, 417340 is called but its AL is IGNORED before setting bit1.
    Requires independently source-qualified at-call read-only 417340 proof.
    """
    if not isinstance(reached,Original419680Reached):
        raise Original419680SourceError("typed original reached 419680 call required")
    p=reached.original_player_at_entry
    if type(p) is not bytes or len(p)<0x164:
        raise Original419680SourceError("actual source player through+160 required")
    ptr=_u32(reached.original_calendar_lookup_pointer,"615D10 calendar lookup pointer")
    extras=(reached.original_competition_v18_eax,
            reached.original_second_competition_34,
            reached.original_510a20_reached_date_raw,
            reached.original_417340_registered_owner_proof)
    uefa=None
    due=False
    calls_user=False
    bit1=False
    if ptr==0:
        if reached.original_player_after_virtuals is not None:
            raise Original419680SourceError(
                "NULL original lookup skips virtual player snapshot")
        if any(v is not None for v in extras):
            raise Original419680SourceError("NULL original calendar pointer skips all virtual/date/user callbacks")
        bit1=p[0x13b]>0
    else:
        post=reached.original_player_after_virtuals
        if type(post) is not bytes or post!=p:
            raise Original419680SourceError(
                "independently reached post-virtual player must match original entry")
        v18=_u32(extras[0],"first competition virtual+18 result")
        if v18:
            cat=_u32(extras[1],"second competition owner+34")
            uefa=cat==1
        elif extras[1] is not None:
            raise Original419680SourceError("zero v18 skips second competition+34")
        else:
            uefa=False
        if uefa:
            if extras[2] is not None or extras[3] is not None:
                raise Original419680SourceError("UEFA branch returns before FA date/user callback")
            bit1=p[0x13e]>0
        elif p[0x13b]==0:
            if extras[2] is not None or extras[3] is not None:
                raise Original419680SourceError("zero FA counter skips 510A20/417340")
        else:
            raw=_u32(extras[2],"510A20 reached signed date")
            due=True
            bit1=_signed(unpack_from("<I",p,0x160)[0])<=_signed(raw)
            proof=extras[3]
            if bit1:
                if (not isinstance(proof,Original417340RegisteredUserReceipt)
                        or proof.original_native_player_at_call!=p
                        or proof.original_417340_return_al not in (0,1)
                        or proof.native_callback_executed
                        or proof.live_game_state_updated):
                    raise Original419680SourceError(
                        "due 419680 requires exact at-call original 417340 user predicate")
                calls_user=True
            elif proof is not None:
                raise Original419680SourceError(
                    "not-yet-due FA match skips 417340 registered-user call")
    edited=bytearray(p)
    prior=unpack_from("<I",p,0x14)[0]
    if bit1:
        pack_into("<I",edited,0x14,prior|0x02)
    return Original419680AvailabilityReceipt(
        original_player_id=unpack_from("<H",p,4)[0],
        original_player_after=bytes(edited),
        original_calendar_lookup_nonnull=bool(ptr),
        original_league_uefa_source_owner_34_one=uefa,
        original_fa_due_date_checked=due,
        original_417340_eligibility_callback_reached=calls_user,
        original_status_bit1_source_or_branch=bit1,
        original_510a20_world_effects_unverified=due,
        original_competition_virtual_world_effects_unverified=bool(ptr),
    )
