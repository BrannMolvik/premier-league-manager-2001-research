"""Source-backed runtime-ownership plan for every TeamSelect League.

The original TeamSelect catalog tells us which country/League targets are
player-selectable. Parsed DBRCompetition fields tell us which schedule
container owns each target. This module joins those two facts without
materializing fixtures or changing gameplay state.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from fm2001_data import FM2001Database
from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    derive_original_playable_scope,
)
from verify import verify_canonical_files


class CompetitionSource(Protocol):
    id: int
    country_region_id: int
    runtime_kind_code: int
    schedule_container_code: int
    parent_competition_id: int | None


class Gate17PlayableLeagueRuntimePlanError(RuntimeError):
    pass


RUNTIME_FIXED_PRIMARY = "fixed_primary"
RUNTIME_PROCEDURAL_PRIMARY = "procedural_primary"
RUNTIME_PROCEDURAL_SECONDARY = "procedural_secondary"


@dataclass(frozen=True)
class PlayableLeagueRuntimeEntry:
    scope_id: str
    country_id: int
    country_name: str
    competition_id: int
    competition_name: str
    runtime_kind_code: int
    schedule_container_code: int
    runtime_owner: str
    source_club_count: int
    selectable_club_ids: tuple[int, ...]

    @property
    def uses_primary_container(self) -> bool:
        return self.runtime_owner in (
            RUNTIME_FIXED_PRIMARY,
            RUNTIME_PROCEDURAL_PRIMARY,
        )

    @property
    def uses_secondary_container(self) -> bool:
        return self.runtime_owner == RUNTIME_PROCEDURAL_SECONDARY

    def as_dict(self) -> dict:
        return {
            "scope_id": self.scope_id,
            "country_id": self.country_id,
            "country_name": self.country_name,
            "competition_id": self.competition_id,
            "competition_name": self.competition_name,
            "runtime_kind_code": self.runtime_kind_code,
            "schedule_container_code": self.schedule_container_code,
            "runtime_owner": self.runtime_owner,
            "source_club_count": self.source_club_count,
            "selectable_club_ids": list(self.selectable_club_ids),
            "uses_primary_container": self.uses_primary_container,
            "uses_secondary_container": self.uses_secondary_container,
        }


@dataclass(frozen=True)
class PlayableLeagueRuntimePlan:
    catalog_sha256: str
    entries: tuple[PlayableLeagueRuntimeEntry, ...]

    @property
    def primary_scope_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.scope_id for entry in self.entries
            if entry.uses_primary_container
        )

    @property
    def secondary_scope_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.scope_id for entry in self.entries
            if entry.uses_secondary_container
        )

    @property
    def fixed_primary_scope_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.scope_id for entry in self.entries
            if entry.runtime_owner == RUNTIME_FIXED_PRIMARY
        )

    @property
    def procedural_primary_scope_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.scope_id for entry in self.entries
            if entry.runtime_owner == RUNTIME_PROCEDURAL_PRIMARY
        )

    @property
    def procedural_primary_competition_ids(self) -> tuple[int, ...]:
        return tuple(
            int(entry.competition_id) for entry in self.entries
            if entry.runtime_owner == RUNTIME_PROCEDURAL_PRIMARY
        )

    @property
    def procedural_secondary_scope_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.scope_id for entry in self.entries
            if entry.runtime_owner == RUNTIME_PROCEDURAL_SECONDARY
        )

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "scope_entry_count": len(self.entries),
            "primary_scope_ids": list(self.primary_scope_ids),
            "secondary_scope_ids": list(self.secondary_scope_ids),
            "fixed_primary_scope_ids": list(self.fixed_primary_scope_ids),
            "procedural_primary_scope_ids": list(
                self.procedural_primary_scope_ids
            ),
            "procedural_primary_competition_ids": list(
                self.procedural_primary_competition_ids
            ),
            "procedural_secondary_scope_ids": list(
                self.procedural_secondary_scope_ids
            ),
            "entries": [entry.as_dict() for entry in self.entries],
        }


def derive_playable_league_runtime_plan(
    scope: OriginalPlayableScope,
    competitions: Iterable[CompetitionSource],
    *,
    fixed_fixture_competition_ids: Iterable[int] = (0,),
) -> PlayableLeagueRuntimePlan:
    """Join exact TeamSelect targets to their recovered runtime ownership."""
    if type(scope) is not OriginalPlayableScope:
        raise Gate17PlayableLeagueRuntimePlanError(
            "runtime plan requires exact OriginalPlayableScope"
        )

    competition_map: dict[int, CompetitionSource] = {}
    for competition in competitions:
        competition_id = int(competition.id)
        if competition_id in competition_map:
            raise Gate17PlayableLeagueRuntimePlanError(
                f"duplicate competition ID {competition_id}"
            )
        competition_map[competition_id] = competition

    fixed_ids: set[int] = set()
    for raw in fixed_fixture_competition_ids:
        if type(raw) is not int or raw < 0:
            raise Gate17PlayableLeagueRuntimePlanError(
                "fixed-fixture competition IDs must be exact non-negative integers"
            )
        if raw in fixed_ids:
            raise Gate17PlayableLeagueRuntimePlanError(
                f"duplicate fixed-fixture competition ID {raw}"
            )
        fixed_ids.add(raw)

    entries: list[PlayableLeagueRuntimeEntry] = []
    seen_scope_ids: set[str] = set()
    seen_competitions: set[int] = set()

    for country in scope.countries:
        country_id = int(country.country_id)
        for league in country.leagues:
            competition_id = int(league.competition_id)
            scope_id = f"{country_id}:{competition_id}"
            if scope_id in seen_scope_ids or competition_id in seen_competitions:
                raise Gate17PlayableLeagueRuntimePlanError(
                    f"duplicate playable League identity {scope_id}"
                )
            seen_scope_ids.add(scope_id)
            seen_competitions.add(competition_id)

            competition = competition_map.get(competition_id)
            if competition is None:
                raise Gate17PlayableLeagueRuntimePlanError(
                    f"playable League {scope_id} has no competition record"
                )
            if getattr(competition, "parent_competition_id", None) is not None:
                raise Gate17PlayableLeagueRuntimePlanError(
                    f"playable League {scope_id} is not a root competition"
                )
            if int(competition.country_region_id) != country_id:
                raise Gate17PlayableLeagueRuntimePlanError(
                    f"playable League {scope_id} country identity drifted"
                )
            runtime_kind = int(competition.runtime_kind_code)
            if runtime_kind != 1:
                raise Gate17PlayableLeagueRuntimePlanError(
                    f"playable League {scope_id} is no longer runtime kind 1"
                )

            container = int(competition.schedule_container_code)
            if competition_id in fixed_ids:
                if container in (2, 3):
                    raise Gate17PlayableLeagueRuntimePlanError(
                        f"fixed playable League {scope_id} belongs to secondary container"
                    )
                owner = RUNTIME_FIXED_PRIMARY
            elif container in (2, 3):
                owner = RUNTIME_PROCEDURAL_SECONDARY
            else:
                owner = RUNTIME_PROCEDURAL_PRIMARY

            entries.append(
                PlayableLeagueRuntimeEntry(
                    scope_id=scope_id,
                    country_id=country_id,
                    country_name=str(country.name),
                    competition_id=competition_id,
                    competition_name=str(league.name),
                    runtime_kind_code=runtime_kind,
                    schedule_container_code=container,
                    runtime_owner=owner,
                    source_club_count=int(league.source_club_count),
                    selectable_club_ids=tuple(
                        int(value) for value in league.selectable_club_ids
                    ),
                )
            )

    if not entries:
        raise Gate17PlayableLeagueRuntimePlanError(
            "TeamSelect catalog contains no playable League entries"
        )
    unknown_fixed = tuple(sorted(fixed_ids - seen_competitions))
    if unknown_fixed:
        raise Gate17PlayableLeagueRuntimePlanError(
            f"fixed-fixture IDs are not TeamSelect-playable Leagues: {unknown_fixed}"
        )

    return PlayableLeagueRuntimePlan(
        catalog_sha256=scope.catalog_sha256,
        entries=tuple(entries),
    )


def load_canonical_playable_league_runtime_plan(
    game_dir: str | Path,
    *,
    fixed_fixture_competition_ids: Iterable[int] = (0,),
) -> PlayableLeagueRuntimePlan:
    """Verify canonical sources, parse once, and derive the ownership plan."""
    game_dir = Path(game_dir)
    verify_canonical_files(game_dir)
    database = FM2001Database(game_dir)
    scope = derive_original_playable_scope(database)
    return derive_playable_league_runtime_plan(
        scope,
        database.competitions,
        fixed_fixture_competition_ids=fixed_fixture_competition_ids,
    )
