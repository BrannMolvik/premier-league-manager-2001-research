"""Original 0x5127A0 roster uint16 IDs vs active-row native player pointers.

Source original 0x512841/0x5128EA roster IDs use 0x875640 native player
pool, 592-byte entries; row+4 vectors instead carry already-resolved
native player pointers. Pointer-to-ID ownership is verified by the
ACTUALLY REACHED original DBRPlayer +4 unsigned ID, never by guessing
that a row pointer's numeric value is the roster ID.

Private original executable source SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Static source mapping only, no original runtime or GameState writes.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_5127a0_order_guard import Original5127A0OrderedSide


class Original5127A0IdentityError(ValueError):
    pass


@dataclass(frozen=True)
class Original5127A0ReachedPlayer:
    """One independently reached original player at its *native pointer*."""
    original_player_pointer: int
    original_player_at_call: bytes


@dataclass(frozen=True)
class Original5127A0PlayerOwnerReceipt:
    side_index: int
    native_roster_ids: tuple[int,...]
    native_roster_pointers: tuple[int,...]
    native_row_ids: tuple[int,...]
    native_row_pointers: tuple[int,...]
    native_callbacks_executed: bool = False
    live_game_state_updated: bool = False


def source_original_5127a0_player_pointer_identity(
    *,
    source_side: Original5127A0OrderedSide,
    original_reached_players: tuple[Original5127A0ReachedPlayer, ...],
) -> Original5127A0PlayerOwnerReceipt:
    """Require exact roster identity and source row-pointer membership.

    Full original player pool pointer arithmetic requires a separately
    reached original 0x875640 pool base and 592-byte object stride.
    This routine does NOT guess that pool base. Its actually reached
    address+record pair must establish the row ID from DBRPlayer+4;
    the source roster still supplies unsigned IDs at side+244.
    """
    side=source_side
    if not isinstance(side,Original5127A0OrderedSide) or side.pass_index not in (0,1):
        raise Original5127A0IdentityError("actual source side EBX 0 or 1 required")
    if type(original_reached_players) is not tuple:
        raise Original5127A0IdentityError("actual source player pointer records tuple required")
    ids=side.source_roster_ids
    if type(ids) is not tuple or not ids or len(ids)>40:
        raise Original5127A0IdentityError("actual native side roster IDs required")
    if len(original_reached_players)!=len(ids):
        raise Original5127A0IdentityError("source roster pointer coverage missing/extra")
    expected={}
    pointers=[]
    for record,needed in zip(original_reached_players,ids):
        if not isinstance(record,Original5127A0ReachedPlayer):
            raise Original5127A0IdentityError("actual native player record required")
        ptr=record.original_player_pointer
        raw=record.original_player_at_call
        if type(ptr) is not int or not 0<ptr<=0xffffffff:
            raise Original5127A0IdentityError("original resolved player pointer invalid")
        if type(raw) is not bytes or len(raw)<6:
            raise Original5127A0IdentityError("original player+4 identity bytes missing")
        pid=unpack_from("<H",raw,4)[0]
        if type(needed) is not int or not 0<=needed<=65535 or needed!=pid:
            raise Original5127A0IdentityError("source roster uint16 and actual DBRPlayer+4 differ")
        if ptr in expected:
            raise Original5127A0IdentityError("source resolved player pointer repeated")
        expected[ptr]=pid
        pointers.append(ptr)
    for i,row in enumerate(side.source_rows):
        if row.pass_index!=side.pass_index or row.row_index!=i:
            raise Original5127A0IdentityError("native row side/index identity mismatch")
        if row.source_player_pointer not in expected:
            raise Original5127A0IdentityError(
                "native active row player pointer not in actual side roster")
    return Original5127A0PlayerOwnerReceipt(
        side_index=side.pass_index,
        native_roster_ids=ids,
        native_roster_pointers=tuple(pointers),
        native_row_ids=tuple(expected[row.source_player_pointer] for row in side.source_rows),
        native_row_pointers=tuple(row.source_player_pointer for row in side.source_rows),
    )
