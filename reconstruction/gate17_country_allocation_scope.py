"""Map source LeagueAllocation rows onto TeamSelect-playable countries.

This is a planning/audit primitive for Gate 17. It preserves the source record
order and exact ranking endpoint IDs but performs no membership exchange and
does not invent promotion/relegation policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    derive_original_playable_scope,
)
from fm2001_data import FM2001Database
from verify import verify_canonical_files


class CompetitionSource(Protocol):
    id: int
    country_region_id: int


class LeagueAllocationSource(Protocol):
    id: int
    competition_a_id: int
    competition_b_id: int


class Gate17CountryAllocationScopeError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlayableCountryAllocationScope:
    country_id: int
    country_name: str
    selectable_league_ids: tuple[int, ...]
    allocation_ids: tuple[int, ...]
    ranking_endpoint_ids: tuple[int, ...]

    @property
    def has_transition_rows(self) -> bool:
        return bool(self.allocation_ids)

    def as_dict(self) -> dict:
        return {
            "country_id": self.country_id,
            "country_name": self.country_name,
            "selectable_league_ids": list(self.selectable_league_ids),
            "allocation_ids": list(self.allocation_ids),
            "ranking_endpoint_ids": list(self.ranking_endpoint_ids),
            "has_transition_rows": self.has_transition_rows,
        }


@dataclass(frozen=True)
class PlayableCountryAllocationPlan:
    catalog_sha256: str
    countries: tuple[PlayableCountryAllocationScope, ...]
    assigned_allocation_ids: tuple[int, ...]
    ignored_allocation_ids: tuple[int, ...]

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "country_count": len(self.countries),
            "assigned_allocation_ids": list(self.assigned_allocation_ids),
            "ignored_allocation_ids": list(self.ignored_allocation_ids),
            "countries": [country.as_dict() for country in self.countries],
        }


def derive_playable_country_allocation_plan(
    scope: OriginalPlayableScope,
    records: Iterable[LeagueAllocationSource],
    competitions: Iterable[CompetitionSource],
) -> PlayableCountryAllocationPlan:
    """Group allocation rows by the exact source country of both endpoints."""
    if type(scope) is not OriginalPlayableScope:
        raise Gate17CountryAllocationScopeError(
            "country allocation plan requires exact OriginalPlayableScope"
        )

    competition_map: dict[int, CompetitionSource] = {}
    for competition in competitions:
        competition_id = int(competition.id)
        if competition_id in competition_map:
            raise Gate17CountryAllocationScopeError(
                f"duplicate competition ID {competition_id}"
            )
        competition_map[competition_id] = competition

    rows = tuple(records)
    record_ids = tuple(int(record.id) for record in rows)
    if len(set(record_ids)) != len(record_ids):
        raise Gate17CountryAllocationScopeError(
            "LeagueAllocation record IDs must be unique"
        )

    playable_country_ids = tuple(int(country.country_id) for country in scope.countries)
    playable_set = set(playable_country_ids)
    assigned: dict[int, list[LeagueAllocationSource]] = {
        country_id: [] for country_id in playable_country_ids
    }
    ignored: list[int] = []

    for record in rows:
        allocation_id = int(record.id)
        a_id = int(record.competition_a_id)
        b_id = int(record.competition_b_id)
        a = competition_map.get(a_id)
        b = competition_map.get(b_id)
        if a is None or b is None:
            missing = tuple(
                value
                for value, item in ((a_id, a), (b_id, b))
                if item is None
            )
            raise Gate17CountryAllocationScopeError(
                f"allocation {allocation_id} references missing competitions {missing}"
            )

        country_a = int(a.country_region_id)
        country_b = int(b.country_region_id)
        if country_a == country_b and country_a in playable_set:
            assigned[country_a].append(record)
            continue
        if country_a in playable_set or country_b in playable_set:
            raise Gate17CountryAllocationScopeError(
                f"allocation {allocation_id} crosses playable-country boundary "
                f"{country_a}/{country_b}"
            )
        ignored.append(allocation_id)

    country_plans: list[PlayableCountryAllocationScope] = []
    assigned_ids: list[int] = []
    for country in scope.countries:
        country_id = int(country.country_id)
        country_rows = tuple(assigned[country_id])
        endpoints: list[int] = []
        seen_endpoints: set[int] = set()
        for record in country_rows:
            assigned_ids.append(int(record.id))
            for endpoint in (
                int(record.competition_a_id),
                int(record.competition_b_id),
            ):
                if endpoint not in seen_endpoints:
                    endpoints.append(endpoint)
                    seen_endpoints.add(endpoint)

        country_plans.append(
            PlayableCountryAllocationScope(
                country_id=country_id,
                country_name=str(country.name),
                selectable_league_ids=tuple(
                    int(league.competition_id) for league in country.leagues
                ),
                allocation_ids=tuple(int(record.id) for record in country_rows),
                ranking_endpoint_ids=tuple(endpoints),
            )
        )

    return PlayableCountryAllocationPlan(
        catalog_sha256=scope.catalog_sha256,
        countries=tuple(country_plans),
        assigned_allocation_ids=tuple(assigned_ids),
        ignored_allocation_ids=tuple(ignored),
    )


def load_canonical_playable_country_allocation_plan(
    game_dir: str | Path,
) -> PlayableCountryAllocationPlan:
    """Verify canonical files, parse them once, and derive the country plan."""
    game_dir = Path(game_dir)
    verify_canonical_files(game_dir)
    database = FM2001Database(game_dir)
    scope = derive_original_playable_scope(database)
    return derive_playable_country_allocation_plan(
        scope,
        database.league_allocation_records,
        database.competitions,
    )
