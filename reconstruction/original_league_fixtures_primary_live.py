"""Actual first-season primary LeagueMatch candidates in native PLeagueFixtures order.

Source-backed original chain: PLeagueFixtures::0x46D950 scans 373 heads of
primary ScheduleContainer 0x947AD8, then fixture+0x04 linked nodes. The
clean-room canonical primary schedule already reproduces 0x615950 conflict
placement and head insert, 0x615BE0/0x615AE0 in-place per-bucket shuffle,
and preserves the resulting original linked order in primary_schedule_shadow.
Only source-matched, status-qualified direct/procedural live LeagueMatches
are returned here. This adapter NEVER manufactures native fixture IDs or
source PMatchInfo links from modern symbolic tuple tokens.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from original_league_fixtures_resources import (
    league_fixture_matrix_accepts_candidate,
    league_fixture_first_free_repeat_slot,
)


class SourcePrimaryLeagueFixturesError(ValueError):
    """The native 373-head original League fixture sequence is unqualified."""


@dataclass(frozen=True)
class SourcePrimaryLeagueFixture:
    node_token: tuple
    native_encounter_index: int
    scheduled_date: date
    home_club_id: int
    away_club_id: int
    played: bool
    home_goals: int | None
    away_goals: int | None


@dataclass(frozen=True)
class SourcePrimaryLeagueFixtures:
    competition_id: int
    member_club_ids: tuple[int, ...]
    scheduled_matchday_count: int
    schedule_cycle_count: int
    matrix_layer_count: int
    fixtures_in_source_order: tuple[SourcePrimaryLeagueFixture, ...]


def qualified_primary_league_fixtures(
    *,
    competition_id: int,
    member_club_ids: tuple[int, ...],
    scheduled_matchday_count: int,
    live: object,
    days: Mapping[date, tuple[object, ...]],
) -> SourcePrimaryLeagueFixtures:
    """Scan actual preserved original primary linked-bucket order, fail closed.

    The source-owned IDs are the original tuple node tokens. They remain
    opaque identifiers and must never be passed as a fake native integer
    fixture/PMatchInfo pointer.
    """
    if (type(competition_id) is not int or competition_id <= 0
            or type(member_club_ids) is not tuple
            or not 2 <= len(member_club_ids) <= 24
            or len(member_club_ids) != len(set(member_club_ids))
            or any(type(cid) is not int or cid < 0 for cid in member_club_ids)):
        raise SourcePrimaryLeagueFixturesError(
            "Current League has no qualified original source member identity"
        )
    if type(scheduled_matchday_count) is not int or scheduled_matchday_count <= 0:
        raise SourcePrimaryLeagueFixturesError(
            "Original League matchday count is unavailable"
        )
    n = len(member_club_ids)
    cycles, remainder = divmod(scheduled_matchday_count, n - 1)
    cycles += int(bool(remainder))
    layers = cycles // 2
    if layers <= 0:
        raise SourcePrimaryLeagueFixturesError(
            "Original 0x616F40 produced no directed-pair repeat layer"
        )
    if (getattr(live, "competition_id", None) != competition_id
            or getattr(live, "competition_context", None) != 0
            or not hasattr(getattr(live, "fixtures", None), "get")
            or not hasattr(getattr(live, "results", None), "get")):
        raise SourcePrimaryLeagueFixturesError(
            "Original selected League has no matching live context-zero fixtures/results"
        )
    if not hasattr(days, "items"):
        raise SourcePrimaryLeagueFixturesError(
            "Original source primary 373-head schedule is unavailable"
        )
    member_index = {cid: i for i, cid in enumerate(member_club_ids)}
    matrix_occupied = [False] * (n*n*layers)
    known_tokens = set(live.fixtures)
    # A complete source League season has N clubs playing the original
    # number of matchdays. Partial schedule materialization must never
    # masquerade as an original full-season fixtures grid.
    expected_fixture_count = n * scheduled_matchday_count
    if expected_fixture_count % 2 or len(known_tokens) != expected_fixture_count // 2:
        raise SourcePrimaryLeagueFixturesError(
            "Source League fixture schedule is incomplete for original matchdays"
        )
    seen = set()
    ordered = []
    # PrimaryScheduleShadowState.days preserves exact sorted original source
    # day-slot / linked-node ordering after the verified native shuffle.
    head_days = tuple(sorted(days))
    if (len(head_days) > 373
            or any(type(d) is not date for d in head_days)):
        raise SourcePrimaryLeagueFixturesError(
            "Original primary schedule exceeds source 373 bucket bounds"
        )
    native_index = 0
    for on_date in head_days:
        bucket = days[on_date]
        if not isinstance(bucket, tuple):
            raise SourcePrimaryLeagueFixturesError(
                "Original primary fixture bucket lost linked head-to-tail order"
            )
        for entry in bucket:
            if getattr(entry, "competition_id", None) != competition_id:
                native_index += 1
                continue
            if (getattr(entry, "node_kind", None) != "league_match"
                    or getattr(entry, "competition_context", None) != 0):
                raise SourcePrimaryLeagueFixturesError(
                    "Selected League has unsupported native match kind/context"
                )
            token = getattr(entry, "node_token", None)
            if (type(token) is not tuple or not token
                    or token in seen or token not in known_tokens):
                raise SourcePrimaryLeagueFixturesError(
                    "Original fixture chain token is missing, duplicate or unmapped"
                )
            seen.add(token)
            raw_bits = getattr(entry, "payload_filter_bits", None)
            if (type(raw_bits) is not int or raw_bits < 0
                    or raw_bits & ~0x61):
                raise SourcePrimaryLeagueFixturesError(
                    "Original fixture +0x44 source status bits are unknown"
                )
            fixture = live.fixtures[token]
            h = getattr(fixture, "home_club_id", None)
            a = getattr(fixture, "away_club_id", None)
            if (type(h) is not int or type(a) is not int
                    or h == a or h not in member_index or a not in member_index):
                raise SourcePrimaryLeagueFixturesError(
                    "Original fixture clubs do not resolve to selected League members"
                )
            cached = getattr(entry, "side_club_cache", None)
            if cached is not None and cached != (h, a):
                raise SourcePrimaryLeagueFixturesError(
                    "Native fixture side cache disagrees with resolved live League clubs"
                )
            accepted = league_fixture_matrix_accepts_candidate(
                kind_code=1,
                fixture_competition_identity=competition_id,
                selected_competition_identity=competition_id,
                fixture_status_bits=raw_bits,
                left_club_identity=h,
                right_club_identity=a,
            )
            if accepted:
                try:
                    slot = league_fixture_first_free_repeat_slot(
                        matrix_occupied,
                        club_count=n,
                        left_member_index=member_index[h],
                        right_member_index=member_index[a],
                        layer_count=layers,
                    )
                except ValueError as exc:
                    raise SourcePrimaryLeagueFixturesError(
                        "Original fixture chain exceeds its native directed-pair layer count"
                    ) from exc
                matrix_occupied[slot] = True
                result = live.results.get(token)
                goals = None if result is None else (
                    getattr(result, "home_goals", None),
                    getattr(result, "away_goals", None),
                )
                if goals is not None and (
                    any(type(value) is not int or value < 0 for value in goals)
                ):
                    raise SourcePrimaryLeagueFixturesError(
                        "Original played match has no complete source score"
                    )
                ordered.append(SourcePrimaryLeagueFixture(
                    node_token=token,
                    native_encounter_index=native_index,
                    scheduled_date=on_date,
                    home_club_id=h,
                    away_club_id=a,
                    played=goals is not None,
                    home_goals=None if goals is None else goals[0],
                    away_goals=None if goals is None else goals[1],
                ))
            native_index += 1
    if seen != known_tokens:
        raise SourcePrimaryLeagueFixturesError(
            "Source primary linked buckets omit live selected-League fixture tokens"
        )
    return SourcePrimaryLeagueFixtures(
        competition_id=competition_id,
        member_club_ids=member_club_ids,
        scheduled_matchday_count=scheduled_matchday_count,
        schedule_cycle_count=cycles,
        matrix_layer_count=layers,
        fixtures_in_source_order=tuple(ordered),
    )
