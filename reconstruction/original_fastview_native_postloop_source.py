"""Original FastView 0x533270 post-first-loop global three-value projection.

Owner-private original footballmanager.exe SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
is statically inspected, not executed. This is the exact bounded
0x631270->0x631290->0x6CC890 values-only sequence. No match play,
original heap/pointer resolution, 24 tick initializers, event queues,
match simulation, status writeback or UI is executed.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

SOURCE_FASTVIEW_POSTLOOP_SELECTOR_VA = 0x631270
SOURCE_FASTVIEW_POSTLOOP_AGGREGATOR_VA = 0x631290
SOURCE_FASTVIEW_POSTLOOP_GLOBAL_WRITER_VA = 0x6CC890
SOURCE_FASTVIEW_POSTLOOP_COUNT_WORD_OFFSET = 0xFF8
SOURCE_FASTVIEW_POSTLOOP_MATCH_18_SENTINEL = 0x12
SOURCE_FASTVIEW_POSTLOOP_TWO_CASE_OFFSETS = (0x1058, 0x10B8, 0x1118)
SOURCE_FASTVIEW_POSTLOOP_GLOBAL_HEADS = (0xA25940, 0xA25950, 0xA25930)


class SourceFastViewOriginalPostLoopError(ValueError):
    pass


@dataclass(frozen=True)
class SourceFastViewOriginalThreeGlobalValues:
    source_631270_iteration_count: int
    native_three_dword_parameters: tuple[int, int, int]
    original_globals_a25940_bytes: bytes
    original_globals_a25950_bytes: bytes
    original_globals_a25930_bytes: bytes
    native_631290_wrote_outputs: bool


def source_fastview_original_postloop_global_values_533270(
    *, original_live_match_object: bytes,
    original_three_global_buffers_before: tuple[bytes, bytes, bytes],
    original_uninitialized_stack_values_when_mode_four: tuple[int, int, int] | None,
) -> SourceFastViewOriginalThreeGlobalValues:
    """Source-exact bounded 0x5332BE..0x533302 stage, no world mutation.

    0x631270 returns TWO when match DWORD+0xFF8 equals 18, otherwise
    FOUR, using NEG/SBB flag semantics. The actual 0x631290 call has
    jump-table cases 0/1/2/3; thus for mode FOUR it returns without
    writing any of its three passed output pointers. The 533270
    caller nonetheless publishes the EXISTING three raw stack DWORDs
    via 0x6CC890 four times. They are NOT necessarily zero, and must
    come from a genuine source-qualified stack state.

    Mode TWO enters 631290 table case 2, reads three two-DWORD ranges
    at match +0x1058, +0x10B8 and +0x1118, adds with native DWORD
    overflow, divides each resulting unsigned sum by two, and writes
    the three values to globals at A25940/A25950/A25930 for i=0,1.
    Other two entries of each original 4-DWORD global are untouched.
    """
    if type(original_live_match_object) is not bytes or len(original_live_match_object) < 0xFFC:
        raise SourceFastViewOriginalPostLoopError(
            "original match record +0xFF8 selector DWORD required")
    if (type(original_three_global_buffers_before) is not tuple
            or len(original_three_global_buffers_before) != 3
            or any(type(x) is not bytes or len(x) != 16
                   for x in original_three_global_buffers_before)):
        raise SourceFastViewOriginalPostLoopError(
            "three exact original 4-DWORD destination buffers required")
    source_mode_field=unpack_from("<I",original_live_match_object,0xFF8)[0]
    count=2 if source_mode_field==0x12 else 4
    if count==2:
        if original_uninitialized_stack_values_when_mode_four is not None:
            raise SourceFastViewOriginalPostLoopError(
                "source unvisited stack values cannot be supplied in mode two")
        if len(original_live_match_object)<0x1120:
            raise SourceFastViewOriginalPostLoopError(
                "original 631290 case2 requires match source through +0x111F")
        values=[]
        for offset in SOURCE_FASTVIEW_POSTLOOP_TWO_CASE_OFFSETS:
            a,b=unpack_from("<II",original_live_match_object,offset)
            values.append(((a+b)&0xFFFFFFFF)//2)
        native_outputs=True
    else:
        tup=original_uninitialized_stack_values_when_mode_four
        if (type(tup) is not tuple or len(tup)!=3 or
            any(type(v) is not int or not 0<=v<=0xFFFFFFFF for v in tup)):
            raise SourceFastViewOriginalPostLoopError(
                "original three native caller stack values required when 631290 mode4 writes none")
        values=list(tup)
        native_outputs=False
    original_globals=[]
    for initial,value in zip(original_three_global_buffers_before,values):
        updated=bytearray(initial)
        for index in range(count):
            pack_into("<I",updated,4*index,value)
        original_globals.append(bytes(updated))
    return SourceFastViewOriginalThreeGlobalValues(
        source_631270_iteration_count=count,
        native_three_dword_parameters=tuple(values),
        original_globals_a25940_bytes=original_globals[0],
        original_globals_a25950_bytes=original_globals[1],
        original_globals_a25930_bytes=original_globals[2],
        native_631290_wrote_outputs=native_outputs,
    )
