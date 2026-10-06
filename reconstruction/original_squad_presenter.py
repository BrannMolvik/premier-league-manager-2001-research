"""Source-bounded read-only presenter for FM2001 PSquadList rows.

This module consumes immutable SquadRowView-style objects and exposes only the
row geometry/fields recovered from PSquadPlayerRow and PSCFRow. It deliberately
does not choose first-team versus reserve membership, resolve the club-relative
assignment selector, name the native status icon categories, or invent scrolling.

Recovery 330 additionally source-closes PSquadPlayerRow's visible name formatter,
name-status colors, and assigned-role compatibility color. Font rasterization is
still kept outside this presenter until the exact runtime font object behind
slot 0x94758C is independently bound to an original font resource.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from original_squad_resources import (
    SQUAD_PLAYER_COLUMNS,
    SQUAD_SCF_COLUMNS,
    SQUAD_VISIBLE_ROW_COUNT,
    SQUAD_VISIBLE_ROW_Y_ORIGINS,
)


class OriginalSquadPresentationError(ValueError):
    """The recovered Squad row contract cannot be projected safely."""


# Canonical PSquadPlayerRow helper boundaries.
PSQUAD_ROLE_PREFERRED_PREDICATE_VA = 0x4EA3F0
PSQUAD_PLAYER_ROLE_READER_VA = 0x4EA3C0
PSQUAD_NAME_CONTROL_SETUP_VA = 0x5D6C50
PSQUAD_NAME_CONTROL_REFRESH_VA = 0x5D7080
PSQUAD_NAME_LENGTH_VA = 0x417A90
PSQUAD_NAME_FORMAT_VA = 0x417AE0
PSQUAD_NAME_FONT_SLOT_VA = 0x94758C
PSQUAD_NAME_RAW_FLAGS = 0x21

# 0x417AE0 literals used by the shared player-name formatter.
PSQUAD_NAME_FORMAT_FULL = "%s %s"
PSQUAD_NAME_FORMAT_INITIAL_SURNAME = "%c. %s"

# Logical source RGB components before the original packs them into the active
# game surface format. 0x489530 selects the role pair; 0x5D6C50 selects the
# name-status hierarchy.
PSQUAD_ROLE_PREFERRED_RGB = (255, 255, 255)
PSQUAD_ROLE_UNPREFERRED_RGB = (125, 1, 0)
PSQUAD_NAME_STATUS_RGB = (
    ("match_active", (255, 255, 255)),
    ("match_substitute_available", (232, 191, 94)),
    ("injured", (176, 176, 176)),
    ("suspended", (185, 167, 131)),
    ("default", (217, 210, 62)),
)


@dataclass(frozen=True)
class OriginalSquadColumnSnapshot:
    semantic_key: str
    x: int
    width: int | None
    source: str
    value_resolved: bool


@dataclass(frozen=True)
class OriginalSquadRowSnapshot:
    visible_index: int
    source_roster_index: int
    player_id: int
    y: int
    display_name: str
    display_name_status: str
    display_name_rgb: tuple[int, int, int]
    assigned_role: int
    assigned_role_is_preferred: bool
    assigned_role_rgb: tuple[int, int, int]
    condition: int
    recent_form_average: float
    current_role_rating: int


@dataclass(frozen=True)
class OriginalSquadViewportSnapshot:
    row_capacity: int
    row_y_origins: tuple[int, ...]
    player_columns: tuple[OriginalSquadColumnSnapshot, ...]
    side_columns: tuple[OriginalSquadColumnSnapshot, ...]
    rows: tuple[OriginalSquadRowSnapshot, ...]
    unresolved_value_columns: tuple[str, ...]


_RESOLVED_PLAYER_COLUMNS = {"assigned_role", "display_name"}
_RESOLVED_SIDE_COLUMNS = {"condition", "recent_form_average", "current_role_rating"}
_UNRESOLVED_COLUMNS = ("club_relative_assignment", "native_status_icon")


def _column_snapshot(column, resolved: set[str]) -> OriginalSquadColumnSnapshot:
    return OriginalSquadColumnSnapshot(
        semantic_key=column.name,
        x=column.x,
        width=column.width,
        source=column.source,
        value_resolved=column.name in resolved,
    )


def _require_int(value, *, label: str) -> int:
    if type(value) is not int:
        raise OriginalSquadPresentationError(f"{label} must be an integer source value")
    return value


def _require_bool(value, *, label: str) -> bool:
    if type(value) is not bool:
        raise OriginalSquadPresentationError(f"{label} must be a boolean source value")
    return value


def native_squad_display_name(first_name: str, surname: str) -> str:
    """Apply the exact PSquadPlayerRow name mode passed to 0x417AE0.

    PSquadPlayerRow passes name-format flag zero. The shared formatter therefore
    uses "%c. %s": first character of the first-name string plus surname. A
    first-name source string beginning '-' takes the formatter's special
    surname-only branch.
    """
    if not isinstance(first_name, str) or not first_name:
        raise OriginalSquadPresentationError(
            "first_name must be a non-empty source string"
        )
    if not isinstance(surname, str) or not surname:
        raise OriginalSquadPresentationError(
            "surname must be a non-empty source string"
        )
    if first_name.startswith("-"):
        return surname
    return f"{first_name[0]}. {surname}"


def native_squad_name_status(
    *,
    match_active: bool,
    match_substitute_available: bool,
    injured: bool,
    suspended: bool,
) -> tuple[str, tuple[int, int, int]]:
    """Return 0x5D6C50's exact first-match status/color branch."""
    flags = {
        "match_active": _require_bool(match_active, label="match_active"),
        "match_substitute_available": _require_bool(
            match_substitute_available,
            label="match_substitute_available",
        ),
        "injured": _require_bool(injured, label="injured"),
        "suspended": _require_bool(suspended, label="suspended"),
    }
    colors = dict(PSQUAD_NAME_STATUS_RGB)
    for status in (
        "match_active",
        "match_substitute_available",
        "injured",
        "suspended",
    ):
        if flags[status]:
            return status, colors[status]
    return "default", colors["default"]


