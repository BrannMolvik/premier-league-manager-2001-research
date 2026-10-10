"""Source-qualified League Position rows for an actual live procedural League.

PLeagueTables uses native League::0x4F45E0: points↓, played↑,
goal difference↓, goals for↓, goals against↑ and source CP1252 short name↑.
This owner accepts real retained match results only when the root League,
human club, complete current member set and competition context all agree.
It never materializes fixtures during a GUI read, invents an unknown member,
uses the procedural first-fixture-encounter order as the native prepared order,
or enables unrecovered PLeagueTables Current Form / Division pointer controls.
"""

from __future__ import annotations

from typing import Mapping


class SourceProceduralLeagueTableError(ValueError):
    """A real competition's original League Position rows are unqualified."""


def source_qualified_procedural_league_table(
    *,
    human_club_id: int,
    competition_id: int,
    membership: Mapping[int, int],
    clubs: Mapping[int, object],
    competitions: Mapping[int, object],
    procedural_leagues: Mapping[tuple[int, int], object],
) -> tuple[object, ...]:
    """Return actual live LeagueRow records in recovered 0x4F45E0 order.

    A partial/synthetic procedural schedule cannot prove the original
    displayed League roster. Only expose rows when participant membership
    and original DBRClub+0x10 agree exactly. Full-key identical ties are
    rejected, because CRT qsort's equal-key permutation is not established.
    """
    if type(human_club_id) is not int or type(competition_id) is not int:
        raise SourceProceduralLeagueTableError(
            "Manager club and League identities must be source integers"
        )
    if human_club_id < 0 or competition_id <= 0:
        raise SourceProceduralLeagueTableError(
            "This owner requires a non-Premier-League source identity"
        )
    if membership.get(human_club_id) != competition_id:
        raise SourceProceduralLeagueTableError(
            "Current manager's DBRClub League does not match selected competition"
        )
    human_club = clubs.get(human_club_id)
    competition = competitions.get(competition_id)
    if human_club is None or competition is None:
        raise SourceProceduralLeagueTableError(
            "Current club or original League source record is missing"
        )
    if (getattr(competition, "runtime_kind_code", None) != 1
            or getattr(competition, "parent_competition_id", object()) is not None
            or getattr(competition, "country_region_id", None)
            != getattr(human_club, "country_id", None)):
        raise SourceProceduralLeagueTableError(
            "Selected source competition is not the current club's root League"
        )

    keys = tuple(key for key in procedural_leagues
                 if (type(key) is tuple and len(key) == 2
                     and type(key[0]) is int and key[0] == competition_id))
    if keys != ((competition_id, 0),):
        raise SourceProceduralLeagueTableError(
            "Current League has no unambiguous live context-zero result state"
        )
    live = procedural_leagues[keys[0]]
    if (getattr(live, "competition_id", None) != competition_id
            or getattr(live, "competition_context", None) != 0):
        raise SourceProceduralLeagueTableError(
            "Live result state does not match its source League context"
        )
    member_ids = getattr(live, "club_ids", None)
    if (type(member_ids) is not tuple or not 2 <= len(member_ids) <= 24
            or any(type(cid) is not int or cid < 0 for cid in member_ids)
            or len(set(member_ids)) != len(member_ids)):
        raise SourceProceduralLeagueTableError(
            "Live procedural League has no qualified distinct member set"
        )
    roster = {
        cid for cid, league_id in membership.items()
        if type(cid) is int and league_id == competition_id
    }
    if set(member_ids) != roster or human_club_id not in roster:
        raise SourceProceduralLeagueTableError(
            "Live League participants disagree with current source club memberships"
        )

    source_names = {}
    for cid in member_ids:
        club = clubs.get(cid)
        if club is None or getattr(club, "country_id", None) != human_club.country_id:
            raise SourceProceduralLeagueTableError(
                "Live League participant lacks a matching source club/country"
            )
        name = getattr(club, "short_name", None)
        if not isinstance(name, str) or not name:
            raise SourceProceduralLeagueTableError(
                "Original club short-name sort key is missing"
            )
        try:
            source_names[cid] = name.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise SourceProceduralLeagueTableError(
                "Original club short-name sort key is not CP1252"
            ) from exc

    if not callable(getattr(live, "table", None)) or not callable(
        getattr(live, "exact_ranking", None)
    ):
        raise SourceProceduralLeagueTableError(
            "Live League results/ranking producer is missing"
        )
    rows = tuple(live.table())
    if len(rows) != len(member_ids):
        raise SourceProceduralLeagueTableError(
            "Live League results omitted a source member"
        )
    by_club = {getattr(row, "club_id", None): row for row in rows}
    if set(by_club) != set(member_ids) or len(by_club) != len(rows):
        raise SourceProceduralLeagueTableError(
            "Live League row identities differ from the member set"
        )
    keys_seen = set()
    for cid, row in by_club.items():
        source_key = (
            -int(row.points),
            int(row.played),
            -int(row.goal_difference),
            -int(row.goals_for),
            int(row.goals_against),
            source_names[cid],
        )
        if source_key in keys_seen:
            raise SourceProceduralLeagueTableError(
                "Unresolved exact CRT sort tie; refusing invented original row order"
            )
        keys_seen.add(source_key)
    ranking = live.exact_ranking(source_names.get)
    if (ranking is None or tuple(ranking) != tuple(
        sorted(member_ids, key=lambda cid: (
            -int(by_club[cid].points),
            int(by_club[cid].played),
            -int(by_club[cid].goal_difference),
            -int(by_club[cid].goals_for),
            int(by_club[cid].goals_against),
            source_names[cid],
        ))
    )):
        raise SourceProceduralLeagueTableError(
            "Live League ranking disagrees with original 0x4F45E0 comparator"
        )
    return tuple(by_club[cid] for cid in ranking)
