from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Protocol

from match_schedule import schedule_bucket_pre_shuffle_order


class FixtureSource(Protocol):
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


class RoundSource(Protocol):
    round_number: int
    scheduled_week: int
    scheduled_weekday: int


def season_weekday_date(season_year: int, week: int, weekday: int) -> date:
    """Convert FM2001 round week/day to a Gregorian date.

    Static.dat uses weekday 1..7 = Monday..Sunday. Week 0 is the Monday-led
    week containing July 1 of the season start year. This reproduces the
    shipped 2000-01 PL dates (e.g. 7/6 -> 19 Aug 2000, 26/2 -> Boxing Day,
    27/1 -> New Year's Day, and 46/7 -> 20 May 2001).
    """
    if not 1 <= int(weekday) <= 7:
        raise ValueError("FM2001 scheduled weekday must be 1..7")
    july_first = date(int(season_year), 7, 1)
    week_zero_monday = july_first - timedelta(days=july_first.weekday())
    return week_zero_monday + timedelta(weeks=int(week), days=int(weekday) - 1)


@dataclass(frozen=True)
class MatchResult:
    fixture_id: int
    home_goals: int
    away_goals: int

    def __post_init__(self) -> None:
        if self.home_goals < 0 or self.away_goals < 0:
            raise ValueError("goals must be non-negative")


@dataclass
class LeagueRow:
    club_id: int
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def record(self, goals_for: int, goals_against: int) -> None:
        self.played += 1
        self.goals_for += goals_for
        self.goals_against += goals_against
        if goals_for > goals_against:
            self.wins += 1
            self.points += 3
        elif goals_for == goals_against:
            self.draws += 1
            self.points += 1
        else:
            self.losses += 1


