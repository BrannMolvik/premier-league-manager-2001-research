"""Strict original fixed/annual Premier0 selector and 373-head fixture source.

Non-pointer data producer only. A native radio coordinate is not a click.
No invented alternate-manager data, score, original PMatchInfo link or date.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from competition_state import PremierLeagueState
from original_league_fixtures_resources import (
    league_fixture_first_free_repeat_slot,
    league_fixture_matrix_accepts_candidate,
)
from original_league_fixtures_selector_context import (
    LeagueFixturesSelectionContext,
    LeagueFixturesSelectorContextError,
    build_league_fixtures_selection_context,
)


class SourceSelectedPremierFixturesError(ValueError):
    """Original fixed Premier0 selected-League source could not be certified."""


@dataclass(frozen=True)
class SourceSelectedPremierFixture:
    native_encounter_index: int
    fixture_id: int
    node_token: tuple
    round_index: int
    scheduled_date: date
    home_club_id: int
    away_club_id: int
    played: bool
    home_goals: int | None
    away_goals: int | None


@dataclass(frozen=True)
class SourceSelectedPremierFixtures:
    competition_id: int
    member_club_ids: tuple[int, ...]
    scheduled_matchday_count: int
    schedule_cycle_count: int
    matrix_layer_count: int
    fixtures_in_source_order: tuple[SourceSelectedPremierFixture, ...]


def source_qualified_selected_premier0_league_fixtures(
    *, human_club_id: int, selection: LeagueFixturesSelectionContext,
    clubs: Mapping[int, object], membership: Mapping[int, int],
    competitions: Mapping[int, object], premier_league: object,
    days: Mapping[date, tuple[object, ...]],
) -> SourceSelectedPremierFixtures:
    """Read only source-complete Premier0 fixtures in original bucket order.

    PLeagueFixtures::0x46D950 scans 373 buckets head-to-tail, accepts source
    kind 1, selected League pointer, two resolved clubs, not status bit 0x20.
    League::0x4F4940 uses exact source qsort 0x4F45E0 for member order.
    This uses no guess about a GUI radio hit, conditional rescheduling or
    an unavailable original PMatchInfo +0x40 report pointer.
    """
    if type(selection) is not LeagueFixturesSelectionContext:
        raise SourceSelectedPremierFixturesError("Original radio selection type is unavailable")
    if not (hasattr(clubs, "get") and hasattr(membership, "items")
            and hasattr(competitions, "get") and hasattr(competitions, "values")):
        raise SourceSelectedPremierFixturesError("Original club/source definition data missing")
    try:
        initial = build_league_fixtures_selection_context(
            club_id=human_club_id, clubs=clubs, membership=membership,
            competitions=competitions.values(),
        )
    except (LeagueFixturesSelectorContextError, AttributeError, TypeError) as exc:
        raise SourceSelectedPremierFixturesError(
            "Original current human League selector is unauthenticated") from exc
    if (selection.league_candidates != initial.league_candidates
            or type(selection.active_country_index) is not int
            or selection.active_country_index != 0
            or type(selection.selected_league_indices) is not tuple
            or len(selection.selected_league_indices) != 8
            or any(type(v) is not int or not 0 <= v < len(
                initial.league_candidates[i]
            ) for i, v in enumerate(selection.selected_league_indices))
            or selection.selected_league_indices[0] != 0
            or selection.selected_competition_id != 0
            or selection.active_country_id != 26):
        raise SourceSelectedPremierFixturesError(
            "Selected England Premier0 native radio state is unauthenticated")
    definition = competitions.get(0)
    if (definition is None
            or getattr(definition, "runtime_kind_code", None) != 1
            or getattr(definition, "parent_competition_id", object()) is not None
            or getattr(definition, "country_region_id", None) != 26
            or getattr(definition, "scheduled_matchday_count", None) != 38):
        raise SourceSelectedPremierFixturesError(
            "Source Premier0 root League does not have 38 matchdays")
    league = premier_league
    if type(league) is not PremierLeagueState:
        raise SourceSelectedPremierFixturesError(
            "Distinct fixed/annual Premier0 live fixture owner is unavailable")
    members = getattr(league, "club_ids", None)
    ids = getattr(league, "fixture_source_order", None)
    fixtures = getattr(league, "fixtures", None)
    results = getattr(league, "results", None)
    if (type(members) is not tuple or len(members) != 20
            or len(set(members)) != 20
            or any(type(cid) is not int or cid < 0 for cid in members)
            or type(ids) is not tuple or len(ids) != 380
            or any(type(fid) is not int for fid in ids)
            or len(set(ids)) != 380
            or not hasattr(fixtures, "get") or set(fixtures) != set(ids)
            or not hasattr(results, "get") or not set(results).issubset(set(ids))):
        raise SourceSelectedPremierFixturesError(
            "Premier0 requires exactly 20 live members and 380 source fixture IDs")
    membership_ids = {
        cid for cid, comp in membership.items()
        if type(cid) is int and type(comp) is int and comp == 0
    }
    if membership_ids != set(members):
        raise SourceSelectedPremierFixturesError(
            "Fixed Premier0 members disagree with current DBRClub memberships")
    names = {}
    for cid in members:
        club = clubs.get(cid)
        value = getattr(club, "short_name", None)
        if (getattr(club, "country_id", None) != 26
                or not isinstance(value, str) or not value):
            raise SourceSelectedPremierFixturesError(
                "Premier0 member lacks canonical English short-name identity")
        try:
            names[cid] = value.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise SourceSelectedPremierFixturesError(
                "Original Premier0 name sort key is not CP1252") from exc
    if len(set(names.values())) != 20:
        raise SourceSelectedPremierFixturesError(
            "Original Premier0 short-name keys are ambiguous")
    try:
        ranked = tuple(league.table(names.get))
    except (ValueError, KeyError) as exc:
        raise SourceSelectedPremierFixturesError(
            "Original ranking requires unique full CP1252 source keys") from exc
    ranked_ids = tuple(getattr(row, "club_id", None) for row in ranked)
    if len(ranked_ids) != 20 or set(ranked_ids) != set(members):
        raise SourceSelectedPremierFixturesError(
            "Original prepared Premier0 member ranking is incomplete")
    pairs = []
    for fid in ids:
        fixture = fixtures[fid]
        h = getattr(fixture, "home_club_id", None)
        a = getattr(fixture, "away_club_id", None)
        rd = getattr(fixture, "round_index", None)
        if (type(h) is not int or type(a) is not int or h == a
                or h not in members or a not in members
                or type(rd) is not int or not 0 <= rd < 38):
            raise SourceSelectedPremierFixturesError(
                "Premier0 fixture side or round is not source-qualified")
        pairs.append((h, a))
    if len(set(pairs)) != 380:
        raise SourceSelectedPremierFixturesError(
            "Premier0 fixed owner is not a complete home/away League season")
    if not hasattr(days, "items"):
        raise SourceSelectedPremierFixturesError(
            "Original primary fixture bucket source is unavailable")
    keys = tuple(days)
    if len(keys) > 373 or any(type(value) is not date for value in keys):
        raise SourceSelectedPremierFixturesError(
            "Original primary fixture buckets exceed native 373-day capacity")
    ordered_days = tuple(sorted(keys))
    row_index = {cid: index for index, cid in enumerate(ranked_ids)}
    occupied = [False] * 400
    seen_ids: set[int] = set()
    seen_tokens: set[tuple] = set()
    rows = []
    encounter = 0
    for on_date in ordered_days:
        bucket = days[on_date]
        if type(bucket) is not tuple:
            raise SourceSelectedPremierFixturesError(
                "Original primary bucket no longer has linked head-to-tail order")
        for entry in bucket:
            if getattr(entry, "competition_id", None) != 0:
                encounter += 1
                continue
            if (getattr(entry, "node_kind", None) != "fixed_league_match"
                    or getattr(entry, "competition_context", None) != 0):
                raise SourceSelectedPremierFixturesError(
                    "Selected Premier0 bucket has unexpected fixture kind/context")
            token = getattr(entry, "node_token", None)
            if (type(token) is not tuple or len(token) != 4
                    or token in seen_tokens or type(token[-1]) is not int
                    or token[-1] not in fixtures):
                raise SourceSelectedPremierFixturesError(
                    "Selected native fixed fixture token is missing or duplicated")
            fid = token[-1]
            if fid in seen_ids:
                raise SourceSelectedPremierFixturesError(
                    "Duplicate fixed Premier0 source fixture in the primary calendar")
            seen_ids.add(fid)
            seen_tokens.add(token)
            fixture = fixtures[fid]
            home, away = fixture.home_club_id, fixture.away_club_id
            refs = (getattr(entry, "participant_0_ref", None),
                    getattr(entry, "participant_1_ref", None))
            direct = tuple(getattr(ref, "direct_club_id", None) for ref in refs)
            cache = getattr(entry, "side_club_cache", None)
            if direct != (home, away) or cache not in (None, (home, away)):
                raise SourceSelectedPremierFixturesError(
                    "Original fixture Side pointers disagree with fixed live owner")
            bits = getattr(entry, "payload_filter_bits", None)
            if type(bits) is not int or bits < 0 or bits & ~0x61:
                raise SourceSelectedPremierFixturesError(
                    "Original Premier0 fixture status bits are not verified")
            if league_fixture_matrix_accepts_candidate(
                kind_code=1, fixture_competition_identity=0,
                selected_competition_identity=0, fixture_status_bits=bits,
                left_club_identity=home, right_club_identity=away,
            ):
                try:
                    slot = league_fixture_first_free_repeat_slot(
                        occupied, club_count=20,
                        left_member_index=row_index[home],
                        right_member_index=row_index[away], layer_count=1,
                    )
                except ValueError as exc:
                    raise SourceSelectedPremierFixturesError(
                        "Original Premier0 directed-pair matrix layer exhausted") from exc
                occupied[slot] = True
                result = results.get(fid)
                if result is None:
                    hg = ag = None
                else:
                    hg = getattr(result, "home_goals", None)
                    ag = getattr(result, "away_goals", None)
                    if (getattr(result, "fixture_id", None) != fid
                            or type(hg) is not int or hg < 0
                            or type(ag) is not int or ag < 0):
                        raise SourceSelectedPremierFixturesError(
                            "Premier0 recorded score is not source-qualified")
                rows.append(SourceSelectedPremierFixture(
                    native_encounter_index=encounter, fixture_id=fid,
                    node_token=token, round_index=fixture.round_index,
                    scheduled_date=on_date, home_club_id=home, away_club_id=away,
                    played=result is not None, home_goals=hg, away_goals=ag,
                ))
            encounter += 1
    if seen_ids != set(ids):
        raise SourceSelectedPremierFixturesError(
            "Original 373-head primary calendar lacks fixed Premier0 fixtures")
    return SourceSelectedPremierFixtures(
        competition_id=0, member_club_ids=ranked_ids,
        scheduled_matchday_count=38, schedule_cycle_count=2, matrix_layer_count=1,
        fixtures_in_source_order=tuple(rows),
    )
