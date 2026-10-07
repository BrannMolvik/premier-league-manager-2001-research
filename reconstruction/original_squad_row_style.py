"""Executable-bound PSquadPlayerRow / PSCFRow text and color contract.

This module keeps recovered ordinary Squad row styling separate from viewport
membership/filtering. The canonical executable proves the player role/name
controls plus the paired PSCFRow Condition, recent-form and current-role-rating
numeric controls. Runtime callers retain the independent reserve-selection
flags initialized by the original constructor. Bounded/legacy adapters lacking
those states still withhold an unproven color rather than inventing one.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import ceil, floor, isfinite
from pathlib import Path

from ea_font import EAFont, EATextMask
from original_squad_resources import SQUAD_FIRST_ROSTER_RECT, SQUAD_PANEL_RECT


class OriginalSquadRowStyleError(ValueError):
    """The native Squad row text/style contract cannot be applied safely."""


PSQUAD_PLAYER_ROW_SETUP_VA = 0x489530
SQUAD_ROLE_PREFERRED_PREDICATE_VA = 0x4EA3F0
SQUAD_ROLE_CODE_HELPER_VA = 0x4EA3C0
SQUAD_DISPLAY_NAME_HELPER_VA = 0x5D6C50
SQUAD_DISPLAY_STRING_HELPER_VA = 0x5D7080
SQUAD_DISPLAY_STRING_FORMATTER_VA = 0x417AE0

SQUAD_ROW_FONT_SLOT_VA = 0x94758C
SQUAD_ROW_FONT_WRAPPER_VA = 0x87BE90
SQUAD_ROW_FONT_BASE_OBJECT_VA = 0x9197E0
SQUAD_ROW_FONT_SOURCE_PATH = "Fonts/Zurich_BdXCn_BT_18pixel.fnt"
SQUAD_ROW_FONT_SHA256 = (
    "4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd"
)
SQUAD_ROW_FONT_BYTE_SIZE = 83_174
SQUAD_ROW_FONT_ATLAS_SIZE = (1633, 18)

PSCF_ROW_SETUP_VA = 0x489B40
SQUAD_NUMERIC_CONTROL_HELPER_VA = 0x652400
SQUAD_NUMERIC_FORMATTER_VA = 0x655F40
SQUAD_CONDITION_THRESHOLD_VA = 0x821814
SQUAD_CONDITION_THRESHOLD = 75
SQUAD_SCF_LIST_LOCAL_X = 239
SQUAD_SCF_FONT_OBJECT_VA = 0x8CAB80
SQUAD_SCF_FONT_SOURCE_PATH = "Fonts/Zurich_XCn_BT_18pixel.fnt"
SQUAD_SCF_FONT_SHA256 = (
    "968936a5f5e42c4dd321f0a1096a8668c8f9ca3bd0b86243b585190969c1b71a"
)
SQUAD_SCF_FONT_BYTE_SIZE = 79_734
SQUAD_SCF_FONT_ATLAS_SIZE = (1366, 19)
SQUAD_SCF_TEXT_FLAGS = 0x24
SQUAD_CONDITION_RECT = (24, 1, 19, 14)
SQUAD_RECENT_FORM_RECT = (47, 1, 19, 14)
SQUAD_CURRENT_ROLE_RATING_RECT = (70, 1, 19, 14)
SQUAD_CONDITION_HIGH_RGB = (255, 255, 255)
SQUAD_CONDITION_LOW_RGB = (0, 45, 255)
SQUAD_SCF_NUMERIC_RGB = (255, 255, 255)

SQUAD_ROLE_RECT = (28, 1, 38, 14)
SQUAD_ROLE_TEXT_FLAGS = 0x24
SQUAD_NAME_RECT = (76, 1, 144, 14)
SQUAD_NAME_TEXT_FLAGS = 0x21

SQUAD_FIRST_TEAM_ACTIVE_PREDICATE_VA = 0x417EE0
SQUAD_FIRST_TEAM_SUBSTITUTE_PREDICATE_VA = 0x417F00
SQUAD_RESERVE_ACTIVE_PREDICATE_VA = 0x417EA0
SQUAD_RESERVE_SUBSTITUTE_PREDICATE_VA = 0x417EC0
SQUAD_FIRST_TEAM_FLAGS_OFFSET = 0x14
SQUAD_FIRST_TEAM_ACTIVE_MASK = 0x10
SQUAD_FIRST_TEAM_SUBSTITUTE_MASK = 0x20
SQUAD_RESERVE_FLAGS_OFFSET = 0x174
SQUAD_RESERVE_ACTIVE_MASK = 0x01
SQUAD_RESERVE_SUBSTITUTE_MASK = 0x02

SQUAD_ROLE_PREFERRED_RGB = (255, 255, 255)
SQUAD_ROLE_OUT_OF_POSITION_RGB = (0, 0, 125)
SQUAD_NAME_FIRST_TEAM_ACTIVE_RGB = (255, 255, 255)
SQUAD_NAME_FIRST_TEAM_SUBSTITUTE_RGB = (232, 191, 94)
SQUAD_NAME_RESERVE_ACTIVE_RGB = (176, 176, 176)
SQUAD_NAME_RESERVE_SUBSTITUTE_RGB = (185, 167, 131)
SQUAD_NAME_DEFAULT_RGB = (217, 210, 62)


@dataclass(frozen=True)
class OriginalSquadRowTextResources:
    font: EAFont
    scf_font: EAFont

    def __post_init__(self) -> None:
        if (self.font.atlas_width, self.font.atlas_height) != SQUAD_ROW_FONT_ATLAS_SIZE:
            raise OriginalSquadRowStyleError("Squad row font atlas geometry drifted")
        if (
            self.scf_font.atlas_width,
            self.scf_font.atlas_height,
        ) != SQUAD_SCF_FONT_ATLAS_SIZE:
            raise OriginalSquadRowStyleError("Squad PSCF font atlas geometry drifted")


def _load_verified_font(
    root: Path,
    *,
    source_path: str,
    expected_size: int,
    expected_sha256: str,
    label: str,
) -> EAFont:
    path = root / source_path
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalSquadRowStyleError(
            f"Missing exact {label} font: {source_path}"
        ) from exc
    if len(raw) != expected_size:
        raise OriginalSquadRowStyleError(f"{label} font byte-size mismatch")
    if sha256(raw).hexdigest() != expected_sha256:
        raise OriginalSquadRowStyleError(f"{label} font checksum mismatch")
    return EAFont.from_bytes(raw)


def load_verified_squad_row_text_resources(
    source_root: str | Path,
) -> OriginalSquadRowTextResources:
    root = Path(source_root)
    return OriginalSquadRowTextResources(
        _load_verified_font(
            root,
            source_path=SQUAD_ROW_FONT_SOURCE_PATH,
            expected_size=SQUAD_ROW_FONT_BYTE_SIZE,
            expected_sha256=SQUAD_ROW_FONT_SHA256,
            label="Squad row",
        ),
        _load_verified_font(
            root,
            source_path=SQUAD_SCF_FONT_SOURCE_PATH,
            expected_size=SQUAD_SCF_FONT_BYTE_SIZE,
            expected_sha256=SQUAD_SCF_FONT_SHA256,
            label="Squad PSCF",
        ),
    )


def format_squad_display_name(first_name: str, surname: str) -> str:
    """Apply native style-0 0x417AE0: %c. %s or surname-only sentinel."""
    if not isinstance(first_name, str) or not isinstance(surname, str):
        raise OriginalSquadRowStyleError("Squad source names must be strings")
    if not first_name:
        raise OriginalSquadRowStyleError("Squad source first name must be non-empty")
    if not surname:
        raise OriginalSquadRowStyleError("Squad source surname must be non-empty")
    if first_name.startswith("-"):
        return surname
    return f"{first_name[0]}. {surname}"


def format_squad_whole_number(value: int) -> str:
    """Apply PSCFRow's native %N whole-number presentation."""
    if type(value) is not int:
        raise OriginalSquadRowStyleError("Squad whole-number value must be an integer")
    return str(value)


