"""Source-closed runtime pool selection for FM2001 chants.

The enqueue callback uses a three-entry selector table:
0 -> home specialized pool, 1 -> away specialized pool, 2 -> generic pool.
Specialized selection walks candidates in list order, applying the source
availability predicate and a one-in-pool-count RNG remainder test. If no
specialized candidate is accepted, the source falls back to the generic pool.

The generic pool itself cycles backward through its already-shuffled list using
a persistent cursor that reloads the current list count whenever it reaches 0.

This module models only those mechanics with caller-supplied reduced RNG
remainders. It does not claim chant meaning, event binding, or RNG generator
state.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14ChantPoolSelectionError(ValueError):
    pass


ENQUEUE_VA = 0x723360
SELECT_POOL_VA = 0x723440
GENERIC_PICK_VA = 0x723470
SPECIALIZED_PICK_VA = 0x7234D0
SPECIALIZED_PREDICATE_VA = 0x723510
SELECTOR_TABLE_VA = 0x7DE270

HOME_SELECTOR = 0
AWAY_SELECTOR = 1
GENERIC_SELECTOR = 2

HOME_POOL_INDEX = 2
AWAY_POOL_INDEX = 3
GENERIC_POOL_INDEX = 1

HOME_POOL_GLOBAL_VA = 0xA87984
AWAY_POOL_GLOBAL_VA = 0xA879A0
GENERIC_POOL_GLOBAL_VA = 0xA87968
GENERIC_CURSOR_GLOBAL_VA = 0xA878DC

RECORD_USE_FIELD_OFFSET = 0x04
RECORD_GATE_DEADLINE_OFFSET = 0x0C


@dataclass(frozen=True)
class RuntimeChantCandidate:
    token: str
    use_field: int
    gate_deadline_ms: int

    def __post_init__(self) -> None:
        if not isinstance(self.token, str) or not self.token:
            raise Gate14ChantPoolSelectionError("candidate token must be non-empty")
        if type(self.use_field) is not int:
            raise Gate14ChantPoolSelectionError("candidate use field must be integer")
        if type(self.gate_deadline_ms) is not int or self.gate_deadline_ms < 0:
            raise Gate14ChantPoolSelectionError(
                "candidate gate deadline must be non-negative"
            )


def selector_pool(selector: int) -> str:
    """Return the source-specialized pool identity for selector 0/1/2."""
    if type(selector) is not int:
        raise Gate14ChantPoolSelectionError("selector must be integer")
    if selector == HOME_SELECTOR:
        return "home"
    if selector == AWAY_SELECTOR:
        return "away"
    if selector == GENERIC_SELECTOR:
        return "generic"
    raise Gate14ChantPoolSelectionError("chant selector must be 0, 1, or 2")


def specialized_candidate_is_eligible(
    candidate: RuntimeChantCandidate,
    *,
    now_ms: int,
) -> bool:
    """Exact non-RNG gate at 0x723510."""
    if type(candidate) is not RuntimeChantCandidate:
        raise Gate14ChantPoolSelectionError(
            "candidate must be exact RuntimeChantCandidate"
        )
    if type(now_ms) is not int or now_ms < 0:
        raise Gate14ChantPoolSelectionError("now_ms must be non-negative integer")
    return now_ms >= candidate.gate_deadline_ms or candidate.use_field < 2


def select_specialized_candidate(
    candidates: tuple[RuntimeChantCandidate, ...],
    *,
    now_ms: int,
    rng_remainders: tuple[int, ...],
) -> RuntimeChantCandidate | None:
    """Reproduce the list-order predicate search used by 0x7234D0.

    Source helper 0x6B2550 walks the list in order. The predicate consumes an
    RNG value only for candidates that pass the non-RNG eligibility gate, then
    accepts when RNG % total_pool_count == 0.

    rng_remainders therefore supplies only the already-reduced remainders for
    eligible candidates actually tested, in source traversal order.
    """
    if type(candidates) is not tuple or any(
        type(item) is not RuntimeChantCandidate for item in candidates
    ):
        raise Gate14ChantPoolSelectionError(
            "candidates must be exact RuntimeChantCandidate tuple"
        )
    if type(rng_remainders) is not tuple or any(
        type(value) is not int for value in rng_remainders
    ):
        raise Gate14ChantPoolSelectionError("rng_remainders must be integer tuple")
    if type(now_ms) is not int or now_ms < 0:
        raise Gate14ChantPoolSelectionError("now_ms must be non-negative integer")

    pool_count = len(candidates)
    if pool_count == 0:
        if rng_remainders:
            raise Gate14ChantPoolSelectionError(
                "empty specialized pool consumes no RNG remainders"
            )
        return None

    remainder_index = 0
    for candidate in candidates:
        if not specialized_candidate_is_eligible(candidate, now_ms=now_ms):
            continue
        if remainder_index >= len(rng_remainders):
            raise Gate14ChantPoolSelectionError(
                "missing RNG remainder for eligible specialized candidate"
            )
        remainder = rng_remainders[remainder_index]
        remainder_index += 1
        if not 0 <= remainder < pool_count:
            raise Gate14ChantPoolSelectionError(
                "specialized RNG remainder must be within pool count"
            )
        if remainder == 0:
            if remainder_index != len(rng_remainders):
                raise Gate14ChantPoolSelectionError(
                    "source stops consuming RNG after first accepted candidate"
                )
            return candidate

    if remainder_index != len(rng_remainders):
        raise Gate14ChantPoolSelectionError(
            "unused specialized RNG remainders do not match source traversal"
        )
    return None


def select_generic_candidate(
    candidates: tuple[RuntimeChantCandidate, ...],
    *,
    cursor: int,
) -> tuple[RuntimeChantCandidate | None, int]:
    """Reproduce 0x723470's persistent reverse cursor over generic records."""
    if type(candidates) is not tuple or any(
        type(item) is not RuntimeChantCandidate for item in candidates
    ):
        raise Gate14ChantPoolSelectionError(
            "candidates must be exact RuntimeChantCandidate tuple"
        )
    if type(cursor) is not int or cursor < 0:
        raise Gate14ChantPoolSelectionError("generic cursor must be non-negative")
    count = len(candidates)
    if count == 0:
        if cursor != 0:
            raise Gate14ChantPoolSelectionError(
                "empty generic pool requires zero cursor"
            )
        return None, 0
    if cursor > count:
        raise Gate14ChantPoolSelectionError(
            "generic cursor cannot exceed current pool count"
        )

    effective = count if cursor == 0 else cursor
    next_cursor = effective - 1
    return candidates[next_cursor], next_cursor


@dataclass(frozen=True)
class ChantPoolSelectionBoundary:
    specialized_fallback_to_generic_recovered: bool = True
    specialized_list_order_recovered: bool = True
    generic_reverse_cursor_recovered: bool = True
    rng_generator_state_recovered: bool = False
    event_binding_recovered: bool = False
    chant_meaning_recovered: bool = False

    def __post_init__(self) -> None:
        if not (
            self.specialized_fallback_to_generic_recovered
            and self.specialized_list_order_recovered
            and self.generic_reverse_cursor_recovered
        ):
            raise Gate14ChantPoolSelectionError(
                "selection boundary cannot weaken recovered pool mechanics"
            )
        if (
            self.rng_generator_state_recovered
            or self.event_binding_recovered
            or self.chant_meaning_recovered
        ):
            raise Gate14ChantPoolSelectionError(
                "pool selection cannot promote unrecovered semantics"
            )


SOURCE_BOUNDARY = ChantPoolSelectionBoundary()
