from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from time import time
from typing import Callable, Iterable

from competition_state import PremierLeagueState
from match_condition import ConditionInjurySettings
from match_environment import (
    MatchEnvironment,
    generate_match_environment,
    pitch_wear_after_match,
    recover_ai_pitch_wear,
)
from match_injury_persistence import clear_expired_persistent_injury
from match_schedule import MsvcCrtRng
from match_preparation import (
    PreparedAiMatchSelection,
    PreparedPremierLeagueAiSide,
    build_prepared_match_side_from_selection,
    build_premier_league_ai_match_side,
    prepare_premier_league_ai_selection,
)
from match_postmatch import (
    persist_post_match_form,
    persist_premier_league_match_incidents,
    sync_post_match_conditions,
)
from match_orders import TeamOrderPriorities
from match_simulation import PreparedMatchSide, NormalMatchResult, simulate_normal_match
from match_team_setup import TeamTacticalState
from runtime_state import RuntimePlayer, derive_non_eu_status


DateHook = Callable[[date], None]


@dataclass
class GameCalendar:
    current_date: date
    daily_hooks: list[DateHook] = field(default_factory=list)
    monthly_hooks: list[DateHook] = field(default_factory=list)

    def increment_one_day(self) -> date:
        """Move the calendar date without running post-fixture maintenance."""
        self.current_date += timedelta(days=1)
        return self.current_date

    def run_post_fixture_maintenance(self) -> date:
        """Run the reconstructed 0x4A8070-era day maintenance subset."""
        for hook in tuple(self.daily_hooks):
            hook(self.current_date)
        if self.current_date.day == 1:
            for hook in tuple(self.monthly_hooks):
                hook(self.current_date)
        return self.current_date

    def advance_one_day(self) -> date:
        """Advance a fixture-free day and run its post-fixture maintenance."""
        self.increment_one_day()
        return self.run_post_fixture_maintenance()

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
    premier_league_scheduler_order: dict[int, tuple[int, ...]] = field(default_factory=dict)
    rng: MsvcCrtRng | None = None

    def _resolve_rng(self, rng=None):
        if rng is not None:
            return rng
        if self.rng is None:
            raise RuntimeError(
                "no shared game RNG is attached; pass rng explicitly or build "
                "the state with GameState.from_database"
            )
        return self.rng

    @classmethod
    def from_database(
        cls,
        database,
        start_date: date,
        seed: int | None = None,
        season_year: int | None = None,
    ) -> "GameState":
        if seed is None:
            seed = int(time())
        rng = MsvcCrtRng(int(seed))
        source_players = tuple(database.players)
        clubs = tuple(getattr(database, "clubs", ()))
        countries = tuple(getattr(database, "countries", ()))
        financial_values = tuple(
            getattr(database, "access_skill_financial_values", ())
        )
        clubs_by_id_for_wage = {int(club.index): club for club in clubs}
        countries_by_id_for_wage = {
            int(country.id): country
            for country in countries
            if hasattr(country, "id")
        }

        # DBTPlayers 0x421C80 constructs the complete player array before its
        # load pass. Therefore all constructor RNG(15) morale draws precede
        # every player's wage, peak-age and contract-span draws.
        constructor_morales = tuple(100 - rng.randbelow(15) for _ in source_players)

        def build_player(p, constructor_morale):
            multiplier = 100
            club = clubs_by_id_for_wage.get(int(p.club_id))
            if club is not None:
                country = countries_by_id_for_wage.get(int(club.country_id))
                if country is not None:
                    multiplier = int(
                        getattr(country, "financial_multiplier_percent", 100)
                    )
            return RuntimePlayer.from_database_player(
                p,
                start_date,
                rng,
                constructor_morale=constructor_morale,
                financial_values=financial_values,
                country_multiplier_percent=multiplier,
            )

        players = {
            p.index: build_player(p, constructor_morale)
            for p, constructor_morale in zip(source_players, constructor_morales)
        }

        # Original startup 0x421CE0 derives DBRPlayer +0x14 bit 11 (Non-EU)
        # after player and club/country tables are loaded. Keep lightweight fake
        # databases compatible by applying this only when those exact tables are
        # available.
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
        for source_player in source_players:
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
            rng=rng,
        )
        state.calendar.daily_hooks.append(state._run_daily_injury_returns)
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
        state.calendar.daily_hooks.append(state._run_daily_injury_returns)
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

    def _run_daily_injury_returns(self, on_date: date) -> None:
        """Clear persistent injury state when the scheduled return date arrives."""
        for player in self.players.values():
            clear_expired_persistent_injury(player, on_date)

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

    def install_premier_league_scheduler_order(
        self,
        order_by_round: Iterable[tuple[int, Iterable[int]]],
    ) -> None:
        """Install exact shuffled ScheduleContainer order for PL rounds.

        Gate 4 reconstructs the fixed-League fixture order by scanning the
        shuffled primary container in 0x615C10 head-to-tail traversal order.
        Each supplied round must contain exactly that round's fixture IDs once.
        """

        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")

        normalized: dict[int, tuple[int, ...]] = {}
        for round_index, fixture_ids in order_by_round:
            round_index = int(round_index)
            ids = tuple(int(fixture_id) for fixture_id in fixture_ids)
            expected = {
                int(fixture.id)
                for fixture in self.premier_league.fixtures_for_round(round_index)
            }
            if (
                len(ids) != len(set(ids))
                or set(ids) != expected
            ):
                raise ValueError(
                    f"scheduler order for round {round_index} must contain "
                    "each round fixture exactly once"
                )
            normalized[round_index] = ids

        self.premier_league_scheduler_order = normalized

    def due_premier_league_fixture_ids_in_scheduler_order(self) -> tuple[int, ...]:
        """Return today's unplayed PL fixtures in recovered scheduler order.

        Installed Gate-4 round order is preferred. A round without installed
        scheduler state retains PremierLeagueState.fixtures_on()'s stable
        fixture-ID fallback so lightweight/synthetic callers remain usable.
        """

        due = tuple(self.fixtures_due_today())
        if not due:
            return ()

        due_ids = {int(fixture.id) for fixture in due}
        by_round: dict[int, set[int]] = {}
        for fixture in due:
            by_round.setdefault(int(fixture.round_index), set()).add(
                int(fixture.id)
            )

        ordered: list[int] = []
        covered: set[int] = set()
        if self.premier_league is not None:
            round_order = tuple(self.premier_league.round_source_order)
        else:
            round_order = ()

        for round_index in round_order:
            round_due = by_round.get(int(round_index))
            if not round_due:
                continue
            installed = self.premier_league_scheduler_order.get(int(round_index))
            if installed is None:
                fallback = tuple(
                    int(fixture.id)
                    for fixture in due
                    if int(fixture.round_index) == int(round_index)
                )
                ordered.extend(fallback)
                covered.update(fallback)
                continue

            selected = tuple(
                fixture_id
                for fixture_id in installed
                if fixture_id in round_due
            )
            ordered.extend(selected)
            covered.update(selected)

        # Synthetic callers can omit DBTRounds; preserve the existing due-list
        # fallback for any fixture not covered by round_source_order.
        ordered.extend(
            int(fixture.id)
            for fixture in due
            if int(fixture.id) not in covered
        )

        if set(ordered) != due_ids or len(ordered) != len(due_ids):
            raise RuntimeError("installed Premier League scheduler order is inconsistent")
        return tuple(ordered)

    def simulate_due_premier_league_ai_fixtures(
        self,
        attack_matrix,
        defence_matrix,
        rng=None,
        *,
        fixture_order: Iterable[int] | None = None,
    ) -> tuple[tuple[int, NormalMatchResult], ...]:
        """Simulate every unplayed Premier League fixture due on the current date.

        The executable walks a shuffled per-date linked list. When Gate-4
        scheduler order has been installed, that recovered order is used by
        default. Lightweight/synthetic callers without installed scheduler
        state retain PremierLeagueState.fixtures_on()'s stable fixture-ID
        fallback. An explicit fixture_order still overrides both.
        """
        rng = self._resolve_rng(rng)
        due_ids = tuple(int(fixture.id) for fixture in self.fixtures_due_today())
        if fixture_order is None:
            ordered_ids = self.due_premier_league_fixture_ids_in_scheduler_order()
        else:
            ordered_ids = tuple(int(fixture_id) for fixture_id in fixture_order)
            if (
                len(ordered_ids) != len(set(ordered_ids))
                or set(ordered_ids) != set(due_ids)
            ):
                raise ValueError(
                    "fixture_order must contain each fixture due today exactly once"
                )

        return tuple(
            (
                fixture_id,
                self.simulate_premier_league_ai_fixture(
                    fixture_id,
                    attack_matrix,
                    defence_matrix,
                    rng,
                ),
            )
            for fixture_id in ordered_ids
        )

    def advance_one_day_with_premier_league_ai_fixtures(
        self,
        attack_matrix,
        defence_matrix,
        rng=None,
        *,
        fixture_order: Iterable[int] | None = None,
    ) -> tuple[tuple[int, NormalMatchResult], ...]:
        """Advance one day using the recovered fast-calendar phase order.

        The proven ordering is date increment -> due fixtures -> the reconstructed
        post-fixture day-maintenance subset. In particular, injury return events
        on the new date are processed only after that date's fixtures, followed
        by daily AI Pitch Wear recovery and then first-of-month development.
        """
        rng = self._resolve_rng(rng)
        self.calendar.increment_one_day()
        results = self.simulate_due_premier_league_ai_fixtures(
            attack_matrix,
            defence_matrix,
            rng,
            fixture_order=fixture_order,
        )
        self.calendar.run_post_fixture_maintenance()
        return results

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
        rng=None,
    ) -> tuple[PreparedPremierLeagueAiSide, PreparedPremierLeagueAiSide]:
        """Prepare both AI sides in the original shared fixture RNG order.

        The original high-level order is:
        both AI selections -> weather -> home AI Condition -> away AI Condition.
        """
        rng = self._resolve_rng(rng)
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
        rng=None,
    ) -> NormalMatchResult:
        """Prepare two AI clubs, simulate the due fixture, and store its result."""
        rng = self._resolve_rng(rng)
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

        # MatchCalculator mutates DBRPlayer Condition in-place in the original.
        # Our calculator uses prepared copies, so synchronize both participant
        # arrays before the 0x5127A0 incident persistence loop can apply an
        # additional injury Condition drop.
        sync_post_match_conditions(
            home.match_side,
            home.preparation.selection.participants,
        )
        sync_post_match_conditions(
            away.match_side,
            away.preparation.selection.participants,
        )

        # Exact participant-order persistence:
        # old bans -> each player's cards then injury -> next-fixture ban state.
        # This preserves red RNG(3) / injury RNG interleaving.
        persist_premier_league_match_incidents(
            self.ordered_club_roster(home_club_id),
            home.preparation.selection.participants,
            0,
            result,
            fixture_date,
            home_next,
            rng,
            user_controlled=False,
        )
        persist_premier_league_match_incidents(
            self.ordered_club_roster(away_club_id),
            away.preparation.selection.participants,
            1,
            result,
            fixture_date,
            away_next,
            rng,
            user_controlled=False,
        )

        # 0x404D40 updates only the home club's pitch after incident handling.
        self.pitch_wear[home_club_id] = pitch_wear_after_match(
            pitch_wear_before,
            environment.weather_code,
        )

        # The later player pass runs Form only. It must not re-copy Condition,
        # which would erase the persistent injury finalizer's Condition loss.
        persist_post_match_form(
            home.match_side,
            home.preparation.selection.participants,
            result,
            rng,
        )
        persist_post_match_form(
            away.match_side,
            away.preparation.selection.participants,
            result,
            rng,
        )
        return result

    def simulate_premier_league_human_fixture(
        self,
        fixture_id: int,
        human_club_id: int,
        human_selection: PreparedAiMatchSelection,
        attack_matrix,
        defence_matrix,
        rng=None,
        *,
        team_orders: TeamOrderPriorities | None = None,
    ) -> NormalMatchResult:
        """Simulate one human-vs-AI PL fixture through the shared backend.

        Human selection/tactics remain persistent runtime state. The opponent
        uses the same autonomous preparation path as AI-vs-AI fixtures. Match
        simulation and every post-match persistence helper are shared with the
        established backend; the only control distinction is the exact
        user_controlled flag passed into match-side/treatment paths.
        """
        rng = self._resolve_rng(rng)
        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")

        fixture_id = int(fixture_id)
        human_club_id = int(human_club_id)
        if fixture_id not in self.premier_league.fixtures:
            raise KeyError(fixture_id)
        fixture = self.premier_league.fixtures[fixture_id]
        home_club_id = int(fixture.home_club_id)
        away_club_id = int(fixture.away_club_id)
        if human_club_id not in (home_club_id, away_club_id):
            raise ValueError("human club does not participate in this fixture")

        competition = self.competitions.get(0)
        if competition is None:
            raise RuntimeError("Premier League competition definition is not loaded")

        human_is_home = human_club_id == home_club_id
        ai_club_id = away_club_id if human_is_home else home_club_id
        ai_club = self.clubs.get(ai_club_id)
        if ai_club is None:
            raise RuntimeError(f"club definition {ai_club_id} is not loaded")
        ai_manager = self.managers.get(int(ai_club.manager_id))
        if ai_manager is None:
            raise RuntimeError(
                f"manager {int(ai_club.manager_id)} for club {ai_club_id} is not loaded"
            )

        human_roster = self.ordered_club_roster(human_club_id)
        ai_roster = self.ordered_club_roster(ai_club_id)
        if not human_roster or not ai_roster:
            raise RuntimeError("human/AI fixture requires both runtime rosters")

        ai_preparation = prepare_premier_league_ai_selection(
            ai_club_id,
            ai_roster,
            human_roster,
            ai_manager,
            competition,
            self.premier_league.table(),
            is_home=not human_is_home,
        )

        # Original high-level setup performs both selections before weather.
        # User Condition is persistent; only the autonomous side receives the
        # recovered OppMinVal + RNG(6) + RNG(5) pre-match overwrite.
        environment = generate_match_environment(
            self.calendar.current_date,
            rng,
        )
        self.prepared_match_environments[fixture_id] = environment

        ai_prepared = build_premier_league_ai_match_side(
            ai_preparation,
            ai_roster,
            side=1 if human_is_home else 0,
            rng=rng,
            tactical_state=self.team_tactics.get(
                ai_club_id,
                TeamTacticalState(),
            ),
        )
        human_side = build_prepared_match_side_from_selection(
            human_selection,
            0 if human_is_home else 1,
            self.team_tactics.get(
                human_club_id,
                TeamTacticalState(),
            ),
            user_controlled=True,
            team_orders=team_orders or TeamOrderPriorities(),
        )

        if human_is_home:
            home_side = human_side
            away_side = ai_prepared.match_side
            home_participants = human_selection.participants
            away_participants = ai_preparation.selection.participants
            home_user_controlled = True
            away_user_controlled = False
        else:
            home_side = ai_prepared.match_side
            away_side = human_side
            home_participants = ai_preparation.selection.participants
            away_participants = human_selection.participants
            home_user_controlled = False
            away_user_controlled = True

        pitch_wear_before = int(self.pitch_wear.get(home_club_id, 0))
        result = self.simulate_premier_league_fixture(
            fixture_id,
            home_side,
            away_side,
            attack_matrix,
            defence_matrix,
            rng,
            condition_injury_settings=ConditionInjurySettings(
                environment_byte=pitch_wear_before,
            ),
        )

        fixture_date = self.calendar.current_date
        home_next = self.premier_league.next_club_match_date(
            home_club_id,
            after_date=fixture_date,
        )
        away_next = self.premier_league.next_club_match_date(
            away_club_id,
            after_date=fixture_date,
        )

        sync_post_match_conditions(home_side, home_participants)
        sync_post_match_conditions(away_side, away_participants)

        persist_premier_league_match_incidents(
            self.ordered_club_roster(home_club_id),
            home_participants,
            0,
            result,
            fixture_date,
            home_next,
            rng,
            user_controlled=home_user_controlled,
        )
        persist_premier_league_match_incidents(
            self.ordered_club_roster(away_club_id),
            away_participants,
            1,
            result,
            fixture_date,
            away_next,
            rng,
            user_controlled=away_user_controlled,
        )

        self.pitch_wear[home_club_id] = pitch_wear_after_match(
            pitch_wear_before,
            environment.weather_code,
        )

        persist_post_match_form(
            home_side,
            home_participants,
            result,
            rng,
        )
        persist_post_match_form(
            away_side,
            away_participants,
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
        rng=None,
        *,
        condition_injury_settings: ConditionInjurySettings | None = None,
    ) -> NormalMatchResult:
        """Simulate one fixture due today and persist its result into league state.

        The caller supplies the recovered match-day player/tactic state explicitly;
        this method does not invent a lineup, Condition, Form, or Team Orders.
        """
        rng = self._resolve_rng(rng)
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