def format_squad_recent_form(value: int | float) -> str:
    """Apply PSCFRow's native %.N one-decimal rounding contract.

    The canonical formatter's '.' modifier selects 0x655EE0, which multiplies
    by 10, rounds half away from zero, then multiplies by 0.1 before formatting.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise OriginalSquadRowStyleError("Squad recent-form value must be numeric")
    source = float(value)
    if not isfinite(source):
        raise OriginalSquadRowStyleError("Squad recent-form value must be finite")
    scaled = source * 10.0
    rounded = floor(scaled + 0.5) if scaled >= 0.0 else ceil(scaled - 0.5)
    return f"{rounded / 10.0:.1f}"


def squad_condition_rgb(condition: int) -> tuple[int, int, int]:
    """Apply PSCFRow's strict DBRPlayer+0x77 > 75 color branch."""
    if type(condition) is not int:
        raise OriginalSquadRowStyleError("Squad condition must be an integer")
    return (
        SQUAD_CONDITION_HIGH_RGB
        if condition > SQUAD_CONDITION_THRESHOLD
        else SQUAD_CONDITION_LOW_RGB
    )


def squad_role_is_preferred(
    assigned_role: int,
    preferred_roles: tuple[int, int, int],
) -> bool:
    """Apply 0x4EA3C0/0x4EA3F0 without adding semantic role aliases."""
    if type(assigned_role) is not int:
        raise OriginalSquadRowStyleError("Squad assigned role must be an integer")
    if (
        not isinstance(preferred_roles, tuple)
        or len(preferred_roles) != 3
        or any(type(value) is not int or not 0 <= value <= 0xFF for value in preferred_roles)
    ):
        raise OriginalSquadRowStyleError(
            "Squad preferred roles must be three source bytes"
        )
    selected_code = assigned_role & 0x1F
    return selected_code in preferred_roles


