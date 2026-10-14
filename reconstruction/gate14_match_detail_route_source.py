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
    mode: MatchDetailMode | None
    before_callback_flags_esi44: int
    after_callback_flags_esi44_if_reached: int | None
    pre_presentation_native_call_va: int | None
    selected_presentation_wrapper_va: int | None
    selected_wrapper_variant: int | None
    native_post_virtual_offsets: tuple[int, int] = MATCH_POST_PRESENTATION_VIRTUAL_OFFSETS
    native_callbacks_executed: bool = False
    live_match_state_committed: bool = False


def source_original_match_mode_handoff_phase(
    mode: int | MatchDetailMode | None,
    *,
    original_flags_at_513238: int,
    original_flags_at_513257_if_reached: int | None,
) -> SourceMatchModeHandoffPhase:
    """Strict native 513238->5DA2F0->513257->mode->v38/v3c receipt.

    The OUTER router reads global 877530 at 51325D after both bit tests.\n    Earlier 510D60 virtual+34 may ALREADY copy global 877530 into context+D3C.
    A bypassed mode must therefore be passed as None, not guessed from
    earlier settings or supplied via a synthetic user selection.
    Original callbacks, modal and game state are never executed.
    """
    flags = original_flags_at_513238
    if type(flags) is not int or not 0 <= flags <= 0xFFFFFFFF:
        raise ValueError("exact original DWORD esi+44 at 513238 required")
    second = original_flags_at_513257_if_reached
    if flags & MATCH_SOURCE_SKIP_PRE_FLAG:
        if second is not None or mode is not None:
            raise ValueError("native 513257 and mode not reached after 513238 skip")
        return SourceMatchModeHandoffPhase(None, flags, None, None, None, None)
    if type(second) is not int or not 0 <= second <= 0xFFFFFFFF:
        raise ValueError("separately reached original DWORD esi+44 after 5DA2F0 required")
    if not (second & MATCH_SOURCE_PRESENTATION_FLAG):
        if mode is not None:
            raise ValueError("original mode at 51325D not reached after 513257 skip")
        return SourceMatchModeHandoffPhase(
            None, flags, second, MATCH_PRE_PRESENTATION_NATIVE_CALL_VA,
            None, None,
        )
    if mode is None:
        raise ValueError("original 877530 mode required at reached 51325D")
    selected = coerce_match_detail_mode(mode)
    dispatch = source_match_detail_dispatch(selected)
    return SourceMatchModeHandoffPhase(
        selected, flags, second, MATCH_PRE_PRESENTATION_NATIVE_CALL_VA,
        dispatch.presentation_wrapper_va, dispatch.wrapper_variant,
    )

@dataclass(frozen=True)
class SourceOriginalMatchRouterGuard:
    """Only original 5130C2 / 5130DC entry guards, not match execution."""

    original_v34_result_nonzero: bool
    original_516080_result_nonzero_if_reached: bool | None
    early_native_512d80_called: bool
    reaches_mode_handoff_at_513238: bool
    reaches_post_callbacks_at_513294: bool = True
    original_callbacks_executed: bool = False
    live_game_state_committed: bool = False


def source_original_match_router_guard(
    *, original_5130c2_v34_al_nonzero: bool,
    original_516080_al_nonzero_if_reached: bool | None,
) -> SourceOriginalMatchRouterGuard:
    """Source 5130C2..5130F4, after the native+34 callback has been reached.

    If vtable+34 returns AL=0, 5130CE calls 512D80 and 5130D6
    jumps straight to 513294; 513238 and presentation are skipped.
    If AL!=0, 516080 is called: nonzero calls 512D80 and jumps
    513235->513238; zero reaches the later mode-setup branch from
    5130F4, ultimately 513238 after its nested native callbacks.
    In EVERY case the 513294 post virtual+38/+3C callbacks remain.
    Earlier gate/context/side effects and whether either native
    callback ACTUALLY executed are intentionally not inferred.
    """
    first = original_5130c2_v34_al_nonzero
    second = original_516080_al_nonzero_if_reached
    if type(first) is not bool:
        raise ValueError("actual reached 5130C2 vtable+34 AL zero/nonzero result required")
    if not first:
        if second is not None:
            raise ValueError("516080 not reached after vtable+34 AL zero")
        return SourceOriginalMatchRouterGuard(False, None, True, False)
    if type(second) is not bool:
        raise ValueError("actual reached 516080 AL zero/nonzero result required")
    return SourceOriginalMatchRouterGuard(True, second, bool(second), True)


