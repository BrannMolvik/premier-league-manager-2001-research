"""Original 4182F0 -> 417340 -> optional 41EDF0 reached-byte leaf.

Based only on previously verified original footballmanager.exe opcode receipts
(SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3).
Pure source-byte projection, NOT original execution or a full 409C90 lineup.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into,unpack_from

from original_native_409c90_assignment_status import (
    source_original_418220_exact_role_position_exchange,
    SourceOriginal418220Exchange,
    Original409C90SourceError,
)
from original_native_417340_registered_user_gate import (
    Original417340RegisteredUserReceipt,
)
from original_native_41edf0_registered_quota import (
    Original41EDF0Reached,Original41EDF0QuotaReceipt,
    source_original_41edf0_registered_quota_from_reached,
)


@dataclass(frozen=True)
class SourceOriginal4182F0QualifiedLeaf:
    original_native_player_pointer: int
    original_player_before_4182f0: bytes
    original_status_before_4182f0: bytes
    original_player_after_leaf: bytes
    original_status_after_leaf: bytes
    original_417340_registered_user_al: int
    original_418220_exchange_if_reached: SourceOriginal418220Exchange | None
    original_41edf0_quota_if_reached: Original41EDF0QuotaReceipt | None
    original_41edf0_was_reached: bool
    native_original_callbacks_executed: bool = False
    live_game_state_modified: bool = False


def source_original_4182f0_417340_optional_41edf0_leaf(
    *, original_native_player_pointer: int,
    original_player_before_4182f0: bytes,
    original_status_before_4182f0: bytes,
    original_417340_source_receipt: Original417340RegisteredUserReceipt,
    original_41edf0_source_if_reached: Original41EDF0Reached | None,
) -> SourceOriginal4182F0QualifiedLeaf:
    """Native reached stores and callback/skip ownership; never run callbacks.

    Original 4182F3 sets +14 bit4; 418160 clears bit5; 418180 exchanges
    original status+3/+4 with full player+152/+153 when +174 bit0;
    418170 clears +174 bits0/1; 41830C calls 417340. Only original AL0
    AND player +14 bit13 CLEAR reaches 418321 -> 41EDF0. The separate
    41EDF0 source function handles player bit12 and signed +72 quota.
    """
    p=original_player_before_4182f0
    st=original_status_before_4182f0
    ptr=original_native_player_pointer
    if (type(ptr) is not int or not 0<ptr<=0xffffffff
            or type(p) is not bytes or len(p)<0x24c
            or type(st) is not bytes or len(st)<5
            or unpack_from("<I",p,0x248)[0]==0):
        raise Original409C90SourceError(
            "actual original 4182F0 player pointer/full source player/status required")
    flags14=unpack_from("<I",p,0x14)[0]
    flags174=unpack_from("<I",p,0x174)[0]
    player=bytearray(p)
    pack_into("<I",player,0x14,(flags14|0x10)&~0x20)
    exchange=None
    status=st
    if flags174&1:
        exchange=source_original_418220_exact_role_position_exchange(
            original_native_player_pointer=ptr,
            original_player_record_before_418220=bytes(player),
            original_status_record_before_418220=st)
        player=bytearray(exchange.source_player_after_418220)
        status=exchange.source_status_after_418220
    pack_into("<I",player,0x174,flags174&~3)

    received=original_417340_source_receipt
    after_417340=bytes(player)
    if (type(received) is not Original417340RegisteredUserReceipt
            or received.original_native_player_at_call!=after_417340
            or received.original_native_player_id!=unpack_from("<H",p,4)[0]
            or received.original_current_club_index_signed!=unpack_from("<h",p,0x10)[0]
            or type(received.original_417340_return_al) is not int
            or received.original_417340_return_al not in (0,1)
            or received.original_417340_return_al!=int(
                received.original_matching_user_pointer is not None)):
        raise Original409C90SourceError(
            "exact independently reached original 417340 after-local-store receipt required")
    al=received.original_417340_return_al
    needs_41edf0=(al==0 and not (unpack_from("<I",after_417340,0x14)[0]&0x2000))
    quota=None
    if needs_41edf0:
        original=original_41edf0_source_if_reached
        if (type(original) is not Original41EDF0Reached
                or original.original_player_at_call!=after_417340):
            raise Original409C90SourceError(
                "original 418321 reached 41EDF0 exact post-417340 player required")
        quota=source_original_41edf0_registered_quota_from_reached(original)
        player=bytearray(quota.original_player_after_41edf0)
    elif original_41edf0_source_if_reached is not None:
        raise Original409C90SourceError("unreached original 41EDF0 source must not be supplied")
    return SourceOriginal4182F0QualifiedLeaf(
        ptr,p,st,bytes(player),status,al,exchange,quota,needs_41edf0)
