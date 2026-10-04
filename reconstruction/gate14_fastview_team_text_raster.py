"""Source-backed partial FastView PlayerRow text raster.

Private canonical-executable tracing closes the shared PlayerRow text-control
style without inventing localization or the own-goal recolor:

* all six controls use source text style index 3;
* style 3 binds Fonts/Zurich_XCn_BT_16pixel.fnt;
* constructor color is native 0xFFFF;
* raw flags 0x24 mean horizontal-center + vertical-center;
* raw flags 0x21 mean left + vertical-center;
* the native font line height is 18 while each control is 16 px tall, so the
  centered line is intentionally clipped by the control rectangle.

Only literal cells that retain the default source color are rasterized here.
Position remains a localization key and a written own-goal cell retains an
unresolved source color update, so both remain explicit unresolved cells.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont, EAFontError
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE
from gate14_fastview_playerrow_snapshot import (
    FastViewPlayerRowRenderPlan,
    FastViewPlayerRowTextRenderInstruction,
)
from original_live_debug_view import endpoint_text_rgba


class FastViewTeamTextRasterError(ValueError):
    pass


PLAYERROW_TEXT_STYLE_INDEX = 3
PLAYERROW_TEXT_NATIVE_COLOR_16 = 0xFFFF
PLAYERROW_TEXT_FONT_PATH = "Fonts/Zurich_XCn_BT_16pixel.fnt"
PLAYERROW_TEXT_FONT_BYTE_SIZE = 75_217
PLAYERROW_TEXT_FONT_SHA256 = (
    "e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18"
)
PLAYERROW_TEXT_FONT_ATLAS_SIZE = (1261, 17)
PLAYERROW_TEXT_NATIVE_LINE_HEIGHT = 18

# Source constructor order uses these flags for cells 1..6.
PLAYERROW_TEXT_FLAGS = (0x24, 0x24, 0x21, 0x21, 0x21, 0x24)


@dataclass(frozen=True)
class FastViewUnresolvedPlayerRowText:
    side_index: int
    row_index: int
    text_cell_index: int
    semantic: str
    reason: str

    def __post_init__(self) -> None:
        if self.text_cell_index not in range(1, 7):
            raise FastViewTeamTextRasterError("unresolved text cell must be 1..6")
        if not self.semantic or not self.reason:
            raise FastViewTeamTextRasterError(
                "unresolved text cell requires semantic and reason"
            )


@dataclass(frozen=True)
class FastViewTeamTextRaster:
    size: tuple[int, int]
    rgba: bytes
    rendered_cells: tuple[tuple[int, int, int], ...]
    unresolved_cells: tuple[FastViewUnresolvedPlayerRowText, ...]
    source_font_sha256: str
    rgba_sha256: str
    text_style_index: int = PLAYERROW_TEXT_STYLE_INDEX
    native_color_16: int = PLAYERROW_TEXT_NATIVE_COLOR_16
    position_localization_recovered: bool = False
    own_goal_color_recovered: bool = False
    complete_team_table_text: bool = False

    def __post_init__(self) -> None:
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster must retain the 800x600 FastView surface"
            )
        width, height = self.size
        if len(self.rgba) != width * height * 4:
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster RGBA payload has wrong size"
            )
        if len(set(self.rendered_cells)) != len(self.rendered_cells):
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster contains duplicate rendered cells"
            )
        unresolved_ids = tuple(
            (item.side_index, item.row_index, item.text_cell_index)
            for item in self.unresolved_cells
        )
        if len(set(unresolved_ids)) != len(unresolved_ids):
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster contains duplicate unresolved cells"
            )
        if set(self.rendered_cells) & set(unresolved_ids):
            raise FastViewTeamTextRasterError(
                "PlayerRow text cell cannot be rendered and unresolved"
            )
        if self.source_font_sha256 != PLAYERROW_TEXT_FONT_SHA256:
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster must retain the verified source font hash"
            )
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster SHA-256 does not match RGBA payload"
            )
        if (
            self.text_style_index != PLAYERROW_TEXT_STYLE_INDEX
            or self.native_color_16 != PLAYERROW_TEXT_NATIVE_COLOR_16
        ):
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster style/color drifted from source"
            )
        if (
            self.position_localization_recovered
            or self.own_goal_color_recovered
            or self.complete_team_table_text
        ):
            raise FastViewTeamTextRasterError(
                "partial PlayerRow text raster cannot promote unresolved fidelity"
            )


def load_verified_playerrow_text_font(repo_root: str | Path) -> EAFont:
    path = (
        Path(repo_root)
        / "original_assets"
        / "source"
        / PLAYERROW_TEXT_FONT_PATH
    )
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise FastViewTeamTextRasterError(
            f"Missing staged PlayerRow font: {PLAYERROW_TEXT_FONT_PATH}"
        ) from exc
    if len(data) != PLAYERROW_TEXT_FONT_BYTE_SIZE:
        raise FastViewTeamTextRasterError(
            "PlayerRow font byte-size mismatch"
        )
    if sha256(data).hexdigest() != PLAYERROW_TEXT_FONT_SHA256:
        raise FastViewTeamTextRasterError(
            "PlayerRow font checksum mismatch"
        )
    try:
        font = EAFont.from_bytes(data)
    except EAFontError as exc:
        raise FastViewTeamTextRasterError(str(exc)) from exc
    if (font.atlas_width, font.atlas_height) != PLAYERROW_TEXT_FONT_ATLAS_SIZE:
        raise FastViewTeamTextRasterError(
            "PlayerRow font atlas geometry mismatch"
        )
    if font.native_line_height() != PLAYERROW_TEXT_NATIVE_LINE_HEIGHT:
        raise FastViewTeamTextRasterError(
            "PlayerRow font native line-height mismatch"
        )
    return font


def _alignment_for_cell(text_cell_index: int) -> tuple[str, str]:
    if type(text_cell_index) is not int or not 1 <= text_cell_index <= 6:
        raise FastViewTeamTextRasterError("PlayerRow text cell must be 1..6")
    flags = PLAYERROW_TEXT_FLAGS[text_cell_index - 1]
    horizontal = "center" if flags & 0x04 else "left"
    vertical = "center" if flags & 0x20 else "top"
    if flags & 0x02 or flags & 0x10:
        raise FastViewTeamTextRasterError(
            "unexpected right/bottom PlayerRow text alignment flag"
        )
    return horizontal, vertical


def _line_origin(
    font: EAFont,
    instruction: FastViewPlayerRowTextRenderInstruction,
) -> tuple[int, int]:
    if instruction.value is None:
        raise FastViewTeamTextRasterError(
            "written PlayerRow text instruction requires a value"
        )
    left, top, right, bottom = instruction.rect
    width = right - left
    height = bottom - top
    text_width = font.measure_text(instruction.value)
    horizontal, vertical = _alignment_for_cell(instruction.text_cell_index)

    if horizontal == "center":
        # Native renderer computes half-control minus half-text independently.
        x = left + width // 2 - text_width // 2
    else:
        x = left

    if vertical == "center":
        y = top + height // 2 - font.native_line_height() // 2
    else:
        y = top
    return x, y


def _draw_clipped_text(
    canvas: bytearray,
    font: EAFont,
    instruction: FastViewPlayerRowTextRenderInstruction,
) -> None:
    if instruction.value is None:
        raise FastViewTeamTextRasterError(
            "written PlayerRow text instruction requires a value"
        )
    mask = font.render_text_alpha(instruction.value)
    if mask.width == 0 or mask.height == 0:
        return
    rgba = endpoint_text_rgba(mask.alpha, PLAYERROW_TEXT_NATIVE_COLOR_16)
    origin_x, origin_y = _line_origin(font, instruction)
    clip_left, clip_top, clip_right, clip_bottom = instruction.rect
    surface_width, surface_height = FASTVIEW_SURFACE_SIZE

    for y in range(mask.height):
        dst_y = origin_y + y
        if dst_y < clip_top or dst_y >= clip_bottom:
            continue
        if not 0 <= dst_y < surface_height:
            continue
        for x in range(mask.width):
            dst_x = origin_x + x
            if dst_x < clip_left or dst_x >= clip_right:
                continue
            if not 0 <= dst_x < surface_width:
                continue
            src = (y * mask.width + x) * 4
            alpha = rgba[src + 3]
            if alpha == 0:
                continue
            dst = (dst_y * surface_width + dst_x) * 4
            canvas[dst:dst + 4] = rgba[src:src + 4]


def rasterize_fastview_playerrow_text(
    repo_root: str | Path,
    render_plans: tuple[FastViewPlayerRowRenderPlan, ...],
) -> FastViewTeamTextRaster:
    """Rasterize only literal/default-color PlayerRow text cells.

    The verified font is loaded internally so callers cannot substitute a
    same-shaped font while retaining the canonical source hash.
    """
    font = load_verified_playerrow_text_font(repo_root)
    if type(render_plans) is not tuple:
        raise FastViewTeamTextRasterError(
            "PlayerRow text render plans must be a retained tuple"
        )

    width, height = FASTVIEW_SURFACE_SIZE
    canvas = bytearray(width * height * 4)
    rendered: list[tuple[int, int, int]] = []
    unresolved: list[FastViewUnresolvedPlayerRowText] = []

    for plan in render_plans:
        if type(plan) is not FastViewPlayerRowRenderPlan:
            raise FastViewTeamTextRasterError(
                "PlayerRow text raster requires exact render plans"
            )
        for instruction in plan.text_instructions:
            identity = (
                int(plan.side_index),
                int(plan.row_index),
                int(instruction.text_cell_index),
            )
            if instruction.value_kind == "unwritten":
                continue
            if instruction.value_kind == "localization_key":
                unresolved.append(
                    FastViewUnresolvedPlayerRowText(
                        *identity,
                        semantic=instruction.semantic,
                        reason="position_localization_string_not_source_bound",
                    )
                )
                continue
            if instruction.value_kind != "literal":
                raise FastViewTeamTextRasterError(
                    "unknown PlayerRow text instruction value kind"
                )
            if instruction.source_color_update:
                unresolved.append(
                    FastViewUnresolvedPlayerRowText(
                        *identity,
                        semantic=instruction.semantic,
                        reason="native_source_color_update_not_rgba_bound",
                    )
                )
                continue
            _draw_clipped_text(canvas, font, instruction)
            rendered.append(identity)

    rgba = bytes(canvas)
    return FastViewTeamTextRaster(
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        rendered_cells=tuple(rendered),
        unresolved_cells=tuple(unresolved),
        source_font_sha256=PLAYERROW_TEXT_FONT_SHA256,
        rgba_sha256=sha256(rgba).hexdigest(),
    )
