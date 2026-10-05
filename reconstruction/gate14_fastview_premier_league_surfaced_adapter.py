"""Read-only Premier League adapter for FastView surfaced resources.

The fixed League builder passes literal -1 as Match constructor argument 4,
which becomes Match+0x48. Therefore ordinary fixed Premier League matches have
no background-club override and source helper 0x514220 falls back to the home
side. This adapter applies that proven fixed-League rule to one immutable
FixtureRowView and delegates all resource selection to the existing pure
selection layer.
"""
from __future__ import annotations

from datetime import date
from typing import Mapping

from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedResourceSelection,
    build_fastview_surfaced_resource_selection,
)


class FastViewPremierLeagueSurfacedAdapterError(ValueError):
    pass


FIXED_LEAGUE_BUILDER_VA = 0x6173D0
FIXED_LEAGUE_MATCH_CONSTRUCTOR_CALLSITE_VA = 0x617490
LEAGUE_MATCH_CONSTRUCTOR_VA = 0x5104F0
MATCH_BACKGROUND_OVERRIDE_OFFSET = 0x48
FIXED_LEAGUE_BACKGROUND_OVERRIDE_VALUE = -1


def build_premier_league_surfaced_resource_selection(
    fixture_row: object,
    *,
    clubs: Mapping[int, object],
    countries: Mapping[int, object],
) -> FastViewSurfacedResourceSelection:
    """Build the source resource plan for one fixed Premier League fixture."""
    scheduled_date = getattr(fixture_row, "scheduled_date", None)
    home_club_id = getattr(fixture_row, "home_club_id", None)
    away_club_id = getattr(fixture_row, "away_club_id", None)

    if type(scheduled_date) is not date:
        raise FastViewPremierLeagueSurfacedAdapterError(
            "Premier League surfaced selection requires exact scheduled_date"
        )
    if type(home_club_id) is not int or home_club_id < 0:
        raise FastViewPremierLeagueSurfacedAdapterError(
            "Premier League surfaced selection requires source home club id"
        )
    if type(away_club_id) is not int or away_club_id < 0:
        raise FastViewPremierLeagueSurfacedAdapterError(
            "Premier League surfaced selection requires source away club id"
        )

    # Source-proven fixed League construction passes -1 for Match+0x48.
    # The pure selector represents that absent sentinel as explicit None.
    return build_fastview_surfaced_resource_selection(
        match_date=scheduled_date,
        clubs=clubs,
        countries=countries,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        background_club_override_id=None,
    )


def premier_league_surfaced_adapter_contract() -> dict:
    return {
        "fixed_league_builder_va": FIXED_LEAGUE_BUILDER_VA,
        "fixed_league_match_constructor_callsite_va":
            FIXED_LEAGUE_MATCH_CONSTRUCTOR_CALLSITE_VA,
        "league_match_constructor_va": LEAGUE_MATCH_CONSTRUCTOR_VA,
        "match_background_override_offset": MATCH_BACKGROUND_OVERRIDE_OFFSET,
        "fixed_league_background_override_value":
            FIXED_LEAGUE_BACKGROUND_OVERRIDE_VALUE,
        "selection_override_passed_as_none": True,
        "read_only_adapter": True,
        "source_bytes_loaded": False,
        "ea444_decoded": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
