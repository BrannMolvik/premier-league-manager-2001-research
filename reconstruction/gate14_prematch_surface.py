"""Source-backed render boundary for the original FM2001 PPreMatchPanel.

This layer joins the already-recovered Match Detail/pre-match asset model to the
same Team_Backgrounds selector/loader used by FastView.  It exposes native
800x600 pixel layers and control resources without inventing the unresolved
management-to-match launch transition, rating meanings, dynamic rating values,
or a guessed full-frame z-order.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedResourceSelection,
    build_fastview_surfaced_resource_selection,
)
from gate14_fastview_surfaced_resource_loader import (
    VerifiedFastViewSurfacedResource,
    load_verified_selected_background,
)
from gate14_prematch_rating_widths import PrematchTeamRatingWidths
from original_front_end_layout import OriginalRect
from original_prematch_panel import (
    PREMATCH_ACTIVE_LEFT,
    PREMATCH_ACTIVE_RIGHT,
    PREMATCH_DISABLED_LEFT,
    PREMATCH_DISABLED_RIGHT,
    PREMATCH_LIVE_BACKGROUND_RECT,
    PREMATCH_RATING_LEFT,
    PREMATCH_RATING_RIGHT,
    PREMATCH_RATING_RIGHT2,
    PREMATCH_RATING_ROWS,
    PREMATCH_SELECTORS,
    PREMATCH_STATIC_PLACEMENTS,
    OriginalPrematchPanelResources,
    load_verified_original_prematch_resources,
)


class PrematchSurfaceError(ValueError):
    pass


@dataclass(frozen=True)
class PrematchRasterLayer:
    role: str
    rect: OriginalRect
    source_path: str
    rgba: bytes

    def __post_init__(self) -> None:
        if not self.role:
            raise PrematchSurfaceError("pre-match raster role must be non-empty")
        if not self.source_path:
            raise PrematchSurfaceError("pre-match raster source path must be non-empty")
        if len(self.rgba) != self.rect.width * self.rect.height * 4:
            raise PrematchSurfaceError("pre-match raster RGBA geometry mismatch")


@dataclass(frozen=True)
class PrematchSelectorSurface:
    mode: int
    event_id: int
    label: str
    rect: OriginalRect
    atlas: object


@dataclass(frozen=True)
class PrematchRatingSurface:
    native_record_discriminator: int
    native_width_function_va: int
    left_rect: OriginalRect
    right_rect: OriginalRect
    left_dynamic_rgba: bytes
    left_base_rgba: bytes
    right_base_rgba: bytes
    right_dynamic_mask_rgba: bytes

    def __post_init__(self) -> None:
        expected = self.left_rect.width * self.left_rect.height * 4
        if self.left_rect.width != 171 or self.left_rect.height != 16:
            raise PrematchSurfaceError("left rating geometry drifted")
        if self.right_rect.width != 171 or self.right_rect.height != 16:
            raise PrematchSurfaceError("right rating geometry drifted")
        for payload in (
            self.left_dynamic_rgba,
            self.left_base_rgba,
            self.right_base_rgba,
            self.right_dynamic_mask_rgba,
        ):
            if len(payload) != expected:
                raise PrematchSurfaceError("rating source geometry mismatch")


@dataclass(frozen=True)
class BoundPrematchRatingSurface:
    """One source row with exact state-bound left/right dynamic rectangles."""

    source: PrematchRatingSurface
    semantic_group: str
    left_width: int
    right_width: int
    left_dynamic_rect: OriginalRect
    right_dynamic_rect: OriginalRect

    def __post_init__(self) -> None:
        if not self.semantic_group:
            raise PrematchSurfaceError("bound rating group must be named")
        for width in (self.left_width, self.right_width):
            if not 0 <= int(width) <= 171:
                raise PrematchSurfaceError("bound rating width must be in 0..171")
        if (
            self.left_dynamic_rect.x,
            self.left_dynamic_rect.y,
            self.left_dynamic_rect.width,
            self.left_dynamic_rect.height,
        ) != (
            self.source.left_rect.x,
            self.source.left_rect.y,
            self.left_width,
            self.source.left_rect.height,
        ):
            raise PrematchSurfaceError("left dynamic rating rectangle is not native")
        if (
            self.right_dynamic_rect.x,
            self.right_dynamic_rect.y,
            self.right_dynamic_rect.width,
            self.right_dynamic_rect.height,
        ) != (
            self.source.right_rect.x + self.source.right_rect.width - self.right_width,
            self.source.right_rect.y,
            self.right_width,
            self.source.right_rect.height,
        ):
            raise PrematchSurfaceError("right dynamic rating rectangle is not mirrored")


@dataclass(frozen=True)
class BoundPrematchRatingRows:
    rows: tuple[BoundPrematchRatingSurface, ...]
    left_widths: PrematchTeamRatingWidths
    right_widths: PrematchTeamRatingWidths
    source_state_bound: bool = True
    native_mirroring_preserved: bool = True
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if len(self.rows) != 4:
            raise PrematchSurfaceError("bound pre-match rating set must have four rows")
        if not self.source_state_bound or not self.native_mirroring_preserved:
            raise PrematchSurfaceError("bound pre-match ratings cannot weaken source state")
        if self.complete_prematch_frame or self.gate14_complete:
            raise PrematchSurfaceError(
                "rating binding cannot promote complete-frame or Gate-14 claims"
            )


_PREMATCH_RATING_GROUP_NAMES = {
    3: "goalkeeper",
    0: "defence",
    1: "midfield",
    2: "attack",
}


def bind_prematch_rating_widths(
    boundary: "PrematchSurfaceBoundary",
    *,
    left_widths: PrematchTeamRatingWidths,
    right_widths: PrematchTeamRatingWidths,
) -> BoundPrematchRatingRows:
    """Bind exact native width results without mutating the resource boundary.

    Native side 0 grows rightward from x=65. Side 1 is anchored at its right
    edge (x=564+171) and therefore grows leftward by subtracting the width.
    """
    if type(boundary) is not PrematchSurfaceBoundary:
        raise PrematchSurfaceError("rating binding requires exact PrematchSurfaceBoundary")
    if type(left_widths) is not PrematchTeamRatingWidths:
        raise PrematchSurfaceError("left widths require exact PrematchTeamRatingWidths")
    if type(right_widths) is not PrematchTeamRatingWidths:
        raise PrematchSurfaceError("right widths require exact PrematchTeamRatingWidths")

    rows = []
    for source in boundary.rating_rows:
        discriminator = int(source.native_record_discriminator)
        try:
            semantic_group = _PREMATCH_RATING_GROUP_NAMES[discriminator]
        except KeyError as exc:
            raise PrematchSurfaceError(
                f"unsupported native rating discriminator: {discriminator}"
            ) from exc
        left_width = left_widths.by_discriminator(discriminator)
        right_width = right_widths.by_discriminator(discriminator)
        rows.append(
            BoundPrematchRatingSurface(
                source=source,
                semantic_group=semantic_group,
                left_width=left_width,
                right_width=right_width,
                left_dynamic_rect=OriginalRect(
                    source.left_rect.x,
                    source.left_rect.y,
                    left_width,
                    source.left_rect.height,
                ),
                right_dynamic_rect=OriginalRect(
                    source.right_rect.x + source.right_rect.width - right_width,
                    source.right_rect.y,
                    right_width,
                    source.right_rect.height,
                ),
            )
        )
    return BoundPrematchRatingRows(
        rows=tuple(rows),
        left_widths=left_widths,
        right_widths=right_widths,
    )


@dataclass(frozen=True)
class PrematchSurfaceBoundary:
    selection: FastViewSurfacedResourceSelection
    background: PrematchRasterLayer
    static_layers: tuple[PrematchRasterLayer, ...]
    selectors: tuple[PrematchSelectorSurface, ...]
    rating_rows: tuple[PrematchRatingSurface, ...]
    font: object
    team_backgrounds_contract_reused: bool = True
    source_assets_verified: bool = True
    native_geometry_preserved: bool = True
    rating_dynamic_widths_bound_to_cleanroom_state: bool = False
    full_cross_layer_draw_order_recovered: bool = False
    management_launch_trigger_recovered: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.selection) is not FastViewSurfacedResourceSelection:
            raise PrematchSurfaceError(
                "pre-match boundary requires exact source-backed background selection"
            )
        if self.background.role != "background":
            raise PrematchSurfaceError("pre-match background layer identity mismatch")
        if (
            self.background.rect.x,
            self.background.rect.y,
            self.background.rect.width,
            self.background.rect.height,
        ) != (0, 0, 800, 600):
            raise PrematchSurfaceError("pre-match live background must remain 800x600")
        if len(self.static_layers) != len(PREMATCH_STATIC_PLACEMENTS):
            raise PrematchSurfaceError("pre-match static layer set is incomplete")
        if len(self.selectors) != len(PREMATCH_SELECTORS):
            raise PrematchSurfaceError("pre-match selector surface set is incomplete")
        if len(self.rating_rows) != len(PREMATCH_RATING_ROWS):
            raise PrematchSurfaceError("pre-match rating row set is incomplete")
        if not (
            self.team_backgrounds_contract_reused
            and self.source_assets_verified
            and self.native_geometry_preserved
        ):
            raise PrematchSurfaceError("pre-match boundary cannot weaken verified source state")
        if (
            self.rating_dynamic_widths_bound_to_cleanroom_state
            or self.full_cross_layer_draw_order_recovered
            or self.management_launch_trigger_recovered
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchSurfaceError(
                "pre-match boundary cannot promote unresolved runtime/fidelity claims"
            )


def _layer_from_decoded(role, rect, spec, decoded) -> PrematchRasterLayer:
    if (decoded.width, decoded.height) != (rect.width, rect.height):
        raise PrematchSurfaceError(f"{role} decoded geometry differs from native rect")
    return PrematchRasterLayer(
        role=role,
        rect=rect,
        source_path=spec.source_path,
        rgba=decoded.rgba,
    )


def build_verified_prematch_surface_boundary(
    *,
    match_date: date,
    clubs: Mapping[int, object],
    countries: Mapping[int, object],
    home_club_id: int,
    away_club_id: int,
    background_club_override_id: int | None,
    source_root,
    original_executable,
) -> PrematchSurfaceBoundary:
    """Resolve and load only the source-proven pre-match presentation slice."""
    selection = build_fastview_surfaced_resource_selection(
        match_date=match_date,
        clubs=clubs,
        countries=countries,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        background_club_override_id=background_club_override_id,
    )
    background_resource: VerifiedFastViewSurfacedResource = (
        load_verified_selected_background(
            selection,
            source_root=source_root,
            original_executable=original_executable,
        )
    )
    if background_resource.role != "background":
        raise PrematchSurfaceError("shared Team_Backgrounds loader returned wrong role")
    if background_resource.geometry != (800, 600):
        raise PrematchSurfaceError("shared Team_Backgrounds resource is not 800x600")

    resources: OriginalPrematchPanelResources = load_verified_original_prematch_resources(
        source_root=source_root,
        original_executable=original_executable,
    )

    background = PrematchRasterLayer(
        role="background",
        rect=PREMATCH_LIVE_BACKGROUND_RECT,
        source_path=background_resource.source_path,
        rgba=background_resource.rgba,
    )
    static_layers = tuple(
        _layer_from_decoded(
            placement.role,
            placement.rect,
            placement.spec,
            resources.decoded(placement.spec.source_path),
        )
        for placement in PREMATCH_STATIC_PLACEMENTS
    )
    selectors = tuple(
        PrematchSelectorSurface(
            mode=int(selector.mode),
            event_id=selector.event_id,
            label=selector.label,
            rect=selector.rect,
            atlas=resources.selector_atlas,
        )
        for selector in PREMATCH_SELECTORS
    )

    left_dynamic = resources.decoded(PREMATCH_RATING_LEFT.source_path)
    left_base = resources.decoded(PREMATCH_RATING_RIGHT.source_path)
    right_base = resources.decoded(PREMATCH_RATING_RIGHT2.source_path)
    right_mask = resources.decoded(PREMATCH_RATING_RIGHT.source_path)
    rating_rows = tuple(
        PrematchRatingSurface(
            native_record_discriminator=row.native_record_discriminator,
            native_width_function_va=row.native_width_function_va,
            left_rect=OriginalRect(row.left_x, row.y, row.full_width, row.height),
            right_rect=OriginalRect(row.right_x, row.y, row.full_width, row.height),
            left_dynamic_rgba=left_dynamic.rgba,
            left_base_rgba=left_base.rgba,
            right_base_rgba=right_base.rgba,
            right_dynamic_mask_rgba=right_mask.rgba,
        )
        for row in PREMATCH_RATING_ROWS
    )

    return PrematchSurfaceBoundary(
        selection=selection,
        background=background,
        static_layers=static_layers,
        selectors=selectors,
        rating_rows=rating_rows,
        font=resources.font,
    )


def prematch_surface_contract() -> dict:
    return {
        "native_surface": (800, 600),
        "team_backgrounds_selector_reused": True,
        "team_backgrounds_loader_reused": True,
        "dedicated_static_asset_roles": tuple(
            placement.role for placement in PREMATCH_STATIC_PLACEMENTS
        ),
        "selector_modes": tuple(int(selector.mode) for selector in PREMATCH_SELECTORS),
        "selector_events": tuple(selector.event_id for selector in PREMATCH_SELECTORS),
        "rating_discriminators": tuple(
            row.native_record_discriminator for row in PREMATCH_RATING_ROWS
        ),
        "rating_width_binding_available": True,
        "rating_dynamic_widths_bound_by_resource_loader": False,
        "rating_dynamic_widths_bound_to_cleanroom_state": False,
        "full_cross_layer_draw_order_recovered": False,
        "management_launch_trigger_recovered": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
