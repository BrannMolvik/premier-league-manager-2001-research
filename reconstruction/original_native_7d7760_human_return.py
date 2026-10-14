"""Original 7D7760 due event 5D7B40: human return notice BEFORE cleanup.

Static original private PE SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Source 5D7B40, 5D8108/18/28 jump tables, 5D8094..5D80E2.
The function returns a SOURCE candidate only: no native allocation,
no 947AA8 insertion, no user+6B4 append, no GUI/Inbox or GameState mutation.
This is the 7D7760 recovery family, NOT 606540 injury-onset notices.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_418ad0_cleanup import (
    Original418AD0CleanupReceipt, source_original_418ad0_cleanup,
)


class Original7D7760ReturnSourceError(ValueError):
    pass


# [family: 31 if 4D1190 nonnull; 30 if only 4D1110 nonnull;
#           2 if both null] x [native event+0x10 severity 0..3].
# constructor, FINAL class vtable, +0x18 title, +0x1C body,
# original EnglishEAM IDX title ordinal, three body STR IDs.
# Native status3 constructors temporarily set a DIFFERENT vtable, then
# 5D7D51, 5D7F04, 5D8082 overwrite it to these final values.
ORIGINAL_RECOVERY_NOTICE_ROUTES = {
    31: (
        (0x59D6B0,0x7D3F8C,0x59D740,0x59D7C0,2328,(1411,1411,1411)),
        (0x59DFF0,0x7D4088,0x59E080,0x59E100,2343,(1417,1417,1417)),
        (0x59E970,0x7D4184,0x59EA00,0x59EA80,2358,(1423,1423,1423)),
        (0x59F2B0,0x7CB37C,0x59F340,0x59F3C0,2373,(1429,1429,1429)),
    ),
    30: (
        (0x59D3A0,0x7D3F38,0x59D430,0x59D4B0,2323,(1408,1409,1409)),
        (0x59DCE0,0x7D4034,0x59DD70,0x59DDF0,2338,(1415,1415,1415)),
        (0x59E660,0x7D4130,0x59E6F0,0x59E770,2353,(1421,1421,1421)),
        (0x59EFA0,0x7CB424,0x59F030,0x59F0B0,2368,(1427,1427,1427)),
    ),
    2: (
        (0x59D9C0,0x7D3FE0,0x59DA60,0x59DAE0,2333,(1413,1413,1413)),
        (0x59E340,0x7D40DC,0x59E3E0,0x59E460,2348,(1419,1419,1419)),
        (0x59EC80,0x7D41D8,0x59ED20,0x59EDA0,2363,(1425,1425,1425)),
        (0x59F5C0,0x7CB2D4,0x59F660,0x59F6E0,2378,(1431,1431,1431)),
    ),
}


def _u32(v, name):
    if type(v) is not int or not 0 <= v <= 0xFFFFFFFF:
        raise Original7D7760ReturnSourceError("Reached original " + name + " DWORD required")
    return v


def _signed(v):
    return v - 0x100000000 if v >= 0x80000000 else v


@dataclass(frozen=True)
class Original7D7760HumanReturnReached:
    """Actual source inputs, NOT assumed successful original callbacks."""

    original_native_event_bytes: bytes
    original_player_id_payload_bytes: bytes
    original_player_before_due: bytes
    original_native_scanner_target_date_raw: int
    original_native_9847fc_current_day_at_creation: int
    original_4139e0_human_club_lookup_al: int
    original_4d1190_lookup_nonnull_if_reached: bool | None = None
    original_4d1110_lookup_nonnull_if_reached: bool | None = None
    original_417270_source_club_record_if_reached: bytes | None = None


@dataclass(frozen=True)
class Original7D7760HumanReturnSourceReceipt:
    original_player_id: int
    original_source_due_day_signed: int
    original_source_current_day_signed: int
    original_registered_human: bool
    original_selected_family: int | None
    original_event_status: int
    original_selected_constructor_if_human: int | None
    original_final_notice_vtable_if_human: int | None
    original_notice_title_callback_if_human: int | None
    original_notice_body_callback_if_human: int | None
    original_eamail_title_idx_if_human: int | None
    original_eamail_body_ids_if_human: tuple[int,int,int] | None
    original_recipient_manager_key_if_human: int | None
    original_7bd564_notice_wrapper_date_if_human: int | None
    original_player_source_cleanup: Original418AD0CleanupReceipt
    original_947aa8_human_event_insert_executed: bool = False
    original_native_418ad0_executed: bool = False
    original_user_inbox_delivered: bool = False
    live_game_state_updated: bool = False


def source_original_7d7760_human_return_from_reached(
    reached: Original7D7760HumanReturnReached,
) -> Original7D7760HumanReturnSourceReceipt:
    """One original 60AA20-produced count1 7D7760 due player event.

    Source valid for count1 only. Native 5D7B40 can loop multiple IDs, so
    larger original events require a separate complete ordered-owner proof.
    The original notification, if constructed, is posted to global 947AA8
    BEFORE the original 418AD0 descriptor/bit cleanup, not delivered now.
    """
    if type(reached) is not Original7D7760HumanReturnReached:
        raise Original7D7760ReturnSourceError("Reached original typed 7D7760 source required")
    e = reached.original_native_event_bytes
    payload = reached.original_player_id_payload_bytes
    if type(e) is not bytes or len(e) != 20:
        raise Original7D7760ReturnSourceError("Exact original 20-byte event required")
    vtable,due,count,idptr = unpack_from("<IIII",e)
    status=e[0x10]
    if (vtable != 0x7D7760 or count != 1 or idptr == 0
            or status not in range(4) or e[0x11:] != b"\x00\x00\x00"):
        raise Original7D7760ReturnSourceError("Original 7D7760 owner/count/status unqualified")
    if type(payload) is not bytes or len(payload) != 4:
        raise Original7D7760ReturnSourceError("Actual original allocated player ID DWORD required")
    player_id = unpack_from("<I",payload)[0]
    if not 0 <= player_id <= 0xFFFF:
        raise Original7D7760ReturnSourceError("Source player ID must fit original unsigned short")
    target=_u32(reached.original_native_scanner_target_date_raw,"613EE0 target day")
    creation=_u32(reached.original_native_9847fc_current_day_at_creation,"9847FC creation day")
    if _signed(due)>_signed(target):
        raise Original7D7760ReturnSourceError("Native signed future event cannot return player")
    player=reached.original_player_before_due
    if (type(player) is not bytes or len(player)<0x250
            or unpack_from("<H",player,4)[0]!=player_id
            or unpack_from("<I",player,0x24c)[0]==0
            or unpack_from("<I",player,0x14)[0]&1==0):
        raise Original7D7760ReturnSourceError("Reached injured player/descriptor identity required")
    owner=reached.original_4139e0_human_club_lookup_al
    if type(owner) is not int or owner not in (0,1):
        raise Original7D7760ReturnSourceError("Reached original 4139E0 AL 0 or 1 required")
    first=reached.original_4d1190_lookup_nonnull_if_reached
    second=reached.original_4d1110_lookup_nonnull_if_reached
    club=reached.original_417270_source_club_record_if_reached
    family=None; manager_key=None; choice=None
    if owner:
        if type(first) is not bool:
            raise Original7D7760ReturnSourceError("Human original 4D1190 result required")
        if first:
            if second is not None:
                raise Original7D7760ReturnSourceError("4D1110 skipped on 4D1190 success")
            family=31
        else:
            if type(second) is not bool:
                raise Original7D7760ReturnSourceError("Human original later 4D1110 result required")
            family=30 if second else 2
        if type(club) is not bytes or len(club)<0x44:
            raise Original7D7760ReturnSourceError("Human original 417270 club+40 required")
        manager_key=unpack_from("<I",club,0x40)[0]
        choice=ORIGINAL_RECOVERY_NOTICE_ROUTES[family][status]
    elif first is not None or second is not None or club is not None:
        raise Original7D7760ReturnSourceError("AI skips human recovery lookup/club constructor")
    cleanup=source_original_418ad0_cleanup(player_id=player_id,player_before=player)
    return Original7D7760HumanReturnSourceReceipt(
        player_id,_signed(due),_signed(creation),bool(owner),family,status,
        None if choice is None else choice[0],
        None if choice is None else choice[1],
        None if choice is None else choice[2],
        None if choice is None else choice[3],
        None if choice is None else choice[4],
        None if choice is None else choice[5],
        manager_key,creation if owner else None,cleanup,
    )
