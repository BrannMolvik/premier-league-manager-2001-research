"""Original source-backed startup schedule emitter -> native LeagueMatch class.

Private original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
Read-only x86 PE inspection. No original binary is committed/launched.

This identifies constructor CLASS from a verified producer/callsite.
It does NOT instantiate an original event, assign original event +0x0C
identity, native +8 link, +0x44 flags, v+0x10 execution, or imply that a
symbolic clean-room node can be used as a live original runtime object.
"""
from __future__ import annotations
from dataclasses import dataclass

from original_native_serialized_event_loader import (
    SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH,
)


class OriginalScheduleProducerSourceError(ValueError):
    """An original emitted native class is not source-authenticated."""


@dataclass(frozen=True)
class OriginalNativeScheduleConstructorEvidence:
    original_source_producer_va: int
    original_native_constructor_callsite_va: int | None
    original_native_constructor_va: int
    original_native_serialized_type_code: int
    original_native_vtable_va: int

    @property
    def is_live_original_event(self) -> bool:
        """Static constructor identity is NOT actual live native event evidence."""
        return False


# Source producer identity and exact native callsite(s), not names inferred
# from fixture types. In Scottish split BOTH original branches call 0x5104F0,
# so no one particular branch/callsite is claimed for a symbolic emission.
SOURCE_NATIVE_STARTUP_MATCH_PRODUCERS = {
    "fixed_league_match": (0x6173D0, 0x617490, 0x5104F0, 1),
    "league_match": (0x616FC0, 0x617047, 0x5104F0, 1),
    "cup_match": (0x4F64D0, 0x4F66C9, 0x510520, 2),
    "first_leg_match": (0x4F6820, 0x4F6A02, 0x510640, 4),
    "second_leg_match": (0x4F6820, 0x4F6A64, 0x510680, 5),
    "scot_split_league_match": (0x4FAC60, None, 0x5104F0, 1),
}
SOURCE_SCOTTISH_SPLIT_CLASS_CALLSITES = (0x4FADBE, 0x4FAE30)
SOURCE_PROCEDURAL_PAIR_GENERATOR_VA = 0x6170F0
SOURCE_GENERIC_PROCEDURAL_EVENT_EMITTER_VA = 0x616FC0
SOURCE_SCOTTISH_PROCEDURAL_EVENT_OVERRIDE_VA = 0x6170A0


def source_original_schedule_constructor_for_verified_producer(
    *, source_emission_kind: str,
    original_source_producer_va: int,
    original_native_constructor_callsite_va: int | None = None,
) -> OriginalNativeScheduleConstructorEvidence:
    """Require explicit original production source, never a naked node kind.

    The generated procedural League pairs from 0x6170F0 must be
    distinguished from their ACTUAL native event emitter 0x616FC0,
    called for generic League via vtable+0x3C at 0x617310.
    The emitter allocates 0x50, constructs 0x5104F0 at 0x617047,
    resolves its original calendar owner at 0x617071 and inserts
    through 0x615950 at 0x617078. Scottish League vtable+0x3C
    may instead reach 0x6170A0, whose final synthetic cycle is
    retained as pairs rather than constructed as matches.
    This only qualifies emitted class, NOT live original event identity.
    Scottish split uses two class-identical calls and leaves site unknown.
    """
    if type(source_emission_kind) is not str:
        raise OriginalScheduleProducerSourceError("original source emission kind required")
    spec=SOURCE_NATIVE_STARTUP_MATCH_PRODUCERS.get(source_emission_kind)
    if spec is None:
        raise OriginalScheduleProducerSourceError(
            "original emitter-to-native class unresolved for this emission")
    producer,callsite,ctor,serialized=spec
    if type(original_source_producer_va) is not int or original_source_producer_va!=producer:
        raise OriginalScheduleProducerSourceError(
            "original native emitter provenance must match recovered producer")
    if (original_native_constructor_callsite_va is not None and
            (type(original_native_constructor_callsite_va) is not int or
             original_native_constructor_callsite_va not in
             ((SOURCE_SCOTTISH_SPLIT_CLASS_CALLSITES if callsite is None
               else (callsite,))))):
        raise OriginalScheduleProducerSourceError(
            "original native constructor callsite is not source-authenticated")
    if callsite is not None and original_native_constructor_callsite_va!=callsite:
        raise OriginalScheduleProducerSourceError(
            "exact original native constructor callsite required")
    loaded=SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH[serialized]
    if loaded[1]!=ctor:
        raise OriginalScheduleProducerSourceError(
            "original emitted constructor and serialized class conflict")
    return OriginalNativeScheduleConstructorEvidence(
        producer,original_native_constructor_callsite_va,ctor,serialized,loaded[2])
