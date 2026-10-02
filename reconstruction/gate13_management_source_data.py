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
    recent_form_average: float
    current_role_rating: int
    morale: int
    injured: bool
    suspended: bool
    out_of_contract: bool
    transfer_listed: bool
    loan_listed: bool
    wanted: bool


@dataclass(frozen=True)
class SquadPresentationContract:
    team_roster_ids_offset: int
    team_roster_count_offset: int
    team_roster_player_id_size: int
    participant_collector_va: int
    active_predicate_va: int
    substitute_predicate_va: int
    active_setter_va: int
    substitute_setter_va: int
    removal_helper_va: int
    current_club_selection_flags_offset: int
    active_flag_mask: int
    substitute_flag_mask: int
    participant_order_preserves_team_roster_order: bool
    original_screen_sort_proven: bool
    screen_class_name: str | None


# Firsthand canonical-executable evidence only. These values describe the
# ordered DBRTeam/DBRPlayer backend state consumed by match preparation; they
# do not identify an original Squad screen class, row sort or visual layout.
SQUAD_PRESENTATION_CONTRACT = SquadPresentationContract(
    team_roster_ids_offset=0x244,
    team_roster_count_offset=0x294,
    team_roster_player_id_size=2,
    participant_collector_va=0x510CD0,
    active_predicate_va=0x417F50,
    substitute_predicate_va=0x417F60,
    active_setter_va=0x4182F0,
    substitute_setter_va=0x4182C0,
    removal_helper_va=0x4181B0,
    current_club_selection_flags_offset=0x14,
    active_flag_mask=0x10,
    substitute_flag_mask=0x20,
    participant_order_preserves_team_roster_order=True,
    original_screen_sort_proven=False,
    screen_class_name=None,
)


@dataclass(frozen=True)
class FixturesPresentationContract:
    table_class_name: str
    table_vtable_va: int
    table_global_va: int
    record_class_name: str
    record_vtable_va: int
    record_size: int
    static_table_offset: int
    shipped_fixture_count: int
    shipped_round_count: int
    fixtures_per_round: int
    round_table_class_name: str
    round_table_vtable_va: int
    round_table_global_va: int
    round_record_class_name: str
    round_record_vtable_va: int
    round_attach_va: int
    fixture_attach_start_va: int
    fixture_attach_end_va: int
    fixed_builder_va: int
    league_add_round_va: int
    league_match_constructor_va: int
    schedule_insert_va: int
    source_order_preserved_before_schedule_insertion: bool
    rng_before_fixed_schedule_insertion: bool
    original_screen_sort_proven: bool
    screen_class_name: str | None


FIXTURES_PRESENTATION_CONTRACT = FixturesPresentationContract(
    table_class_name="DBTRealFixtures",
    table_vtable_va=0x7C9884,
    table_global_va=0x876C18,
    record_class_name="DBRRealFixture",
    record_vtable_va=0x7C9898,
    record_size=0x14,
    static_table_offset=0x10057,
    shipped_fixture_count=380,
    shipped_round_count=38,
    fixtures_per_round=10,
    round_table_class_name="DBTRounds",
    round_table_vtable_va=0x7C99C4,
    round_table_global_va=0x876BD0,
    round_record_class_name="DBRRound",
    round_record_vtable_va=0x7C99D8,
    round_attach_va=0x4F72D0,
    fixture_attach_start_va=0x4F76A4,
    fixture_attach_end_va=0x4F770D,
    fixed_builder_va=0x6173D0,
    league_add_round_va=0x4F4500,
    league_match_constructor_va=0x5104F0,
    schedule_insert_va=0x615950,
    source_order_preserved_before_schedule_insertion=True,
    rng_before_fixed_schedule_insertion=False,
    original_screen_sort_proven=False,
    screen_class_name=None,
)


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
class LeagueTableSortFieldContract:
    semantic_key: str
    direction: str
    source_encoding: str | None


