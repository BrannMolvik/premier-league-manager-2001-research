"""Fail-closed source contract for the outer FastView ScoreCompositeMain family.

The complete outer FastViewPanel registration trace proves that exactly one of
three owner branches constructs ScoreCompositeMain. Both concrete constructors
flow through the shared ScoreComposite base builder, which appends one
PictureControl followed by four TextControls directly to the outer draw array.

This module records only that already-canonical topology. It deliberately does
not assign branch selector semantics, control rectangles, visible strings,
resource identity, final screen geometry, or pixels.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_outer_draw_order import (
    SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA,
    SCORE_COMPOSITE_MAIN_CONSTRUCTORS,
    SCORE_COMPOSITE_MAIN_OWNER_CALL_VAS,
    SCORE_COMPOSITE_MAIN_REGISTER_CALLS,
    outer_draw_rank,
)


class FastViewScoreCompositeMainSourceError(ValueError):
    pass


SCORE_COMPOSITE_MAIN_INSTANCE_COUNT = 1
SCORE_COMPOSITE_MAIN_BRANCHES = (
    (0x520356, 0x51B400),
    (0x520416, 0x51B330),
    (0x5204D6, 0x51B330),
)
SCORE_COMPOSITE_MAIN_CONTROL_IDENTITIES = tuple(
    f"score_composite_main_control_{index}" for index in range(5)
)
SCORE_COMPOSITE_MAIN_CONTROL_KINDS = (
    "picture_control_constructor",
    "text_control_constructor",
    "text_control_constructor",
    "text_control_constructor",
    "text_control_constructor",
)


@dataclass(frozen=True)
class ScoreCompositeMainBranch:
    owner_call_va: int
    constructor_va: int

    def __post_init__(self) -> None:
        if type(self.owner_call_va) is not int or self.owner_call_va <= 0:
            raise FastViewScoreCompositeMainSourceError(
                "ScoreCompositeMain owner call VA must be positive integer"
            )
        if type(self.constructor_va) is not int or self.constructor_va <= 0:
            raise FastViewScoreCompositeMainSourceError(
                "ScoreCompositeMain constructor VA must be positive integer"
            )


SOURCE_BRANCHES = tuple(
    ScoreCompositeMainBranch(owner, constructor)
    for owner, constructor in SCORE_COMPOSITE_MAIN_BRANCHES
)


def scorecomposite_main_branch(owner_call_va: int) -> ScoreCompositeMainBranch:
    """Resolve only the three source-proven owner callsites.

    The caller still has to know which original branch is active. This helper
    does not infer the selector condition from game state.
    """
    if type(owner_call_va) is not int:
        raise FastViewScoreCompositeMainSourceError(
            "ScoreCompositeMain owner call VA must be integer"
        )
    for branch in SOURCE_BRANCHES:
        if branch.owner_call_va == owner_call_va:
            return branch
    raise FastViewScoreCompositeMainSourceError(
        "unknown ScoreCompositeMain owner branch"
    )


def scorecomposite_main_outer_ranks() -> tuple[int, ...]:
    return tuple(outer_draw_rank(identity) for identity in SCORE_COMPOSITE_MAIN_CONTROL_IDENTITIES)


def scorecomposite_main_source_contract() -> dict:
    """Return the exact persisted source boundary without promoting pixels."""
    registrations = tuple(SCORE_COMPOSITE_MAIN_REGISTER_CALLS)
    return {
        "instance_count": SCORE_COMPOSITE_MAIN_INSTANCE_COUNT,
        "owner_branches": tuple(
            (branch.owner_call_va, branch.constructor_va)
            for branch in SOURCE_BRANCHES
        ),
        "shared_base_constructor_va": SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA,
        "control_identities": SCORE_COMPOSITE_MAIN_CONTROL_IDENTITIES,
        "control_registrations": registrations,
        "control_kinds": SCORE_COMPOSITE_MAIN_CONTROL_KINDS,
        "outer_draw_ranks": scorecomposite_main_outer_ranks(),
        "branch_selector_semantics_recovered": False,
        "control_geometry_recovered": False,
        "runtime_content_semantics_recovered": False,
        "resource_identity_recovered": False,
        "absolute_position_recovered": False,
        "pixels_rasterized": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