def squad_role_rgb(
    assigned_role: int,
    preferred_roles: tuple[int, int, int],
) -> tuple[int, int, int]:
    return (
        SQUAD_ROLE_PREFERRED_RGB
        if squad_role_is_preferred(assigned_role, preferred_roles)
        else SQUAD_ROLE_OUT_OF_POSITION_RGB
    )


def squad_name_rgb(
    *,
    first_team_active: bool,
    first_team_substitute: bool,
    reserve_active: bool,
    reserve_substitute: bool,
) -> tuple[int, int, int]:
    """Apply the exact 0x5D6C50 predicate precedence to source RGB inputs."""
    states = (
        first_team_active,
        first_team_substitute,
        reserve_active,
        reserve_substitute,
    )
    if any(type(value) is not bool for value in states):
        raise OriginalSquadRowStyleError(
            "Squad selection color states must be booleans"
        )
    if first_team_active:
        return SQUAD_NAME_FIRST_TEAM_ACTIVE_RGB
    if first_team_substitute:
        return SQUAD_NAME_FIRST_TEAM_SUBSTITUTE_RGB
    if reserve_active:
        return SQUAD_NAME_RESERVE_ACTIVE_RGB
    if reserve_substitute:
        return SQUAD_NAME_RESERVE_SUBSTITUTE_RGB
    return SQUAD_NAME_DEFAULT_RGB


def squad_name_rgb_from_available_state(
    *,
    first_team_active: bool,
    first_team_substitute: bool,
    reserve_active: bool | None = None,
    reserve_substitute: bool | None = None,
) -> tuple[int, int, int] | None:
    """Resolve color only when the available source state proves a branch.

    0x5D6C50 checks the first-team predicates before the reserve-team pair.
    Therefore first-team active/substitute can be resolved without reserve
    state. If neither first-team branch applies, unknown reserve flags must not
    be treated as false because that would fabricate the default yellow branch.
    """
    if type(first_team_active) is not bool or type(first_team_substitute) is not bool:
        raise OriginalSquadRowStyleError(
            "Squad first-team selection color states must be booleans"
        )
    if first_team_active:
        return SQUAD_NAME_FIRST_TEAM_ACTIVE_RGB
    if first_team_substitute:
        return SQUAD_NAME_FIRST_TEAM_SUBSTITUTE_RGB
    if reserve_active is None or reserve_substitute is None:
        return None
    return squad_name_rgb(
        first_team_active=False,
        first_team_substitute=False,
        reserve_active=reserve_active,
        reserve_substitute=reserve_substitute,
    )


