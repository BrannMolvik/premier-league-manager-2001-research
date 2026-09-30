from dataclasses import dataclass, field
from datetime import date
from types import SimpleNamespace
import unittest

from gate13_management_source_data import (
    FINANCE_OVERVIEW_PRESENTATION_CONTRACT,
    FIXTURES_PRESENTATION_CONTRACT,
    LEAGUE_TABLE_PRESENTATION_CONTRACT,
    MESSAGES_PRESENTATION_CONTRACT,
    PLAYER_PROFILE_PRESENTATION_CONTRACT,
    ManagementPresentationError,
    ManagementSourceDataBridge,
    SCOUTING_PRESENTATION_CONTRACT,
    TACTICS_PRESENTATION_CONTRACT,
    TICKETS_PRESENTATION_CONTRACT,
    TRAINING_PRESENTATION_CONTRACT,
    TRANSFER_PRESENTATION_CONTRACT,
)
from finance_state import BalanceRuntimeState, FinancePosting, FinancialObjectiveState
from contract_maintenance import ContractRenewalSuggestion, ContractRenewalSuggestionKind
from match_postmatch import PlayerTransferRequest
from scouting import ScoutingReseedState
from transfer_state import (
    ContractTerms,
    DealInProgress,
    ScheduledTransfer,
    TransferProposal,
    TransferRuntimeState,
)


@dataclass
class FakeClub:
    name: str
    short_name: str


