"""Source-bounded FastView outer-modal pre/post state-block copies.

Original owner-approved footballmanager.exe (SHA256 833bf95e...)
at 0x5331C0 stages *both* sides before modal 0x532650, then calls
0x533CA0 on both sides after modal return. Original 0x533BF0 reads
20 DWORDs from side record+0x244 to side global 0x877CF4+side*0xA0;
original 0x533CA0 reverses those 80-byte copies and additionally
updates source player records through native methods 0x4182F0/0x4182C0,
0x4EA330 and 0x4EA350. These immutable helpers model ONLY the two
20-DWORD transfers, and must never be described as complete FastView
world-state writeback or a playable match.
"""
from __future__ import annotations

from dataclasses import dataclass

SOURCE_FASTVIEW_OUTER_MODAL_VA = 0x5331C0
SOURCE_FASTVIEW_INTERMEDIATE_RESET_CALLSITE_VA = 0x533203
SOURCE_FASTVIEW_INTERMEDIATE_RESET_VA = 0x6C1CF0
SOURCE_FASTVIEW_INTERMEDIATE_RESET_GLOBAL_VAS = (0xA145F0, 0xA145F4)
SOURCE_FASTVIEW_PRE_MODAL_COPIER_VA = 0x533BF0
SOURCE_FASTVIEW_POST_MODAL_COPIER_VA = 0x533CA0
SOURCE_FASTVIEW_MODAL_RUN_VA = 0x532650
SOURCE_FASTVIEW_GLOBAL_TWO_SIDE_ORIGIN_VA = 0x877CF4
SOURCE_FASTVIEW_NATIVE_SECOND_SIDE_GLOBAL_STRIDE = 0xA0
SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_DWORDS = 20
SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_BYTES = 20 * 4
SOURCE_FASTVIEW_NATIVE_LIVE_CLUB_SIDE_BLOCK_OFFSET = 0x244
SOURCE_FASTVIEW_NATIVE_SIDE_COUNT = 2
SOURCE_FASTVIEW_NATIVE_GLOBAL_SIDE_BYTES = (
    SOURCE_FASTVIEW_NATIVE_SECOND_SIDE_GLOBAL_STRIDE
    * SOURCE_FASTVIEW_NATIVE_SIDE_COUNT
)
SOURCE_FASTVIEW_POST_MODAL_PLAYER_MUTATION_FIRST_VA = 0x4182F0
SOURCE_FASTVIEW_POST_MODAL_PLAYER_MUTATION_SUBSEQUENT_VA = 0x4182C0
SOURCE_FASTVIEW_POST_MODAL_PLAYER_VALUE_SETTER_VA = 0x4EA330
SOURCE_FASTVIEW_POST_MODAL_PLAYER_BYTE_SETTER_VA = 0x4EA350


class OriginalFastViewTwoSideWritebackError(ValueError):
    pass


def source_fastview_original_pre_modal_two_flag_reset_6c1cf0(
    *, original_a145f0_a145f4_eight_bytes_before: bytes,
) -> bytes:
    """Exactly 0x533203 -> 0x6C1CF0, after two-side prep, before 0x533BF0.

    The original XOR EAX,EAX, then performs two DWORD stores, at
    0xA145F0 and 0xA145F4. No other source global is claimed altered.
    This immutable projection neither initializes a FastView modal nor
    simulates any team, player, event, or match-world side effect.
    """
    before = original_a145f0_a145f4_eight_bytes_before
    if type(before) is not bytes or len(before) != 8:
        raise OriginalFastViewTwoSideWritebackError(
            "actual original two adjacent pre-modal global DWORDs required"
        )
    return bytes(8)


@dataclass(frozen=True)
class SourceFastViewTwoSideBlockState:
    first_side_bytes: bytes
    second_side_bytes: bytes

    def __post_init__(self) -> None:
        for payload in (self.first_side_bytes, self.second_side_bytes):
            if type(payload) is not bytes:
                raise OriginalFastViewTwoSideWritebackError(
                    "native side memory must be immutable bytes")
            if len(payload) < (
                SOURCE_FASTVIEW_NATIVE_LIVE_CLUB_SIDE_BLOCK_OFFSET
                + SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_BYTES
            ):
                raise OriginalFastViewTwoSideWritebackError(
                    "native side memory must contain original +0x244..+0x293 block")


def _native_global_side(global_mem: bytes) -> None:
    if type(global_mem) is not bytes or len(global_mem) != SOURCE_FASTVIEW_NATIVE_GLOBAL_SIDE_BYTES:
        raise OriginalFastViewTwoSideWritebackError(
            "original two-side global memory must be exactly 0x140 bytes")


