"""Source-closed FM2001 PPreMatch modal -> presentation dispatch.

This module records the canonical executable's exact Match Detail handoff
without inventing a management-screen trigger.

PPreMatch commit 0x49ABA0 writes the accepted mode to global 0x877530, hides
all four selector controls, signals modal owner 0x877960 via 0x5328B0, then
closes the panel through 0x6539F0.

The normal match-processing routine at 0x513010 resolves sentinel mode 5 by
calling the PPreMatch modal wrapper 0x533120. That wrapper constructs the panel
through 0x499C30, runs the modal through 0x532650, then copies the selected
global value into the active match-processing object at +0xD3C.

The same 0x513010 path later dispatches presentation exactly:
- mode 0 -> 0x533D80 with variant 0;
- mode 1 -> 0x533D80 with variant 1;
- mode 2 -> 0x5331C0 (FastView);
- mode 3 -> no presentation-wrapper call (Quick Match).

This source contract does not identify the ordinary management-screen control
that enters 0x513010, so the normal host navigation trigger remains fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from match_detail_mode import MatchDetailMode, coerce_match_detail_mode


PREMATCH_SELECTOR_COMMIT_VA = 0x49ABA0
PREMATCH_MODE_GLOBAL_VA = 0x877530
PREMATCH_MODAL_OWNER_VA = 0x877960
PREMATCH_MODAL_SIGNAL_VA = 0x5328B0
PREMATCH_PANEL_CLOSE_VA = 0x6539F0

PREMATCH_MODAL_WRAPPER_VA = 0x533120
PREMATCH_PANEL_CONSTRUCT_VA = 0x499C30
PREMATCH_MODAL_RUN_VA = 0x532650
PREMATCH_PANEL_DESTROY_VA = 0x49A100
PREMATCH_SELECTED_MODE_OBJECT_OFFSET = 0xD3C

MATCH_PROCESSING_ROUTER_VA = 0x513010
MATCH_DETAIL_SETTINGS_READY_GLOBAL_VA = 0x875680
MATCH_DETAIL_SENTINEL = 5
FASTVIEW_PRESENTATION_WRAPPER_VA = 0x5331C0
THREED_PRESENTATION_WRAPPER_VA = 0x533D80

# Source branches in 0x51325D..0x513294.
MODE_DISPATCH_BRANCH_VA = 0x51325D
FASTVIEW_CALLSITE_VA = 0x513272
THREED_CALLSITE_VA = 0x51328C


class MatchPresentationRoute(Enum):
    THREE_D_MATCH = "three_d_match"
    THREE_D_HIGHLIGHTS = "three_d_highlights"
    FASTVIEW = "fastview"
    QUICK_MATCH = "quick_match"


@dataclass(frozen=True)
class SourceMatchDetailDispatch:
    mode: MatchDetailMode
    route: MatchPresentationRoute
    presentation_wrapper_va: int | None
    wrapper_variant: int | None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, MatchDetailMode):
            raise ValueError("dispatch mode must be MatchDetailMode")
        if not isinstance(self.route, MatchPresentationRoute):
            raise ValueError("dispatch route must be MatchPresentationRoute")
        if self.mode is MatchDetailMode.THREE_D_MATCH:
            expected = (MatchPresentationRoute.THREE_D_MATCH, THREED_PRESENTATION_WRAPPER_VA, 0)
        elif self.mode is MatchDetailMode.THREE_D_HIGHLIGHTS:
            expected = (
                MatchPresentationRoute.THREE_D_HIGHLIGHTS,
                THREED_PRESENTATION_WRAPPER_VA,
                1,
            )
        elif self.mode is MatchDetailMode.FASTVIEW:
            expected = (MatchPresentationRoute.FASTVIEW, FASTVIEW_PRESENTATION_WRAPPER_VA, None)
        else:
            expected = (MatchPresentationRoute.QUICK_MATCH, None, None)
        if (
            self.route,
            self.presentation_wrapper_va,
            self.wrapper_variant,
        ) != expected:
            raise ValueError("dispatch does not match source mode branch")


def source_match_detail_dispatch(
    mode: int | MatchDetailMode,
) -> SourceMatchDetailDispatch:
    """Return the exact source presentation route for one accepted mode."""
    selected = coerce_match_detail_mode(mode)
    if selected is MatchDetailMode.THREE_D_MATCH:
        return SourceMatchDetailDispatch(
            mode=selected,
            route=MatchPresentationRoute.THREE_D_MATCH,
            presentation_wrapper_va=THREED_PRESENTATION_WRAPPER_VA,
            wrapper_variant=0,
        )
    if selected is MatchDetailMode.THREE_D_HIGHLIGHTS:
        return SourceMatchDetailDispatch(
            mode=selected,
            route=MatchPresentationRoute.THREE_D_HIGHLIGHTS,
            presentation_wrapper_va=THREED_PRESENTATION_WRAPPER_VA,
            wrapper_variant=1,
        )
    if selected is MatchDetailMode.FASTVIEW:
        return SourceMatchDetailDispatch(
            mode=selected,
            route=MatchPresentationRoute.FASTVIEW,
            presentation_wrapper_va=FASTVIEW_PRESENTATION_WRAPPER_VA,
            wrapper_variant=None,
        )
    return SourceMatchDetailDispatch(
        mode=selected,
        route=MatchPresentationRoute.QUICK_MATCH,
        presentation_wrapper_va=None,
        wrapper_variant=None,
    )


def match_detail_route_source_contract() -> dict:
    return {
        "selector_commit_va": PREMATCH_SELECTOR_COMMIT_VA,
        "mode_global_va": PREMATCH_MODE_GLOBAL_VA,
        "modal_owner_va": PREMATCH_MODAL_OWNER_VA,
        "modal_signal_va": PREMATCH_MODAL_SIGNAL_VA,
        "panel_close_va": PREMATCH_PANEL_CLOSE_VA,
        "modal_wrapper_va": PREMATCH_MODAL_WRAPPER_VA,
        "panel_construct_va": PREMATCH_PANEL_CONSTRUCT_VA,
        "modal_run_va": PREMATCH_MODAL_RUN_VA,
        "panel_destroy_va": PREMATCH_PANEL_DESTROY_VA,
        "selected_mode_object_offset": PREMATCH_SELECTED_MODE_OBJECT_OFFSET,
        "match_processing_router_va": MATCH_PROCESSING_ROUTER_VA,
        "sentinel": MATCH_DETAIL_SENTINEL,
        "fastview_wrapper_va": FASTVIEW_PRESENTATION_WRAPPER_VA,
        "three_d_wrapper_va": THREED_PRESENTATION_WRAPPER_VA,
        "mode_routes": tuple(
            (
                int(mode),
                source_match_detail_dispatch(mode).route.value,
                source_match_detail_dispatch(mode).presentation_wrapper_va,
                source_match_detail_dispatch(mode).wrapper_variant,
            )
            for mode in MatchDetailMode
        ),
        "prematch_modal_to_presentation_dispatch_recovered": True,
        "management_ui_entry_trigger_recovered": False,
        "three_d_choreography_recovered": False,
        "complete_match_presentation_recovered": False,
        "gate14_complete": False,
    }
