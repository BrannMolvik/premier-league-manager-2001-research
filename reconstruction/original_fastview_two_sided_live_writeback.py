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
