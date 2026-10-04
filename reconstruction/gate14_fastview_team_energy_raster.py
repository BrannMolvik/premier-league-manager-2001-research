"""Source-backed FastView TeamTable raster including dynamic energy crops.

Private canonical-executable tracing closes the generic PictureControl resize
rule needed by PlayerRow energy bars:

* EventPlayerUpdateEnergy changes only the dynamic PictureControl destination
  rectangle;
* the PictureControl renderer derives a source rectangle by offsetting from the
  original image with the clipped-control delta;
* source width/height are copied from the clipped destination width/height;
* the normal PictureControl path reaches DirectDraw Blt with those separate,
  equal-sized source/destination rectangles.

Therefore resized energy bars are cropped from the original 82x16 source image,
not stretched. PlayerRow construction order is static bar first, dynamic bar
second, so the cropped dynamic resource overlays the static resource.

Text pixels remain outside this module's fidelity boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_playerrow_snapshot import FastViewPlayerRowRenderPlan
from gate14_fastview_team import PLAYER_ROW_ENERGY_BAR_WIDTH
from gate14_fastview_team_static_raster import (
    FastViewTeamStaticRaster,
    FastViewTeamStaticRasterError,
    rasterize_fastview_team_static_rows,
)
from original_fastview_team_art import OriginalFastViewTeamArt


class FastViewTeamEnergyRasterError(ValueError):
    pass


PICTURECONTROL_RENDER_PREPARE_VA = 0x64E5D0
PICTURECONTROL_BLIT_WRAPPER_VA = 0x6556C0
PLAYERROW_ENERGY_RECT_WRITER_VA = 0x526680
PLAYERROW_STATIC_PICTURECONTROL_CREATE_VA = 0x5262E6
PLAYERROW_DYNAMIC_PICTURECONTROL_CREATE_VA = 0x526351


@dataclass(frozen=True)
class FastViewTeamEnergyRaster:
    size: tuple[int, int]
    rgba: bytes
    row_identities: tuple[tuple[int, int], ...]
    source_layer_count: int
    rgba_sha256: str
    dynamic_energy_rasterized: bool = True
    picturecontrol_resize_rule: str = "crop_equal_source_destination_extent"
    text_rasterized: bool = False
    complete_team_table: bool = False

    def __post_init__(self) -> None:
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster must retain the 800x600 FastView surface"
            )
        width, height = self.size
        if len(self.rgba) != width * height * 4:
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster RGBA payload has wrong size"
            )
        if len(set(self.row_identities)) != len(self.row_identities):
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster contains duplicate row identities"
            )
        if self.source_layer_count != 3 * len(self.row_identities):
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster must retain three source controls per row"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster SHA-256 does not match its RGBA payload"
            )
        if not self.dynamic_energy_rasterized:
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster cannot drop source-closed dynamic energy"
            )
        if self.picturecontrol_resize_rule != "crop_equal_source_destination_extent":
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster must retain the source-closed crop rule"
            )
        if self.text_rasterized or self.complete_team_table:
            raise FastViewTeamEnergyRasterError(
                "energy raster cannot promote unresolved TeamTable text/completeness"
            )


def _alpha_over_crop(
    canvas: bytearray,
    source_rgba: bytes,
    source_size: tuple[int, int],
    destination_rect: tuple[int, int, int, int],
) -> None:
    """Draw the top-left source crop matching the dynamic destination extent."""
    source_width, source_height = source_size
    if (
        type(destination_rect) is not tuple
        or len(destination_rect) != 4
        or any(type(value) is not int for value in destination_rect)
    ):
        raise FastViewTeamEnergyRasterError(
            "dynamic energy destination rect must contain four integers"
        )
    left, top, right, bottom = destination_rect
    width = right - left
    height = bottom - top

    # Source callback can produce an empty dynamic control at the exact endpoint.
    if width == 0:
        if height != source_height:
            raise FastViewTeamEnergyRasterError(
                "empty dynamic energy crop must retain source height"
            )
        return

    surface_width, surface_height = FASTVIEW_SURFACE_SIZE
    if (
        width < 0
        or height <= 0
        or width > source_width
        or height > source_height
        or not (0 <= left < right <= surface_width)
        or not (0 <= top < bottom <= surface_height)
    ):
        raise FastViewTeamEnergyRasterError(
            "dynamic energy crop lies outside the source-closed PictureControl domain"
        )
    if height != source_height:
        raise FastViewTeamEnergyRasterError(
            "dynamic energy crop must retain the full source bar height"
        )
    if len(source_rgba) != source_width * source_height * 4:
        raise FastViewTeamEnergyRasterError(
            "dynamic energy source RGBA geometry mismatch"
        )

    for y in range(height):
        for x in range(width):
            src = (y * source_width + x) * 4
            alpha = source_rgba[src + 3]
            if alpha == 0:
                continue
            dst = ((top + y) * surface_width + left + x) * 4
            if alpha == 255:
                canvas[dst:dst + 4] = source_rgba[src:src + 4]
                continue
            inv = 255 - alpha
            dst_alpha = canvas[dst + 3]
            out_alpha = alpha + (dst_alpha * inv + 127) // 255
            if out_alpha == 0:
                continue
            for channel in range(3):
                src_premul = source_rgba[src + channel] * alpha
                dst_premul = (
                    canvas[dst + channel] * dst_alpha * inv + 127
                ) // 255
                canvas[dst + channel] = (
                    src_premul + dst_premul + out_alpha // 2
                ) // out_alpha
            canvas[dst + 3] = out_alpha


def rasterize_fastview_team_energy_rows(
    art: OriginalFastViewTeamArt,
    render_plans: tuple[FastViewPlayerRowRenderPlan, ...],
) -> FastViewTeamEnergyRaster:
    """Rasterize static row art then source-cropped dynamic energy overlays."""
    if type(art) is not OriginalFastViewTeamArt:
        raise FastViewTeamEnergyRasterError(
            "TeamTable energy raster requires exact OriginalFastViewTeamArt"
        )
    if type(render_plans) is not tuple:
        raise FastViewTeamEnergyRasterError(
            "TeamTable render plans must be a retained tuple"
        )

    try:
        static = rasterize_fastview_team_static_rows(art, render_plans)
    except FastViewTeamStaticRasterError as exc:
        raise FastViewTeamEnergyRasterError(str(exc)) from exc
    if type(static) is not FastViewTeamStaticRaster:
        raise FastViewTeamEnergyRasterError(
            "TeamTable energy raster requires exact static-raster boundary"
        )

    canvas = bytearray(static.rgba)
    identities: list[tuple[int, int]] = []
    for plan in render_plans:
        if type(plan) is not FastViewPlayerRowRenderPlan:
            raise FastViewTeamEnergyRasterError(
                "TeamTable energy raster requires exact PlayerRow render plans"
            )
        identity = (int(plan.side_index), int(plan.row_index))
        if identity in identities:
            raise FastViewTeamEnergyRasterError(
                f"duplicate TeamTable PlayerRow identity: {identity}"
            )
        identities.append(identity)

        full_left, full_top, full_right, full_bottom = plan.energy_full_rect
        dyn_left, dyn_top, dyn_right, dyn_bottom = plan.energy_dynamic_rect
        if (
            dyn_left != full_left
            or dyn_top != full_top
            or dyn_bottom != full_bottom
            or (full_right - full_left) != PLAYER_ROW_ENERGY_BAR_WIDTH
        ):
            raise FastViewTeamEnergyRasterError(
                "dynamic energy crop drifted from source PlayerRow rectangle ownership"
            )

        image = art.image_for(plan.dynamic_energy_resource)
        if (image.width, image.height) != (
            PLAYER_ROW_ENERGY_BAR_WIDTH,
            full_bottom - full_top,
        ):
            raise FastViewTeamEnergyRasterError(
                "dynamic energy resource geometry drifted from source bar"
            )
        _alpha_over_crop(
            canvas,
            image.rgba,
            (image.width, image.height),
            plan.energy_dynamic_rect,
        )

    rgba = bytes(canvas)
    return FastViewTeamEnergyRaster(
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        row_identities=tuple(identities),
        source_layer_count=3 * len(identities),
        rgba_sha256=sha256(rgba).hexdigest(),
    )
