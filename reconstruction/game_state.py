from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from random import Random
from typing import Callable, Iterable

from competition_state import PremierLeagueState
from match_condition import ConditionInjurySettings
from match_environment import (
    MatchEnvironment,
    generate_match_environment,
    pitch_wear_after_match,
    recover_ai_pitch_wear,
)
from match_preparation import (
    PreparedPremierLeagueAiSide,
    build_premier_league_ai_match_side,
    prepare_premier_league_ai_selection,
)
from match_postmatch import (
    persist_post_match_side,
    persist_premier_league_discipline,
)
from match_simulation import PreparedMatchSide, NormalMatchResult, simulate_normal_match
from match_team_setup import TeamTacticalState
from runtime_state import RuntimePlayer, derive_non_eu_status


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
    club_roster_order: dict[int, list[int]] = field(default_factory=dict)
    clubs: dict[int, object] = field(default_factory=dict)
    managers: dict[int, object] = field(default_factory=dict)
    competitions: dict[int, object] = field(default_factory=dict)
    team_tactics: dict[int, TeamTacticalState] = field(default_factory=dict)
    pitch_wear: dict[int, int] = field(default_factory=dict)
    prepared_match_environments: dict[int, MatchEnvironment] = field(default_factory=dict)

    @classmethod
    def from_database(
        cls,
        database,
        start_date: date,
        seed: int | None = None,
        season_year: int | None = None,
    ) -> "GameState":
        rng = Random(seed)
        players = {
            p.index: RuntimePlayer.from_database_player(p, start_date, rng)
            for p in database.players
        }

        # Original startup 0x421CE0 derives DBRPlayer +0x14 bit 11 (Non-EU)
        # after player and club/country tables are loaded. Keep lightweight fake
        # databases compatible by applying this only when those exact tables are
        # available.
        clubs = tuple(getattr(database, "clubs", ()))
        countries = tuple(getattr(database, "countries", ()))
        if clubs and countries:
            clubs_by_id = {int(club.index): club for club in clubs}
            countries_by_nationality = {
                int(country.nationality_id): country
                for country in countries
            }
            for player in players.values():
                club = clubs_by_id[int(player.club_id)]
                nationality_country = countries_by_nationality.get(
                    int(player.nationality_id)
                )
                player.non_eu = derive_non_eu_status(
                    int(club.country_id),
                    int(player.eu_status_code),
                    nationality_country,
                )

        fixtures = getattr(database, "real_fixtures", ())
        rounds = getattr(database, "premier_league_rounds", ())
        if season_year is None:
            season_year = start_date.year if start_date.month >= 7 else start_date.year - 1
        league = PremierLeagueState(fixtures, rounds, season_year) if fixtures else None
        roster_order: dict[int, list[int]] = {}
        for source_player in database.players:
            roster_order.setdefault(int(source_player.club_id), []).append(
                int(source_player.index)
            )

        clubs_by_id = {
            int(club.index): club
            for club in getattr(database, "clubs", ())
        }
        managers_by_id = {
            int(manager.index): manager
            for manager in getattr(database, "managers", ())
        }
        competitions_by_id = {
            int(competition.id): competition
            for competition in getattr(database, "competitions", ())
        }
        known_club_ids = set(roster_order) | set(clubs_by_id)
        team_tactics = {
            club_id: TeamTacticalState()
            for club_id in known_club_ids
        }
        pitch_wear = {
            club_id: 0
            for club_id in known_club_ids
        }

        state = cls(
            calendar=GameCalendar(start_date),
            players=players,
            premier_league=league,
            club_roster_order=roster_order,
            clubs=clubs_by_id,
            managers=managers_by_id,
            competitions=competitions_by_id,
            team_tactics=team_tactics,
            pitch_wear=pitch_wear,
        )
        state.calendar.daily_hooks.append(state._run_daily_ai_pitch_recovery)
        state.calendar.monthly_hooks.append(state._run_monthly_player_development)
        return state

    @classmethod
    def from_players(
        cls,
        players: Iterable[RuntimePlayer],
        start_date: date,
    ) -> "GameState":
        player_list = tuple(players)
        roster_order: dict[int, list[int]] = {}
        for player in player_list:
            roster_order.setdefault(int(player.club_id), []).append(int(player.index))
        state = cls(
            calendar=GameCalendar(start_date),
            players={p.index: p for p in player_list},
            club_roster_order=roster_order,
            team_tactics={
                club_id: TeamTacticalState()
                for club_id in roster_order
            },
            pitch_wear={
                club_id: 0
                for club_id in roster_order
            },
        )
        state.calendar.daily_hooks.append(state._run_daily_ai_pitch_recovery)
        state.calendar.monthly_hooks.append(state._run_monthly_player_development)
        return state

    def ordered_club_roster(self, club_id: int) -> tuple[RuntimePlayer, ...]:
        """Return live team-roster order matching DBRTeam +0x244 semantics."""
        club_id = int(club_id)
        ids = self.club_roster_order.get(club_id, ())
        return tuple(
            self.players[player_id]
            for player_id in ids
            if player_id in self.players
        )

    def set_team_tactics(self, club_id: int, state: TeamTacticalState) -> None:
        """Replace the live backend tactical state for one club."""
        club_id = int(club_id)
        if club_id not in self.club_roster_order and club_id not in self.clubs:
            raise KeyError(club_id)
        self.team_tactics[club_id] = state

    def _run_daily_ai_pitch_recovery(self, _on_date: date) -> None:
        """Apply the exact base PitchRecover=2 path for autonomous AI clubs."""
        for club_id, wear in tuple(self.pitch_wear.items()):
            self.pitch_wear[club_id] = recover_ai_pitch_wear(wear)

    def _run_monthly_player_development(self, on_date: date) -> None:
        self.monthly_player_updates += sum(
            int(player.monthly_development_update(on_date))
            for player in self.players.values()
        )

    def advance_one_day(self) -> date:
        return self.calendar.advance_one_day()

    def advance(self, days: int) -> date:
        return self.calendar.advance(days)

    def fixtures_due_today(self):
        if self.premier_league is None:
            return ()
        return self.premier_league.fixtures_on(self.calendar.current_date)

    def next_match_date(self) -> date | None:
        if self.premier_league is None:
            return None
        return self.premier_league.next_match_date(self.calendar.current_date)

    def record_premier_league_result(self, fixture_id: int, home_goals: int, away_goals: int):
        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")
        return self.premier_league.record_result(fixture_id, home_goals, away_goals)

    def premier_league_table(self):
        if self.premier_league is None:
            return ()
        return self.premier_league.table()

    def prepare_premier_league_ai_fixture_sides(
        self,
        fixture_id: int,
        rng,
    ) -> tuple[PreparedPremierLeagueAiSide, PreparedPremierLeagueAiSide]:
        """Prepare both AI sides in the original shared fixture RNG order.

        The original high-level order is:
        both AI selections -> weather -> home AI Condition -> away AI Condition.
        """
        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")
        fixture_id = int(fixture_id)
        if fixture_id not in self.premier_league.fixtures:
            raise KeyError(fixture_id)

        competition = self.competitions.get(0)
        if competition is None:
            raise RuntimeError(
                "Premier League competition definition is not loaded"
            )

        fixture = self.premier_league.fixtures[fixture_id]
        table = self.premier_league.table()

        def inputs_for(club_id: int, opponent_id: int):
            club_id = int(club_id)
            opponent_id = int(opponent_id)
            club = self.clubs.get(club_id)
            if club is None:
                raise RuntimeError(f"club definition {club_id} is not loaded")
            manager_id = int(club.manager_id)
            manager = self.managers.get(manager_id)
            if manager is None:
                raise RuntimeError(
                    f"manager {manager_id} for club {club_id} is not loaded"
                )
            roster = self.ordered_club_roster(club_id)
            opponent_roster = self.ordered_club_roster(opponent_id)
            if not roster:
                raise RuntimeError(f"club {club_id} has no runtime roster")
            if not opponent_roster:
                raise RuntimeError(f"club {opponent_id} has no runtime roster")
            return manager, roster, opponent_roster

        home_manager, home_roster, away_roster = inputs_for(
            fixture.home_club_id,
            fixture.away_club_id,
        )
        away_manager, away_roster_check, home_roster_check = inputs_for(
            fixture.away_club_id,
            fixture.home_club_id,
        )
        if away_roster_check != away_roster or home_roster_check != home_roster:
            raise RuntimeError("fixture roster resolution became inconsistent")

        home_preparation = prepare_premier_league_ai_selection(
            fixture.home_club_id,
            home_roster,
            away_roster,
            home_manager,
            competition,
            table,
            is_home=True,
        )
        away_preparation = prepare_premier_league_ai_selection(
            fixture.away_club_id,
            away_roster,
            home_roster,
            away_manager,
            competition,
            table,
            is_home=False,
        )

        environment = generate_match_environment(
            self.calendar.current_date,
            rng,
        )
        self.prepared_match_environments[fixture_id] = environment

        home = build_premier_league_ai_match_side(
            home_preparation,
            home_roster,
            side=0,
            rng=rng,
            tactical_state=self.team_tactics.get(
                int(fixture.home_club_id),
                TeamTacticalState(),
            ),
        )
        away = build_premier_league_ai_match_side(
            away_preparation,
            away_roster,
            side=1,
            rng=rng,
            tactical_state=self.team_tactics.get(
                int(fixture.away_club_id),
                TeamTacticalState(),
            ),
        )
        return home, away

    def simulate_premier_league_ai_fixture(
        self,
        fixture_id: int,
        attack_matrix,
        defence_matrix,
        rng,
    ) -> NormalMatchResult:
        """Prepare two AI clubs, simulate the due fixture, and store its result."""
        home, away = self.prepare_premier_league_ai_fixture_sides(fixture_id, rng)
        fixture = self.premier_league.fixtures[int(fixture_id)]
        home_club_id = int(fixture.home_club_id)
        pitch_wear_before = int(self.pitch_wear.get(home_club_id, 0))
        environment = self.prepared_match_environments[int(fixture_id)]

        result = self.simulate_premier_league_fixture(
            fixture_id,
            home.match_side,
            away.match_side,
            attack_matrix,
            defence_matrix,
            rng,
            condition_injury_settings=ConditionInjurySettings(
                environment_byte=pitch_wear_before,
            ),
        )

        fixture_date = self.calendar.current_date
        away_club_id = int(fixture.away_club_id)
        home_next = self.premier_league.next_club_match_date(
            home_club_id,
            after_date=fixture_date,
        )
        away_next = self.premier_league.next_club_match_date(
            away_club_id,
            after_date=fixture_date,
        )

        # Exact post-match order: serve old suspensions across the full roster,
        # apply this match's participant cards, then refresh next-fixture
        # availability. Red-card RNG(3) therefore precedes Form RNG(100).
        persist_premier_league_discipline(
            self.ordered_club_roster(home_club_id),
            home.preparation.selection.participants,
            0,
            result,
            fixture_date,
            home_next,
            rng,
        )
        persist_premier_league_discipline(
            self.ordered_club_roster(away_club_id),
            away.preparation.selection.participants,
            1,
            result,
            fixture_date,
            away_next,
            rng,
        )

        # 0x404D40 updates only the home club's pitch after discipline handling.
        self.pitch_wear[home_club_id] = pitch_wear_after_match(
            pitch_wear_before,
            environment.weather_code,
        )

        # The later 0x404CE0 player pass persists Condition/injury state and
        # runs post-match Form transitions on the same continuing RNG stream.
        persist_post_match_side(
            home.match_side,
            home.preparation.selection.participants,
            result,
            rng,
        )
        persist_post_match_side(
            away.match_side,
            away.preparation.selection.participants,
            result,
            rng,
        )
        return result

    def simulate_premier_league_fixture(
        self,
        fixture_id: int,
        home_side: PreparedMatchSide,
        away_side: PreparedMatchSide,
        attack_matrix,
        defence_matrix,
        rng,
        *,
        condition_injury_settings: ConditionInjurySettings | None = None,
    ) -> NormalMatchResult:
        """Simulate one fixture due today and persist its result into league state.

        The caller supplies the recovered match-day player/tactic state explicitly;
        this method does not invent a lineup, Condition, Form, or Team Orders.
        """
        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")
        if fixture_id not in self.premier_league.fixtures:
            raise KeyError(fixture_id)
        if fixture_id in self.premier_league.results:
            raise ValueError(f"fixture {fixture_id} already has a result")

        due_ids = {fixture.id for fixture in self.fixtures_due_today()}
        if fixture_id not in due_ids:
            raise ValueError(
                f"fixture {fixture_id} is not due on {self.calendar.current_date}"
            )

        result = simulate_normal_match(
            home_side,
            away_side,
            attack_matrix,
            defence_matrix,
            rng,
            condition_injury_settings=condition_injury_settings,
        )
        home_goals, away_goals = result.score
        self.premier_league.record_result(
            fixture_id,
            home_goals,
            away_goals,
        )
        return result
