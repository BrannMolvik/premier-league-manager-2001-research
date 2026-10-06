"""Executable-bound PSquadPlayerRow text and color contract.

This module keeps the newly recovered ordinary Squad row styling separate from
viewport membership/filtering. The canonical executable proves the role/name
controls, the display-name formatter and the five player-name color branches.
Reserve-team selection flags are source-known but are not yet represented by
the clean-room gameplay model, so callers must supply those states explicitly
when they need them.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont


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

    def __post_init__(self) -> None:
        if (self.font.atlas_width, self.font.atlas_height) != SQUAD_ROW_FONT_ATLAS_SIZE:
            raise OriginalSquadRowStyleError("Squad row font atlas geometry drifted")


def load_verified_squad_row_text_resources(
    source_root: str | Path,
) -> OriginalSquadRowTextResources:
    root = Path(source_root)
    path = root / SQUAD_ROW_FONT_SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalSquadRowStyleError(
            f"Missing exact Squad row font: {SQUAD_ROW_FONT_SOURCE_PATH}"
        ) from exc
    if len(raw) != SQUAD_ROW_FONT_BYTE_SIZE:
        raise OriginalSquadRowStyleError("Squad row font byte-size mismatch")
    if sha256(raw).hexdigest() != SQUAD_ROW_FONT_SHA256:
        raise OriginalSquadRowStyleError("Squad row font checksum mismatch")
    return OriginalSquadRowTextResources(EAFont.from_bytes(raw))


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
