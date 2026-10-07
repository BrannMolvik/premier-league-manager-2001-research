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
from original_squad_row_style import (
    format_squad_display_name,
    squad_name_rgb_from_available_state,
    squad_role_rgb,
)
from original_squad_status import (
    direct_squad_status_frame_index,
    source_qualified_squad_status_frame_index,
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
    display_name_rgb: tuple[int, int, int] | None
    assigned_role: int
    assigned_role_abbreviation: str
    assigned_role_rgb: tuple[int, int, int]
    condition: int
    recent_form_average: float
    current_role_rating: int
    native_status_frame_index: int | None


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
        first_name = getattr(row, "first_name", None)
        surname = getattr(row, "surname", None)
        positions = getattr(row, "positions", None)
        match_active = getattr(row, "match_active", None)
        match_substitute_available = getattr(
            row, "match_substitute_available", None
        )
        reserve_active = getattr(row, "reserve_active", None)
        reserve_substitute_available = getattr(
            row, "reserve_substitute_available", None
        )
        try:
            display_name = format_squad_display_name(first_name, surname)
            display_name_rgb = squad_name_rgb_from_available_state(
                first_team_active=match_active,
                first_team_substitute=match_substitute_available,
                reserve_active=reserve_active,
                reserve_substitute=reserve_substitute_available,
            )
        except ValueError as exc:
            raise OriginalSquadPresentationError(str(exc)) from exc
        assigned_role = _require_int(
            getattr(row, "current_position", None),
            label="current_position",
        )
        assigned_role_abbreviation = getattr(row, "assigned_role_abbreviation", None)
        if not isinstance(assigned_role_abbreviation, str) or not assigned_role_abbreviation:
            raise OriginalSquadPresentationError(
                "assigned_role_abbreviation must be a non-empty source string"
            )
        try:
            assigned_role_rgb = squad_role_rgb(assigned_role, positions)
        except ValueError as exc:
            raise OriginalSquadPresentationError(str(exc)) from exc
        injured = getattr(row, "injured", None)
        banned = getattr(row, "suspended", None)
        international = getattr(row, "international", None)
        status_states = (injured, banned, international)
        if all(value is None for value in status_states):
            # Older/minimal source fixtures that do not carry the newly
            # recovered status state remain unresolved rather than fabricated.
            native_status_frame_index = None
        else:
            if any(type(value) is not bool for value in status_states):
                raise OriginalSquadPresentationError(
                    "Squad direct status states must be booleans when present"
                )
            alternate_on_loan = getattr(row, "alternate_on_loan", None)
            non_eu = getattr(row, "non_eu", None)
            non_eu_registration_expired = getattr(
                row, "non_eu_registration_expired", None
            )
            cup_tied_positive = getattr(row, "cup_tied_positive", None)
            extended_status_states = (
                alternate_on_loan,
                non_eu,
                cup_tied_positive,
            )
            try:
                if all(type(value) is bool for value in extended_status_states):
                    if (
                        non_eu_registration_expired is not None
                        and type(non_eu_registration_expired) is not bool
                    ):
                        raise OriginalSquadPresentationError(
                            "Non-EU registration cutoff state must be boolean or unresolved"
                        )
                    native_status_frame_index = source_qualified_squad_status_frame_index(
                        injured=injured,
                        banned=banned,
                        international=international,
                        alternate_on_loan=alternate_on_loan,
                        non_eu=non_eu,
                        non_eu_registration_expired=non_eu_registration_expired,
                        cup_tied_positive=cup_tied_positive,
                    )
                elif all(value is None for value in extended_status_states):
                    # Compatibility for bounded fixtures predating Recovery 340:
                    # preserve only the already source-closed direct 0/1/2 path.
                    native_status_frame_index = direct_squad_status_frame_index(
                        injured=injured,
                        banned=banned,
                        international=international,
                    )
                else:
                    raise OriginalSquadPresentationError(
                        "Extended Squad status states must be complete booleans"
                    )
            except ValueError as exc:
                raise OriginalSquadPresentationError(str(exc)) from exc

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
                display_name_rgb=display_name_rgb,
                assigned_role=assigned_role,
                assigned_role_abbreviation=assigned_role_abbreviation,
                assigned_role_rgb=assigned_role_rgb,
                condition=condition,
                recent_form_average=float(recent_form_average),
                current_role_rating=current_role_rating,
                native_status_frame_index=native_status_frame_index,
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