@dataclass(frozen=True)
class SourceOriginalGuardedMatchRoute:
    """A guarded source order, not an executed/committed native match."""

    original_entry_guard: SourceOriginalMatchRouterGuard
    original_mode_phase_if_reached: SourceMatchModeHandoffPhase | None
    original_post_v38_and_v3c_still_required: bool = True
    original_game_result_published: bool = False


def source_original_guarded_match_route(
    *, original_5130c2_v34_al_nonzero: bool,
    original_516080_al_nonzero_if_reached: bool | None,
    original_mode_if_51325d_reached: int | MatchDetailMode | None,
    original_flags_at_513238_if_reached: int | None,
    original_flags_at_513257_if_reached: int | None,
) -> SourceOriginalGuardedMatchRoute:
    """Compose original entry guard with handoff ONLY on reached 513238.

    A v34 AL=0 follows 512D80 directly to 513294 without reading native
    mode, pre-calling 5DA2F0 or reading either phase flag. Caller must
    not inject an unobserved mode or a stale processor+44 snapshot.
    Post v38/v3c remain source-required for BOTH entry paths, not run.
    """
    guard = source_original_match_router_guard(
        original_5130c2_v34_al_nonzero=original_5130c2_v34_al_nonzero,
        original_516080_al_nonzero_if_reached=original_516080_al_nonzero_if_reached,
    )
    if not guard.reaches_mode_handoff_at_513238:
        if (original_mode_if_51325d_reached is not None
                or original_flags_at_513238_if_reached is not None
                or original_flags_at_513257_if_reached is not None):
            raise ValueError("original 513238 mode/flags not reached after early v34 bypass")
        return SourceOriginalGuardedMatchRoute(guard, None)
    mode_phase = source_original_match_mode_handoff_phase(
        original_mode_if_51325d_reached,
        original_flags_at_513238=original_flags_at_513238_if_reached,
        original_flags_at_513257_if_reached=original_flags_at_513257_if_reached,
    )
    return SourceOriginalGuardedMatchRoute(guard, mode_phase)


@dataclass(frozen=True)
class SourceOriginalV34ModeContextStore:
    """Only 510D95/510D9B source store, never full v34 execution."""

    original_match_vtable: int
    original_virtual34_owner_va: int
    original_877530_raw_mode_value: int
    original_context_after_single_mode_store: bytes
    original_full_native_v34_executed: bool = False
    live_game_state_updated: bool = False


def source_original_v34_mode_context_store_from_reached(
    *, original_native_match_record: bytes,
    original_processing_context_at_510d95: bytes,
    original_global_877530_raw_value: int,
) -> SourceOriginalV34ModeContextStore:
    """Source v34 510D60 copies global 877530 to context+D3C.

    All seven authenticated original match classes use 510D60 directly
    or through 511120, which calls 510D60 FIRST. This reached-source
    projection requires the actual context AT 510D95, after earlier
    getter/632550 calls, not a synthetic fresh/initialized context.
    It permits original unresolved sentinel 5 and all DWORD values:
    the native COPY performs no mode selection or numeric validation.
    Other 510D60 context stores, native AL outcome and live world
    mutations remain wholly unexecuted.
    """
    from struct import pack_into
    from original_leaguematch_native_process_owners import (
        source_original_leaguematch_process_owners_for_native_record,
    )
    owner = source_original_leaguematch_process_owners_for_native_record(
        original_match_record=original_native_match_record)
    if owner.virtual34_prepare_va not in (0x510D60, 0x511120):
        raise ValueError("original v34 wrapper/base mode cache not qualified")
    context = original_processing_context_at_510d95
    if type(context) is not bytes or len(context) < 0xD40:
        raise ValueError("actual original processing context at 510D95 through D3F required")
    raw_mode = original_global_877530_raw_value
    if type(raw_mode) is not int or not 0 <= raw_mode <= 0xFFFFFFFF:
        raise ValueError("original global 877530 raw DWORD required")
    after = bytearray(context)
    pack_into("<I", after, 0xD3C, raw_mode)
    return SourceOriginalV34ModeContextStore(
        owner.source_vtable_va, owner.virtual34_prepare_va, raw_mode,
        bytes(after),
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
