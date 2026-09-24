from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class FixtureSource(Protocol):
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


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
    """Mutable result/table state over FM2001's verified 380-match PL fixture list."""

    def __init__(self, fixtures: Iterable[FixtureSource]):
        self.fixtures = {f.id: f for f in fixtures}
        club_ids = {
            club_id
            for f in self.fixtures.values()
            for club_id in (f.home_club_id, f.away_club_id)
        }
        self.club_ids = tuple(sorted(club_ids))
        self.results: dict[int, MatchResult] = {}

    def fixtures_for_round(self, round_index: int):
        return tuple(
            sorted(
                (f for f in self.fixtures.values() if f.round_index == round_index),
                key=lambda f: f.id,
            )
        )

    def record_result(self, fixture_id: int, home_goals: int, away_goals: int) -> MatchResult:
        if fixture_id not in self.fixtures:
            raise KeyError(fixture_id)
        if fixture_id in self.results:
            raise ValueError(f"fixture {fixture_id} already has a result")
        result = MatchResult(fixture_id, int(home_goals), int(away_goals))
        self.results[fixture_id] = result
        return result

    def next_unplayed_round(self) -> int | None:
        rounds = sorted({f.round_index for f in self.fixtures.values()})
        for round_index in rounds:
            if any(f.id not in self.results for f in self.fixtures_for_round(round_index)):
                return round_index
        return None

    def table(self) -> tuple[LeagueRow, ...]:
        rows = {club_id: LeagueRow(club_id) for club_id in self.club_ids}
        for fixture_id, result in self.results.items():
            fixture = self.fixtures[fixture_id]
            rows[fixture.home_club_id].record(result.home_goals, result.away_goals)
            rows[fixture.away_club_id].record(result.away_goals, result.home_goals)

        # Isolated here because the exact FM2001 equal-points fallback beyond
        # points / goal difference / goals scored has not yet been traced.
        return tuple(sorted(
            rows.values(),
            key=lambda row: (-row.points, -row.goal_difference, -row.goals_for, row.club_id),
        ))
