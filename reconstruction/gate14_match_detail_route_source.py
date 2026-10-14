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
MODE_PREPARATION_BRANCH_VA = 0x51312F
MODE_THREED_PRECLEAR_VA = 0x632B50
MODE_SHARED_PREPARATION_VA = 0x632B20


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


@dataclass(frozen=True)
class SourceMatchModePreparation:
    mode: MatchDetailMode
    clears_context_byte_1145: bool
    shared_preparation_va: int = MODE_SHARED_PREPARATION_VA


def source_requires_prematch_modal(
    settings_owner_present: bool | None,
    mode: int | MatchDetailMode | None,
) -> bool:
    """Mirror 0x513010's exact owner-null OR sentinel-5 predicate."""
    if settings_owner_present is not None and type(settings_owner_present) is not bool:
        raise ValueError("Match Detail settings-owner state must be bool or None")
    if mode is None:
        return True
    coerce_match_detail_mode(mode)
    if settings_owner_present is None:
        raise RuntimeError("Match Detail settings-owner availability is unknown")
    return not settings_owner_present


def source_match_mode_preparation(
    mode: int | MatchDetailMode,
) -> SourceMatchModePreparation:
    """Return the proven pre-calculator branch without naming unknown effects."""
    selected = coerce_match_detail_mode(mode)
    return SourceMatchModePreparation(
        mode=selected,
        clears_context_byte_1145=selected in (
            MatchDetailMode.THREE_D_MATCH,
            MatchDetailMode.THREE_D_HIGHLIGHTS,
        ),
    )


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



# Original 513238..5132AC is a separate conditional match processing phase.
# Do not mistake the 5DA2F0 pre-wrapper call for the complete calculator:
# its original effects, mode-specific modal, and post callbacks are separate.
MATCH_SOURCE_PHASE_ENTRY_VA = 0x513238
MATCH_PRE_PRESENTATION_NATIVE_CALL_VA = 0x5DA2F0
MATCH_POST_PRESENTATION_VIRTUAL_OFFSETS = (0x38, 0x3C)
MATCH_SOURCE_SKIP_PRE_FLAG = 0x20
MATCH_SOURCE_PRESENTATION_FLAG = 0x10


@dataclass(frozen=True)
class SourceMatchModeHandoffPhase:
    """Read-only branch plan after REACHING native 0x513238.

    The source reads object+44 twice: once BEFORE 5DA2F0 and once AFTER.
    Those snapshots must not be treated as identical without evidence.
    No native routine is invoked and no modern match state is committed.
    """
    mode: MatchDetailMode
    before_callback_flags_esi44: int
    after_callback_flags_esi44_if_reached: int | None
    pre_presentation_native_call_va: int | None
    selected_presentation_wrapper_va: int | None
    selected_wrapper_variant: int | None
    native_post_virtual_offsets: tuple[int, int] = MATCH_POST_PRESENTATION_VIRTUAL_OFFSETS
    native_callbacks_executed: bool = False
    live_match_state_committed: bool = False


def source_original_match_mode_handoff_phase(
    mode: int | MatchDetailMode,
    *,
    original_flags_at_513238: int,
    original_flags_at_513257_if_reached: int | None,
) -> SourceMatchModeHandoffPhase:
    """Exact guarded 513238→5DA2F0→513257→mode wrapper→vft+38/+3C.

    This is NOT the earlier 5130xx entry/virtual+28 gate. A reached
    0x513238 context is a precondition, not established by these inputs.
    If flags bit 0x20 is set at 513238, source jumps directly to 513294
    without visiting 5DA2F0 OR 513257. Otherwise 5DA2F0 is called,
    and a separately reached later flags BYTE+44 bit0x10 decides whether
    0/1/2 modal dispatch occurs (mode 3 has no presentation wrapper).
    Both post virtual offsets run at 513294/5132A0 after that choice.
    """
    selected = coerce_match_detail_mode(mode)
    flags = original_flags_at_513238
    if type(flags) is not int or not 0 <= flags <= 0xFFFFFFFF:
        raise ValueError("exact original DWORD esi+44 at 513238 required")
    reached_pre = not bool(flags & MATCH_SOURCE_SKIP_PRE_FLAG)
    second = original_flags_at_513257_if_reached
    if not reached_pre:
        if second is not None:
            raise ValueError("native 513257 flag read skipped after early 513294 branch")
        return SourceMatchModeHandoffPhase(
            selected, flags, None, None, None, None
        )
    if type(second) is not int or not 0 <= second <= 0xFFFFFFFF:
        raise ValueError("separately reached original DWORD esi+44 after 5DA2F0 required")
    dispatch = source_match_detail_dispatch(selected)
    wrapper = dispatch.presentation_wrapper_va if second & MATCH_SOURCE_PRESENTATION_FLAG else None
    variant = dispatch.wrapper_variant if wrapper is not None else None
    return SourceMatchModeHandoffPhase(
        selected, flags, second, MATCH_PRE_PRESENTATION_NATIVE_CALL_VA,
        wrapper, variant,
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
        "mode_preparation_branch_va": MODE_PREPARATION_BRANCH_VA,
        "mode_three_d_preclear_va": MODE_THREED_PRECLEAR_VA,
        "mode_shared_preparation_va": MODE_SHARED_PREPARATION_VA,
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
