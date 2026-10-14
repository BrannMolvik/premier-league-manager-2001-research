"""Original FM2001 LeagueMatch 0x513010 post-preparation presentation reachability.

The original's match virtual+0x34 preparation, match+0x44 bit5 gate,
Side0 virtual+0, 0x5DA2F0 call and *subsequent* match+0x44 bit4 read
determine whether a match presentation route is reached. The mode byte
is NOT read for every processed match. Both source virtual+0x38/+0x3C
post-callbacks are still reached after a skipped presentation.

All source-dependent results are supplied by the caller from the reached
original native stages. This never calculates a score, runs an original
callback, provides fake object pointers, or returns to management.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_match_detail_route_source import (
    SourceMatchDetailDispatch,
    source_match_detail_dispatch,
)

SOURCE_ORIGINAL_NATIVE_PROCESS_VA = 0x513010
SOURCE_ORIGINAL_NATIVE_PREPARE_V34_CALL_VA = 0x5130C2
SOURCE_ORIGINAL_NATIVE_MATCH_FLAGS_AT_513238_VA = 0x513238
SOURCE_ORIGINAL_NATIVE_BIT5_SKIP_MASK = 0x20
SOURCE_ORIGINAL_NATIVE_SIDE0_GETTER_VA = 0x513248
SOURCE_ORIGINAL_NATIVE_SHARED_STAGE_VA = 0x5DA2F0
SOURCE_ORIGINAL_NATIVE_SHARED_CALLSITE_VA = 0x513252
SOURCE_ORIGINAL_NATIVE_POST_SHARED_HUMAN_FLAG_VA = 0x513257
SOURCE_ORIGINAL_NATIVE_HUMAN_PRESENTATION_MASK = 0x10
SOURCE_ORIGINAL_NATIVE_MODE_READ_VA = 0x51325D
SOURCE_ORIGINAL_NATIVE_POST_V38_CALL_VA = 0x51329D
SOURCE_ORIGINAL_NATIVE_POST_V3C_CALL_VA = 0x5132A9


class OriginalNativeMatchPresentationGateError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalNativeMatchPresentationGate:
    """Reached source stages ONLY; not proof that a match was playable."""

    original_v34_prepare_succeeded: bool
    original_flags44_at_pre_shared_gate: int | None
    original_flags44_after_shared_stage: int | None
    original_native_side0_club_pointer: int | None
    shared_stage_5da2f0_reached: bool
    view_51325d_reached: bool
    source_view_route: SourceMatchDetailDispatch | None
    post_virtual38_and_virtual3c_reached: bool = True


def source_original_native_match_view_gate_513238(
    *,
    original_v34_prepare_succeeded: bool,
    original_flags44_at_pre_shared_gate: int | None,
    original_native_side0_club_pointer_from_reached_v0: int | None,
    original_flags44_after_reached_5da2f0: int | None,
    original_mode_global_877530_if_view_reached: int | None,
) -> OriginalNativeMatchPresentationGate:
    """Strict source path from virtual+0x34 through 0x513294 callbacks.

    If +0x34 fails, original jumps to 0x513294 post callbacks.
    Otherwise 0x513238 reads flags+0x44 bit5. When bit5 is set, it
    jumps to post callbacks without calling Side0 v0 or 0x5DA2F0.
    Otherwise it calls the Side0 native getter then 0x5DA2F0. It
    re-reads the match+0x44 *after* that call; only bit4 permits
    loading global mode 0x877530 and routing presentation 0/1/2/3.
    The two virtual post callbacks run at 0x51329D and 0x5132A9 on
    all reached branches. They are NOT executed by this helper.
    """
    if type(original_v34_prepare_succeeded) is not bool:
        raise OriginalNativeMatchPresentationGateError(
            "actual native virtual+0x34 AL result required"
        )
    flags_before = original_flags44_at_pre_shared_gate
    ptr = original_native_side0_club_pointer_from_reached_v0
    flags_after = original_flags44_after_reached_5da2f0
    mode = original_mode_global_877530_if_view_reached
    if not original_v34_prepare_succeeded:
        if any(x is not None for x in (flags_before, ptr, flags_after, mode)):
            raise OriginalNativeMatchPresentationGateError(
                "virtual+0x34 false skips all presentation-stage source reads"
            )
        return OriginalNativeMatchPresentationGate(
            False, None, None, None, False, False, None
        )
    if type(flags_before) is not int or not 0 <= flags_before <= 0xFFFFFFFF:
        raise OriginalNativeMatchPresentationGateError(
            "actual native match+0x44 DWORD at 0x513238 required"
        )
    if flags_before & SOURCE_ORIGINAL_NATIVE_BIT5_SKIP_MASK:
        if any(x is not None for x in (ptr, flags_after, mode)):
            raise OriginalNativeMatchPresentationGateError(
                "match+0x44 bit5 skips source Side0 and shared stage"
            )
        return OriginalNativeMatchPresentationGate(
            True, flags_before, None, None, False, False, None
        )
    if type(ptr) is not int or not 0 < ptr <= 0xFFFFFFFF:
        raise OriginalNativeMatchPresentationGateError(
            "reached original Side0 virtual+0 nonnull pointer required"
        )
    if type(flags_after) is not int or not 0 <= flags_after <= 0xFFFFFFFF:
        raise OriginalNativeMatchPresentationGateError(
            "actual native match+0x44 DWORD AFTER 0x5DA2F0 required"
        )
    if not flags_after & SOURCE_ORIGINAL_NATIVE_HUMAN_PRESENTATION_MASK:
        if mode is not None:
            raise OriginalNativeMatchPresentationGateError(
                "original view mode global is skipped when poststage bit4 clear"
            )
        return OriginalNativeMatchPresentationGate(
            True, flags_before, flags_after, ptr, True, False, None
        )
    if type(mode) is not int or mode not in (0, 1, 2, 3):
        raise OriginalNativeMatchPresentationGateError(
            "source qualified original Match Detail global 0..3 required"
        )
    return OriginalNativeMatchPresentationGate(
        True, flags_before, flags_after, ptr, True, True,
        source_match_detail_dispatch(mode)
    )
