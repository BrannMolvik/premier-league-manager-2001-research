"""Exact source-font rasterization for supplied PPreMatch TextControls.

This module consumes already-bound PPreMatch strings/player rows and the exact
original TextStyle font resources. Each visible text child is rasterized into
its own native control rectangle and retains its source child index, so later
composition can preserve the proven 0..181 paint order.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from gate14_prematch_text_binding import BoundPrematchDynamicText
from gate14_prematch_text_style import (
    PREMATCH_DATE_WEATHER_FLAGS,
    PREMATCH_FIXTURE_HEADER_FLAGS,
    PREMATCH_HEADER_STYLE,
    PREMATCH_LEFT_PLAYER_NAME_FLAGS,
    PREMATCH_LEFT_TEAM_IDENTITY_FLAGS,
    PREMATCH_PLAYER_NUMBER_FLAGS,
    PREMATCH_RATING_CAPTION_FLAGS,
    PREMATCH_RIGHT_PLAYER_NAME_FLAGS,
    PREMATCH_RIGHT_TEAM_IDENTITY_FLAGS,
    PREMATCH_ROW_STYLE,
    PREMATCH_TEAM_STYLE,
    PREMATCH_VERSUS_FLAGS,
    PREMATCH_VERSUS_STYLE,
    TEXT_ALIGN_BOTTOM,
    TEXT_ALIGN_HCENTER,
    TEXT_ALIGN_RIGHT,
    TEXT_ALIGN_VCENTER,
    TEXT_NATIVE_COLOR_16,
    TEXT_ROTATED_ORIENTATION,
)
from original_front_end_layout import OriginalRect
from original_live_debug_view import endpoint_text_rgba


class PrematchTextRasterError(ValueError):
    pass


PREMATCH_DIRECT_TEXT_CHILD_INDEX = {
    "fixture_header": 3,
    "date_weather": 4,
    "team_identity_0": 7,
    "versus": 8,
    "team_identity_1": 9,
    "rating_left_gk": 170,
    "rating_left_def": 171,
    "rating_left_mid": 172,
    "rating_left_att": 173,
    "rating_right_gk": 174,
    "rating_right_def": 175,
    "rating_right_mid": 176,
    "rating_right_att": 177,
}


@dataclass(frozen=True)
class PrematchTextFontSet:
    header: object
    team: object
    versus: object
    row: object
    source_bytes_verified: bool = True

    def __post_init__(self) -> None:
        for font, style in (
            (self.header, PREMATCH_HEADER_STYLE),
            (self.team, PREMATCH_TEAM_STYLE),
            (self.versus, PREMATCH_VERSUS_STYLE),
            (self.row, PREMATCH_ROW_STYLE),
        ):
            for method in ("measure_text", "native_line_height", "render_text_alpha"):
                if not callable(getattr(font, method, None)):
                    raise PrematchTextRasterError(
                        "pre-match text font does not expose required EAFont behavior"
                    )
            if (
                getattr(font, "atlas_width", None),
                getattr(font, "atlas_height", None),
            ) != style.atlas_size:
                raise PrematchTextRasterError(
                    f"{style.semantic} font atlas geometry mismatch"
                )
            if font.native_line_height() != style.native_line_height:
                raise PrematchTextRasterError(
                    f"{style.semantic} font line-height mismatch"
                )
        if not self.source_bytes_verified:
            raise PrematchTextRasterError(
                "PPreMatch text fonts must retain verified original bytes"
            )

    def for_wrapper(self, wrapper_va: int):
        mapping = {
            PREMATCH_HEADER_STYLE.wrapper_va: self.header,
            PREMATCH_TEAM_STYLE.wrapper_va: self.team,
            PREMATCH_VERSUS_STYLE.wrapper_va: self.versus,
            PREMATCH_ROW_STYLE.wrapper_va: self.row,
        }
        try:
            return mapping[wrapper_va]
        except KeyError as exc:
            raise PrematchTextRasterError(
                f"unknown PPreMatch TextStyle wrapper {wrapper_va:#x}"
            ) from exc


@dataclass(frozen=True)
class PrematchTextRasterChild:
    child_index: int
    role: str
    text: str
    rect: OriginalRect
    raw_flags: int
    style_wrapper_va: int
    line_origin: tuple[int, int]
    glyph_size: tuple[int, int]
    rgba: bytes
    rgba_sha256: str
    native_color_16: int = TEXT_NATIVE_COLOR_16

    def __post_init__(self) -> None:
        if type(self.child_index) is not int or not 0 <= self.child_index < 182:
            raise PrematchTextRasterError("text child index must be native 0..181")
        if not self.role or not isinstance(self.text, str) or not self.text:
            raise PrematchTextRasterError("visible text child requires role/text")
        if self.raw_flags & TEXT_ROTATED_ORIENTATION:
            raise PrematchTextRasterError(
                "PPreMatch text raster cannot silently accept rotated orientation"
            )
        if len(self.rgba) != self.rect.width * self.rect.height * 4:
            raise PrematchTextRasterError("text child RGBA geometry mismatch")
        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise PrematchTextRasterError("text child RGBA checksum mismatch")
        if self.native_color_16 != TEXT_NATIVE_COLOR_16:
            raise PrematchTextRasterError("PPreMatch text color drifted")


@dataclass(frozen=True)
class PrematchTextRasterSet:
    children: tuple[PrematchTextRasterChild, ...]
    registered_text_child_indices: tuple[int, ...]
    hidden_text_child_indices: tuple[int, ...]
    source_fonts_verified: bool = True
    source_alignment_preserved: bool = True
    source_control_clipping_preserved: bool = True
    text_pixels_rasterized: bool = True
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        indices = tuple(child.child_index for child in self.children)
        if indices != tuple(sorted(indices)) or len(indices) != len(set(indices)):
            raise PrematchTextRasterError(
                "visible text children must keep unique ascending native indices"
            )
        if set(indices).intersection(self.hidden_text_child_indices):
            raise PrematchTextRasterError("visible/hidden text child sets overlap")
        if tuple(sorted(indices + self.hidden_text_child_indices)) != (
            self.registered_text_child_indices
        ):
            raise PrematchTextRasterError(
                "visible/hidden text children do not cover registered controls"
            )
        if not (
            self.source_fonts_verified
            and self.source_alignment_preserved
            and self.source_control_clipping_preserved
            and self.text_pixels_rasterized
        ):
            raise PrematchTextRasterError(
                "text raster set cannot weaken verified source state"
            )
        if self.complete_prematch_frame or self.gate14_complete:
            raise PrematchTextRasterError(
                "text rasterization cannot promote complete frame/Gate 14"
            )


def _read_verified_font(root: Path, style):
    path = root.joinpath(*style.source_path.replace("\\", "/").split("/"))
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise PrematchTextRasterError(
            f"missing original PPreMatch font: {style.source_path}"
        ) from exc
    if len(raw) != style.source_size:
        raise PrematchTextRasterError(
            f"PPreMatch font size mismatch: {style.source_path}"
        )
    if sha256(raw).hexdigest() != style.source_sha256:
        raise PrematchTextRasterError(
            f"PPreMatch font checksum mismatch: {style.source_path}"
        )
    try:
        font = EAFont.from_bytes(raw)
    except Exception as exc:
        raise PrematchTextRasterError(
            f"PPreMatch font parse failed: {style.source_path}"
        ) from exc
    if (font.atlas_width, font.atlas_height) != style.atlas_size:
        raise PrematchTextRasterError(
            f"PPreMatch font atlas mismatch: {style.source_path}"
        )
    if font.native_line_height() != style.native_line_height:
        raise PrematchTextRasterError(
            f"PPreMatch font line height mismatch: {style.source_path}"
        )
    return font


def load_verified_prematch_text_fonts(source_root: str | Path) -> PrematchTextFontSet:
    root = Path(source_root)
    if not root.is_dir():
        raise PrematchTextRasterError("original source root is unavailable")
    return PrematchTextFontSet(
        header=_read_verified_font(root, PREMATCH_HEADER_STYLE),
        team=_read_verified_font(root, PREMATCH_TEAM_STYLE),
        versus=_read_verified_font(root, PREMATCH_VERSUS_STYLE),
        row=_read_verified_font(root, PREMATCH_ROW_STYLE),
    )


def _trunc_half(value: int) -> int:
    if type(value) is not int:
        raise PrematchTextRasterError("alignment delta must be integer")
    return value // 2 if value >= 0 else -((-value) // 2)


def source_text_line_origin(font, text: str, rect: OriginalRect, raw_flags: int):
    """Mirror ordinary-orientation branches in TextStyle draw 0x64F090."""
    if raw_flags & TEXT_ROTATED_ORIENTATION:
        raise PrematchTextRasterError(
            "rotated TextControl orientation is outside PPreMatch text contract"
        )
    if not isinstance(text, str) or not text:
        raise PrematchTextRasterError("text line origin requires non-empty text")

    text_width = font.measure_text(text)
    line_height = font.native_line_height()

    if raw_flags & TEXT_ALIGN_RIGHT:
        dx = rect.width - text_width
    elif raw_flags & TEXT_ALIGN_HCENTER:
        dx = _trunc_half(rect.width - text_width)
    else:
        dx = 0

    if raw_flags & TEXT_ALIGN_BOTTOM:
        dy = rect.height - line_height
    elif raw_flags & TEXT_ALIGN_VCENTER:
        dy = _trunc_half(rect.height - line_height)
    else:
        dy = 0
    return rect.x + dx, rect.y + dy


def _rasterize_child(
    *,
    child_index: int,
    role: str,
    text: str,
    rect: OriginalRect,
    raw_flags: int,
    style_wrapper_va: int,
    font,
) -> PrematchTextRasterChild:
    origin_x, origin_y = source_text_line_origin(font, text, rect, raw_flags)
    mask = font.render_text_alpha(text)
    glyph_rgba = endpoint_text_rgba(mask.alpha, TEXT_NATIVE_COLOR_16)
    if len(glyph_rgba) != mask.width * mask.height * 4:
        raise PrematchTextRasterError("source text glyph RGBA geometry mismatch")

    canvas = bytearray(rect.width * rect.height * 4)
    for y in range(mask.height):
        screen_y = origin_y + y
        local_y = screen_y - rect.y
        if not 0 <= local_y < rect.height:
            continue
        for x in range(mask.width):
            screen_x = origin_x + x
            local_x = screen_x - rect.x
            if not 0 <= local_x < rect.width:
                continue
            src = (y * mask.width + x) * 4
            if glyph_rgba[src + 3] == 0:
                continue
            dst = (local_y * rect.width + local_x) * 4
            canvas[dst:dst + 4] = glyph_rgba[src:src + 4]

    payload = bytes(canvas)
    return PrematchTextRasterChild(
        child_index=child_index,
        role=role,
        text=text,
        rect=rect,
        raw_flags=raw_flags,
        style_wrapper_va=style_wrapper_va,
        line_origin=(origin_x, origin_y),
        glyph_size=(mask.width, mask.height),
        rgba=payload,
        rgba_sha256=sha256(payload).hexdigest(),
    )


def build_prematch_text_rasters(
    boundary,
    *,
    dynamic_text: BoundPrematchDynamicText,
    player_rows,
    fonts: PrematchTextFontSet,
) -> PrematchTextRasterSet:
    """Raster every visible native PPreMatch text child for supplied state."""
    from gate14_prematch_surface import PrematchSurfaceBoundary, BoundPrematchPlayerRows

    if type(boundary) is not PrematchSurfaceBoundary:
        raise PrematchTextRasterError(
            "text rasterization requires exact PrematchSurfaceBoundary"
        )
    if type(dynamic_text) is not BoundPrematchDynamicText:
        raise PrematchTextRasterError(
            "text rasterization requires exact dynamic text binding"
        )
    if type(player_rows) is not BoundPrematchPlayerRows:
        raise PrematchTextRasterError(
            "text rasterization requires exact player-row binding"
        )
    if type(fonts) is not PrematchTextFontSet:
        raise PrematchTextRasterError(
            "text rasterization requires exact PrematchTextFontSet"
        )
    if dynamic_text.selection != boundary.selection:
        raise PrematchTextRasterError(
            "dynamic text selection differs from pre-match boundary"
        )
    if tuple(row.source for row in player_rows.rows) != boundary.player_text_rows:
        raise PrematchTextRasterError(
            "player text state is detached from pre-match boundary"
        )

    dynamic_by_role = {
        "fixture_header": dynamic_text.fixture_header,
        "date_weather": dynamic_text.date_weather,
        "team_identity_0": dynamic_text.home_team_identity,
        "versus": dynamic_text.versus,
        "team_identity_1": dynamic_text.away_team_identity,
    }
    direct_style = {
        "fixture_header": (PREMATCH_FIXTURE_HEADER_FLAGS, PREMATCH_HEADER_STYLE.wrapper_va),
        "date_weather": (PREMATCH_DATE_WEATHER_FLAGS, PREMATCH_HEADER_STYLE.wrapper_va),
        "team_identity_0": (PREMATCH_LEFT_TEAM_IDENTITY_FLAGS, PREMATCH_TEAM_STYLE.wrapper_va),
        "versus": (PREMATCH_VERSUS_FLAGS, PREMATCH_VERSUS_STYLE.wrapper_va),
        "team_identity_1": (PREMATCH_RIGHT_TEAM_IDENTITY_FLAGS, PREMATCH_TEAM_STYLE.wrapper_va),
    }

    visible = []
    for control in boundary.text_controls:
        child_index = PREMATCH_DIRECT_TEXT_CHILD_INDEX[control.role]
        text = dynamic_by_role.get(control.role, control.fixed_text)
        if not isinstance(text, str) or not text:
            raise PrematchTextRasterError(
                f"visible direct text is unavailable for {control.role}"
            )
        if control.role.startswith("rating_"):
            raw_flags = PREMATCH_RATING_CAPTION_FLAGS
            wrapper_va = PREMATCH_ROW_STYLE.wrapper_va
        else:
            raw_flags, wrapper_va = direct_style[control.role]
        visible.append(
            _rasterize_child(
                child_index=child_index,
                role=control.role,
                text=text,
                rect=control.rect,
                raw_flags=raw_flags,
                style_wrapper_va=wrapper_va,
                font=fonts.for_wrapper(wrapper_va),
            )
        )

    hidden = []
    for row in player_rows.rows:
        source = row.source
        if row.variant != "active":
            hidden.extend((source.number_child_index, source.name_child_index))
            continue
        name_flags = (
            PREMATCH_LEFT_PLAYER_NAME_FLAGS
            if source.side == "left"
            else PREMATCH_RIGHT_PLAYER_NAME_FLAGS
        )
        visible.append(
            _rasterize_child(
                child_index=source.number_child_index,
                role=f"{source.side}_player_{source.slot_index}_number",
                text=row.shirt_number_text,
                rect=source.number_rect,
                raw_flags=PREMATCH_PLAYER_NUMBER_FLAGS,
                style_wrapper_va=PREMATCH_ROW_STYLE.wrapper_va,
                font=fonts.row,
            )
        )
        visible.append(
            _rasterize_child(
                child_index=source.name_child_index,
                role=f"{source.side}_player_{source.slot_index}_name",
                text=row.display_name_text,
                rect=source.name_rect,
                raw_flags=name_flags,
                style_wrapper_va=PREMATCH_ROW_STYLE.wrapper_va,
                font=fonts.row,
            )
        )

    registered = tuple(
        sorted(
            tuple(PREMATCH_DIRECT_TEXT_CHILD_INDEX.values())
            + tuple(
                index
                for source in boundary.player_text_rows
                for index in (source.number_child_index, source.name_child_index)
            )
        )
    )
    return PrematchTextRasterSet(
        children=tuple(sorted(visible, key=lambda child: child.child_index)),
        registered_text_child_indices=registered,
        hidden_text_child_indices=tuple(sorted(hidden)),
    )


def prematch_text_raster_contract() -> dict:
    return {
        "direct_text_child_indices": PREMATCH_DIRECT_TEXT_CHILD_INDEX,
        "registered_text_child_count": 85,
        "native_color_16": TEXT_NATIVE_COLOR_16,
        "alignment_draw_va": 0x64F090,
        "control_clipping_preserved": True,
        "source_font_hashes_required": True,
        "text_pixels_rasterized_for_supplied_state": True,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
