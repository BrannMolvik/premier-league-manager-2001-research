"""Minimum human-manager gameplay controller for Gate 7.

This is intentionally a backend workflow layer, not a replacement UI. It keeps
one human club's persistent selection/tactics while every match still runs
through GameState's reconstructed Premier League simulation backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Iterable

from game_state import GameState
from match_lineup import AI_FORMATIONS, AiLineupCoreResult, StarterAssignment
from match_orders import TeamOrderPriorities
from match_participants import collect_match_participants
from match_preparation import PreparedAiMatchSelection, prepare_ai_match_selection
from match_schedule import MsvcCrtRng
from match_team_setup import TeamTacticalState, resolved_substitute_quota
from scouting import (
    SCOUTING_SORT_MODE_CLUB_NAME,
    SCOUTING_SORT_MODE_HISTORY_AVERAGE,
    SCOUTING_SORT_MODE_POSITION_LABEL,
    SCOUTING_SORT_MODE_VALUE,
    ScoutingFilterControls,
    ScoutingFilterValues,
    ScoutingRankValues,
    ScoutingReseedState,
    ScoutingSortValues,
    run_scouting_search,
    scouting_country_context_passes,
    scouting_first_stage_passes,
    scouting_loan_list_user_match,
    scouting_preferred_position_passes,
    scouting_strength_threshold_passes,
)
from transfer_decision import SellingClubDecision
from transfer_negotiation import (
    OrdinaryMoneyResponse,
    OrdinaryMoneyResponseResult,
    evaluate_ordinary_money_response,
)
from transfer_state import ContractTerms
from transfer_workflow import (
    LiveCashBidEvaluation,
    evaluate_live_cash_bid,
    execute_due_ordinary_cash_transfers,
    schedule_ordinary_cash_transfer,
    submit_live_cash_bid,
)


@dataclass
class HumanManagerState:
    club_id: int
    formation_id: int = 0
    starter_ids: tuple[int, ...] = ()
    substitute_ids: tuple[int, ...] = ()
    team_orders: TeamOrderPriorities = field(default_factory=TeamOrderPriorities)


@dataclass(frozen=True)
class HumanPrimaryMatchdayOutcome:
    match_entry: tuple
    user_result: object
    matchday_results: tuple[tuple[tuple, object], ...]
    table: tuple[object, ...]


@dataclass(frozen=True)
class HumanMatchdayOutcome:
    fixture_id: int
    user_result: object
    matchday_results: tuple[tuple[int, object], ...]
    table: tuple[object, ...]


class HumanGameplayController:
    """Small persistent gameplay loop over the reconstructed match backend."""

    def __init__(
        self,
        state: GameState,
        attack_matrix,
        defence_matrix,
        match_rng,
    ):
        if state.premier_league is None:
            raise RuntimeError("Premier League state is required")
        self.state = state
        self.attack_matrix = attack_matrix
        self.defence_matrix = defence_matrix
        self.match_rng = match_rng
        self.human: HumanManagerState | None = None
        self.pending_fixture_id: int | None = None
        self._pending_prior_results: tuple[tuple[int, object], ...] = ()
        self._pending_after_fixture_ids: tuple[int, ...] = ()
        self.pending_primary_entry: tuple | None = None
        self._pending_prior_primary_results: tuple[tuple[tuple, object], ...] = ()
        self._pending_after_primary_entries: tuple[tuple, ...] = ()
        self.last_transfer_executions: tuple[object, ...] = ()

    @classmethod
    def from_canonical_game_dir(
        cls,
        game_dir: str | Path,
        *,
        player_seed: int = 1,
        start_date: date = date(2000, 8, 18),
    ) -> "HumanGameplayController":
        """Create the same canonical shipped-data runtime used by Gates 5/6."""

        # Local imports keep the lightweight/synthetic controller independent
        # from canonical-file verification and FOOTBAL.EXE coefficient loading.
        from canonical_matchday_audit import reconstruct_canonical_primary_schedule
        from fm2001_data import FM2001Database
        from match_coefficients import MatchCoefficientMatrices
        from verify import verify_canonical_files

        game_dir = Path(game_dir)
        verify_canonical_files(game_dir)
        database = FM2001Database(game_dir)
        matrices = MatchCoefficientMatrices.from_executable(
            game_dir / "FOOTBAL.EXE"
        )
        primary_schedule = reconstruct_canonical_primary_schedule(database)
        state = GameState.from_database(
            database,
            start_date,
            seed=int(player_seed),
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(
            primary_schedule.premier_league_order
        )
        state.install_domestic_cup_primary_schedule(
            primary_schedule.buckets,
            season_year=2000,
        )
        state.install_primary_matchday_order(
            primary_schedule.buckets,
            season_year=2000,
        )
        state.install_primary_schedule_shadow(
            primary_schedule.buckets,
            season_year=2000,
        )
        return cls(
            state,
            matrices.attack,
            matrices.defence,
            MsvcCrtRng(primary_schedule.state_after),
        )

    def select_club(self, club_id: int) -> HumanManagerState:
        """Select one Premier League club for human control."""

        if self.pending_fixture_id is not None:
            raise RuntimeError("cannot change club during a pending matchday")

        club_id = int(club_id)
        league = self.state.premier_league
        if club_id not in set(int(value) for value in league.club_ids):
            raise ValueError(f"club {club_id} is not in the Premier League")
        if not self.state.ordered_club_roster(club_id):
            raise ValueError(f"club {club_id} has no runtime squad")

        self.human = HumanManagerState(club_id=club_id)
        club = self.state.clubs.get(club_id)
        if club is not None and hasattr(club, "starting_cash"):
            self.state.initialize_controlled_club_balance(club_id)
        else:
            # Lightweight synthetic databases may intentionally omit original
            # finance source fields.
            self.state.user_controlled_club_id = club_id
        return self.human

    def initialize_fresh_youth(self, option_mode: int | None = None):
        """Materialize the original separate fresh user youth list."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.initialize_fresh_user_youth(option_mode)

    def youth_players(self) -> tuple[object, ...]:
        """Return the current separate youth-list players in record order."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.user_youth_players()

    def promote_youth_player(
        self,
        player_id: int,
        *,
        weekly_wage: float,
        contract_months: int,
    ):
        """Apply the mapped EAMyouthpromoteplayer roster/contract transition."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.promote_user_youth_player(
            int(player_id),
            weekly_wage=float(weekly_wage),
            contract_months=int(contract_months),
        )

    def release_youth_player(self, player_id: int) -> bool:
        """Apply the mapped youth-list removal and free-player transition."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.release_user_youth_player(int(player_id))

    def financial_objective_candidates(self) -> tuple[int, int, int]:
        """Return the three recovered chairman objective choices."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.financial_objective_candidates(self.human.club_id)

    def select_financial_objective(self, candidate_index: int) -> int | float:
        """Accept one chairman objective and apply its immediate starting funds."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.select_financial_objective(
            self.human.club_id,
            int(candidate_index),
        )

    def squad(self) -> tuple[object, ...]:
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.ordered_club_roster(self.human.club_id)

    def search_scouting_players(
        self,
        panel_state: ScoutingReseedState,
        *,
        candidate_predicate: Callable[[object], bool],
        sort_mode: int = 0,
        secondary_score_mode: int | None = None,
        secondary_caller_argument: int = 0,
        history_average_resolver: Callable[[object], float] | None = None,
        position_label_resolver: Callable[[object], str] | None = None,
        valuation_resolver: Callable[[object], float] | None = None,
    ) -> tuple[object, ...]:
        """Run the recovered UI-independent PScouting2K result pipeline.

        The original first-stage predicate contains several panel controls whose
        user-facing labels are still intentionally neutral. candidate_predicate
        is therefore explicit rather than replaced with guessed UI semantics.

        Sort modes 3 and 5 require their source values only when selected.
        Sort mode 2 reads RuntimePlayer's exact six-byte 0x41FB60 history by
        default; history_average_resolver remains available only as an explicit
        compatibility override. The five-state form_state is never substituted.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")

        sort_mode = int(sort_mode)
        if (
            sort_mode == SCOUTING_SORT_MODE_POSITION_LABEL
            and position_label_resolver is None
        ):
            raise ValueError("sort mode 3 requires position_label_resolver")
        if sort_mode == SCOUTING_SORT_MODE_VALUE and valuation_resolver is None:
            raise ValueError("sort mode 5 requires valuation_resolver")

        human_club_id = int(self.human.club_id)
        on_date = self.state.calendar.current_date

        # 0x4AE680 rejects either registered-club or current/temporary-club
        # membership in the controlled club before applying the panel filters.
        candidates = tuple(
            player
            for player in self.state.players.values()
            if int(player.club_id) != human_club_id
            and (
                player.loan_club_id is None
                or int(player.loan_club_id) != human_club_id
            )
        )

        def values_for(player) -> ScoutingSortValues:
            age = player.age(on_date)
            if age is None:
                if sort_mode == 1 or secondary_score_mode is not None:
                    raise ValueError(
                        f"player {player.index} has no usable date of birth"
                    )
                age = 0

            club_name = ""
            if sort_mode == SCOUTING_SORT_MODE_CLUB_NAME:
                club = self.state.clubs.get(int(player.club_id))
                if club is None or not hasattr(club, "name"):
                    raise ValueError(
                        f"player {player.index} has no source-backed club name"
                    )
                club_name = str(club.name)

            return ScoutingSortValues(
                # FILE_FORMATS.md maps runtime +0x0C=surname and +0x08=first.
                name_primary=str(player.surname),
                name_secondary=str(player.first_name),
                age=int(age),
                history_average=(
                    float(history_average_resolver(player))
                    if history_average_resolver is not None
                    else float(player.match_performance_average())
                ),
                position_label=(
                    str(position_label_resolver(player))
                    if position_label_resolver is not None
                    else ""
                ),
                club_name=club_name,
                valuation=(
                    float(valuation_resolver(player))
                    if valuation_resolver is not None
                    else 0.0
                ),
            )

        def rank_values_for(player) -> ScoutingRankValues:
            age = player.age(on_date)
            if age is None:
                raise ValueError(
                    f"player {player.index} has no usable date of birth"
                )
            return ScoutingRankValues(
                current_raw=tuple(player.current_raw),
                preferred_positions=tuple(player.positions),
                age=int(age),
            )

        return run_scouting_search(
            candidates,
            panel_state,
            candidate_predicate=candidate_predicate,
            sort_mode=sort_mode,
            sort_values=values_for,
            secondary_score_mode=secondary_score_mode,
            secondary_caller_argument=int(secondary_caller_argument),
            rank_values=rank_values_for if secondary_score_mode is not None else None,
        )

    def search_scouting_players_mapped(
        self,
        panel_state: ScoutingReseedState,
        *,
        page_mode: int,
        valuation_resolver: Callable[[object], float],
        scout_strength_min: int = 20,
        threshold_predicate: Callable[[object], bool] | None = None,
        selected_position_id: int | None = None,
        team_selector_predicate: Callable[[object], bool] | None = None,
        optional_position_predicate: Callable[[object], bool] | None = None,
        status_controls: ScoutingFilterControls = ScoutingFilterControls(),
        out_of_contract_resolver: Callable[[object], bool] | None = None,
        loan_listed_resolver: Callable[[object], bool] | None = None,
        loan_list_user_match_resolver: Callable[[object], bool] | None = None,
        sort_mode: int = 0,
        secondary_score_mode: int | None = None,
        secondary_caller_argument: int = 0,
        history_average_resolver: Callable[[object], float] | None = None,
        position_label_resolver: Callable[[object], str] | None = None,
    ) -> tuple[object, ...]:
        """Apply the mapped 0x4AE680 gates before the recovered result pipeline.

        Country-context mode, preferred-position membership and the Strengths
        threshold now come from live RuntimePlayer/GameState state. The original
        Strengths selector stores 0 for All and 1..17 for current_raw slots;
        scout_strength_min defaults to the shipped value 20. The optional
        predicate callbacks are retained only as additional caller constraints
        for compatibility. Out-of-contract status now comes from persistent
        RuntimePlayer state produced by the mapped monthly contract lifecycle;
        out_of_contract_resolver remains only as an explicit compatibility
        override.
        """

        if self.human is None:
            raise RuntimeError("select a human club first")

        on_date = self.state.calendar.current_date
        human_club = self.state.clubs.get(int(self.human.club_id))
        if human_club is None:
            raise ValueError("human-controlled club metadata is unavailable")
        active_country_id = int(getattr(human_club, "country_id"))
        active_competition_id = int(getattr(human_club, "competition_id"))
        countries_by_nationality = {
            int(getattr(country, "nationality_id")): country
            for country in self.state.countries.values()
        }

        def mapped_predicate(player) -> bool:
            # 0x4AE610 uses registered-club country whenever the player has
            # club context; only unattached players fall back to nationality.
            if int(player.club_id) >= 0:
                registered_club = self.state.clubs.get(int(player.club_id))
                if registered_club is None:
                    raise ValueError(
                        f"club metadata for player {int(player.index)} is unavailable"
                    )
                candidate_country_id = int(getattr(registered_club, "country_id"))
                candidate_country = self.state.countries.get(candidate_country_id)
            else:
                candidate_country = countries_by_nationality.get(
                    int(player.nationality_id)
                )
                candidate_country_id = (
                    int(getattr(candidate_country, "id"))
                    if candidate_country is not None
                    else -1
                )
            if candidate_country is None:
                raise ValueError(
                    f"country metadata for player {int(player.index)} is unavailable"
                )
            if not scouting_country_context_passes(
                int(panel_state.field_64e0),
                candidate_country_id=candidate_country_id,
                candidate_european_index=int(
                    getattr(candidate_country, "european_index")
                ),
                active_club_country_id=active_country_id,
            ):
                return False
            if (
                team_selector_predicate is not None
                and not bool(team_selector_predicate(player))
            ):
                return False

            age = player.age(on_date)
            if age is None:
                return False

            preferred_role = int(player.positions[0])
            position = self.state.positions.get(preferred_role)
            if position is None:
                raise ValueError(
                    f"position metadata for preferred role {preferred_role} is unavailable"
                )
            player_class = int(position.lineup_group)
            if not 0 <= player_class < 4:
                raise ValueError(
                    f"preferred role {preferred_role} has no scouting class"
                )

            return scouting_first_stage_passes(
                panel_state,
                ScoutingFilterValues(
                    age=int(age),
                    valuation=float(valuation_resolver(player)),
                    player_class=player_class,
                    transfer_listed=bool(player.transfer_listed),
                    out_of_contract=(
                        bool(out_of_contract_resolver(player))
                        if out_of_contract_resolver is not None
                        else bool(player.out_of_contract)
                    ),
                    loan_listed=(
                        bool(loan_listed_resolver(player))
                        if loan_listed_resolver is not None
                        else bool(player.loan_listed)
                    ),
                    loan_list_user_match=(
                        bool(loan_list_user_match_resolver(player))
                        if loan_list_user_match_resolver is not None
                        else (
                            registered_club is not None
                            and scouting_loan_list_user_match(
                                transfer_listed=bool(player.transfer_listed),
                                non_eu=bool(player.non_eu),
                                registered_club_competition_id=int(
                                    getattr(registered_club, "competition_id")
                                ),
                                active_club_competition_id=active_competition_id,
                            )
                        )
                    ),
                    team_selector_passes=True,
                    optional_position_passes=(
                        scouting_preferred_position_passes(
                            player.positions,
                            selected_position_id,
                        )
                        and (
                            optional_position_predicate is None
                            or bool(optional_position_predicate(player))
                        )
                    ),
                    threshold_passes=(
                        scouting_strength_threshold_passes(
                            player.current_raw,
                            int(panel_state.field_64e4),
                            int(scout_strength_min),
                        )
                        and (
                            threshold_predicate is None
                            or bool(threshold_predicate(player))
                        )
                    ),
                ),
                page_mode=int(page_mode),
                status_controls=status_controls,
            )

        return self.search_scouting_players(
            panel_state,
            candidate_predicate=mapped_predicate,
            sort_mode=int(sort_mode),
            secondary_score_mode=secondary_score_mode,
            secondary_caller_argument=int(secondary_caller_argument),
            history_average_resolver=history_average_resolver,
            position_label_resolver=position_label_resolver,
            valuation_resolver=(
                valuation_resolver
                if int(sort_mode) == SCOUTING_SORT_MODE_VALUE
                else None
            ),
        )

    def set_player_training_method(self, player_id: int, method_id: int) -> None:
        """Assign one of the seven original per-player training methods."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        player_id = int(player_id)
        player = self.state.players.get(player_id)
        if player is None or int(player.club_id) != int(self.human.club_id):
            raise ValueError("player is not in the human-controlled squad")
        player.set_training_method(int(method_id))

    def set_tactics(self, tactics: TeamTacticalState) -> None:
        if self.human is None:
            raise RuntimeError("select a human club first")
        self.state.set_team_tactics(self.human.club_id, tactics)

    def set_team_orders(self, orders: TeamOrderPriorities) -> None:
        if self.human is None:
            raise RuntimeError("select a human club first")
        self.human.team_orders = orders

    def set_current_cash(self, amount: int):
        """Initialize/update the selected club's live Balance current cash."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.set_current_cash(self.human.club_id, int(amount))

    def submit_cash_bid(
        self,
        target_player_id: int,
        cash_fee: int,
    ) -> LiveCashBidEvaluation:
        """Submit and evaluate one recovered ordinary cash-only transfer bid."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return submit_live_cash_bid(
            self.state,
            target_player_id=int(target_player_id),
            buying_club_id=int(self.human.club_id),
            cash_fee=int(cash_fee),
        )

    def offer_player_contract(
        self,
        target_player_id: int,
        terms: ContractTerms,
        *,
        rng=None,
    ) -> OrdinaryMoneyResponseResult:
        """Submit player terms after the selling club accepted the cash bid.

        The method composes already recovered Gate-9 primitives. It does not
        invent the still-unmapped 0x422470 refusal/duration branches: those are
        returned explicitly by evaluate_ordinary_money_response.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")

        player_id = int(target_player_id)
        buyer_id = int(self.human.club_id)
        key = self.state.transfers.proposal_key(player_id, buyer_id)
        proposal = self.state.transfers.proposals.get(key)
        if proposal is None:
            raise RuntimeError("submit a cash bid for this player first")

        seller_response = evaluate_live_cash_bid(self.state, proposal)
        if seller_response.decision != SellingClubDecision.ACCEPTED:
            raise RuntimeError(
                f"selling club has not accepted the bid: "
                f"{seller_response.decision.value}"
            )

        if any(
            int(scheduled.proposal.target_player_id) == player_id
            and int(scheduled.proposal.buying_club_id) == buyer_id
            for scheduled in self.state.transfers.scheduled_transfers
        ):
            raise RuntimeError("this transfer is already scheduled")

        submitted = replace(proposal, contract_terms=terms)
        self.state.transfers.proposals[key] = submitted
        deal = self.state.transfers.deals.get(player_id)
        if deal is not None:
            deal.contract_terms = terms

        if rng is None:
            rng = self.match_rng
        result = evaluate_ordinary_money_response(
            self.state,
            submitted,
            rng,
        )

        self.state.transfers.proposals[key] = result.proposal
        if deal is not None:
            deal.contract_terms = result.proposal.contract_terms

        if result.outcome == OrdinaryMoneyResponse.ACCEPTED:
            schedule_ordinary_cash_transfer(
                self.state,
                result.proposal,
                mode=0,
            )
        return result

    def process_due_transfers(self):
        """Execute due transfers using the explicit Gate-10 affordability hook."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        results = execute_due_ordinary_cash_transfers(
            self.state,
            user_controlled_club_id=int(self.human.club_id),
        )
        self.last_transfer_executions = tuple(results)
        return self.last_transfer_executions

    def _prepare_human_selection(
        self,
        formation_id: int,
        starter_ids: Iterable[int],
        substitute_ids: Iterable[int],
    ) -> PreparedAiMatchSelection:
        if self.human is None:
            raise RuntimeError("select a human club first")

        formation_id = int(formation_id)
        if not 0 <= formation_id < len(AI_FORMATIONS):
            raise ValueError("formation_id must be in 0..20")

        starters = tuple(int(value) for value in starter_ids)
        substitutes = tuple(int(value) for value in substitute_ids)
        if len(starters) != 11:
            raise ValueError("human lineup requires exactly 11 starters")

        competition = self.state.competitions.get(0)
        if competition is None:
            raise RuntimeError("Premier League competition definition is not loaded")
        substitute_quota = resolved_substitute_quota(
            int(competition.substitute_quota)
        )
        if len(substitutes) != substitute_quota:
            raise ValueError(
                f"human lineup requires exactly {substitute_quota} substitutes"
            )

        all_selected = starters + substitutes
        if len(set(all_selected)) != len(all_selected):
            raise ValueError("human starters/substitutes must be unique")

        roster = self.state.ordered_club_roster(self.human.club_id)
        by_id = {int(player.index): player for player in roster}
        missing = tuple(player_id for player_id in all_selected if player_id not in by_id)
        if missing:
            raise ValueError(f"selected players are not in the human squad: {missing}")

        unavailable = tuple(
            player_id
            for player_id in all_selected
            if bool(by_id[player_id].base_match_unavailable)
        )
        if unavailable:
            raise ValueError(f"selected players are unavailable: {unavailable}")

        max_non_eu = int(competition.max_non_eu_players)
        selected_non_eu = sum(bool(by_id[player_id].non_eu) for player_id in all_selected)
        if selected_non_eu > max_non_eu:
            raise ValueError(
                f"human lineup contains {selected_non_eu} Non-EU players; "
                f"competition limit is {max_non_eu}"
            )

        for player in roster:
            player.clear_match_selection(reset_position=True)

        assignments: list[StarterAssignment] = []
        for player_id, slot in zip(starters, AI_FORMATIONS[formation_id]):
            player = by_id[player_id]
            player.assign_match_position(
                int(slot.role),
                int(slot.auxiliary_code),
            )
            player.set_match_active()
            assignments.append(
                StarterAssignment(
                    player_index=player_id,
                    role=int(slot.role),
                    auxiliary_code=int(slot.auxiliary_code),
                )
            )

        for player_id in substitutes:
            by_id[player_id].set_match_substitute_available()

        participants = collect_match_participants(
            self.human.club_id,
            roster,
        )
        if len(participants) != 11 + substitute_quota:
            raise RuntimeError("human participant collection did not match selection")

        return PreparedAiMatchSelection(
            lineup=AiLineupCoreResult(
                starters=tuple(assignments),
                substitutes=substitutes,
                unfilled_slot_indices=(),
            ),
            participants=tuple(participants),
            non_eu_restriction_relaxed=False,
        )

    def set_lineup(
        self,
        formation_id: int,
        starter_ids: Iterable[int],
        substitute_ids: Iterable[int],
    ) -> PreparedAiMatchSelection:
        """Persist the human XI/bench and apply it to live RuntimePlayer state."""

        selection = self._prepare_human_selection(
            formation_id,
            starter_ids,
            substitute_ids,
        )
        self.human.formation_id = int(formation_id)
        self.human.starter_ids = tuple(int(value) for value in starter_ids)
        self.human.substitute_ids = tuple(int(value) for value in substitute_ids)
        return selection

    def autofill_lineup(
        self,
        formation_id: int = 0,
    ) -> PreparedAiMatchSelection:
        """Choose a legal deterministic XI/bench using the proven selection core.

        This is a convenience for the temporary prototype and automated audits,
        not a replacement for manual human selection. It reuses the same
        evidence-backed slot/bench/Non-EU logic already used by AI selection,
        then persists the resulting player IDs as the human-controlled lineup.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")

        competition = self.state.competitions.get(0)
        if competition is None:
            raise RuntimeError("Premier League competition definition is not loaded")

        roster = self.state.ordered_club_roster(self.human.club_id)
        selection = prepare_ai_match_selection(
            self.human.club_id,
            roster,
            int(formation_id),
            resolved_substitute_quota(int(competition.substitute_quota)),
            require_complete_xi=True,
            non_eu_limit=int(competition.max_non_eu_players),
        )
        starter_ids = tuple(
            int(assignment.player_index)
            for assignment in selection.lineup.starters
        )
        substitute_ids = tuple(
            int(player_id)
            for player_id in selection.lineup.substitutes
        )
        return self.set_lineup(
            int(formation_id),
            starter_ids,
            substitute_ids,
        )

    def current_selection(self) -> PreparedAiMatchSelection:
        if self.human is None:
            raise RuntimeError("select a human club first")
        if not self.human.starter_ids:
            raise RuntimeError("set a human lineup first")
        return self._prepare_human_selection(
            self.human.formation_id,
            self.human.starter_ids,
            self.human.substitute_ids,
        )

    def _primary_entry_clubs(self, entry: tuple) -> tuple[int, int] | None:
        entry = tuple(entry)
        if entry[0] == "premier_league":
            fixture = self.state.premier_league.fixtures[int(entry[1])]
            return int(fixture.home_club_id), int(fixture.away_club_id)
        if entry[0] == "domestic_cup":
            node = self.state.domestic_cups.node(tuple(entry[1]))
            return node.resolve_pair(self.state.cup_results)
        raise ValueError(f"unsupported primary match entry {entry!r}")

    def _finish_shared_primary_day(self, had_results: bool) -> None:
        if (
            had_results
            and self.state.premier_league is not None
            and len(self.state.premier_league.results)
            == len(self.state.premier_league.fixtures)
        ):
            self.state.run_premier_league_financial_objective_season_transition()
        self.state.calendar.run_post_fixture_maintenance()
        controlled = None if self.human is None else self.human.club_id
        self.last_transfer_executions = tuple(
            self.state.run_due_transfer_maintenance(
                user_controlled_club_id=controlled,
            )
        )
        self.state.run_weekly_player_payroll()
        self.state.run_weekly_ai_transfer_maintenance(
            self.match_rng,
            user_controlled_club_id=controlled,
        )
        if self.state.finalize_single_user_sacking_control() is not None:
            self.human = None

    def advance_to_next_user_primary_match(self):
        """Advance until a tagged PL/Cup match involving the human is pending."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_primary_entry is not None:
            return self.pending_primary_entry

        while True:
            future_dates = [
                on_date
                for on_date in self.state.primary_matchday_order
                if on_date > self.state.calendar.current_date
            ]
            future_dates.extend(
                node.scheduled_date
                for node in self.state.domestic_cups.nodes
                if node.node_token not in self.state.domestic_cups.completed_node_tokens
                and node.scheduled_date > self.state.calendar.current_date
            )
            if not future_dates:
                return None

            self.state.calendar.increment_one_day()
            due_order = self.state.primary_entries_due_today()
            human_due = []
            for entry in due_order:
                pair = self._primary_entry_clubs(entry)
                if pair is not None and self.human.club_id in pair:
                    human_due.append(entry)

            if len(human_due) > 1:
                raise RuntimeError(
                    f"expected at most one human primary match on "
                    f"{self.state.calendar.current_date}, got {human_due}"
                )

            if not human_due:
                results = self.state.simulate_due_primary_ai_entries(
                    self.attack_matrix,
                    self.defence_matrix,
                    self.match_rng,
                )
                self._finish_shared_primary_day(bool(results))
                if self.human is None:
                    return None
                continue

            human_entry = human_due[0]
            split = due_order.index(human_entry)
            prior = tuple(
                (
                    entry,
                    self.state.simulate_primary_ai_entry(
                        entry,
                        self.attack_matrix,
                        self.defence_matrix,
                        self.match_rng,
                    ),
                )
                for entry in due_order[:split]
            )
            self.pending_primary_entry = human_entry
            self._pending_prior_primary_results = prior
            self._pending_after_primary_entries = tuple(due_order[split + 1 :])
            return human_entry

    def play_user_primary_match(self) -> HumanPrimaryMatchdayOutcome:
        """Play the pending tagged PL/Cup match and finish its shared matchday."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_primary_entry is None:
            raise RuntimeError("advance to a user primary match first")

        entry = self.pending_primary_entry
        selection = self.current_selection()
        if entry[0] == "premier_league":
            user_result = self.state.simulate_premier_league_human_fixture(
                int(entry[1]),
                self.human.club_id,
                selection,
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                team_orders=self.human.team_orders,
            )
        elif entry[0] == "domestic_cup":
            user_result, _completion = self.state.simulate_domestic_cup_human_node(
                tuple(entry[1]),
                self.human.club_id,
                selection,
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                team_orders=self.human.team_orders,
            )
        else:
            raise ValueError(f"unsupported primary match entry {entry!r}")

        trailing = tuple(
            (
                trailing_entry,
                self.state.simulate_primary_ai_entry(
                    trailing_entry,
                    self.attack_matrix,
                    self.defence_matrix,
                    self.match_rng,
                ),
            )
            for trailing_entry in self._pending_after_primary_entries
        )
        all_results = (
            self._pending_prior_primary_results
            + ((entry, user_result),)
            + trailing
        )
        self._finish_shared_primary_day(bool(all_results))

        self.pending_primary_entry = None
        self._pending_prior_primary_results = ()
        self._pending_after_primary_entries = ()

        return HumanPrimaryMatchdayOutcome(
            match_entry=entry,
            user_result=user_result,
            matchday_results=all_results,
            table=tuple(self.state.premier_league_table()),
        )

    def next_user_fixture(self):
        """Return the next unplayed PL fixture involving the human club."""

        if self.human is None:
            raise RuntimeError("select a human club first")

        current_date = self.state.calendar.current_date
        candidates = []
        for fixture in self.state.premier_league.fixtures.values():
            if int(fixture.id) in self.state.premier_league.results:
                continue
            if self.human.club_id not in (
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            ):
                continue
            fixture_date = self.state.premier_league.round_date(
                int(fixture.round_index)
            )
            if fixture_date is None or fixture_date < current_date:
                continue
            candidates.append((fixture_date, int(fixture.id), fixture))

        if not candidates:
            return None
        return min(candidates, key=lambda item: (item[0], item[1]))[2]

    def advance_to_next_user_fixture(self):
        """Advance autonomously until the human fixture is next to execute.

        Earlier fixtures on the same date are simulated in exact installed
        scheduler order. Later same-day fixtures remain pending until after the
        user fixture, preserving 0x615C10-style matchday order and ensuring
        daily maintenance still runs only after every fixture on that date.
        """

        if self.pending_fixture_id is not None:
            return self.state.premier_league.fixtures[self.pending_fixture_id]

        fixture = self.next_user_fixture()
        if fixture is None:
            return None
        target_date = self.state.premier_league.round_date(
            int(fixture.round_index)
        )
        if target_date is None:
            raise RuntimeError("human fixture has no reconstructed round date")

        while self.state.calendar.current_date + timedelta(days=1) < target_date:
            self.state.advance_one_day_with_premier_league_ai_fixtures(
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
            )

        if self.state.calendar.current_date < target_date:
            self.state.calendar.increment_one_day()

        due_order = self.state.due_premier_league_fixture_ids_in_scheduler_order()
        human_due = tuple(
            fixture_id
            for fixture_id in due_order
            if self.human.club_id
            in (
                int(self.state.premier_league.fixtures[fixture_id].home_club_id),
                int(self.state.premier_league.fixtures[fixture_id].away_club_id),
            )
        )
        if len(human_due) != 1:
            raise RuntimeError(
                f"expected exactly one human fixture on {target_date}, got {human_due}"
            )

        human_fixture_id = human_due[0]
        split = due_order.index(human_fixture_id)
        prior_results = []
        for fixture_id in due_order[:split]:
            prior_results.append(
                (
                    fixture_id,
                    self.state.simulate_premier_league_ai_fixture(
                        fixture_id,
                        self.attack_matrix,
                        self.defence_matrix,
                        self.match_rng,
                    ),
                )
            )

        self.pending_fixture_id = human_fixture_id
        self._pending_prior_results = tuple(prior_results)
        self._pending_after_fixture_ids = tuple(due_order[split + 1 :])
        return self.state.premier_league.fixtures[human_fixture_id]

    def play_user_fixture(self) -> HumanMatchdayOutcome:
        """Play the pending human fixture, finish the matchday, and return state."""

        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_fixture_id is None:
            raise RuntimeError("advance to a user fixture first")

        selection = self.current_selection()
        fixture_id = int(self.pending_fixture_id)
        user_result = self.state.simulate_premier_league_human_fixture(
            fixture_id,
            self.human.club_id,
            selection,
            self.attack_matrix,
            self.defence_matrix,
            self.match_rng,
            team_orders=self.human.team_orders,
        )

        trailing = []
        for ai_fixture_id in self._pending_after_fixture_ids:
            trailing.append(
                (
                    int(ai_fixture_id),
                    self.state.simulate_premier_league_ai_fixture(
                        int(ai_fixture_id),
                        self.attack_matrix,
                        self.defence_matrix,
                        self.match_rng,
                    ),
                )
            )

        all_results = (
            self._pending_prior_results
            + ((fixture_id, user_result),)
            + tuple(trailing)
        )
        # Matchday completion is the clean-room counterpart of the annual
        # competition-finalization boundary. Only the final PL matchday can
        # trigger the recovered sporting/financial objective transition.
        if (
            all_results
            and len(self.state.premier_league.results)
            == len(self.state.premier_league.fixtures)
        ):
            self.state.run_premier_league_financial_objective_season_transition()
        self.state.calendar.run_post_fixture_maintenance()
        self.last_transfer_executions = tuple(
            self.state.run_due_transfer_maintenance(
                user_controlled_club_id=self.human.club_id,
            )
        )
        self.state.run_weekly_player_payroll()
        self.state.run_weekly_ai_transfer_maintenance(
            self.match_rng,
            user_controlled_club_id=self.human.club_id,
        )

        # DBRUser +0x10D8 is consumed by the outer manager loop after the
        # reason-specific sacking message is queued. In single-user play the
        # original then leaves management for PStartMenu. Preserve the state,
        # but end active human control only after this matchday's maintenance.
        sacking_reason = self.state.finalize_single_user_sacking_control()
        if sacking_reason is not None:
            self.human = None

        self.pending_fixture_id = None
        self._pending_prior_results = ()
        self._pending_after_fixture_ids = ()

        return HumanMatchdayOutcome(
            fixture_id=fixture_id,
            user_result=user_result,
            matchday_results=all_results,
            table=tuple(self.state.premier_league_table()),
        )
