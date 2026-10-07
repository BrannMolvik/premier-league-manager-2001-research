"""Source-closed PPreMatch starting-XI shirt selection.

This module preserves the native division between:
* 0x5EF940 kit-clash/context selection;
* 0x408320 custom-shirt ownership with dynamic generic-BMP fallback; and
* 0x41E3F0 -> 0x41E3D0 per-player numbered-frame selection.

It deliberately does not approximate 0x5E4C60's generic BMP recolor pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_management_background import native_art_component


class PrematchShirtSelectionError(ValueError):
    pass


PREMATCH_KIT_CONTEXT_SELECTOR_VA = 0x5EF940
PREMATCH_KIT_CLASH_SELECTOR_VA = 0x5EF9E0
PREMATCH_KIT_CLASH_TABLE_VA = 0x834AF8
PREMATCH_KIT_CLASH_COLOR_COUNT = 23
PREMATCH_KIT_CLASH_ROW_BYTES = 6
PREMATCH_KIT_CLASH_SENTINEL = 23

PREMATCH_TEAM_SHIRT_BUILDER_VA = 0x408320
PREMATCH_GENERIC_RECOLOR_VA = 0x5E4C60
PREMATCH_CLUB_GRAPHICS_BASENAME_GETTER_VA = 0x40DA90

PREMATCH_CUSTOM_SHIRT_ROOT = r"fm2001_art\Generic\front-end-shirts\custom"
PREMATCH_GENERIC_SHIRT_ROOT = r"fm2001_art\Generic\front-end-shirts\generic"
PREMATCH_GENERIC_SHIRT_FORMAT = "Team%.2d.bmp"
PREMATCH_GENERIC_TEMPLATE_MIN = 0
PREMATCH_GENERIC_TEMPLATE_MAX = 36

PREMATCH_PLAYER_SHIRT_SELECTOR_VA = 0x41E3F0
PREMATCH_PLAYER_SHIRT_NUMBER_SELECTOR_VA = 0x41E3D0
PREMATCH_PLAYER_REGISTERED_CLUB_OFFSET = 0x10
PREMATCH_PLAYER_PRIMARY_SHIRT_NUMBER_OFFSET = 0x70
PREMATCH_PLAYER_ALTERNATE_SHIRT_NUMBER_OFFSET = 0x76
PREMATCH_TEAM_OBJECT_CLUB_ID_OFFSET = 0x04
PREMATCH_SHIRT_FRAME_HEIGHT = 32
PREMATCH_SHIRT_FRAME_WIDTH = 36


@dataclass(frozen=True)
class PrematchClubShirtState:
    club_id: int
    graphics_basename: str
    primary_template_index: int
    alternate_template_index: int
    primary_color_id: int
    primary_secondary_color_id: int
    alternate_color_id: int
    alternate_secondary_color_id: int

    def __post_init__(self) -> None:
        if type(self.club_id) is not int or self.club_id < 0:
            raise PrematchShirtSelectionError("club_id must be a non-negative integer")
        if not isinstance(self.graphics_basename, str) or not self.graphics_basename:
            raise PrematchShirtSelectionError("graphics_basename must be non-empty")
        for name, value in (
            ("primary_template_index", self.primary_template_index),
            ("alternate_template_index", self.alternate_template_index),
            ("primary_color_id", self.primary_color_id),
            ("primary_secondary_color_id", self.primary_secondary_color_id),
            ("alternate_color_id", self.alternate_color_id),
            ("alternate_secondary_color_id", self.alternate_secondary_color_id),
        ):
            if type(value) is not int or not 0 <= value <= 255:
                raise PrematchShirtSelectionError(f"{name} must preserve one source byte")


@dataclass(frozen=True)
class PrematchSideKitContext:
    use_alternate: bool
    selected_template_index: int
    custom_source_path: str | None
    generic_template_index: int
    generic_source_path: str

    def __post_init__(self) -> None:
        if type(self.use_alternate) is not bool:
            raise PrematchShirtSelectionError("use_alternate must be exact bool")
        if type(self.selected_template_index) is not int:
            raise PrematchShirtSelectionError("selected_template_index must be integer")
        if not 0 <= self.generic_template_index <= PREMATCH_GENERIC_TEMPLATE_MAX:
            raise PrematchShirtSelectionError("generic template index is outside native clamp")
        if not self.generic_source_path:
            raise PrematchShirtSelectionError("generic source path must be retained")
        if self.use_alternate and self.custom_source_path is not None:
            raise PrematchShirtSelectionError(
                "0x408320 does not attempt club custom art for alternate kit context"
            )


@dataclass(frozen=True)
class PrematchTeamKitSelection:
    home: PrematchSideKitContext
    away: PrematchSideKitContext
    source_context_closed: bool = True
    generic_pixels_recovered: bool = False

    def __post_init__(self) -> None:
        if not self.source_context_closed or self.generic_pixels_recovered:
            raise PrematchShirtSelectionError(
                "selection contract cannot promote unresolved generic recolor pixels"
            )


def club_shirt_state(club) -> PrematchClubShirtState:
    try:
        return PrematchClubShirtState(
            club_id=club.index,
            graphics_basename=club.graphics_basename,
            primary_template_index=club.primary_shirt_template_index,
            alternate_template_index=club.alternate_shirt_template_index,
            primary_color_id=club.primary_kit_color_id,
            primary_secondary_color_id=club.primary_kit_secondary_color_id,
            alternate_color_id=club.alternate_kit_color_id,
            alternate_secondary_color_id=club.alternate_kit_secondary_color_id,
        )
    except AttributeError as exc:
        raise PrematchShirtSelectionError(
            "club lacks source-backed PPreMatch shirt selector fields"
        ) from exc


def _clashes(first: int, second: int, clash_table: bytes) -> bool:
    if not isinstance(clash_table, bytes):
        raise PrematchShirtSelectionError("clash table must be exact bytes")
    expected = PREMATCH_KIT_CLASH_COLOR_COUNT * PREMATCH_KIT_CLASH_ROW_BYTES
    if len(clash_table) != expected:
        raise PrematchShirtSelectionError(
            f"clash table must contain exactly {expected} source bytes"
        )
    if not 0 <= first < PREMATCH_KIT_CLASH_COLOR_COUNT:
        raise PrematchShirtSelectionError("first kit color is outside native table")
    if not 0 <= second < PREMATCH_KIT_CLASH_COLOR_COUNT:
        raise PrematchShirtSelectionError("second kit color is outside native table")
    if first == second:
        return True
    for left, right in ((first, second), (second, first)):
        row = clash_table[
            left * PREMATCH_KIT_CLASH_ROW_BYTES:
            (left + 1) * PREMATCH_KIT_CLASH_ROW_BYTES
        ]
        for value in row:
            if value == PREMATCH_KIT_CLASH_SENTINEL:
                break
            if value == right:
                return True
    return False


def _side_context(club: PrematchClubShirtState, use_alternate: bool) -> PrematchSideKitContext:
    selected_template = (
        club.alternate_template_index if use_alternate else club.primary_template_index
    )
    # 0x408320 only attempts the club-specific custom atlas when its third
    # argument is zero. On alternate context, or after a failed custom load,
    # its generic branch reads DBRClub+0x47 directly and clamps to 0..36.
    custom_path = None
    if not use_alternate:
        custom_path = (
            f"{PREMATCH_CUSTOM_SHIRT_ROOT}\\"
            f"{native_art_component(club.graphics_basename)}.444"
        )
    generic_index = min(
        max(int(club.alternate_template_index), PREMATCH_GENERIC_TEMPLATE_MIN),
        PREMATCH_GENERIC_TEMPLATE_MAX,
    )
    generic_path = (
        f"{PREMATCH_GENERIC_SHIRT_ROOT}\\"
        f"{PREMATCH_GENERIC_SHIRT_FORMAT % generic_index}"
    )
    return PrematchSideKitContext(
        use_alternate=use_alternate,
        selected_template_index=selected_template,
        custom_source_path=custom_path,
        generic_template_index=generic_index,
        generic_source_path=generic_path,
    )


def select_prematch_team_kits(
    home: PrematchClubShirtState,
    away: PrematchClubShirtState,
    *,
    clash_table: bytes,
) -> PrematchTeamKitSelection:
    """Mirror 0x5EF940's exact primary/alternate decision tree."""
    if type(home) is not PrematchClubShirtState or type(away) is not PrematchClubShirtState:
        raise PrematchShirtSelectionError(
            "team kit selector requires exact PrematchClubShirtState values"
        )

    home_alt = False
    away_alt = False
    if _clashes(home.primary_color_id, away.primary_color_id, clash_table):
        if home.primary_color_id != away.alternate_color_id:
            away_alt = True
        elif home.alternate_color_id != away.primary_color_id:
            home_alt = True
        elif home.alternate_color_id != away.alternate_color_id:
            home_alt = True
            away_alt = True

    return PrematchTeamKitSelection(
        home=_side_context(home, home_alt),
        away=_side_context(away, away_alt),
    )