def source_fastview_pre_modal_two_side_block_values_533bf0(
    *, live_side_records: SourceFastViewTwoSideBlockState,
    original_global_side_memory: bytes,
) -> bytes:
    """Native 0x533BF0 pre-modal two 20-DWORD state copies; no match."""
    if type(live_side_records) is not SourceFastViewTwoSideBlockState:
        raise OriginalFastViewTwoSideWritebackError("both authentic club side records required")
    _native_global_side(original_global_side_memory)
    out = bytearray(original_global_side_memory)
    for side_index, payload in enumerate(
        (live_side_records.first_side_bytes, live_side_records.second_side_bytes)
    ):
        g = side_index * SOURCE_FASTVIEW_NATIVE_SECOND_SIDE_GLOBAL_STRIDE
        r = SOURCE_FASTVIEW_NATIVE_LIVE_CLUB_SIDE_BLOCK_OFFSET
        out[g:g + SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_BYTES] = (
            payload[r:r + SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_BYTES]
        )
    return bytes(out)


def source_fastview_post_modal_two_side_block_values_533ca0(
    *, live_side_records: SourceFastViewTwoSideBlockState,
    original_global_side_memory_after_modal: bytes,
) -> SourceFastViewTwoSideBlockState:
    """Native 0x533CA0 post-modal block-copy subset, NOT complete edit save.

    Original callback also modifies player records based on live lists
    and side-global scores. This model returns only the 2×80 bytes
    replacing each source side record at +0x244. It never changes
    persistent team state or processes the original linked edit queue.
    """
    if type(live_side_records) is not SourceFastViewTwoSideBlockState:
        raise OriginalFastViewTwoSideWritebackError("both authentic club side records required")
    _native_global_side(original_global_side_memory_after_modal)
    outputs = []
    for index, payload in enumerate(
        (live_side_records.first_side_bytes, live_side_records.second_side_bytes)
    ):
        updated = bytearray(payload)
        r = SOURCE_FASTVIEW_NATIVE_LIVE_CLUB_SIDE_BLOCK_OFFSET
        g = index * SOURCE_FASTVIEW_NATIVE_SECOND_SIDE_GLOBAL_STRIDE
        updated[r:r + SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_BYTES] = (
            original_global_side_memory_after_modal[
                g:g + SOURCE_FASTVIEW_NATIVE_SIDE_BLOCK_BYTES
            ]
        )
        outputs.append(bytes(updated))
    return SourceFastViewTwoSideBlockState(outputs[0], outputs[1])


# ORIGINAL 0x533270 initializes both live side snapshots in one loop:
# 0x533370 -> 0x6C1D00 copies 389 DWORDs of the native original
# stage owner to 0xA14AD0 + 1556*side. 0x533B20 -> 0x6C1D30
# then copies 70 DWORDs to 0xA14898 + 280*side and transforms
# that 280B side buffer using full owner +0xFC count, +0x100 byte,
# +0x13C+0x48*ordinal native starter flags and 0x6C1E50's
# source-only position/rank compatibility rules.
SOURCE_FASTVIEW_TWO_SIDE_STAGE_SETUP_VA = 0x533270
SOURCE_FASTVIEW_CLUB_STAGE_POPULATOR_VA = 0x533370
SOURCE_FASTVIEW_TACTICAL_STAGE_POPULATOR_VA = 0x533B20
SOURCE_FASTVIEW_FULL_SIDE_COPY_VA = 0x6C1D00
SOURCE_FASTVIEW_TACTICAL_SIDE_INIT_VA = 0x6C1D30
SOURCE_FASTVIEW_TACTICAL_RANK_COMPAT_VA = 0x6C1E50
SOURCE_FASTVIEW_FULL_SIDE_BYTES = 0x185 * 4
SOURCE_FASTVIEW_TACTICAL_SIDE_BYTES = 0x46 * 4
SOURCE_FASTVIEW_GLOBAL_FULL_SIDE_VA = 0xA14AD0
SOURCE_FASTVIEW_GLOBAL_TACTICAL_SIDE_VA = 0xA14898
SOURCE_FASTVIEW_FULL_SIDE_COUNT_DWORD_OFFSET = 0xFC
SOURCE_FASTVIEW_FULL_SIDE_FLAG_BYTE_OFFSET = 0x100
SOURCE_FASTVIEW_FULL_SIDE_STARTER_FLAGS_OFFSET = 0x13C
SOURCE_FASTVIEW_FULL_SIDE_PLAYER_STRIDE = 0x48
SOURCE_FASTVIEW_TACTICAL_COUNT_DWORD_OFFSET = 0x14
SOURCE_FASTVIEW_TACTICAL_POSITION_DWORDS_OFFSET = 0x18
SOURCE_FASTVIEW_TACTICAL_POSITION_RANK_DWORDS_OFFSET = 0x60
SOURCE_FASTVIEW_TACTICAL_CURRENT_FLAG_BYTE_OFFSET = 0xF0
SOURCE_FASTVIEW_TACTICAL_AVAILABLE_BYTE_OFFSET = 0xF1
SOURCE_FASTVIEW_TACTICAL_ORDER_BYTES_OFFSET = 0xF2
SOURCE_FASTVIEW_TACTICAL_RESERVE_BYTES_OFFSET = 0x104
# Full owner 0x13C+0x48*(N-1) must remain within its 1556 bytes:
# original roster size beyond 18 cannot fit both native source arrays.
SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MIN = 11
SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MAX = 18


