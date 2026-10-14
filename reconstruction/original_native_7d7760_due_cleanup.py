"""Original 7D7760 queued player event -> due dispatch -> 418AD0 cleanup.

Source: private canonical footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Native 613EE0 calls vtable+0x10 for due events. Vtable 7D7760+0x10
is 5D7B40; on NONHUMAN 4139E0 AL=0, 5D7BAA skips notifications
and 5D80E2 calls 418AD0, which releases player+24C then clears bit0
at player+14. This is an immutable source projection, not native execution,
successful allocation/free, Inbox delivery, world save or played match.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from,pack_into

from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt
from original_native_60aa20_pending_event import Original60AA20NonhumanReceipt


class Original7D7760DueSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original7D7760DueNonhumanReached:
    """A single independently reached original queue element and handler path.

    Does NOT imply 613EE0 processed the entire queue, that the original
    native binary executed or that a user-visible notice was delivered.
    """
    original_source_producer: Original60AA20NonhumanReceipt
    original_613ee0_queue_node_pointer: int
    original_613ee0_queue_node_bytes: bytes
    original_native_event_object_pointer: int
    original_native_event_object_bytes: bytes
    original_native_player_id_allocation_pointer: int
    original_native_player_id_allocation_bytes: bytes
    original_613ee0_target_day_raw_dword: int
    original_player_before_due_handler: bytes
    original_5d7b40_4139e0_manager_proof: Original417340RegisteredUserReceipt


@dataclass(frozen=True)
class Original7D7760DueCleanupReceipt:
    original_player_id: int
    original_event_due_signed32: int
    original_target_day_signed32: int
    original_7d7760_dispatch_handler: int
    original_5d7b40_nonhuman_skips_notification: bool
    original_player_24c_descriptor_pointer_before: int
    original_418ad0_calls_686fe3_if_nonnull: bool
    original_player_after_source_cleanup: bytes
    original_original_event_queue_mutated: bool = False
    original_native_event_handler_executed: bool = False
    original_player_heap_freed: bool = False
    original_notice_delivered: bool = False
    live_game_state_updated: bool = False


def _u32(x: int, name: str) -> int:
    if type(x) is not int or not 0<=x<=0xffffffff:
        raise Original7D7760DueSourceError(f"actual native {name} DWORD required")
    return x


def _signed32(raw: int) -> int:
    return raw-0x100000000 if raw>=0x80000000 else raw


def source_original_7d7760_due_nonhuman_cleanup(
    reached: Original7D7760DueNonhumanReached,
) -> Original7D7760DueCleanupReceipt:
    """Source 613EE0 due signed comparison -> vtable+10 -> 5D7B40.

    5D7B40 original status player list ID uses record-count 1, then
    4139E0 manager gate. With nonhuman AL=0, it jumps to 5D80CB,
    resolves player through 875640+592*source ushort ID and invokes
    418AD0, which calls a no-op 667E20 and 686FE3 heap deallocator
    only when player+24C is nonnull, sets +24C=0 and clears bit0
    of DWORD player+14. Native execution and actual free are NOT claimed.
    """
    if not isinstance(reached,Original7D7760DueNonhumanReached):
        raise Original7D7760DueSourceError("typed actually reached original 7D7760 event required")
    producer=reached.original_source_producer
    if (not isinstance(producer,Original60AA20NonhumanReceipt)
            or producer.live_game_state_updated
            or producer.native_41a860_callback_executed
            or producer.native_613ec0_callback_executed):
        raise Original7D7760DueSourceError("original nonhuman pending event SOURCE receipt required")
    e=producer.original_pending_event_candidate
    if (e.original_event_vtable!=0x7d7760 or
            e.original_subtype_status_5 not in (0,1,2,3) or
            not e.original_native_event_required or
            e.native_wrapper_allocated or e.original_947aa8_pending_queue_changed or
            e.original_delivery_verified):
        raise Original7D7760DueSourceError("original 60AA20 pending source candidate unexecuted and 7D7760 required")
    qptr=_u32(reached.original_613ee0_queue_node_pointer,"queue node pointer")
    eventptr=_u32(reached.original_native_event_object_pointer,"event object pointer")
    idptr=_u32(reached.original_native_player_id_allocation_pointer,"player-ID payload pointer")
    if 0 in (qptr,eventptr,idptr):
        raise Original7D7760DueSourceError("nonzero native queue/event/ID addresses required")
    q=reached.original_613ee0_queue_node_bytes
    if type(q) is not bytes or len(q)<8 or unpack_from("<I",q,0)[0]!=eventptr:
        raise Original7D7760DueSourceError("native 613EE0 queue wrapper+0 event owner mismatch")
    event=reached.original_native_event_object_bytes
    if (type(event) is not bytes or len(event)!=20 or
            unpack_from("<I",event,0)[0]!=0x7d7760 or
            unpack_from("<I",event,8)[0]!=1 or
            unpack_from("<I",event,12)[0]!=idptr or
            event[0x10]!=e.original_subtype_status_5 or
            unpack_from("<I",event,4)[0]!=e.original_due_day_raw):
        raise Original7D7760DueSourceError("exact original 7D7760 event count/status/date/player pointer required")
    pid=e.original_player_id
    source_id=reached.original_native_player_id_allocation_bytes
    if (type(source_id) is not bytes or len(source_id)!=4 or
            unpack_from("<I",source_id,0)[0]!=pid):
        raise Original7D7760DueSourceError("original 60AA20 allocated four-byte player ID required")
    target=_signed32(_u32(reached.original_613ee0_target_day_raw_dword,"due scanner day"))
    due=_signed32(e.original_due_day_raw)
    if due>target:
        raise Original7D7760DueSourceError("original 613EE0 signed date comparison skips not-due event")
    player=reached.original_player_before_due_handler
    if (type(player) is not bytes or len(player)<0x250 or
            player!=producer.original_player_after_41a860_and_60aa20 or
            unpack_from("<H",player,4)[0]!=pid):
        raise Original7D7760DueSourceError("original due player must match independently reached post-producer world")
    proof=reached.original_5d7b40_4139e0_manager_proof
    if (not isinstance(proof,Original417340RegisteredUserReceipt) or
            proof.original_native_player_at_call!=player or
            proof.original_native_player_id!=pid or
            type(proof.original_417340_return_al) is not int or proof.original_417340_return_al!=0 or
            proof.native_callback_executed or proof.live_game_state_updated):
        raise Original7D7760DueSourceError("5D7BAA native no-manager owner predicate AL0 required")
    ptr=unpack_from("<I",player,0x24c)[0]
    after=bytearray(player)
    pack_into("<I",after,0x24c,0)
    pack_into("<I",after,0x14,unpack_from("<I",player,0x14)[0]&~1)
    return Original7D7760DueCleanupReceipt(
        pid,due,target,0x5d7b40,True,ptr,ptr!=0,bytes(after),
    )
