"""Fail-closed source contract for four outer FastView embedded controls.

The exhaustive outer FastViewPanel registration trace proves two embedded
controls immediately before GoalFlash and two more immediately after the
FastViewTeam wrapper. Their parent offsets, append/setup callsites, constructor
paths, and outer draw ranks are already canonical.

This module records only that topology. It deliberately does not assign user-
visible roles, rectangles, resource identities, state semantics, or pixels.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_outer_draw_order import (
    EMBEDDED_BUTTON0_CONSTRUCTOR_CALL_VA,
    EMBEDDED_BUTTON0_PARENT_OFFSET,
    EMBEDDED_BUTTON0_REGISTER_CALL_VA,
    EMBEDDED_BUTTON1_CONSTRUCTOR_CALL_VA,
    EMBEDDED_BUTTON1_PARENT_OFFSET,
    EMBEDDED_BUTTON1_REGISTER_CALL_VA,
    EMBEDDED_BUTTON_CONSTRUCTOR_VA,
    POST_TEAM_CONTROL_ARRAY_PARENT_OFFSET,
    POST_TEAM_CONTROL_CONSTRUCTOR_VA,
    POST_TEAM_CONTROL_COUNT,
    POST_TEAM_CONTROL_STRIDE,
    POST_TEAM_REGISTER_LOOP_CALL_VA,
    outer_draw_rank,
)


class FastViewEmbeddedControlsSourceError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewEmbeddedOuterControl:
    identity: str
    family: str
    parent_offset: int
    registration_call_va: int
    setup_call_va: int | None
    constructor_target_va: int
    outer_draw_rank: int

    def __post_init__(self) -> None:
        if not isinstance(self.identity, str) or not self.identity:
            raise FastViewEmbeddedControlsSourceError("identity must be non-empty")
        if self.family not in {"pre_goalflash", "post_team"}:
            raise FastViewEmbeddedControlsSourceError("unknown embedded-control family")
        for label, value in (
            ("parent offset", self.parent_offset),
            ("registration call VA", self.registration_call_va),
            ("constructor target VA", self.constructor_target_va),
            ("outer draw rank", self.outer_draw_rank),
        ):
            if type(value) is not int or value < 0:
                raise FastViewEmbeddedControlsSourceError(
                    f"{label} must be a non-negative integer"
                )
        if self.setup_call_va is not None and (
            type(self.setup_call_va) is not int or self.setup_call_va <= 0
        ):
            raise FastViewEmbeddedControlsSourceError(
                "setup call VA must be positive integer or None"
            )


PRE_GOALFLASH_EMBEDDED_CONTROLS = (
    FastViewEmbeddedOuterControl(
        identity="embedded_button_0",
        family="pre_goalflash",
        parent_offset=EMBEDDED_BUTTON0_PARENT_OFFSET,
        registration_call_va=EMBEDDED_BUTTON0_REGISTER_CALL_VA,
        setup_call_va=EMBEDDED_BUTTON0_CONSTRUCTOR_CALL_VA,
        constructor_target_va=EMBEDDED_BUTTON_CONSTRUCTOR_VA,
        outer_draw_rank=outer_draw_rank("embedded_button_0"),
    ),
    FastViewEmbeddedOuterControl(
        identity="embedded_button_1",
        family="pre_goalflash",
        parent_offset=EMBEDDED_BUTTON1_PARENT_OFFSET,
        registration_call_va=EMBEDDED_BUTTON1_REGISTER_CALL_VA,
        setup_call_va=EMBEDDED_BUTTON1_CONSTRUCTOR_CALL_VA,
        constructor_target_va=EMBEDDED_BUTTON_CONSTRUCTOR_VA,
        outer_draw_rank=outer_draw_rank("embedded_button_1"),
    ),
)

POST_TEAM_EMBEDDED_CONTROLS = tuple(
    FastViewEmbeddedOuterControl(
        identity=f"post_team_control_{index}",
        family="post_team",
        parent_offset=POST_TEAM_CONTROL_ARRAY_PARENT_OFFSET
        + index * POST_TEAM_CONTROL_STRIDE,
        registration_call_va=POST_TEAM_REGISTER_LOOP_CALL_VA,
        setup_call_va=None,
        constructor_target_va=POST_TEAM_CONTROL_CONSTRUCTOR_VA,
        outer_draw_rank=outer_draw_rank(f"post_team_control_{index}"),
    )
    for index in range(POST_TEAM_CONTROL_COUNT)
)

FASTVIEW_EMBEDDED_OUTER_CONTROLS = (
    PRE_GOALFLASH_EMBEDDED_CONTROLS + POST_TEAM_EMBEDDED_CONTROLS
)
FASTVIEW_EMBEDDED_OUTER_CONTROL_COUNT = 4


def embedded_outer_control(identity: str) -> FastViewEmbeddedOuterControl:
    if not isinstance(identity, str) or not identity:
        raise FastViewEmbeddedControlsSourceError("identity must be non-empty string")
    for control in FASTVIEW_EMBEDDED_OUTER_CONTROLS:
        if control.identity == identity:
            return control
    raise FastViewEmbeddedControlsSourceError("unknown embedded FastView control")


def embedded_outer_controls_source_contract() -> dict:
    return {
        "control_count": FASTVIEW_EMBEDDED_OUTER_CONTROL_COUNT,
        "controls": tuple(
            (
                control.identity,
                control.family,
                control.parent_offset,
                control.registration_call_va,
                control.setup_call_va,
                control.constructor_target_va,
                control.outer_draw_rank,
            )
            for control in FASTVIEW_EMBEDDED_OUTER_CONTROLS
        ),
        "role_semantics_recovered": False,
        "control_geometry_recovered": False,
        "resource_identity_recovered": False,
        "state_behavior_recovered": False,
        "pixels_rasterized": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
