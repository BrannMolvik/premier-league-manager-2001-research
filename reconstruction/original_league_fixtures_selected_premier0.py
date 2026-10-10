"""Exact native 373-head selected original Premier League0 fixed-fixture grid.

PLeagueFixtures::0x46D950 scans the global primary schedule's 373 heads,
not modern PremierLeagueState.fixture_source_order. This is the DISTINCT
fixed-League source path for selecting England DIVISION0 while managing a
different country/League, with actual fixed fixture IDs and live scores.
No fabricated dates, pointer hit acceptance or match-report capture link.
"""
from __future__ import annotations

from datetime import date
from typing import Mapping

from competition_state import PremierLeagueState
from original_league_fixtures_primary_live import (
    SourcePrimaryLeagueFixture, SourcePrimaryLeagueFixtures,
)
from original_league_fixtures_resources import (
    league_fixture_matrix_accepts_candidate,
    league_fixture_first_free_repeat_slot,
)
from original_league_fixtures_selector_context import (
    LeagueFixturesSelectionContext, LeagueFixturesSelectorContextError,
    build_league_fixtures_selection_context,
)


class SelectedPremier0FixturesSourceError(ValueError):
    """Actual Premier0 primary fixture-chain data is incomplete or unauthenticated."""


def selected_original_premier0_primary_fixtures(
    *,
    human_club_id: int,
    selection: LeagueFixturesSelectionContext,
    clubs: Mapping[int, object],
    membership: Mapping[int, int],
    competitions: Mapping[int, object],
    premier_league: object,
    days: Mapping[date, tuple[object, ...]],
) -> SourcePrimaryLeagueFixtures:
    """Return genuine original Premier0 primary encounter order, fail closed.

    The original selected League radio is independent of the current manager.
    Numeric IDs are accepted ONLY for original fixed fixture nodes linked to
    the exact present PremierLeagueState fixture, not synthesized for unrelated
    procedural node tokens or PMatchInfo report pointers.
    """
    if type(selection) is not LeagueFixturesSelectionContext:
        raise SelectedPremier0FixturesSourceError("Original League selector is missing")
    try:
        authenticated = build_league_fixtures_selection_context(
            club_id=human_club_id, clubs=clubs, membership=membership,
            competitions=competitions.values(),
        )
    except (LeagueFixturesSelectorContextError, AttributeError, TypeError) as exc:
        raise SelectedPremier0FixturesSourceError(
            "Current human League selector source is unavailable"
        ) from exc
    if (selection.league_candidates != authenticated.league_candidates
            or type(selection.active_country_index) is not int
            or selection.active_country_index != 0
            or type(selection.selected_league_indices) is not tuple
            or len(selection.selected_league_indices) != 8):
        raise SelectedPremier0FixturesSourceError(
            "England first-League radio is not an authenticated native selection"
        )
    for country_index, index in enumerate(selection.selected_league_indices):
        if (type(index) is not int or not 0 <= index < len(
                authenticated.league_candidates[country_index])):
            raise SelectedPremier0FixturesSourceError(
                "Native radio index points outside constructed country League roots"
            )
    if (selection.selected_league_indices[0] != 0
            or selection.active_country_id != 26
            or selection.selected_competition_id != 0):
        raise SelectedPremier0FixturesSourceError(
            "Selected original League is not England Premier League0"
        )
    original = competitions.get(0)
    if (original is None
            or getattr(original, "runtime_kind_code", None) != 1
            or getattr(original, "parent_competition_id", object()) is not None
            or getattr(original, "country_region_id", None) != 26
            or getattr(original, "scheduled_matchday_count", None) != 38):
        raise SelectedPremier0FixturesSourceError(
            "Canonical 20-club Premier0 38-matchday source root is unavailable"
        )
    if type(premier_league) is not PremierLeagueState:
        raise SelectedPremier0FixturesSourceError(
            "Premier0 live fixed/annual fixture and results owner is missing"
        )
    member_ids = getattr(premier_league, "club_ids", None)
    fixtures = getattr(premier_league, "fixtures", None)
    results = getattr(premier_league, "results", None)
    if (type(member_ids) is not tuple or len(member_ids) != 20
            or len(set(member_ids)) != 20
            or any(type(cid) is not int or cid < 0 for cid in member_ids)
            or not hasattr(fixtures, "items") or len(fixtures) != 380
            or not hasattr(results, "get")):
        raise SelectedPremier0FixturesSourceError(
            "Premier0 full 20-club /380-fixture source identity is incomplete"
        )
    members = set(member_ids)
    actual_members = {cid for cid, comp in membership.items()
                      if type(cid) is int and type(comp) is int and comp == 0}
    if actual_members != members:
        raise SelectedPremier0FixturesSourceError(
            "Premier0 live clubs disagree with source DBRClub League membership"
        )
    names = {}
    for cid in member_ids:
        club = clubs.get(cid)
        text = getattr(club, "short_name", None)
        if (getattr(club, "country_id", None) != 26
                or not isinstance(text, str) or not text):
            raise SelectedPremier0FixturesSourceError(
                "Premier0 original club short-name/country is missing"
            )
        try:
            names[cid] = text.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise SelectedPremier0FixturesSourceError(
                "Premier0 club name is not canonical source CP1252"
            ) from exc
    try:
        ordered_members = tuple(int(row.club_id)
                                for row in premier_league.table(names.get))
    except (ValueError, KeyError) as exc:
        raise SelectedPremier0FixturesSourceError(
            "Native League::0x4F45E0 prepared member order is ambiguous"
        ) from exc
    if set(ordered_members) != members or len(ordered_members) != 20:
        raise SelectedPremier0FixturesSourceError(
            "Premier0 original native sorted member set is incomplete"
        )
    directed = []
    for fid, fixture in fixtures.items():
        h, a = getattr(fixture, "home_club_id", None), getattr(fixture, "away_club_id", None)
        if (type(fid) is not int or fid < 0 or type(h) is not int
                or type(a) is not int or h == a
                or h not in members or a not in members):
            raise SelectedPremier0FixturesSourceError(
                "Fixed Premier0 source fixture ID or clubs are invalid"
            )
        directed.append((h, a))
    if len(set(directed)) != 380:
        raise SelectedPremier0FixturesSourceError(
            "Premier0 fixed fixture IDs do not form a real directed double round robin"
        )
    if not hasattr(days, "items") or len(days) > 373:
        raise SelectedPremier0FixturesSourceError(
            "Original 373-head primary schedule source is missing"
        )
    head_days = tuple(days)
    if (any(type(day) is not date for day in head_days)
            or any(type(items) is not tuple for items in days.values())):
        raise SelectedPremier0FixturesSourceError(
            "Original primary head dates or linked node ordering are invalid"
        )
    indexed = {cid: idx for idx, cid in enumerate(ordered_members)}
    slots = [False] * (20 * 20)
    encountered: set[int] = set()
    ordered: list[SourcePrimaryLeagueFixture] = []
    native_index = 0
    # The source 0x46D950 scans day buckets ascending, head-to-tail per day.
    for day in sorted(head_days):
        for entry in days[day]:
            if (getattr(entry, "competition_id", None) != 0
                    or getattr(entry, "competition_context", None) != 0):
                native_index += 1
                continue
            node = getattr(entry, "node_token", None)
            if (getattr(entry, "node_kind", None) != "fixed_league_match"
                    or type(node) is not tuple or len(node) != 4
                    or node[:3] != ("fixed_league_match", 0, 0)
                    or type(node[3]) is not int
                    or node[3] not in fixtures or node[3] in encountered):
                raise SelectedPremier0FixturesSourceError(
                    "Premier0 primary fixed fixture source token is missing or duplicated"
                )
            fixture_id = node[3]
            encountered.add(fixture_id)
            fixture = fixtures[fixture_id]
            home, away = fixture.home_club_id, fixture.away_club_id
            cache = getattr(entry, "side_club_cache", None)
            if cache is not None and cache != (home, away):
                raise SelectedPremier0FixturesSourceError(
                    "Premier0 fixed fixture participant cache disagrees with source"
                )
            bits = getattr(entry, "payload_filter_bits", None)
            if type(bits) is not int or bits < 0 or bits & ~0x61:
                raise SelectedPremier0FixturesSourceError(
                    "Premier0 original fixture status +0x44 is unknown"
                )
            if league_fixture_matrix_accepts_candidate(
                kind_code=1, fixture_competition_identity=0,
                selected_competition_identity=0, fixture_status_bits=bits,
                left_club_identity=home, right_club_identity=away,
            ):
                try:
                    slot = league_fixture_first_free_repeat_slot(
                        slots, club_count=20, left_member_index=indexed[home],
                        right_member_index=indexed[away], layer_count=1,
                    )
                except ValueError as exc:
                    raise SelectedPremier0FixturesSourceError(
                        "Premier0 matrix has duplicate original directed fixture cell"
                    ) from exc
                slots[slot] = True
                result = results.get(fixture_id)
                goals = None if result is None else (
                    getattr(result, "home_goals", None),
                    getattr(result, "away_goals", None),
                )
                if goals is not None and any(
                    type(goal) is not int or goal < 0 for goal in goals
                ):
                    raise SelectedPremier0FixturesSourceError(
                        "Premier0 live recorded result has invalid goals"
                    )
                ordered.append(SourcePrimaryLeagueFixture(
                    node_token=node, native_encounter_index=native_index,
                    scheduled_date=day, home_club_id=home, away_club_id=away,
                    played=goals is not None,
                    home_goals=None if goals is None else goals[0],
                    away_goals=None if goals is None else goals[1],
                ))
            native_index += 1
    if encountered != set(fixtures):
        raise SelectedPremier0FixturesSourceError(
            "Native primary 373-head chain omits original Premier0 fixed fixture IDs"
        )
    return SourcePrimaryLeagueFixtures(
        competition_id=0, member_club_ids=ordered_members,
        scheduled_matchday_count=38, schedule_cycle_count=2,
        matrix_layer_count=1, fixtures_in_source_order=tuple(ordered),
    )
