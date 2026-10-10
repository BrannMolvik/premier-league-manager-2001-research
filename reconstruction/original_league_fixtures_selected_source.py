"""Source-authorized other real root-League fixtures, not the human's League.

Original PLeagueFixtures::0x46D950 uses the country/League radio's selected
League object, source 0x4F4940 ranked members and the primary global
373-head 0x947AD8 fixture-chain. This is read-only source qualification:
no native click acceptance, date guessing, new match reports or RNG.
"""
from __future__ import annotations

from typing import Mapping

from original_league_fixtures_selector_context import (
    LeagueFixturesSelectionContext,
    LeagueFixturesSelectorContextError,
    build_league_fixtures_selection_context,
)
from original_league_fixtures_primary_live import (
    SourcePrimaryLeagueFixtures,
    SourcePrimaryLeagueFixturesError,
    qualified_primary_league_fixtures,
)
from original_league_tables_live_source import (
    SourceProceduralLeagueTableError,
    source_qualified_selected_procedural_league_table,
)


class SourceSelectedLeagueFixturesError(ValueError):
    """Selected native true-League source cannot support a verified grid."""


def source_qualified_selected_nonpl_league_fixtures(
    *,
    human_club_id: int,
    selection: LeagueFixturesSelectionContext,
    clubs: Mapping[int, object],
    membership: Mapping[int, int],
    competitions: Mapping[int, object],
    procedural_leagues: Mapping[tuple[int, int], object],
    days: Mapping[object, tuple[object, ...]],
) -> SourcePrimaryLeagueFixtures:
    """Accept only actual eight-country source roots and complete native data.

    User-selected indices can differ from fresh constructor indices after
    legitimate radio events, but every option must be the real canonical
    root-League candidate for the current manager's available country radios.
    """
    if type(selection) is not LeagueFixturesSelectionContext:
        raise SourceSelectedLeagueFixturesError(
            "Original source-selected radio context is unavailable"
        )
    try:
        initial = build_league_fixtures_selection_context(
            club_id=human_club_id,
            clubs=clubs,
            membership=membership,
            competitions=competitions.values(),
        )
    except (LeagueFixturesSelectorContextError, AttributeError, TypeError) as exc:
        raise SourceSelectedLeagueFixturesError(
            "Original current-manager selector source is unauthenticated"
        ) from exc
    if selection.league_candidates != initial.league_candidates:
        raise SourceSelectedLeagueFixturesError(
            "Selected League radio candidates disagree with source country roots"
        )
    if (type(selection.active_country_index) is not int
            or not 0 <= selection.active_country_index < 8
            or type(selection.selected_league_indices) is not tuple
            or len(selection.selected_league_indices) != 8):
        raise SourceSelectedLeagueFixturesError(
            "Original source-selected radio index structure is malformed"
        )
    for country_index, league_index in enumerate(selection.selected_league_indices):
        if (type(league_index) is not int
                or not 0 <= league_index < len(initial.league_candidates[country_index])):
            raise SourceSelectedLeagueFixturesError(
                "Selected League index refers to an unconstructed native radio"
            )
    competition_id = selection.selected_competition_id
    selected_country_id = selection.active_country_id
    if competition_id == 0:
        raise SourceSelectedLeagueFixturesError(
            "Premier League 0 requires its distinct original fixed-source fixture path"
        )
    definition = competitions.get(competition_id)
    if definition is None:
        raise SourceSelectedLeagueFixturesError(
            "Selected original League competition definition is absent"
        )
    try:
        ranked = source_qualified_selected_procedural_league_table(
            selected_country_id=selected_country_id,
            competition_id=competition_id,
            membership=membership,
            clubs=clubs,
            competitions=competitions,
            procedural_leagues=procedural_leagues,
        )
        return qualified_primary_league_fixtures(
            competition_id=competition_id,
            member_club_ids=tuple(row.club_id for row in ranked),
            scheduled_matchday_count=getattr(
                definition, "scheduled_matchday_count", None),
            live=procedural_leagues.get((competition_id, 0)),
            days=days,
        )
    except (SourceProceduralLeagueTableError, SourcePrimaryLeagueFixturesError) as exc:
        raise SourceSelectedLeagueFixturesError(str(exc)) from exc
