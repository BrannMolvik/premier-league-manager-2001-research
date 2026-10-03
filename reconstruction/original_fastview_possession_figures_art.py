"""Exact source-backed text art for FM2001 FastView PossessionFigures.

The three percentage controls share source style index 1. Canonical executable
tracing maps that style through 0x527BA0 to wrapper 0x87BE90, whose initializer
binds font object 0x9197E0. The font loader uses the already provenance-staged
Fonts/Zurich_BdXCn_BT_18pixel.fnt. Generic text rendering uses native color
0xFFFF and flags 9, which resolve to left/top alignment.

This module renders only the three source-proven percentage strings and control
rectangles. It does not assign side 0/1 to the human user or synthesize the
surrounding FastView background.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from gate14_possession_figures import (
    SOURCE_TEXT_FONT_ATLAS_SIZE,
    SOURCE_TEXT_FONT_BYTE_SIZE,
    SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
    SOURCE_TEXT_FONT_PATH,
    SOURCE_TEXT_FONT_SHA256,
    SOURCE_TEXT_HORIZONTAL_ALIGNMENT,
    SOURCE_TEXT_NATIVE_COLOR_16,
    SOURCE_TEXT_RENDER_FLAGS,
    SOURCE_TEXT_VERTICAL_ALIGNMENT,
    PossessionFigureText,
    possession_figures_text_layout,
)
from original_live_debug_view import endpoint_text_rgba


class OriginalFastViewPossessionFiguresArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewPossessionFigureTextArt:
    source: PossessionFigureText
    line_origin: tuple[int, int]
    clip_rect: tuple[int, int, int, int]
    native_color_16: int
    glyph_width: int
    glyph_height: int
    glyph_rgba: bytes

    def __post_init__(self) -> None:
        if len(self.glyph_rgba) != self.glyph_width * self.glyph_height * 4:
            raise OriginalFastViewPossessionFiguresArtError(
                "PossessionFigures glyph RGBA geometry mismatch"
            )


@dataclass(frozen=True)
class OriginalFastViewPossessionFiguresArt:
    rows: tuple[
        OriginalFastViewPossessionFigureTextArt,
        OriginalFastViewPossessionFigureTextArt,
        OriginalFastViewPossessionFigureTextArt,
    ]
    horizontal_alignment: str = SOURCE_TEXT_HORIZONTAL_ALIGNMENT
    vertical_alignment: str = SOURCE_TEXT_VERTICAL_ALIGNMENT
    human_side_orientation_recovered: bool = False


def load_verified_possession_figures_font(repo_root: str | Path) -> EAFont:
    path = Path(repo_root) / "original_assets/source" / SOURCE_TEXT_FONT_PATH
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewPossessionFiguresArtError(
            f"Missing staged PossessionFigures font: {SOURCE_TEXT_FONT_PATH}"
        ) from exc
    if len(data) != SOURCE_TEXT_FONT_BYTE_SIZE:
        raise OriginalFastViewPossessionFiguresArtError(
            "PossessionFigures font byte-size mismatch"
        )
    if sha256(data).hexdigest() != SOURCE_TEXT_FONT_SHA256:
        raise OriginalFastViewPossessionFiguresArtError(
            "PossessionFigures font checksum mismatch"
        )
    font = EAFont.from_bytes(data)
    if (font.atlas_width, font.atlas_height) != SOURCE_TEXT_FONT_ATLAS_SIZE:
        raise OriginalFastViewPossessionFiguresArtError(
            "PossessionFigures font atlas geometry mismatch"
        )
    if font.native_line_height() != SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT:
        raise OriginalFastViewPossessionFiguresArtError(
            "PossessionFigures font line-height mismatch"
        )
    return font


def build_possession_figures_art(
    font: EAFont,
    side0_percent: int,
    neutral_percent: int,
) -> OriginalFastViewPossessionFiguresArt:
    if not isinstance(font, EAFont):
        raise OriginalFastViewPossessionFiguresArtError(
            "PossessionFigures requires a verified EAFont"
        )
    rows = []
    for source in possession_figures_text_layout(side0_percent, neutral_percent):
        mask = font.render_text_alpha(source.text)
        left, top, right, bottom = source.rect
        control_width = right - left
        control_height = bottom - top
        if mask.width > control_width or mask.height > control_height:
            raise OriginalFastViewPossessionFiguresArtError(
                f"Source percentage text exceeds recovered control: {source.text}"
            )
        rows.append(
            OriginalFastViewPossessionFigureTextArt(
                source=source,
                line_origin=(left, top),
                clip_rect=source.rect,
                native_color_16=SOURCE_TEXT_NATIVE_COLOR_16,
                glyph_width=mask.width,
                glyph_height=mask.height,
                glyph_rgba=endpoint_text_rgba(
                    mask.alpha,
                    SOURCE_TEXT_NATIVE_COLOR_16,
                ),
            )
        )
    return OriginalFastViewPossessionFiguresArt(tuple(rows))
