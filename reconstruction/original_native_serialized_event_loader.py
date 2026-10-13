"""Original 0x616100 seven-way serialized dated-event loader class dispatch.

Original 4,714,541 byte footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Static PE disassembly only. This class/constructor routing metadata is NOT a
serialization parser, a live event instance or proof of native object fields
after unrelated later loader/season callbacks. Original serial type codes
are NOT equivalent to the reconstructed PrimaryScheduleShadowEntry.node_kind.
"""
from __future__ import annotations
from dataclasses import dataclass


class OriginalSerializedEventLoaderSourceError(ValueError):
    """Authentic loader family/type not source-qualified."""


SOURCE_SERIALIZED_EVENT_LOADER_VA = 0x616100
SOURCE_SERIALIZED_EVENT_READ_VA = 0x667E90
SOURCE_SERIALIZED_EVENT_ALLOC_VA = 0x668140
SOURCE_SERIALIZED_EVENT_PTR_WRITEBACK_VA = 0x6163BA
SOURCE_SERIALIZED_EVENT_JUMP_TABLE_VA = 0x6163D0

# SOURCE type 0 is an event but not any of seven LeagueMatch process vtables.
# For each type: (allocated native bytes, source constructor VA, final vtable,
#                source dispatch callsite). The final vtable is a directly
# checked native constructor write, not derived from a local fixture name.
SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH = {
    0: (0x1C, 0x510380, 0x7C9FE8, 0x6161A0),
    1: (0x50, 0x5104F0, 0x7C4C24, 0x61622B),
    2: (0x5C, 0x510520, 0x7C9D9C, 0x6162F5),
    3: (0x5C, 0x510600, 0x7C9E80, 0x616332),
    4: (0x5C, 0x510640, 0x7C9EF8, 0x616369),
    5: (0x5C, 0x510680, 0x7C9F70, 0x6163A1),
    6: (0x50, 0x5105D0, 0x7C9E14, 0x616265),
}

SOURCE_ORIGINAL_LOADER_JUMP_TABLE_ENTRIES_2_TO_5 = (
    0x6162BA,0x6162FF,0x616339,0x616370
)


@dataclass(frozen=True)
class OriginalSerializedEventClassSource:
    original_native_source_type_code: int
    source_allocated_size_bytes: int
    source_constructor_va: int
    source_final_vtable_va: int
    source_call_site_va: int
    source_is_league_match_vtable: bool


def source_original_serialized_event_class_616100(
    *, original_native_serialized_type_code: int,
) -> OriginalSerializedEventClassSource:
    """Classify reached native original loader's 0..6 source type branch.

    Source: 0x616145 checks zero separately, 0x6161F3 tests 1,
    0x616235 tests 6 and 0x6162A7..0x6162B3 2..5 unsigned jump
    table. Higher/unexpected values use different original fallback
    memory; this model refuses to reconstruct its type semantics.
    """
    t=original_native_serialized_type_code
    if type(t) is not int or t not in SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH:
        raise OriginalSerializedEventLoaderSourceError(
            "original serialized event type must be source-verified 0..6")
    size,ctor,vt,site=SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH[t]
    return OriginalSerializedEventClassSource(
        t,size,ctor,vt,site,t!=0)
