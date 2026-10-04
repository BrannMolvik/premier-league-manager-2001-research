"""Source-closed numeric event-record routing into the FM2001 chant callback.

The original audio subsystem registers chant enqueue 0x723360 in callback slot
0x86644C. A separate 16-byte source event-record dispatcher at 0x70C97D reads
its numeric type from record +0x00 and routes selected codes through wrappers
that invoke that registered chant callback.

Only numeric code -> chant selector routing is recorded here. The source owner
and human-facing meanings of these 16-byte event records are not yet recovered,
so this module must not equate these codes with MatchCalculator record types or
FastView event names merely because some numbers overlap.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14ChantEventRoutingError(ValueError):
    pass


CHANT_ENQUEUE_VA = 0x723360
CHANT_CALLBACK_SLOT_VA = 0x86644C
AUDIO_EVENT_DISPATCH_VA = 0x70C97D
AUDIO_EVENT_JUMP_TABLE_VA = 0x70D18C
AUDIO_EVENT_RECORD_SIZE = 0x10
AUDIO_EVENT_TYPE_OFFSET = 0x00

HOME_SELECTOR = 0
AWAY_SELECTOR = 1

# Exact dispatch cases that reach the registered chant callback.
# Event-record meanings remain intentionally unnamed.
NUMERIC_EVENT_ROUTES = (
    (9, 0x727710, HOME_SELECTOR),
    (10, 0x7277C0, HOME_SELECTOR),
    (11, 0x727860, HOME_SELECTOR),
    (12, 0x727900, HOME_SELECTOR),
    (13, 0x7279A0, HOME_SELECTOR),
    (14, 0x727A40, AWAY_SELECTOR),
    (15, 0x727A40, AWAY_SELECTOR),
    (16, 0x727A40, AWAY_SELECTOR),
)


@dataclass(frozen=True)
class NumericChantEventRoute:
    event_code: int
    wrapper_va: int
    chant_selector: int
    event_semantics_recovered: bool = False
    matchcalculator_type_equivalence_recovered: bool = False
    fastview_event_equivalence_recovered: bool = False

    def __post_init__(self) -> None:
        if type(self.event_code) is not int or not 1 <= self.event_code <= 30:
            raise Gate14ChantEventRoutingError(
                "numeric audio-event code must be within dispatcher range 1..30"
            )
        if type(self.wrapper_va) is not int or self.wrapper_va <= 0:
            raise Gate14ChantEventRoutingError("wrapper VA must be a positive integer")
        if self.chant_selector not in (HOME_SELECTOR, AWAY_SELECTOR):
            raise Gate14ChantEventRoutingError(
                "source-closed numeric chant route requires selector 0 or 1"
            )
        if (
            self.event_semantics_recovered
            or self.matchcalculator_type_equivalence_recovered
            or self.fastview_event_equivalence_recovered
        ):
            raise Gate14ChantEventRoutingError(
                "numeric chant route cannot promote unrecovered event semantics"
            )


ROUTES = tuple(
    NumericChantEventRoute(code, wrapper, selector)
    for code, wrapper, selector in NUMERIC_EVENT_ROUTES
)


def chant_route_for_numeric_event(event_code: int) -> NumericChantEventRoute | None:
    """Return the exact chant route for one source numeric event code.

    Codes in the dispatcher's 1..30 range that are not source-proven chant
    callers return None rather than being assigned an inferred audio behavior.
    """
    if type(event_code) is not int or not 1 <= event_code <= 30:
        raise Gate14ChantEventRoutingError(
            "numeric audio-event code must be within dispatcher range 1..30"
        )
    for route in ROUTES:
        if route.event_code == event_code:
            return route
    return None


def chant_selector_for_numeric_event(event_code: int) -> int | None:
    route = chant_route_for_numeric_event(event_code)
    return None if route is None else route.chant_selector


@dataclass(frozen=True)
class NumericChantEventRoutingBoundary:
    callback_registration_recovered: bool = True
    numeric_dispatch_recovered: bool = True
    named_event_semantics_recovered: bool = False
    matchcalculator_record_equivalence_recovered: bool = False
    fastview_sender_equivalence_recovered: bool = False

    def __post_init__(self) -> None:
        if not self.callback_registration_recovered or not self.numeric_dispatch_recovered:
            raise Gate14ChantEventRoutingError(
                "routing boundary cannot weaken recovered callback/dispatch facts"
            )
        if (
            self.named_event_semantics_recovered
            or self.matchcalculator_record_equivalence_recovered
            or self.fastview_sender_equivalence_recovered
        ):
            raise Gate14ChantEventRoutingError(
                "numeric routing cannot promote unrecovered event identity"
            )


SOURCE_BOUNDARY = NumericChantEventRoutingBoundary()
