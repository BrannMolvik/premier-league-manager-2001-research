"""Native original 0x419490 FA/UEFA suspension-return producer.

Original private footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Read-only source reached memory+virtual-result projection, never invokes
native virtuals, original allocators, GameState, or mailbox delivery.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into, unpack_from


class Original419490SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original419490ReachedCalls:
    original_initial_511170_eax: int
    original_secondary_511170_eax: int | None = None
    original_4f8e40_al: int | None = None
    original_competition_v18_eax: int | None = None
    original_competition_34: int | None = None
    original_417340_al: int | None = None


@dataclass(frozen=True)
class Original419490ReturnEventReceipt:
    original_player_id: int
    original_club_context_index_signed: int
    original_source_native_player_after: bytes
    original_uefa_counter_after: int
    original_fa_counter_after: int
    original_event_class_if_allocation_succeeds: str | None
    original_constructor_va_if_allocation_succeeds: int | None
    original_pending_event_queue_va: int = 0x947AA8
    original_recipient_manager_key_resolved: bool = False
    original_event_allocated: bool = False
    original_native_613ec0_enqueued: bool = False
    live_game_state_updated: bool = False


def _reached_u32(value: int | None, name: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise Original419490SourceError(f"actual reached {name} uint32 required")
    return value


def _reached_byte(value: int | None, name: str) -> int:
    return _reached_u32(value,name)&0xff


def _receipt(player: bytes, name: str | None = None, ctor: int | None = None
             ) -> Original419490ReturnEventReceipt:
    return Original419490ReturnEventReceipt(
        original_player_id=unpack_from("<H",player,4)[0],
        original_club_context_index_signed=unpack_from("<h",player,0x10)[0],
        original_source_native_player_after=player,
        original_uefa_counter_after=player[0x13e],
        original_fa_counter_after=player[0x13b],
        original_event_class_if_allocation_succeeds=name,
        original_constructor_va_if_allocation_succeeds=ctor,
    )


def source_original_419490_suspension_return_from_reached(
    *, original_player_at_entry: bytes,
    original_match_at_entry: bytes,
    reached: Original419490ReachedCalls,
    original_date_9847fc: int,
) -> Original419490ReturnEventReceipt:
    """Source 0x419490..0x41967F branches, mutating only projected player bytes.

    Initial 511170; nonzero invokes second 511170 + 4F8E40 and may exit.
    Otherwise original player+14 bit1 clears. Competition owner virtual18
    then +34==1 selects UEFA byte+13E; otherwise FA byte+13B with
    signed schedule DWORD+160 <= signed global date 9847FC.
    Zero-reaching countdown calls 417340. On a true return, original tries
    0x48 and 0x0C allocations, constructs two distinct event classes,
    and queues via 613EC0. This projection records only potential type.
    """
    player=original_player_at_entry
    match=original_match_at_entry
    if type(player) is not bytes or len(player)<0x164:
        raise Original419490SourceError("original DBRPlayer through +160 required")
    if type(match) is not bytes or len(match)<0x50:
        raise Original419490SourceError("original LeagueMatch through +4C required")
    if not unpack_from("<I",match,0x4c)[0]:
        raise Original419490SourceError("original match+4C competition owner must be nonnull")
    if not isinstance(reached,Original419490ReachedCalls):
        raise Original419490SourceError("typed actual reached callback results required")
    if type(original_date_9847fc) is not int or not 0<=original_date_9847fc<=0xffffffff:
        raise Original419490SourceError("actual original global date uint32 required")
    initial=_reached_u32(reached.original_initial_511170_eax,"initial 511170")
    others=(reached.original_secondary_511170_eax,reached.original_4f8e40_al,
            reached.original_competition_v18_eax,reached.original_competition_34,
            reached.original_417340_al)
    if initial:
        _reached_u32(others[0],"secondary 511170")
        if _reached_byte(others[1],"4F8E40"):
            if any(v is not None for v in others[2:]):
                raise Original419490SourceError("source early exit skips downstream competition callbacks")
            return _receipt(player)
    elif others[0] is not None or others[1] is not None:
        raise Original419490SourceError("zero first 511170 skips secondary callback")
    v18=_reached_u32(reached.original_competition_v18_eax,"competition virtual18")
    if v18:
        is_uefa=_reached_u32(reached.original_competition_34,"competition+34")==1
    else:
        is_uefa=False
        if reached.original_competition_34 is not None:
            raise Original419490SourceError("zero competition virtual18 skips competition+34")
    edited=bytearray(player)
    pack_into("<I",edited,0x14,unpack_from("<I",edited,0x14)[0]&0xfffffffd)
    candidate=None
    constructor=None
    if is_uefa:
        remain=edited[0x13e]
        if remain:
            remain-=1
            edited[0x13e]=remain
            if remain==0:
                if _reached_byte(reached.original_417340_al,"UEFA 417340"):
                    candidate="EAMReturnFromUEFASuspension"
                    constructor=0x5853F0
            elif reached.original_417340_al is not None:
                raise Original419490SourceError("UEFA countdown nonzero skips 417340")
        elif reached.original_417340_al is not None:
            raise Original419490SourceError("UEFA countdown zero skips 417340")
    else:
        remain=edited[0x13b]
        scheduled=unpack_from("<i",edited,0x160)[0]
        date=original_date_9847fc
        if date>=0x80000000: date-=0x100000000
        if remain and scheduled<=date:
            remain-=1
            edited[0x13b]=remain
            if remain==0:
                if _reached_byte(reached.original_417340_al,"FA 417340"):
                    candidate="EAMReturnFromFASuspension"
                    constructor=0x585000
            elif reached.original_417340_al is not None:
                raise Original419490SourceError("FA countdown nonzero skips 417340")
        elif reached.original_417340_al is not None:
            raise Original419490SourceError("FA countdown not due/zero skips 417340")
    return _receipt(bytes(edited),candidate,constructor)
