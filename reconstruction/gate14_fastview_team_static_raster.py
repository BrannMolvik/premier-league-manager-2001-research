"""Rasterize the source-closed static FastView TeamTable row art.

This is intentionally a partial TeamTable pixel layer. For each retained
PlayerRow render plan, only two source-closed full-size PictureControl layers
are drawn:

* the selected 259x16 name-grid resource;
* the 82x16 static energy-bar resource.

Dynamic energy-bar resizing is not rasterized because the exact generic
PictureControl source-rectangle behavior for resized destinations remains a
separate evidence boundary. Text controls are also left out until their font,
color and localization inputs are fully bound at the raster layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_playerrow_snapshot import FastViewPlayerRowRenderPlan
from original_fastview_team_art import OriginalFastViewTeamArt


class FastViewTeamStaticRasterError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewTeamStaticRaster:
    size: tuple[int, int]
    rgba: bytes
    row_identities: tuple[tuple[int, int], ...]
    source_layer_count: int
    rgba_sha256: str
    dynamic_energy_rasterized: bool = False
    text_rasterized: bool = False
    complete_team_table: bool = False

    def __post_init__(self) -> None:
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewTeamStaticRasterError(
                "TeamTable static raster must retain the 800x600 FastView surface"
            )
        width, height = self.size
        if len(self.rgba) != width * height * 4:
            raise FastViewTeamStaticRasterError(
                "TeamTable static raster RGBA payload has wrong size"
            )
        if len(set(self.row_identities)) != len(self.row_identities):
            raise FastViewTeamStaticRasterError(
                "TeamTable static raster contains duplicate row identities"
            )
        if self.source_layer_count != 2 * len(self.row_identities):
            raise FastViewTeamStaticRasterError(
                "TeamTable static raster must contain two source layers per row"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewTeamStaticRasterError(
                "TeamTable static raster SHA-256 does not match its RGBA payload"
            )
        if (
            self.dynamic_energy_rasterized
            or self.text_rasterized
            or self.complete_team_table
        ):
            raise FastViewTeamStaticRasterError(
                "static TeamTable raster cannot promote unresolved dynamic/text pixels"
            )


def _validate_rect(
    rect: tuple[int, int, int, int],
    width: int,
    height: int,
) -> None:
    if (
        type(rect) is not tuple
        or len(rect) != 4
        or any(type(value) is not int for value in rect)
    ):
        raise FastViewTeamStaticRasterError(
            "TeamTable source rect must contain four integers"
        )
    left, top, right, bottom = rect
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    if not (
        0 <= left < right <= surface_width
        and 0 <= top < bottom <= surface_height
    ):
        raise FastViewTeamStaticRasterError(
            "TeamTable source rect lies outside the 800x600 surface"
        )
    if (right - left, bottom - top) != (width, height):
        raise FastViewTeamStaticRasterError(
            "TeamTable source rect does not match decoded resource geometry"
        )


def _alpha_over(
    canvas: bytearray,
    source: bytes,
    rect: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if len(source) != width * height * 4:
        raise FastViewTeamStaticRasterError(
            "TeamTable source RGBA does not match placement geometry"
        )

    surface_width, _ = FASTVIEW_SURFACE_SIZE
    for y in range(height):
        for x in range(width):
            src = (y * width + x) * 4
            alpha = source[src + 3]
            if alpha == 0:
                continue
            dst = ((top + y) * surface_width + left + x) * 4
            if alpha == 255:
                canvas[dst:dst + 4] = source[src:src + 4]
                continue

            inv = 255 - alpha
            dst_alpha = canvas[dst + 3]
            out_alpha = alpha + (dst_alpha * inv + 127) // 255
            if out_alpha == 0:
                continue
            for channel in range(3):
                src_premul = source[src + channel] * alpha
                dst_premul = (
                    canvas[dst + channel] * dst_alpha * inv + 127
                ) // 255
                canvas[dst + channel] = (
                    src_premul + dst_premul + out_alpha // 2
                ) // out_alpha
            canvas[dst + 3] = out_alpha


def rasterize_fastview_team_static_rows(
    art: OriginalFastViewTeamArt,
    render_plans: tuple[FastViewPlayerRowRenderPlan, ...],
) -> FastViewTeamStaticRaster:
    """Draw only full-size source-closed static row assets in plan order."""
    if type(art) is not OriginalFastViewTeamArt:
        raise FastViewTeamStaticRasterError(
            "TeamTable static raster requires exact OriginalFastViewTeamArt"
        )
    if type(render_plans) is not tuple:
        raise FastViewTeamStaticRasterError(
            "TeamTable render plans must be a retained tuple"
        )

    identities: list[tuple[int, int]] = []
    canvas = bytearray(FASTVIEW_SURFACE_SIZE[0] * FASTVIEW_SURFACE_SIZE[1] * 4)

    for plan in render_plans:
        if type(plan) is not FastViewPlayerRowRenderPlan:
            raise FastViewTeamStaticRasterError(
                "TeamTable static raster requires exact PlayerRow render plans"
            )
        identity = (int(plan.side_index), int(plan.row_index))
        if identity in identities:
            raise FastViewTeamStaticRasterError(
                f"duplicate TeamTable PlayerRow identity: {identity}"
            )
        identities.append(identity)

        name_image = art.image_for(plan.name_grid_resource)
        _validate_rect(
            plan.name_grid_rect,
            name_image.width,
            name_image.height,
        )
        _alpha_over(canvas, name_image.rgba, plan.name_grid_rect)

        static_image = art.image_for(plan.static_energy_resource)
        _validate_rect(
            plan.energy_full_rect,
            static_image.width,
            static_image.height,
        )
        _alpha_over(canvas, static_image.rgba, plan.energy_full_rect)

    rgba = bytes(canvas)
    return FastViewTeamStaticRaster(
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        row_identities=tuple(identities),
        source_layer_count=2 * len(identities),
        rgba_sha256=sha256(rgba).hexdigest(),
    )
