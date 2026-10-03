"""Source-backed Gate-17 catalog of original TeamSelect-playable scope.

The original TeamSelect hierarchy is already recovered in
original_teamselect_native.py.  This module turns that presentation contract
into a deterministic release-audit catalog without hard-coding modern league
knowledge:

* the eight canonical TeamSelect countries come from the executable-recovered
  TEAMSELECT_ENGLISH_COUNTRY_ORDER;
* root League filtering and source ordering reuse native_competitions_for_country;
* club ordering reuses native_clubs_for_competition;
* the original 16 hierarchy controls and 24 club controls are respected;
* canonical-file loading first verifies the analyzed Master.dat / Static.dat /
  English.str / Core.str hashes.

No original game bytes are embedded here.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from fm2001_data import FM2001Database
from original_front_end_layout import (
    TEAMSELECT_CLUB_ROW_ORIGINS,
    TEAMSELECT_ENGLISH_COUNTRY_ORDER,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
)
from original_teamselect_native import (
    native_clubs_for_competition,
    native_competitions_for_country,
)
from verify import verify_canonical_files


CATALOG_SCHEMA_VERSION = 1
TEAMSELECT_COUNTRY_COUNT = len(TEAMSELECT_ENGLISH_COUNTRY_ORDER)
TEAMSELECT_MAX_VISIBLE_LEAGUES = (
    len(TEAMSELECT_HIERARCHY_ROW_ORIGINS) - TEAMSELECT_COUNTRY_COUNT
)
TEAMSELECT_MAX_VISIBLE_CLUBS = len(TEAMSELECT_CLUB_ROW_ORIGINS)


class Gate17PlayableScopeError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlayableLeagueScope:
    competition_id: int
    name: str
    source_club_count: int
    selectable_club_ids: tuple[int, ...]
    selectable_club_names: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "competition_id": int(self.competition_id),
            "name": self.name,
            "source_club_count": int(self.source_club_count),
            "selectable_club_count": len(self.selectable_club_ids),
            "selectable_club_ids": list(self.selectable_club_ids),
            "selectable_club_names": list(self.selectable_club_names),
            "club_rows_truncated": (
                int(self.source_club_count) > len(self.selectable_club_ids)
            ),
        }


@dataclass(frozen=True)
class PlayableCountryScope:
    country_id: int
    name: str
    source_root_league_count: int
    leagues: tuple[PlayableLeagueScope, ...]

    def as_dict(self) -> dict:
        return {
            "country_id": int(self.country_id),
            "name": self.name,
            "source_root_league_count": int(self.source_root_league_count),
            "selectable_league_count": len(self.leagues),
            "league_rows_truncated": (
                int(self.source_root_league_count) > len(self.leagues)
            ),
            "leagues": [league.as_dict() for league in self.leagues],
        }


@dataclass(frozen=True)
class OriginalPlayableScope:
    countries: tuple[PlayableCountryScope, ...]

    def _core_payload(self) -> dict:
        return {
            "schema_version": CATALOG_SCHEMA_VERSION,
            "source_contract": "original_teamselect",
            "country_count": len(self.countries),
            "hierarchy_control_count": len(TEAMSELECT_HIERARCHY_ROW_ORIGINS),
            "club_control_count": len(TEAMSELECT_CLUB_ROW_ORIGINS),
            "max_visible_leagues_per_country": TEAMSELECT_MAX_VISIBLE_LEAGUES,
            "max_visible_clubs_per_league": TEAMSELECT_MAX_VISIBLE_CLUBS,
            "selectable_league_count": sum(
                len(country.leagues) for country in self.countries
            ),
            "selectable_club_row_count": sum(
                len(league.selectable_club_ids)
                for country in self.countries
                for league in country.leagues
            ),
            "countries": [country.as_dict() for country in self.countries],
        }

    @property
    def catalog_sha256(self) -> str:
        encoded = json.dumps(
            self._core_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        return sha256(encoded).hexdigest()

    def as_dict(self) -> dict:
        payload = self._core_payload()
        payload["catalog_sha256"] = self.catalog_sha256
        return payload


def _country_map(countries: Iterable[object]) -> dict[int, object]:
    result: dict[int, object] = {}
    for country in countries:
        country_id = int(getattr(country, "id"))
        if country_id in result:
            raise Gate17PlayableScopeError(
                f"duplicate country ID in canonical database: {country_id}"
            )
        result[country_id] = country
    return result


def derive_original_playable_scope(database) -> OriginalPlayableScope:
    """Derive exactly what the recovered original TeamSelect can expose.

    Root League and club source lists are allowed to be larger than the visible
    control arrays because the original screen itself has fixed capacities.
    The catalog records both source counts and the exact visible/selectable
    prefix, making any truncation explicit instead of silently widening the UI.
    """

    countries_by_id = _country_map(database.countries)
    competition_source = tuple(database.competitions)
    club_source = tuple(database.clubs)
    output: list[PlayableCountryScope] = []

    for expected_country_id, expected_name in TEAMSELECT_ENGLISH_COUNTRY_ORDER:
        country = countries_by_id.get(int(expected_country_id))
        if country is None:
            raise Gate17PlayableScopeError(
                f"canonical TeamSelect country {expected_country_id} is missing"
            )
        actual_name = str(getattr(country, "name"))
        if actual_name != expected_name:
            raise Gate17PlayableScopeError(
                "canonical TeamSelect country name changed: "
                f"{expected_country_id} expected {expected_name!r}, "
                f"got {actual_name!r}"
            )

        source_leagues = native_competitions_for_country(
            competition_source,
            int(expected_country_id),
        )
        if not source_leagues:
            raise Gate17PlayableScopeError(
                f"TeamSelect country {expected_name} has no root League"
            )
        visible_leagues = source_leagues[:TEAMSELECT_MAX_VISIBLE_LEAGUES]

        leagues: list[PlayableLeagueScope] = []
        for competition in visible_leagues:
            competition_id = int(getattr(competition, "id"))
            name = str(getattr(competition, "name"))
            if not name:
                raise Gate17PlayableScopeError(
                    f"TeamSelect League {competition_id} has an empty caption"
                )

            source_clubs = native_clubs_for_competition(
                club_source,
                competition_id,
            )
            visible_clubs = source_clubs[:TEAMSELECT_MAX_VISIBLE_CLUBS]
            if not visible_clubs:
                raise Gate17PlayableScopeError(
                    f"TeamSelect League {competition_id} ({name}) has no selectable club"
                )

            club_ids = tuple(int(getattr(club, "index")) for club in visible_clubs)
            club_names = tuple(str(getattr(club, "name")) for club in visible_clubs)
            if len(club_ids) != len(set(club_ids)):
                raise Gate17PlayableScopeError(
                    f"TeamSelect League {competition_id} exposes duplicate club IDs"
                )
            if any(not value for value in club_names):
                raise Gate17PlayableScopeError(
                    f"TeamSelect League {competition_id} exposes an empty club caption"
                )

            leagues.append(
                PlayableLeagueScope(
                    competition_id=competition_id,
                    name=name,
                    source_club_count=len(source_clubs),
                    selectable_club_ids=club_ids,
                    selectable_club_names=club_names,
                )
            )

        output.append(
            PlayableCountryScope(
                country_id=int(expected_country_id),
                name=expected_name,
                source_root_league_count=len(source_leagues),
                leagues=tuple(leagues),
            )
        )

    scope = OriginalPlayableScope(tuple(output))
    if len(scope.countries) != TEAMSELECT_COUNTRY_COUNT:
        raise Gate17PlayableScopeError("TeamSelect country catalog is incomplete")
    return scope


def load_canonical_original_playable_scope(
    game_dir: str | Path,
) -> OriginalPlayableScope:
    """Verify canonical source files, parse them, and derive the catalog."""

    game_dir = Path(game_dir)
    verify_canonical_files(game_dir)
    return derive_original_playable_scope(FM2001Database(game_dir))


def write_catalog(scope: OriginalPlayableScope, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(scope.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit the source-backed FM2001 original TeamSelect playable scope."
    )
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    scope = load_canonical_original_playable_scope(args.game_dir)
    payload = scope.as_dict()
    if args.output is not None:
        write_catalog(scope, args.output)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
