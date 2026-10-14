"""Bounded, non-executing source projection for original 0x60AA20.

Evidence: original private footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
static x86 0x60AA20..0x60ABE9. Source results are not original execution,
allocation, queue delivery, a GameState transaction or GUI acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from


class Original60AA20SourceError(ValueError):
    pass


def _int(value: int, name: str, lo: int, hi: int) -> int:
    if type(value) is not int or not lo <= value <= hi:
        raise Original60AA20SourceError(f"original {name} out of native range")
    return value


@dataclass(frozen=True)
class Original60AA20Reached:
    """Independent native call-site snapshots, never synthesized callbacks.

    Player bytes must be observed at the 60AA20 entry, not a pre-4197C0
    roster snapshot. Resolver identities cover each actually reached
    875644/vtable[0] getter, in call order (six, or eight for human).
    """
    player_id: int
    player_before: bytes
    descriptor_before: bytes
    descriptor_pointer: int
    resolver_player_ids: tuple[int, ...]
    duration_delta_arg: int
    player77_decrement_base_arg: int
    current_date_9847fc: int
    registered_417340_al: int
    native_4d1190_result_nonnull: bool | None = None
    native_v40_threshold: int | None = None
    rng5_results: tuple[int, ...] = ()


@dataclass(frozen=True)
class Original60AA20PendingIdentity:
    """Portable SOURCE-PROJECTED queue item identity, not delivered Inbox."""
    original_queue_address: int
    original_vtable_address: int
    original_type_dword: int
    original_date_raw_u32: int
    original_player_id_u16: int
    original_status_byte: int

    def to_portable(self) -> dict[str, int]:
        return {"queue": self.original_queue_address,
                "vtable": self.original_vtable_address,
                "type": self.original_type_dword,
                "date_raw_u32": self.original_date_raw_u32,
                "player_id_u16": self.original_player_id_u16,
                "status": self.original_status_byte}

    @classmethod
    def from_portable(cls, data: object) -> Original60AA20PendingIdentity:
        if type(data) is not dict or set(data) != {
            "queue", "vtable", "type", "date_raw_u32", "player_id_u16", "status"
        }:
            raise Original60AA20SourceError("complete portable original event fields required")
        if (any(type(data[key]) is not int for key in data) or
                data["queue"] != 0x947AA8 or data["vtable"] != 0x7D7760
                or data["type"] != 1):
            raise Original60AA20SourceError("original 60AA20 event owner/type mismatch")
        _int(data["date_raw_u32"], "event date", 0, 0xffffffff)
        _int(data["player_id_u16"], "event player ID", 0, 0xffff)
        _int(data["status"], "event status", 0, 3)
        return cls(data["queue"], data["vtable"], data["type"],
                   data["date_raw_u32"], data["player_id_u16"], data["status"])


@dataclass(frozen=True)
class Original60AA20Projection:
    original_player_id: int
    original_native_descriptor_pointer: int
    original_player_after_source: bytes
    original_descriptor_after_source: bytes
    original_duration_after_mitigation: int
    original_rng5_draw_count: int
    original_pending_identity: Original60AA20PendingIdentity
    original_native_callback_executed: bool = False
    original_event_allocated: bool = False
    original_queue_inserted: bool = False
    original_mail_delivered: bool = False
    live_game_state_updated: bool = False


def source_original_60aa20_project(reached: Original60AA20Reached) -> Original60AA20Projection:
    """Source 60AA20 effects, including the exact x86 human RNG(5) loop.

    Source ALWAYS ORs player+14 bit0 (41A860), stores current day+7*duration
    at descriptor+0, changes byte+77 by the signed-base gate, increments byte
    +22 by status 0/1/2/3 -> 1/4/8/8 and constructs a dated native event for
    947AA8. Bounded to original 606540-produced duration/status pairs;
    other callers need their own source trace. Native 20B+4B heap
    allocation/613EC0 enqueue are NOT performed.
    The manager + 4D1190 + virtual+0x40 branch is a dynamic dependency;
    without independently reached results it must be rejected, never guessed.
    """
    if not isinstance(reached, Original60AA20Reached):
        raise Original60AA20SourceError("original 60AA20 reached-call record required")
    pid = _int(reached.player_id, "player ID", 0, 0xffff)
    ptr = _int(reached.descriptor_pointer, "descriptor pointer", 1, 0xffffffff)
    p = reached.player_before
    d = reached.descriptor_before
    if type(p) is not bytes or len(p) < 0x250 or unpack_from("<H", p, 4)[0] != pid:
        raise Original60AA20SourceError("actual original DBRPlayer +4 owner identity required")
    if unpack_from("<I", p, 0x24c)[0] != ptr:
        raise Original60AA20SourceError("DBRPlayer+24C must own exact source descriptor pointer")
    if (type(d) is not bytes or len(d) != 12 or
            unpack_from("<I", d, 8)[0] != pid or d[4] not in (0, 1, 2)
            or d[5] not in (0, 1, 2, 3)):
        raise Original60AA20SourceError("actual original 12-byte descriptor subtype/status/player ID required")
    flag = _int(reached.registered_417340_al, "417340 AL", 0, 1)
    getters = reached.resolver_player_ids
    expected = 8 if flag else 6
    if (type(getters) is not tuple or len(getters) != expected or
            any(type(x) is not int or x != pid for x in getters)):
        raise Original60AA20SourceError("each actually reached native player getter must match owner")
    delta = _int(reached.duration_delta_arg, "606540 duration", 1, 14)
    if ((d[5] == 0 and delta != 1) or
            (d[5] == 1 and not 3 <= delta <= 6) or
            (d[5] in (2, 3) and not 11 <= delta <= 14)):
        raise Original60AA20SourceError("original 606540 status/duration branch mismatch")
    base = _int(reached.player77_decrement_base_arg, "signed base", -0x80000000, 0x7fffffff)
    today = _int(reached.current_date_9847fc, "mutable day", -0x80000000, 0x7fffffff)
    if type(reached.rng5_results) is not tuple:
        raise Original60AA20SourceError("original reached RNG(5) tuple required")
    if flag:
        if type(reached.native_4d1190_result_nonnull) is not bool:
            raise Original60AA20SourceError("human owner requires reached 4D1190 null/non-null result")
        if reached.native_4d1190_result_nonnull:
            threshold = _int(reached.native_v40_threshold, "native virtual+40 threshold", -0x80000000, 0x7fffffff)
            draws = (delta + 3) // 4
            if len(reached.rng5_results) != draws:
                raise Original60AA20SourceError("exact human RNG(5) loop draw count required")
            for draw in reached.rng5_results:
                _int(draw, "RNG(5)", 0, 4)
                if draw < threshold and delta > 1:
                    delta -= 1
        else:
            if reached.native_v40_threshold is not None or reached.rng5_results:
                raise Original60AA20SourceError("null 4D1190 skips virtual+40 and RNG5")
            draws = 0
    else:
        if (reached.native_4d1190_result_nonnull is not None
                or reached.native_v40_threshold is not None or reached.rng5_results):
            raise Original60AA20SourceError("non-human 60AA20 skips 4D1190/v40/RNG5")
        draws = 0
    day_raw = (today + 7 * delta) & 0xffffffff
    after = bytearray(p)
    pack_into("<I", after, 0x14, unpack_from("<I", p, 0x14)[0] | 1)
    old77 = p[0x77]
    after[0x77] = ((old77 - (base & 0xff)) & 0xff) if old77 > base else 1
    after[0x22] = (p[0x22] + (1, 4, 8, 8)[d[5]]) & 0xff
    next_descriptor = bytearray(d)
    pack_into("<I", next_descriptor, 0, day_raw)
    identity = Original60AA20PendingIdentity(0x947AA8, 0x7D7760, 1, day_raw, pid, d[5])
    return Original60AA20Projection(pid, ptr, bytes(after), bytes(next_descriptor),
                                     delta, draws, identity)
