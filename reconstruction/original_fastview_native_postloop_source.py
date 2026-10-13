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


SOURCE_FASTVIEW_POSTLOOP_24_BYTE_READER_VA = 0x62B6B0
SOURCE_FASTVIEW_POSTLOOP_24_SLOT_GLOBAL_WRITER_VA = 0x6CA900
SOURCE_FASTVIEW_POSTLOOP_24_SOURCE_BYTE_START = 0x112D
SOURCE_FASTVIEW_POSTLOOP_24_SOURCE_COUNT = 24
SOURCE_FASTVIEW_POSTLOOP_24_GLOBAL_VA = 0xA257B8
SOURCE_FASTVIEW_POSTLOOP_MATCH_POINTER_OFFSET = 0xB60
SOURCE_FASTVIEW_POSTLOOP_MATCH_VALUE_OFFSET = 0xB68
SOURCE_FASTVIEW_POSTLOOP_MATCH_POINTER_WRITER_VA = 0x6CBD80
SOURCE_FASTVIEW_POSTLOOP_MATCH_VALUE_WRITER_VA = 0x6CA8F0
SOURCE_FASTVIEW_POSTLOOP_ORIGINAL_MODE_POINTER_VA = 0x877534
SOURCE_FASTVIEW_POSTLOOP_SOURCE_MODE_WRITER_VA = 0x6CA910
SOURCE_FASTVIEW_POSTLOOP_SOURCE_GRID_RESET_VA = 0x6C2890
SOURCE_FASTVIEW_POSTLOOP_GRID_108_BYTES_VA = 0xA14828


@dataclass(frozen=True)
class SourceFastViewOriginalPostLoopSlotAndResetValues:
    original_24_dword_global_a257b8: bytes
    original_match_b60_pointer_offset_intent: int
    original_match_b68_dword_to_a25874: int
    original_877534_null_mode_to_a2578c: int
    source_grid_a14828_108_after_reset: bytes


def source_fastview_original_postloop_slot_and_reset_533270(
    *, original_match_object: bytes,
    original_global_slots_a257b8_before: bytes,
    original_grid_a14828_before: bytes,
    original_877534_pointer_is_nonzero: bool,
) -> SourceFastViewOriginalPostLoopSlotAndResetValues:
    """Exact later 0x533305..0x533359 original stage writes, value-only.

    Original loops ESI=0..23: ECX=match, calls 0x62B6B0 reading
    zero-extended BYTE match+0x112D+i through stack output DWORD,
    then 0x6CA900 stores that DWORD at global0xA257B8+4*i.
    Next 0x6CBD80 stores POINTER (match+0xB60) at global0xA258C0;
    this model preserves only the pointer-relative offset intent,
    since a real original address cannot be manufactured.
    It writes original match DWORD+0xB68 to 0xA25874 via 0x6CA8F0.
    0x6CA910 stores DWORD 1 iff global0x877534 was NULL, otherwise 0,
    at 0xA2578C. Finally 0x6C2890 loops two 18-entry grids
    (3 bytes per cell) clearing exactly global A14828..A14893
    (108 bytes). This is NOT live match/tick processing.
    """
    if (type(original_match_object) is not bytes or
            len(original_match_object)<SOURCE_FASTVIEW_POSTLOOP_24_SOURCE_BYTE_START+24):
        raise SourceFastViewOriginalPostLoopError(
            "actual original match+0x112D..+0x1144 24 source bytes required")
    if (type(original_global_slots_a257b8_before) is not bytes or
            len(original_global_slots_a257b8_before)!=24*4):
        raise SourceFastViewOriginalPostLoopError(
            "original 24 DWORD global slots before stage required")
    if (type(original_grid_a14828_before) is not bytes or
            len(original_grid_a14828_before)!=108):
        raise SourceFastViewOriginalPostLoopError(
            "original 108-byte two-row grid required")
    if type(original_877534_pointer_is_nonzero) is not bool:
        raise SourceFastViewOriginalPostLoopError(
            "qualified original global 0x877534 NULL predicate required")
    updated=bytearray(original_global_slots_a257b8_before)
    for i in range(24):
        pack_into("<I", updated, i*4, original_match_object[0x112D+i])
    return SourceFastViewOriginalPostLoopSlotAndResetValues(
        original_24_dword_global_a257b8=bytes(updated),
        original_match_b60_pointer_offset_intent=SOURCE_FASTVIEW_POSTLOOP_MATCH_POINTER_OFFSET,
        original_match_b68_dword_to_a25874=unpack_from("<I",original_match_object,0xB68)[0],
        original_877534_null_mode_to_a2578c=(
            0 if original_877534_pointer_is_nonzero else 1),
        source_grid_a14828_108_after_reset=b"\x00"*108,
    )