def build_squad_row_viewport(rows: Iterable[object]) -> OriginalSquadViewportSnapshot:
    """Project one already-selected native Squad list viewport.

    PSquadList owns exactly 20 visible row shells. The original first/reserve
    filtering and any scrolling/paging behavior are outside this bounded
    presenter, so callers must provide no more than one recovered visible
    viewport and this function never chooses which players belong in it.
    """
    source_rows = tuple(rows)
    if len(source_rows) > SQUAD_VISIBLE_ROW_COUNT:
        raise OriginalSquadPresentationError(
            "Squad row input exceeds the source-proven 20-row visible viewport"
        )

    projected = []
    for visible_index, row in enumerate(source_rows):
        source_roster_index = _require_int(
            getattr(row, "source_roster_index", None),
            label="source_roster_index",
        )
        player_id = _require_int(getattr(row, "player_id", None), label="player_id")

        display_name = native_squad_display_name(
            getattr(row, "first_name", None),
            getattr(row, "surname", None),
        )
        display_name_status, display_name_rgb = native_squad_name_status(
            match_active=getattr(row, "match_active", None),
            match_substitute_available=getattr(
                row, "match_substitute_available", None
            ),
            injured=getattr(row, "injured", None),
            suspended=getattr(row, "suspended", None),
        )

        preferred_positions = getattr(row, "positions", None)
        if (
            not isinstance(preferred_positions, tuple)
            or len(preferred_positions) != 3
            or any(type(value) is not int for value in preferred_positions)
        ):
            raise OriginalSquadPresentationError(
                "positions must contain the three source role codes"
            )
        assigned_role = _require_int(
            getattr(row, "current_position", None),
            label="current_position",
        )
        assigned_role_is_preferred = assigned_role in preferred_positions
        assigned_role_rgb = (
            PSQUAD_ROLE_PREFERRED_RGB
            if assigned_role_is_preferred
            else PSQUAD_ROLE_UNPREFERRED_RGB
        )

        condition = _require_int(getattr(row, "condition", None), label="condition")
        current_role_rating = _require_int(
            getattr(row, "current_role_rating", None),
            label="current_role_rating",
        )
        recent_form_average = getattr(row, "recent_form_average", None)
        if isinstance(recent_form_average, bool) or not isinstance(
            recent_form_average, (int, float)
        ):
            raise OriginalSquadPresentationError(
                "recent_form_average must be a numeric source value"
            )

        projected.append(
            OriginalSquadRowSnapshot(
                visible_index=visible_index,
                source_roster_index=source_roster_index,
                player_id=player_id,
                y=SQUAD_VISIBLE_ROW_Y_ORIGINS[visible_index],
                display_name=display_name,
                display_name_status=display_name_status,
                display_name_rgb=display_name_rgb,
                assigned_role=assigned_role,
                assigned_role_is_preferred=assigned_role_is_preferred,
                assigned_role_rgb=assigned_role_rgb,
                condition=condition,
                recent_form_average=float(recent_form_average),
                current_role_rating=current_role_rating,
            )
        )

    return OriginalSquadViewportSnapshot(
        row_capacity=SQUAD_VISIBLE_ROW_COUNT,
        row_y_origins=tuple(SQUAD_VISIBLE_ROW_Y_ORIGINS),
        player_columns=tuple(
            _column_snapshot(column, _RESOLVED_PLAYER_COLUMNS)
            for column in SQUAD_PLAYER_COLUMNS
        ),
        side_columns=tuple(
            _column_snapshot(column, _RESOLVED_SIDE_COLUMNS)
            for column in SQUAD_SCF_COLUMNS
        ),
        rows=tuple(projected),
        unresolved_value_columns=_UNRESOLVED_COLUMNS,
    )
