"""Source-bounded country/League identity owner for the original PLeagueFixtures.

This is NOT a substitute for the original prepared-member vector (0x4F4940),
373-head fixture-chain order, date/status filters, control hit rectangles or
rendered GUI. It is an independent, immutable selector state over canonical
DBRClub and DBRCompetition metadata. Recovery507 original constructor
0x46D5FC..0x46D60C proves all eight per-country selection slots start at zero;
0x46B01F..0x46B028 replaces the managed club's slot with its actual League.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Mapping

from competition_startup import country_league_root_storage_order
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_COUNTRY_SELECTORS,
    LeagueFixturesLeagueSelector,
    league_fixtures_country_selector_for_club_country,
    league_fixtures_league_selectors,
    league_fixtures_selected_league_index,
    league_fixtures_selector_event,
)


class LeagueFixturesSelectorContextError(ValueError):
    """Selected original country/League identity is not source-qualified."""


@dataclass(frozen=True)
class LeagueFixturesSelectionContext:
    """Original +0x64 active country and +0x68[8] per-country indexes.

    Native constructor 0x46D5FC writes eight zero indexes, then current-club
    0x46B028 replaces only the active country's index. Other countries start
    at their first source League until the user selects another radio.
    Stored competition IDs are original DBRCompetition identities. Display
    captions are canonical English.str/Static.dat names, whose equality to
    the native League+0x14 runtime captions still needs a separate check.
    """

    active_country_index: int
    selected_league_indices: tuple[int, ...]
    league_candidates: tuple[tuple[tuple[int, str], ...], ...]

    @property
    def active_country_id(self) -> int:
        return LEAGUE_FIXTURES_COUNTRY_SELECTORS[self.active_country_index].country_id

    @property
    def selected_competition_id(self) -> int:
        selected = self.selected_league_indices[self.active_country_index]
        return self.league_candidates[self.active_country_index][selected][0]

    def active_league_radios(self) -> tuple[LeagueFixturesLeagueSelector, ...]:
        selected = self.selected_league_indices[self.active_country_index]
        return league_fixtures_league_selectors(
            self.league_candidates[self.active_country_index],
            selected_index=selected,
        )

    def accept_native_radio_event(self, event_id: int) -> "LeagueFixturesSelectionContext":
        """Only events 1..8 and 9..14; reject absent radios transactionally."""
        try:
            kind, index = league_fixtures_selector_event(event_id)
        except ValueError as exc:
            raise LeagueFixturesSelectorContextError(str(exc)) from exc
        if kind == "country":
            if not self.league_candidates[index]:
                raise LeagueFixturesSelectorContextError(
                    "Country has no original League radio candidate"
                )
            return replace(self, active_country_index=index)

        country = self.active_country_index
        if index >= len(self.league_candidates[country]):
            raise LeagueFixturesSelectorContextError(
                "League event refers to an unconstructed original radio"
            )
        updated = list(self.selected_league_indices)
        updated[country] = index
        return replace(self, selected_league_indices=tuple(updated))


def build_league_fixtures_selection_context(
    *,
    club_id: int,
    clubs: Mapping[int, object],
    membership: Mapping[int, int],
    competitions: Iterable[object],
) -> LeagueFixturesSelectionContext:
    """Resolve the selected human's ORIGINAL country and League identity.

    Eligible option candidates are original root runtime League kind 1 in the
    already-recovered country +0x48 ordering (0x4F79D0), never DummyLeague
    kind 3 and never a root-Cup or alternate-country competition. This seam
    does not claim native RTTI/caption proof or permission to build fixtures
    for an unverified competition.
    """
    if type(club_id) is not int or club_id < 0:
        raise LeagueFixturesSelectorContextError("Human club ID must be canonical")
    club = clubs.get(club_id)
    if club is None:
        raise LeagueFixturesSelectorContextError("Human club is unavailable")
    country_id = getattr(club, "country_id", None)
    if type(country_id) is not int:
        raise LeagueFixturesSelectorContextError("Human club source country is missing")
    try:
        current_country = league_fixtures_country_selector_for_club_country(country_id)
    except ValueError as exc:
        raise LeagueFixturesSelectorContextError(str(exc)) from exc
    competition_id = membership.get(club_id)
    if type(competition_id) is not int or competition_id < 0:
        raise LeagueFixturesSelectorContextError("Current human club League is missing")

    definitions = tuple(competitions)
    identities: set[int] = set()
    for competition in definitions:
        identity = getattr(competition, "id", None)
        if type(identity) is not int or identity < 0 or identity in identities:
            raise LeagueFixturesSelectorContextError(
                "Competition identities must be distinct source integers"
            )
        identities.add(identity)

    country_rows: list[tuple[tuple[int, str], ...]] = []
    for country in LEAGUE_FIXTURES_COUNTRY_SELECTORS:
        roots = country_league_root_storage_order(
            definitions, country.country_id
        )
        rows = []
        for competition in roots:
            if getattr(competition, "runtime_kind_code", None) != 1:
                continue  # Native LeagueBase -> League cast excludes DummyLeague.
            name = getattr(competition, "name", None)
            if not isinstance(name, str) or not name:
                raise LeagueFixturesSelectorContextError(
                    "League source caption is unavailable"
                )
            rows.append((int(competition.id), name))
        if not 1 <= len(rows) <= 6:
            raise LeagueFixturesSelectorContextError(
                "Country has no League candidates or exceeds six native radios"
            )
        country_rows.append(tuple(rows))

    # Original PLeagueFixtures constructor: xor eax,eax; ecx=8;
    # lea edi,[panel+0x68]; rep stosd (0x46D5FC..0x46D60C).
    # The managed club's native League index overwrites only its country.
    selected: list[int] = [0] * len(LEAGUE_FIXTURES_COUNTRY_SELECTORS)
    try:
        selected[current_country.index] = league_fixtures_selected_league_index(
            competition_id,
            [identity for identity, _caption in country_rows[current_country.index]],
        )
    except ValueError as exc:
        raise LeagueFixturesSelectorContextError(
            "Human club's current League is absent from its original country list"
        ) from exc
    return LeagueFixturesSelectionContext(
        active_country_index=current_country.index,
        selected_league_indices=tuple(selected),
        league_candidates=tuple(country_rows),
    )