@dataclass(frozen=True)
class SourceFastViewOriginalEntireSetupValueStage:
    """One source-ordered 0x533270 projection; not real match state."""
    two_sided_roster_and_tactics: object
    native_three_statistics_globals: SourceFastViewOriginalThreeGlobalValues
    native_match_slots_and_reset: SourceFastViewOriginalPostLoopSlotAndResetValues


def source_fastview_original_complete_value_stage_533270(
    *, original_live_match_object: bytes,
    original_side0,
    original_side1,
    original_human_registry_club_ids_in_link_order: tuple[int, ...],
    original_country_name_indexes_germany_france_england: tuple[int, int, int],
    original_three_global_buffers_before: tuple[bytes, bytes, bytes],
    original_uninitialized_stack_values_when_mode_four: tuple[int, int, int] | None,
    original_global_slots_a257b8_before: bytes,
    original_grid_a14828_before: bytes,
    original_877534_pointer_is_nonzero: bool,
) -> SourceFastViewOriginalEntireSetupValueStage:
    """Read-only joined 0x533270 native TWO-sided, statistics, 24-slot init.

    Original source stage ownership/read order:
     1) 0x533370→6C1D00 / 0x533B20→6C1D30 for side0 then side1;
     2) 0x631270/631290/6CC890 for mode-dependent 2 or 4 iterations;
     3) 0x62B6B0/6CA900 for 24 source match byte slots;
     4) 0x6CBD80/6CA8F0/6CA910 original scalar and pointer writes;
     5) 0x6C2890 108-byte two-row native reset.
    Returns only immutable *source values* after EVERY bounded dependency
    has been validated, with no local/global state changes. Does not
    resolve original DBRPlayer/DBRClub native heap identities, perform
    the FastView 0x5331C0 modal, mutate GameState or process PResults.
    """
    from original_fastview_native_full_side_setup import (
        source_fastview_original_first_two_side_init_533270,
    )
    sides = source_fastview_original_first_two_side_init_533270(
        original_match_object=original_live_match_object,
        source_side0=original_side0,
        source_side1=original_side1,
        original_human_registry_club_ids_in_link_order=(
            original_human_registry_club_ids_in_link_order),
        original_country_name_indexes_germany_france_england=(
            original_country_name_indexes_germany_france_england))
    statistics = source_fastview_original_postloop_global_values_533270(
        original_live_match_object=original_live_match_object,
        original_three_global_buffers_before=original_three_global_buffers_before,
        original_uninitialized_stack_values_when_mode_four=(
            original_uninitialized_stack_values_when_mode_four))
    slots = source_fastview_original_postloop_slot_and_reset_533270(
        original_match_object=original_live_match_object,
        original_global_slots_a257b8_before=original_global_slots_a257b8_before,
        original_grid_a14828_before=original_grid_a14828_before,
        original_877534_pointer_is_nonzero=original_877534_pointer_is_nonzero)
    return SourceFastViewOriginalEntireSetupValueStage(sides,statistics,slots)
