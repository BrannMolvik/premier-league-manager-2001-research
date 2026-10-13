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
SOURCE_ORIGINAL_ZERO_FLAGS_NATIVE_KINDS = frozenset((1,6))
SOURCE_ORIGINAL_INHERITS_CUP_FLAGS_NATIVE_KINDS = frozenset((2,3,4,5))


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
