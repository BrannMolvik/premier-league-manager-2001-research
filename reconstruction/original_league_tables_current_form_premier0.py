"""Original Premier League0 Current Form data producer: source-first and read-only.

This handles the shipped Premier0 20-club/380-fixture owner, which is distinct
from LiveProceduralLeagueState. No Current Form GUI, radio click, or original
secondary history is inferred. Original provenance: verified private PE
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
0x4F4970/0x615ED0/0x513F70 six-form filter and 0x4F3B70/0x510380
container ownership; original selected fixed/annual Premier0 373-head source
is independently verified in original_league_fixtures_selected_premier0.py.
"""
from __future__ import annotations

from datetime import date

from competition_state import PremierLeagueState
from original_league_tables_current_form import (
    OriginalCurrentFormSourceError,
    SourceCurrentFormClub,
    SourceCurrentFormMatch,
    source_qualified_current_form_ranking,
)


def source_qualified_premier0_current_form_from_game_state(state: object):
    """Produce source-ranked Premier0 six-cell form; reject any unknown native owner."""
    def refuse(reason: str):
        raise OriginalCurrentFormSourceError("Premier0 Current Form source: " + reason)

    competitions = getattr(state, "competitions", None)
    clubs = getattr(state, "clubs", None)
    membership = getattr(state, "club_competition_membership", None)
    if not all(isinstance(o, dict) for o in (competitions, clubs, membership)):
        refuse("original source definitions/club membership missing")
    definition = competitions.get(0)
    if (definition is None
            or getattr(definition, "runtime_kind_code", None) != 1
            or getattr(definition, "parent_competition_id", object()) is not None
            or getattr(definition, "country_region_id", None) != 26
            or getattr(definition, "scheduled_matchday_count", None) != 38
            or getattr(definition, "uses_secondary_schedule_container", None) is not False):
        refuse("original England root Premier League0 / primary calendar unavailable")

    league = getattr(state, "premier_league", None)
    if type(league) is not PremierLeagueState:
        refuse("fixed/annual Premier League source owner missing")
    member_ids = getattr(league, "club_ids", None)
    source_order = getattr(league, "fixture_source_order", None)
    fixtures = getattr(league, "fixtures", None)
    results = getattr(league, "results", None)
    if (type(member_ids) is not tuple or len(member_ids) != 20
            or len(set(member_ids)) != 20
            or any(type(cid) is not int or cid < 0 for cid in member_ids)
            or type(source_order) is not tuple or len(source_order) != 380
            or any(type(fid) is not int for fid in source_order)
            or len(set(source_order)) != 380
            or type(fixtures) is not dict or set(fixtures) != set(source_order)
            or type(results) is not dict or not set(results).issubset(fixtures)):
        refuse("complete canonical 20-member/380-fixture owner is missing")
    actual = {cid for cid, competition in membership.items()
              if type(cid) is int and competition == 0}
    if actual != set(member_ids):
        refuse("original current membership differs from Premier0 source roster")

    source_clubs = []
    for cid in member_ids:
        record = clubs.get(cid)
        if (record is None or getattr(record, "country_id", None) != 26
                or getattr(record, "team_category_code", None) != 1):
            refuse("Premier0 club has foreign or unresolved source calendar mode")
        short = getattr(record, "short_name", None)
        if type(short) is not str:
            refuse("original club short-name bytes unavailable")
        try:
            name = short.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalCurrentFormSourceError(
                "Premier0 Current Form source: unencodable CP1252 short name"
            ) from exc
        source_clubs.append(SourceCurrentFormClub(cid, name, 1))

    directed_pairs = set()
    for fid in source_order:
        source_fixture = fixtures[fid]
        h, a = getattr(source_fixture, "home_club_id", None), getattr(source_fixture, "away_club_id", None)
        if (type(h) is not int or type(a) is not int or h == a
                or h not in actual or a not in actual
                or getattr(source_fixture, "id", None) != fid
                or type(getattr(source_fixture, "round_index", None)) is not int
                or not 0 <= source_fixture.round_index < 38):
            refuse("Premier0 source fixture sides/identity/round are invalid")
        if (h, a) in directed_pairs:
            refuse("Premier0 source has a duplicate directed pair")
        directed_pairs.add((h, a))
    if len(directed_pairs) != 380:
        refuse("source calendar is not an original complete directed season")

    calendar = getattr(state, "calendar", None)
    current = getattr(calendar, "current_date", None)
    end = getattr(state, "primary_schedule_end_date", None)
    shadow = getattr(state, "primary_schedule_shadow", None)
    days = getattr(shadow, "days", None)
    if (type(current) is not date or type(end) is not date or current >= end
            or type(days) is not dict or not days or len(days) > 373):
        refuse("native 373-head primary day window unavailable")
    seen_ids = set()
    kinds = set()
    converted_days = {}
    for day in sorted(days):
        entries = days[day]
        if type(day) is not date or type(entries) is not tuple:
            refuse("original day bucket/head order unavailable")
        selected = []
        for entry in entries:
            if getattr(entry, "competition_id", None) != 0:
                continue
            kind = getattr(entry, "node_kind", None)
            if kind not in ("fixed_league_match", "league_match") or (
                    getattr(entry, "competition_context", None) != 0):
                refuse("Premier0 native LeagueMatch class or context is unresolved")
            kinds.add(kind)
            token = getattr(entry, "node_token", None)
            if (type(token) is not tuple or len(token) != 4
                    or token[:3] != (kind, 0, 0)
                    or type(token[3]) is not int or token[3] not in fixtures
                    or token[3] in seen_ids):
                refuse("original Premier0 fixture token missing/duplicated")
            fid = token[3]
            seen_ids.add(fid)
            src = fixtures[fid]
            home, away = src.home_club_id, src.away_club_id
            refs = (getattr(entry, "participant_0_ref", None),
                    getattr(entry, "participant_1_ref", None))
            direct = tuple(getattr(ref, "direct_club_id", None) for ref in refs)
            if (direct != (home, away)
                    or getattr(entry, "side_club_cache", None) != direct):
                refuse("native LeagueMatch participant Side source disagrees with live owner")
            bits = getattr(entry, "payload_filter_bits", None)
            if type(bits) is not int or bits < 0 or bits & ~0x61:
                refuse("native match +0x44 flags unavailable")
            link = getattr(entry, "wrapper_link_state", None)
            if link not in ("clear", "linked"):
                refuse("original wrapper +0x08 lifecycle is unresolved")
            result = results.get(fid)
            if bool(bits & 1) != (result is not None):
                refuse("live result and native match played bit0 disagree")
            if result is None:
                home_goals = away_goals = 0  # Original new Match::0x5103D0.
            else:
                if getattr(result, "fixture_id", None) != fid:
                    refuse("original Premier0 result identity mismatch")
                home_goals, away_goals = getattr(result, "home_goals", None), getattr(result, "away_goals", None)
            selected.append(SourceCurrentFormMatch(
                token=token, competition_id=0, home_club_id=home, away_club_id=away,
                fixture_secondary_calendar=False, source_status_bits=bits,
                source_wrapper_link=0 if link == "clear" else 1,
                home_goals=home_goals, away_goals=away_goals,
            ))
        if selected:
            converted_days[day] = tuple(selected)
    if seen_ids != set(source_order) or len(kinds) != 1:
        refuse("primary history incomplete or mixes original first/annual class")
    return source_qualified_current_form_ranking(
        competition_id=0, current_date=current,
        members=tuple(source_clubs), primary_days=converted_days, secondary_days={},
    )
