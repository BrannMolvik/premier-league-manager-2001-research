"""Source-qualified ordinary management text rasterization for Gate 13.

The final Gate-13 private receipt closes PLeagueTableRow's visible text path:

* canonical setup 0x446930 uses runtime font slot 0x947578;
* the canonical font-wrapper branch (0x6596A0 == 0) maps that slot to
  font object 0x9269F0;
* existing source work binds 0x9269F0 to
  Fonts/Zurich_BdXCn_BT_16pixel.fnt;
* club-name controls use raw flags 0x21 (left + vertical centre);
* rank/stat controls use raw flags 0x24 (horizontal + vertical centre);
* all visible row text uses native endpoint color 0xFFFF.

Only these source-closed League Tables row strings are rasterized here.  The
PLeagueTables header labels and colorized Squad side columns remain outside
this bounded layer rather than receiving guessed typography.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont, EATextMask
from original_league_tables_presenter import OriginalLeagueTablesSnapshot
from original_league_tables_resources import (
    LEAGUE_TABLES_LIST_RECT,
    LEAGUE_TABLES_LIST_ROW_STEP,
)


class OriginalManagementTextError(ValueError):
    """Ordinary management text left the source-qualified rendering contract."""


LEAGUE_TABLES_ROW_SETUP_VA = 0x446930
LEAGUE_TABLES_ROW_FONT_SLOT_VA = 0x947578
LEAGUE_TABLES_ROW_FONT_OBJECT_VA = 0x9269F0
LEAGUE_TABLES_ROW_FONT_SOURCE_PATH = "Fonts/Zurich_BdXCn_BT_16pixel.fnt"
LEAGUE_TABLES_ROW_FONT_SHA256 = (
    "9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732"
)
LEAGUE_TABLES_ROW_FONT_BYTE_SIZE = 79_722
LEAGUE_TABLES_ROW_FONT_ATLAS_SIZE = (1526, 17)
LEAGUE_TABLES_ROW_FONT_NATIVE_LINE_HEIGHT = 18

LEAGUE_TABLES_ROW_CLUB_FLAGS = 0x21
LEAGUE_TABLES_ROW_NUMERIC_FLAGS = 0x24
LEAGUE_TABLES_ROW_NATIVE_COLOR_16 = 0xFFFF


@dataclass(frozen=True)
class OriginalManagementTextResources:
    league_tables_row_font: EAFont

    def __post_init__(self) -> None:
        font = self.league_tables_row_font
        if (font.atlas_width, font.atlas_height) != LEAGUE_TABLES_ROW_FONT_ATLAS_SIZE:
            raise OriginalManagementTextError(
                "League Tables row font atlas geometry drifted"
            )
        if font.native_line_height() != LEAGUE_TABLES_ROW_FONT_NATIVE_LINE_HEIGHT:
            raise OriginalManagementTextError(
                "League Tables row font line height drifted"
            )


@dataclass(frozen=True)
class OriginalManagementTextOverlay:
    role: str
    text: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes
    control_rect: tuple[int, int, int, int]
    raw_flags: int
    native_color_16: int
    font_source_path: str

    def __post_init__(self) -> None:
        if not self.text:
            raise OriginalManagementTextError("Management text overlay must be non-empty")
        if self.role not in {"rank", "club", "stat"}:
            raise OriginalManagementTextError("Unknown management text overlay role")
        if self.width <= 0 or self.height <= 0:
            raise OriginalManagementTextError("Management text overlay has no pixels")
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalManagementTextError("Management text RGBA geometry mismatch")
        left, top, width, height = self.control_rect
        if not (
            left <= self.x < left + width
            and top <= self.y < top + height
            and self.x + self.width <= left + width
            and self.y + self.height <= top + height
        ):
            raise OriginalManagementTextError(
                "Management text overlay escaped its native control rectangle"
            )


def load_verified_management_text_resources(
    source_root: str | Path,
) -> OriginalManagementTextResources:
    root = Path(source_root)
    path = root / LEAGUE_TABLES_ROW_FONT_SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalManagementTextError(
            f"Missing exact League Tables row font: {LEAGUE_TABLES_ROW_FONT_SOURCE_PATH}"
        ) from exc
    if len(raw) != LEAGUE_TABLES_ROW_FONT_BYTE_SIZE:
        raise OriginalManagementTextError("League Tables row font byte-size mismatch")
    if sha256(raw).hexdigest() != LEAGUE_TABLES_ROW_FONT_SHA256:
        raise OriginalManagementTextError("League Tables row font checksum mismatch")
    return OriginalManagementTextResources(EAFont.from_bytes(raw))


def _trunc_half(value: int) -> int:
    return value // 2 if value >= 0 else -((-value) // 2)


def _line_origin(
    font: EAFont,
    text: str,
    rect: tuple[int, int, int, int],
    raw_flags: int,
) -> tuple[int, int]:
    left, top, width, height = rect
    if width <= 0 or height <= 0:
        raise OriginalManagementTextError("Text control rectangle must be positive")
    if raw_flags not in (
        LEAGUE_TABLES_ROW_CLUB_FLAGS,
        LEAGUE_TABLES_ROW_NUMERIC_FLAGS,
    ):
        raise OriginalManagementTextError("Unqualified management text flags")

    # Shared 0x6520C0 semantics already recovered elsewhere in the project:
    # bit 0x04 centers horizontally, bit 0x20 centers vertically, while 0x01
    # retains the left origin.  The line may begin above a 12px control because
    # the source font line height is 18px; glyphs are then clipped half-open.
    if raw_flags & 0x04:
        x = left + width // 2 - font.measure_text(text) // 2
    else:
        x = left

    if raw_flags & 0x20:
        y = top + height // 2 - font.native_line_height() // 2
    else:
        y = top
    return x, y


def _clip_mask(
    mask: EATextMask,
    line_origin: tuple[int, int],
    rect: tuple[int, int, int, int],
) -> tuple[int, int, int, int, bytes] | None:
    if mask.width <= 0 or mask.height <= 0:
        return None
    line_x, line_y = line_origin
    left, top, width, height = rect
    right = left + width
    bottom = top + height

    out_left = max(line_x, left)
    out_top = max(line_y, top)
    out_right = min(line_x + mask.width, right)
    out_bottom = min(line_y + mask.height, bottom)
    if out_left >= out_right or out_top >= out_bottom:
        return None

    out_width = out_right - out_left
    out_height = out_bottom - out_top
    src_x = out_left - line_x
    src_y = out_top - line_y
    alpha = bytearray(out_width * out_height)
    for row in range(out_height):
        src = (src_y + row) * mask.width + src_x
        dst = row * out_width
        alpha[dst:dst + out_width] = mask.alpha[src:src + out_width]
    return out_left, out_top, out_width, out_height, bytes(alpha)


def _white_rgba(alpha: bytes) -> bytes:
    rgba = bytearray(len(alpha) * 4)
    for index, value in enumerate(alpha):
        pos = index * 4
        rgba[pos:pos + 4] = bytes((255, 255, 255, value))
    return bytes(rgba)


def _overlay(
    font: EAFont,
    *,
    role: str,
    text: str,
    rect: tuple[int, int, int, int],
    raw_flags: int,
) -> OriginalManagementTextOverlay | None:
    mask = font.render_text_alpha(text)
    clipped = _clip_mask(mask, _line_origin(font, text, rect, raw_flags), rect)
    if clipped is None:
        return None
    x, y, width, height, alpha = clipped
    return OriginalManagementTextOverlay(
        role=role,
        text=text,
        x=x,
        y=y,
        width=width,
        height=height,
        rgba=_white_rgba(alpha),
        control_rect=rect,
        raw_flags=raw_flags,
        native_color_16=LEAGUE_TABLES_ROW_NATIVE_COLOR_16,
        font_source_path=LEAGUE_TABLES_ROW_FONT_SOURCE_PATH,
    )


def league_tables_row_text_overlays(
    snapshot: OriginalLeagueTablesSnapshot,
    resources: OriginalManagementTextResources,
) -> tuple[OriginalManagementTextOverlay, ...]:
    """Raster every source-backed visible PLeagueTableRow string.

    The presenter has already enforced source-default ordering, 24-row capacity
    and original points arithmetic.  This function adds only the exact native
    text geometry/style/font/color layer.
    """
    if not isinstance(snapshot, OriginalLeagueTablesSnapshot):
        raise OriginalManagementTextError(
            "League Tables text requires the exact table snapshot"
        )
    if not isinstance(resources, OriginalManagementTextResources):
        raise OriginalManagementTextError(
            "League Tables text requires verified source font resources"
        )
    if snapshot.list_rect != LEAGUE_TABLES_LIST_RECT:
        raise OriginalManagementTextError("League Tables list rectangle drifted")
    if snapshot.row_step != LEAGUE_TABLES_LIST_ROW_STEP:
        raise OriginalManagementTextError("League Tables row step drifted")

    font = resources.league_tables_row_font
    list_x, list_y, _list_width, _list_height = snapshot.list_rect
    overlays: list[OriginalManagementTextOverlay] = []

    def absolute_rect(
        local: tuple[int, int, int, int],
        row_index: int,
    ) -> tuple[int, int, int, int]:
        x, y, width, height = local
        return (
            list_x + x,
            list_y + row_index * snapshot.row_step + y,
            width,
            height,
        )

    for row_index, row in enumerate(snapshot.rows):
        if row.source_index != row_index:
            raise OriginalManagementTextError(
                "League Tables source row order drifted from presenter snapshot"
            )
        entries = (
            ("rank", str(row.position), row.rank_rect, LEAGUE_TABLES_ROW_NUMERIC_FLAGS),
            ("club", row.club_name, row.club_rect, LEAGUE_TABLES_ROW_CLUB_FLAGS),
            *(
                ("stat", str(value), rect, LEAGUE_TABLES_ROW_NUMERIC_FLAGS)
                for value, rect in zip(row.values, row.stat_rects)
            ),
        )
        for role, text, local_rect, flags in entries:
            item = _overlay(
                font,
                role=role,
                text=text,
                rect=absolute_rect(local_rect, row_index),
                raw_flags=flags,
            )
            if item is not None:
                overlays.append(item)

    return tuple(overlays)
