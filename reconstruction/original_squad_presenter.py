"""Source-bounded read-only presenter for FM2001 PSquadList rows.

This module consumes immutable SquadRowView-style objects and exposes only the
row geometry/fields recovered from PSquadPlayerRow and PSCFRow. It deliberately
does not choose first-team versus reserve membership, resolve the club-relative
assignment selector, name the native status icon categories, or invent scrolling.
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
    assigned_role: int
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
        display_name = getattr(row, "full_name", None)
        if not isinstance(display_name, str) or not display_name:
            raise OriginalSquadPresentationError(
                "full_name must be a non-empty source string"
            )
        assigned_role = _require_int(
            getattr(row, "current_position", None),
            label="current_position",
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
                assigned_role=assigned_role,
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
