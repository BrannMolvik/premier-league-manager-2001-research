"""Complete source-backed raster for retained FastView PlayerRow controls.

This composes two already source-closed per-row raster domains:

* name-grid + static/dynamic energy PictureControls;
* all six PlayerRow text controls for the canonical English release.

Native PlayerRow construction order is name-grid, six text controls, static
energy PictureControl, dynamic energy PictureControl. The energy bar rectangle
is source-proven disjoint from every text rectangle for both side layouts, so
alpha-compositing the text plane over the already-composed energy raster is
pixel-equivalent to native order while retaining a simple fail-closed boundary.

This does not claim non-row TeamTable presentation, global FastView z-order,
background ownership, audio, or 3D choreography.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_playerrow_snapshot import FastViewPlayerRowRenderPlan
from gate14_fastview_team_energy_raster import FastViewTeamEnergyRaster
from gate14_fastview_team_text_raster import FastViewTeamTextRaster


class FastViewPlayerRowsRasterError(ValueError):
    pass


PLAYERROW_NAME_GRID_CREATE_VA = 0x525E7F
PLAYERROW_FIRST_TEXT_CREATE_VA = 0x525F1A
PLAYERROW_LAST_TEXT_CREATE_VA = 0x526244
PLAYERROW_STATIC_BAR_CREATE_VA = 0x5262E6
PLAYERROW_DYNAMIC_BAR_CREATE_VA = 0x526351


@dataclass(frozen=True)
class FastViewPlayerRowsRaster:
    size: tuple[int, int]
    rgba: bytes
    row_identities: tuple[tuple[int, int], ...]
    energy_rgba_sha256: str
    text_rgba_sha256: str
    rgba_sha256: str
    native_row_control_order_recovered: bool = True
    text_energy_rectangles_disjoint: bool = True
    complete_retained_player_rows: bool = True
    complete_team_table: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewPlayerRowsRasterError(
                "PlayerRows raster must retain the 800x600 FastView surface"
            )
        width, height = self.size
        if len(self.rgba) != width * height * 4:
            raise FastViewPlayerRowsRasterError(
                "PlayerRows raster RGBA payload has wrong size"
            )
        if len(set(self.row_identities)) != len(self.row_identities):
            raise FastViewPlayerRowsRasterError(
                "PlayerRows raster contains duplicate row identities"
            )
        for digest in (
            self.energy_rgba_sha256,
            self.text_rgba_sha256,
            self.rgba_sha256,
        ):
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(ch not in "0123456789abcdef" for ch in digest)
            ):
                raise FastViewPlayerRowsRasterError(
                    "PlayerRows raster hashes must be lowercase SHA-256"
                )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewPlayerRowsRasterError(
                "PlayerRows raster SHA-256 does not match RGBA payload"
            )
        if not (
            self.native_row_control_order_recovered
            and self.text_energy_rectangles_disjoint
            and self.complete_retained_player_rows
        ):
            raise FastViewPlayerRowsRasterError(
                "PlayerRows raster cannot weaken source-closed retained-row fidelity"
            )
        if self.complete_team_table or self.complete_fastview_frame:
            raise FastViewPlayerRowsRasterError(
                "retained PlayerRows raster cannot promote broader completeness"
            )


def _rects_overlap(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
) -> bool:
    a_left, a_top, a_right, a_bottom = first
    b_left, b_top, b_right, b_bottom = second
    return (
        max(a_left, b_left) < min(a_right, b_right)
        and max(a_top, b_top) < min(a_bottom, b_bottom)
    )


def _alpha_over_surface(canvas: bytearray, source_rgba: bytes) -> None:
    width, height = FASTVIEW_SURFACE_SIZE
    if len(source_rgba) != width * height * 4:
        raise FastViewPlayerRowsRasterError(
            "PlayerRow text plane has wrong FastView surface size"
        )
    for pixel in range(width * height):
        src = pixel * 4
        alpha = source_rgba[src + 3]
        if alpha == 0:
            continue
        dst = src
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


def compose_fastview_player_rows_raster(
    energy: FastViewTeamEnergyRaster,
    text: FastViewTeamTextRaster,
    render_plans: tuple[FastViewPlayerRowRenderPlan, ...],
) -> FastViewPlayerRowsRaster:
    """Compose source-closed retained PlayerRow controls only."""
    if type(energy) is not FastViewTeamEnergyRaster:
        raise FastViewPlayerRowsRasterError(
            "PlayerRows raster requires exact FastViewTeamEnergyRaster"
        )
    if type(text) is not FastViewTeamTextRaster:
        raise FastViewPlayerRowsRasterError(
            "PlayerRows raster requires exact FastViewTeamTextRaster"
        )
    if type(render_plans) is not tuple:
        raise FastViewPlayerRowsRasterError(
            "PlayerRows render plans must be a retained tuple"
        )
    if energy.size != FASTVIEW_SURFACE_SIZE or text.size != FASTVIEW_SURFACE_SIZE:
        raise FastViewPlayerRowsRasterError(
            "PlayerRows source rasters must retain the FastView surface"
        )
    if not (
        energy.dynamic_energy_rasterized
        and not energy.text_rasterized
        and text.complete_team_table_text
        and text.position_english_localization_recovered
        and text.own_goal_color_recovered
    ):
        raise FastViewPlayerRowsRasterError(
            "PlayerRows source rasters do not expose the required fidelity"
        )

    identities: list[tuple[int, int]] = []
    expected_rendered = set()
    for plan in render_plans:
        if type(plan) is not FastViewPlayerRowRenderPlan:
            raise FastViewPlayerRowsRasterError(
                "PlayerRows raster requires exact PlayerRow render plans"
            )
        identity = (int(plan.side_index), int(plan.row_index))
        if identity in identities:
            raise FastViewPlayerRowsRasterError(
                f"duplicate retained PlayerRow identity: {identity}"
            )
        identities.append(identity)
        for instruction in plan.text_instructions:
            if _rects_overlap(instruction.rect, plan.energy_full_rect):
                raise FastViewPlayerRowsRasterError(
                    "PlayerRow text overlaps energy bar; simple composition is not source-safe"
                )
            if instruction.value_kind != "unwritten":
                expected_rendered.add(
                    (
                        int(plan.side_index),
                        int(plan.row_index),
                        int(instruction.text_cell_index),
                    )
                )

    if tuple(identities) != energy.row_identities:
        raise FastViewPlayerRowsRasterError(
            "energy raster row identities drifted from retained render plans"
        )
    if set(text.rendered_cells) != expected_rendered:
        raise FastViewPlayerRowsRasterError(
            "text raster rendered-cell set drifted from retained render plans"
        )
    if text.unresolved_cells:
        raise FastViewPlayerRowsRasterError(
            "complete English PlayerRow text raster cannot retain unresolved cells"
        )

    canvas = bytearray(energy.rgba)
    _alpha_over_surface(canvas, text.rgba)
    rgba = bytes(canvas)
    return FastViewPlayerRowsRaster(
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        row_identities=tuple(identities),
        energy_rgba_sha256=energy.rgba_sha256,
        text_rgba_sha256=text.rgba_sha256,
        rgba_sha256=sha256(rgba).hexdigest(),
    )
