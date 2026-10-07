"""Complete supplied child-state model for the source-closed PPreMatch panel.

This joins already verified PPreMatch resource/layout state to explicit runtime
inputs. It proves that every native child family can be assigned its original
state for one supplied match. It deliberately does not flatten/rasterize the
entire 800x600 frame and therefore does not promote complete-frame or Gate-14
completion.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_prematch_marker_binding import BoundPrematchStartingXIMarkers
from gate14_prematch_text_binding import BoundPrematchDynamicText
from gate14_prematch_surface import (
    BoundPrematchPlayerRows,
    BoundPrematchRatingRows,
    BoundPrematchSelectorFrames,
    PrematchSurfaceBoundary,
)
from original_prematch_panel import PREMATCH_CHILD_COUNT, PREMATCH_CHILD_ORDER_RANGES


class PrematchSuppliedStateError(ValueError):
    pass


PREMATCH_SUPPLIED_STATE_FAMILIES = tuple(
    role for role, _start, _end in PREMATCH_CHILD_ORDER_RANGES
)


@dataclass(frozen=True)
class BoundPrematchSuppliedState:
    boundary: PrematchSurfaceBoundary
    dynamic_text: BoundPrematchDynamicText
    player_rows: BoundPrematchPlayerRows
    starting_xi_markers: BoundPrematchStartingXIMarkers
    rating_rows: BoundPrematchRatingRows
    selector_frames: BoundPrematchSelectorFrames
    supplied_state_complete_families: tuple[str, ...] = PREMATCH_SUPPLIED_STATE_FAMILIES
    source_child_count: int = PREMATCH_CHILD_COUNT
    all_native_child_state_bound: bool = True
    full_cross_layer_draw_order_recovered: bool = True
    text_pixels_rasterized: bool = False
    flattened_frame_available: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.boundary) is not PrematchSurfaceBoundary:
            raise PrematchSuppliedStateError(
                "supplied state requires exact PrematchSurfaceBoundary"
            )
        if type(self.dynamic_text) is not BoundPrematchDynamicText:
            raise PrematchSuppliedStateError(
                "supplied state requires exact dynamic text binding"
            )
        if type(self.player_rows) is not BoundPrematchPlayerRows:
            raise PrematchSuppliedStateError(
                "supplied state requires exact player-row binding"
            )
        if type(self.starting_xi_markers) is not BoundPrematchStartingXIMarkers:
            raise PrematchSuppliedStateError(
                "supplied state requires exact starting-XI marker binding"
            )
        if type(self.rating_rows) is not BoundPrematchRatingRows:
            raise PrematchSuppliedStateError(
                "supplied state requires exact rating binding"
            )
        if type(self.selector_frames) is not BoundPrematchSelectorFrames:
            raise PrematchSuppliedStateError(
                "supplied state requires exact selector-frame binding"
            )
        if self.dynamic_text.selection != self.boundary.selection:
            raise PrematchSuppliedStateError(
                "dynamic text selection differs from base pre-match boundary"
            )
        if tuple(row.source for row in self.player_rows.rows) != self.boundary.player_text_rows:
            raise PrematchSuppliedStateError(
                "player-row supplied state is detached from base boundary"
            )
        if tuple(row.source for row in self.rating_rows.rows) != self.boundary.rating_rows:
            raise PrematchSuppliedStateError(
                "rating supplied state is detached from base boundary"
            )
        if tuple(item.source for item in self.selector_frames.selectors) != self.boundary.selectors:
            raise PrematchSuppliedStateError(
                "selector supplied state is detached from base boundary"
            )
        if tuple(marker.child_index for marker in self.starting_xi_markers.markers) != tuple(
            range(10, 32)
        ):
            raise PrematchSuppliedStateError(
                "starting-XI marker supplied state lost native child ownership"
            )
        if self.supplied_state_complete_families != PREMATCH_SUPPLIED_STATE_FAMILIES:
            raise PrematchSuppliedStateError(
                "supplied-state family coverage no longer matches native child partition"
            )
        if self.source_child_count != PREMATCH_CHILD_COUNT:
            raise PrematchSuppliedStateError(
                "supplied-state child count no longer matches native panel"
            )
        if not (
            self.all_native_child_state_bound
            and self.full_cross_layer_draw_order_recovered
        ):
            raise PrematchSuppliedStateError(
                "supplied-state model cannot weaken source child/order proof"
            )
        if (
            self.text_pixels_rasterized
            or self.flattened_frame_available
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchSuppliedStateError(
                "child-state binding cannot promote unresolved pixel/frame/gate claims"
            )


def bind_prematch_supplied_state(
    *,
    boundary: PrematchSurfaceBoundary,
    dynamic_text: BoundPrematchDynamicText,
    player_rows: BoundPrematchPlayerRows,
    starting_xi_markers: BoundPrematchStartingXIMarkers,
    rating_rows: BoundPrematchRatingRows,
    selector_frames: BoundPrematchSelectorFrames,
) -> BoundPrematchSuppliedState:
    """Attach every supplied runtime family to one verified base surface."""
    return BoundPrematchSuppliedState(
        boundary=boundary,
        dynamic_text=dynamic_text,
        player_rows=player_rows,
        starting_xi_markers=starting_xi_markers,
        rating_rows=rating_rows,
        selector_frames=selector_frames,
    )


def prematch_supplied_state_contract() -> dict:
    return {
        "source_child_count": PREMATCH_CHILD_COUNT,
        "supplied_state_complete_families": PREMATCH_SUPPLIED_STATE_FAMILIES,
        "all_native_child_state_binding_available": True,
        "full_cross_layer_draw_order_recovered": True,
        "text_pixels_rasterized": False,
        "flattened_frame_available": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
