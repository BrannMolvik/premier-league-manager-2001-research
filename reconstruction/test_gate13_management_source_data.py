from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace
import unittest

from gate13_management_source_data import (
    ManagementPresentationError,
    ManagementSourceDataBridge,
)
from finance_state import BalanceRuntimeState, FinancePosting, FinancialObjectiveState
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

    def test_squad_projection_retains_recovered_neutral_runtime_fields(self):
        bridge = ManagementSourceDataBridge(FakeController())

        second, first = bridge.squad_rows()

        self.assertEqual(
            (second.full_name, second.shirt_number, second.positions,
             second.condition, second.form_state, second.morale),
            ("Second Source", 9, (4, 0, 0), 91, 3, 88),
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