@dataclass(frozen=True)
class LeagueTablePresentationContract:
    backend_class_name: str
    backend_vtable_va: int
    comparator_va: int
    screen_class_name: str | None
    strict_source_name_required_on_numeric_tie: bool
    equal_full_key_relative_order_proven: bool
    fields: tuple[LeagueTableSortFieldContract, ...]


LEAGUE_TABLE_PRESENTATION_CONTRACT = LeagueTablePresentationContract(
    backend_class_name="League",
    backend_vtable_va=0x7C9AC0,
    comparator_va=0x4F45E0,
    screen_class_name=None,
    strict_source_name_required_on_numeric_tie=True,
    equal_full_key_relative_order_proven=False,
    fields=(
        LeagueTableSortFieldContract("points", "descending", None),
        LeagueTableSortFieldContract("played", "ascending", None),
        LeagueTableSortFieldContract("goal_difference", "descending", None),
        LeagueTableSortFieldContract("goals_for", "descending", None),
        LeagueTableSortFieldContract("goals_against", "ascending", None),
        LeagueTableSortFieldContract(
            "club_short_name_bytes",
            "ascending",
            "CP1252",
        ),
    ),
)


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
class TeamOrderPriorityPresentationContract:
    category: int
    semantic_key: str
    corroborating_original_strings: tuple[str, ...]


@dataclass(frozen=True)
class TacticsPresentationContract:
    formation_panel_class_name: str
    formation_vtable_va: int
    formation_user_region_offset: int
    formation_user_region_size: int
    formation_magic: int
    formation_records_offset: int
    formation_record_count: int
    formation_record_size: int
    team_orders_panel_class_name: str
    team_orders_vtable_anchor_va: int
    team_orders_type_descriptor_anchor_va: int
    team_orders_source_path: str
    priority_categories: tuple[TeamOrderPriorityPresentationContract, ...]


# Firsthand executable/RTTI and MatchCalculator evidence only. The Team Orders
# addresses are retained as the RTTI neighborhood anchors recorded by the
# existing analysis, not as a substitute for a fresh PE canary while private
# byte execution is unavailable.
TACTICS_PRESENTATION_CONTRACT = TacticsPresentationContract(
    formation_panel_class_name="PFormation2k",
    formation_vtable_va=0x7C1AB4,
    formation_user_region_offset=0x70C,
    formation_user_region_size=0x9CC,
    formation_magic=0x074A3216,
    formation_records_offset=0x714,
    formation_record_count=5,
    formation_record_size=0x1F4,
    team_orders_panel_class_name="PTeamOrders2K",
    team_orders_vtable_anchor_va=0x7C6FE0,
    team_orders_type_descriptor_anchor_va=0x81DE68,
    team_orders_source_path=r"Applications\FootballManager\SquadPan.cpp",
    priority_categories=(
        TeamOrderPriorityPresentationContract(
            0,
            "captaincy_order",
            ("Captains", "Click for captaincy order", "CAPTAIN"),
        ),
        TeamOrderPriorityPresentationContract(
            1,
            "penalty_taker_order",
            ("Penalty Takers", "Click for penalties order", "PENALTIES"),
        ),
        TeamOrderPriorityPresentationContract(
            2,
            "corner_kick_order",
            ("Corner Kicks (Left)", "Corner Kicks (Right)"),
        ),
        TeamOrderPriorityPresentationContract(
            3,
            "free_kick_order",
            ("Free Kicks (Left)", "Free Kicks (Right)"),
        ),
    ),
)


@dataclass(frozen=True)
class PlayerProfilePresentationContract:
    table_class_name: str
    table_vtable_anchor_va: int
    table_global_va: int
    record_class_name: str
    record_vtable_anchor_va: int
    runtime_record_size: int
    record_accessor_anchor_va: int
    binary_reader_anchor_va: int
    compact_importer_va: int
    current_skill_offset: int
    current_skill_count: int
    development_target_offset: int
    development_target_count: int
    development_targets_proven_visible_on_profile: bool
    screen_class_name: str | None


