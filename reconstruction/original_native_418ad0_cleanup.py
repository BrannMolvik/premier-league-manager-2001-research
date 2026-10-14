"""Original player 418AD0 descriptor cleanup, read-only static source.

Private verified footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Original 418AD4 reads DBRPlayer+24C; if nonnull 667E20 is a bare RET,
and 686FE3 wraps heap free; then ALWAYS +24C=0, DWORD+14 bit0 cleared.
No native deallocator invoked by this Python projector.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into,unpack_from


class Original418AD0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original418AD0CleanupReceipt:
    original_player_id: int
    original_descriptor_pointer_before: int
    original_native_calls_noop_667e20_if_nonzero: bool
    original_native_requests_686fe3_free_if_nonzero: bool
    original_player_after_source: bytes
    original_cleanup_native_executed: bool = False
    original_heap_freed: bool = False
    live_game_state_updated: bool = False


def source_original_418ad0_cleanup(*, player_id: int, player_before: bytes) -> Original418AD0CleanupReceipt:
    """Source byte-level 418AD0..418B02. Operates on one independent player.

    No original native heap ownership proof, event queue mutation, or
    GameState commit is inferred from a single function.
    """
    if type(player_id) is not int or not 0<=player_id<=0xffff:
        raise Original418AD0SourceError("source native unsigned 16-bit player ID required")
    if (type(player_before) is not bytes or len(player_before)<0x250
            or unpack_from("<H",player_before,4)[0]!=player_id):
        raise Original418AD0SourceError("actual original player+4 ID/24C source bytes required")
    old=unpack_from("<I",player_before,0x24c)[0]
    out=bytearray(player_before)
    pack_into("<I",out,0x24c,0)
    pack_into("<I",out,0x14,unpack_from("<I",player_before,0x14)[0]&0xfffffffe)
    return Original418AD0CleanupReceipt(
        player_id,old,old!=0,old!=0,bytes(out),
    )
