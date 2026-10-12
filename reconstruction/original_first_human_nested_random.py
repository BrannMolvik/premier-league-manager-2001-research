"""Source-bounded first-user nested constructor RNG *call accounting*.

Original authorized executable SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3

First human source 0x425B2C -> constructor 0x60CE70 when outer
0x3C-byte allocation succeeds. That constructor conditionally
allocates three 0x90-byte child records. Each successful child
allocation invokes 0x60CD90 once (0x60CF2A, 0x60CFC6, 0x60D062).
0x60CD90 calls bounded RNG 0x64D540 at 0x60CE38 with bound 0x14;
0x64D540 calls original shared CRT rand 0x66951C exactly once.

Allocation outcomes are caller-supplied hypothetical branch facts,
NOT proven runtime snapshots. This is not an executable game RNG,
random seed synchronizer, queue observer or GameState mutation.
"""
from __future__ import annotations

from dataclasses import dataclass

CHILD_CONSTRUCTOR_SITES = (0x60CF2A, 0x60CFC6, 0x60D062)
NESTED_BOUNDED_RNG_SITE = 0x60CE38
NESTED_BOUNDED_RNG_BOUND = 0x14
ORIGINAL_RAW_RAND_SITE = 0x66951C


class OriginalNestedRandomSourceError(ValueError):
    """Allocation path lacks the narrow, original source prerequisites."""


@dataclass(frozen=True)
class OriginalNestedRandomBranchProjection:
    """Native callsite evidence, not measured original game execution."""
    outer_allocation_succeeded: bool
    child_allocations_succeeded: tuple[bool, bool, bool]
    reached_child_constructor_sites: tuple[int, ...]
    bounded_rng_calls: int
    raw_shared_crt_rand_calls: int
    live_crt_checkpoint_verified: bool = False


def project_original_first_human_nested_random(
    *,
    outer_allocation_succeeded: bool,
    child_allocations_succeeded: tuple[bool, bool, bool],
) -> OriginalNestedRandomBranchProjection:
    """Count DIRECT source RNG calls inside 0x60CE70's three children.

    The initial outer 0x668140 allocation at 0x425B12 must succeed to
    reach 0x425B2C. Each child 0x668140 allocation must likewise
    succeed for its corresponding 0x60CD90, whose unconditional one
    bounded draw consumes exactly one 0x66951C CRT draw. This
    projection excludes name generation, other original user fields,
    startup seed, event queues and conditional later virtual callbacks.
    """
    if type(outer_allocation_succeeded) is not bool:
        raise OriginalNestedRandomSourceError("Outer source allocation must be Boolean")
    if (type(child_allocations_succeeded) is not tuple
            or len(child_allocations_succeeded) != 3
            or any(type(value) is not bool for value in child_allocations_succeeded)):
        raise OriginalNestedRandomSourceError("Three exact child allocation outcomes required")
    if not outer_allocation_succeeded and any(child_allocations_succeeded):
        raise OriginalNestedRandomSourceError("Cannot run child initializer without source outer allocation")
    selected = tuple(
        site for site, succeeded in zip(CHILD_CONSTRUCTOR_SITES, child_allocations_succeeded)
        if outer_allocation_succeeded and succeeded
    )
    return OriginalNestedRandomBranchProjection(
        outer_allocation_succeeded,
        child_allocations_succeeded,
        selected,
        len(selected),
        len(selected),
    )
