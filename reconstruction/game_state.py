from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from time import time
from typing import Callable, Iterable

from competition_state import PremierLeagueState
from finance_state import (
    BalanceRuntimeState,
    FinancialObjectiveEvaluation,
    FinancialObjectiveState,
    GATE_HOME_ACCOUNT_CATEGORY,
    GATE_VISITING_ACCOUNT_CATEGORY,
    PLAYER_COST_ACCOUNT_CATEGORY,
    TRANSFER_ACCOUNT_CATEGORY,
)
from gate_receipts import (
    FRESH_CONTROLLED_FACILITY_FACTOR,
    PREMIER_LEAGUE_SEATING_REFERENCE,
    PREMIER_LEAGUE_TERRACE_REFERENCE,
    PREMIER_LEAGUE_TIER_FACTOR,
    GateReceiptResult,
    calculate_matchday_gate_receipts,
    league_end_play_factor,
    league_importance_factor,
    league_position_factor,
    ordinary_league_side_modifier,
)
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
from match_role_rating import best_preferred_role_rating
from match_simulation import PreparedMatchSide, NormalMatchResult, simulate_normal_match
from match_team_setup import TeamTacticalState
from runtime_state import RuntimePlayer, derive_non_eu_status
from stadium_state import StadiumSourceState, TicketRuntimeState
from transfer_state import TransferRuntimeState


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
    countries: dict[int, object] = field(default_factory=dict)
    positions: dict[int, object] = field(default_factory=dict)
    access_fan_bases: tuple[object, ...] = ()
    access_skill_financial_values: tuple[object, ...] = ()
    team_tactics: dict[int, TeamTacticalState] = field(default_factory=dict)
    pitch_wear: dict[int, int] = field(default_factory=dict)
    prepared_match_environments: dict[int, MatchEnvironment] = field(default_factory=dict)
    premier_league_scheduler_order: dict[int, tuple[int, ...]] = field(default_factory=dict)
    transfers: TransferRuntimeState = field(default_factory=TransferRuntimeState)
    # Original DBRUser owns Balance pointers rather than club-wide finance
    # scalars. The clean-room runtime keys materialized Balance objects by the
    # controlled club they belong to. Fresh controlled-club cash comes from
    # Master.dat club +165 -> DBRClub +0xD0/+0xD4 -> Balance +0x10.
    finance_balances: dict[int, BalanceRuntimeState] = field(default_factory=dict)
    stadium_sources: dict[int, StadiumSourceState] = field(default_factory=dict)
    ticket_states: dict[int, TicketRuntimeState] = field(default_factory=dict)
    # Gate-9 source/runtime inputs for the recovered weekly club acquisition
    # path. Startup roster counts are immutable initialization baselines;
    # country gates start enabled at 0x4117C6; the neutral buy-counter byte is
    # persisted so a save/reload does not reset autonomous acquisition state.
    ai_transfer_startup_roster_count: dict[int, int] = field(default_factory=dict)
    ai_transfer_buy_counter: dict[int, int] = field(default_factory=dict)
    country_transfer_window_open: dict[int, bool] = field(default_factory=dict)
    user_controlled_club_id: int | None = None
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
        fan_bases = tuple(getattr(database, "access_fan_bases", ()))
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
        countries_by_id = {
            int(country.id): country
            for country in getattr(database, "countries", ())
            if hasattr(country, "id")
        }
        # Player position bytes are source-table indices, not Position.id
        # semantic codes. 0x4EA310 indexes the runtime Position array directly.
        positions_by_id = {
            int(index): position
            for index, position in enumerate(getattr(database, "positions", ()))
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
        ai_transfer_startup_roster_count = {
            club_id: len(roster_order.get(club_id, ()))
            for club_id in known_club_ids
        }
        ai_transfer_buy_counter = {
            club_id: 0
            for club_id in known_club_ids
        }
        country_transfer_window_open = {
            country_id: True
            for country_id in countries_by_id
        }

        state = cls(
            calendar=GameCalendar(start_date),
            players=players,
            premier_league=league,
            club_roster_order=roster_order,
            clubs=clubs_by_id,
            managers=managers_by_id,
            competitions=competitions_by_id,
            countries=countries_by_id,
            positions=positions_by_id,
            access_fan_bases=fan_bases,
            access_skill_financial_values=financial_values,
            team_tactics=team_tactics,
            pitch_wear=pitch_wear,
            ai_transfer_startup_roster_count=ai_transfer_startup_roster_count,
            ai_transfer_buy_counter=ai_transfer_buy_counter,
            country_transfer_window_open=country_transfer_window_open,
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
            ai_transfer_startup_roster_count={
                club_id: len(values)
                for club_id, values in roster_order.items()
            },
            ai_transfer_buy_counter={
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

    def run_weekly_ai_transfer_maintenance(
        self,
        rng=None,
        *,
        user_controlled_club_id: int | None = None,
    ):
        """Run the recovered Saturday 0x40DD70 autonomous acquisition pass."""
        if rng is None:
            if self.rng is None:
                return ()
            rng = self.rng
        from ai_transfers import run_weekly_ai_acquisitions

        if user_controlled_club_id is None:
            user_controlled_club_id = self.user_controlled_club_id
        return run_weekly_ai_acquisitions(
            self,
            rng,
            user_controlled_club_id=user_controlled_club_id,
        )

    def materialize_gate_source_state(
        self,
        club_id: int,
        stadium: StadiumSourceState,
        *,
        seating_reference: float,
        terrace_reference: float,
        competition_id: int = 0,
    ) -> TicketRuntimeState:
        """Attach the recovered minimum stadium/ticket state for one club.

        Reference ticket prices are explicit because 0x40CBC0 obtains them
        through the original tuning/currency path rather than a field currently
        materialized in CompetitionDefinition. Everything after those converted
        references is source-backed from the live club/league/stadium state.
        """
        club_id = int(club_id)
        competition_id = int(competition_id)
        club = self.clubs.get(club_id)
        if club is None:
            raise KeyError(club_id)

        if competition_id == 0 and self.premier_league is not None:
            league_club_ids = tuple(int(value) for value in self.premier_league.club_ids)
        else:
            league_club_ids = tuple(
                int(candidate_id)
                for candidate_id, candidate in self.clubs.items()
                if int(getattr(candidate, "competition_id", -1)) == competition_id
            )
        if club_id not in league_club_ids:
            raise ValueError(
                f"club {club_id} is not in competition {competition_id}"
            )

        target_fan_base_index = int(getattr(club, "fan_base_index"))
        rank_count = sum(
            int(getattr(self.clubs[candidate_id], "fan_base_index"))
            <= target_fan_base_index
            for candidate_id in league_club_ids
        )

        tickets = TicketRuntimeState.from_stadium(stadium)
        tickets.allocate_visiting_sections(
            stadium,
            int(getattr(club, "runtime_value_1c_source")),
        )
        tickets.initialize_ordinary_prices(
            seating_reference=seating_reference,
            terrace_reference=terrace_reference,
            fan_base_rank_count=rank_count,
            league_team_count=len(league_club_ids),
        )
        self.stadium_sources[club_id] = stadium
        self.ticket_states[club_id] = tickets
        return tickets

    def initialize_controlled_club_balance(
        self,
        club_id: int,
    ) -> BalanceRuntimeState:
        """Materialize fresh DBRUser Balance cash from the original club field.

        Master.dat club +165 is copied to DBRClub +0xD0/+0xD4. Fresh-user
        initializer 0x425680 passes that double through the standard-build
        finance conversion (currency factor 1.0) and stores it at active
        Balance +0x10. Existing runtime Balance state is preserved.
        """
        club_id = int(club_id)
        club = self.clubs.get(club_id)
        if club is None:
            raise KeyError(club_id)
        if club_id in self.finance_balances:
            self.user_controlled_club_id = club_id
            return self.finance_balances[club_id]
        if not hasattr(club, "starting_cash"):
            raise RuntimeError(
                f"club {club_id} has no source-backed starting cash"
            )
        amount = float(getattr(club, "starting_cash"))
        objective = None
        if self.premier_league is not None:
            league_club_ids = tuple(int(value) for value in self.premier_league.club_ids)
            if club_id in league_club_ids and hasattr(club, "fan_base_index"):
                target_fan_base_index = int(getattr(club, "fan_base_index"))
                rank_count = sum(
                    int(getattr(self.clubs[candidate_id], "fan_base_index"))
                    <= target_fan_base_index
                    for candidate_id in league_club_ids
                )
                objective = FinancialObjectiveState(
                    base_cash=amount,
                    candidate_ids=FinancialObjectiveState.premier_league_candidates(
                        rank_count,
                        len(league_club_ids),
                    ),
                )
        balance = BalanceRuntimeState(
            current_cash=amount,
            financial_objective=objective,
        )
        self.finance_balances[club_id] = balance
        self.user_controlled_club_id = club_id
        return balance

    def financial_objective_candidates(self, club_id: int) -> tuple[int, int, int]:
        """Return the recovered fresh candidate IDs for a controlled PL club."""
        club_id = int(club_id)
        balance = self.finance_balances.get(club_id)
        if balance is None or balance.financial_objective is None:
            raise RuntimeError(f"financial objective is not initialized for club {club_id}")
        return balance.financial_objective.candidate_ids

    def select_financial_objective(
        self,
        club_id: int,
        candidate_index: int,
    ) -> int | float:
        """Choose one chairman objective and replace live cash as 0x5DFB90 does."""
        club_id = int(club_id)
        balance = self.finance_balances.get(club_id)
        if balance is None or balance.financial_objective is None:
            raise RuntimeError(f"financial objective is not initialized for club {club_id}")
        replacement_cash = balance.financial_objective.select(
            int(candidate_index),
            self.calendar.current_date,
        )
        balance.current_cash = replacement_cash
        return replacement_cash

    def set_financial_objective_progression_gate(
        self,
        club_id: int,
        reached: bool = True,
    ) -> None:
        """Set the recovered objective +0x68 progression gate explicitly.

        The original flips this during later competition/season progression,
        not during objective selection. Keeping it explicit prevents an invented
        early reason-5 evaluation until that broader transition is integrated.
        """
        club_id = int(club_id)
        balance = self.finance_balances.get(club_id)
        if balance is None or balance.financial_objective is None:
            raise RuntimeError(f"financial objective is not initialized for club {club_id}")
        balance.financial_objective.progression_gate_reached = bool(reached)
        if reached:
            balance.financial_objective.progression_state = (
                int(balance.financial_objective.progression_state) + 1
            ) & 0xFF

    def evaluate_financial_objective(
        self,
        club_id: int,
    ) -> FinancialObjectiveEvaluation | None:
        """Evaluate the recovered chairman objective against current Balance cash."""
        club_id = int(club_id)
        balance = self.finance_balances.get(club_id)
        if balance is None or balance.financial_objective is None:
            raise RuntimeError(f"financial objective is not initialized for club {club_id}")
        return balance.financial_objective.evaluate(
            balance.current_cash,
            self.calendar.current_date,
        )

    def run_premier_league_financial_objective_season_transition(
        self,
    ) -> FinancialObjectiveEvaluation | None:
        """Run the recovered same-PL sporting objective at season finalization.

        Original 0x4A8628 reaches 0x5E1C00/0x5E0310 at the annual competition
        transition. This clean-room slice intentionally covers only the
        same-Premier-League branches reachable from fresh PL candidates
        13/1/5. Broader promotion/relegation classification routes remain
        deferred with broader competition season transitions.
        """
        if self.premier_league is None or self.user_controlled_club_id is None:
            return None
        if len(self.premier_league.results) != len(self.premier_league.fixtures):
            return None

        club_id = int(self.user_controlled_club_id)
        balance = self.finance_balances.get(club_id)
        if balance is None or balance.financial_objective is None:
            return None
        objective = balance.financial_objective
        if (
            not objective.active
            or objective.selected_objective_id == 0
            or objective.selected_on is None
        ):
            return None

        # 0x5E1C00 skips the sporting-progression check in the same calendar
        # year as objective selection and once +0x68 has already been set.
        if (
            int(self.calendar.current_date.year) != int(objective.selected_on.year)
            and not objective.progression_gate_reached
        ):
            table = tuple(self.premier_league.table())
            table_index = next(
                (
                    index
                    for index, row in enumerate(table)
                    if int(row.club_id) == club_id
                ),
                None,
            )
            if table_index is None:
                raise RuntimeError(
                    f"controlled club {club_id} is absent from Premier League table"
                )

            objective_id = int(objective.selected_objective_id)
            achieved = False
            if objective_id == 13:
                achieved = table_index < 1
            elif objective_id == 1:
                achieved = table_index <= 1
            elif objective_id == 5:
                # Preserve the original inclusive midpoint comparison exactly.
                achieved = table_index <= len(table) // 2
            elif objective_id == 6:
                # 0x5E07E4 succeeds when the current competition
                # classification is unchanged or improved from the objective's
                # selected competition. The current clean-room season slice
                # does not yet perform relegation/promotion transitions, so a
                # club still in the Premier League satisfies this branch.
                achieved = True
            else:
                # Broader competition/objective branches are intentionally not
                # approximated in the Premier League-only season slice.
                return objective.evaluate(
                    balance.current_cash,
                    self.calendar.current_date,
                )

            if achieved:
                objective.progression_gate_reached = True
                objective.progression_state = (
                    int(objective.progression_state) + 1
                ) & 0xFF

        # 0x426220 -> 0x5E1D90 is the annual objective evaluation. Its own
        # year gate makes this a no-op until the exact three-year deadline year.
        return objective.evaluate(
            balance.current_cash,
            self.calendar.current_date,
        )

    def set_current_cash(self, club_id: int, amount: int) -> BalanceRuntimeState:
        """Materialize/update the active Balance current-cash qword for a club."""
        club_id = int(club_id)
        amount = int(amount)
        if club_id not in self.clubs and club_id not in self.club_roster_order:
            raise KeyError(club_id)
        balance = self.finance_balances.get(club_id)
        if balance is None:
            balance = BalanceRuntimeState(current_cash=amount)
            self.finance_balances[club_id] = balance
        else:
            balance.current_cash = amount
        return balance

    def current_cash(self, club_id: int) -> int:
        club_id = int(club_id)
        try:
            return int(self.finance_balances[club_id].current_cash)
        except KeyError as exc:
            raise RuntimeError(
                f"current cash is not initialized for club {club_id}"
            ) from exc

    def can_afford_current_cash(self, club_id: int, amount: int) -> bool:
        club_id = int(club_id)
        try:
            balance = self.finance_balances[club_id]
        except KeyError as exc:
            raise RuntimeError(
                f"current cash is not initialized for club {club_id}"
            ) from exc
        return bool(balance.can_afford(int(amount)))

    def post_transfer_cash(
        self,
        *,
        buyer_club_id: int,
        seller_club_id: int,
        amount: int,
    ) -> None:
        """Apply the recovered category-1000 transfer cash postings.

        Original wrappers resolve a Balance only for a user-controlled club.
        The reconstruction therefore posts only to materialized Balance objects:
        a controlled buyer is debited and a controlled seller is credited.
        """
        buyer_club_id = int(buyer_club_id)
        seller_club_id = int(seller_club_id)
        amount = int(amount)
        if amount <= 0:
            # Movement sentinels/free transfers are not cash postings.
            return
        buyer = self.finance_balances.get(buyer_club_id)
        if buyer is not None:
            buyer.debit(
                amount,
                category=TRANSFER_ACCOUNT_CATEGORY,
                posting_date=self.calendar.current_date,
            )
        seller = self.finance_balances.get(seller_club_id)
        if seller is not None:
            seller.credit(
                amount,
                category=TRANSFER_ACCOUNT_CATEGORY,
                posting_date=self.calendar.current_date,
            )

    def _premier_league_gate_fan_base_raw(self, club_id: int) -> float:
        """Resolve DBRAccessFanBase +0x08 from the club's +0x70 table index."""
        club = self.clubs.get(int(club_id))
        if club is None:
            raise RuntimeError(f"club definition {int(club_id)} is not loaded")
        index = int(getattr(club, "fan_base_index"))
        if not 0 <= index < len(self.access_fan_bases):
            raise RuntimeError(f"fan-base row {index} is unavailable")
        row = self.access_fan_bases[index]
        if int(getattr(row, "id", index)) != index:
            raise RuntimeError("AccessFanBase rows are not indexed by club fan-base ID")
        values = tuple(getattr(row, "values"))
        if not values:
            raise RuntimeError(f"fan-base row {index} has no +0x08 scalar")
        return float(values[0])

    def _premier_league_importance_factor(self) -> float:
        """Resolve the exact 0x4FA670 hierarchy term from parsed competitions."""
        competition = self.competitions.get(0)
        if competition is None:
            raise RuntimeError("Premier League competition definition is not loaded")
        region_id = int(getattr(competition, "country_region_id"))
        roots = tuple(
            candidate
            for candidate in self.competitions.values()
            if getattr(candidate, "parent_competition_id", None) is None
            and int(getattr(candidate, "country_region_id", -1)) == region_id
        )
        if not roots:
            raise RuntimeError("Premier League country root-competition list is unavailable")
        runtime_orders = tuple(
            -int(getattr(candidate, "initialization_order_value"))
            for candidate in roots
        )
        return league_importance_factor(
            current_runtime_order=-int(getattr(competition, "initialization_order_value")),
            first_runtime_order=min(runtime_orders),
            competition_count=len(roots),
        )

    def _premier_league_gate_side_modifier(
        self,
        club_id: int,
        participants,
    ) -> float:
        """Resolve the ordinary 0x5DBA60 side modifier from live PL state."""
        if self.premier_league is None:
            raise RuntimeError("Premier League state is not loaded")
        table = self.premier_league.table()
        club_id = int(club_id)
        try:
            table_index = next(
                index for index, row in enumerate(table)
                if int(row.club_id) == club_id
            )
        except StopIteration as exc:
            raise RuntimeError(f"club {club_id} is absent from the Premier League table") from exc
        row = table[table_index]
        team_count = len(table)
        competition = self.competitions.get(0)
        total_matches = int(getattr(competition, "scheduled_matchday_count", 38))
        if total_matches <= 0:
            total_matches = 38
        games_remaining = total_matches - int(row.played)
        position = league_position_factor(
            table_index=table_index,
            team_count=team_count,
            games_played=int(row.played),
            games_remaining=games_remaining,
        )

        # The shipped Premier League has no upward promotion/playoff boundary
        # and three direct relegation places. 0x4F8C50 therefore exposes the
        # title gap first, followed (when positive/reachable) by the safety gap
        # to the last non-relegation row.
        leader_gap = int(table[0].points) - int(row.points)
        safety_index = max(0, team_count - 3 - 1)
        safety_gap = int(table[safety_index].points) - int(row.points)
        end_play = league_end_play_factor(
            games_remaining=games_remaining,
            objective_gaps=(
                (True, leader_gap, 1.0),
                (team_count >= 4, safety_gap, 0.3),
            ),
        )

        starters = tuple(
            player for player in participants if bool(getattr(player, "match_active", False))
        )
        if len(starters) != 11:
            raise RuntimeError(
                f"club {club_id} must have exactly 11 active starters for gate prestige"
            )
        ratings = tuple(
            best_preferred_role_rating(player.current_raw, player.positions)
            for player in starters
        )
        return ordinary_league_side_modifier(
            first_xi_ratings=ratings,
            end_play_factor=end_play,
            position_factor=position,
            importance_factor=self._premier_league_importance_factor(),
        )

    def _prepare_premier_league_gate_inputs(
        self,
        home_club_id: int,
        away_club_id: int,
        home_participants,
        away_participants,
        *,
        controlled_club_id: int | None,
    ) -> dict[str, object] | None:
        """Snapshot all non-RNG gate inputs before the current result is recorded."""
        home_club_id = int(home_club_id)
        away_club_id = int(away_club_id)
        if controlled_club_id is None or home_club_id != int(controlled_club_id):
            return None
        if home_club_id not in self.finance_balances:
            return None
        stadium = self.stadium_sources.get(home_club_id)
        tickets = self.ticket_states.get(home_club_id)
        if stadium is None or tickets is None:
            return None

        home_capacity = tickets.capacity(stadium, 0)
        visiting_capacity = tickets.capacity(stadium, 1)
        return {
            "home_fan_base_raw": self._premier_league_gate_fan_base_raw(home_club_id),
            "visiting_fan_base_raw": self._premier_league_gate_fan_base_raw(away_club_id),
            "home_tier_factor": PREMIER_LEAGUE_TIER_FACTOR,
            "visiting_tier_factor": PREMIER_LEAGUE_TIER_FACTOR,
            "home_side_modifier": self._premier_league_gate_side_modifier(
                home_club_id, home_participants
            ),
            "visiting_side_modifier": self._premier_league_gate_side_modifier(
                away_club_id, away_participants
            ),
            "seating_reference": PREMIER_LEAGUE_SEATING_REFERENCE,
            "terrace_reference": PREMIER_LEAGUE_TERRACE_REFERENCE,
            "home_seating_price_delta": float(tickets.seating_price) - PREMIER_LEAGUE_SEATING_REFERENCE,
            # Uncontrolled supporters take the original reference-price branch.
            "visiting_seating_price_delta": 0.0,
            "home_terrace_price_delta": float(tickets.terrace_price) - PREMIER_LEAGUE_TERRACE_REFERENCE,
            "visiting_terrace_price_delta": 0.0,
            "home_seating_capacity": int(home_capacity.seating),
            "visiting_seating_capacity": int(visiting_capacity.seating),
            "home_terrace_capacity": int(home_capacity.terrace),
            "visiting_terrace_capacity": int(visiting_capacity.terrace),
            "host_seating_price": int(tickets.seating_price),
            "host_terrace_price": int(tickets.terrace_price),
            # Fresh DBRUser +0x65C contains no facilities. 0x42B0E0 therefore
            # returns its exact 0.90 base until the later building system adds
            # Hotel/Club House/Parking levels.
            "home_facility_factor": FRESH_CONTROLLED_FACILITY_FACTOR,
            "visiting_facility_factor": 1.0,
            "season_ticket_quantity": int(tickets.season_ticket_quantity),
            "cup_special": False,
        }

    def _finish_premier_league_gate_receipts(
        self,
        home_club_id: int,
        prepared_inputs: dict[str, object] | None,
        rng,
    ) -> GateReceiptResult | None:
        """Consume the four post-calculator gate draws and post when materialized."""
        rand15_values = tuple(int(rng.randbelow(32768)) for _ in range(4))
        if prepared_inputs is None:
            return None
        receipts = calculate_matchday_gate_receipts(
            **prepared_inputs,
            rand15_values=rand15_values,
        )
        self.post_gate_receipts(int(home_club_id), receipts)
        return receipts

    def post_gate_receipts(
        self,
        home_club_id: int,
        receipts: GateReceiptResult,
    ) -> dict[int, int]:
        """Credit recovered category-1/2 match-day gate revenue to the host.

        Original finance wrappers post only when the host has a materialized
        user Balance. Category 1 is visiting-supporter ordinary ticket income;
        category 2 is home-supporter ordinary ticket income. Season-ticket
        quantity is attendance-only here because category 3 is a separate sale
        producer.
        """
        home_club_id = int(home_club_id)
        balance = self.finance_balances.get(home_club_id)
        if balance is None:
            return {}
        posted: dict[int, int] = {}
        visiting = max(0, int(receipts.visiting_revenue))
        home = max(0, int(receipts.home_revenue))
        if visiting:
            balance.credit(
                visiting,
                category=GATE_VISITING_ACCOUNT_CATEGORY,
                posting_date=self.calendar.current_date,
            )
            posted[GATE_VISITING_ACCOUNT_CATEGORY] = visiting
        if home:
            balance.credit(
                home,
                category=GATE_HOME_ACCOUNT_CATEGORY,
                posting_date=self.calendar.current_date,
            )
            posted[GATE_HOME_ACCOUNT_CATEGORY] = home
        return posted

    def run_weekly_player_payroll(self) -> dict[int, int]:
        """Apply the recovered Saturday category-101 player payroll debit.

        Original 0x4A8070 -> 0x40BAD0 -> 0x403C70 runs on the same
        (date + 5) % 7 == 0 phase already mapped to Saturday. Only clubs with
        a materialized/user Balance can produce a cash posting in the original
        wrappers, so the clean-room runtime likewise limits postings to
        finance_balances.

        The ordinary fresh-game DBRUser wage-suppression state at +0xCC starts
        clear. Therefore the standard mapped path charges all registered
        players except loaned-in players. A parent club still pays a player who
        is loaned out because registered club ownership remains with the parent.
        """
        if self.calendar.current_date.weekday() != 5:
            return {}

        debited: dict[int, int] = {}
        for club_id, balance in tuple(self.finance_balances.items()):
            club_id = int(club_id)
            total = 0
            for player_id in self.club_roster_order.get(club_id, ()):
                player = self.players.get(int(player_id))
                if player is None:
                    continue

                # 0x41FA50 excludes the loaned-in shape: registered/contract
                # club differs from this club while the temporary/current club
                # is this club. In the clean-room model, club_id remains the
                # registered club and loan_club_id carries the temporary club.
                if int(player.club_id) != club_id:
                    if (
                        player.loan_club_id is not None
                        and int(player.loan_club_id) == club_id
                    ):
                        continue
                    # Synthetic/corrupt roster mismatch is not a source-backed
                    # wage obligation for this club.
                    continue

                total += max(0, int(player.weekly_wage))

            if total <= 0:
                continue

            # Balance debit 0x5DC650 refuses a debit above current cash. The
            # original payroll caller does not invent overdraft state, so leave
            # cash/ledger unchanged when the debit cannot be accepted.
            if not balance.can_afford(total):
                continue

            balance.debit(
                total,
                category=PLAYER_COST_ACCOUNT_CATEGORY,
                posting_date=self.calendar.current_date,
            )
            debited[club_id] = total

        return debited

    def run_due_transfer_maintenance(
        self,
        *,
        user_controlled_club_id: int | None = None,
    ):
        """Execute due recovered MPMTransferPlayer objects using live Balance cash."""
        from transfer_workflow import execute_due_ordinary_cash_transfers

        if user_controlled_club_id is None:
            user_controlled_club_id = self.user_controlled_club_id
        return execute_due_ordinary_cash_transfers(
            self,
            user_controlled_club_id=user_controlled_club_id,
        )

    def advance_one_day(self) -> date:
        self.calendar.increment_one_day()
        self.calendar.run_post_fixture_maintenance()
        self.run_due_transfer_maintenance()
        self.run_weekly_player_payroll()
        self.run_weekly_ai_transfer_maintenance()
        return self.calendar.current_date

    def advance(self, days: int) -> date:
        if days < 0:
            raise ValueError("days must be non-negative")
        for _ in range(days):
            self.advance_one_day()
        return self.calendar.current_date

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
        # The original chairman sporting-objective transition is annual, not
        # daily. Invoke it only on the matchday that actually completes the PL.
        if results and len(self.premier_league.results) == len(self.premier_league.fixtures):
            self.run_premier_league_financial_objective_season_transition()
        self.calendar.run_post_fixture_maintenance()
        self.run_due_transfer_maintenance(
            user_controlled_club_id=self.user_controlled_club_id,
        )
        self.run_weekly_player_payroll()
        self.run_weekly_ai_transfer_maintenance(
            rng,
            user_controlled_club_id=self.user_controlled_club_id,
        )
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

        gate_inputs = self._prepare_premier_league_gate_inputs(
            home_club_id,
            int(fixture.away_club_id),
            home.preparation.selection.participants,
            away.preparation.selection.participants,
            controlled_club_id=self.user_controlled_club_id,
        )
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
        # 0x513252 -> 0x5DA2F0 runs after MatchCalculator and before
        # 0x5127A0 incident persistence / later Form RNG. Every normal League
        # fixture consumes these four draws even when no user Balance is posted.
        self._finish_premier_league_gate_receipts(home_club_id, gate_inputs, rng)

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
        gate_inputs = self._prepare_premier_league_gate_inputs(
            home_club_id,
            away_club_id,
            home_participants,
            away_participants,
            controlled_club_id=human_club_id,
        )
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
        self._finish_premier_league_gate_receipts(home_club_id, gate_inputs, rng)

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
