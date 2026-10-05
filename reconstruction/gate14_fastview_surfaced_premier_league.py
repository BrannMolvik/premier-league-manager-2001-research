"""Read-only surfaced-resource selection for fixed Premier League matches.

The shipped fixed League builder passes literal -1 as Match constructor
argument 4. Match::0x5103D0 stores that argument at +0x48, so the already
source-closed background helper 0x514220 falls back to Match +0x14 (home).

This adapter is intentionally restricted to fixtures that are present in the
immutable shipped source-fixture identity ledger. Annual procedural Premier
League fixtures and Cup nodes require their own constructor proof.
"""
from __future__ import annotations

from datetime import date

from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedResourceSelection,
    FastViewSurfacedSelectionError,
    build_fastview_surfaced_resource_selection,
)


FIXED_LEAGUE_BUILDER_VA = 0x6173D0
FIXED_LEAGUE_MATCH_CONSTRUCTOR_CALLSITE_VA = 0x617490
LEAGUE_MATCH_CONSTRUCTOR_VA = 0x5104F0
MATCH_BASE_CONSTRUCTOR_VA = 0x5103D0
MATCH_BACKGROUND_OVERRIDE_OFFSET = 0x48
FIXED_LEAGUE_BACKGROUND_OVERRIDE_LITERAL = -1


class FastViewPremierLeagueSurfacedSelectionError(ValueError):
    pass


def _fixed_source_fixture_identity(state: object, fixture_id: int) -> tuple[int, int, int, int]:
    rows = getattr(state, "source_fixture_identity", None)
    if type(rows) is not tuple:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "state has no immutable shipped source-fixture identity ledger"
        )
    matches = tuple(
        row
        for row in rows
        if type(row) is tuple
        and len(row) == 4
        and type(row[0]) is int
        and row[0] == fixture_id
    )
    if len(matches) != 1:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "fixture is not exactly one shipped fixed League source fixture"
        )
    row = matches[0]
    if any(type(value) is not int for value in row):
        raise FastViewPremierLeagueSurfacedSelectionError(
            "source-fixture identity must contain exact integers"
        )
    return row


def build_fixed_premier_league_surfaced_selection(
    state: object,
    fixture_id: int,
) -> FastViewSurfacedResourceSelection:
    """Bind one shipped fixed PL fixture to exact surfaced-resource attempts."""
    if type(fixture_id) is not int or fixture_id < 0:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "fixture_id must be a non-negative integer"
        )

    premier = getattr(state, "premier_league", None)
    if premier is None:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "state has no Premier League runtime"
        )
    fixtures = getattr(premier, "fixtures", None)
    if not isinstance(fixtures, dict) or fixture_id not in fixtures:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "fixture is not present in the live Premier League runtime"
        )
    fixture = fixtures[fixture_id]
    source_id, source_round, source_home, source_away = (
        _fixed_source_fixture_identity(state, fixture_id)
    )

    actual = (
        int(getattr(fixture, "id")),
        int(getattr(fixture, "round_index")),
        int(getattr(fixture, "home_club_id")),
        int(getattr(fixture, "away_club_id")),
    )
    if actual != (source_id, source_round, source_home, source_away):
        raise FastViewPremierLeagueSurfacedSelectionError(
            "live fixed fixture identity drifted from shipped source"
        )

    round_date = getattr(premier, "round_date", None)
    if not callable(round_date):
        raise FastViewPremierLeagueSurfacedSelectionError(
            "Premier League runtime cannot resolve the source match date"
        )
    match_date = round_date(source_round)
    if type(match_date) is not date:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "fixed fixture has no exact reconstructed match date"
        )

    clubs = getattr(state, "clubs", None)
    countries = getattr(state, "countries", None)
    if not isinstance(clubs, dict) or not isinstance(countries, dict):
        raise FastViewPremierLeagueSurfacedSelectionError(
            "state has no source-backed club/country art data"
        )

    try:
        return build_fastview_surfaced_resource_selection(
            match_date=match_date,
            clubs=clubs,
            countries=countries,
            home_club_id=source_home,
            away_club_id=source_away,
            background_club_override_id=None,
        )
    except FastViewSurfacedSelectionError as exc:
        raise FastViewPremierLeagueSurfacedSelectionError(
            "fixed Premier League surfaced selection could not be source-bound"
        ) from exc


def fixed_premier_league_surfaced_contract() -> dict:
    return {
        "fixed_league_builder_va": FIXED_LEAGUE_BUILDER_VA,
        "match_constructor_callsite_va": FIXED_LEAGUE_MATCH_CONSTRUCTOR_CALLSITE_VA,
        "league_match_constructor_va": LEAGUE_MATCH_CONSTRUCTOR_VA,
        "match_base_constructor_va": MATCH_BASE_CONSTRUCTOR_VA,
        "match_background_override_offset": MATCH_BACKGROUND_OVERRIDE_OFFSET,
        "fixed_league_background_override_literal": FIXED_LEAGUE_BACKGROUND_OVERRIDE_LITERAL,
        "fixed_league_background_override_absent": True,
        "fixed_league_background_falls_back_to_home": True,
        "shipped_source_fixture_identity_required": True,
        "annual_procedural_league_override_proven": False,
        "cup_override_proven": False,
        "gate14_complete": False,
    }