@dataclass
class FakePlayer:
    index: int
    first_name: str
    surname: str
    shirt_number: int
    positions: tuple[int, int, int]
    condition: int
    form_state: int
    morale: int
    club_id: int = 10
    nationality_id: int = 1
    date_of_birth: date | None = date(1980, 1, 2)
    height_cm: int = 180
    weight_kg: int = 75
    current_raw: tuple[int, ...] = (
        10, 20, 30, 40, 50, 60, 70, 80, 90,
        100, 110, 120, 130, 140, 150, 160, 170,
    )
    weekly_wage: int = 5000
    contract_expiry_date: date | None = date(2002, 6, 30)
    loan_club_id: int | None = None
    injured: bool = False
    suspended: bool = False
    out_of_contract: bool = False
    transfer_listed: bool = False
    loan_listed: bool = False
    wanted: bool = False
    current_position: int = 0
    training_modifiers: list[int] = field(
        default_factory=lambda: [0] * 17
    )
    training_method_id: int = 2
    training_countdown: int = 4
    training_active_count: int = 3
    training_skill_states: list[int] = field(
        default_factory=lambda: [1] * 17
    )
    training_method_results: list[int] = field(
        default_factory=lambda: [0, 1, 2, 3, 4, 5, 6]
    )

    @property
    def base_match_unavailable(self):
        return bool(self.injured or self.suspended)

    def age(self, on_date):
        if self.date_of_birth is None:
            return None
        return on_date.year - self.date_of_birth.year - (
            (on_date.month, on_date.day)
            < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def match_performance_average(self):
        return float(self.index % 10) + 0.5


@dataclass
class FakeFixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


@dataclass
class FakeTableRow:
    club_id: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against


class FakeLeague:
    def __init__(self):
        # Deliberately not numeric or chronological order: the bridge must
        # preserve recovered source insertion order, not invent a UI sort.
        self.fixture_source_order = (17, 3)
        self.fixtures = {
            3: FakeFixture(3, 1, 11, 10),
            17: FakeFixture(17, 0, 10, 11),
        }
        self.results = {
            17: SimpleNamespace(home_goals=2, away_goals=1),
        }
        self._dates = {
            0: date(2000, 8, 19),
            1: date(2000, 8, 26),
        }

    def round_date(self, round_index):
        return self._dates.get(round_index)


class FakeState:
    def __init__(self):
        self.clubs = {
            10: FakeClub("Alpha FC", "Alpha"),
            11: FakeClub("Beta City", "Beta"),
        }
        self.calendar = SimpleNamespace(current_date=date(2000, 8, 20))
        self.premier_league = FakeLeague()
        self.team_tactics = {
            10: SimpleNamespace(
                play_style=2,
                without_ball_style=3,
                with_ball_style=1,
                aggression=7,
            )
        }
        # Deliberately Beta first: represents the backend's already recovered
        # native-comparator order, which the bridge must not second-guess.
        self._table = (
            FakeTableRow(11, 2, 2, 0, 0, 4, 1, 6),
            FakeTableRow(10, 2, 1, 0, 1, 3, 2, 3),
        )

    def premier_league_table(self):
        return self._table


class FakeController:
    def __init__(self):
        self.state = FakeState()
        self.human = SimpleNamespace(
            club_id=10,
            formation_id=4,
            starter_ids=(202, 101),
            substitute_ids=(303,),
            team_orders=SimpleNamespace(
                captain=(202, 101),
                penalty=(101,),
                corner=(202,),
                free_kick=(101, 202),
            ),
        )
        self.squad_calls = 0
        self.pending_fixture_id = 3
        self._squad = (
            FakePlayer(
                202, "Second", "Source", 9, (4, 0, 0),
                91, 3, 88, transfer_listed=True,
            ),
            FakePlayer(
                101, "First", "Source", 1, (0, 1, 0),
                77, 2, 92, injured=True, suspended=True,
                out_of_contract=True, loan_listed=True, wanted=True,
            ),
        )
        self.state.players = {player.index: player for player in self._squad}
        target = FakePlayer(
            404, "Target", "Player", 18, (3, 4, 0),
            84, 2, 76, club_id=11, nationality_id=2,
        )
        self.state.players[target.index] = target
        scout_other = FakePlayer(
            405, "Scout", "Result", 7, (2, 3, 0),
            86, 4, 81, club_id=11, nationality_id=3,
            transfer_listed=True,
        )
        self.state.players[scout_other.index] = scout_other
        unattached = FakePlayer(
            406, "Free", "Agent", 0, (1, 2, 0),
            80, 2, 70, club_id=-1, nationality_id=4,
            out_of_contract=True,
        )
        self.state.players[unattached.index] = unattached
        self.state.contract_renewal_suggestions = [
            ContractRenewalSuggestion(
                player_id=202,
                queued_on=date(2000, 8, 18),
                kind=ContractRenewalSuggestionKind.ORDINARY,
            ),
            ContractRenewalSuggestion(
                player_id=101,
                queued_on=date(2000, 8, 19),
                kind=ContractRenewalSuggestionKind.BOSMAN,
            ),
        ]
        self.state.player_transfer_requests = [
            PlayerTransferRequest(
                player_id=101,
                queued_on=date(2000, 8, 19),
                due_on=date(2000, 8, 20),
            ),
            PlayerTransferRequest(
                player_id=202,
                queued_on=date(2000, 8, 20),
                due_on=date(2000, 8, 21),
            ),
        ]

        objective = FinancialObjectiveState(
            base_cash=100000,
            candidate_ids=(13, 1, 5),
        )
        objective.selected_objective_id = 13
        objective.starting_funds = 60000
        objective.target_cash = 120000
        objective.selected_on = date(2000, 7, 4)
        objective.deadline = date(2003, 7, 4)
        objective.active = True
        objective.progression_gate_reached = True
        objective.progression_state = 2
        self.state.finance_balances = {
            10: BalanceRuntimeState(
                current_cash=50000.5,
                ledger=[
                    FinancePosting(1000, 42, date(2000, 8, 18)),
                    FinancePosting(-25, 1600, date(2000, 8, 19)),
                ],
                financial_objective=objective,
            )
        }

        terms = ContractTerms(
            weekly_wage=750,
            signing_on_fee=5000,
            promotion_bonus=250,
            contract_length_months=36,
            appearance_fee=50,
            relegation_transfer_request_clause=True,
            big_club_offer_clause=True,
            big_money_offer_clause=False,
            house=True,
            car=False,
        )
        proposal = TransferProposal(
            target_player_id=404,
            buying_club_id=10,
            cash_fee=250000,
            exchange_player_ids=(202, -1, -1),
            negotiation_state_14=7,
            negotiation_state_15=8,
            contract_terms=terms,
            previous_wage_offer=700,
            previous_signing_on_fee_offer=4000,
            previous_total_value=240000,
        )
        self.state.transfers = TransferRuntimeState(
            proposals={(404, 10): proposal},
            deals={
                404: DealInProgress(
                    player_id=404,
                    buying_club_id=10,
                    selling_club_id=11,
                    state=4,
                    contract_terms=terms,
                    created_date=date(2000, 8, 20),
                )
            },
            scheduled_transfers=[
                ScheduledTransfer(
                    proposal=proposal,
                    due_date=date(2000, 8, 23),
                    mode=0,
                )
            ],
        )

    def squad(self):
        self.squad_calls += 1
        return self._squad

    def search_scouting_players_mapped(self, panel_state, **kwargs):
        self.last_scout_panel_state = panel_state
        self.last_scout_kwargs = kwargs
        return (
            self.state.players[406],
            self.state.players[405],
            self.state.players[404],
        )


class ManagementSourceDataBridgeTests(unittest.TestCase):
    def test_snapshot_preserves_backend_source_order_and_exact_table_order(self):
        controller = FakeController()
        bridge = ManagementSourceDataBridge(controller)

        snapshot = bridge.snapshot()

        self.assertEqual(
            (snapshot.club.club_id, snapshot.club.name,
             snapshot.club.short_name, snapshot.club.current_date),
            (10, "Alpha FC", "Alpha", date(2000, 8, 20)),
        )
        self.assertEqual(
            [row.player_id for row in snapshot.squad],
            [202, 101],
        )
        self.assertEqual(
            [row.source_roster_index for row in snapshot.squad],
            [0, 1],
        )
        self.assertEqual(
            [row.fixture_id for row in snapshot.fixtures_in_source_order],
            [17, 3],
        )
        self.assertEqual(
            [row.source_fixture_index for row in snapshot.fixtures_in_source_order],
            [0, 1],
        )
        self.assertEqual(
            [row.club_id for row in snapshot.league_table],
            [11, 10],
        )
        self.assertEqual(
            [row.position for row in snapshot.league_table],
            [1, 2],
        )
        self.assertEqual(
            (
                snapshot.tactics.formation_id,
                snapshot.tactics.starter_ids,
                snapshot.tactics.substitute_ids,
                snapshot.tactics.play_style,
                snapshot.tactics.without_ball_style,
                snapshot.tactics.with_ball_style,
                snapshot.tactics.aggression,
            ),
            (4, (202, 101), (303,), 2, 3, 1, 7),
        )
        self.assertEqual(snapshot.tactics.captain_priority, (202, 101))
        self.assertEqual(snapshot.tactics.penalty_priority, (101,))
        self.assertEqual(snapshot.tactics.corner_priority, (202,))
        self.assertEqual(snapshot.tactics.free_kick_priority, (101, 202))
        self.assertEqual(controller.squad_calls, 1)

    def test_fixtures_presentation_contract_preserves_fixed_real_fixture_path(self):
        contract = ManagementSourceDataBridge.fixtures_presentation_contract()
        self.assertIs(contract, FIXTURES_PRESENTATION_CONTRACT)
        self.assertEqual(
            (contract.table_class_name, contract.table_vtable_va, contract.table_global_va),
            ("DBTRealFixtures", 0x7C9884, 0x876C18),
        )
        self.assertEqual(
            (contract.record_class_name, contract.record_vtable_va, contract.record_size),
            ("DBRRealFixture", 0x7C9898, 0x14),
        )
        self.assertEqual(
            (contract.static_table_offset, contract.shipped_fixture_count,
             contract.shipped_round_count, contract.fixtures_per_round),
            (0x10057, 380, 38, 10),
        )
        self.assertEqual(
            (contract.round_table_class_name, contract.round_table_vtable_va,
             contract.round_table_global_va, contract.round_record_class_name,
             contract.round_record_vtable_va),
            ("DBTRounds", 0x7C99C4, 0x876BD0, "DBRRound", 0x7C99D8),
        )
        self.assertEqual(contract.round_attach_va, 0x4F72D0)
        self.assertEqual((contract.fixture_attach_start_va, contract.fixture_attach_end_va),
                         (0x4F76A4, 0x4F770D))
        self.assertEqual(contract.fixed_builder_va, 0x6173D0)
        self.assertEqual(contract.league_add_round_va, 0x4F4500)
        self.assertEqual(contract.league_match_constructor_va, 0x5104F0)
        self.assertEqual(contract.schedule_insert_va, 0x615950)
        self.assertTrue(contract.source_order_preserved_before_schedule_insertion)
        self.assertFalse(contract.rng_before_fixed_schedule_insertion)
        self.assertFalse(contract.original_screen_sort_proven)
        self.assertIsNone(contract.screen_class_name)
        for unsupported in ("control_id", "row_rectangle", "art_path", "navigation_id"):
            self.assertFalse(hasattr(contract, unsupported))

    def test_fixture_projection_uses_recovered_dates_names_and_result_only(self):
        bridge = ManagementSourceDataBridge(FakeController())

        first, second = bridge.fixture_rows()

        self.assertEqual(
            (
                first.fixture_id, first.round_index, first.scheduled_date,
                first.home_club_name, first.away_club_name,
                first.played, first.home_goals, first.away_goals,
            ),
            (17, 0, date(2000, 8, 19),
             "Alpha FC", "Beta City", True, 2, 1),
        )
        self.assertEqual(
            (
                second.fixture_id, second.round_index, second.scheduled_date,
                second.home_club_name, second.away_club_name,
                second.played, second.home_goals, second.away_goals,
            ),
            (3, 1, date(2000, 8, 26),
             "Beta City", "Alpha FC", False, None, None),
        )

    def test_pending_fixture_uses_same_source_fixture_projection(self):
        controller = FakeController()
        row = ManagementSourceDataBridge(controller).pending_fixture()

        self.assertIsNotNone(row)
        self.assertEqual(row.fixture_id, 3)
        self.assertEqual(row.scheduled_date, date(2000, 8, 26))
        self.assertEqual(row.home_club_name, "Beta City")
        self.assertEqual(row.away_club_name, "Alpha FC")

        controller.pending_fixture_id = None
        self.assertIsNone(ManagementSourceDataBridge(controller).pending_fixture())

        controller.pending_fixture_id = 999
        with self.assertRaisesRegex(ManagementPresentationError, "absent or ambiguous"):
            ManagementSourceDataBridge(controller).pending_fixture()

    def test_squad_projection_retains_recovered_neutral_runtime_fields(self):
        bridge = ManagementSourceDataBridge(FakeController())

        second, first = bridge.squad_rows()

        self.assertEqual(
            (
                second.full_name, second.shirt_number, second.positions,
                second.current_position, second.match_unavailable,
                second.condition, second.form_state, second.morale,
            ),
            ("Second Source", 9, (4, 0, 0), 0, False, 91, 3, 88),
        )
        self.assertTrue(second.transfer_listed)
        self.assertFalse(second.injured)
        self.assertEqual(
            (first.full_name, first.condition, first.form_state, first.morale),
            ("First Source", 77, 2, 92),
        )
        self.assertTrue(first.injured)
        self.assertTrue(first.suspended)
        self.assertTrue(first.out_of_contract)
        self.assertTrue(first.loan_listed)
        self.assertTrue(first.wanted)

    def test_league_table_presentation_contract_preserves_native_comparator(self):
        contract = ManagementSourceDataBridge.league_table_presentation_contract()

        self.assertIs(contract, LEAGUE_TABLE_PRESENTATION_CONTRACT)
        self.assertEqual(contract.backend_class_name, "League")
        self.assertEqual(contract.backend_vtable_va, 0x7C9AC0)
        self.assertEqual(contract.comparator_va, 0x4F45E0)
        self.assertIsNone(contract.screen_class_name)
        self.assertTrue(contract.strict_source_name_required_on_numeric_tie)
        self.assertFalse(contract.equal_full_key_relative_order_proven)
        self.assertEqual(
            [
                (item.semantic_key, item.direction, item.source_encoding)
                for item in contract.fields
            ],
            [
                ("points", "descending", None),
                ("played", "ascending", None),
                ("goal_difference", "descending", None),
                ("goals_for", "descending", None),
                ("goals_against", "ascending", None),
                ("club_short_name_bytes", "ascending", "CP1252"),
            ],
        )
        for unsupported in (
            "screen_id",
            "control_id",
            "column_rectangle",
            "art_path",
            "navigation_id",
        ):
            self.assertFalse(hasattr(contract, unsupported))

    def test_table_projection_does_not_resort_native_comparator_output(self):
        controller = FakeController()
        controller.state._table = (
            FakeTableRow(10, 3, 1, 2, 0, 3, 1, 5),
            FakeTableRow(11, 3, 1, 2, 0, 3, 1, 5),
        )
        rows = ManagementSourceDataBridge(controller).league_table_rows()

        # Even a numerically identical synthetic pair remains in the backend's
        # returned order. The bridge never substitutes ID/name sorting.
        self.assertEqual([row.club_id for row in rows], [10, 11])
        self.assertEqual([row.short_name for row in rows], ["Alpha", "Beta"])

    def test_tactics_projection_preserves_exact_backend_numeric_state(self):
        controller = FakeController()
        view = ManagementSourceDataBridge(controller).tactics_selection()
        self.assertEqual(view.formation_id, 4)
        self.assertEqual(view.starter_ids, (202, 101))
        self.assertEqual(view.substitute_ids, (303,))
        self.assertEqual(
            (
                view.play_style,
                view.without_ball_style,
                view.with_ball_style,
                view.aggression,
            ),
            (2, 3, 1, 7),
        )
        self.assertEqual(view.captain_priority, (202, 101))
        self.assertEqual(view.penalty_priority, (101,))
        self.assertEqual(view.corner_priority, (202,))
        self.assertEqual(view.free_kick_priority, (101, 202))

    def test_missing_tactics_or_team_orders_fail_closed_without_defaults(self):
        controller = FakeController()
        del controller.state.team_tactics[10]
        with self.assertRaisesRegex(ManagementPresentationError, "tactical"):
            ManagementSourceDataBridge(controller).tactics_selection()

        controller = FakeController()
        controller.human.team_orders = SimpleNamespace(
            captain=(202,), penalty=(101,), corner=(202,),
        )
        with self.assertRaisesRegex(ManagementPresentationError, "Team Orders"):
            ManagementSourceDataBridge(controller).tactics_selection()

        controller = FakeController()
        controller.human.starter_ids = [202, 101]
        with self.assertRaisesRegex(ManagementPresentationError, "lineup"):
            ManagementSourceDataBridge(controller).tactics_selection()

    def test_tactics_presentation_contract_preserves_native_panel_and_order_evidence(self):
        contract = ManagementSourceDataBridge.tactics_presentation_contract()

        self.assertIs(contract, TACTICS_PRESENTATION_CONTRACT)
        self.assertEqual(contract.formation_panel_class_name, "PFormation2k")
        self.assertEqual(contract.formation_vtable_va, 0x7C1AB4)
        self.assertEqual(contract.formation_user_region_offset, 0x70C)
        self.assertEqual(contract.formation_user_region_size, 0x9CC)
        self.assertEqual(contract.formation_magic, 0x074A3216)
        self.assertEqual(contract.formation_records_offset, 0x714)
        self.assertEqual(contract.formation_record_count, 5)
        self.assertEqual(contract.formation_record_size, 0x1F4)
        self.assertEqual(contract.team_orders_panel_class_name, "PTeamOrders2K")
        self.assertEqual(contract.team_orders_vtable_anchor_va, 0x7C6FE0)
        self.assertEqual(contract.team_orders_type_descriptor_anchor_va, 0x81DE68)
        self.assertEqual(
            contract.team_orders_source_path,
            r"Applications\FootballManager\SquadPan.cpp",
        )
        self.assertEqual(
            [
                (item.category, item.semantic_key)
                for item in contract.priority_categories
            ],
            [
                (0, "captaincy_order"),
                (1, "penalty_taker_order"),
                (2, "corner_kick_order"),
                (3, "free_kick_order"),
            ],
        )
        self.assertIn(
            "Click for captaincy order",
            contract.priority_categories[0].corroborating_original_strings,
        )
        self.assertIn(
            "Penalty Takers",
            contract.priority_categories[1].corroborating_original_strings,
        )
        self.assertEqual(
            contract.priority_categories[2].corroborating_original_strings,
            ("Corner Kicks (Left)", "Corner Kicks (Right)"),
        )
        self.assertEqual(
            contract.priority_categories[3].corroborating_original_strings,
            ("Free Kicks (Left)", "Free Kicks (Right)"),
        )
        for item in contract.priority_categories:
            self.assertFalse(hasattr(item, "control_id"))
            self.assertFalse(hasattr(item, "rectangle"))
            self.assertFalse(hasattr(item, "art_path"))

    def test_player_profile_presentation_contract_preserves_runtime_identity_boundaries(self):
        contract = ManagementSourceDataBridge.player_profile_presentation_contract()
        self.assertIs(contract, PLAYER_PROFILE_PRESENTATION_CONTRACT)
        self.assertEqual(contract.table_class_name, "DBTPlayers")
        self.assertEqual(contract.table_vtable_anchor_va, 0x7BDA78)
        self.assertEqual(contract.table_global_va, 0x875638)
        self.assertEqual(contract.record_class_name, "DBRPlayer")
        self.assertEqual(contract.record_vtable_anchor_va, 0x7BDEDC)
        self.assertEqual(contract.runtime_record_size, 0x250)
        self.assertEqual(contract.record_accessor_anchor_va, 0x416F90)
        self.assertEqual(contract.binary_reader_anchor_va, 0x416210)
        self.assertEqual(contract.compact_importer_va, 0x418B90)
        self.assertEqual((contract.current_skill_offset, contract.current_skill_count), (0x1E, 17))
        self.assertEqual((contract.development_target_offset, contract.development_target_count), (0x2F, 17))
        self.assertFalse(contract.development_targets_proven_visible_on_profile)
        self.assertIsNone(contract.screen_class_name)
        for unsupported in (
            "screen_id", "control_id", "skill_column_labels",
            "row_rectangle", "art_path", "navigation_id",
        ):
            self.assertFalse(hasattr(contract, unsupported))

    def test_player_profile_projects_only_recovered_runtime_source_fields(self):
        controller = FakeController()
        view = ManagementSourceDataBridge(controller).player_profile(202)

        self.assertEqual(
            (
                view.player_id, view.first_name, view.surname,
                view.club_id, view.club_name, view.nationality_id,
                view.date_of_birth, view.shirt_number,
                view.height_cm, view.weight_kg, view.positions,
            ),
            (
                202, "Second", "Source", 10, "Alpha FC", 1,
                date(1980, 1, 2), 9, 180, 75, (4, 0, 0),
            ),
        )
        self.assertEqual(
            view.current_skill_bytes,
            (
                10, 20, 30, 40, 50, 60, 70, 80, 90,
                100, 110, 120, 130, 140, 150, 160, 170,
            ),
        )
        self.assertEqual(
            (
                view.condition, view.form_state, view.morale,
                view.weekly_wage, view.contract_expiry_date,
            ),
            (91, 3, 88, 5000, date(2002, 6, 30)),
        )
        self.assertTrue(view.transfer_listed)
        self.assertFalse(view.injured)
        # Development target bytes exist in RuntimePlayer but are not
        # established as original player-profile UI and stay outside the bridge.
        self.assertFalse(hasattr(view, "target_raw"))
        self.assertFalse(hasattr(view, "target_skill_bytes"))

    def test_player_profile_invalid_or_unverified_runtime_fields_fail_closed(self):
        controller = FakeController()
        with self.assertRaisesRegex(ManagementPresentationError, "Unknown"):
            ManagementSourceDataBridge(controller).player_profile(999)
        with self.assertRaisesRegex(ManagementPresentationError, "integer"):
            ManagementSourceDataBridge(controller).player_profile(True)

        controller = FakeController()
        controller.state.players[202].current_raw = (1, 2, 3)
        with self.assertRaisesRegex(ManagementPresentationError, "17-byte"):
            ManagementSourceDataBridge(controller).player_profile(202)

        controller = FakeController()
        controller.state.players[202].contract_expiry_date = "unknown"
        with self.assertRaisesRegex(ManagementPresentationError, "contract expiry"):
            ManagementSourceDataBridge(controller).player_profile(202)

    def test_ticket_presentation_contract_preserves_ptickets_native_state_identity(self):
        contract = ManagementSourceDataBridge.tickets_presentation_contract()

        self.assertIs(contract, TICKETS_PRESENTATION_CONTRACT)
        self.assertEqual(contract.panel_class_name, "PTickets")
        self.assertEqual(contract.update_routine_va, 0x45FF10)
        self.assertEqual(contract.user_ticket_state_offset, 0x694)
        self.assertEqual(contract.ticket_state_size, 0x7C)
        self.assertEqual(contract.season_ticket_quantity_offset, 0x00)
        self.assertEqual(contract.season_ticket_price_offset, 0x04)
        self.assertEqual(contract.terrace_price_offset, 0x08)
        self.assertEqual(contract.seating_price_offset, 0x0C)
        self.assertEqual(contract.section_states_offset, 0x14)
        self.assertEqual(contract.section_state_count, 26)
        self.assertEqual(contract.terrace_recommendation_helper_va, 0x461340)
        self.assertEqual(contract.seating_recommendation_helper_va, 0x4615B0)
        self.assertEqual(contract.terrace_compare_va, 0x4605AD)
        self.assertEqual(contract.seating_compare_va, 0x460753)
        self.assertEqual(contract.terrace_reference_factor, 0.75)
        self.assertEqual(contract.stadium_terrace_capacity_offset, 0x1C)
        self.assertEqual(contract.stadium_seating_capacity_offset, 0x28)
        self.assertEqual(
            [(item.value, item.semantic_key) for item in contract.section_states],
            [
                (-1, "unavailable"),
                (0, "home"),
                (1, "visiting"),
                (2, "season_ticket_reserved"),
            ],
        )
        for unsupported in ("control_id", "rectangle", "art_path", "navigation_id"):
            self.assertFalse(hasattr(contract, unsupported))

    def test_ticket_state_view_preserves_prices_and_26_native_section_states(self):
        controller = FakeController()
        section_states = [-1, 0, 1, 2] + [0] * 22
        controller.state.ticket_states = {
            10: SimpleNamespace(
                season_ticket_quantity=321,
                season_ticket_price=44,
                terrace_price=17,
                seating_price=23,
                section_states=section_states,
            )
        }

        view = ManagementSourceDataBridge(controller).ticket_state_view()

        self.assertEqual(view.club_id, 10)
        self.assertEqual(view.season_ticket_quantity, 321)
        self.assertEqual(view.season_ticket_price, 44)
        self.assertEqual(view.terrace_price, 17)
        self.assertEqual(view.seating_price, 23)
        self.assertEqual(view.section_states, tuple(section_states))

    def test_ticket_state_view_fails_closed_for_missing_or_unmapped_state(self):
        controller = FakeController()
        with self.assertRaisesRegex(
            ManagementPresentationError, "ticket runtime state"
        ):
            ManagementSourceDataBridge(controller).ticket_state_view()

        controller.state.ticket_states = {
            10: SimpleNamespace(
                season_ticket_quantity=1,
                season_ticket_price=2,
                terrace_price=3,
                seating_price=4,
                section_states=[0] * 25 + [7],
            )
        }
        with self.assertRaisesRegex(
            ManagementPresentationError, "unmapped native value"
        ):
            ManagementSourceDataBridge(controller).ticket_state_view()

    def test_finance_overview_contract_preserves_only_proven_category_1000_path(self):
        contract = ManagementSourceDataBridge.finance_overview_presentation_contract()

        self.assertIs(contract, FINANCE_OVERVIEW_PRESENTATION_CONTRACT)
        self.assertEqual(contract.panel_class_name, "PFinanceOverview")
        self.assertTrue(contract.balance_accounting_driven)
        self.assertEqual(contract.transfer_account_category_id, 1000)
        self.assertEqual(contract.transfer_credit_aggregate_va, 0x5DC890)
        self.assertEqual(contract.transfer_debit_aggregate_va, 0x5DD650)
        self.assertEqual(contract.transfer_net_helper_va, 0x43F1E0)
        self.assertEqual(
            contract.transfer_query_call_sites,
            (0x43E08B, 0x43E0DB, 0x43E115),
        )
        self.assertEqual(contract.transfer_panel_state_anchor_offset, 0xAC0)
        self.assertFalse(contract.dormant_budget_event_live_consumer_proven)
        for unsupported in (
            "transfer_account_label",
            "control_id",
            "rectangle",
            "art_path",
            "navigation_id",
        ):
            self.assertFalse(hasattr(contract, unsupported))

    def test_transfer_contract_preserves_native_event_and_deal_state_semantics(self):
        contract = ManagementSourceDataBridge.transfer_presentation_contract()

        self.assertIs(contract, TRANSFER_PRESENTATION_CONTRACT)
        self.assertEqual(contract.panel_class_name, "PTransfer2K")
        self.assertEqual(
            [
                (item.semantic_key, item.class_name, item.vtable_va, item.player_response_code)
                for item in contract.events
            ],
            [
                ("end_negotiations", "EAMTPUserEndNegotiationssub", 0x7C8F50, None),
                (
                    "confirm_conclude_transfer",
                    "EAMConfirmConcludeTransferDealsub",
                    0x7C9008,
                    None,
                ),
                (
                    "transfer_deal_concluded",
                    "EAMTransferDealConcludedsub",
                    0x7C8FAC,
                    None,
                ),
                (
                    "player_counter_offer",
                    "EAMTransferUserPlayerCounterOfferMsub",
                    None,
                    1,
                ),
                (
                    "player_accepts_terms",
                    "EAMTransferPlayerAcceptsMsub",
                    0x7C8EFC,
                    2,
                ),
                (
                    "player_rejects_terms",
                    "EAMTPUserPlayerRejectsMsub",
                    0x7C8AB8,
                    3,
                ),
                (
                    "deadline_passed",
                    "EAMEndNegotiationsTransferDeadLinePassed",
                    0x7CE3CC,
                    None,
                ),
                (
                    "offer_not_enough",
                    "EAMTPUserEndNegotiationsOfferNotEnoughM",
                    0x7D5C38,
                    None,
                ),
            ],
        )
        self.assertEqual(
            [
                (item.ordinary_state, item.swap_state, item.semantic_key)
                for item in contract.deal_states
            ],
            [
                (0, 3, "pending_or_unresolved"),
                (1, 4, "cleared_for_execution"),
                (2, 5, "player_rejected_contract_terms"),
            ],
        )
        for unsupported in ("sort_key", "control_id", "rectangle", "art_path"):
            self.assertFalse(hasattr(contract, unsupported))

    def test_finance_view_preserves_balance_ledger_order_and_neutral_categories(self):
        controller = FakeController()
        view = ManagementSourceDataBridge(controller).finance_view()

        self.assertEqual(view.current_cash, 50000.5)
        self.assertEqual(
            [
                (posting.amount, posting.category_id, posting.posting_date)
                for posting in view.ledger_in_runtime_order
            ],
            [
                (1000, 42, date(2000, 8, 18)),
                (-25, 1600, date(2000, 8, 19)),
            ],
        )
        self.assertIsNotNone(view.objective)
        self.assertEqual(view.objective.candidate_ids, (13, 1, 5))
        self.assertEqual(view.objective.selected_objective_id, 13)
        self.assertEqual(view.objective.starting_funds, 60000)
        self.assertEqual(view.objective.target_cash, 120000)
        self.assertEqual(view.objective.selected_on, date(2000, 7, 4))
        self.assertEqual(view.objective.deadline, date(2003, 7, 4))
        self.assertTrue(view.objective.active)
        self.assertTrue(view.objective.progression_gate_reached)
        self.assertEqual(view.objective.progression_state, 2)

    def test_transfer_view_projects_recovered_proposal_deal_terms_and_schedule(self):
        controller = FakeController()
        rows = ManagementSourceDataBridge(controller).transfer_proposal_rows()

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(
            (
                row.runtime_order_index,
                row.target_player_id,
                row.target_player_name,
                row.buying_club_id,
                row.buying_club_name,
                row.selling_club_id,
                row.selling_club_name,
                row.cash_fee,
                row.exchange_player_ids,
            ),
            (
                0, 404, "Target Player", 10, "Alpha FC",
                11, "Beta City", 250000, (202, -1, -1),
            ),
        )
        self.assertEqual((row.negotiation_state_14, row.negotiation_state_15), (7, 8))
        self.assertEqual(row.previous_wage_offer, 700)
        self.assertEqual(row.previous_signing_on_fee_offer, 4000)
        self.assertEqual(row.previous_total_value, 240000)
        self.assertEqual(row.contract_terms.weekly_wage, 750)
        self.assertEqual(row.contract_terms.signing_on_fee, 5000)
        self.assertEqual(row.contract_terms.promotion_bonus, 250)
        self.assertEqual(row.contract_terms.contract_length_months, 36)
        self.assertEqual(row.contract_terms.appearance_fee, 50)
        self.assertTrue(row.contract_terms.relegation_transfer_request_clause)
        self.assertTrue(row.contract_terms.big_club_offer_clause)
        self.assertFalse(row.contract_terms.big_money_offer_clause)
        self.assertTrue(row.contract_terms.house)
        self.assertFalse(row.contract_terms.car)
        self.assertEqual((row.deal_state, row.deal_base_state), (4, 1))
        self.assertTrue(row.deal_is_swap_variant)
        self.assertEqual(row.deal_created_date, date(2000, 8, 20))
        self.assertEqual(row.scheduled_due_date, date(2000, 8, 23))
        self.assertEqual(row.scheduled_mode, 0)

    def test_finance_and_transfer_missing_or_ambiguous_state_fails_closed(self):
        controller = FakeController()
        controller.state.finance_balances = {}
        with self.assertRaisesRegex(ManagementPresentationError, "Balance"):
            ManagementSourceDataBridge(controller).finance_view()

        controller = FakeController()
        controller.state.transfers.deals.pop(404)
        with self.assertRaisesRegex(ManagementPresentationError, "DealInProgress"):
            ManagementSourceDataBridge(controller).transfer_proposal_rows()

        controller = FakeController()
        controller.state.transfers.proposals[(999, 10)] = next(
            iter(controller.state.transfers.proposals.values())
        )
        with self.assertRaisesRegex(ManagementPresentationError, "dictionary key"):
            ManagementSourceDataBridge(controller).transfer_proposal_rows()

        controller = FakeController()
        item = controller.state.transfers.scheduled_transfers[0]
        controller.state.transfers.scheduled_transfers.append(item)
        with self.assertRaisesRegex(ManagementPresentationError, "ambiguous"):
            ManagementSourceDataBridge(controller).transfer_proposal_rows()

    def test_messages_presentation_contract_preserves_only_recovered_mail_families(self):
        contract = ManagementSourceDataBridge.messages_presentation_contract()

        self.assertIs(contract, MESSAGES_PRESENTATION_CONTRACT)
        self.assertEqual(contract.queue_container_family, "MPMEAMail")
        self.assertFalse(contract.global_interleave_proven)
        self.assertEqual(
            [
                (
                    item.semantic_key,
                    item.message_id,
                    item.original_key,
                    item.event_class,
                    item.accepted_action_class,
                    item.refused_action_class,
                )
                for item in contract.families
            ],
            [
                (
                    "ordinary_contract_renewal_suggestion",
                    0x0E,
                    "AssManSuggestPlayerContractRenewalM",
                    "EAMAssManSuggestPlayerContractRenewalMsub",
                    "EAMAmendContractsub",
                    None,
                ),
                (
                    "bosman_contract_renewal_suggestion",
                    0x1B7,
                    "AssManSuggestBosmanPlayerContractRenewalM",
                    "EAMAssManSuggestBosmanPlayerContractRenewalMsub",
                    "EAMAmendContractsub",
                    None,
                ),
                (
                    "player_transfer_list_request",
                    None,
                    "PlayerAskTransferList",
                    "EAMPlayerAskTransferListsub",
                    "EAMAcceptTransferRequestsub",
                    "EAMRefuseTransferRequestsub",
                ),
            ],
        )
        for unsupported in (
            "screen_id",
            "sort_key",
            "row_rectangle",
            "art_path",
            "navigation_id",
        ):
            self.assertFalse(hasattr(contract, unsupported))

    def test_message_source_queues_preserve_separate_runtime_order_and_exact_events(self):
        controller = FakeController()
        queues = ManagementSourceDataBridge(controller).message_source_queues()

        self.assertEqual(
            [row.player_id for row in queues.contract_renewal_in_runtime_order],
            [202, 101],
        )
        ordinary, bosman = queues.contract_renewal_in_runtime_order
        self.assertEqual(
            (
                ordinary.player_name,
                ordinary.queued_on,
                ordinary.message_id,
                ordinary.original_key,
                ordinary.event_class,
                ordinary.accepted_action_class,
            ),
            (
                "Second Source",
                date(2000, 8, 18),
                0x0E,
                "AssManSuggestPlayerContractRenewalM",
                "EAMAssManSuggestPlayerContractRenewalMsub",
                "EAMAmendContractsub",
            ),
        )
        self.assertEqual(bosman.message_id, 0x1B7)
        self.assertEqual(
            bosman.original_key,
            "AssManSuggestBosmanPlayerContractRenewalM",
        )
        self.assertEqual(
            [row.player_id for row in queues.transfer_requests_in_runtime_order],
            [101, 202],
        )
        due, future = queues.transfer_requests_in_runtime_order
        self.assertTrue(due.due)
        self.assertFalse(future.due)
        self.assertEqual(due.original_key, "PlayerAskTransferList")
        self.assertEqual(due.event_class, "EAMPlayerAskTransferListsub")
        self.assertEqual(due.accepted_action_class, "EAMAcceptTransferRequestsub")
        self.assertEqual(due.refused_action_class, "EAMRefuseTransferRequestsub")
        # The two source queues are deliberately not merged or chronologically
        # resorted, because their global manager-mail interleave is unproven.
        self.assertEqual(ordinary.queue_index, 0)
        self.assertEqual(due.queue_index, 0)

    def test_training_presentation_contract_preserves_native_record_and_method_map(self):
        contract = ManagementSourceDataBridge.training_presentation_contract()

        self.assertIs(contract, TRAINING_PRESENTATION_CONTRACT)
        self.assertEqual(
            contract.source_module_path,
            r"D:\Projects\FM2001\Applications\FootballManager\Training.cpp",
        )
        self.assertIsNone(contract.screen_class_name)
        self.assertEqual((contract.record_count, contract.record_size), (40, 0xC8))
        self.assertEqual(contract.player_id_offset, 0x08)
        self.assertEqual(contract.embedded_training_offset, 0x24)
        self.assertEqual(contract.method_id_offset, 0x00)
        self.assertEqual(contract.countdown_offset, 0x04)
        self.assertEqual(contract.active_count_offset, 0x08)
        self.assertEqual(
            (contract.skill_counter_offset, contract.skill_counter_count),
            (0x0C, 17),
        )
        self.assertEqual(
            (contract.skill_state_offset, contract.skill_state_count),
            (0x20, 17),
        )
        self.assertEqual(
            (contract.method_result_offset, contract.method_result_count),
            (0x64, 7),
        )
        self.assertEqual(
            (contract.fresh_method_id, contract.fresh_countdown, contract.fresh_active_count),
            (5, 8, 0),
        )
        self.assertEqual(contract.profile_selector_va, 0x4EA9A0)
        self.assertEqual(contract.profile_builder_va, 0x4EAA00)
        self.assertEqual(contract.coach_dispatcher_va, 0x42C240)
        self.assertEqual(contract.weekly_user_dispatch_va, 0x42AE40)
        self.assertEqual(contract.record_walker_va, 0x61CBA0)
        self.assertEqual(contract.eligible_record_va, 0x61C520)
        self.assertEqual(contract.weekly_update_va, 0x4EACE0)
        self.assertEqual(contract.daily_maintenance_va, 0x61CA60)
        self.assertEqual(
            [
                (
                    item.method_id,
                    item.semantic_key,
                    item.profile_vector_index,
                    item.weekly_rng_draw_count,
                )
                for item in contract.methods
            ],
            [
                (0, "rest_recovery", 4, 0),
                (1, "attacking", 0, 4),
                (2, "midfield", 2, 4),
                (3, "defensive", 1, 4),
                (4, "goalkeeper", 3, 4),
                (5, "fitness", 5, 6),
                (6, "technique", 6, 4),
            ],
        )
        for unsupported in (
            "screen_id",
            "control_id",
            "rectangle",
            "art_path",
            "navigation_id",
        ):
            self.assertFalse(hasattr(contract, unsupported))

    def test_training_rows_preserve_roster_order_and_raw_recovered_training_state(self):
        controller = FakeController()
        controller._squad[0].training_modifiers[2] = 8
        controller._squad[0].training_skill_states[3] = 9
        rows = ManagementSourceDataBridge(controller).training_rows()

        self.assertEqual([row.player_id for row in rows], [202, 101])
        first = rows[0]
        self.assertEqual(first.source_roster_index, 0)
        self.assertEqual(first.player_name, "Second Source")
        self.assertEqual(
            (first.method_id, first.countdown, first.active_count),
            (2, 4, 3),
        )
        self.assertEqual(len(first.skill_modifiers), 17)
        self.assertEqual(first.skill_modifiers[2], 8)
        self.assertEqual(first.skill_states[3], 9)
        self.assertEqual(first.method_results, (0, 1, 2, 3, 4, 5, 6))

    def test_training_invalid_array_shape_fails_closed_instead_of_guessing(self):
        controller = FakeController()
        controller._squad[0].training_modifiers = [0] * 16
        with self.assertRaisesRegex(ManagementPresentationError, "17-byte"):
            ManagementSourceDataBridge(controller).training_rows()

        controller = FakeController()
        controller._squad[0].training_method_results = [0] * 6
        with self.assertRaisesRegex(ManagementPresentationError, "seven-method"):
            ManagementSourceDataBridge(controller).training_rows()

    def test_scouting_presentation_contract_preserves_firsthand_native_identity(self):
        contract = ManagementSourceDataBridge.scouting_presentation_contract()

        self.assertIs(contract, SCOUTING_PRESENTATION_CONTRACT)
        self.assertEqual(contract.panel_class_name, "PScouting2K")
        self.assertEqual(contract.type_descriptor_va, 0x81C9C0)
        self.assertEqual(contract.complete_object_locator_va, 0x7E3D20)
        self.assertEqual(contract.vtable_va, 0x7C2E6C)
        self.assertEqual(contract.event_handler_va, 0x4ADB50)
        self.assertEqual(contract.search_event_code, 31)
        self.assertEqual(contract.search_dispatch_va, 0x4AE0FB)
        self.assertEqual(contract.search_build_va, 0x4AE970)
        self.assertEqual(contract.reseed_va, 0x4AF7F0)
        self.assertEqual(
            contract.source_path,
            r"D:\Projects\FM2001\Applications\FootballManager\MenuPan.cpp",
        )
        self.assertEqual(
            [
                (entry.mode, entry.semantic_key, entry.direction, entry.comparator_va)
                for entry in contract.sort_modes
            ],
            [
                (0, "player_name", "ascending", 0x4AF020),
                (1, "age", "ascending", 0x4AF0B0),
                (2, "history_average", "descending", 0x4AF200),
                (3, "position_display_string", "descending", 0x4AF270),
                (4, "club_display_name", "ascending", 0x4AF0F0),
                (5, "monetary_value", "descending", 0x4AF190),
            ],
        )
        for entry in contract.sort_modes:
            self.assertFalse(hasattr(entry, "display_label"))
            self.assertFalse(hasattr(entry, "control_id"))
            self.assertFalse(hasattr(entry, "rectangle"))

    def test_scouting_search_delegates_to_mapped_backend_and_preserves_result_order(self):
        controller = FakeController()
        panel = ScoutingReseedState(
            field_64e4=3,
            field_64e0=1,
            age_low_64d8=18,
            age_high_64dc=30,
        )
        valuation = lambda player: float(player.index * 1000)
        rows = ManagementSourceDataBridge(controller).scouting_search_rows(
            panel,
            page_mode=2,
            valuation_resolver=valuation,
            scout_strength_min=20,
            selected_position_id=3,
            sort_mode=4,
            secondary_score_mode=16,
            secondary_caller_argument=7,
        )

        self.assertIs(controller.last_scout_panel_state, panel)
        self.assertEqual(controller.last_scout_kwargs["page_mode"], 2)
        self.assertIs(controller.last_scout_kwargs["valuation_resolver"], valuation)
        self.assertEqual(controller.last_scout_kwargs["scout_strength_min"], 20)
        self.assertEqual(controller.last_scout_kwargs["selected_position_id"], 3)
        self.assertEqual(controller.last_scout_kwargs["sort_mode"], 4)
        self.assertEqual(controller.last_scout_kwargs["secondary_score_mode"], 16)
        self.assertEqual(controller.last_scout_kwargs["secondary_caller_argument"], 7)
        self.assertNotIn("status_controls", controller.last_scout_kwargs)
        self.assertEqual([row.player_id for row in rows], [406, 405, 404])
        self.assertEqual([row.result_index for row in rows], [0, 1, 2])
        self.assertEqual(rows[0].player_name, "Free Agent")
        self.assertEqual(rows[0].club_id, -1)
        self.assertIsNone(rows[0].club_name)
        self.assertTrue(rows[0].out_of_contract)
        self.assertEqual(rows[1].player_name, "Scout Result")
        self.assertEqual(rows[1].club_name, "Beta City")
        self.assertEqual(rows[1].positions, (2, 3, 0))
        self.assertEqual(len(rows[1].current_skill_bytes), 17)
        self.assertEqual(rows[1].age, 20)
        self.assertEqual(rows[1].history_average, 5.5)
        self.assertTrue(rows[1].transfer_listed)

    def test_scouting_backend_error_is_fail_closed_presentation_error(self):
        controller = FakeController()
        def broken_search(_panel, **_kwargs):
            raise ValueError("source control metadata unavailable")
        controller.search_scouting_players_mapped = broken_search
        with self.assertRaisesRegex(
            ManagementPresentationError,
            "source control metadata unavailable",
        ):
            ManagementSourceDataBridge(controller).scouting_search_rows(
                ScoutingReseedState(),
                page_mode=0,
                valuation_resolver=lambda _player: 1.0,
            )

    def test_missing_human_or_source_identity_fails_closed(self):
        controller = FakeController()
        controller.human = None
        bridge = ManagementSourceDataBridge(controller)
        with self.assertRaisesRegex(ManagementPresentationError, "Select"):
            bridge.club_header()
        with self.assertRaisesRegex(ManagementPresentationError, "Select"):
            bridge.squad_rows()

        controller = FakeController()
        controller.state.clubs[11] = SimpleNamespace(name="Beta City")
        bridge = ManagementSourceDataBridge(controller)
        with self.assertRaisesRegex(ManagementPresentationError, "short name"):
            bridge.fixture_rows()
        with self.assertRaisesRegex(ManagementPresentationError, "short name"):
            bridge.league_table_rows()

    def test_incomplete_fixture_source_contract_is_rejected_not_guessed(self):
        controller = FakeController()
        controller.state.premier_league.fixture_source_order = [17, 3]
        with self.assertRaisesRegex(ManagementPresentationError, "source ordering"):
            ManagementSourceDataBridge(controller).fixture_rows()

        controller = FakeController()
        controller.state.premier_league.fixture_source_order = (17, 999)
        with self.assertRaisesRegex(ManagementPresentationError, "missing"):
            ManagementSourceDataBridge(controller).fixture_rows()


if __name__ == "__main__":
    unittest.main()