def prematch_player_shirt_frame_offset(
    *,
    player_registered_club_id: int,
    team_club_id: int,
    primary_shirt_number: int,
    alternate_shirt_number: int,
) -> int:
    """Mirror 0x41E3F0 -> 0x41E3D0 and PPreMatch's 32-pixel frame transform."""
    for name, value in (
        ("player_registered_club_id", player_registered_club_id),
        ("team_club_id", team_club_id),
        ("primary_shirt_number", primary_shirt_number),
        ("alternate_shirt_number", alternate_shirt_number),
    ):
        if type(value) is not int:
            raise PrematchShirtSelectionError(f"{name} must be integer")
    selected = (
        primary_shirt_number
        if player_registered_club_id == team_club_id
        else alternate_shirt_number
    )
    selected &= 0xFF
    return (selected << 5) - PREMATCH_SHIRT_FRAME_HEIGHT


def prematch_shirt_selection_contract() -> dict:
    return {
        "kit_context_selector_va": PREMATCH_KIT_CONTEXT_SELECTOR_VA,
        "kit_clash_selector_va": PREMATCH_KIT_CLASH_SELECTOR_VA,
        "kit_clash_table_va": PREMATCH_KIT_CLASH_TABLE_VA,
        "team_shirt_builder_va": PREMATCH_TEAM_SHIRT_BUILDER_VA,
        "generic_recolor_va": PREMATCH_GENERIC_RECOLOR_VA,
        "player_shirt_selector_va": PREMATCH_PLAYER_SHIRT_SELECTOR_VA,
        "player_shirt_number_selector_va": PREMATCH_PLAYER_SHIRT_NUMBER_SELECTOR_VA,
        "custom_primary_attempt_source_closed": True,
        "alternate_skips_custom_source_closed": True,
        "generic_template_fallback_source_closed": True,
        "generic_recolor_pixels_recovered": False,
        "player_frame_offset_source_closed": True,
        "marker_size": (PREMATCH_SHIRT_FRAME_WIDTH, PREMATCH_SHIRT_FRAME_HEIGHT),
        "complete_marker_pixels_recovered": False,
        "gate14_complete": False,
    }
