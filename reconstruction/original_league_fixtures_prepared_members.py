"""Read-only original PLeagueFixtures member preparation for a live League.

Hash-gated source (Recovery505): PLeagueFixtures::0x46D950 calls
League::0x4F4940; League vtable+0x38 points to 0x4F4720, which calls CRT
qsort with original comparator 0x4F45E0 over League+0x34 members.
This is NOT the original 373-head fixture-chain/linked status traversal.
The returned member vector must not authorize a non-PL fixtures matrix until
that independently recovered original producer is attached and verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from original_league_fixtures_selector_context import (
    LeagueFixturesSelectorContextError,
    build_league_fixtures_selection_context,
)
from original_league_tables_live_source import (
    SourceProceduralLeagueTableError,
    source_qualified_procedural_league_table,
)


class OriginalLeagueFixturesMembersError(ValueError):
    """Original selected League's prepared members are not source-qualified."""


@dataclass(frozen=True)
class OriginalPreparedLeagueFixturesMembers:
    manager_club_id: int
    country_id: int
    competition_id: int
    member_club_ids: tuple[int, ...]
    # Do not treat this order as original fixture-chain/date/phase order.
    original_member_comparator_va: int = 0x4F45E0
    original_member_preparation_va: int = 0x4F4940


def original_current_league_fixtures_prepared_members(
    *,
    human_club_id: int,
    membership: Mapping[int, int],
    clubs: Mapping[int, object],
    competitions: Mapping[int, object],
    procedural_leagues: Mapping[tuple[int, int], object],
) -> OriginalPreparedLeagueFixturesMembers:
    """Recover verified current-manager League members, not a match matrix.

    A fresh Southport career has club349, England26, Conference7. Unlike a
    hardcoded fixture choice, this function always resolves the LIVE source
    membership and survives later legitimate season promotion/relegation.
    A separately recovered Premier League source path already owns League0,
    so do not substitute that unrelated backend for any other competition.
    """
    try:
        selected = build_league_fixtures_selection_context(
            club_id=human_club_id,
            clubs=clubs,
            membership=membership,
            competitions=competitions.values(),
        )
    except LeagueFixturesSelectorContextError as exc:
        raise OriginalLeagueFixturesMembersError(str(exc)) from exc
    league_id = selected.selected_competition_id
    if league_id is None:
        raise OriginalLeagueFixturesMembersError(
            "Current managed club's original League radio is unresolved"
        )
    if league_id == 0:
        raise OriginalLeagueFixturesMembersError(
            "The existing Premier League source owns competition 0"
        )
    try:
        ranked = source_qualified_procedural_league_table(
            human_club_id=human_club_id,
            competition_id=league_id,
            membership=membership,
            clubs=clubs,
            competitions=competitions,
            procedural_leagues=procedural_leagues,
        )
    except SourceProceduralLeagueTableError as exc:
        raise OriginalLeagueFixturesMembersError(str(exc)) from exc

    members = tuple(row.club_id for row in ranked)
    if human_club_id not in members or len(set(members)) != len(members):
        raise OriginalLeagueFixturesMembersError(
            "Prepared member list omits or repeats the controlled club"
        )
    return OriginalPreparedLeagueFixturesMembers(
        manager_club_id=human_club_id,
        country_id=selected.active_country_id,
        competition_id=league_id,
        member_club_ids=members,
    )
