"""Original source 0x41A250 UEFA incident branches, with reached callback boundaries.

Canonical original footballmanager.exe SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
No original EXE execution; native heap/event queue/virtuals are not invoked.
0x4197C0 only reaches this when competition v18/owner+34=1.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt


class Original41A250SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original41A250Reached:
    original_row: Original5127A0RowCall
    original_native_player_at_entry: bytes
    original_41a250_reached: bool
    original_first_reached_417340_eax: int | None = None
    original_player_after_first_branch: bytes | None = None
    original_second_reached_417340_eax: int | None = None
    original_first_417340_registered_owner_proof: Original417340RegisteredUserReceipt | None = None
    original_second_417340_registered_owner_proof: Original417340RegisteredUserReceipt | None = None


@dataclass(frozen=True)
class Original41A250Receipt:
    original_player_id: int
    original_first_417340_entry_player: bytes | None
    first_original_event_constructor_if_allocated: int | None
    original_source_player_at_second_gate_or_return: bytes
    second_original_event_constructor_if_allocated: int | None
    first_417340_original_callback_reached: bool
    second_417340_original_callback_reached: bool
    source_callback_free_leaf_complete: bool
    native_pending_queue_mutated: bool = False
    live_game_state_mutated: bool = False


def _uint32(value: int | None, name: str) -> int:
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise Original41A250SourceError(f"actual reached {name} DWORD required")
    return value


def _qualified_417340_al(
    raw_eax: int | None,
    source_proof: Original417340RegisteredUserReceipt | None,
    original_player_at_callback: bytes,
    name: str,
) -> int:
    """Native 417340 returns only AL; optional registered-owner proof can qualify it."""
    if source_proof is None:
        return _uint32(raw_eax, name) & 0xff
    if (not isinstance(source_proof, Original417340RegisteredUserReceipt)
            or source_proof.native_callback_executed
            or source_proof.live_game_state_updated
            or source_proof.original_native_player_at_call != original_player_at_callback):
        raise Original41A250SourceError(f"{name} original player/owner predicate proof mismatch")
    qualified=source_proof.original_417340_return_al
    if type(qualified) is not int or qualified not in (0,1):
        raise Original41A250SourceError(f"{name} original owner predicate AL not qualified")
    if raw_eax is not None and (_uint32(raw_eax,name)&0xff)!=qualified:
        raise Original41A250SourceError(f"{name} raw AL disagrees with registered user source")
    return qualified


def source_original_41a250_uefa_incident_from_reached(
    original: Original41A250Reached,
) -> Original41A250Receipt:
    """Only the source writes preceding optional original callbacks.

    41A26C tests source row arg2 >0: writes player+13E=1, calls
    417340 and possibly constructs original 585750 pending event. Either
    way native virtual callbacks can change source state. Require actual
    post-first-branch player snapshot before any subsequent calculation.

    41A369 adds BYTE source row arg1 to player+13D, wrapping to byte.
    If RESULT >2, subtracts exactly 3 ONCE, sets +13E=1 and calls
    417340; qualifying true original result may construct 585AD0.
    If both original gates reach, both event families can be generated.
    """
    if not isinstance(original,Original41A250Reached) or original.original_41a250_reached is not True:
        raise Original41A250SourceError("actual reached original 41A250 entry required")
    row=original.original_row
    if not isinstance(row,Original5127A0RowCall):
        raise Original41A250SourceError("source-typed 5127A0 row required")
    arg1=row.source_4197c0_arg1
    arg2=row.source_4197c0_arg2
    if any(type(x) is not int or not 0<=x<=255 for x in (arg1,arg2)):
        raise Original41A250SourceError("actual source unsigned incident row bytes required")
    src=original.original_native_player_at_entry
    if type(src) is not bytes or len(src)<0x164:
        raise Original41A250SourceError("actual native player through +160 at UEFA entry required")
    pid=unpack_from("<H",src,4)[0]
    first=None
    first_ctor=None
    if arg2>0:
        first=bytearray(src)
        first[0x13e]=1
        first_gate=_qualified_417340_al(
            original.original_first_reached_417340_eax,
            original.original_first_417340_registered_owner_proof,
            bytes(first),
            "first 417340 EAX",
        )
        first_ctor=0x585750 if first_gate==1 else None
        post=original.original_player_after_first_branch
        if type(post) is not bytes or len(post)<0x164 or unpack_from("<H",post,4)[0]!=pid:
            raise Original41A250SourceError("actual player snapshot AFTER first source callback/event due required")
        p=bytearray(post)
    else:
        if (original.original_first_reached_417340_eax is not None or
                original.original_first_417340_registered_owner_proof is not None or
                original.original_player_after_first_branch is not None):
            raise Original41A250SourceError("native initial branch skipped but extra callbacks supplied")
        p=bytearray(src)
    total=(p[0x13d]+arg1)&0xff
    p[0x13d]=total
    second_ctor=None
    if total>2:
        p[0x13d]=(total-3)&0xff
        p[0x13e]=1
        second_gate=_qualified_417340_al(
            original.original_second_reached_417340_eax,
            original.original_second_417340_registered_owner_proof,
            bytes(p),
            "second 417340 EAX",
        )
        second_ctor=0x585ad0 if second_gate==1 else None
    elif (original.original_second_reached_417340_eax is not None or
            original.original_second_417340_registered_owner_proof is not None):
        raise Original41A250SourceError("native second callback skipped but result supplied")
    return Original41A250Receipt(
        original_player_id=pid,
        original_first_417340_entry_player=(None if first is None else bytes(first)),
        first_original_event_constructor_if_allocated=first_ctor,
        original_source_player_at_second_gate_or_return=bytes(p),
        second_original_event_constructor_if_allocated=second_ctor,
        first_417340_original_callback_reached=arg2>0,
        second_417340_original_callback_reached=total>2,
        source_callback_free_leaf_complete=(arg2==0 and total<=2),
    )
