"""Original 605F90 post-handler registered-human record byte+24 clearing.

Verified private original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
static x86 functions 605FEE..60601F, 417380, 4172D0, 403850, 413B40,
41E3D0. No original function execution or claim of descriptor destruction.

The target is a **registered human user+0x6B8-owned pointer**, NOT a
DBRClub+0x6B8 record: original 4172D0->403850->413B40 returns the
matching user object; 417380 then dereferences user+0x6B8.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt
from original_native_605f90_dispatch import Original605F90PreDispatchReceipt


class Original605F90PostSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original605F90PostReached:
    """Separately reached native getter and original owner-scan snapshots.

    Native third getter feeds 417340; only an AL=1 branch calls the fourth
    getter and 417380. No assertion that event handlers are pure, nor that
    third/fourth player snapshots or addresses must be bitwise identical.
    """
    original_predispatch: Original605F90PreDispatchReceipt
    original_third_resolved_player_pointer: int
    original_third_resolved_player: bytes
    original_posthandler_417340_owner_proof: Original417340RegisteredUserReceipt
    original_fourth_resolved_player_pointer: int | None = None
    original_fourth_resolved_player: bytes | None = None
    original_4172d0_403850_returned_user_pointer: int | None = None
    original_413b40_reached_user_record: bytes | None = None
    original_417380_user_table_pointer: int | None = None
    original_417380_target_record_pointer: int | None = None
    original_417380_target_record_before: bytes | None = None


@dataclass(frozen=True)
class Original605F90PostReceipt:
    original_player_id: int
    original_registered_human_al: int
    original_third_getter_player_pointer: int
    original_fourth_getter_player_pointer_if_reached: int | None
    original_417380_branch_reached: bool
    original_41e3d0_selector_from_player70_if_reached: int | None
    original_registered_user_pointer_if_reached: int | None
    original_target_pointer_if_reached: int | None
    original_target_record_source_after_if_reached: bytes | None
    original_605f90_source_return_al: int = 1
    original_native_posthandler_executed: bool = False
    original_417380_target_write_executed: bool = False
    original_descriptor_freed_or_detached: bool = False
    original_pending_event_delivered: bool = False
    live_game_state_updated: bool = False


def _ptr(value: int | None, name: str) -> int:
    if type(value) is not int or not 0 < value <= 0xffffffff:
        raise Original605F90PostSourceError(f"original reached {name} pointer required")
    return value


def _player(value: bytes | None, wanted: int, label: str) -> bytes:
    if type(value) is not bytes or len(value)<0x78 or unpack_from("<H",value,4)[0]!=wanted:
        raise Original605F90PostSourceError(f"actual {label} native player +4 ID and +70 required")
    return value


def source_original_605f90_posthandler_from_reached(
    reached: Original605F90PostReached,
) -> Original605F90PostReceipt:
    """Native 605FEE fifth stage: third getter -> 417340; if AL=1 fourth
    getter -> 417380 -> returned pointer+0x24 byte cleared -> AL=1.

    417380 calls 4172D0->403850->413B40, which finds the registered USER
    object, reads user+0x6B8 for a table pointer, and calls 41E3D0 with
    player signed+0x10 as its explicit argument. This *always* equals
    41E3D0's comparison to current player signed+0x10, so 41E3D0
    returns BYTE player+0x70 (NOT BYTE+0x76). The return is masked
    to byte and transformed into source target table+200*(index-1),
    at which original 605F90 clears byte+0x24.

    Index zero is unproven as a safe owned table element: original pointer
    math addresses table-200. This safe projection deliberately fails
    closed until a real independent owner extent proves that memory belongs
    to the original target object. It is not evidence native ignores zero.
    """
    if not isinstance(reached,Original605F90PostReached):
        raise Original605F90PostSourceError("typed 605F90 post-handler reached stage required")
    prior=reached.original_predispatch
    if (not isinstance(prior, Original605F90PreDispatchReceipt) or
            prior.original_native_handler_executed or
            prior.original_allocated_descriptor_freed or
            prior.original_player24c_lifecycle_complete or
            prior.live_game_state_updated or
            prior.original_event_delivery_verified or
            prior.original_handler_choice.original_subtype!=prior.original_subtype):
        raise Original605F90PostSourceError("source 605F90 predispatch receipt, no premature completion required")
    player_id=prior.original_player_id
    third_ptr=_ptr(reached.original_third_resolved_player_pointer,"third getter")
    third=_player(reached.original_third_resolved_player,player_id,"third getter")
    proof=reached.original_posthandler_417340_owner_proof
    if (not isinstance(proof,Original417340RegisteredUserReceipt) or
            proof.original_native_player_id!=player_id or
            proof.original_native_player_at_call!=third or
            proof.native_callback_executed or proof.live_game_state_updated or
            type(proof.original_417340_return_al) is not int or
            proof.original_417340_return_al not in (0,1)):
        raise Original605F90PostSourceError("actual third getter 417340 original manager proof required")
    human=proof.original_417340_return_al
    fourth_fields=(
        reached.original_fourth_resolved_player_pointer,
        reached.original_fourth_resolved_player,
        reached.original_4172d0_403850_returned_user_pointer,
        reached.original_413b40_reached_user_record,
        reached.original_417380_user_table_pointer,
        reached.original_417380_target_record_pointer,
        reached.original_417380_target_record_before,
    )
    if human==0:
        if any(item is not None for item in fourth_fields) or proof.original_matching_user_pointer is not None:
            raise Original605F90PostSourceError("original AL0 skips fourth getter and 417380 entirely")
        return Original605F90PostReceipt(player_id,0,third_ptr,None,False,
                                         None,None,None,None)
    fourth_ptr=_ptr(reached.original_fourth_resolved_player_pointer,"fourth getter")
    fourth=_player(reached.original_fourth_resolved_player,player_id,"fourth getter")
    if unpack_from("<h",fourth,0x10)[0]!=proof.original_current_club_index_signed:
        raise Original605F90PostSourceError("human source team owner changed between 417340 and 417380")
    userptr=_ptr(reached.original_4172d0_403850_returned_user_pointer,"registered user from 413B40")
    if userptr!=proof.original_matching_user_pointer:
        raise Original605F90PostSourceError("actual 4172D0/403850/413B40 user pointer disagrees with 417340 user")
    user=reached.original_413b40_reached_user_record
    if type(user) is not bytes or len(user)<0x6bc:
        raise Original605F90PostSourceError("native registered human USER bytes through +6B8 required")
    source_table_ptr=_ptr(unpack_from("<I",user,0x6b8)[0],"user+6B8 table")
    table_ptr=_ptr(reached.original_417380_user_table_pointer,"reached user table")
    if table_ptr!=source_table_ptr:
        raise Original605F90PostSourceError("native table is user+6B8, not club or other owner")
    index=fourth[0x70]
    if index==0:
        raise Original605F90PostSourceError("native 41E3D0 selector 0 points before table; extent unproven")
    target=(table_ptr+200*(index-1))&0xffffffff
    if target==0 or table_ptr+200*(index-1)>0xffffffff:
        raise Original605F90PostSourceError("native user record target pointer overflows")
    if _ptr(reached.original_417380_target_record_pointer,"source record target")!=target:
        raise Original605F90PostSourceError("original 417380 200-byte indexed target identity mismatch")
    before=reached.original_417380_target_record_before
    if type(before) is not bytes or len(before)!=200:
        raise Original605F90PostSourceError("actual reached original 200-byte indexed record required")
    after=bytearray(before)
    after[0x24]=0
    return Original605F90PostReceipt(
        player_id,1,third_ptr,fourth_ptr,True,index,userptr,target,bytes(after),
    )
