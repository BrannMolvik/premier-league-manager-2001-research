"""Source native 0x413020 type-12 human-owner queue routing for 0x419490 events.

Canonical original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Read-only reached native pointers and records. No actual wrapper allocation,
0x617D70 insertion, current user change, message delivery or GameState effect.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_native_5cfa20_due_event_transfer import (
    OriginalQueuedEventTransferReceipt,
    SOURCE_REFERENCED_EVENT_VTABLES,
)


class Original413020ManagerRouteError(ValueError):
    pass


@dataclass(frozen=True)
class Original413020ReachedManager:
    original_manager_link_pointer: int
    original_manager_link_record: bytes
    original_user_pointer: int
    original_user_record: bytes
    original_team_context_pointer: int
    original_team_context_record: bytes


@dataclass(frozen=True)
class Original413020ManagerRouteReceipt:
    original_event_object_pointer: int
    original_original_type12_team_identity: int
    original_visited_manager_nodes: tuple[int, ...]
    original_selected_user_pointer: int | None
    original_selected_user_event_queue_pointer: int | None
    source_queue_wrapper_size: int = 12
    source_queue_insertion_va: int = 0x617D70
    original_wrapper_allocated: bool = False
    native_user_queue_mutated: bool = False
    player_visible_inbox_delivered: bool = False
    live_game_state_updated: bool = False


def _nonnull(value: int, name: str) -> int:
    if type(value) is not int or not 0 < value <= 0xffffffff:
        raise Original413020ManagerRouteError(f"reached original {name} nonnull uint32 required")
    return value


def source_original_413020_first_human_owner_for_type12(
    *, original_due_transfer: OriginalQueuedEventTransferReceipt,
    original_global_world_874c10_record: bytes,
    original_reached_manager_nodes: tuple[Original413020ReachedManager, ...],
    max_managers: int = 65536,
) -> Original413020ManagerRouteReceipt:
    """Source first manager-owned queue for two original 0x419490 event types.

    413020 global+9CC manager list; manager node+0 user and node+4 next.
    User+5B4 team context, team+40 original club identity. First matching
    user is selected for original +6B4 owner after event type12 jump table:
    (12-8) -> 413554[4]=16 -> 413510[16]=41325A; category+10=1;
    concrete vtable+0C returns DC/DD, both reach 4134ED->617D70.
    Unmatched player-event world is NOT delivered to arbitrary user.
    """
    transfer = original_due_transfer
    if not isinstance(transfer, OriginalQueuedEventTransferReceipt):
        raise Original413020ManagerRouteError("qualified original 5CFA20 transfer required")
    if transfer.native_413020_executed or transfer.player_visible_inbox_delivered:
        raise Original413020ManagerRouteError("cannot reuse a claimed dispatched source receipt")
    if (type(transfer.original_referenced_after_5cfa20) is not bytes
            or len(transfer.original_referenced_after_5cfa20) < 0x48):
        raise Original413020ManagerRouteError("source referenced object through+44 required")
    ref = transfer.original_referenced_after_5cfa20
    if (unpack_from("<I", ref, 0)[0] not in SOURCE_REFERENCED_EVENT_VTABLES
            or unpack_from("<I", ref, 0x10)[0] != 1
            or unpack_from("<I", ref, 0x1c)[0] != 12):
        raise Original413020ManagerRouteError("only concrete category1/type12 event source routing proven")
    team_id = unpack_from("<I", ref, 0x14)[0]
    original = original_global_world_874c10_record
    if type(original) is not bytes or len(original) < 0x9d0:
        raise Original413020ManagerRouteError("actual global owner bytes through +9CC required")
    if type(original_reached_manager_nodes) is not tuple:
        raise Original413020ManagerRouteError("ordered original reached manager list required")
    if type(max_managers) is not int or not 1 <= max_managers <= 65536:
        raise Original413020ManagerRouteError("bounded source manager count required")
    ptr=unpack_from("<I",original,0x9cc)[0]
    visited=[]
    seen=set()
    chosen_user=None
    chosen_queue=None
    for step in original_reached_manager_nodes:
        if not ptr:
            raise Original413020ManagerRouteError("extra original manager result after native end")
        if ptr in seen or len(visited) >= max_managers:
            raise Original413020ManagerRouteError("cyclic/unbounded native manager list")
        if (not isinstance(step,Original413020ReachedManager)
                or step.original_manager_link_pointer != ptr):
            raise Original413020ManagerRouteError("actual reached native manager link pointer missing/mismatched")
        node=step.original_manager_link_record
        if type(node) is not bytes or len(node) < 8:
            raise Original413020ManagerRouteError("reached manager link DWORD+4 required")
        user_ptr=_nonnull(step.original_user_pointer,"user object pointer")
        if unpack_from("<I",node,0)[0]!=user_ptr:
            raise Original413020ManagerRouteError("source manager link+0 user identity mismatch")
        user=step.original_user_record
        if type(user) is not bytes or len(user) < 0x6b8:
            raise Original413020ManagerRouteError("original user source bytes through +6B4 required")
        context_ptr=_nonnull(step.original_team_context_pointer,"team context")
        if unpack_from("<I",user,0x5b4)[0]!=context_ptr:
            raise Original413020ManagerRouteError("original user+5B4 source team owner mismatch")
        context=step.original_team_context_record
        if type(context) is not bytes or len(context) < 0x44:
            raise Original413020ManagerRouteError("original team owner bytes through +40 required")
        visited.append(ptr)
        seen.add(ptr)
        if unpack_from("<I",context,0x40)[0]==team_id:
            chosen_user=user_ptr
            chosen_queue=unpack_from("<I",user,0x6b4)[0]
            _nonnull(chosen_queue,"per-user +6B4 event queue")
            ptr=0
            break
        ptr=unpack_from("<I",node,4)[0]
    if ptr:
        raise Original413020ManagerRouteError("original manager list ended before all reached nodes")
    # Caller must not fabricate unused entries after first-match/empty stop.
    if len(visited)!=len(original_reached_manager_nodes):
        raise Original413020ManagerRouteError("extra native manager reads after first source match")
    return Original413020ManagerRouteReceipt(
        transfer.original_referenced_pointer,team_id,tuple(visited),
        chosen_user,chosen_queue,
    )
