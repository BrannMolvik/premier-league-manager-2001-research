"""Bounded original 0x606540 registered-human notice constructor SOURCE selector.

Canonical private footballmanager.exe (4,714,541 bytes, SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3),
static x86 606618..606CC1; original game was NOT launched or committed.

Output is a *constructor call plan*, never native allocation, receipt/delivery,
human-visible Inbox, or live GameState mutation. Source 0x606C88 also creates a
SEPARATE 7BD564 wrapper in 947AA8 before 606CCE->60AA20 creates its own
7D7760 player-event object, but neither execution nor ordering is asserted
for a Python runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_605f90_dispatch import (
    Original605F90PreDispatchReceipt, Original606540PreHumanReceipt,
)
from original_native_417340_registered_user_gate import (
    Original417340RegisteredUserReceipt,
)


class Original606540HumanNoticeSourceError(ValueError):
    pass


# Exact native 606CE4/606CF4/606D04 status jump tables, independently
# inspected; status 2 and 3 intentionally enter the same case.
_NATIVE_STATUS_SWITCH_TARGETS = (
    (0x60667E,0x606729,0x6067D6,0x6067D6),  # original 4D1190 != NULL
    (0x606889,0x606939,0x6069E9,0x6069E9),  # 4D1190 NULL / 4D1110 != NULL
    (0x606A64,0x606B3C,0x606C11,0x606C11),  # both source lookup calls NULL
)
# [lookup family][status group 0,1,2/3][subtype2=False/True]
# Original returns a constructed 0x44/0x48 object pointer or a NULL path.
_NATIVE_CONSTRUCTOR_ROUTES = {
    0: (
        ((0x58AD80,0x44), (0x59FEC0,0x44)),
        ((0x58B670,0x44), (0x5A04E0,0x44)),
        ((0x58BEA0,0x44), None),
    ),
    1: (
        ((0x58AA70,0x44), (0x59F8E0,0x44)),
        ((0x58B360,0x44), (0x5A01D0,0x44)),
        ((0x58BB90,0x44), None),
    ),
    2: (
        ((0x58B090,0x48), (0x59FBF0,0x48)),
        ((0x58B980,0x48), (0x5A07F0,0x48)),
        ((0x58C1B0,0x48), None),
    ),
}


@dataclass(frozen=True)
class Original606540HumanNoticeReached:
    original_predispatch: Original605F90PreDispatchReceipt
    original_prehuman: Original606540PreHumanReceipt
    original_registered_417340_owner_proof: Original417340RegisteredUserReceipt
    original_4d1190_lookup_nonnull: bool
    # Native 4D1110 is reached ONLY when 4D1190 returns NULL.
    original_4d1110_lookup_nonnull_if_reached: bool | None = None
    # Independently reached at 606C98, not assumed equal to 60AA20 date.
    original_raw_calendar_date_at_606c98: int = -1


@dataclass(frozen=True)
class Original606540HumanNoticeSourcePlan:
    original_player_id: int
    original_descriptor_subtype: int
    original_descriptor_status: int
    original_lookup_family: int
    original_native_jump_table_address: int
    original_native_status_case_address: int
    original_selected_constructor_address: int
    original_constructor_object_size: int
    original_native_human_user_pointer: int
    original_notice_wrapper_date_raw_u32: int
    original_notice_flags_or_mask: int = 6
    original_notice_envelope_vtable: int = 0x7BD564
    original_notice_envelope_size: int = 12
    original_pending_queue_address: int = 0x947AA8
    original_following_player_event_handler: int = 0x60AA20
    original_native_constructor_executed: bool = False
    original_notice_object_allocated: bool = False
    original_notice_envelope_allocated: bool = False
    original_947aa8_pending_queue_changed: bool = False
    original_notice_delivered: bool = False
    live_game_state_updated: bool = False


def source_original_606540_human_notice_plan(
    reached: Original606540HumanNoticeReached,
) -> Original606540HumanNoticeSourcePlan:
    """Source 606618 human branch: 4D1190 -> optionally 4D1110 -> native
    notice constructor/status dispatch -> 7BD564 wrapper -> 613EC0 -> 60AA20.

    Requires an actual reached source-qualified registered human proof; native
    virtual/lookups remain separately supplied *observations* rather than
    invented club identities. A native subtype2+status2/3 case jumps to the
    wrapper without a new constructed EDI pointer, so it is UNQUALIFIED here
    rather than assuming NULL or a safe fallback.
    """
    if not isinstance(reached,Original606540HumanNoticeReached):
        raise Original606540HumanNoticeSourceError("typed native 606540 human stage required")
    p=reached.original_predispatch
    h=reached.original_prehuman
    owner=reached.original_registered_417340_owner_proof
    if (not isinstance(p,Original605F90PreDispatchReceipt) or
            p.original_native_handler_executed or p.live_game_state_updated or
            p.original_event_delivery_verified or
            p.original_handler_choice.original_selected_handler_address != 0x606540):
        raise Original606540HumanNoticeSourceError("source-selected original 606540 predispatch required")
    if (not isinstance(h,Original606540PreHumanReceipt) or
            h.original_player_id != p.original_player_id or
            h.original_subtype != p.original_subtype or
            h.original_event_pending_or_delivered or h.live_game_state_updated or
            not h.original_handler_417340_callback_outstanding or
            not h.original_60aa20_descriptor_schedule_callback_outstanding):
        raise Original606540HumanNoticeSourceError("source-matching original prehuman status required")
    before=p.original_descriptor_at_subhandler_entry
    after=h.original_source_descriptor_before_417340
    if type(before) is not bytes or type(after) is not bytes or len(before)!=12 or len(after)!=12:
        raise Original606540HumanNoticeSourceError("exact 12-byte native descriptor required")
    if (after[:5]!=before[:5] or after[6:]!=before[6:] or
            unpack_from("<I",after,8)[0]!=p.original_player_id):
        raise Original606540HumanNoticeSourceError("606540 prehuman may alter only descriptor+5")
    subtype=after[4]
    status=after[5]
    if subtype not in (0,1,2) or subtype!=p.original_subtype or status not in (0,1,2,3):
        raise Original606540HumanNoticeSourceError("source subtype/status out of native jump tables")
    if (not isinstance(owner,Original417340RegisteredUserReceipt) or
            owner.original_native_player_id != p.original_player_id or
            type(owner.original_417340_return_al) is not int or owner.original_417340_return_al != 1 or
            owner.original_matching_user_pointer is None or
            type(owner.original_matching_user_pointer) is not int or not 0<owner.original_matching_user_pointer<=0xffffffff or
            owner.native_callback_executed or owner.live_game_state_updated or
            type(owner.original_native_player_at_call) is not bytes or
            len(owner.original_native_player_at_call)<0x250 or
            unpack_from("<H",owner.original_native_player_at_call,4)[0]!=p.original_player_id or
            unpack_from("<I",owner.original_native_player_at_call,0x24c)[0]!=p.original_descriptor_pointer):
        raise Original606540HumanNoticeSourceError("reached original 417340 registered-user AL=1 proof required")
    first=reached.original_4d1190_lookup_nonnull
    second=reached.original_4d1110_lookup_nonnull_if_reached
    if type(first) is not bool:
        raise Original606540HumanNoticeSourceError("reached 4D1190 null/non-null outcome required")
    if first:
        if second is not None:
            raise Original606540HumanNoticeSourceError("4D1110 is skipped when 4D1190 is nonnull")
        family=0
    else:
        if type(second) is not bool:
            raise Original606540HumanNoticeSourceError("4D1110 outcome required after NULL 4D1190")
        family=1 if second else 2
    raw_day=reached.original_raw_calendar_date_at_606c98
    if type(raw_day) is not int or not 0<=raw_day<=0xffffffff:
        raise Original606540HumanNoticeSourceError("separately reached raw 606C98 date DWORD required")
    choice=_NATIVE_CONSTRUCTOR_ROUTES[family][min(status,2)][int(subtype==2)]
    if choice is None:
        raise Original606540HumanNoticeSourceError(
            "subtype2 status2/3 branches to wrapper without a qualified notice constructor")
    return Original606540HumanNoticeSourcePlan(
        p.original_player_id,subtype,status,family,
        (0x606CE4,0x606CF4,0x606D04)[family],
        _NATIVE_STATUS_SWITCH_TARGETS[family][status],
        choice[0],choice[1],
        owner.original_matching_user_pointer,raw_day,
    )