PLAYER_PROFILE_PRESENTATION_CONTRACT = PlayerProfilePresentationContract(
    table_class_name="DBTPlayers",
    table_vtable_anchor_va=0x7BDA78,
    table_global_va=0x875638,
    record_class_name="DBRPlayer",
    record_vtable_anchor_va=0x7BDEDC,
    runtime_record_size=0x250,
    record_accessor_anchor_va=0x416F90,
    binary_reader_anchor_va=0x416210,
    compact_importer_va=0x418B90,
    current_skill_offset=0x1E,
    current_skill_count=17,
    development_target_offset=0x2F,
    development_target_count=17,
    development_targets_proven_visible_on_profile=False,
    screen_class_name=None,
)


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
class TicketSectionStatePresentationContract:
    value: int
    semantic_key: str


@dataclass(frozen=True)
class TicketsPresentationContract:
    panel_class_name: str
    update_routine_va: int
    user_ticket_state_offset: int
    ticket_state_size: int
    season_ticket_quantity_offset: int
    season_ticket_price_offset: int
    terrace_price_offset: int
    seating_price_offset: int
    section_states_offset: int
    section_state_count: int
    terrace_recommendation_helper_va: int
    seating_recommendation_helper_va: int
    terrace_compare_va: int
    seating_compare_va: int
    terrace_reference_factor: float
    stadium_terrace_capacity_offset: int
    stadium_seating_capacity_offset: int
    section_states: tuple[TicketSectionStatePresentationContract, ...]


@dataclass(frozen=True)
class TicketStateView:
    club_id: int
    season_ticket_quantity: int
    season_ticket_price: int
    terrace_price: int
    seating_price: int
    section_states: tuple[int, ...]


# Firsthand original ticket-screen / stadium-consumer evidence only. No visible
# control binding, label placement, screen geometry, artwork, or navigation is
# inferred from these state offsets and instruction addresses.
TICKETS_PRESENTATION_CONTRACT = TicketsPresentationContract(
    panel_class_name="PTickets",
    update_routine_va=0x45FF10,
    user_ticket_state_offset=0x694,
    ticket_state_size=0x7C,
    season_ticket_quantity_offset=0x00,
    season_ticket_price_offset=0x04,
    terrace_price_offset=0x08,
    seating_price_offset=0x0C,
    section_states_offset=0x14,
    section_state_count=26,
    terrace_recommendation_helper_va=0x461340,
    seating_recommendation_helper_va=0x4615B0,
    terrace_compare_va=0x4605AD,
    seating_compare_va=0x460753,
    terrace_reference_factor=0.75,
    stadium_terrace_capacity_offset=0x1C,
    stadium_seating_capacity_offset=0x28,
    section_states=(
        TicketSectionStatePresentationContract(-1, "unavailable"),
        TicketSectionStatePresentationContract(0, "home"),
        TicketSectionStatePresentationContract(1, "visiting"),
        TicketSectionStatePresentationContract(2, "season_ticket_reserved"),
    ),
)


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
class FinanceOverviewPresentationContract:
    panel_class_name: str
    balance_accounting_driven: bool
    transfer_account_category_id: int
    transfer_credit_aggregate_va: int
    transfer_debit_aggregate_va: int
    transfer_net_helper_va: int
    transfer_query_call_sites: tuple[int, int, int]
    transfer_panel_state_anchor_offset: int
    dormant_budget_event_live_consumer_proven: bool


@dataclass(frozen=True)
class TransferEventPresentationContract:
    semantic_key: str
    class_name: str
    vtable_va: int | None
    player_response_code: int | None


@dataclass(frozen=True)
class TransferDealStatePresentationContract:
    ordinary_state: int
    swap_state: int
    semantic_key: str


@dataclass(frozen=True)
class TransferPresentationContract:
    panel_class_name: str
    events: tuple[TransferEventPresentationContract, ...]
    deal_states: tuple[TransferDealStatePresentationContract, ...]


