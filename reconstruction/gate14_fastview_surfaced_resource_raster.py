"""Raster planes for verified FastView surfaced resources.

The full match background and the pair of club badges occupy different native
outer draw positions. They are therefore kept as two independent transparent
800x600 planes rather than flattened into one aggregate component.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_surfaced_picture_source import (
    AWAY_BADGE_RECT,
    FULL_SURFACE_RECT,
    HOME_BADGE_RECT,
)
from gate14_fastview_surfaced_resource_loader import (
    VerifiedFastViewSurfacedResource,
    VerifiedFastViewSurfacedResourceSet,
)


class FastViewSurfacedRasterError(ValueError):
    pass


FASTVIEW_SURFACE_SIZE = (800, 600)
BACKGROUND_COMPONENT = "match_background_surface"
BADGES_COMPONENT = "club_badge_surfaces"


@dataclass(frozen=True)
class FastViewSurfacedRasterPlane:
    component: str
    size: tuple[int, int]
    rgba: bytes
    source_layer_count: int
    rgba_sha256: str
    source_paths: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.component not in {BACKGROUND_COMPONENT, BADGES_COMPONENT}:
            raise FastViewSurfacedRasterError("unknown surfaced raster component")
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewSurfacedRasterError("surfaced raster must remain 800x600")
        if len(self.rgba) != 800 * 600 * 4:
            raise FastViewSurfacedRasterError("surfaced raster RGBA size mismatch")
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewSurfacedRasterError("surfaced raster SHA-256 mismatch")
        expected_layers = 1 if self.component == BACKGROUND_COMPONENT else 2
        if self.source_layer_count != expected_layers:
            raise FastViewSurfacedRasterError("surfaced raster source-layer count drifted")
        if len(self.source_paths) != expected_layers:
            raise FastViewSurfacedRasterError("surfaced raster source paths drifted")


@dataclass(frozen=True)
class FastViewSurfacedRasterSet:
    background: FastViewSurfacedRasterPlane
    badges: FastViewSurfacedRasterPlane
    source_bytes_loaded: bool = True
    ea444_decoded: bool = True
    outer_draw_positions_preserved: bool = True
    cross_component_blend_recovered: bool = False
    complete_fastview_frame_recovered: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if self.background.component != BACKGROUND_COMPONENT:
            raise FastViewSurfacedRasterError("background plane identity mismatch")
        if self.badges.component != BADGES_COMPONENT:
            raise FastViewSurfacedRasterError("badge plane identity mismatch")
        if not (
            self.source_bytes_loaded
            and self.ea444_decoded
            and self.outer_draw_positions_preserved
        ):
            raise FastViewSurfacedRasterError(
                "surfaced raster set cannot weaken verified source state"
            )
        if (
            self.cross_component_blend_recovered
            or self.complete_fastview_frame_recovered
            or self.gate14_complete
        ):
            raise FastViewSurfacedRasterError(
                "surfaced rasters cannot promote unresolved frame fidelity"
            )


def _copy_resource_into_surface(
    canvas: bytearray,
    resource: VerifiedFastViewSurfacedResource,
    rect: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if resource.geometry != (width, height):
        raise FastViewSurfacedRasterError(
            f"{resource.role} geometry does not match recovered control rectangle"
        )
    for y in range(height):
        src = y * width * 4
        dst = ((top + y) * 800 + left) * 4
        canvas[dst:dst + width * 4] = resource.rgba[src:src + width * 4]


def build_fastview_surfaced_rasters(
    resources: VerifiedFastViewSurfacedResourceSet,
) -> FastViewSurfacedRasterSet:
    if type(resources) is not VerifiedFastViewSurfacedResourceSet:
        raise FastViewSurfacedRasterError(
            "surfaced raster builder requires exact verified resource set"
        )

    # Background is already native full-surface geometry at the earliest outer
    # draw rank and therefore remains its own component plane.
    background_rgba = resources.background.rgba
    if resources.background.geometry != FASTVIEW_SURFACE_SIZE:
        raise FastViewSurfacedRasterError(
            "verified background no longer matches full FastView surface"
        )
    background = FastViewSurfacedRasterPlane(
        component=BACKGROUND_COMPONENT,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=background_rgba,
        source_layer_count=1,
        rgba_sha256=sha256(background_rgba).hexdigest(),
        source_paths=(resources.background.source_path,),
    )

    # Home and away badge controls are consecutive outer registrations after
    # ScoreCompositeMain and before PossessionDiagram. They share one aggregate
    # plane because they do not overlap each other and have identical relative
    # order against currently modeled raster families.
    badge_canvas = bytearray(800 * 600 * 4)
    _copy_resource_into_surface(
        badge_canvas,
        resources.home_badge,
        HOME_BADGE_RECT,
    )
    _copy_resource_into_surface(
        badge_canvas,
        resources.away_badge,
        AWAY_BADGE_RECT,
    )
    badge_rgba = bytes(badge_canvas)
    badges = FastViewSurfacedRasterPlane(
        component=BADGES_COMPONENT,
        size=FASTVIEW_SURFACE_SIZE,
        rgba=badge_rgba,
        source_layer_count=2,
        rgba_sha256=sha256(badge_rgba).hexdigest(),
        source_paths=(
            resources.home_badge.source_path,
            resources.away_badge.source_path,
        ),
    )
    return FastViewSurfacedRasterSet(background=background, badges=badges)


def surfaced_raster_contract() -> dict:
    return {
        "surface_size": FASTVIEW_SURFACE_SIZE,
        "background_component": BACKGROUND_COMPONENT,
        "background_rect": FULL_SURFACE_RECT,
        "background_outer_position": "first_outer_visible_control",
        "badges_component": BADGES_COMPONENT,
        "home_badge_rect": HOME_BADGE_RECT,
        "away_badge_rect": AWAY_BADGE_RECT,
        "badges_outer_position":
            "after_score_composite_main_before_possession_diagram",
        "background_and_badges_kept_separate": True,
        "source_bytes_loaded": True,
        "ea444_decoded": True,
        "cross_component_blend_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
