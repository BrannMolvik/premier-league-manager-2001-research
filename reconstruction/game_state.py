from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from time import time
from typing import Callable, Iterable

from competition_state import PremierLeagueState
from cup_progression import (
    CupMatchCompletion,
    CupMatchResolutionSnapshot,
    CupResultRegistry,
)
from domestic_cup_state import DomesticCupScheduleState
from contract_maintenance import (
    ContractRenewalSuggestion,
    ContractRenewalSuggestionKind,
    ControlledContractMaintenanceOutcome,
    run_ai_monthly_contract_maintenance,
    run_controlled_monthly_contract_maintenance,
)
from commercial_timers import UserCommercialTimerState
from concession_offer import (
    ConcessionRuntimeSource,
    choose_concession_local_value,
    concession_candidate_value,
    select_fresh_concession_candidate,
)
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
    prepare_cup_ai_selection,
    prepare_premier_league_ai_selection,
)
from match_postmatch import (
    PlayerTransferRequest,
    apply_player_transfer_request_response,
    persist_match_performance_history,
    persist_premier_league_morale_and_form,
    persist_premier_league_match_incidents,
    sync_post_match_conditions,
)
from match_orders import TeamOrderPriorities
from match_role_rating import best_preferred_role_rating
from match_simulation import PreparedMatchSide, NormalMatchResult, simulate_normal_match
from match_team_setup import TeamTacticalState, initialize_ai_roster_condition
from primary_schedule_shadow import (
    PrimaryScheduleResolutionPending,
    PrimaryScheduleShadowState,
)
from runtime_state import RuntimePlayer, derive_non_eu_status
from stadium_state import StadiumSourceState, TicketRuntimeState
from transfer_state import TransferRuntimeState
from youth_state import (
    YouthTeamState,
    generate_fresh_user_youth,
    promote_youth_player,
    release_youth_player,
)


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
    cup_results: CupResultRegistry = field(default_factory=CupResultRegistry)
    domestic_cups: DomesticCupScheduleState = field(
        default_factory=DomesticCupScheduleState
    )
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
    primary_matchday_order: dict[date, tuple[tuple, ...]] = field(default_factory=dict)
    primary_schedule_shadow: PrimaryScheduleShadowState = field(
        default_factory=lambda: PrimaryScheduleShadowState(days={})
    )
    transfers: TransferRuntimeState = field(default_factory=TransferRuntimeState)
    # Controlled 0x41BEE0 queues MPMEAMail renewal suggestions rather than
    # auto-renewing the contract. Keep the source event kind/date/player
    # persistently so save/reload and later Amend Contract UI can resume it.
    contract_renewal_suggestions: list[ContractRenewalSuggestion] = field(
        default_factory=list
    )
    # 0x404E25 -> 0x41B580 queues next-day PlayerAskTransferList MPMEAMail
    # records after the controlled club's per-player morale/Form work.
    player_transfer_requests: list[PlayerTransferRequest] = field(
        default_factory=list
    )
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
    # DBRUser+0x6BC separate 20-slot youth list. Membership is intentionally
    # independent of club_roster_order until 0x61E3D0 promotion.
    user_youth: YouthTeamState | None = None
    # Gate-11 DBRUser daily/weekly training integration. These remain opt-in
    # until the neighboring commercial/event scheduler is fully materialized;
    # once configured, advance_one_day() preserves the proven 0x42A9E0 order
    # of daily 0x61CA60 recovery before optional Saturday 0x4EACE0 training.
    user_training_recovery_threshold: int | None = None
    user_training_quality_multiplier: float | None = None
    user_commercial_timers: UserCommercialTimerState | None = None
    user_concession_source: ConcessionRuntimeSource | None = None
    # DBRUser +0x10D8: persistent manager-sacking reason. The original
    # objective evaluator writes this first; the outer manager loop later
    # consumes it to show the reason-specific message and leave management.
    user_sacking_reason: int | None = None
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
        state.calendar.monthly_hooks.append(state._run_monthly_contract_maintenance)
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

    def _player_active_club_is_user_controlled(
        self,
        player: RuntimePlayer,
    ) -> bool:
        controlled = self.user_controlled_club_id
        if controlled is None:
            return False
        active_club_id = (
            int(player.loan_club_id)
            if player.loan_club_id is not None
            else int(player.club_id)
        )
        return active_club_id == int(controlled)

    def _persist_premier_league_morale_form_and_requests(
        self,
        club_id: int,
        side: PreparedMatchSide,
        participants,
        result: NormalMatchResult,
        fixture_date: date,
        rng,
    ) -> frozenset[int]:
        """Run the source-ordered 0x404CE0 morale/Form/danger-morale slice."""
        club_id = int(club_id)
        club_user_controlled = bool(
            self.user_controlled_club_id is not None
            and club_id == int(self.user_controlled_club_id)
        )
        return persist_premier_league_morale_and_form(
            self.ordered_club_roster(club_id),
            side,
            participants,
            result,
            fixture_date,
            rng,
            club_user_controlled=club_user_controlled,
            active_club_user_controlled=self._player_active_club_is_user_controlled,
            transfer_request_sink=self.player_transfer_requests.append,
        )

    def due_player_transfer_requests(
        self,
        on_date: date | None = None,
    ) -> tuple[PlayerTransferRequest, ...]:
        """Return queued PlayerAskTransferList mail whose MPM date is due."""
        if on_date is None:
            on_date = self.calendar.current_date
        return tuple(
            request
            for request in self.player_transfer_requests
            if request.due_on <= on_date
        )

    def respond_to_player_transfer_request(
        self,
        request: PlayerTransferRequest,
        *,
        accept: bool,
    ) -> PlayerTransferRequest:
        """Apply the recovered accept/refuse response and clear the mail chain."""
        try:
            stored_index = self.player_transfer_requests.index(request)
        except ValueError as exc:
            raise ValueError("transfer request is not queued") from exc
        if self.calendar.current_date < request.due_on:
            raise ValueError("transfer request is not due yet")

        player = self.players.get(int(request.player_id))
        if player is None:
            raise KeyError(int(request.player_id))
        apply_player_transfer_request_response(player, accept=bool(accept))
        del self.player_transfer_requests[stored_index]
        return request

    def initialize_fresh_user_youth(
        self,
        option_mode: int | None,
        rng=None,
    ) -> YouthTeamState:
        """Run the mapped fresh 0x61DF90 -> 0x61DD30 user youth pass.

        This is explicit rather than automatic because the original call sits
        in the pre-schedule startup RNG sequence. Existing reconstructed startup
        callers can invoke it at that exact boundary without silently changing
        established fixture RNG state.
        """
        if self.user_controlled_club_id is None:
            raise RuntimeError("user-controlled club is required")
        if self.user_youth is not None and self.user_youth.records:
            raise RuntimeError("fresh user youth has already been initialized")
        rng = self._resolve_rng(rng)
        self.user_youth = generate_fresh_user_youth(
            self,
            user_club_id=int(self.user_controlled_club_id),
            option_mode=option_mode,
            rng=rng,
        )
        return self.user_youth

    def user_youth_players(self) -> tuple[RuntimePlayer, ...]:
        if self.user_youth is None:
            return ()
        return tuple(
            self.players[int(record.player_id)]
            for record in self.user_youth.records
            if int(record.player_id) in self.players
        )

    def promote_user_youth_player(
        self,
        player_id: int,
        *,
        weekly_wage: float,
        contract_months: int,
    ) -> RuntimePlayer:
        if self.user_controlled_club_id is None or self.user_youth is None:
            raise RuntimeError("initialized user youth state is required")
        return promote_youth_player(
            self,
            self.user_youth,
            player_id=int(player_id),
            target_club_id=int(self.user_controlled_club_id),
            weekly_wage=float(weekly_wage),
            contract_months=int(contract_months),
            rng=self._resolve_rng(),
        )

    def release_user_youth_player(self, player_id: int) -> bool:
        if self.user_controlled_club_id is None or self.user_youth is None:
            return False
        return release_youth_player(
            self,
            self.user_youth,
            player_id=int(player_id),
            user_club_id=int(self.user_controlled_club_id),
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

    def _run_monthly_ai_contract_maintenance(self, on_date: date) -> None:
        """Compatibility helper for the non-user 0x41ABC0 branch only.

        Normal database-backed calendar progression uses the unified method
        below so AI and controlled-player RNG calls retain club/roster order.
        """
        rng = self._resolve_rng()
        controlled = (
            None
            if self.user_controlled_club_id is None
            else int(self.user_controlled_club_id)
        )

        for club_id, player_ids in self.club_roster_order.items():
            roster_ids = tuple(int(player_id) for player_id in player_ids)
            roster_count = len(roster_ids)
            for player_id in roster_ids:
                player = self.players.get(player_id)
                if player is None:
                    continue
                active_club_id = (
                    int(player.loan_club_id)
                    if player.loan_club_id is not None
                    else int(player.club_id)
                )
                if controlled is not None and active_club_id == controlled:
                    continue
                run_ai_monthly_contract_maintenance(
                    player,
                    on_date=on_date,
                    roster_count=roster_count,
                    rng=rng,
                )

    def _controlled_contract_has_suppressing_deal(self, player_id: int) -> bool:
        """Reproduce 0x422950/0x50E590 plus the positive +0x178 gate.

        The clean-room transfer runtime permits one live DealInProgress per
        player. Direct executable writer tracing proves +0x178 is incremented
        when a deal entry is created and decremented when it is removed, so
        existence of this supported record supplies the positive-count half.
        """
        deal = self.transfers.deals.get(int(player_id))
        return bool(deal is not None and 3 <= int(deal.state) <= 5)

    def _queue_contract_renewal_suggestion(
        self,
        player_id: int,
        on_date: date,
        outcome: ControlledContractMaintenanceOutcome,
    ) -> None:
        if outcome is ControlledContractMaintenanceOutcome.SUGGEST_BOSMAN_RENEWAL:
            kind = ContractRenewalSuggestionKind.BOSMAN
        elif outcome is ControlledContractMaintenanceOutcome.SUGGEST_ORDINARY_RENEWAL:
            kind = ContractRenewalSuggestionKind.ORDINARY
        else:
            return
        self.contract_renewal_suggestions.append(
            ContractRenewalSuggestion(
                player_id=int(player_id),
                queued_on=on_date,
                kind=kind,
            )
        )

    def _purge_contract_mail_for_player(self, player_id: int) -> None:
        """Materialized player-linked MPMEAMail subset of original 0x5CE460."""
        player_id = int(player_id)
        self.contract_renewal_suggestions[:] = [
            value
            for value in self.contract_renewal_suggestions
            if int(value.player_id) != player_id
        ]
        self.player_transfer_requests[:] = [
            value
            for value in self.player_transfer_requests
            if int(value.player_id) != player_id
        ]

    def _run_monthly_contract_maintenance(self, on_date: date) -> None:
        """Run 0x41ABC0/0x41BEE0 in exact club/roster RNG order.

        Monthly player development remains the preceding calendar hook. It is
        deterministic and consumes no shared CRT RNG, so completing that whole
        pass first does not alter the contract-maintenance RNG sequence.

        Branch ownership follows 0x417360: a loaned player's active/current
        club controls whether the user or non-user contract path runs.
        """
        rng = self._resolve_rng()
        controlled = (
            None
            if self.user_controlled_club_id is None
            else int(self.user_controlled_club_id)
        )

        for club_id, player_ids in tuple(self.club_roster_order.items()):
            club_id = int(club_id)
            roster_ids = tuple(int(player_id) for player_id in player_ids)
            roster_count = len(roster_ids)

            for player_id in roster_ids:
                player = self.players.get(player_id)
                if player is None:
                    continue

                active_club_id = (
                    int(player.loan_club_id)
                    if player.loan_club_id is not None
                    else int(player.club_id)
                )
                is_controlled = bool(
                    controlled is not None and active_club_id == controlled
                )

                if not is_controlled:
                    run_ai_monthly_contract_maintenance(
                        player,
                        on_date=on_date,
                        roster_count=roster_count,
                        rng=rng,
                    )
                    continue

                in_registered_roster = bool(
                    int(player.club_id) == club_id
                    and player_id in self.club_roster_order.get(club_id, ())
                )
                outcome = run_controlled_monthly_contract_maintenance(
                    player,
                    on_date=on_date,
                    rng=rng,
                    in_registered_roster=in_registered_roster,
                    pending_contract_workflow=(
                        self._controlled_contract_has_suppressing_deal(player_id)
                    ),
                )
                self._queue_contract_renewal_suggestion(
                    player_id,
                    on_date,
                    outcome,
                )

                if (
                    outcome
                    is ControlledContractMaintenanceOutcome.DETACHED_OUT_OF_CONTRACT
                ):
                    roster = self.club_roster_order.get(club_id, [])
                    if player_id in roster:
                        roster.remove(player_id)
                    # 0x41EF00 -> 0x5CE460 removes player-linked queued mail
                    # before the training-record/roster detachment.
                    self._purge_contract_mail_for_player(player_id)

    def configure_user_commercial_calendar(self) -> None:
        """Enable the recovered fresh DBRUser concession/sponsor wait state."""
        if self.user_controlled_club_id is None:
            raise RuntimeError("user-controlled club is required")
        club_id = int(self.user_controlled_club_id)
        if club_id not in self.stadium_sources:
            raise RuntimeError("source-backed stadium state is required")
        if club_id not in self.clubs:
            raise RuntimeError("source-backed club state is required")
        access_row = self.access_fan_bases[int(getattr(self.clubs[club_id], "fan_base_index"))]
        values = tuple(getattr(access_row, "values"))
        stadium = self.stadium_sources[club_id]
        self.user_concession_source = ConcessionRuntimeSource(
            selector_capacities=tuple(
                int(stadium.concession_capacity_for_selector(selector))
                for selector in range(8)
            ),
            stadium_total=int(stadium.concession_capacity_total),
            club_metric=int(getattr(self.clubs[club_id], "runtime_value_1c_source")),
            access_metric=int(values[0]),
        )
        self.user_commercial_timers = UserCommercialTimerState()

    def disable_user_commercial_calendar(self) -> None:
        """Disable automatic commercial timing without mutating other state."""
        self.user_commercial_timers = None
        self.user_concession_source = None

    def _attempt_user_concession_offer(self, rng) -> bool:
        """Consume the mapped fresh 0x5E5330 concession-offer RNG body.

        The current slice reproduces selection/timing RNG and intentionally
        stops short of inventing presentation/event payload state.
        """
        source = self.user_concession_source
        if source is None:
            return False

        for selector, capacity in enumerate(source.selector_capacities):
            capacity = int(capacity)
            if capacity <= 0:
                continue

            candidate_value = concession_candidate_value(
                rng,
                club_metric=source.club_metric,
                access_metric=source.access_metric,
                stadium_total=source.stadium_total,
                adjustment_percent=source.adjustment_percent,
            )
            candidate_index, _ = select_fresh_concession_candidate(
                rng,
                capacity=capacity,
                candidate_value=candidate_value,
            )
            if candidate_index is None:
                continue

            # 0x5E5495 consumes the candidate-local range when non-degenerate.
            choose_concession_local_value(rng, candidate_index)

            # The later fresh offer-lifetime branch uses the recovered
            # 0x8212C8..0x8212CC range of three values.
            rng.randbelow(3)
            return True

        return False

    def run_user_commercial_day(self, rng=None) -> tuple[int, bool]:
        """Run commercial timing before the DBRUser training maintenance."""
        if self.user_commercial_timers is None:
            return 0, False
        rng = self._resolve_rng(rng)
        return self.user_commercial_timers.run_daily(
            rng,
            concession_attempt=self._attempt_user_concession_offer,
        )

    def configure_user_training_calendar(
        self,
        *,
        recovery_threshold: int,
        quality_multiplier: float,
    ) -> None:
        """Enable source-backed user training in normal day progression.

        The first fresh Arsenal interval is proven with threshold 50 and
        quality 1.30. Callers may provide other values only when their source
        state has been independently materialized.
        """
        recovery_threshold = int(recovery_threshold)
        quality_multiplier = float(quality_multiplier)
        if not 0 <= recovery_threshold <= 100:
            raise ValueError("training recovery threshold must be in 0..100")
        if quality_multiplier <= 0.0:
            raise ValueError("training quality multiplier must be positive")
        self.user_training_recovery_threshold = recovery_threshold
        self.user_training_quality_multiplier = quality_multiplier

    def disable_user_training_calendar(self) -> None:
        """Disable automatic user training without mutating player state."""
        self.user_training_recovery_threshold = None
        self.user_training_quality_multiplier = None

    def run_configured_user_training_day(self, rng=None) -> tuple[int, int]:
        """Run configured DBRUser training maintenance for the current date.

        A missing configuration intentionally consumes no RNG. This prevents
        unresolved staff/facility or commercial scheduler state from being
        silently replaced with guessed defaults.
        """
        if (
            self.user_training_recovery_threshold is None
            or self.user_training_quality_multiplier is None
        ):
            return 0, 0
        return self.run_user_training_primary_day(
            rng,
            recovery_threshold=self.user_training_recovery_threshold,
            quality_multiplier=self.user_training_quality_multiplier,
        )

    def run_user_daily_training_condition_recovery(
        self,
        rng=None,
        *,
        recovery_threshold: int,
        user_controlled_club_id: int | None = None,
    ) -> int:
        """Run the source-backed primary 0x61CA60/0x61C580 recovery slice.

        Training storage is exactly 40 records in the original DBRUser. The
        current clean-room roster order is source-table order at fresh startup,
        so only the first 40 controlled-club records participate here.

        This intentionally excludes the later low-Condition/event branches in
        0x61C580 and 0x61C6C0; callers must supply a threshold whose source
        state is already proven. The fresh first-week threshold is 50.
        """
        if user_controlled_club_id is None:
            user_controlled_club_id = self.user_controlled_club_id
        if user_controlled_club_id is None:
            return 0
        rng = self._resolve_rng(rng)

        draws = 0
        for player in self.ordered_club_roster(int(user_controlled_club_id))[:40]:
            draws += player.run_daily_training_condition_recovery(
                rng,
                int(recovery_threshold),
            )
        return draws

    def run_user_weekly_training_primary(
        self,
        rng=None,
        *,
        quality_multiplier: float,
        user_controlled_club_id: int | None = None,
    ) -> int:
        """Run the exact primary 0x4EACE0 transition on the Saturday phase."""
        if self.calendar.current_date.weekday() != 5:
            return 0
        if user_controlled_club_id is None:
            user_controlled_club_id = self.user_controlled_club_id
        if user_controlled_club_id is None:
            return 0
        rng = self._resolve_rng(rng)

        draws = 0
        for player in self.ordered_club_roster(int(user_controlled_club_id))[:40]:
            draws += player.run_weekly_training_primary(
                rng,
                float(quality_multiplier),
            )
        return draws

    def run_user_training_primary_day(
        self,
        rng=None,
        *,
        recovery_threshold: int,
        quality_multiplier: float,
        user_controlled_club_id: int | None = None,
    ) -> tuple[int, int]:
        """Run daily recovery before the optional same-day weekly transition.

        This mirrors the proven 0x42A9E0 ordering:
        0x61CA60 daily recovery precedes the Saturday
        0x42AE40 -> 0x4EACE0 training transition.
        """
        rng = self._resolve_rng(rng)
        daily_draws = self.run_user_daily_training_condition_recovery(
            rng,
            recovery_threshold=int(recovery_threshold),
            user_controlled_club_id=user_controlled_club_id,
        )
        weekly_draws = self.run_user_weekly_training_primary(
            rng,
            quality_multiplier=float(quality_multiplier),
            user_controlled_club_id=user_controlled_club_id,
        )
        return daily_draws, weekly_draws

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
        evaluation = objective.evaluate(
            balance.current_cash,
            self.calendar.current_date,
        )
        if evaluation is not None and evaluation.sacking_reason is not None:
            # 0x5E1D90 -> DBRUser::0x42C6C0 stores the reason at +0x10D8.
            self.user_sacking_reason = int(evaluation.sacking_reason)
        return evaluation

    def finalize_single_user_sacking_control(self) -> int | None:
        """Mirror the shipped single-user DBRUser sacking control transition.

        0x4290F0 consumes +0x10D8 and queues the reason-specific manager-
        sacking message. With the canonical 0x516010 gate true and only one
        user, the outer loop leaves management and constructs PStartMenu. The
        DBRUser/Balance state itself is not destroyed at the reason-write site,
        so this method only ends active control and keeps the persistent reason.
        """
        if self.user_sacking_reason is None:
            return None
        reason = int(self.user_sacking_reason)
        self.user_controlled_club_id = None
        return reason

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

    @staticmethod
    def _draw_matchday_gate_rand15_values(rng) -> tuple[int, int, int, int]:
        """Consume 0x5DA2F0's four randomized-subtraction draws in source order."""
        return tuple(int(rng.randbelow(32768)) for _ in range(4))

    def _finish_premier_league_gate_receipts(
        self,
        home_club_id: int,
        prepared_inputs: dict[str, object] | None,
        rng,
    ) -> GateReceiptResult | None:
        """Consume the four post-calculator gate draws and post when materialized."""
        rand15_values = self._draw_matchday_gate_rand15_values(rng)
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

        # Original 0x42A9E0 processes commercial timing before its daily
        # training-record maintenance. Preserve that shared-RNG order before
        # the later global Saturday maintenance in 0x4A8070.
        self.run_user_commercial_day()
        self.run_configured_user_training_day()

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
        match_engine_rng=None,
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
                    match_engine_rng=match_engine_rng,
                ),
            )
            for fixture_id in ordered_ids
        )

    def simulate_primary_ai_entry(
        self,
        entry: tuple,
        attack_matrix,
        defence_matrix,
        rng=None,
    ) -> NormalMatchResult:
        """Simulate one tagged primary PL/Cup entry as AI-vs-AI."""
        rng = self._resolve_rng(rng)
        entry = tuple(entry)
        kind = entry[0]
        if kind == "premier_league":
            return self.simulate_premier_league_ai_fixture(
                int(entry[1]),
                attack_matrix,
                defence_matrix,
                rng,
            )
        if kind == "domestic_cup":
            result, _completion = self.simulate_domestic_cup_ai_node(
                tuple(entry[1]),
                attack_matrix,
                defence_matrix,
                rng,
            )
            return result
        raise ValueError(f"unsupported primary match entry {entry!r}")

    def simulate_due_primary_ai_entries(
        self,
        attack_matrix,
        defence_matrix,
        rng=None,
        *,
        entry_order: Iterable[tuple] | None = None,
    ) -> tuple[tuple[tuple, object], ...]:
        """Simulate today's PL/domestic-Cup entries in one scheduler order.

        This is the Gate-12 counterpart of the PL-only due-fixture walker.
        Entries come from the post-shuffle primary linked-list order retained
        by install_primary_matchday_order().
        """
        rng = self._resolve_rng(rng)
        due = self.primary_entries_due_today()
        if entry_order is None:
            ordered = due
        else:
            ordered = tuple(tuple(entry) for entry in entry_order)
            if len(ordered) != len(set(ordered)) or set(ordered) != set(due):
                raise ValueError(
                    "entry_order must contain each due primary entry exactly once"
                )

        return tuple(
            (
                entry,
                self.simulate_primary_ai_entry(
                    entry,
                    attack_matrix,
                    defence_matrix,
                    rng,
                ),
            )
            for entry in ordered
        )

    def advance_one_day_with_primary_ai_matches(
        self,
        attack_matrix,
        defence_matrix,
        rng=None,
    ) -> tuple[tuple[tuple, object], ...]:
        """Advance one day and execute PL/Cup matches in shared primary order."""
        rng = self._resolve_rng(rng)
        self.calendar.increment_one_day()
        results = self.simulate_due_primary_ai_entries(
            attack_matrix,
            defence_matrix,
            rng,
        )
        if (
            results
            and self.premier_league is not None
            and len(self.premier_league.results) == len(self.premier_league.fixtures)
        ):
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
        self.finalize_single_user_sacking_control()
        return results

    def advance_one_day_with_premier_league_ai_fixtures(
        self,
        attack_matrix,
        defence_matrix,
        rng=None,
        *,
        fixture_order: Iterable[int] | None = None,
        match_engine_rng=None,
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
            match_engine_rng=match_engine_rng,
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
        self.finalize_single_user_sacking_control()
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

    def record_cup_match_resolution(
        self,
        result_token: tuple,
        snapshot: CupMatchResolutionSnapshot,
    ):
        """Persist a definitive Cup outcome in the live GameState registry."""
        return self.cup_results.record_match_resolution(result_token, snapshot)

    def resolve_cup_club_ref(self, ref):
        """Resolve a Cup ClubRef against live GameState result state."""
        return self.cup_results.resolve_club_ref(ref)

    def install_primary_schedule_shadow(
        self,
        buckets,
        *,
        season_year: int,
    ) -> PrimaryScheduleShadowState:
        """Retain all primary-container participants for 0x615D10 lookups."""
        self.primary_schedule_shadow = (
            PrimaryScheduleShadowState.from_primary_schedule_buckets(
                buckets,
                season_year=int(season_year),
            )
        )
        return self.primary_schedule_shadow

    def next_primary_match_date_for_club(
        self,
        club_id: int,
        *,
        after_date: date | None = None,
    ) -> date | None:
        """Return the exact next primary-container match date when resolvable."""
        return self.primary_schedule_shadow.next_match_date(
            int(club_id),
            self.calendar.current_date if after_date is None else after_date,
            self.cup_results.resolve_club_ref,
        )

    def _preflight_domestic_cup_post_match_dates(
        self,
        home_club_id: int,
        away_club_id: int,
        fixture_date: date,
    ) -> tuple[bool, date | None, date | None]:
        """Resolve both 0x615D10 dates before any shared incident RNG is consumed.

        A nonempty primary shadow is required for the source-backed Cup path.
        If either lookup reaches an unresolved earlier symbolic node, return a
        single pending result rather than exposing one exact side and allowing
        partial 0x5127A0 persistence.
        """
        if not self.primary_schedule_shadow.days:
            return False, None, None

        try:
            home_next = self.next_primary_match_date_for_club(
                int(home_club_id),
                after_date=fixture_date,
            )
            away_next = self.next_primary_match_date_for_club(
                int(away_club_id),
                after_date=fixture_date,
            )
        except PrimaryScheduleResolutionPending:
            return False, None, None

        return True, home_next, away_next

    def _persist_domestic_cup_shared_post_match(
        self,
        *,
        home_club_id: int,
        away_club_id: int,
        home_side: PreparedMatchSide,
        away_side: PreparedMatchSide,
        home_participants,
        away_participants,
        result: NormalMatchResult,
        environment: MatchEnvironment,
        pitch_wear_before: int,
        rng,
    ) -> bool:
        """Apply shared Cup post-match state only after an exact two-side preflight.

        MatchCalculator Condition is always synchronized because the original
        mutates DBRPlayer in place. Pitch wear is RNG-clean and likewise remains
        live. The RNG-consuming 0x5127A0 incident and 0x404CE0 morale/Form
        branches run only when both clubs' next primary-container dates are
        provably exact.
        """
        home_club_id = int(home_club_id)
        away_club_id = int(away_club_id)
        fixture_date = self.calendar.current_date

        sync_post_match_conditions(home_side, home_participants)
        sync_post_match_conditions(away_side, away_participants)

        exact, home_next, away_next = self._preflight_domestic_cup_post_match_dates(
            home_club_id,
            away_club_id,
            fixture_date,
        )

        if exact:
            home_user_controlled = bool(
                self.user_controlled_club_id is not None
                and home_club_id == int(self.user_controlled_club_id)
            )
            away_user_controlled = bool(
                self.user_controlled_club_id is not None
                and away_club_id == int(self.user_controlled_club_id)
            )
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
            int(pitch_wear_before),
            environment.weather_code,
        )

        if exact:
            self._persist_premier_league_morale_form_and_requests(
                home_club_id,
                home_side,
                home_participants,
                result,
                fixture_date,
                rng,
            )
            self._persist_premier_league_morale_form_and_requests(
                away_club_id,
                away_side,
                away_participants,
                result,
                fixture_date,
                rng,
            )

        return exact

    def install_primary_matchday_order(
        self,
        buckets,
        *,
        season_year: int,
    ) -> dict[date, tuple[tuple, ...]]:
        """Persist exact shuffled PL/domestic-Cup order for Gate-12 dates."""
        from primary_schedule import gate12_primary_matchday_order

        self.primary_matchday_order = dict(
            gate12_primary_matchday_order(
                buckets,
                season_year=int(season_year),
            )
        )
        return self.primary_matchday_order

    def primary_entries_due_today(self) -> tuple[tuple, ...]:
        """Return uncompleted/playable PL/Cup entries in global scheduler order."""
        entries = self.primary_matchday_order.get(self.calendar.current_date, ())
        if not entries:
            return ()

        due_pl = {
            int(fixture.id)
            for fixture in self.fixtures_due_today()
        }
        due_cup = {
            tuple(node.node_token)
            for node in self.domestic_cup_nodes_due_today()
        }

        due: list[tuple] = []
        for entry in entries:
            kind = entry[0]
            if kind == "premier_league" and int(entry[1]) in due_pl:
                due.append(entry)
            elif kind == "domestic_cup" and tuple(entry[1]) in due_cup:
                due.append(entry)
        return tuple(due)

    def install_domestic_cup_schedule_nodes(
        self,
        nodes,
        *,
        season_year: int,
    ) -> DomesticCupScheduleState:
        """Attach already-materialized FA/League Cup nodes to live state.

        The caller supplies Gate-3/Gate-4 schedule nodes. This method never
        redraws participants or consumes RNG.
        """
        self.domestic_cups = DomesticCupScheduleState.from_startup_nodes(
            nodes,
            season_year=int(season_year),
        )
        return self.domestic_cups

    def install_domestic_cup_primary_schedule(
        self,
        buckets,
        *,
        season_year: int,
    ) -> DomesticCupScheduleState:
        """Attach post-placement/post-shuffle primary Cup nodes to live state.

        The supplied buckets must already reflect Gate-4 0x615950 conflict
        placement and 0x615BE0/0x615AE0 shuffle. No draw or schedule RNG is
        consumed here.
        """
        self.domestic_cups = DomesticCupScheduleState.from_primary_schedule_buckets(
            buckets,
            season_year=int(season_year),
        )
        return self.domestic_cups

    def domestic_cup_nodes_due_today(self):
        """Return placed/shuffled domestic Cup nodes whose refs now resolve."""
        return self.domestic_cups.due_nodes(
            self.calendar.current_date,
            self.cup_results,
        )

    def simulate_domestic_cup_ai_node(
        self,
        node_token: tuple,
        attack_matrix,
        defence_matrix,
        rng=None,
    ) -> tuple[NormalMatchResult, CupMatchCompletion]:
        """Run one due AI-vs-AI domestic Cup node through the shared backend.

        This closes score production and the Cup lifecycle only. It preserves
        the proven pre-match order (both selections, weather, side-0 Condition,
        side-1 Condition), uses the Cup runtime extra-time policy, syncs
        MatchCalculator Condition back to runtime players, and updates the home
        pitch. When the full-primary shadow proves both clubs' next match dates,
        the shared incident and morale/Form branches also run in executable
        order. Special Cup revenue posting remains separate Gate-12 work.
        """
        rng = self._resolve_rng(rng)
        token = tuple(node_token)
        node = self.domestic_cups.node(token)
        if node.scheduled_date != self.calendar.current_date:
            raise ValueError(
                f"domestic Cup node {token!r} is not due on "
                f"{self.calendar.current_date}"
            )
        if node.round_number is None:
            raise RuntimeError("domestic Cup node has no source round number")

        match = self.domestic_cups.materialize_scheduled_match(
            token,
            self.cup_results,
        )
        home_club_id = int(match.participant_0_club_id)
        away_club_id = int(match.participant_1_club_id)
        competition = self.competitions.get(int(node.competition_id))
        if competition is None:
            raise RuntimeError(
                f"Cup competition definition {int(node.competition_id)} is not loaded"
            )

        def club_inputs(club_id: int):
            club = self.clubs.get(int(club_id))
            if club is None:
                raise RuntimeError(f"club definition {int(club_id)} is not loaded")
            manager = self.managers.get(int(club.manager_id))
            if manager is None:
                raise RuntimeError(
                    f"manager {int(club.manager_id)} for club {int(club_id)} "
                    "is not loaded"
                )
            roster = self.ordered_club_roster(int(club_id))
            if not roster:
                raise RuntimeError(f"club {int(club_id)} has no runtime roster")
            return manager, roster

        home_manager, home_roster = club_inputs(home_club_id)
        away_manager, away_roster = club_inputs(away_club_id)

        home_deficit = 0
        away_deficit = 0
        if match.prior_match is not None:
            prior = match.prior_match
            # Linked Replay/SecondLeg participants are reversed. Before the
            # current match, aggregate side 0 owns prior score_1 and side 1
            # owns prior score_0.
            home_deficit = max(
                0,
                int(prior.composed_score_0) - int(prior.composed_score_1),
            )
            away_deficit = max(
                0,
                int(prior.composed_score_1) - int(prior.composed_score_0),
            )

        home_preparation = prepare_cup_ai_selection(
            home_club_id,
            home_roster,
            away_roster,
            home_manager,
            competition,
            round_number=int(node.round_number),
            is_home=True,
            aggregate_goals_behind=home_deficit,
        )
        away_preparation = prepare_cup_ai_selection(
            away_club_id,
            away_roster,
            home_roster,
            away_manager,
            competition,
            round_number=int(node.round_number),
            is_home=False,
            aggregate_goals_behind=away_deficit,
        )

        environment = generate_match_environment(
            self.calendar.current_date,
            rng,
        )
        initialize_ai_roster_condition(home_roster, rng)
        initialize_ai_roster_condition(away_roster, rng)
        home_side = build_prepared_match_side_from_selection(
            home_preparation.selection,
            0,
            self.team_tactics.get(home_club_id, TeamTacticalState()),
            user_controlled=False,
            team_orders=TeamOrderPriorities(),
        )
        away_side = build_prepared_match_side_from_selection(
            away_preparation.selection,
            1,
            self.team_tactics.get(away_club_id, TeamTacticalState()),
            user_controlled=False,
            team_orders=TeamOrderPriorities(),
        )

        pitch_wear_before = int(self.pitch_wear.get(home_club_id, 0))
        result = simulate_normal_match(
            home_side,
            away_side,
            attack_matrix,
            defence_matrix,
            rng,
            condition_injury_settings=ConditionInjurySettings(
                environment_byte=pitch_wear_before,
            ),
            extra_time=bool(match.uses_extra_time),
        )

        # Shared match execution calls 0x513252 -> 0x5DA2F0 after the
        # MatchCalculator returns and before the class-specific +0x3C
        # completion virtual. Cup completion can itself consume decisive
        # fallback RNG, so preserve these four draws ahead of that boundary
        # even while special Cup revenue posting remains a separate slice.
        self._draw_matchday_gate_rand15_values(rng)

        completion = self.domestic_cups.complete_scheduled_match(
            token,
            self.cup_results,
            result.score[0],
            result.score[1],
            current_date=self.calendar.current_date,
            rng=rng,
        )
        if completion.replay is not None and self.primary_schedule_shadow.days:
            replay_node = self.domestic_cups.node(completion.replay.node_token)
            self.primary_schedule_shadow.insert_dynamic_node(
                replay_node,
                on_date=replay_node.scheduled_date,
            )


        self._persist_domestic_cup_shared_post_match(
            home_club_id=home_club_id,
            away_club_id=away_club_id,
            home_side=home_side,
            away_side=away_side,
            home_participants=home_preparation.selection.participants,
            away_participants=away_preparation.selection.participants,
            result=result,
            environment=environment,
            pitch_wear_before=pitch_wear_before,
            rng=rng,
        )
        return result, completion

    def simulate_domestic_cup_human_node(
        self,
        node_token: tuple,
        human_club_id: int,
        human_selection: PreparedAiMatchSelection,
        attack_matrix,
        defence_matrix,
        rng=None,
        *,
        team_orders: TeamOrderPriorities | None = None,
    ) -> tuple[NormalMatchResult, CupMatchCompletion]:
        """Run one due human-vs-AI domestic Cup node through the shared backend.

        Human selection/Condition/tactics remain persistent runtime state. The
        opponent uses the source-backed Cup AI strategy path. As with the AI
        bridge, shared incident and morale/Form persistence runs only when the
        full-primary shadow proves both next-match dates exactly.
        """
        rng = self._resolve_rng(rng)
        token = tuple(node_token)
        node = self.domestic_cups.node(token)
        if node.scheduled_date != self.calendar.current_date:
            raise ValueError(
                f"domestic Cup node {token!r} is not due on "
                f"{self.calendar.current_date}"
            )
        if node.round_number is None:
            raise RuntimeError("domestic Cup node has no source round number")

        match = self.domestic_cups.materialize_scheduled_match(
            token,
            self.cup_results,
        )
        home_club_id = int(match.participant_0_club_id)
        away_club_id = int(match.participant_1_club_id)
        human_club_id = int(human_club_id)
        if human_club_id not in (home_club_id, away_club_id):
            raise ValueError("human club does not participate in this Cup match")

        competition = self.competitions.get(int(node.competition_id))
        if competition is None:
            raise RuntimeError(
                f"Cup competition definition {int(node.competition_id)} is not loaded"
            )

        human_is_home = human_club_id == home_club_id
        ai_club_id = away_club_id if human_is_home else home_club_id
        ai_club = self.clubs.get(ai_club_id)
        if ai_club is None:
            raise RuntimeError(f"club definition {ai_club_id} is not loaded")
        ai_manager = self.managers.get(int(ai_club.manager_id))
        if ai_manager is None:
            raise RuntimeError(
                f"manager {int(ai_club.manager_id)} for club {ai_club_id} "
                "is not loaded"
            )

        human_roster = self.ordered_club_roster(human_club_id)
        ai_roster = self.ordered_club_roster(ai_club_id)
        if not human_roster or not ai_roster:
            raise RuntimeError("human/AI Cup match requires both runtime rosters")

        home_deficit = 0
        away_deficit = 0
        if match.prior_match is not None:
            prior = match.prior_match
            home_deficit = max(
                0,
                int(prior.composed_score_0) - int(prior.composed_score_1),
            )
            away_deficit = max(
                0,
                int(prior.composed_score_1) - int(prior.composed_score_0),
            )
        ai_deficit = away_deficit if human_is_home else home_deficit

        ai_preparation = prepare_cup_ai_selection(
            ai_club_id,
            ai_roster,
            human_roster,
            ai_manager,
            competition,
            round_number=int(node.round_number),
            is_home=not human_is_home,
            aggregate_goals_behind=ai_deficit,
        )

        environment = generate_match_environment(
            self.calendar.current_date,
            rng,
        )
        initialize_ai_roster_condition(ai_roster, rng)
        ai_side = build_prepared_match_side_from_selection(
            ai_preparation.selection,
            1 if human_is_home else 0,
            self.team_tactics.get(ai_club_id, TeamTacticalState()),
            user_controlled=False,
            team_orders=TeamOrderPriorities(),
        )
        human_side = build_prepared_match_side_from_selection(
            human_selection,
            0 if human_is_home else 1,
            self.team_tactics.get(human_club_id, TeamTacticalState()),
            user_controlled=True,
            team_orders=team_orders or TeamOrderPriorities(),
        )

        if human_is_home:
            home_side = human_side
            away_side = ai_side
            home_participants = human_selection.participants
            away_participants = ai_preparation.selection.participants
        else:
            home_side = ai_side
            away_side = human_side
            home_participants = ai_preparation.selection.participants
            away_participants = human_selection.participants

        pitch_wear_before = int(self.pitch_wear.get(home_club_id, 0))
        result = simulate_normal_match(
            home_side,
            away_side,
            attack_matrix,
            defence_matrix,
            rng,
            condition_injury_settings=ConditionInjurySettings(
                environment_byte=pitch_wear_before,
            ),
            match_mode_code=1,
            extra_time=bool(match.uses_extra_time),
        )

        # The human Cup path shares the same post-calculator gate producer and
        # therefore the same four-draw boundary before Cup completion.
        self._draw_matchday_gate_rand15_values(rng)

        completion = self.domestic_cups.complete_scheduled_match(
            token,
            self.cup_results,
            result.score[0],
            result.score[1],
            current_date=self.calendar.current_date,
            rng=rng,
        )
        if completion.replay is not None and self.primary_schedule_shadow.days:
            replay_node = self.domestic_cups.node(completion.replay.node_token)
            self.primary_schedule_shadow.insert_dynamic_node(
                replay_node,
                on_date=replay_node.scheduled_date,
            )


        self._persist_domestic_cup_shared_post_match(
            home_club_id=home_club_id,
            away_club_id=away_club_id,
            home_side=home_side,
            away_side=away_side,
            home_participants=home_participants,
            away_participants=away_participants,
            result=result,
            environment=environment,
            pitch_wear_before=pitch_wear_before,
            rng=rng,
        )
        return result, completion

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
        *,
        match_engine_rng=None,
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
        # MatchCalculator 0x630FC0 appends the just-computed +0x30 target
        # ratings before returning to the later gate/incident/Form pipeline.
        # Keep this opt-in until a distinct MatchEngine RNG is explicitly
        # supplied; never alias the shared CRT stream as a substitute.
        if match_engine_rng is not None:
            persist_match_performance_history(
                home.match_side,
                home.preparation.selection.participants,
                result,
                rng,
                match_engine_rng,
            )
            persist_match_performance_history(
                away.match_side,
                away.preparation.selection.participants,
                result,
                rng,
                match_engine_rng,
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

        # 0x404CE0 runs after incident persistence and interleaves each
        # roster player's morale handling with that same player's Form update.
        # It must not re-copy Condition, which would erase injury Condition loss.
        self._persist_premier_league_morale_form_and_requests(
            home_club_id,
            home.match_side,
            home.preparation.selection.participants,
            result,
            fixture_date,
            rng,
        )
        self._persist_premier_league_morale_form_and_requests(
            away_club_id,
            away.match_side,
            away.preparation.selection.participants,
            result,
            fixture_date,
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
        match_engine_rng=None,
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
        if match_engine_rng is not None:
            persist_match_performance_history(
                home_side,
                home_participants,
                result,
                rng,
                match_engine_rng,
            )
            persist_match_performance_history(
                away_side,
                away_participants,
                result,
                rng,
                match_engine_rng,
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

        self._persist_premier_league_morale_form_and_requests(
            home_club_id,
            home_side,
            home_participants,
            result,
            fixture_date,
            rng,
        )
        self._persist_premier_league_morale_form_and_requests(
            away_club_id,
            away_side,
            away_participants,
            result,
            fixture_date,
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
