"""Source-only native Current Form PLeagueTables view; NOT original row art.

Original source uses a different 0x2B0 row class (constructor 0x4480A0)
when PLeagueTables sort state is 1. Actual six-child widget geometry, font,
raster, clip and OS mouse-to-radio acceptance remain unverified. This immutable
view represents only the genuine source-selected rows, never stat-row pixels.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gate13_management_source_data import LeagueCurrentFormSourceRowView
from original_league_tables_selector_context import OriginalLeagueTablesSelectionContext
from original_league_tables_resources import LEAGUE_TABLES_LIST_ROW_COUNT


class OriginalLeagueTablesCurrentFormDataError(ValueError):
    """Cannot represent original alternate Current Form source without invention."""


@dataclass(frozen=True)
class OriginalLeagueTablesCurrentFormDataSnapshot:
    """Native event15/0x4F4A10 data; no native 0x4480A0 coordinates."""

    competition_id: int
    country_id: int
    sort_state: int
    rows: tuple[LeagueCurrentFormSourceRowView, ...]
    native_alternate_row_geometry_recovered: bool = False
    native_mouse_event15_recovered: bool = False

    def __post_init__(self) -> None:
        if self.sort_state != 1:
            raise OriginalLeagueTablesCurrentFormDataError(
                "Current Form data snapshot requires original sort state1"
            )
        if self.native_alternate_row_geometry_recovered or self.native_mouse_event15_recovered:
            raise OriginalLeagueTablesCurrentFormDataError(
                "Current Form data cannot claim unproven native row or mouse behavior"
            )


def build_league_tables_current_form_data_snapshot(
    selection: OriginalLeagueTablesSelectionContext,
    source_rows: Iterable[LeagueCurrentFormSourceRowView],
) -> OriginalLeagueTablesCurrentFormDataSnapshot:
    """Preserve the qualified native six-result ranking, not seven-stat layout."""
    if (type(selection) is not OriginalLeagueTablesSelectionContext
            or type(selection.sort_state) is not int
            or selection.sort_state != 1):
        raise OriginalLeagueTablesCurrentFormDataError(
            "Original Current Form semantic view requires native event15 selection"
        )
    rows = tuple(source_rows)
    if not 1 <= len(rows) <= LEAGUE_TABLES_LIST_ROW_COUNT:
        raise OriginalLeagueTablesCurrentFormDataError(
            "Original Current Form row count outside source list capacity"
        )
    found = set()
    for i, row in enumerate(rows):
        if type(row) is not LeagueCurrentFormSourceRowView:
            raise OriginalLeagueTablesCurrentFormDataError(
                "Original Current Form row has non-native source type"
            )
        if type(row.source_index) is not int or row.source_index != i:
            raise OriginalLeagueTablesCurrentFormDataError(
                "Original Current Form row source order is unverified"
            )
        if type(row.club_id) is not int or row.club_id in found:
            raise OriginalLeagueTablesCurrentFormDataError(
                "Original Current Form row source club identity is invalid"
            )
        found.add(row.club_id)
        if not isinstance(row.club_name, str) or not row.club_name:
            raise OriginalLeagueTablesCurrentFormDataError(
                "Original Current Form club name is unavailable"
            )
        if (type(row.form_score) is not int or not 0 <= row.form_score <= 18
                or type(row.six_form_labels) is not tuple
                or len(row.six_form_labels) != 6
                or any(type(label) is not str or label not in ("W", "D", "L", " ")
                       for label in row.six_form_labels)
                or type(row.matching_source_tokens) is not tuple):
            raise OriginalLeagueTablesCurrentFormDataError(
                "Original Current Form has invalid six-result source values"
            )
    return OriginalLeagueTablesCurrentFormDataSnapshot(
        competition_id=selection.selected_competition_id,
        country_id=selection.active_country_id,
        sort_state=selection.sort_state,
        rows=rows,
    )