@dataclass(frozen=True)
class OriginalSquadRowTextOverlay:
    text: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes
    source_rgb: tuple[int, int, int]
    font_source_path: str = SQUAD_ROW_FONT_SOURCE_PATH

    def __post_init__(self) -> None:
        if not self.text:
            raise OriginalSquadRowStyleError("Squad row overlay text must be non-empty")
        if self.width <= 0 or self.height <= 0:
            raise OriginalSquadRowStyleError("Squad row overlay has no pixels")
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalSquadRowStyleError("Squad row overlay RGBA geometry mismatch")


def _clip_mask(
    mask: EATextMask,
    *,
    line_x: int,
    line_y: int,
    rect: tuple[int, int, int, int],
) -> tuple[int, int, int, int, bytes] | None:
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


def _rgb_rgba(alpha: bytes, rgb: tuple[int, int, int]) -> bytes:
    if (
        not isinstance(rgb, tuple)
        or len(rgb) != 3
        or any(type(value) is not int or not 0 <= value <= 255 for value in rgb)
    ):
        raise OriginalSquadRowStyleError("Squad source RGB must be three bytes")
    rgba = bytearray(len(alpha) * 4)
    red, green, blue = rgb
    for index, value in enumerate(alpha):
        pos = index * 4
        rgba[pos:pos + 4] = bytes((red, green, blue, value))
    return bytes(rgba)


def build_first_roster_role_overlays(
    rows,
    resources: OriginalSquadRowTextResources,
) -> tuple[OriginalSquadRowTextOverlay, ...]:
    """Raster the source-closed assigned-role abbreviation controls."""
    if not isinstance(resources, OriginalSquadRowTextResources):
        raise OriginalSquadRowStyleError(
            "Squad row rendering requires verified source font resources"
        )
    panel_x, panel_y, _panel_width, _panel_height = SQUAD_PANEL_RECT
    roster = SQUAD_FIRST_ROSTER_RECT
    role_x, role_y, role_width, role_height = SQUAD_ROLE_RECT
    font = resources.font
    overlays: list[OriginalSquadRowTextOverlay] = []

    for row in tuple(rows):
        row_y = getattr(row, "y", None)
        text = getattr(row, "assigned_role_abbreviation", None)
        rgb = getattr(row, "assigned_role_rgb", None)
        if type(row_y) is not int:
            raise OriginalSquadRowStyleError("Squad row y must be an integer")
        if not isinstance(text, str) or not text:
            raise OriginalSquadRowStyleError(
                "Squad assigned-role abbreviation must be source-resolved"
            )
        rect = (
            panel_x + roster.x + role_x,
            panel_y + roster.y + row_y + role_y,
            role_width,
            role_height,
        )
        mask = font.render_text_alpha(text)
        # Native raw flags 0x24 center both horizontally and vertically.
        line_x = rect[0] + rect[2] // 2 - font.measure_text(text) // 2
        line_y = rect[1] + rect[3] // 2 - font.native_line_height() // 2
        clipped = _clip_mask(mask, line_x=line_x, line_y=line_y, rect=rect)
        if clipped is None:
            continue
        x, y, width, height, alpha = clipped
        overlays.append(
            OriginalSquadRowTextOverlay(
                text=text,
                x=x,
                y=y,
                width=width,
                height=height,
                rgba=_rgb_rgba(alpha, rgb),
                source_rgb=rgb,
            )
        )
    return tuple(overlays)


