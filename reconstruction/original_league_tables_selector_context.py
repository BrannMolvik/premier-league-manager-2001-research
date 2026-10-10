"""Source-owned PLeagueTables country8 / DIVISION5 / sort0-1 selection.

Unlike PLeagueFixtures, original PLeagueTables panel+0x68 stores ONE selected
division index, not eight per-country indices. This is a non-pointer source
event/state owner. Sort state1 is retained but is NOT permission to invent
0x4F4A10 Current Form rows.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Mapping

from competition_startup import country_league_root_storage_order
from original_league_tables_resources import LEAGUE_TABLES_COUNTRY_IDS


class OriginalLeagueTablesSelectorError(ValueError):
    """Original table country/DIVISION/sort source is unavailable."""


@dataclass(frozen=True)
class OriginalLeagueTablesSelectionContext:
    active_country_index: int
    selected_division_index: int
    sort_state: int
    division_candidates: tuple[tuple[tuple[int, str], ...], ...]
    human_country_index: int
    human_competition_id: int

    @property
    def active_country_id(self) -> int:
        return LEAGUE_TABLES_COUNTRY_IDS[self.active_country_index]

    @property
    def selected_competition_id(self) -> int:
        return self.division_candidates[self.active_country_index][
            self.selected_division_index
        ][0]

    def accept_native_radio_event(self, event_id: int) -> "OriginalLeagueTablesSelectionContext":
        """Source event1..8 country, 9..13 DIVISION, 14/15 sort; not a Tk click."""
        if type(event_id) is not int or not 1 <= event_id <= 15:
            raise OriginalLeagueTablesSelectorError("Original table event must be 1..15")
        if event_id <= 8:
            country = event_id - 1
            options = self.division_candidates[country]
            if not options:
                raise OriginalLeagueTablesSelectorError(
                    "Country has no constructed original DIVISION radio"
                )
            own = (next((i for i, (cid, _) in enumerate(options)
                         if cid == self.human_competition_id), 0)
                   if country == self.human_country_index else 0)
            return replace(self, active_country_index=country,
                           selected_division_index=own)
        if event_id <= 13:
            division = event_id - 9
            if division >= len(self.division_candidates[self.active_country_index]):
                raise OriginalLeagueTablesSelectorError(
                    "DIVISION event refers to an unconstructed original radio"
                )
            return replace(self, selected_division_index=division)
        return replace(self, sort_state=event_id - 14)


def build_original_league_tables_selection_context(
    *,
    human_club_id: int,
    clubs: Mapping[int, object],
    membership: Mapping[int, int],
    competitions: Iterable[object],
) -> OriginalLeagueTablesSelectionContext:
    """Use only source DBRCountry +0x48 League roots, never DummyLeague/Cups."""
    if type(human_club_id) is not int or human_club_id < 0:
        raise OriginalLeagueTablesSelectorError("Human club ID must be a source integer")
    club = clubs.get(human_club_id)
    country_id = getattr(club, "country_id", None)
    source_competition = membership.get(human_club_id)
    if (type(country_id) is not int or country_id not in LEAGUE_TABLES_COUNTRY_IDS
            or type(source_competition) is not int or source_competition < 0):
        raise OriginalLeagueTablesSelectorError(
            "Original human club country/current League identity unavailable"
        )
    source_country_index = LEAGUE_TABLES_COUNTRY_IDS.index(country_id)
    defs = tuple(competitions)
    ids = [getattr(c, "id", None) for c in defs]
    if (any(type(cid) is not int or cid < 0 for cid in ids)
            or len(ids) != len(set(ids))):
        raise OriginalLeagueTablesSelectorError(
            "Source table competition identities must be unique canonical integers"
        )
    candidates = []
    for country in LEAGUE_TABLES_COUNTRY_IDS:
        roots = country_league_root_storage_order(defs, country)
        rows = []
        for root in roots:
            if getattr(root, "runtime_kind_code", None) != 1:
                continue
            label = getattr(root, "name", None)
            if not isinstance(label, str) or not label:
                raise OriginalLeagueTablesSelectorError(
                    "Original selected DIVISION caption is missing"
                )
            rows.append((root.id, label))
        if not 1 <= len(rows) <= 5:
            raise OriginalLeagueTablesSelectorError(
                "Original country has no League or exceeds five DIVISION radios"
            )
        candidates.append(tuple(rows))
    chosen = candidates[source_country_index]
    if source_competition not in [cid for cid, _ in chosen]:
        raise OriginalLeagueTablesSelectorError(
            "Human club original League is outside its constructed DIVISION radios"
        )
    return OriginalLeagueTablesSelectionContext(
        active_country_index=source_country_index,
        selected_division_index=next(i for i,(cid,_) in enumerate(chosen)
                                     if cid == source_competition),
        sort_state=0,
        division_candidates=tuple(candidates),
        human_country_index=source_country_index,
        human_competition_id=source_competition,
    )
