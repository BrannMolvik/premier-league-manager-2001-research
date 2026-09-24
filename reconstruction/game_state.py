from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from random import Random
from typing import Callable, Iterable

from competition_state import PremierLeagueState
from runtime_state import RuntimePlayer


DateHook = Callable[[date], None]


@dataclass
class GameCalendar:
    current_date: date
    daily_hooks: list[DateHook] = field(default_factory=list)
    monthly_hooks: list[DateHook] = field(default_factory=list)

    def advance_one_day(self) -> date:
        self.current_date += timedelta(days=1)
        for hook in tuple(self.daily_hooks):
            hook(self.current_date)
        if self.current_date.day == 1:
            for hook in tuple(self.monthly_hooks):
                hook(self.current_date)
        return self.current_date

    def advance(self, days: int) -> date:
        if days < 0:
            raise ValueError("days must be non-negative")
        for _ in range(days):
            self.advance_one_day()
        return self.current_date


@dataclass
class GameState:
    calendar: GameCalendar
    players: dict[int, RuntimePlayer]
    premier_league: PremierLeagueState | None = None
    monthly_player_updates: int = 0

    @classmethod
    def from_database(cls, database, start_date: date, seed: int | None = None) -> "GameState":
        rng = Random(seed)
        players = {
            p.index: RuntimePlayer.from_database_player(p, start_date, rng)
            for p in database.players
        }
        fixtures = getattr(database, "real_fixtures", ())
        league = PremierLeagueState(fixtures) if fixtures else None
        state = cls(
            calendar=GameCalendar(start_date),
            players=players,
            premier_league=league,
        )
        state.calendar.monthly_hooks.append(state._run_monthly_player_development)
        return state

    @classmethod
    def from_players(
        cls,
        players: Iterable[RuntimePlayer],
        start_date: date,
    ) -> "GameState":
        state = cls(
            calendar=GameCalendar(start_date),
            players={p.index: p for p in players},
        )
        state.calendar.monthly_hooks.append(state._run_monthly_player_development)
        return state

    def _run_monthly_player_development(self, on_date: date) -> None:
        updated = 0
        for player in self.players.values():
            updated += int(player.monthly_development_update(on_date))
        self.monthly_player_updates += updated

    def advance_one_day(self) -> date:
        return self.calendar.advance_one_day()

    def advance(self, days: int) -> date:
        return self.calendar.advance(days)

    def record_premier_league_result(self, fixture_id: int, home_goals: int, away_goals: int):
        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")
        return self.premier_league.record_result(fixture_id, home_goals, away_goals)

    def premier_league_table(self):
        if self.premier_league is None:
            return ()
        return self.premier_league.table()
