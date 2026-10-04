"""Fail-closed Gate-13 audit for PLeagueFixtures selector source data.

The eight country selectors are source-proven. Dynamic League radios are rebuilt
from the native DBRCountry competition array at +0x48/+0x4C after RTTI-casting
LeagueBase entries to League. Generic GameState competition-map iteration is not
evidence for that encounter order, so this module never uses it as a fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_COUNTRY_SELECTORS,
    LEAGUE_FIXTURES_LEAGUE_SELECTOR_COUNT,
    league_fixtures_country_selector_for_club_country,
    league_fixtures_league_selectors,
    league_fixtures_selected_league_index,
)


class LeagueFixturesSelectorSourceAuditError(RuntimeError):
    """Required selector source identity/order is absent or inconsistent."""


@dataclass(frozen=True)
class LeagueFixturesSelectorSourceAudit:
    country_selector_ids: tuple[int, ...]
    country_selector_events: tuple[int, ...]
    current_club_id: int
    current_country_id: int
    current_country_selector_index: int
    current_competition_id: int
    source_array_offset: int
    source_count_offset: int
    source_order_kind: str
    supplied_country_ids: tuple[int, ...]
    missing_country_ids: tuple[int, ...]
    current_country_league_ids: tuple[int, ...]
    current_country_league_captions: tuple[str, ...]
    current_country_selected_league_index: int | None
    current_country_league_events: tuple[int, ...]
    dynamic_league_order_available: bool
    ready_for_integrated_selector_state: bool
    blocker_codes: tuple[str, ...]


def _normalize_source_cast_leagues(
    value: Sequence[tuple[int, str]],
    *,
    country_id: int,
) -> tuple[tuple[int, str], ...]:
    normalized = tuple(value)
    if not normalized:
        raise LeagueFixturesSelectorSourceAuditError(
            f"country {country_id} source-cast League list is empty"
        )
    if len(normalized) > LEAGUE_FIXTURES_LEAGUE_SELECTOR_COUNT:
        raise LeagueFixturesSelectorSourceAuditError(
            f"country {country_id} exposes more than six source League selectors"
        )
    seen: set[int] = set()
    result: list[tuple[int, str]] = []
    for item in normalized:
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or type(item[0]) is not int
            or item[0] < 0
            or not isinstance(item[1], str)
            or not item[1]
        ):
            raise LeagueFixturesSelectorSourceAuditError(
                f"country {country_id} source League entries must be "
                "(non-negative identity, non-empty caption)"
            )
        identity, caption = item
        if identity in seen:
            raise LeagueFixturesSelectorSourceAuditError(
                f"country {country_id} source League identities are not unique"
            )
        seen.add(identity)
        result.append((identity, caption))
    return tuple(result)


def audit_league_fixtures_selector_source(
    controller,
    *,
    source_cast_leagues_by_country: Mapping[
        int, Sequence[tuple[int, str]]
    ] | None = None,
) -> LeagueFixturesSelectorSourceAudit:
    """Measure whether exact dynamic League-selector input is available.

    source_cast_leagues_by_country must already preserve the encounter order
    from DBRCountry +0x48/+0x4C after the recovered League RTTI cast/filter.
    No order is derived from state.competitions.
    """
    state = getattr(controller, "state", None)
    human = getattr(controller, "human", None)
    if state is None or human is None:
        raise LeagueFixturesSelectorSourceAuditError(
            "League Fixtures selector audit requires an active human game"
        )
    club_id = getattr(human, "club_id", None)
    if type(club_id) is not int:
        raise LeagueFixturesSelectorSourceAuditError("human club ID is unavailable")

    clubs = getattr(state, "clubs", None)
    if not hasattr(clubs, "get"):
        raise LeagueFixturesSelectorSourceAuditError("source club table is unavailable")
    club = clubs.get(club_id)
    if club is None:
        raise LeagueFixturesSelectorSourceAuditError(
            f"controlled club {club_id} is absent from the source club table"
        )
    country_id = getattr(club, "country_id", None)
    if type(country_id) is not int or country_id < 0:
        raise LeagueFixturesSelectorSourceAuditError(
            "controlled club source country ID is unavailable"
        )

    membership = getattr(state, "club_competition_membership", None)
    if not hasattr(membership, "get"):
        raise LeagueFixturesSelectorSourceAuditError(
            "live club competition membership is unavailable"
        )
    competition_id = membership.get(club_id)
    if type(competition_id) is not int or competition_id < 0:
        raise LeagueFixturesSelectorSourceAuditError(
            "controlled club live competition identity is unavailable"
        )

    try:
        country_selector = league_fixtures_country_selector_for_club_country(
            country_id
        )
    except Exception as exc:
        raise LeagueFixturesSelectorSourceAuditError(str(exc)) from exc

    selector_country_ids = tuple(
        int(selector.country_id)
        for selector in LEAGUE_FIXTURES_COUNTRY_SELECTORS
    )
    selector_events = tuple(
        int(selector.event_id)
        for selector in LEAGUE_FIXTURES_COUNTRY_SELECTORS
    )

    if source_cast_leagues_by_country is None:
        supplied_country_ids: tuple[int, ...] = ()
        missing_country_ids = selector_country_ids
        current_entries: tuple[tuple[int, str], ...] = ()
        selected_index = None
        current_events: tuple[int, ...] = ()
        blockers = ("dbrcountry_competition_array_order_unmaterialized",)
        dynamic_available = False
        ready = False
    else:
        if not isinstance(source_cast_leagues_by_country, Mapping):
            raise LeagueFixturesSelectorSourceAuditError(
                "source_cast_leagues_by_country must be a mapping"
            )
        supplied_keys = tuple(source_cast_leagues_by_country.keys())
        if any(type(value) is not int for value in supplied_keys):
            raise LeagueFixturesSelectorSourceAuditError(
                "source country mapping keys must be integer country IDs"
            )
        extras = tuple(
            value for value in supplied_keys if value not in selector_country_ids
        )
        if extras:
            raise LeagueFixturesSelectorSourceAuditError(
                "source League mapping contains non-selector countries: "
                + ",".join(str(value) for value in extras)
            )

        supplied_country_ids = tuple(
            country for country in selector_country_ids
            if country in source_cast_leagues_by_country
        )
        missing_country_ids = tuple(
            country for country in selector_country_ids
            if country not in source_cast_leagues_by_country
        )
        normalized_by_country = {
            country: _normalize_source_cast_leagues(
                source_cast_leagues_by_country[country],
                country_id=country,
            )
            for country in supplied_country_ids
        }
        current_entries = normalized_by_country.get(country_id, ())
        if current_entries:
            try:
                selected_index = league_fixtures_selected_league_index(
                    competition_id,
                    tuple(identity for identity, _caption in current_entries),
                )
                current_selectors = league_fixtures_league_selectors(
                    current_entries,
                    selected_index=selected_index,
                )
            except Exception as exc:
                raise LeagueFixturesSelectorSourceAuditError(str(exc)) from exc
            current_events = tuple(
                int(selector.event_id) for selector in current_selectors
            )
        else:
            selected_index = None
            current_events = ()

        dynamic_available = not missing_country_ids
        blockers_list: list[str] = []
        if missing_country_ids:
            blockers_list.append(
                "dbrcountry_competition_array_order_incomplete"
            )
        if not current_entries:
            blockers_list.append("current_country_league_array_missing")
        blockers = tuple(blockers_list)
        ready = (
            dynamic_available
            and bool(current_entries)
            and selected_index is not None
            and not blockers
        )

    return LeagueFixturesSelectorSourceAudit(
        country_selector_ids=selector_country_ids,
        country_selector_events=selector_events,
        current_club_id=int(club_id),
        current_country_id=int(country_id),
        current_country_selector_index=int(country_selector.index),
        current_competition_id=int(competition_id),
        source_array_offset=0x48,
        source_count_offset=0x4C,
        source_order_kind=(
            "native_dbrcountry_competition_array_after_league_rtti_cast"
        ),
        supplied_country_ids=supplied_country_ids,
        missing_country_ids=missing_country_ids,
        current_country_league_ids=tuple(
            identity for identity, _caption in current_entries
        ),
        current_country_league_captions=tuple(
            caption for _identity, caption in current_entries
        ),
        current_country_selected_league_index=selected_index,
        current_country_league_events=current_events,
        dynamic_league_order_available=dynamic_available,
        ready_for_integrated_selector_state=ready,
        blocker_codes=blockers,
    )
