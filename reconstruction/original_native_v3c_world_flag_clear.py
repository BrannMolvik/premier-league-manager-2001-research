"""Source-native 0x511370→0x50EA40→0x418030 first-side world effects.

Original private footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Static source proof; immutable projections from *reached* original memory.
No SideRef calls, real GameState mutation or match completion are executed.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into, unpack_from


class OriginalV3CWorldClearError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalV3CReachedPlayer:
    original_player_id: int
    original_player_record_at_418030: bytes


@dataclass(frozen=True)
class OriginalV3CReachedSide:
    original_side_ref_offset: int
    original_side_object_pointer: int
    original_side_record_at_50ea40: bytes
    original_world_object_pointer_at_compare: int
    original_world_record_at_compare: bytes
    original_world_object_pointer_at_final_store: int | None = None
    original_world_record_at_final_store: bytes | None = None
    original_player_records_at_418030: tuple[OriginalV3CReachedPlayer, ...] = ()


@dataclass(frozen=True)
class OriginalV3CSideWorldClearResult:
    original_side_ref_offset: int
    original_world_pointer: int
    original_world_index_before: int
    original_side_world_equal: bool
    original_player_flags_after: tuple[OriginalV3CReachedPlayer, ...]
    original_world_record_after: bytes | None


@dataclass(frozen=True)
class OriginalV3CWorldClearReceipt:
    original_match_day_category_signed: int
    original_initial_competition_al: int
    original_side_results: tuple[OriginalV3CSideWorldClearResult, ...]
    native_side_callbacks_invoked: bool = False
    live_game_state_updated: bool = False


def _uint32(value: int | None, name: str, *, nonzero: bool = False) -> int:
    if type(value) is not int or not (0 <= value <= 0xffffffff) or (nonzero and value == 0):
        raise OriginalV3CWorldClearError(f"actual original {name} uint32 required")
    return value


def source_original_511370_first_side_world_clears(
    *, original_match_at_511381: bytes,
    original_first_competition_virtual30_eax: int,
    original_reached_sides: tuple[OriginalV3CReachedSide, ...],
) -> OriginalV3CWorldClearReceipt:
    """Project source 511392..511429, requiring all native reached callback values.

    Initial 5112E0 AL zero skips both SideRefs; nonzero processes +14 then
    +28. Each reached world+68 is compared with signed SAR(match+0C,1).
    On match, 50EA40 loops signed side+294 count over uint16 IDs at
    side+244; 418030 clears bit2 at player+14/+148. A second original
    SideRef/world getter is then followed by world+68 = 0xFFFFFFFF.
    """
    record = original_match_at_511381
    if type(record) is not bytes or len(record) < 0x50:
        raise OriginalV3CWorldClearError("original match bytes through +4C required")
    if not unpack_from("<I", record, 0x44)[0] & 1:
        raise OriginalV3CWorldClearError("original 511381 bit0 store missing")
    al = _uint32(original_first_competition_virtual30_eax, "competition v30 EAX") & 0xff
    if type(original_reached_sides) is not tuple:
        raise OriginalV3CWorldClearError("ordered reached side tuple required")
    category = unpack_from("<i", record, 0x0c)[0] >> 1
    if not al:
        if original_reached_sides:
            raise OriginalV3CWorldClearError("original AL zero skips both SideRef branches")
        return OriginalV3CWorldClearReceipt(category, al, ())
    if (len(original_reached_sides) != 2 or
        tuple(s.original_side_ref_offset if isinstance(s, OriginalV3CReachedSide) else None
              for s in original_reached_sides) != (0x14, 0x28)):
        raise OriginalV3CWorldClearError("original source must reach SideRef +14 then +28")
    results = []
    for side in original_reached_sides:
        _uint32(side.original_side_object_pointer, "SideRef getter", nonzero=True)
        ptr = _uint32(side.original_world_object_pointer_at_compare, "global owner", nonzero=True)
        world = side.original_world_record_at_compare
        if type(world) is not bytes or len(world) < 0x6c:
            raise OriginalV3CWorldClearError("world bytes through +68 required")
        prev = unpack_from("<i", world, 0x68)[0]
        side_bytes = side.original_side_record_at_50ea40
        if type(side_bytes) is not bytes or len(side_bytes) < 0x298:
            raise OriginalV3CWorldClearError("reached side bytes through +294 required")
        if prev != category:
            if (side.original_world_object_pointer_at_final_store is not None or
                side.original_world_record_at_final_store is not None or
                side.original_player_records_at_418030):
                raise OriginalV3CWorldClearError("source marker mismatch skips player callbacks/store")
            results.append(OriginalV3CSideWorldClearResult(
                side.original_side_ref_offset, ptr, prev, False, (), None))
            continue
        count = unpack_from("<i", side_bytes, 0x294)[0]
        if not 0 <= count <= 40:
            raise OriginalV3CWorldClearError("unqualified roster count outside side+244..+293")
        reached = side.original_player_records_at_418030
        if type(reached) is not tuple or len(reached) != count:
            raise OriginalV3CWorldClearError("one original reached player for each roster index required")
        converted = []
        for i, p in enumerate(reached):
            if not isinstance(p, OriginalV3CReachedPlayer):
                raise OriginalV3CWorldClearError("original reached player type required")
            native_id = unpack_from("<H", side_bytes, 0x244 + 2*i)[0]
            if type(p.original_player_id) is not int or p.original_player_id != native_id:
                raise OriginalV3CWorldClearError("original 50EA40 player ID mismatch")
            raw = p.original_player_record_at_418030
            if type(raw) is not bytes or len(raw) < 0x14c:
                raise OriginalV3CWorldClearError("actual player bytes through +148 required")
            output = bytearray(raw)
            for off in (0x14, 0x148):
                pack_into("<I", output, off, unpack_from("<I", raw, off)[0] & 0xfffffffb)
            converted.append(OriginalV3CReachedPlayer(native_id, bytes(output)))
        store_ptr = _uint32(side.original_world_object_pointer_at_final_store,
                            "post-callback world pointer", nonzero=True)
        final = side.original_world_record_at_final_store
        if type(final) is not bytes or len(final) < 0x6c:
            raise OriginalV3CWorldClearError("post-callback world bytes through +68 required")
        if store_ptr != ptr:
            raise OriginalV3CWorldClearError(
                "original world owner changed after callback; cross-pointer effect unresolved")
        after = bytearray(final)
        pack_into("<I", after, 0x68, 0xffffffff)
        results.append(OriginalV3CSideWorldClearResult(
            side.original_side_ref_offset, store_ptr, prev,
            True, tuple(converted), bytes(after)))
    return OriginalV3CWorldClearReceipt(category, al, tuple(results))
