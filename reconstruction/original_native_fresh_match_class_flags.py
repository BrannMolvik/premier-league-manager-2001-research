"""Authentic initial LeagueMatch flags and dated-event FAMILY, not IDs.

Owner-authorized original footballmanager.exe, 4,714,541 bytes, SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
was inspected STATICALLY ONLY. Original 0x5103D0 zeros match+0x44 at
0x5104CF. Ordinary original LeagueMatch subclasses retain zero, while
0x510520 composes bits 1/2/3 using three exact source DWORD arguments.
The original vtable+0x28 returns a native type kind, and vtable+0x30
chooses one of two dated event collections. This source-only receipt
models those initial writes, NOT an actual original runtime record,
constructor instance, event+0x0C serial, +8 later link, or match callback.
"""
from __future__ import annotations
from dataclasses import dataclass

from original_native_saved_event_link_writer import (
    SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
    SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA,
)
from original_leaguematch_native_process_owners import (
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
)


class OriginalFreshMatchFlagsSourceError(ValueError):
    """Native class/argument source missing or not reached."""


SOURCE_ORIGINAL_BASE_MATCH_INIT_VA = 0x5103D0
SOURCE_ORIGINAL_BASE_MATCH_FLAGS_INITIALIZE_VA = 0x5104CF
SOURCE_ORIGINAL_CUP_MATCH_FLAGS_CONSTRUCTOR_VA = 0x510520
SOURCE_ORIGINAL_CUP_MATCH_FLAGS_COMPOSE_VA = 0x510567
SOURCE_ORIGINAL_CLASS3_FORCED_FLAGS_ARGUMENTS_VA = (0x51061D,0x51061F)
SOURCE_ORIGINAL_CLASS4_ZERO_FLAGS_ARGUMENTS_VA = (0x510654,0x510656,0x510658)
SOURCE_ORIGINAL_CLASS5_FORCED_MIDDLE_FLAG_VA = 0x51069D
SOURCE_ORIGINAL_CUP_FLAG_BITS = 0x0E

# Every actual known native subclass that executes source 0x5103D0.
# Native constructor v+0x28 constant source method results:
# 0x651E20=1, 0x6CE1E0=2, 0x6CE1F0=3,
# 0x6CECB0=4, 0x650010=5, 0x650250=6.
# The original 0x7C4CE4 base class has a non-constant 0x668766 callback
# and is explicitly not promoted here to a saved-match type.
SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS = {
    0x7C4C24: 1,
    0x7C9D9C: 2,
    0x7C9E80: 3,
    0x7C9EF8: 4,
    0x7C9F70: 5,
    0x7C9E14: 6,
}
SOURCE_ORIGINAL_ZERO_FLAGS_NATIVE_KINDS = frozenset((1,4,6))
SOURCE_ORIGINAL_INHERITS_CUP_FLAGS_NATIVE_KINDS = frozenset((2,3,5))


@dataclass(frozen=True)
class OriginalFreshMatchFlagsSourceReceipt:
    original_native_class_vtable: int
    source_native_virtual28_kind: int
    initial_original_flags44: int
    source_native_date_collection_pointer: int
    source_original_event8_is_zero_immediately_after_constructor: bool
    original_event_identity_is_known: bool = False


def source_original_fresh_match_flags44_and_collection(
    *,
    original_native_class_vtable: int,
    original_source_510520_argument_dword_esp18: int | None = None,
    original_source_510520_argument_dword_esp1c: int | None = None,
    original_source_510520_argument_dword_esp20: int | None = None,
) -> OriginalFreshMatchFlagsSourceReceipt:
    """Source only: base +0x44=0, inherited Cup bits, v+0x30 collection.

    Original 0x510520:
       flags = (((arg[esp+20]&1)*2 | (arg[esp+1c]&1))*2
                | (arg[esp+18]&1))*2 | (old_flags&0xF1)
    and since the immediately called native base sets old_flags=0,
    the fresh flags are low bits1/2/3 only.
    Class4 constructor 0x510640 hardcodes all three relevant args
    zero, so no source flag arguments are required. Class3 0x510600
    hardcodes the two lower args 1/1; class5 0x510680 hardcodes
    the middle arg 1. Their remaining relevant args must come from
    the actual reached native wrapper, not a guessed match type.
    Original original v+0x30:
       type1/6: 0x651980 returns AL 0 (primary);
       type2/3/4/5: 0x5112C0 returns AL 1 only iff native kind
       is 2 and match+0x44 bit2 is CLEAR, else primary.
    Native class (0x7C4CE4) with nonconstant virtual+0x28
    is deliberately unsupported; loaded/current runtime flags
    may be different and must be separately sourced.
    """
    vt=original_native_class_vtable
    kind=SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS.get(vt)
    if type(vt) is not int or kind is None or vt not in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
        raise OriginalFreshMatchFlagsSourceError(
            "actual supported original native LeagueMatch subclass required")
    args=(original_source_510520_argument_dword_esp18,
          original_source_510520_argument_dword_esp1c,
          original_source_510520_argument_dword_esp20)
    if kind in SOURCE_ORIGINAL_ZERO_FLAGS_NATIVE_KINDS:
        if any(x is not None for x in args):
            raise OriginalFreshMatchFlagsSourceError(
                "original ordinary LeagueMatch ctor does not reach 0x510520 flag arguments")
        flags=0
    elif kind in SOURCE_ORIGINAL_INHERITS_CUP_FLAGS_NATIVE_KINDS:
        if any(type(x) is not int or not 0<=x<=0xFFFFFFFF for x in args):
            raise OriginalFreshMatchFlagsSourceError(
                "three authentic original reached 0x510520 argument DWORDs required")
        a,b,c=args
        if kind==3 and (a&1,b&1)!=(1,1):
            raise OriginalFreshMatchFlagsSourceError(
                "native 0x510600 forces 0x510520 source arguments a=1,b=1")
        if kind==5 and b&1!=1:
            raise OriginalFreshMatchFlagsSourceError(
                "native 0x510680 forces 0x510520 source argument b=1")
        flags=(((c&1)<<3)|((b&1)<<2)|((a&1)<<1))
    else:
        raise OriginalFreshMatchFlagsSourceError("native flag constructor owner unknown")
    if (flags & ~SOURCE_ORIGINAL_CUP_FLAG_BITS):
        raise OriginalFreshMatchFlagsSourceError("native fresh flags outside proven bits")
    # The original 0x5112C0 is conditional on *kind*, not just vtable
    # naming conventions or a generic Python Cup label.
    secondary=(kind==2 and not flags & 0x04)
    return OriginalFreshMatchFlagsSourceReceipt(
        vt,kind,flags,
        (SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA if secondary
         else SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA),
        True)



