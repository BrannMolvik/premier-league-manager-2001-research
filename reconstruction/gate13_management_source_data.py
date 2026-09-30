"""Read-only source-data bridge for future original FM2001 management screens.

Gate 13 must keep presentation separate from simulation while preserving the
original game's recovered data/order semantics. This module exposes immutable
view data from the existing HumanGameplayController/GameState boundary only.

It deliberately DOES NOT define original screen IDs, widgets, coordinates,
fonts, colors, navigation, fixture-screen sorting, or other visual semantics
that have not yet been recovered from the authorized original executable/art.
Fixture rows preserve DBRRealFixture/runtime source insertion order; table rows
preserve GameState.premier_league_table(), which uses the recovered native
League comparator whenever original CP1252 short names are available.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


class ManagementPresentationError(ValueError):
    pass


@dataclass(frozen=True)
class ClubHeaderView:
    club_id: int
    name: str
    short_name: str
    current_date: date


@dataclass(frozen=True)
class SquadRowView:
    source_roster_index: int
    player_id: int
    full_name: str
    shirt_number: int
    positions: tuple[int, int, int]
    current_position: int
    match_unavailable: bool
    condition: int
    form_state: int
    morale: int
    injured: bool
    suspended: bool
    out_of_contract: bool
    transfer_listed: bool
    loan_listed: bool
    wanted: bool


@dataclass(frozen=True)
class FixtureRowView:
    source_fixture_index: int
    fixture_id: int
    round_index: int
    scheduled_date: date | None
    home_club_id: int
    home_club_name: str
    away_club_id: int
    away_club_name: str
    played: bool
    home_goals: int | None
    away_goals: int | None


@dataclass(frozen=True)
class LeagueTableRowView:
    position: int
    club_id: int
    club_name: str
    short_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


@dataclass(frozen=True)
class TacticsSelectionView:
    formation_id: int
    starter_ids: tuple[int, ...]
    substitute_ids: tuple[int, ...]
    play_style: int
    without_ball_style: int
    with_ball_style: int
    aggression: int
    captain_priority: tuple[int, ...]
    penalty_priority: tuple[int, ...]
    corner_priority: tuple[int, ...]
    free_kick_priority: tuple[int, ...]


@dataclass(frozen=True)
class PlayerProfileView:
    player_id: int
    first_name: str
    surname: str
    club_id: int
    club_name: str | None
    nationality_id: int
    date_of_birth: date | None
    shirt_number: int
    height_cm: int
    weight_kg: int
    positions: tuple[int, int, int]
    current_skill_bytes: tuple[int, ...]
    condition: int
    form_state: int
    morale: int
    weekly_wage: int
    contract_expiry_date: date | None
    injured: bool
    suspended: bool
    out_of_contract: bool
    transfer_listed: bool
    loan_listed: bool
    wanted: bool
    loan_club_id: int | None


@dataclass(frozen=True)
class FinancePostingView:
    amount: int | float
    category_id: int
    posting_date: date


@dataclass(frozen=True)
class FinancialObjectiveView:
    candidate_ids: tuple[int, int, int]
    selected_objective_id: int
    starting_funds: int | float
    target_cash: int | float
    selected_on: date | None
    deadline: date | None
    active: bool
    progression_gate_reached: bool
    progression_state: int


@dataclass(frozen=True)
class FinanceView:
    current_cash: int | float
    ledger_in_runtime_order: tuple[FinancePostingView, ...]
    objective: FinancialObjectiveView | None


@dataclass(frozen=True)
class TransferContractTermsView:
    weekly_wage: int
    signing_on_fee: int
    promotion_bonus: int
    contract_length_months: int
    appearance_fee: int
    relegation_transfer_request_clause: bool
    big_club_offer_clause: bool
    big_money_offer_clause: bool
    house: bool
    car: bool


@dataclass(frozen=True)
class TransferProposalView:
    runtime_order_index: int
    target_player_id: int
    target_player_name: str
    buying_club_id: int
    buying_club_name: str
    selling_club_id: int
    selling_club_name: str
    cash_fee: int
    exchange_player_ids: tuple[int, int, int]
    negotiation_state_14: int
    negotiation_state_15: int
    previous_wage_offer: int
    previous_signing_on_fee_offer: int
    previous_total_value: int
    contract_terms: TransferContractTermsView
    deal_state: int
    deal_base_state: int
    deal_is_swap_variant: bool
    deal_created_date: date
    scheduled_due_date: date | None
    scheduled_mode: int | None


@dataclass(frozen=True)
class ContractRenewalMessageView:
    queue_index: int
    player_id: int
    player_name: str
    queued_on: date
    message_id: int
    original_key: str
    event_class: str
    accepted_action_class: str


@dataclass(frozen=True)
class PlayerTransferRequestMessageView:
    queue_index: int
    player_id: int
    player_name: str
    queued_on: date
    due_on: date
    due: bool
    original_key: str
    event_class: str
    accepted_action_class: str
    refused_action_class: str


@dataclass(frozen=True)
class MessageSourceQueuesView:
    contract_renewal_in_runtime_order: tuple[ContractRenewalMessageView, ...]
    transfer_requests_in_runtime_order: tuple[PlayerTransferRequestMessageView, ...]


@dataclass(frozen=True)
class TrainingPlayerView:
    source_roster_index: int
    player_id: int
    player_name: str
    method_id: int
    countdown: int
    active_count: int
    skill_modifiers: tuple[int, ...]
    skill_states: tuple[int, ...]
    method_results: tuple[int, ...]


@dataclass(frozen=True)
class ScoutingResultView:
    result_index: int
    player_id: int
    player_name: str
    club_id: int
    club_name: str | None
    nationality_id: int
    positions: tuple[int, int, int]
    current_skill_bytes: tuple[int, ...]
    age: int | None
    history_average: float
    transfer_listed: bool
    out_of_contract: bool
    loan_listed: bool


@dataclass(frozen=True)
class ScoutingSortPresentationContract:
    mode: int
    semantic_key: str
    direction: str
    comparator_va: int


@dataclass(frozen=True)
class ScoutingPresentationContract:
    panel_class_name: str
    type_descriptor_va: int
    complete_object_locator_va: int
    vtable_va: int
    event_handler_va: int
    search_event_code: int
    search_dispatch_va: int
    search_build_va: int
    reseed_va: int
    source_path: str
    sort_modes: tuple[ScoutingSortPresentationContract, ...]


# Firsthand canonical-executable evidence only. semantic_key values are neutral
# reconstruction identifiers, NOT claims about original on-screen captions.
SCOUTING_PRESENTATION_CONTRACT = ScoutingPresentationContract(
    panel_class_name="PScouting2K",
    type_descriptor_va=0x81C9C0,
    complete_object_locator_va=0x7E3D20,
    vtable_va=0x7C2E6C,
    event_handler_va=0x4ADB50,
    search_event_code=31,
    search_dispatch_va=0x4AE0FB,
    search_build_va=0x4AE970,
    reseed_va=0x4AF7F0,
    source_path=r"D:\Projects\FM2001\Applications\FootballManager\MenuPan.cpp",
    sort_modes=(
        ScoutingSortPresentationContract(0, "player_name", "ascending", 0x4AF020),
        ScoutingSortPresentationContract(1, "age", "ascending", 0x4AF0B0),
        ScoutingSortPresentationContract(
            2, "history_average", "descending", 0x4AF200
        ),
        ScoutingSortPresentationContract(
            3, "position_display_string", "descending", 0x4AF270
        ),
        ScoutingSortPresentationContract(
            4, "club_display_name", "ascending", 0x4AF0F0
        ),
        ScoutingSortPresentationContract(5, "monetary_value", "descending", 0x4AF190),
    ),
)


@dataclass(frozen=True)
class ManagementSourceDataSnapshot:
    club: ClubHeaderView
    squad: tuple[SquadRowView, ...]
    tactics: TacticsSelectionView
    fixtures_in_source_order: tuple[FixtureRowView, ...]
    league_table: tuple[LeagueTableRowView, ...]


class ManagementSourceDataBridge:
    """Project recovered backend state into immutable presentation data.

    The bridge never advances time, mutates a lineup, performs a transfer, or
    simulates a match. The future original-resource renderer may consume these
    rows after its native control/layout behavior is independently recovered.
    """

    def __init__(self, controller):
        self.controller = controller

    @property
    def state(self):
        state = getattr(self.controller, "state", None)
        if state is None:
            raise ManagementPresentationError(
                "Management presentation requires a live game state"
            )
        return state

    def _human_club_id(self) -> int:
        human = getattr(self.controller, "human", None)
        if human is None:
            raise ManagementPresentationError(
                "Select a human-managed club before opening management presentation"
            )
        club_id = getattr(human, "club_id", None)
        if type(club_id) is not int:
            raise ManagementPresentationError("Human club ID is unavailable")
        return club_id

    def _source_club(self, club_id: int):
        clubs = getattr(self.state, "clubs", None)
        if not hasattr(clubs, "get"):
            raise ManagementPresentationError("Source club table is unavailable")
        club = clubs.get(int(club_id))
        if club is None:
            raise ManagementPresentationError(f"Unknown source club {club_id}")
        if not isinstance(getattr(club, "name", None), str):
            raise ManagementPresentationError(
                f"Source club {club_id} has no recovered display name"
            )
        if not isinstance(getattr(club, "short_name", None), str):
            raise ManagementPresentationError(
                f"Source club {club_id} has no recovered short name"
            )
        return club

    @staticmethod
    def _player_name(player) -> str:
        first = getattr(player, "first_name", None)
        surname = getattr(player, "surname", None)
        if not isinstance(first, str) or not isinstance(surname, str):
            raise ManagementPresentationError(
                "Runtime player lacks recovered source name fields"
            )
        return f"{first} {surname}".strip()

    def club_header(self) -> ClubHeaderView:
        club_id = self._human_club_id()
        club = self._source_club(club_id)
        calendar = getattr(self.state, "calendar", None)
        current_date = getattr(calendar, "current_date", None)
        if not isinstance(current_date, date):
            raise ManagementPresentationError("Game calendar date is unavailable")
        return ClubHeaderView(
            club_id=club_id,
            name=club.name,
            short_name=club.short_name,
            current_date=current_date,
        )

    def squad_rows(self) -> tuple[SquadRowView, ...]:
        self._human_club_id()
        squad = getattr(self.controller, "squad", None)
        if not callable(squad):
            raise ManagementPresentationError("Controlled-club roster is unavailable")
        rows = []
        for source_index, player in enumerate(tuple(squad())):
            player_id = getattr(player, "index", None)
            positions = getattr(player, "positions", None)
            if type(player_id) is not int:
                raise ManagementPresentationError("Runtime player ID is unavailable")
            if (
                not isinstance(positions, tuple)
                or len(positions) != 3
                or any(type(value) is not int for value in positions)
            ):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered three-position tuple"
                )
            rows.append(SquadRowView(
                source_roster_index=source_index,
                player_id=player_id,
                full_name=self._player_name(player),
                shirt_number=int(getattr(player, "shirt_number", 0)),
                positions=positions,
                current_position=int(getattr(player, "current_position")),
                match_unavailable=bool(getattr(player, "base_match_unavailable")),
                condition=int(getattr(player, "condition")),
                form_state=int(getattr(player, "form_state")),
                morale=int(getattr(player, "morale")),
                injured=bool(getattr(player, "injured")),
                suspended=bool(getattr(player, "suspended")),
                out_of_contract=bool(getattr(player, "out_of_contract")),
                transfer_listed=bool(getattr(player, "transfer_listed")),
                loan_listed=bool(getattr(player, "loan_listed")),
                wanted=bool(getattr(player, "wanted")),
            ))
        return tuple(rows)

    def tactics_selection(self) -> TacticsSelectionView:
        """Expose exact backend tactical/selection state without UI labels.

        TeamTacticalState's four values are recovered runtime fields and
        TeamOrderPriorities maps the four original stored priority lists.
        Formation/player IDs are the currently persisted human selection.
        """
        club_id = self._human_club_id()
        human = self.controller.human
        team_tactics = getattr(self.state, "team_tactics", None)
        if not hasattr(team_tactics, "get"):
            raise ManagementPresentationError(
                "Recovered team tactical state is unavailable"
            )
        tactics = team_tactics.get(club_id)
        if tactics is None:
            raise ManagementPresentationError(
                f"Controlled club {club_id} has no recovered tactical state"
            )
        orders = getattr(human, "team_orders", None)
        required_order_fields = ("captain", "penalty", "corner", "free_kick")
        if orders is None or any(
            not isinstance(getattr(orders, name, None), tuple)
            for name in required_order_fields
        ):
            raise ManagementPresentationError(
                "Recovered human Team Orders priority lists are unavailable"
            )
        starter_ids = getattr(human, "starter_ids", None)
        substitute_ids = getattr(human, "substitute_ids", None)
        if not isinstance(starter_ids, tuple) or not isinstance(substitute_ids, tuple):
            raise ManagementPresentationError(
                "Recovered human lineup selection is unavailable"
            )
        if any(type(value) is not int for value in starter_ids + substitute_ids):
            raise ManagementPresentationError(
                "Human lineup player IDs must remain integer source IDs"
            )
        formation_id = getattr(human, "formation_id", None)
        if type(formation_id) is not int:
            raise ManagementPresentationError("Human formation ID is unavailable")
        return TacticsSelectionView(
            formation_id=formation_id,
            starter_ids=starter_ids,
            substitute_ids=substitute_ids,
            play_style=int(getattr(tactics, "play_style")),
            without_ball_style=int(getattr(tactics, "without_ball_style")),
            with_ball_style=int(getattr(tactics, "with_ball_style")),
            aggression=int(getattr(tactics, "aggression")),
            captain_priority=tuple(int(v) for v in orders.captain),
            penalty_priority=tuple(int(v) for v in orders.penalty),
            corner_priority=tuple(int(v) for v in orders.corner),
            free_kick_priority=tuple(int(v) for v in orders.free_kick),
        )

    def player_profile(self, player_id: int) -> PlayerProfileView:
        """Expose recovered runtime/source player data without invented UI labels.

        The current 17-byte skill vector is the live DBRPlayer state already
        reconstructed by the backend. Development target bytes are deliberately
        NOT exposed here because they are not established as player-profile UI.
        """
        if type(player_id) is not int:
            raise ManagementPresentationError("Player profile ID must be an integer")
        players = getattr(self.state, "players", None)
        if not hasattr(players, "get"):
            raise ManagementPresentationError("Runtime player table is unavailable")
        player = players.get(player_id)
        if player is None:
            raise ManagementPresentationError(f"Unknown runtime player {player_id}")
        first = getattr(player, "first_name", None)
        surname = getattr(player, "surname", None)
        if not isinstance(first, str) or not isinstance(surname, str):
            raise ManagementPresentationError(
                f"Player {player_id} lacks recovered source name fields"
            )
        club_id = getattr(player, "club_id", None)
        nationality_id = getattr(player, "nationality_id", None)
        if type(club_id) is not int or type(nationality_id) is not int:
            raise ManagementPresentationError(
                f"Player {player_id} lacks recovered club/nationality IDs"
            )
        club = self._source_club(club_id) if club_id >= 0 else None
        positions = getattr(player, "positions", None)
        if (
            not isinstance(positions, tuple)
            or len(positions) != 3
            or any(type(value) is not int for value in positions)
        ):
            raise ManagementPresentationError(
                f"Player {player_id} has no recovered three-position tuple"
            )
        current = getattr(player, "current_raw", None)
        if (
            not isinstance(current, (list, tuple))
            or len(current) != 17
            or any(type(value) is not int for value in current)
        ):
            raise ManagementPresentationError(
                f"Player {player_id} has no recovered 17-byte current-skill vector"
            )
        dob = getattr(player, "date_of_birth", None)
        if dob is not None and not isinstance(dob, date):
            raise ManagementPresentationError(
                f"Player {player_id} has invalid recovered date of birth"
            )
        expiry = getattr(player, "contract_expiry_date", None)
        if expiry is not None and not isinstance(expiry, date):
            raise ManagementPresentationError(
                f"Player {player_id} has invalid recovered contract expiry"
            )
        loan_club = getattr(player, "loan_club_id", None)
        if loan_club is not None and type(loan_club) is not int:
            raise ManagementPresentationError(
                f"Player {player_id} has invalid recovered loan club ID"
            )
        return PlayerProfileView(
            player_id=player_id,
            first_name=first,
            surname=surname,
            club_id=club_id,
            club_name=(None if club is None else club.name),
            nationality_id=nationality_id,
            date_of_birth=dob,
            shirt_number=int(getattr(player, "shirt_number")),
            height_cm=int(getattr(player, "height_cm")),
            weight_kg=int(getattr(player, "weight_kg")),
            positions=positions,
            current_skill_bytes=tuple(current),
            condition=int(getattr(player, "condition")),
            form_state=int(getattr(player, "form_state")),
            morale=int(getattr(player, "morale")),
            weekly_wage=int(getattr(player, "weekly_wage")),
            contract_expiry_date=expiry,
            injured=bool(getattr(player, "injured")),
            suspended=bool(getattr(player, "suspended")),
            out_of_contract=bool(getattr(player, "out_of_contract")),
            transfer_listed=bool(getattr(player, "transfer_listed")),
            loan_listed=bool(getattr(player, "loan_listed")),
            wanted=bool(getattr(player, "wanted")),
            loan_club_id=loan_club,
        )

    @staticmethod
    def _money_value(value, *, label: str) -> int | float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ManagementPresentationError(f"{label} is not a recovered finance value")
        return value

    def finance_view(self) -> FinanceView:
        """Expose Balance cash/ledger/objective state without guessed labels."""
        club_id = self._human_club_id()
        balances = getattr(self.state, "finance_balances", None)
        if not hasattr(balances, "get"):
            raise ManagementPresentationError("Recovered Balance state is unavailable")
        balance = balances.get(club_id)
        if balance is None:
            raise ManagementPresentationError(
                f"Controlled club {club_id} has no materialized Balance"
            )
        current_cash = self._money_value(
            getattr(balance, "current_cash", None), label="Current cash"
        )
        ledger = getattr(balance, "ledger", None)
        if not isinstance(ledger, list):
            raise ManagementPresentationError("Recovered finance ledger is unavailable")
        postings = []
        for posting in ledger:
            amount = self._money_value(
                getattr(posting, "amount", None), label="Finance posting amount"
            )
            category = getattr(posting, "category", None)
            posting_date = getattr(posting, "posting_date", None)
            if type(category) is not int or not isinstance(posting_date, date):
                raise ManagementPresentationError(
                    "Recovered finance posting identity/date is unavailable"
                )
            postings.append(FinancePostingView(
                amount=amount,
                category_id=category,
                posting_date=posting_date,
            ))

        objective_state = getattr(balance, "financial_objective", None)
        objective = None
        if objective_state is not None:
            candidates = getattr(objective_state, "candidate_ids", None)
            if (
                not isinstance(candidates, tuple)
                or len(candidates) != 3
                or any(type(value) is not int for value in candidates)
            ):
                raise ManagementPresentationError(
                    "Recovered financial-objective candidates are unavailable"
                )
            selected_on = getattr(objective_state, "selected_on", None)
            deadline = getattr(objective_state, "deadline", None)
            if selected_on is not None and not isinstance(selected_on, date):
                raise ManagementPresentationError(
                    "Financial-objective selection date is invalid"
                )
            if deadline is not None and not isinstance(deadline, date):
                raise ManagementPresentationError(
                    "Financial-objective deadline is invalid"
                )
            objective = FinancialObjectiveView(
                candidate_ids=candidates,
                selected_objective_id=int(
                    getattr(objective_state, "selected_objective_id")
                ),
                starting_funds=self._money_value(
                    getattr(objective_state, "starting_funds", None),
                    label="Objective starting funds",
                ),
                target_cash=self._money_value(
                    getattr(objective_state, "target_cash", None),
                    label="Objective target cash",
                ),
                selected_on=selected_on,
                deadline=deadline,
                active=bool(getattr(objective_state, "active")),
                progression_gate_reached=bool(
                    getattr(objective_state, "progression_gate_reached")
                ),
                progression_state=int(
                    getattr(objective_state, "progression_state")
                ),
            )
        return FinanceView(
            current_cash=current_cash,
            ledger_in_runtime_order=tuple(postings),
            objective=objective,
        )

    def transfer_proposal_rows(self) -> tuple[TransferProposalView, ...]:
        """Expose active clean-room transfer records without UI-state names."""
        transfers = getattr(self.state, "transfers", None)
        proposals = getattr(transfers, "proposals", None)
        deals = getattr(transfers, "deals", None)
        scheduled = getattr(transfers, "scheduled_transfers", None)
        if (
            not isinstance(proposals, dict)
            or not isinstance(deals, dict)
            or not isinstance(scheduled, list)
        ):
            raise ManagementPresentationError(
                "Recovered transfer runtime collections are unavailable"
            )
        players = getattr(self.state, "players", None)
        if not hasattr(players, "get"):
            raise ManagementPresentationError("Runtime player table is unavailable")
        rows = []
        for runtime_index, (key, proposal) in enumerate(proposals.items()):
            target_id = int(getattr(proposal, "target_player_id"))
            buying_id = int(getattr(proposal, "buying_club_id"))
            if key != (target_id, buying_id):
                raise ManagementPresentationError(
                    "Transfer proposal dictionary key differs from runtime proposal identity"
                )
            target = players.get(target_id)
            if target is None:
                raise ManagementPresentationError(
                    f"Transfer target {target_id} is missing from runtime players"
                )
            deal = deals.get(target_id)
            if deal is None:
                raise ManagementPresentationError(
                    f"Transfer target {target_id} has no recovered DealInProgress"
                )
            selling_id = int(getattr(deal, "selling_club_id"))
            buying = self._source_club(buying_id)
            selling = self._source_club(selling_id)
            exchange = getattr(proposal, "exchange_player_ids", None)
            if (
                not isinstance(exchange, tuple)
                or len(exchange) != 3
                or any(type(value) is not int for value in exchange)
            ):
                raise ManagementPresentationError(
                    f"Transfer target {target_id} has invalid exchange-player slots"
                )
            terms = getattr(proposal, "contract_terms", None)
            if terms is None:
                raise ManagementPresentationError(
                    f"Transfer target {target_id} has no contract terms"
                )
            created = getattr(deal, "created_date", None)
            if not isinstance(created, date):
                raise ManagementPresentationError(
                    f"Transfer target {target_id} has invalid deal date"
                )
            matching_scheduled = [
                item for item in scheduled
                if int(getattr(item.proposal, "target_player_id")) == target_id
                and int(getattr(item.proposal, "buying_club_id")) == buying_id
            ]
            if len(matching_scheduled) > 1:
                raise ManagementPresentationError(
                    f"Transfer target {target_id} has ambiguous scheduled records"
                )
            due = None
            mode = None
            if matching_scheduled:
                item = matching_scheduled[0]
                due = getattr(item, "due_date", None)
                mode = getattr(item, "mode", None)
                if not isinstance(due, date) or type(mode) is not int:
                    raise ManagementPresentationError(
                        f"Transfer target {target_id} has invalid schedule state"
                    )
            rows.append(TransferProposalView(
                runtime_order_index=runtime_index,
                target_player_id=target_id,
                target_player_name=self._player_name(target),
                buying_club_id=buying_id,
                buying_club_name=buying.name,
                selling_club_id=selling_id,
                selling_club_name=selling.name,
                cash_fee=int(getattr(proposal, "cash_fee")),
                exchange_player_ids=exchange,
                negotiation_state_14=int(getattr(proposal, "negotiation_state_14")),
                negotiation_state_15=int(getattr(proposal, "negotiation_state_15")),
                previous_wage_offer=int(getattr(proposal, "previous_wage_offer")),
                previous_signing_on_fee_offer=int(
                    getattr(proposal, "previous_signing_on_fee_offer")
                ),
                previous_total_value=int(getattr(proposal, "previous_total_value")),
                contract_terms=TransferContractTermsView(
                    weekly_wage=int(getattr(terms, "weekly_wage")),
                    signing_on_fee=int(getattr(terms, "signing_on_fee")),
                    promotion_bonus=int(getattr(terms, "promotion_bonus")),
                    contract_length_months=int(
                        getattr(terms, "contract_length_months")
                    ),
                    appearance_fee=int(getattr(terms, "appearance_fee")),
                    relegation_transfer_request_clause=bool(
                        getattr(terms, "relegation_transfer_request_clause")
                    ),
                    big_club_offer_clause=bool(
                        getattr(terms, "big_club_offer_clause")
                    ),
                    big_money_offer_clause=bool(
                        getattr(terms, "big_money_offer_clause")
                    ),
                    house=bool(getattr(terms, "house")),
                    car=bool(getattr(terms, "car")),
                ),
                deal_state=int(getattr(deal, "state")),
                deal_base_state=int(getattr(deal, "base_state")),
                deal_is_swap_variant=bool(getattr(deal, "is_swap_variant")),
                deal_created_date=created,
                scheduled_due_date=due,
                scheduled_mode=mode,
            ))
        return tuple(rows)

    def message_source_queues(self) -> MessageSourceQueuesView:
        """Expose only the two manager-mail families materialized by GameState.

        They remain separate queues because the clean-room runtime currently
        stores them separately; merging by date would invent a global mail-list
        ordering that has not been reconstructed.
        """
        self._human_club_id()
        players = getattr(self.state, "players", None)
        renewals = getattr(self.state, "contract_renewal_suggestions", None)
        requests = getattr(self.state, "player_transfer_requests", None)
        calendar = getattr(self.state, "calendar", None)
        current_date = getattr(calendar, "current_date", None)
        if not hasattr(players, "get"):
            raise ManagementPresentationError("Runtime player table is unavailable")
        if not isinstance(renewals, list) or not isinstance(requests, list):
            raise ManagementPresentationError(
                "Recovered manager-mail source queues are unavailable"
            )
        if not isinstance(current_date, date):
            raise ManagementPresentationError("Game calendar date is unavailable")

        renewal_rows = []
        for index, item in enumerate(renewals):
            player_id = getattr(item, "player_id", None)
            queued_on = getattr(item, "queued_on", None)
            if type(player_id) is not int or not isinstance(queued_on, date):
                raise ManagementPresentationError(
                    "Contract-renewal mail identity/date is unavailable"
                )
            player = players.get(player_id)
            if player is None:
                raise ManagementPresentationError(
                    f"Contract-renewal mail player {player_id} is missing"
                )
            message_id = getattr(item, "message_id", None)
            original_key = getattr(item, "original_key", None)
            event_class = getattr(item, "event_class", None)
            accepted = getattr(item, "accepted_action_class", None)
            if (
                type(message_id) is not int
                or not isinstance(original_key, str)
                or not isinstance(event_class, str)
                or not isinstance(accepted, str)
            ):
                raise ManagementPresentationError(
                    f"Contract-renewal mail {player_id} lacks recovered event identity"
                )
            renewal_rows.append(ContractRenewalMessageView(
                queue_index=index,
                player_id=player_id,
                player_name=self._player_name(player),
                queued_on=queued_on,
                message_id=message_id,
                original_key=original_key,
                event_class=event_class,
                accepted_action_class=accepted,
            ))

        request_rows = []
        for index, item in enumerate(requests):
            player_id = getattr(item, "player_id", None)
            queued_on = getattr(item, "queued_on", None)
            due_on = getattr(item, "due_on", None)
            if (
                type(player_id) is not int
                or not isinstance(queued_on, date)
                or not isinstance(due_on, date)
            ):
                raise ManagementPresentationError(
                    "Transfer-request mail identity/date is unavailable"
                )
            player = players.get(player_id)
            if player is None:
                raise ManagementPresentationError(
                    f"Transfer-request mail player {player_id} is missing"
                )
            original_key = getattr(item, "original_key", None)
            event_class = getattr(item, "event_class", None)
            accepted = getattr(item, "accepted_action_class", None)
            refused = getattr(item, "refused_action_class", None)
            if any(
                not isinstance(value, str)
                for value in (original_key, event_class, accepted, refused)
            ):
                raise ManagementPresentationError(
                    f"Transfer-request mail {player_id} lacks recovered event identity"
                )
            request_rows.append(PlayerTransferRequestMessageView(
                queue_index=index,
                player_id=player_id,
                player_name=self._player_name(player),
                queued_on=queued_on,
                due_on=due_on,
                due=due_on <= current_date,
                original_key=original_key,
                event_class=event_class,
                accepted_action_class=accepted,
                refused_action_class=refused,
            ))
        return MessageSourceQueuesView(
            contract_renewal_in_runtime_order=tuple(renewal_rows),
            transfer_requests_in_runtime_order=tuple(request_rows),
        )

    def training_rows(self) -> tuple[TrainingPlayerView, ...]:
        """Expose recovered embedded per-player training state in roster order."""
        self._human_club_id()
        squad = getattr(self.controller, "squad", None)
        if not callable(squad):
            raise ManagementPresentationError("Controlled-club roster is unavailable")
        rows = []
        for source_index, player in enumerate(tuple(squad())):
            player_id = getattr(player, "index", None)
            modifiers = getattr(player, "training_modifiers", None)
            states = getattr(player, "training_skill_states", None)
            results = getattr(player, "training_method_results", None)
            if type(player_id) is not int:
                raise ManagementPresentationError("Runtime player ID is unavailable")
            if (
                not isinstance(modifiers, list)
                or len(modifiers) != 17
                or any(type(value) is not int for value in modifiers)
            ):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered 17-byte training modifiers"
                )
            if (
                not isinstance(states, list)
                or len(states) != 17
                or any(type(value) is not int for value in states)
            ):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered 17-entry training state"
                )
            if (
                not isinstance(results, list)
                or len(results) != 7
                or any(type(value) is not int for value in results)
            ):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered seven-method training result state"
                )
            rows.append(TrainingPlayerView(
                source_roster_index=source_index,
                player_id=player_id,
                player_name=self._player_name(player),
                method_id=int(getattr(player, "training_method_id")),
                countdown=int(getattr(player, "training_countdown")),
                active_count=int(getattr(player, "training_active_count")),
                skill_modifiers=tuple(modifiers),
                skill_states=tuple(states),
                method_results=tuple(results),
            ))
        return tuple(rows)

    @staticmethod
    def scouting_presentation_contract() -> ScoutingPresentationContract:
        """Return only the source-proven PScouting2K interaction contract.

        The semantic keys describe recovered comparator inputs for clean-room
        code. They are deliberately not original UI captions, control IDs,
        geometry, or artwork bindings.
        """
        return SCOUTING_PRESENTATION_CONTRACT

    def scouting_search_rows(
        self,
        panel_state,
        *,
        page_mode: int,
        valuation_resolver,
        scout_strength_min: int = 20,
        threshold_predicate=None,
        selected_position_id: int | None = None,
        team_selector_predicate=None,
        optional_position_predicate=None,
        status_controls=None,
        out_of_contract_resolver=None,
        loan_listed_resolver=None,
        loan_list_user_match_resolver=None,
        sort_mode: int = 0,
        secondary_score_mode: int | None = None,
        secondary_caller_argument: int = 0,
        history_average_resolver=None,
        position_label_resolver=None,
    ) -> tuple[ScoutingResultView, ...]:
        """Delegate to the already source-mapped PScouting2K pipeline.

        This method deliberately requires the caller to supply the existing
        panel state and valuation resolver. It does not invent unresolved
        controls. Result order is exactly the controller pipeline result.
        """
        self._human_club_id()
        search = getattr(self.controller, "search_scouting_players_mapped", None)
        if not callable(search):
            raise ManagementPresentationError(
                "Recovered mapped scouting search is unavailable"
            )
        kwargs = dict(
            page_mode=int(page_mode),
            valuation_resolver=valuation_resolver,
            scout_strength_min=int(scout_strength_min),
            threshold_predicate=threshold_predicate,
            selected_position_id=selected_position_id,
            team_selector_predicate=team_selector_predicate,
            optional_position_predicate=optional_position_predicate,
            out_of_contract_resolver=out_of_contract_resolver,
            loan_listed_resolver=loan_listed_resolver,
            loan_list_user_match_resolver=loan_list_user_match_resolver,
            sort_mode=int(sort_mode),
            secondary_score_mode=secondary_score_mode,
            secondary_caller_argument=int(secondary_caller_argument),
            history_average_resolver=history_average_resolver,
            position_label_resolver=position_label_resolver,
        )
        if status_controls is not None:
            kwargs["status_controls"] = status_controls
        try:
            players = tuple(search(panel_state, **kwargs))
        except (TypeError, ValueError, RuntimeError, KeyError) as exc:
            raise ManagementPresentationError(
                f"Mapped scouting search could not be projected: {exc}"
            ) from exc

        on_date = getattr(getattr(self.state, "calendar", None), "current_date", None)
        if not isinstance(on_date, date):
            raise ManagementPresentationError("Game calendar date is unavailable")
        rows = []
        for result_index, player in enumerate(players):
            player_id = getattr(player, "index", None)
            club_id = getattr(player, "club_id", None)
            nationality_id = getattr(player, "nationality_id", None)
            positions = getattr(player, "positions", None)
            current = getattr(player, "current_raw", None)
            if type(player_id) is not int or type(club_id) is not int:
                raise ManagementPresentationError(
                    "Scouting result lacks recovered player/club identity"
                )
            if type(nationality_id) is not int:
                raise ManagementPresentationError(
                    f"Scouting result {player_id} lacks nationality identity"
                )
            if (
                not isinstance(positions, tuple)
                or len(positions) != 3
                or any(type(value) is not int for value in positions)
            ):
                raise ManagementPresentationError(
                    f"Scouting result {player_id} lacks three-position tuple"
                )
            if (
                not isinstance(current, (list, tuple))
                or len(current) != 17
                or any(type(value) is not int for value in current)
            ):
                raise ManagementPresentationError(
                    f"Scouting result {player_id} lacks current 17-byte skill state"
                )
            club = self._source_club(club_id) if club_id >= 0 else None
            age_method = getattr(player, "age", None)
            if not callable(age_method):
                raise ManagementPresentationError(
                    f"Scouting result {player_id} has no recovered age accessor"
                )
            age = age_method(on_date)
            if age is not None:
                age = int(age)
            history_method = getattr(player, "match_performance_average", None)
            if not callable(history_method):
                raise ManagementPresentationError(
                    f"Scouting result {player_id} has no recovered history average"
                )
            rows.append(ScoutingResultView(
                result_index=result_index,
                player_id=player_id,
                player_name=self._player_name(player),
                club_id=club_id,
                club_name=(None if club is None else club.name),
                nationality_id=nationality_id,
                positions=positions,
                current_skill_bytes=tuple(current),
                age=age,
                history_average=float(history_method()),
                transfer_listed=bool(getattr(player, "transfer_listed")),
                out_of_contract=bool(getattr(player, "out_of_contract")),
                loan_listed=bool(getattr(player, "loan_listed")),
            ))
        return tuple(rows)

    def fixture_rows(self) -> tuple[FixtureRowView, ...]:
        league = getattr(self.state, "premier_league", None)
        if league is None:
            raise ManagementPresentationError("Premier League state is unavailable")
        source_order = getattr(league, "fixture_source_order", None)
        fixtures = getattr(league, "fixtures", None)
        results = getattr(league, "results", None)
        round_date = getattr(league, "round_date", None)
        if (
            not isinstance(source_order, tuple)
            or not hasattr(fixtures, "get")
            or not hasattr(results, "get")
            or not callable(round_date)
        ):
            raise ManagementPresentationError(
                "Recovered Premier League fixture source ordering is unavailable"
            )
        rows = []
        for source_index, fixture_id in enumerate(source_order):
            fixture = fixtures.get(int(fixture_id))
            if fixture is None:
                raise ManagementPresentationError(
                    f"Source-order fixture {fixture_id} is missing"
                )
            home_id = int(fixture.home_club_id)
            away_id = int(fixture.away_club_id)
            home = self._source_club(home_id)
            away = self._source_club(away_id)
            result = results.get(int(fixture_id))
            scheduled = round_date(int(fixture.round_index))
            if scheduled is not None and not isinstance(scheduled, date):
                raise ManagementPresentationError(
                    f"Fixture {fixture_id} has invalid recovered date"
                )
            rows.append(FixtureRowView(
                source_fixture_index=source_index,
                fixture_id=int(fixture_id),
                round_index=int(fixture.round_index),
                scheduled_date=scheduled,
                home_club_id=home_id,
                home_club_name=home.name,
                away_club_id=away_id,
                away_club_name=away.name,
                played=result is not None,
                home_goals=(None if result is None else int(result.home_goals)),
                away_goals=(None if result is None else int(result.away_goals)),
            ))
        return tuple(rows)

    def pending_fixture(self) -> FixtureRowView | None:
        """Return the pending human fixture through the same source-data seam."""
        self._human_club_id()
        pending = getattr(self.controller, "pending_fixture_id", None)
        if pending is None:
            return None
        if type(pending) is not int:
            raise ManagementPresentationError(
                "Pending human fixture ID is not a recovered integer identity"
            )
        matches = tuple(
            row for row in self.fixture_rows()
            if int(row.fixture_id) == pending
        )
        if len(matches) != 1:
            raise ManagementPresentationError(
                f"Pending fixture {pending} is absent or ambiguous in source fixtures"
            )
        return matches[0]

    def league_table_rows(self) -> tuple[LeagueTableRowView, ...]:
        table = getattr(self.state, "premier_league_table", None)
        if not callable(table):
            raise ManagementPresentationError(
                "Recovered Premier League table projection is unavailable"
            )
        rows = []
        for position, row in enumerate(tuple(table()), start=1):
            club_id = int(row.club_id)
            club = self._source_club(club_id)
            rows.append(LeagueTableRowView(
                position=position,
                club_id=club_id,
                club_name=(None if club is None else club.name),
                short_name=club.short_name,
                played=int(row.played),
                wins=int(row.wins),
                draws=int(row.draws),
                losses=int(row.losses),
                goals_for=int(row.goals_for),
                goals_against=int(row.goals_against),
                goal_difference=int(row.goal_difference),
                points=int(row.points),
            ))
        return tuple(rows)

    def snapshot(self) -> ManagementSourceDataSnapshot:
        return ManagementSourceDataSnapshot(
            club=self.club_header(),
            squad=self.squad_rows(),
            tactics=self.tactics_selection(),
            fixtures_in_source_order=self.fixture_rows(),
            league_table=self.league_table_rows(),
        )
