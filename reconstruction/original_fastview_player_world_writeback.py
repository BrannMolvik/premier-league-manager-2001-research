"""Source-qualified per-player portions of original FastView post-modal save.

Original footballmanager.exe 0x533BF0 captures two compact attributes
per listed player; 0x533CA0 restores them from global 0x877BB4/0x877A74
and triggers distinct original starter/substitute methods. No original
player object resolver, 0x4182F0/0x4182C0 transitive effects, match
engine, event queue, live world mutation or GUI are represented by
these VALUE projections.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_fastview_two_sided_live_writeback import SourceFastViewTwoSideBlockState

SOURCE_FASTVIEW_NATIVE_PRE_WORLD_CAPTURE_VA = 0x533BF0
SOURCE_FASTVIEW_NATIVE_POST_WORLD_WRITEBACK_VA = 0x533CA0
SOURCE_FASTVIEW_NATIVE_PLAYER_OBJECT_REGISTRY_VA = 0x875644
SOURCE_FASTVIEW_NATIVE_PLAYER_SUBOBJECT_POINTER_OFFSET = 0x248
SOURCE_FASTVIEW_NATIVE_PLAYER_CLUB_WORDS_OFFSET = 0x244
SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_LOW5_VA = 0x877BB4
SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_LOW4_VA = 0x877A74
SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_SIDE_STRIDE = 0xA0
SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_BYTES = 0x140
SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_INDEX_STRIDE = 4
SOURCE_FASTVIEW_NATIVE_FIRST11_METHOD_VA = 0x4182F0
SOURCE_FASTVIEW_NATIVE_AFTER11_METHOD_VA = 0x4182C0
SOURCE_FASTVIEW_NATIVE_FIRST11_STATUS_OR = 0x10
SOURCE_FASTVIEW_NATIVE_AFTER11_STATUS_OR = 0x20
SOURCE_FASTVIEW_NATIVE_PLAYER_LOW5_GETTER_VA = 0x4EA3C0
SOURCE_FASTVIEW_NATIVE_PLAYER_LOW4_GETTER_VA = 0x4EA3D0
SOURCE_FASTVIEW_NATIVE_PLAYER_LOW5_SETTER_VA = 0x4EA330
SOURCE_FASTVIEW_NATIVE_PLAYER_LOW4_SETTER_VA = 0x4EA350


class SourceFastViewPlayerWorldWritebackError(ValueError):
    pass


@dataclass(frozen=True)
class SourceFastViewPlayerWriteIntent:
    side_index: int
    player_ordinal: int
    source_player_id_word: int
    native_player_branch_va: int
    native_object_status_or_bit: int
    original_low5_parameter_dword: int
    original_low4_parameter_byte: int


def source_fastview_native_postmodal_player_write_intents_533ca0(
    *, live_sides_after_modal: SourceFastViewTwoSideBlockState,
    native_player_counts: tuple[int, int],
    global_player_low5_dwords: bytes,
    global_player_low4_dwords: bytes,
) -> tuple[SourceFastViewPlayerWriteIntent, ...]:
    """Project real original per-side player IDs, status branch, parameters.

    Native 0x533CA0 iterates TWO original club side pointers. Each
    player's WORD ID comes from club+0x244+2*ordinal AFTER source
    20-DWORD global writeback. It resolves original player record via
    virtual registry 0x875644; first 11 call 0x4182F0, rest 0x4182C0.
    Attribute sources are indexed by 0xA0*side+4*ordinal. This is a
    read-only intent list, NOT pointer resolution, world mutation,
    result processing or a complete match.
    """
    if type(live_sides_after_modal) is not SourceFastViewTwoSideBlockState:
        raise SourceFastViewPlayerWorldWritebackError(
            "authentic two-sided post-modal club state required")
    if (type(native_player_counts) is not tuple or len(native_player_counts) != 2
            or any(type(n) is not int or not 11 <= n <= 18
                   for n in native_player_counts)):
        raise SourceFastViewPlayerWorldWritebackError(
            "two verified 11..18 native roster counts required")
    for data in (global_player_low5_dwords, global_player_low4_dwords):
        if type(data) is not bytes or len(data) != SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_BYTES:
            raise SourceFastViewPlayerWorldWritebackError(
                "source original player global must be exactly 0x140 bytes")
    out = []
    for side, club in enumerate(
        (live_sides_after_modal.first_side_bytes, live_sides_after_modal.second_side_bytes)
    ):
        for ordinal in range(native_player_counts[side]):
            offset = side * SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_SIDE_STRIDE + 4*ordinal
            player_id = unpack_from(
                "<H", club, SOURCE_FASTVIEW_NATIVE_PLAYER_CLUB_WORDS_OFFSET + 2*ordinal
            )[0]
            out.append(SourceFastViewPlayerWriteIntent(
                side_index=side,
                player_ordinal=ordinal,
                source_player_id_word=player_id,
                native_player_branch_va=(
                    SOURCE_FASTVIEW_NATIVE_FIRST11_METHOD_VA if ordinal < 11
                    else SOURCE_FASTVIEW_NATIVE_AFTER11_METHOD_VA
                ),
                native_object_status_or_bit=(
                    SOURCE_FASTVIEW_NATIVE_FIRST11_STATUS_OR if ordinal < 11
                    else SOURCE_FASTVIEW_NATIVE_AFTER11_STATUS_OR
                ),
                original_low5_parameter_dword=unpack_from(
                    "<I", global_player_low5_dwords, offset
                )[0],
                original_low4_parameter_byte=global_player_low4_dwords[offset],
            ))
    return tuple(out)


def source_fastview_original_player_low5_low4_getters_4ea3c0(
    *, original_player_attribute_bytes: bytes,
) -> tuple[int, int]:
    """Source 0x4EA3C0/0x4EA3D0 return the low-bit field values."""
    if type(original_player_attribute_bytes) is not bytes or len(original_player_attribute_bytes) < 5:
        raise SourceFastViewPlayerWorldWritebackError(
            "original player subobject must contain byte offsets +3/+4")
    return (original_player_attribute_bytes[3] & 0x1F,
            original_player_attribute_bytes[4] & 0x0F)


def source_fastview_original_player_low5_low4_setters_4ea330(
    *, original_player_attribute_bytes: bytes,
    native_low5_parameter_dword: int,
    native_low4_parameter_byte: int,
) -> bytes:
    """Only original two packed-bit setter effects, never full player save.

    Native 0x4EA330 changes only low five bits of byte+3, native
    0x4EA350 only low four bits of byte+4. Native 0x4182F0/0x4182C0
    perform additional field and downstream calls which this immutable
    helper deliberately does not execute.
    """
    source_fastview_original_player_low5_low4_getters_4ea3c0(
        original_player_attribute_bytes=original_player_attribute_bytes)
    if (type(native_low5_parameter_dword) is not int or
            not 0 <= native_low5_parameter_dword <= 0xFFFFFFFF):
        raise SourceFastViewPlayerWorldWritebackError("native low5 DWORD required")
    if (type(native_low4_parameter_byte) is not int or
            not 0 <= native_low4_parameter_byte <= 0xFF):
        raise SourceFastViewPlayerWorldWritebackError("native low4 BYTE required")
    updated = bytearray(original_player_attribute_bytes)
    updated[3] = (updated[3] & 0xE0) | (native_low5_parameter_dword & 0x1F)
    updated[4] = (updated[4] & 0xF0) | (native_low4_parameter_byte & 0x0F)
    return bytes(updated)


@dataclass(frozen=True)
class SourceFastViewPlayerPreModalGlobals:
    original_low5_globals_320: bytes
    original_low4_globals_320: bytes


def source_fastview_original_player_field_pre_modal_capture_533bf0(
    *, original_player_subobjects_by_side: tuple[tuple[bytes, ...], tuple[bytes, ...]],
    original_low5_globals_before: bytes,
    original_low4_globals_before: bytes,
) -> SourceFastViewPlayerPreModalGlobals:
    """Original 0x533BF0 getter+capture values from source-supplied players.

    Real source 0x533BF0 iterates native side record+0x294 count, resolves
    each source player ID from side club+0x244+2*i via registry 0x875644,
    takes its pointer+0x248 and calls low5 getter 0x4EA3C0 and low4
    getter 0x4EA3D0, storing both as DWORD at 0xA0*side+4*i.
    Caller must separately establish real player-ID->subobject order.
    Zero-length lists are source possible; unknown lists fail closed.
    Neither original global buffer is initialized to zeros here.
    """
    from struct import pack_into

    if (type(original_player_subobjects_by_side) is not tuple or
            len(original_player_subobjects_by_side) != 2 or
            any(type(side) is not tuple or len(side) > 20
                for side in original_player_subobjects_by_side)):
        raise SourceFastViewPlayerWorldWritebackError(
            "two original enumerated per-side player subobject tuples required")
    for data in (original_low5_globals_before, original_low4_globals_before):
        if type(data) is not bytes or len(data) != SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_BYTES:
            raise SourceFastViewPlayerWorldWritebackError(
                "original per-player global memory must be 320 immutable bytes")
    first=bytearray(original_low5_globals_before)
    second=bytearray(original_low4_globals_before)
    for side, players in enumerate(original_player_subobjects_by_side):
        for ordinal, player in enumerate(players):
            low5,low4 = source_fastview_original_player_low5_low4_getters_4ea3c0(
                original_player_attribute_bytes=player)
            offset = side*SOURCE_FASTVIEW_NATIVE_PLAYER_GLOBAL_SIDE_STRIDE + 4*ordinal
            pack_into("<I",first,offset,low5)
            pack_into("<I",second,offset,low4)
    return SourceFastViewPlayerPreModalGlobals(bytes(first),bytes(second))


# Original player status methods called by FastView 0x533CA0:
# first-XI 0x4182F0 OR bit0x10 in player DWORD+0x14 then call
# 0x418160 to CLEAR bit0x20. Substitute 0x4182C0 calls
# 0x418150 to CLEAR bit0x10, then OR bit0x20. BOTH call
# 0x418180: if player DWORD+0x174 bit0 set, call 0x418220
# swapping cached player BYTE+0x152/+0x153 with the packed
# low5/low4 values of subobject +0x248, then clear bit0.
# BOTH call 0x418170 to clear DWORD+0x174 bit1.
# Starter additionally invokes 0x417340 and potentially
# 0x41EDF0 which mutates other world/competition structures.
# Thus these are direct source FIELD effects, not full game saves.
SOURCE_FASTVIEW_PLAYER_STATUS_STARTER_VA = 0x4182F0
SOURCE_FASTVIEW_PLAYER_STATUS_RESERVE_VA = 0x4182C0
SOURCE_FASTVIEW_PLAYER_STATUS_CLEAR_STARTER_VA = 0x418150
SOURCE_FASTVIEW_PLAYER_STATUS_CLEAR_RESERVE_VA = 0x418160
SOURCE_FASTVIEW_PLAYER_STATUS_SHARED_174_BIT1_VA = 0x418180
SOURCE_FASTVIEW_PLAYER_STATUS_SHARED_174_BIT2_VA = 0x418170
SOURCE_FASTVIEW_PLAYER_ATTRIBUTE_CACHE_SWAP_VA = 0x418220
SOURCE_FASTVIEW_PLAYER_STARTER_EXTERNAL_EFFECT_VA = 0x41EDF0


@dataclass(frozen=True)
class SourceFastViewPlayerDirectStatusStage:
    direct_flag14_dword: int
    direct_flag174_dword: int
    requires_original_attribute_cache_swap_418220: bool
    starter_external_callback_unresolved: bool


def source_fastview_original_player_direct_status_stage_4182f0(
    *, source_flag14_dword: int, source_flag174_dword: int,
    starting_eleven: bool,
) -> SourceFastViewPlayerDirectStatusStage:
    """Exact local flag operations, not 0x41EDF0 downstream effects.

    Original flags +0x14 bit0x10 and bit0x20 are mutually reset/set.
    0x418180 calls 0x418220 only for incoming DWORD+0x174 bit0,
    then clears bit0; 0x418170 clears bit1. The starter routine can
    then call 0x41EDF0 conditional on unrelated world state, which
    this result deliberately labels unresolved. Caller does not
    mutate actual world objects from this immutable projection.
    """
    for value in (source_flag14_dword, source_flag174_dword):
        if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
            raise SourceFastViewPlayerWorldWritebackError(
                "original player flag DWORDs required")
    if type(starting_eleven) is not bool:
        raise SourceFastViewPlayerWorldWritebackError(
            "verified original starter/substitute selector bool required")
    if starting_eleven:
        flag14 = (source_flag14_dword | 0x10) & ~0x20
    else:
        flag14 = (source_flag14_dword & ~0x10) | 0x20
    return SourceFastViewPlayerDirectStatusStage(
        direct_flag14_dword=flag14,
        direct_flag174_dword=source_flag174_dword & ~0x3,
        requires_original_attribute_cache_swap_418220=bool(source_flag174_dword & 1),
        starter_external_callback_unresolved=starting_eleven,
    )


@dataclass(frozen=True)
class SourceFastViewPlayerAttributeCacheSwap:
    updated_player_record: bytes
    updated_player_subobject: bytes


def source_fastview_original_player_attribute_cache_swap_418220(
    *, original_player_record_bytes: bytes,
    original_player_subobject_bytes: bytes,
) -> SourceFastViewPlayerAttributeCacheSwap:
    """Original 0x418220's two cached bits swaps, no player registry.

    Requires verified native player record BYTE+0x152/+0x153 and
    independently authenticated subobject +0x248. Reads native
    subobject low5/low4 into player cached bytes; copies old player
    cached byte values into the two original subobject setters, which
    preserve subobject byte+3 upper3 and byte+4 upper4. Native
    caller 0x418180 only invokes this when +0x174 bit0 is set.
    """
    if (type(original_player_record_bytes) is not bytes or
            len(original_player_record_bytes) <= 0x153):
        raise SourceFastViewPlayerWorldWritebackError(
            "original player record must contain cached byte +0x153")
    oldlow5, oldlow4 = source_fastview_original_player_low5_low4_getters_4ea3c0(
        original_player_attribute_bytes=original_player_subobject_bytes)
    oldcached5=original_player_record_bytes[0x152]
    oldcached4=original_player_record_bytes[0x153]
    updated_subobject=source_fastview_original_player_low5_low4_setters_4ea330(
        original_player_attribute_bytes=original_player_subobject_bytes,
        native_low5_parameter_dword=oldcached5,
        native_low4_parameter_byte=oldcached4,
    )
    player=bytearray(original_player_record_bytes)
    player[0x152]=oldlow5
    player[0x153]=oldlow4
    return SourceFastViewPlayerAttributeCacheSwap(
        updated_player_record=bytes(player),
        updated_player_subobject=updated_subobject,
    )


def source_fastview_original_substitute_pre_restore_reset_4ea370(
    *, original_player_subobject_bytes: bytes,
) -> bytes:
    """0x4182C0 calls native 0x4EA370, prior to final 0x533CA0 restore.

    0x4EA370 reads subobject byte0, copies its low5 bits into
    byte+3 preserving old upper3, clears byte+4 low4 preserving
    its upper4. After this transient source step, 0x533CA0 uses
    the modal/global sources to restore both low fields.
    """
    source_fastview_original_player_low5_low4_getters_4ea3c0(
        original_player_attribute_bytes=original_player_subobject_bytes)
    return source_fastview_original_player_low5_low4_setters_4ea330(
        original_player_attribute_bytes=original_player_subobject_bytes,
        native_low5_parameter_dword=original_player_subobject_bytes[0],
        native_low4_parameter_byte=0,
    )


# Original starter 0x4182F0 conditional tail:
# source 0x417340 result nonzero -> skip;
# otherwise player+0x14 BIT13 set -> skip; otherwise 0x41EDF0.
# 0x41EDF0 itself requires player+0x14 BIT12. It clears BIT12,
# selects native shared count if signed player WORD+0x72 negative,
# else uses 680-byte registry entry (global0x874B90+0x2A8*index)
# DWORD+0x1A8. If the selected count is positive, decrements by one.
# This is a source-only external *intent*; actual registry pointer and
# 0x417340 implementation remain unknown to the projection.
SOURCE_FASTVIEW_STARTER_CONDITIONAL_GATE_VA = 0x417340
SOURCE_FASTVIEW_STARTER_CONDITIONAL_COUNT_METHOD_VA = 0x41EDF0
SOURCE_FASTVIEW_STARTER_COUNT_ARRAY_GLOBAL_VA = 0x874B90
SOURCE_FASTVIEW_STARTER_FALLBACK_COUNT_POINTER_GLOBAL_VA = 0x874B94
SOURCE_FASTVIEW_STARTER_COUNT_ARRAY_STRIDE_BYTES = 0x2A8
SOURCE_FASTVIEW_STARTER_COUNT_FIELD_OFFSET = 0x1A8
SOURCE_FASTVIEW_STARTER_ORIGINAL_CLUB_INDEX_WORD_OFFSET = 0x72


@dataclass(frozen=True)
class SourceFastViewStarterConditionalExternalResult:
    native_flag14_after: int
    invoked_41edf0: bool
    clears_0x1000_flag: bool
    uses_fallback_count_owner: bool | None
    native_count_after: int | None


def source_fastview_original_starter_external_count_41edf0(
    *, native_flag14_after_direct: int,
    original_417340_result_byte: int,
    original_signed_club_index_word: int,
    native_selected_owner_count_dword: int,
) -> SourceFastViewStarterConditionalExternalResult:
    """Exact source gates and projected count, not a league-world write.

    Caller must source-qualify actual 0x417340 return, player+0x72
    signed club index and selected native external count. No address
    resolution or real side effect is executed by this value result.
    """
    if (type(native_flag14_after_direct) is not int or
            not 0 <= native_flag14_after_direct <= 0xFFFFFFFF):
        raise SourceFastViewPlayerWorldWritebackError("original status+0x14 DWORD required")
    if (type(original_417340_result_byte) is not int or
            not 0 <= original_417340_result_byte <= 0xFF):
        raise SourceFastViewPlayerWorldWritebackError("source 0x417340 AL byte required")
    if (type(original_signed_club_index_word) is not int or
            not -0x8000 <= original_signed_club_index_word <= 0x7FFF):
        raise SourceFastViewPlayerWorldWritebackError("original signed 16-bit club index required")
    if (type(native_selected_owner_count_dword) is not int or
            not 0 <= native_selected_owner_count_dword <= 0xFFFFFFFF):
        raise SourceFastViewPlayerWorldWritebackError("original external count DWORD required")
    if original_417340_result_byte != 0 or native_flag14_after_direct & 0x2000:
        return SourceFastViewStarterConditionalExternalResult(
            native_flag14_after_direct, False, False, None, None)
    if not native_flag14_after_direct & 0x1000:
        return SourceFastViewStarterConditionalExternalResult(
            native_flag14_after_direct, True, False, None, None)
    return SourceFastViewStarterConditionalExternalResult(
        native_flag14_after_direct & ~0x1000, True, True,
        original_signed_club_index_word < 0,
        native_selected_owner_count_dword - 1 if native_selected_owner_count_dword else 0,
    )