def _original_position_rank_compatible_6c1e50(position: int, rank: int) -> bool:
    """Exact original native 0x6C1E50 equality and position alias pairs."""
    if position == rank:
        return True
    aliases = (
        frozenset((18, 19)),
        frozenset((9, 12, 15)),
        frozenset((4, 8)),
        frozenset((2, 6)),
        frozenset((3, 7)),
    )
    return any(position in group and rank in group for group in aliases)


def source_fastview_native_tactical_280_init_6c1d30(
    *, native_full_side_1556: bytes,
    native_raw_tactical_280: bytes,
) -> bytes:
    """Original source-bounded single-side 0x6C1D30 280-byte value result.

    This models original ordering, compatible position ranking and per-
    player reserve/status flags in the global scratch buffer. It does
    not write the live club source, perform a player substitution,
    calculate a match or commit original 0x533CA0 player setters.
    Fail closed when authentic count/ownership cannot be established.
    """
    from struct import unpack_from, pack_into

    if type(native_full_side_1556) is not bytes or len(native_full_side_1556) != SOURCE_FASTVIEW_FULL_SIDE_BYTES:
        raise OriginalFastViewTwoSideWritebackError("native original 1556-byte side owner required")
    if type(native_raw_tactical_280) is not bytes or len(native_raw_tactical_280) != SOURCE_FASTVIEW_TACTICAL_SIDE_BYTES:
        raise OriginalFastViewTwoSideWritebackError("native original 280-byte tactical source required")
    count = unpack_from("<I", native_full_side_1556, SOURCE_FASTVIEW_FULL_SIDE_COUNT_DWORD_OFFSET)[0]
    raw_count = unpack_from("<I", native_raw_tactical_280, SOURCE_FASTVIEW_TACTICAL_COUNT_DWORD_OFFSET)[0]
    if count != raw_count or not SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MIN <= count <= SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MAX:
        raise OriginalFastViewTwoSideWritebackError(
            "original staged counts must agree and have 11..18 verified player records"
        )
    side = bytearray(native_raw_tactical_280)
    for ordinal in range(count):
        side[SOURCE_FASTVIEW_TACTICAL_ORDER_BYTES_OFFSET + ordinal] = ordinal
    cursor = 0
    # EBP values 1..19; for each, source loops exactly 11 ranked
    # starters (not every listed substitute), calling 0x6C1E50.
    for rank in range(1, 20):
        for ordinal in range(11):
            position = unpack_from(
                "<I", side, SOURCE_FASTVIEW_TACTICAL_POSITION_DWORDS_OFFSET + ordinal * 4
            )[0]
            if _original_position_rank_compatible_6c1e50(position, rank):
                pack_into(
                    "<I", side,
                    SOURCE_FASTVIEW_TACTICAL_POSITION_RANK_DWORDS_OFFSET + ordinal * 4,
                    cursor,
                )
                cursor += 1
    side[SOURCE_FASTVIEW_TACTICAL_CURRENT_FLAG_BYTE_OFFSET] = 3
    available = native_full_side_1556[SOURCE_FASTVIEW_FULL_SIDE_FLAG_BYTE_OFFSET]
    for ordinal in range(count):
        side[SOURCE_FASTVIEW_TACTICAL_ORDER_BYTES_OFFSET + ordinal] = ordinal
        side[SOURCE_FASTVIEW_TACTICAL_RESERVE_BYTES_OFFSET + ordinal] = (
            1 if ordinal >= 11 else 0
        )
        if ordinal < 11 and native_full_side_1556[
            SOURCE_FASTVIEW_FULL_SIDE_STARTER_FLAGS_OFFSET
            + SOURCE_FASTVIEW_FULL_SIDE_PLAYER_STRIDE * ordinal
        ]:
            available = (available - 1) & 0xFF
    side[SOURCE_FASTVIEW_TACTICAL_AVAILABLE_BYTE_OFFSET] = available
    return bytes(side)


@dataclass(frozen=True)
class SourceFastViewTwoSideNativeTacticalScratch:
    original_full_side_global_memory: bytes
    original_tactics_side0: bytes
    original_tactics_side1: bytes


