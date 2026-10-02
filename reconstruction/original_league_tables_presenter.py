"""Source-faithful read-only presenter for FM2001 PLeagueTables.

The presenter consumes immutable LeagueTableRowView-style rows from the Gate-13
source-data seam and projects only the layout/data contract recovered from the
original executable. It deliberately does not import simulation modules,
invent substitute artwork, or claim the original Current Form ordering before
that ordering is available from the presentation bridge.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from original_league_tables_resources import (
    LEAGUE_TABLES_HEADER_TEXTS,
    LEAGUE_TABLES_LIST_RECT,
    LEAGUE_TABLES_LIST_ROW_COUNT,
    LEAGUE_TABLES_LIST_ROW_STEP,
    LEAGUE_TABLES_RESOURCE_BY_NAME,
    LEAGUE_TABLES_RESOURCES,
    LEAGUE_TABLES_ROW_CLUB_RECT,
    LEAGUE_TABLES_ROW_COLUMN_LABELS,
    LEAGUE_TABLES_ROW_RANK_RECT,
    LEAGUE_TABLES_ROW_STAT_RECTS,
    LEAGUE_TABLES_SORT_DEFAULT_STATE,
    league_tables_stat_header_state,
)


class OriginalLeagueTablesPresentationError(ValueError):
    """The source-backed League Tables presentation cannot be built safely."""


@dataclass(frozen=True)
class OriginalLeagueTablesHeaderSlot:
    label: str | None
    rect: tuple[int, int, int, int]


@dataclass(frozen=True)
class OriginalLeagueTablesRowSnapshot:
    source_index: int
    position: int
    club_id: int
    club_name: str
    rank_rect: tuple[int, int, int, int]
    club_rect: tuple[int, int, int, int]
    stat_rects: tuple[tuple[int, int, int, int], ...]
    values: tuple[int, int, int, int, int, int, int]

    @property
    def played(self) -> int:
        return self.values[0]

    @property
    def wins(self) -> int:
        return self.values[1]

    @property
    def draws(self) -> int:
        return self.values[2]

    @property
    def losses(self) -> int:
        return self.values[3]

    @property
    def goals_for(self) -> int:
        return self.values[4]

    @property
    def goals_against(self) -> int:
        return self.values[5]

    @property
    def points(self) -> int:
        return self.values[6]


@dataclass(frozen=True)
class OriginalLeagueTablesSnapshot:
    list_rect: tuple[int, int, int, int]
    row_capacity: int
    row_step: int
    sort_state: int
    stat_headers_active: bool
    headers: tuple[OriginalLeagueTablesHeaderSlot, ...]
    rows: tuple[OriginalLeagueTablesRowSnapshot, ...]
    required_art: tuple[str, ...]
    exact_art_staged: bool


def _require_int(value, *, label: str) -> int:
    if type(value) is not int:
        raise OriginalLeagueTablesPresentationError(
            f"{label} must be an integer source value"
        )
    return value


def build_league_tables_snapshot(
    rows: Iterable[object],
    *,
    sort_state: int = LEAGUE_TABLES_SORT_DEFAULT_STATE,
    staged_resource_names: Iterable[str] = (),
) -> OriginalLeagueTablesSnapshot:
    """Project bridge rows into the recovered source-default League Tables view.

    The bridge currently exposes the native League Position ordering. Source
    sort state 1 (Current Form) is known at the original UI boundary but is not
    yet exposed through the bridge, so this function rejects it rather than
    silently reusing League Position order.
    """
    if type(sort_state) is not int:
        raise OriginalLeagueTablesPresentationError(
            "League Tables sort state must be an integer"
        )
    if sort_state != LEAGUE_TABLES_SORT_DEFAULT_STATE:
        raise OriginalLeagueTablesPresentationError(
            "Current Form ordering is not yet available through the presentation bridge"
        )

    source_rows = tuple(rows)
    if len(source_rows) > LEAGUE_TABLES_LIST_ROW_COUNT:
        raise OriginalLeagueTablesPresentationError(
            "League Tables row count exceeds the source-proven 24-row capacity"
        )

    projected = []
    for source_index, row in enumerate(source_rows):
        position = _require_int(getattr(row, "position", None), label="position")
        club_id = _require_int(getattr(row, "club_id", None), label="club_id")
        club_name = getattr(row, "club_name", None)
        if not isinstance(club_name, str) or not club_name:
            raise OriginalLeagueTablesPresentationError(
                "club_name must be a non-empty source string"
            )

        played = _require_int(getattr(row, "played", None), label="played")
        wins = _require_int(getattr(row, "wins", None), label="wins")
        draws = _require_int(getattr(row, "draws", None), label="draws")
        losses = _require_int(getattr(row, "losses", None), label="losses")
        goals_for = _require_int(getattr(row, "goals_for", None), label="goals_for")
        goals_against = _require_int(
            getattr(row, "goals_against", None), label="goals_against"
        )
        points = _require_int(getattr(row, "points", None), label="points")

        source_points = 3 * wins + draws
        if points != source_points:
            raise OriginalLeagueTablesPresentationError(
                f"row {source_index} points do not match original 3*W+D arithmetic"
            )

        projected.append(
            OriginalLeagueTablesRowSnapshot(
                source_index=source_index,
                position=position,
                club_id=club_id,
                club_name=club_name,
                rank_rect=LEAGUE_TABLES_ROW_RANK_RECT,
                club_rect=LEAGUE_TABLES_ROW_CLUB_RECT,
                stat_rects=tuple(LEAGUE_TABLES_ROW_STAT_RECTS),
                values=(
                    played,
                    wins,
                    draws,
                    losses,
                    goals_for,
                    goals_against,
                    points,
                ),
            )
        )

    staged = set(staged_resource_names)
    unknown = staged.difference(LEAGUE_TABLES_RESOURCE_BY_NAME)
    if unknown:
        raise OriginalLeagueTablesPresentationError(
            "Unknown staged League Tables art: " + ", ".join(sorted(unknown))
        )
    required = tuple(resource.name for resource in LEAGUE_TABLES_RESOURCES)

    return OriginalLeagueTablesSnapshot(
        list_rect=LEAGUE_TABLES_LIST_RECT,
        row_capacity=LEAGUE_TABLES_LIST_ROW_COUNT,
        row_step=LEAGUE_TABLES_LIST_ROW_STEP,
        sort_state=sort_state,
        stat_headers_active=league_tables_stat_header_state(sort_state).active,
        headers=tuple(
            OriginalLeagueTablesHeaderSlot(header.label, header.rect)
            for header in LEAGUE_TABLES_HEADER_TEXTS
        ),
        rows=tuple(projected),
        required_art=required,
        exact_art_staged=set(required).issubset(staged),
    )