@dataclass(frozen=True)
class OriginalFreshEventSerialSourceReceipt:
    """Pure native constructor arithmetic, not a materialized live event."""
    source_fresh_match: OriginalFreshMatchFlagsSourceReceipt
    original_selected_collection_counter_before: int
    source_original_event_id_dword_0c: int
    original_selected_collection_counter_after: int
    source_original_event8_immediately_after_constructor: int = 0

    @property
    def original_live_registry_pointer_is_known(self) -> bool:
        return False


def source_original_fresh_match_event_serial_510380(
    *,
    qualified_fresh_source_match: OriginalFreshMatchFlagsSourceReceipt,
    original_selected_collection_counter_before: int,
) -> OriginalFreshEventSerialSourceReceipt:
    """Join source new-match class collection and 0x510380 event serial.

    Original 0x5103D0 selects native date owner 0x947AD8 or 0x947AF0
    from reached owner virtual+0x30; 0x510380 then uses ONLY that
    selected owner's source +0x0C serial. Source event+0x0C is
       2 * unsigned_serial + (owner==0x947AF0 ? 1 : 0)
    modulo DWORD, and the selected owner's serial increments by one.
    Another original event can increment the counter before this
    operation; a caller MUST supply a genuine source-qualified
    BEFORE-counter, not count Python fixtures. No native Side/club
    pointers, event+0x08 subsequent state, queue pointer, or executable
    callback is synthesized.
    """
    if type(qualified_fresh_source_match) is not OriginalFreshMatchFlagsSourceReceipt:
        raise OriginalFreshMatchFlagsSourceError(
            "source-qualified original fresh class/flag receipt required")
    source=qualified_fresh_source_match
    if (source.original_event_identity_is_known or
        not source.source_original_event8_is_zero_immediately_after_constructor or
        source.original_native_class_vtable not in SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS or
        source.source_native_virtual28_kind!=SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS[
            source.original_native_class_vtable
        ]):
        raise OriginalFreshMatchFlagsSourceError(
            "original fresh class/native kind lifecycle is inconsistent")
    flags=source.initial_original_flags44
    kind=source.source_native_virtual28_kind
    if (type(flags) is not int or flags & ~SOURCE_ORIGINAL_CUP_FLAG_BITS or
        (kind in SOURCE_ORIGINAL_ZERO_FLAGS_NATIVE_KINDS and flags != 0)):
        raise OriginalFreshMatchFlagsSourceError(
            "original constructor flags are inconsistent with reached source class")
    expected_collection=(
        SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA if kind==2 and not flags&0x04
        else SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA)
    if source.source_native_date_collection_pointer!=expected_collection:
        raise OriginalFreshMatchFlagsSourceError(
            "native fresh class/bit2 source cannot select asserted date owner")
    counter=original_selected_collection_counter_before
    if type(counter) is not int or not 0<=counter<=0xFFFFFFFF:
        raise OriginalFreshMatchFlagsSourceError(
            "actual selected original collection source serial DWORD required")
    secondary=(source.source_native_date_collection_pointer==
               SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA)
    if not secondary and source.source_native_date_collection_pointer!=SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA:
        raise OriginalFreshMatchFlagsSourceError("unknown original source collection owner")
    return OriginalFreshEventSerialSourceReceipt(
        source,counter,
        (((counter<<1)&0xFFFFFFFF)|int(secondary)),
        (counter+1)&0xFFFFFFFF,
    )