def source_fastview_native_two_side_setup_533270(
    *, native_full_side0_1556: bytes, native_full_side1_1556: bytes,
    native_raw_tactics_side0_280: bytes, native_raw_tactics_side1_280: bytes,
) -> SourceFastViewTwoSideNativeTacticalScratch:
    """Two source-ordered 0x6C1D00/0x6C1D30 stages before modal.

    Pure: both sides are fully verified and computed before any result
    object is returned. Original source 0x533270 performs additional
    calendar, effects and user-data initialization NOT modeled here.
    """
    first = source_fastview_native_tactical_280_init_6c1d30(
        native_full_side_1556=native_full_side0_1556,
        native_raw_tactical_280=native_raw_tactics_side0_280,
    )
    second = source_fastview_native_tactical_280_init_6c1d30(
        native_full_side_1556=native_full_side1_1556,
        native_raw_tactical_280=native_raw_tactics_side1_280,
    )
    return SourceFastViewTwoSideNativeTacticalScratch(
        original_full_side_global_memory=native_full_side0_1556+native_full_side1_1556,
        original_tactics_side0=first,
        original_tactics_side1=second,
    )


# Original 0x533B20 reads selected original match object's
# side +0x5A4/+0xB54 player count and passes packed side pointer
# at +0x5A8/+0xB58 to 0x533B70. Native 0x533B70 fills the first
# five tactical DWORDs, +0x14 player count, and three N-long DWORD
# arrays at +0x18, +0x60, +0xA8. The original 280B stack scratch
# contains other bytes NOT written by 0x533B70; a valid source
# projection MUST retain those bytes, not assume zero initialization.
SOURCE_FASTVIEW_TACTICAL_RAW_POPULATOR_VA = 0x533B70
SOURCE_FASTVIEW_TACTICAL_MATCH_SIDE_SELECTION_VA = 0x533B20
SOURCE_FASTVIEW_TACTICAL_PACKED_POSITIONS_BYTE_OFFSET = 0x16
SOURCE_FASTVIEW_TACTICAL_PACKED_RANK_BYTE_OFFSET = 0x28
SOURCE_FASTVIEW_TACTICAL_PACKED_THIRD_BYTE_OFFSET = 0x04
SOURCE_FASTVIEW_TACTICAL_THIRD_DWORDS_OFFSET = 0xA8


def source_fastview_native_raw_tactical_280_from_packed_533b70(
    *, original_raw_stack_280: bytes, original_packed_side: bytes,
    native_player_count: int,
) -> bytes:
    """Authenticated original packed side -> 280B tactical scratch writes.

    0x533B70 does NOT initialize every byte in its 280B destination.
    Caller must provide the actual original scratch bytes. The 0x533B20
    side pointer and full player's data remain separate verification
    requirements; passing guessed packed bytes cannot validate gameplay.
    """
    from struct import unpack_from, pack_into
    if type(original_raw_stack_280) is not bytes or len(original_raw_stack_280) != SOURCE_FASTVIEW_TACTICAL_SIDE_BYTES:
        raise OriginalFastViewTwoSideWritebackError("authentic 280-byte original stack scratch required")
    if type(native_player_count) is not int or not SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MIN <= native_player_count <= SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MAX:
        raise OriginalFastViewTwoSideWritebackError("original native 11..18 player count required")
    if (type(original_packed_side) is not bytes or
            len(original_packed_side) < SOURCE_FASTVIEW_TACTICAL_PACKED_RANK_BYTE_OFFSET + native_player_count):
        raise OriginalFastViewTwoSideWritebackError(
            "original packed side source must contain all three player byte arrays"
        )
    packed = unpack_from("<I", original_packed_side, 0)[0]
    scratch = bytearray(original_raw_stack_280)
    for at, value in (
        (0x00, packed & 0xFF),
        (0x04, (packed >> 8) & 3),
        (0x08, (packed >> 14) & 3),
        (0x0C, (packed >> 16) & 3),
        (0x10, (packed >> 12) & 3),
        (0x14, native_player_count),
    ):
        pack_into("<I", scratch, at, value)
    for i in range(native_player_count):
        pack_into("<I", scratch, 0x18 + i*4,
                  original_packed_side[SOURCE_FASTVIEW_TACTICAL_PACKED_POSITIONS_BYTE_OFFSET + i])
        pack_into("<I", scratch, 0x60 + i*4,
                  original_packed_side[SOURCE_FASTVIEW_TACTICAL_PACKED_RANK_BYTE_OFFSET + i])
        pack_into("<I", scratch, SOURCE_FASTVIEW_TACTICAL_THIRD_DWORDS_OFFSET + i*4,
                  original_packed_side[SOURCE_FASTVIEW_TACTICAL_PACKED_THIRD_BYTE_OFFSET + i])
    return bytes(scratch)
