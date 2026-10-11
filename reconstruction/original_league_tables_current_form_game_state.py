"""Read-only, fail-closed GameState bridge for original League Current Form.

This is NOT a visible League Tables presenter and never repairs/mutates match
lifecycle. Native evidence: original PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3,
0x403640/0x4079D0, 0x4F3B50/0x4F3B70, 0x4F4970, 0x510380,
0x615C50/0x615ED0 and 0x513F70. Recovery 527/528 reports document
original file/field and calendar selection provenance.

The port only retains a primary ScheduleContainer shadow. This bridge accepts
a single full-member, source-primary league with a matching procedural
fixture/result owner; it refuses second-calendar, incomplete or inconsistent
source state. The original Current Form kernel remains the semantic owner.
"""
from __future__ import annotations

from datetime import date

from original_league_tables_current_form import (
    OriginalCurrentFormSourceError,
    SourceCurrentFormClub,
    SourceCurrentFormMatch,
    source_qualified_current_form_ranking,
)


def source_qualified_primary_current_form_from_game_state(
    state: object, *, competition_id: int, competition_context: int = 0,
):
    """Build original Current Form rows only from complete validated primary state.

    The original selects per-club native primary/secondary history. No retained
    secondary day buckets exist in this GameState schema. Do not infer played
    bits from live scores, guess member sides or manufacture a fixture history.
    """
    def refuse(reason: str):
        raise OriginalCurrentFormSourceError("GameState Current Form source: " + reason)

    if type(competition_id) is not int or competition_id < 0:
        refuse("source competition ID is invalid")
    if type(competition_context) is not int or competition_context != 0:
        refuse("non-root/group competition context is not source-qualified")
    competition = getattr(state, "competitions", {}).get(competition_id)
    if (competition is None or getattr(competition, "runtime_kind", None) != "league"
            or getattr(competition, "parent_competition_id", object()) is not None
            or type(getattr(competition, "country_region_id", None)) is not int
            or getattr(competition, "uses_secondary_schedule_container", None) is not False):
        refuse("original root League / country / native primary container not established")

    live = getattr(state, "procedural_leagues", {}).get((competition_id, 0))
    if live is None or (
        getattr(live, "competition_id", None),
        getattr(live, "competition_context", None),
    ) != (competition_id, 0):
        refuse("missing exact source procedural League owner")

    raw_clubs = getattr(state, "clubs", {})
    membership = getattr(state, "club_competition_membership", {})
    member_ids = getattr(live, "club_ids", None)
    if (type(member_ids) is not tuple or not 2 <= len(member_ids) <= 24
            or len(set(member_ids)) != len(member_ids)):
        refuse("procedural owner has incomplete/duplicate club vector")
    actual_members = {cid for cid, owner in membership.items()
                      if owner == competition_id}
    if actual_members != set(member_ids):
        refuse("live club membership differs from complete original League owner")

    clubs = []
    for cid in member_ids:
        if type(cid) is not int or cid not in raw_clubs:
            refuse("source club record missing")
        raw = raw_clubs[cid]
        if getattr(raw, "country_id", None) != competition.country_region_id:
            refuse("original League member country disagrees with source root")
        # 0x4022D0 Master.dat byte98 -> DBRClub+0x74 verified for initial load.
        mode = getattr(raw, "team_category_code", None)
        if type(mode) is not int or mode != 1:
            refuse("club requires secondary or unresolved dynamic calendar mode")
        short = getattr(raw, "short_name", None)
        if type(short) is not str:
            refuse("native CP1252 club name unavailable")
        try:
            name_bytes = short.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalCurrentFormSourceError(
                "GameState Current Form source: non-CP1252 club name"
            ) from exc
        clubs.append(SourceCurrentFormClub(cid, name_bytes, mode))

    shadow = getattr(state, "primary_schedule_shadow", None)
    days = getattr(shadow, "days", None)
    calendar = getattr(state, "calendar", None)
    current = getattr(calendar, "current_date", None)
    end = getattr(state, "primary_schedule_end_date", None)
    if (type(current) is not date or type(end) is not date or current >= end
            or type(days) is not dict or not days):
        refuse("full native primary calendar/current-day window not retained")

    fixtures = getattr(live, "fixtures", None)
    results = getattr(live, "results", None)
    if type(fixtures) is not dict or not fixtures or type(results) is not dict:
        refuse("complete source fixture/result registry unavailable")
    if not set(results).issubset(fixtures):
        refuse("result without source fixture")
    # Original DBRCompetition source byte18 is the native League round count.
    # Source-complete history must have one fixture for each pair of clubs
    # in each scheduled round; registry/shadow self-agreement is insufficient.
    source_matchdays = getattr(competition, "scheduled_matchday_count", None)
    if type(source_matchdays) is not int or source_matchdays <= 0:
        refuse("original scheduled matchday count unavailable")
    expected_sides = len(member_ids) * source_matchdays
    if expected_sides % 2 or len(fixtures) != expected_sides // 2:
        refuse("live fixture count contradicts original scheduled matchdays")
    observed = set()
    primary_days = {}
    for on_date, entries in days.items():
        if type(on_date) is not date or type(entries) is not tuple:
            refuse("primary schedule contains unqualified native day bucket")
        converted = []
        for entry in entries:
            if (getattr(entry, "competition_id", None) != competition_id
                    or getattr(entry, "competition_context", None) != 0):
                continue
            if getattr(entry, "node_kind", None) != "league_match":
                refuse("selected League contains a non-LeagueMatch source node")
            token = getattr(entry, "node_token", None)
            if type(token) is not tuple or token not in fixtures or token in observed:
                refuse("fixture token missing, repeated or not owned by selected League")
            observed.add(token)
            f = fixtures[token]
            home = getattr(f, "home_club_id", None)
            away = getattr(f, "away_club_id", None)
            if (type(home) is not int or type(away) is not int or home == away
                    or home not in actual_members or away not in actual_members):
                refuse("LeagueMatch references unresolved/foreign participant")
            refs = (getattr(entry, "participant_0_ref", None),
                    getattr(entry, "participant_1_ref", None))
            direct = tuple(getattr(ref, "direct_club_id", None) for ref in refs)
            if (direct != (home, away)
                    or getattr(entry, "side_club_cache", None) != direct
                    or getattr(f, "node_token", None) != token):
                refuse("original Side cache/reference disagrees with live fixture")
            flags = getattr(entry, "payload_filter_bits", None)
            if type(flags) is not int or flags & ~0x61 or flags < 0:
                refuse("native +0x44 status bits incomplete")
            link = getattr(entry, "wrapper_link_state", None)
            if link not in ("clear", "linked"):
                refuse("native wrapper+0x08 state unknown")
            result = results.get(token)
            if (result is None) != (not bool(flags & 1)):
                refuse("native played bit and live results disagree")
            if result is None:
                hg, ag = 0, 0  # Native Match::0x5103D0 constructor, not guessed result.
            else:
                if getattr(result, "node_token", None) != token:
                    refuse("result ownership is inconsistent")
                hg, ag = getattr(result, "home_goals", None), getattr(result, "away_goals", None)
            converted.append(SourceCurrentFormMatch(
                token=token,
                competition_id=competition_id,
                home_club_id=home,
                away_club_id=away,
                fixture_secondary_calendar=False,  # Original primary bucket; 0x510380.
                source_status_bits=flags,
                source_wrapper_link=0 if link == "clear" else 1,
                home_goals=hg,
                away_goals=ag,
            ))
        if converted:
            primary_days[on_date] = tuple(converted)
    if observed != set(fixtures):
        refuse("live fixtures do not equal the retained native primary schedule")
    if not primary_days:
        refuse("no source-qualified LeagueMatch history")
    return source_qualified_current_form_ranking(
        competition_id=competition_id,
        current_date=current,
        members=tuple(clubs),
        primary_days=primary_days,
        secondary_days={},
    )
