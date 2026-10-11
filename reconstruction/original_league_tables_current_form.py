"""Original League::0x4F4A10 Current Form ranking, with explicit source inputs.

This is a source-scoped computation kernel, NOT permission to expose a Current
Form screen without a verified original calendar/DBRClub owner and row bridge.
The caller must supply exact retained primary/secondary native bucket order,
source club mode +0x74 and original LeagueMatch score words. It deliberately
includes qualified *unplayed* 0-0 matches when the original search would.

Native provenance: original hash 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
0x403640/0x4079D0, 0x4F4970, 0x4F4A10/0x4F4A70, 0x615C50/0x615ED0,
0x510300/0x510A20, LeagueMatch::0x513F70 and Match::0x5103D0.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping


class OriginalCurrentFormSourceError(ValueError):
    """The native Current Form source inputs are insufficient or contradictory."""


@dataclass(frozen=True)
class SourceCurrentFormClub:
    club_id: int
    # Original DBRClub name content, not Unicode-normalized displayed text.
    cp1252_short_name: bytes
    # Exact DBRClub+0x74 unsigned byte. Only values 2 and 3 select secondary.
    source_calendar_mode: int


@dataclass(frozen=True)
class SourceCurrentFormMatch:
    token: tuple
    competition_id: int
    home_club_id: int
    away_club_id: int
    # True iff native fixture+0x0c bit0 chooses secondary container.
    fixture_secondary_calendar: bool
    # Native fixture status+0x44 bits 0,5,6 retained. Bit0 need NOT be set.
    source_status_bits: int
    # Native wrapper+0x08: known integer, 0 is eligible.
    source_wrapper_link: int
    # Native LeagueMatch signed 16-bit +0x3C, +0x3E (zero on construction).
    home_goals: int
    away_goals: int
    # Source class must be LeagueMatch before 0x4F4970's unchecked +0x44 call.
    source_class: str = "LeagueMatch"


@dataclass(frozen=True)
class SourceCurrentFormRank:
    club_id: int
    score: int
    matching_tokens: tuple[tuple, ...]


def _integer(value: object, label: str, *, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise OriginalCurrentFormSourceError(
            f"{label} must be a native integer in [{minimum},{maximum}]"
        )
    return value


def _validated_clubs(clubs: tuple[SourceCurrentFormClub, ...]) -> dict[int, SourceCurrentFormClub]:
    if type(clubs) is not tuple or not 2 <= len(clubs) <= 24:
        raise OriginalCurrentFormSourceError("Source League must provide its full 2..24 member vector")
    by_id: dict[int, SourceCurrentFormClub] = {}
    for club in clubs:
        if type(club) is not SourceCurrentFormClub:
            raise OriginalCurrentFormSourceError("Missing typed LeagueClub source member")
        cid = _integer(club.club_id, "club ID", minimum=0, maximum=2147483647)
        _integer(club.source_calendar_mode, "DBRClub calendar mode", minimum=0, maximum=255)
        if (type(club.cp1252_short_name) is not bytes or not club.cp1252_short_name
                or b"\x00" in club.cp1252_short_name):
            raise OriginalCurrentFormSourceError("Require exact nonempty CP1252 name bytes")
        if cid in by_id:
            raise OriginalCurrentFormSourceError("Duplicate source League member")
        by_id[cid] = club
    return by_id


def _validated_calendar(
    calendar: Mapping[date, tuple[SourceCurrentFormMatch, ...]],
    *,
    name: str,
) -> dict[date, tuple[SourceCurrentFormMatch, ...]]:
    if not hasattr(calendar, "items"):
        raise OriginalCurrentFormSourceError(f"Native {name} day buckets are missing")
    copied: dict[date, tuple[SourceCurrentFormMatch, ...]] = {}
    tokens: set[tuple] = set()
    for day, entries in calendar.items():
        if type(day) is not date or type(entries) is not tuple:
            raise OriginalCurrentFormSourceError(f"Native {name} calendar day/bucket is invalid")
        for entry in entries:
            if type(entry) is not SourceCurrentFormMatch:
                raise OriginalCurrentFormSourceError("Native bucket contains unresolved match wrapper")
            if type(entry.token) is not tuple or not entry.token:
                raise OriginalCurrentFormSourceError("Native match token is absent")
            try:
                if entry.token in tokens:
                    raise OriginalCurrentFormSourceError("Duplicate native match token")
                tokens.add(entry.token)
            except TypeError as exc:
                raise OriginalCurrentFormSourceError("Source match token is unhashable") from exc
            _integer(entry.competition_id, "competition ID", minimum=0, maximum=2147483647)
            _integer(entry.home_club_id, "home club", minimum=0, maximum=2147483647)
            _integer(entry.away_club_id, "away club", minimum=0, maximum=2147483647)
            if entry.home_club_id == entry.away_club_id:
                raise OriginalCurrentFormSourceError("Native match references the same club twice")
            if type(entry.fixture_secondary_calendar) is not bool:
                raise OriginalCurrentFormSourceError("Native fixture calendar flag unavailable")
            if entry.fixture_secondary_calendar != (name == "secondary"):
                raise OriginalCurrentFormSourceError("Match fixture calendar bit disagrees with bucket owner")
            _integer(entry.source_status_bits, "source match flags", minimum=0, maximum=0x61)
            if entry.source_status_bits & ~0x61:
                raise OriginalCurrentFormSourceError("Unknown native status bits")
            _integer(entry.source_wrapper_link, "wrapper +0x08 link", minimum=0, maximum=2147483647)
            for value, label in ((entry.home_goals, "home goals"), (entry.away_goals, "away goals")):
                _integer(value, label, minimum=-32768, maximum=32767)
        copied[day] = entries
    return copied


def source_qualified_current_form_ranking(
    *,
    competition_id: int,
    current_date: date,
    members: tuple[SourceCurrentFormClub, ...],
    primary_days: Mapping[date, tuple[SourceCurrentFormMatch, ...]],
    secondary_days: Mapping[date, tuple[SourceCurrentFormMatch, ...]],
) -> tuple[SourceCurrentFormRank, ...]:
    """Calculate source-proven ranking without inventing a provider or mouse action.

    Source 0x615ED0 scans days backwards inclusively; 0x615C50's form flags
    match club/League, bit5=0 and do not demand played bit0; outer strict
    filter refuses wrapper+8 and bit6. It takes the first eligible node on a
    day in original linked order, and 0x510A20 subtracts one day for the next
    lookup. Source 0x513F70 compares raw goals, not the played bit.
    """
    _integer(competition_id, "selected League", minimum=0, maximum=2147483647)
    if type(current_date) is not date:
        raise OriginalCurrentFormSourceError("Source current day is unavailable")
    roster = _validated_clubs(members)
    primary = _validated_calendar(primary_days, name="primary")
    secondary = _validated_calendar(secondary_days, name="secondary")
    if set(entry.token for entries in primary.values() for entry in entries) & set(
            entry.token for entries in secondary.values() for entry in entries):
        raise OriginalCurrentFormSourceError("Same fixture token installed in both source calendars")
    out: list[SourceCurrentFormRank] = []
    for club in members:
        calendar = secondary if club.source_calendar_mode in (2, 3) else primary
        score = 0
        consumed: list[tuple] = []
        for day in sorted((day for day in calendar if day <= current_date), reverse=True):
            for fixture in calendar[day]:
                if (fixture.competition_id != competition_id
                        or fixture.home_club_id != club.club_id
                        and fixture.away_club_id != club.club_id
                        or fixture.source_status_bits & 0x60
                        or fixture.source_wrapper_link):
                    continue
                if fixture.source_class != "LeagueMatch":
                    raise OriginalCurrentFormSourceError("Original native LeagueMatch cast would not succeed")
                if fixture.home_club_id not in roster or fixture.away_club_id not in roster:
                    raise OriginalCurrentFormSourceError("Selected original League fixture has foreign member")
                # Winner accessor 0x513F70 does not check +0x44 played bit0.
                if fixture.home_goals == fixture.away_goals:
                    score += 1
                elif (fixture.home_goals > fixture.away_goals) == (
                        fixture.home_club_id == club.club_id):
                    score += 3
                consumed.append(fixture.token)
                break
            if len(consumed) == 6:
                break
        out.append(SourceCurrentFormRank(club.club_id, score, tuple(consumed)))
    out.sort(key=lambda row: (-row.score, roster[row.club_id].cp1252_short_name))
    for previous, current in zip(out, out[1:]):
        if (previous.score == current.score and
                roster[previous.club_id].cp1252_short_name ==
                roster[current.club_id].cp1252_short_name):
            raise OriginalCurrentFormSourceError("Native qsort equality leaves Current Form order unproved")
    return tuple(out)