def build_first_roster_name_overlays(
    rows,
    resources: OriginalSquadRowTextResources,
) -> tuple[OriginalSquadRowTextOverlay, ...]:
    """Raster the source-closed populated name controls for the first roster.

    PSquadScreen control 3 exposes the first roster at +0x130. The clean-room
    presenter currently supplies only that source-order viewport; reserve-list
    membership remains outside this function.
    """
    if not isinstance(resources, OriginalSquadRowTextResources):
        raise OriginalSquadRowStyleError(
            "Squad row rendering requires verified source font resources"
        )
    panel_x, panel_y, _panel_width, _panel_height = SQUAD_PANEL_RECT
    roster = SQUAD_FIRST_ROSTER_RECT
    name_x, name_y, name_width, name_height = SQUAD_NAME_RECT
    font = resources.font
    overlays: list[OriginalSquadRowTextOverlay] = []

    for row in tuple(rows):
        row_y = getattr(row, "y", None)
        text = getattr(row, "display_name", None)
        rgb = getattr(row, "display_name_rgb", None)
        if type(row_y) is not int:
            raise OriginalSquadRowStyleError("Squad row y must be an integer")
        if not isinstance(text, str) or not text:
            raise OriginalSquadRowStyleError(
                "Squad row display name must be source-resolved"
            )
        if rgb is None:
            # Legacy/bounded adapters may lack retained reserve-selection
            # flags. Do not render a guessed default/reserve color.
            continue
        rect = (
            panel_x + roster.x + name_x,
            panel_y + roster.y + row_y + name_y,
            name_width,
            name_height,
        )
        mask = font.render_text_alpha(text)
        # Native raw flags 0x21 mean left-aligned + vertically centered.
        line_x = rect[0]
        line_y = rect[1] + rect[3] // 2 - font.native_line_height() // 2
        clipped = _clip_mask(mask, line_x=line_x, line_y=line_y, rect=rect)
        if clipped is None:
            continue
        x, y, width, height, alpha = clipped
        overlays.append(
            OriginalSquadRowTextOverlay(
                text=text,
                x=x,
                y=y,
                width=width,
                height=height,
                rgba=_rgb_rgba(alpha, rgb),
                source_rgb=rgb,
            )
        )
    return tuple(overlays)

def build_first_roster_scf_numeric_overlays(
    rows,
    resources: OriginalSquadRowTextResources,
) -> tuple[OriginalSquadRowTextOverlay, ...]:
    """Raster the source-closed PSCFRow numeric controls for the first roster."""
    if not isinstance(resources, OriginalSquadRowTextResources):
        raise OriginalSquadRowStyleError(
            "Squad row rendering requires verified source font resources"
        )
    panel_x, panel_y, _panel_width, _panel_height = SQUAD_PANEL_RECT
    roster = SQUAD_FIRST_ROSTER_RECT
    font = resources.scf_font
    overlays: list[OriginalSquadRowTextOverlay] = []

    for row in tuple(rows):
        row_y = getattr(row, "y", None)
        if type(row_y) is not int:
            raise OriginalSquadRowStyleError("Squad row y must be an integer")

        condition = getattr(row, "condition", None)
        recent_form = getattr(row, "recent_form_average", None)
        current_role_rating = getattr(row, "current_role_rating", None)
        if type(condition) is not int:
            raise OriginalSquadRowStyleError("Squad condition must be an integer")
        if type(current_role_rating) is not int:
            raise OriginalSquadRowStyleError(
                "Squad current-role rating must be an integer"
            )

        fields = (
            (
                format_squad_whole_number(condition),
                SQUAD_CONDITION_RECT,
                squad_condition_rgb(condition),
            ),
            (
                format_squad_recent_form(recent_form),
                SQUAD_RECENT_FORM_RECT,
                SQUAD_SCF_NUMERIC_RGB,
            ),
            (
                format_squad_whole_number(current_role_rating),
                SQUAD_CURRENT_ROLE_RATING_RECT,
                SQUAD_SCF_NUMERIC_RGB,
            ),
        )
        for text, control_rect, rgb in fields:
            local_x, local_y, width, height = control_rect
            rect = (
                panel_x + roster.x + SQUAD_SCF_LIST_LOCAL_X + local_x,
                panel_y + roster.y + row_y + local_y,
                width,
                height,
            )
            mask = font.render_text_alpha(text)
            # Native raw flags 0x24 center both horizontally and vertically.
            line_x = rect[0] + rect[2] // 2 - font.measure_text(text) // 2
            line_y = rect[1] + rect[3] // 2 - font.native_line_height() // 2
            clipped = _clip_mask(mask, line_x=line_x, line_y=line_y, rect=rect)
            if clipped is None:
                continue
            x, y, out_width, out_height, alpha = clipped
            overlays.append(
                OriginalSquadRowTextOverlay(
                    text=text,
                    x=x,
                    y=y,
                    width=out_width,
                    height=out_height,
                    rgba=_rgb_rgba(alpha, rgb),
                    source_rgb=rgb,
                    font_source_path=SQUAD_SCF_FONT_SOURCE_PATH,
                )
            )
    return tuple(overlays)

