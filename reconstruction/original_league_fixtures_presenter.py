"""Source-faithful read-only presenter for FM2001 PLeagueFixtures.

The presenter consumes the strict Gate-13 LeagueFixturesGridSourceView and
projects only the recovered PLeagueFixtures matrix contract. It does not invent
the still-open surrounding shell/background or selector text geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from original_league_fixtures_resources import (
    LEAGUE_FIXTURE_STATUS_COMPLETE_BIT,
    LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
    LEAGUE_FIXTURES_RESOURCES,
    LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
    LEAGUE_FIXTURES_VISIBLE_COLUMNS,
    LEAGUE_FIXTURES_VISIBLE_ROWS,
    league_fixture_box_for_cell,
    league_fixture_empty_slot_is_self_match,
    league_fixture_first_free_repeat_slot,
    league_fixture_matrix_slot,
    league_fixture_visible_text,
)


class OriginalLeagueFixturesPresentationError(ValueError):
    """The recovered League Fixtures grid cannot be projected safely."""


@dataclass(frozen=True)
class OriginalLeagueFixturesCellSnapshot:
    row: int
    column: int
    matrix_slot: int
    row_club_id: int
    column_club_id: int
    fixture_id: int | None
    fixture_source_index: int | None
    played: bool
    text: str | None
    resource_name: str
    selected: bool


@dataclass(frozen=True)
class OriginalLeagueFixturesSnapshot:
    competition_id: int
    member_club_ids: tuple[int, ...]
    scheduled_matchday_count: int
    schedule_cycle_count: int
    matrix_layer_count: int
    column_offset: int
    visible_column_club_ids: tuple[int, ...]
    visible_row_club_ids: tuple[int, ...]
    vertical_grid_positions: tuple[tuple[int, int], ...]
    horizontal_grid_positions: tuple[tuple[int, int], ...]
    cells: tuple[OriginalLeagueFixturesCellSnapshot, ...]
    required_art: tuple[str, ...]
    exact_art_staged: bool
    source_fixture_count: int


def _source_int(value, *, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise OriginalLeagueFixturesPresentationError(
            f"{label} must be an integer >= {minimum}"
        )
    return value


def build_league_fixtures_snapshot(
    source: object,
    *,
    column_offset: int = 0,
    selected_cell: tuple[int, int] | None = None,
    staged_resource_names: Iterable[str] = (),
) -> OriginalLeagueFixturesSnapshot:
    """Project the recovered PLeagueFixtures directed-pair matrix.

    The source object must already carry the exact ordinary-League member order
    produced by 0x4F4940/0x4F45E0 and the 0x616F40-derived repeat-layer count.
    Fixture rows are the current fixed/procedural Premier League rows in their
    persisted source order. The clean-room PL runtime has no modeled 0x20
    exclusion state, so every row in this already-scoped PL sequence is a
    matrix candidate; completion maps only to the independently recovered bit 0.
    """
    competition_id = _source_int(
        getattr(source, "competition_id", None), label="competition_id"
    )
    members = getattr(source, "member_club_ids", None)
    if not isinstance(members, tuple) or len(members) <= 1:
        raise OriginalLeagueFixturesPresentationError(
            "member_club_ids must be a prepared source tuple with at least two clubs"
        )
    member_ids = tuple(_source_int(v, label="member club ID") for v in members)
    if len(member_ids) != len(set(member_ids)):
        raise OriginalLeagueFixturesPresentationError(
            "prepared League Fixtures members must be unique"
        )

    scheduled_matchday_count = _source_int(
        getattr(source, "scheduled_matchday_count", None),
        label="scheduled_matchday_count",
    )
    schedule_cycle_count = _source_int(
        getattr(source, "schedule_cycle_count", None),
        label="schedule_cycle_count",
        minimum=1,
    )
    layer_count = _source_int(
        getattr(source, "matrix_layer_count", None),
        label="matrix_layer_count",
        minimum=1,
    )
    if layer_count != schedule_cycle_count // 2:
        raise OriginalLeagueFixturesPresentationError(
            "matrix_layer_count does not match the recovered PLeagueFixtures "
            "0x616F40 / 2 rule"
        )

    club_count = len(member_ids)
    max_offset = max(0, club_count - LEAGUE_FIXTURES_VISIBLE_COLUMNS)
    if type(column_offset) is not int or not 0 <= column_offset <= max_offset:
        raise OriginalLeagueFixturesPresentationError(
            "column_offset is outside the source-reachable 12-club window"
        )

    selected = None
    if selected_cell is not None:
        if (
            not isinstance(selected_cell, tuple)
            or len(selected_cell) != 2
            or any(type(v) is not int for v in selected_cell)
        ):
            raise OriginalLeagueFixturesPresentationError(
                "selected_cell must be a (column,row) integer tuple"
            )
        selected_column, selected_row = selected_cell
        if not (
            0 <= selected_column < LEAGUE_FIXTURES_VISIBLE_COLUMNS
            and 0 <= selected_row < LEAGUE_FIXTURES_VISIBLE_ROWS
        ):
            raise OriginalLeagueFixturesPresentationError(
                "selected_cell is outside the recovered visible grid"
            )
        selected = (selected_column, selected_row)

    fixtures = getattr(source, "fixtures_in_source_order", None)
    if not isinstance(fixtures, tuple):
        raise OriginalLeagueFixturesPresentationError(
            "fixtures_in_source_order must be a source tuple"
        )

    member_index = {club_id: index for index, club_id in enumerate(member_ids)}
    matrix_size = layer_count * club_count * club_count
    matrix: list[object | None] = [None] * matrix_size
    occupied = [False] * matrix_size

    for fixture in fixtures:
        home_id = _source_int(
            getattr(fixture, "home_club_id", None), label="fixture home club ID"
        )
        away_id = _source_int(
            getattr(fixture, "away_club_id", None), label="fixture away club ID"
        )
        if home_id not in member_index or away_id not in member_index:
            raise OriginalLeagueFixturesPresentationError(
                "Premier League fixture references a club outside prepared members"
            )
        try:
            slot = league_fixture_first_free_repeat_slot(
                occupied,
                club_count=club_count,
                left_member_index=member_index[home_id],
                right_member_index=member_index[away_id],
                layer_count=layer_count,
            )
        except ValueError as exc:
            raise OriginalLeagueFixturesPresentationError(
                "fixture sequence exceeds the source-allocated directed-pair layers"
            ) from exc
        occupied[slot] = True
        matrix[slot] = fixture

    visible_columns = member_ids[
        column_offset : column_offset + LEAGUE_FIXTURES_VISIBLE_COLUMNS
    ]
    total_rows = min(LEAGUE_FIXTURES_VISIBLE_ROWS, layer_count * club_count)
    visible_rows = tuple(
        member_ids[row % club_count] for row in range(total_rows)
    )

    cells = []
    for row in range(total_rows):
        row_member_index = row % club_count
        repeat_layer = row // club_count
        row_club_id = member_ids[row_member_index]
        for column, column_club_id in enumerate(visible_columns):
            column_member_index = column_offset + column
            slot = league_fixture_matrix_slot(
                club_count=club_count,
                left_member_index=row_member_index,
                right_member_index=column_member_index,
                repeat_layer=repeat_layer,
            )
            fixture = matrix[slot]
            is_selected = selected == (column, row)
            if fixture is None:
                resource = league_fixture_box_for_cell(
                    fixture_present=False,
                    empty_slot_same_club=league_fixture_empty_slot_is_self_match(
                        row_club_id, column_club_id
                    ),
                    selected=is_selected,
                )
                cells.append(
                    OriginalLeagueFixturesCellSnapshot(
                        row=row,
                        column=column,
                        matrix_slot=slot,
                        row_club_id=row_club_id,
                        column_club_id=column_club_id,
                        fixture_id=None,
                        fixture_source_index=None,
                        played=False,
                        text=None,
                        resource_name=resource.name,
                        selected=is_selected,
                    )
                )
                continue

            played = getattr(fixture, "played", None)
            if type(played) is not bool:
                raise OriginalLeagueFixturesPresentationError(
                    "fixture played state must be boolean"
                )
            status_bits = LEAGUE_FIXTURE_STATUS_COMPLETE_BIT if played else 0
            if played:
                home_goals = _source_int(
                    getattr(fixture, "home_goals", None), label="home_goals"
                )
                away_goals = _source_int(
                    getattr(fixture, "away_goals", None), label="away_goals"
                )
                text = league_fixture_visible_text(
                    fixture_status_bits=status_bits,
                    score_left=home_goals,
                    score_right=away_goals,
                )
            else:
                scheduled = getattr(fixture, "scheduled_date", None)
                if scheduled is None:
                    raise OriginalLeagueFixturesPresentationError(
                        "unplayed fixture requires the recovered scheduled date"
                    )
                text = league_fixture_visible_text(
                    fixture_status_bits=status_bits,
                    date_day=int(scheduled.day),
                    date_month=int(scheduled.month),
                )

            resource = league_fixture_box_for_cell(
                fixture_present=True,
                fixture_status_bits=status_bits,
                selected=is_selected,
            )
            cells.append(
                OriginalLeagueFixturesCellSnapshot(
                    row=row,
                    column=column,
                    matrix_slot=slot,
                    row_club_id=row_club_id,
                    column_club_id=column_club_id,
                    fixture_id=_source_int(
                        getattr(fixture, "fixture_id", None), label="fixture_id"
                    ),
                    fixture_source_index=_source_int(
                        getattr(fixture, "source_fixture_index", None),
                        label="fixture_source_index",
                    ),
                    played=played,
                    text=text,
                    resource_name=resource.name,
                    selected=is_selected,
                )
            )

    staged = set(staged_resource_names)
    resource_by_name = {resource.name: resource for resource in LEAGUE_FIXTURES_RESOURCES}
    unknown = staged.difference(resource_by_name)
    if unknown:
        raise OriginalLeagueFixturesPresentationError(
            "Unknown staged League Fixtures art: " + ", ".join(sorted(unknown))
        )
    required = tuple(resource_by_name)

    return OriginalLeagueFixturesSnapshot(
        competition_id=competition_id,
        member_club_ids=member_ids,
        scheduled_matchday_count=scheduled_matchday_count,
        schedule_cycle_count=schedule_cycle_count,
        matrix_layer_count=layer_count,
        column_offset=column_offset,
        visible_column_club_ids=visible_columns,
        visible_row_club_ids=visible_rows,
        vertical_grid_positions=tuple(
            LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS[: len(visible_columns)]
        ),
        horizontal_grid_positions=tuple(
            LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS[: len(visible_rows)]
        ),
        cells=tuple(cells),
        required_art=required,
        exact_art_staged=set(required).issubset(staged),
        source_fixture_count=len(fixtures),
    )
