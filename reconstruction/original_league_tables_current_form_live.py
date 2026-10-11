"""Strict live primary-schedule provider for original League Current Form.

This is NOT the player-visible PLeagueTables Current Form panel. Native
Match::0x510380 records a primary/secondary bit from its actual schedule,
0x403640 uses DBRClub+0x74 (Master.dat club record byte98) to select the
search container, and 0x615ED0 searches its preserved head/order and flags.
Only the source-qualified primary member set is currently available here.
A required secondary history is rejected, never substituted with primary.
"""
from __future__ import annotations

from datetime import date
from typing import Mapping

from original_league_tables_current_form import (
    OriginalCurrentFormSourceError,
    SourceCurrentFormClub,
    SourceCurrentFormMatch,
    SourceCurrentFormRank,
    source_qualified_current_form_ranking,
)
from original_league_tables_live_source import (
    SourceProceduralLeagueTableError,
    source_qualified_selected_procedural_league_table,
)


class OriginalLiveCurrentFormSourceError(OriginalCurrentFormSourceError):
    """Source-native calendar/live-result parity has not been established."""


def source_qualified_primary_current_form(
    *,
    selected_country_id: int,
    competition_id: int,
    current_date: date,
    membership: Mapping[int, int],
    clubs: Mapping[int, object],
    competitions: Mapping[int, object],
    procedural_leagues: Mapping[tuple[int, int], object],
    primary_shadow: object,
) -> tuple[SourceCurrentFormRank, ...]:
    """Read source-correct non-PL root League form from retained primary history.

    This does not accept an inferred club mode, a secondary fixture/calendar,
    a partial live League season, an unresolved Side, unknown wrapper status,
    or a missing status/result correspondence. Preserved source bucket order,
    not modern sorted matches, breaks candidates on the same day.
    """
    if (type(selected_country_id) is not int or selected_country_id < 0
            or type(competition_id) is not int or competition_id <= 0
            or type(current_date) is not date):
        raise OriginalLiveCurrentFormSourceError(
            "Selected original League/country/current-day identity unavailable"
        )
    try:
        source_qualified_selected_procedural_league_table(
            selected_country_id=selected_country_id,
            competition_id=competition_id,
            membership=membership,
            clubs=clubs,
            competitions=competitions,
            procedural_leagues=procedural_leagues,
        )
    except SourceProceduralLeagueTableError as exc:
        raise OriginalLiveCurrentFormSourceError(
            "Selected League has no source-complete live roster and results"
        ) from exc

    live = procedural_leagues.get((competition_id, 0))
    defs = competitions.get(competition_id)
    source_matchdays = getattr(defs, "scheduled_matchday_count", None)
    ids = getattr(live, "club_ids", None)
    fixtures = getattr(live, "fixtures", None)
    results = getattr(live, "results", None)
    days = getattr(primary_shadow, "days", None)
    if (type(ids) is not tuple or not 2 <= len(ids) <= 24
            or type(source_matchdays) is not int or source_matchdays <= 0
            or not hasattr(fixtures, "get") or not hasattr(results, "get")
            or not hasattr(days, "items")):
        raise OriginalLiveCurrentFormSourceError(
            "Original complete primary season schedule/status data unavailable"
        )
    expected = len(ids) * source_matchdays
    if expected % 2 or len(fixtures) != expected // 2:
        raise OriginalLiveCurrentFormSourceError(
            "Live original League season is not complete for scheduled matchdays"
        )

    members = []
    for cid in ids:
        club = clubs.get(cid)
        name = getattr(club, "short_name", None)
        mode = getattr(club, "team_category_code", None)
        if (type(cid) is not int or cid < 0 or not isinstance(name, str)
                or not name or type(mode) is not int):
            raise OriginalLiveCurrentFormSourceError(
                "Original League member or native DBRClub source mode is missing"
            )
        # The shipped Master.dat initial field is exactly DBRClub+0x74.
        # Later transient runtime mutations must be audited separately.
        if mode != 1:
            raise OriginalLiveCurrentFormSourceError(
                "Secondary/altered native club calendar requires retained secondary history"
            )
        try:
            source_name = name.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalLiveCurrentFormSourceError(
                "Original club sort text is not CP1252"
            ) from exc
        members.append(SourceCurrentFormClub(cid, source_name, mode))

    ordered_primary: dict[date, tuple[SourceCurrentFormMatch, ...]] = {}
    seen: set[tuple] = set()
    for day, entries in days.items():
        if type(day) is not date or type(entries) is not tuple:
            raise OriginalLiveCurrentFormSourceError(
                "Source primary day or linked-bucket representation is invalid"
            )
        selected = []
        for entry in entries:
            if getattr(entry, "competition_id", None) != competition_id:
                continue
            if (getattr(entry, "node_kind", None) != "league_match"
                    or getattr(entry, "competition_context", None) != 0):
                raise OriginalLiveCurrentFormSourceError(
                    "Selected source contains unsupported native match type/context"
                )
            token = getattr(entry, "node_token", None)
            if (type(token) is not tuple or not token or token in seen
                    or token not in fixtures):
                raise OriginalLiveCurrentFormSourceError(
                    "Original League fixture token is missing/ambiguous"
                )
            seen.add(token)
            fixture = fixtures[token]
            h = getattr(fixture, "home_club_id", None)
            a = getattr(fixture, "away_club_id", None)
            sides = (
                getattr(getattr(entry, "participant_0_ref", None), "direct_club_id", None),
                getattr(getattr(entry, "participant_1_ref", None), "direct_club_id", None),
            )
            if (type(h) is not int or type(a) is not int or h == a
                    or h not in ids or a not in ids or sides != (h, a)):
                raise OriginalLiveCurrentFormSourceError(
                    "Original League participant Side is not source-qualified"
                )
            cached = getattr(entry, "side_club_cache", None)
            if cached is not None and cached != (h, a):
                raise OriginalLiveCurrentFormSourceError(
                    "Original native Side cache contradicts active League fixture"
                )
            bits = getattr(entry, "payload_filter_bits", None)
            if (type(bits) is not int or bits < 0 or bits & ~0x61):
                raise OriginalLiveCurrentFormSourceError(
                    "Original LeagueMatch+0x44 bit0/5/6 source flags unavailable"
                )
            link = getattr(entry, "wrapper_link_state", None)
            if link not in ("clear", "linked"):
                raise OriginalLiveCurrentFormSourceError(
                    "Original wrapper+0x08 resolved/unknown state is unavailable"
                )
            outcome = results.get(token)
            if (outcome is None and bits & 1 or
                    outcome is not None and not bits & 1):
                raise OriginalLiveCurrentFormSourceError(
                    "Live scored-result and original played-bit status disagree"
                )
            if outcome is None:
                hg = ag = 0  # Match::0x5103D0 initializes raw score words to zero.
            else:
                if getattr(outcome, "node_token", None) != token:
                    raise OriginalLiveCurrentFormSourceError(
                        "LeagueMatch result token disagrees with native fixture"
                    )
                hg = getattr(outcome, "home_goals", None)
                ag = getattr(outcome, "away_goals", None)
                if (type(hg) is not int or type(ag) is not int
                        or not 0 <= hg <= 32767 or not 0 <= ag <= 32767):
                    raise OriginalLiveCurrentFormSourceError(
                        "Original LeagueMatch signed score word is unqualified"
                    )
            selected.append(SourceCurrentFormMatch(
                token=token, competition_id=competition_id,
                home_club_id=h, away_club_id=a,
                fixture_secondary_calendar=False,  # Qualified primary head.
                source_status_bits=bits,
                source_wrapper_link=int(link == "linked"),
                home_goals=hg, away_goals=ag,
            ))
        if selected:
            ordered_primary[day] = tuple(selected)
    if seen != set(fixtures):
        raise OriginalLiveCurrentFormSourceError(
            "Preserved primary schedule omitted live League fixtures"
        )
    try:
        return source_qualified_current_form_ranking(
            competition_id=competition_id,
            current_date=current_date,
            members=tuple(members),
            primary_days=ordered_primary,
            secondary_days={},
        )
    except OriginalCurrentFormSourceError as exc:
        raise OriginalLiveCurrentFormSourceError(str(exc)) from exc