FINANCE_OVERVIEW_PRESENTATION_CONTRACT = FinanceOverviewPresentationContract(
    panel_class_name="PFinanceOverview",
    balance_accounting_driven=True,
    transfer_account_category_id=1000,
    transfer_credit_aggregate_va=0x5DC890,
    transfer_debit_aggregate_va=0x5DD650,
    transfer_net_helper_va=0x43F1E0,
    transfer_query_call_sites=(0x43E08B, 0x43E0DB, 0x43E115),
    # Existing executable notes say the resulting category-1000 aggregate is
    # stored "around +0xAC0"; keep this explicitly as an anchor, not an exact
    # field claim.
    transfer_panel_state_anchor_offset=0xAC0,
    dormant_budget_event_live_consumer_proven=False,
)


TRANSFER_PRESENTATION_CONTRACT = TransferPresentationContract(
    panel_class_name="PTransfer2K",
    events=(
        TransferEventPresentationContract(
            "end_negotiations", "EAMTPUserEndNegotiationssub", 0x7C8F50, None
        ),
        TransferEventPresentationContract(
            "confirm_conclude_transfer",
            "EAMConfirmConcludeTransferDealsub",
            0x7C9008,
            None,
        ),
        TransferEventPresentationContract(
            "transfer_deal_concluded",
            "EAMTransferDealConcludedsub",
            0x7C8FAC,
            None,
        ),
        TransferEventPresentationContract(
            "player_counter_offer",
            "EAMTransferUserPlayerCounterOfferMsub",
            None,
            1,
        ),
        TransferEventPresentationContract(
            "player_accepts_terms",
            "EAMTransferPlayerAcceptsMsub",
            0x7C8EFC,
            2,
        ),
        TransferEventPresentationContract(
            "player_rejects_terms",
            "EAMTPUserPlayerRejectsMsub",
            0x7C8AB8,
            3,
        ),
        TransferEventPresentationContract(
            "deadline_passed",
            "EAMEndNegotiationsTransferDeadLinePassed",
            0x7CE3CC,
            None,
        ),
        TransferEventPresentationContract(
            "offer_not_enough",
            "EAMTPUserEndNegotiationsOfferNotEnoughM",
            0x7D5C38,
            None,
        ),
    ),
    deal_states=(
        TransferDealStatePresentationContract(0, 3, "pending_or_unresolved"),
        TransferDealStatePresentationContract(1, 4, "cleared_for_execution"),
        TransferDealStatePresentationContract(2, 5, "player_rejected_contract_terms"),
    ),
)


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
class MessageFamilyPresentationContract:
    semantic_key: str
    message_id: int | None
    original_key: str
    event_class: str
    accepted_action_class: str | None
    refused_action_class: str | None


@dataclass(frozen=True)
class MessagesPresentationContract:
    queue_container_family: str
    global_interleave_proven: bool
    families: tuple[MessageFamilyPresentationContract, ...]


MESSAGES_PRESENTATION_CONTRACT = MessagesPresentationContract(
    queue_container_family="MPMEAMail",
    global_interleave_proven=False,
    families=(
        MessageFamilyPresentationContract(
            semantic_key="ordinary_contract_renewal_suggestion",
            message_id=0x0E,
            original_key="AssManSuggestPlayerContractRenewalM",
            event_class="EAMAssManSuggestPlayerContractRenewalMsub",
            accepted_action_class="EAMAmendContractsub",
            refused_action_class=None,
        ),
        MessageFamilyPresentationContract(
            semantic_key="bosman_contract_renewal_suggestion",
            message_id=0x1B7,
            original_key="AssManSuggestBosmanPlayerContractRenewalM",
            event_class="EAMAssManSuggestBosmanPlayerContractRenewalMsub",
            accepted_action_class="EAMAmendContractsub",
            refused_action_class=None,
        ),
        MessageFamilyPresentationContract(
            semantic_key="player_transfer_list_request",
            message_id=None,
            original_key="PlayerAskTransferList",
            event_class="EAMPlayerAskTransferListsub",
            accepted_action_class="EAMAcceptTransferRequestsub",
            refused_action_class="EAMRefuseTransferRequestsub",
        ),
    ),
)


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
class TrainingMethodPresentationContract:
    method_id: int
    semantic_key: str
    profile_vector_index: int
    weekly_rng_draw_count: int