class PremierLeagueState:
    """Mutable results/table state over FM2001's verified real PL schedule."""

    def __init__(
        self,
        fixtures: Iterable[FixtureSource],
        rounds: Iterable[RoundSource] = (),
        season_year: int | None = None,
    ):
        fixture_sources = tuple(fixtures)
        round_sources = tuple(rounds)
        self.fixture_source_order = tuple(int(f.id) for f in fixture_sources)
        self.fixtures = {f.id: f for f in fixture_sources}
        self.round_source_order = tuple(
            int(round_def.round_number) - 1
            for round_def in round_sources
            if 1 <= int(round_def.round_number) <= 38
        )
        if not self.round_source_order:
            # Lightweight synthetic callers sometimes omit DBTRounds. Preserve
            # first encounter order rather than inventing an ID sort.
            self.round_source_order = tuple(dict.fromkeys(
                int(f.round_index) for f in fixture_sources
            ))
        self.club_ids = tuple(sorted({
            club_id
            for f in self.fixtures.values()
            for club_id in (f.home_club_id, f.away_club_id)
        }))
        self.results: dict[int, MatchResult] = {}
        self.round_dates: dict[int, date] = {}
        if season_year is not None:
            for round_def in round_sources:
                if 1 <= round_def.round_number <= 38:
                    self.round_dates[round_def.round_number - 1] = season_weekday_date(
                        season_year,
                        round_def.scheduled_week,
                        round_def.scheduled_weekday,
                    )


    def fixed_fixture_insertion_ids(
        self,
        round_indices: Iterable[int] | None = None,
        *,
        unplayed_only: bool = False,
    ) -> tuple[int, ...]:
        """Return exact League fixed-fixture insertion order before bucketing.

        The executable attaches real-fixture pointers to each round in global
        fixture source order, then walks League rounds in round source order
        and each round's fixture list in that preserved source order. No RNG is
        consumed by the fixed builder before schedule insertion.
        """
        if round_indices is None:
            selected_rounds = self.round_source_order
        else:
            selected = {int(index) for index in round_indices}
            selected_rounds = tuple(
                index for index in self.round_source_order if index in selected
            )

        ids: list[int] = []
        for round_index in selected_rounds:
            for fixture_id in self.fixture_source_order:
                fixture = self.fixtures[fixture_id]
                if int(fixture.round_index) != int(round_index):
                    continue
                if unplayed_only and fixture_id in self.results:
                    continue
                ids.append(fixture_id)
        return tuple(ids)

    def fixed_fixture_insertion_ids_on(
        self,
        on_date: date,
        *,
        unplayed_only: bool = True,
    ) -> tuple[int, ...]:
        """Return fixed Premier League insertion order for rounds on one date."""
        due_rounds = tuple(
            round_index
            for round_index in self.round_source_order
            if self.round_dates.get(round_index) == on_date
        )
        return self.fixed_fixture_insertion_ids(
            due_rounds,
            unplayed_only=unplayed_only,
        )

    def fixed_fixture_pre_shuffle_ids_on(
        self,
        on_date: date,
        *,
        unplayed_only: bool = True,
    ) -> tuple[int, ...]:
        """Return PL-node order after head insertion, before bucket shuffle.

        This is the exact relative order of fixed Premier League nodes. Other
        competitions can share a global schedule bucket, so this deliberately
        does not claim completeness of the entire global bucket.
        """
        return schedule_bucket_pre_shuffle_order(
            self.fixed_fixture_insertion_ids_on(
                on_date,
                unplayed_only=unplayed_only,
            )
        )

    def fixtures_for_round(self, round_index: int):
        return tuple(sorted(
            (f for f in self.fixtures.values() if f.round_index == round_index),
            key=lambda f: f.id,
        ))

    def fixtures_on(self, on_date: date):
        due_rounds = {r for r, d in self.round_dates.items() if d == on_date}
        return tuple(sorted(
            (
                f for f in self.fixtures.values()
                if f.round_index in due_rounds and f.id not in self.results
            ),
            key=lambda f: f.id,
        ))

    def round_date(self, round_index: int) -> date | None:
        return self.round_dates.get(round_index)

    def next_club_match_date(
        self,
        club_id: int,
        after_date: date | None = None,
    ) -> date | None:
        """Return the next unplayed fixture date for one club.

        FM2001's post-match suspension refresh searches from current_date+1,
        so callers pass the just-played date and this helper requires a
        strictly later round date.
        """
        club_id = int(club_id)
        dates: list[date] = []
        for fixture in self.fixtures.values():
            if fixture.id in self.results:
                continue
            if club_id not in (int(fixture.home_club_id), int(fixture.away_club_id)):
                continue
            round_date = self.round_dates.get(int(fixture.round_index))
            if round_date is None:
                continue
            if after_date is not None and round_date <= after_date:
                continue
            dates.append(round_date)
        return min(dates) if dates else None
    def next_match_date(self, on_or_after: date | None = None) -> date | None:
        dates = []
        for round_index, round_date in self.round_dates.items():
            if on_or_after is not None and round_date < on_or_after:
                continue
            if any(f.id not in self.results for f in self.fixtures_for_round(round_index)):
                dates.append(round_date)
        return min(dates) if dates else None

    def record_result(self, fixture_id: int, home_goals: int, away_goals: int) -> MatchResult:
        if fixture_id not in self.fixtures:
            raise KeyError(fixture_id)
        if fixture_id in self.results:
            raise ValueError(f"fixture {fixture_id} already has a result")
        result = MatchResult(fixture_id, int(home_goals), int(away_goals))
        self.results[fixture_id] = result
        return result

    def next_unplayed_round(self) -> int | None:
        for round_index in sorted({f.round_index for f in self.fixtures.values()}):
            if any(f.id not in self.results for f in self.fixtures_for_round(round_index)):
                return round_index
        return None

    def table(self) -> tuple[LeagueRow, ...]:
        rows = {club_id: LeagueRow(club_id) for club_id in self.club_ids}
        for fixture_id, result in self.results.items():
            fixture = self.fixtures[fixture_id]
            rows[fixture.home_club_id].record(result.home_goals, result.away_goals)
            rows[fixture.away_club_id].record(result.away_goals, result.home_goals)

        # Isolated because the exact FM2001 equal-points fallback beyond
        # points / goal difference / goals scored has not yet been traced.
        return tuple(sorted(
            rows.values(),
            key=lambda row: (-row.points, -row.goal_difference, -row.goals_for, row.club_id),
        ))