@dataclass(frozen=True)
class TrainingPresentationContract:
    source_module_path: str
    screen_class_name: str | None
    record_count: int
    record_size: int
    player_id_offset: int
    embedded_training_offset: int
    method_id_offset: int
    countdown_offset: int
    active_count_offset: int
    skill_counter_offset: int
    skill_counter_count: int
    skill_state_offset: int
    skill_state_count: int
    method_result_offset: int
    method_result_count: int
    fresh_method_id: int
    fresh_countdown: int
    fresh_active_count: int
    profile_selector_va: int
    profile_builder_va: int
    coach_dispatcher_va: int
    weekly_user_dispatch_va: int
    record_walker_va: int
    eligible_record_va: int
    weekly_update_va: int
    daily_maintenance_va: int
    methods: tuple[TrainingMethodPresentationContract, ...]


# Firsthand Training.cpp / canonical-executable evidence only. No Training
# screen RTTI class has been independently pinned in the persisted research, so
# screen_class_name remains None rather than being inferred.
TRAINING_PRESENTATION_CONTRACT = TrainingPresentationContract(
    source_module_path=r"D:\Projects\FM2001\Applications\FootballManager\Training.cpp",
    screen_class_name=None,
    record_count=40,
    record_size=0xC8,
    player_id_offset=0x08,
    embedded_training_offset=0x24,
    method_id_offset=0x00,
    countdown_offset=0x04,
    active_count_offset=0x08,
    skill_counter_offset=0x0C,
    skill_counter_count=17,
    skill_state_offset=0x20,
    skill_state_count=17,
    method_result_offset=0x64,
    method_result_count=7,
    fresh_method_id=5,
    fresh_countdown=8,
    fresh_active_count=0,
    profile_selector_va=0x4EA9A0,
    profile_builder_va=0x4EAA00,
    coach_dispatcher_va=0x42C240,
    weekly_user_dispatch_va=0x42AE40,
    record_walker_va=0x61CBA0,
    eligible_record_va=0x61C520,
    weekly_update_va=0x4EACE0,
    daily_maintenance_va=0x61CA60,
    methods=(
        TrainingMethodPresentationContract(0, "rest_recovery", 4, 0),
        TrainingMethodPresentationContract(1, "attacking", 0, 4),
        TrainingMethodPresentationContract(2, "midfield", 2, 4),
        TrainingMethodPresentationContract(3, "defensive", 1, 4),
        TrainingMethodPresentationContract(4, "goalkeeper", 3, 4),
        TrainingMethodPresentationContract(5, "fitness", 5, 6),
        TrainingMethodPresentationContract(6, "technique", 6, 4),
    ),
)


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

    @staticmethod
    def squad_presentation_contract() -> SquadPresentationContract:
        """Return proven ordered-roster/selection backend metadata only."""
        return SQUAD_PRESENTATION_CONTRACT

    def squad_rows(self) -> tuple[SquadRowView, ...]:
        self._human_club_id()
        squad = getattr(self.controller, "squad", None)
        if not callable(squad):
            raise ManagementPresentationError("Controlled-club roster is unavailable")
        rows = []
        for source_index, player in enumerate(tuple(squad())):
            player_id = getattr(player, "index", None)
            positions = getattr(player, "positions", None)
            history_average = getattr(player, "match_performance_average", None)
            current_role_rating = getattr(player, "current_role_rating", None)
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
            if not callable(history_average):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered six-match performance average"
                )
            if not callable(current_role_rating):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered current-role rating"
                )
            try:
                recent_form_average = float(history_average())
                assigned_role_rating = current_role_rating()
            except (TypeError, ValueError) as exc:
                raise ManagementPresentationError(
                    f"Player {player_id} has invalid recovered Squad row values"
                ) from exc
            if type(assigned_role_rating) is not int:
                raise ManagementPresentationError(
                    f"Player {player_id} current-role rating must be an integer"
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
                recent_form_average=recent_form_average,
                current_role_rating=assigned_role_rating,
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

    @staticmethod
    def tactics_presentation_contract() -> TacticsPresentationContract:
        """Return source-proven formation/team-orders identity and semantics.

        Original control IDs, geometry, graphics, click behavior and navigation
        remain intentionally absent until independently recovered.
        """
        return TACTICS_PRESENTATION_CONTRACT

    @staticmethod
    def player_profile_presentation_contract() -> PlayerProfilePresentationContract:
        """Return DBTPlayers/DBRPlayer identity without inventing profile UI."""
        return PLAYER_PROFILE_PRESENTATION_CONTRACT

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

    @staticmethod
    def tickets_presentation_contract() -> TicketsPresentationContract:
        """Return the source-proven PTickets state/instruction contract."""
        return TICKETS_PRESENTATION_CONTRACT

    def ticket_state_view(self) -> TicketStateView:
        """Expose the controlled club's recovered ticket state without UI guesses."""
        club_id = self._human_club_id()
        states = getattr(self.state, "ticket_states", None)
        if not hasattr(states, "get"):
            raise ManagementPresentationError(
                "Recovered ticket runtime state is unavailable"
            )
        ticket = states.get(club_id)
        if ticket is None:
            raise ManagementPresentationError(
                f"Controlled club {club_id} has no materialized ticket state"
            )

        names = (
            "season_ticket_quantity",
            "season_ticket_price",
            "terrace_price",
            "seating_price",
        )
        values = {}
        for name in names:
            value = getattr(ticket, name, None)
            if type(value) is not int:
                raise ManagementPresentationError(
                    f"Recovered ticket field {name} is unavailable"
                )
            values[name] = value

        section_states = getattr(ticket, "section_states", None)
        if (
            not isinstance(section_states, (list, tuple))
            or len(section_states) != TICKETS_PRESENTATION_CONTRACT.section_state_count
            or any(type(value) is not int for value in section_states)
        ):
            raise ManagementPresentationError(
                "Recovered ticket section-state vector is unavailable"
            )
        allowed = {
            item.value for item in TICKETS_PRESENTATION_CONTRACT.section_states
        }
        if any(value not in allowed for value in section_states):
            raise ManagementPresentationError(
                "Recovered ticket section state has an unmapped native value"
            )

        return TicketStateView(
            club_id=club_id,
            season_ticket_quantity=values["season_ticket_quantity"],
            season_ticket_price=values["season_ticket_price"],
            terrace_price=values["terrace_price"],
            seating_price=values["seating_price"],
            section_states=tuple(section_states),
        )

    @staticmethod
    def finance_overview_presentation_contract() -> FinanceOverviewPresentationContract:
        """Return only already-proven PFinanceOverview presentation-facing facts."""
        return FINANCE_OVERVIEW_PRESENTATION_CONTRACT

    @staticmethod
    def transfer_presentation_contract() -> TransferPresentationContract:
        """Return recovered PTransfer2K event/deal semantics without UI guesses."""
        return TRANSFER_PRESENTATION_CONTRACT

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

    @staticmethod
    def messages_presentation_contract() -> MessagesPresentationContract:
        """Return only source-proven manager-mail family identities/actions."""
        return MESSAGES_PRESENTATION_CONTRACT

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

    @staticmethod
    def training_presentation_contract() -> TrainingPresentationContract:
        """Return source-proven Training.cpp state/method metadata only."""
        return TRAINING_PRESENTATION_CONTRACT

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

    @staticmethod
    def fixtures_presentation_contract() -> FixturesPresentationContract:
        """Return source-proven fixed-fixture identity/construction metadata."""
        return FIXTURES_PRESENTATION_CONTRACT

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

    @staticmethod
    def league_table_presentation_contract() -> LeagueTablePresentationContract:
        """Return source-proven League ordering metadata without UI guesses."""
        return LEAGUE_TABLE_PRESENTATION_CONTRACT

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
