from datetime import date
from types import SimpleNamespace
import unittest

from finance_state import (
    BalanceRuntimeState,
    GATE_HOME_ACCOUNT_CATEGORY,
    GATE_VISITING_ACCOUNT_CATEGORY,
    PLAYER_COST_ACCOUNT_CATEGORY,
    SUPPORT_STAFF_COST_ACCOUNT_CATEGORY,
)
from gate_receipts import GateAttendanceCell, GateReceiptResult
from game_state import GameCalendar, GameState


def player(index, club_id, weekly_wage, *, loan_club_id=None):
    return SimpleNamespace(
        index=int(index),
        club_id=int(club_id),
        loan_club_id=loan_club_id,
        weekly_wage=int(weekly_wage),
    )


def state_for(on_date, *, cash=10_000):
    players = {
        1: player(1, 10, 1_000),
        2: player(2, 10, 500),
        # Registered elsewhere but temporarily active for club 10. The
        # recovered 0x41FA50 payroll predicate excludes this loaned-in shape.
        3: player(3, 20, 700, loan_club_id=10),
    }
    return GameState(
        calendar=GameCalendar(on_date),
        players=players,
        club_roster_order={10: [1, 2, 3], 20: [3]},
        finance_balances={10: BalanceRuntimeState(current_cash=cash)},
    )


class CupControlledGatePostingTests(unittest.TestCase):
    def test_each_controlled_participant_uses_own_ticket_prices(self):
        state = GameState(
            calendar=GameCalendar(date(2000, 8, 19)),
            players={},
            finance_balances={
                10: BalanceRuntimeState(current_cash=10_000),
                20: BalanceRuntimeState(current_cash=20_000),
            },
            ticket_states={
                10: SimpleNamespace(seating_price=30, terrace_price=20),
                20: SimpleNamespace(seating_price=12, terrace_price=8),
            },
        )
        receipts = GateReceiptResult(
            home_seating=GateAttendanceCell(0.0, 1.0, 1, 100),
            visiting_seating=GateAttendanceCell(0.0, 1.0, 1, 40),
            home_terrace=GateAttendanceCell(0.0, 1.0, 1, 60),
            visiting_terrace=GateAttendanceCell(0.0, 1.0, 1, 20),
            home_revenue=0,
            visiting_revenue=0,
        )

        posted = state.post_cup_gate_receipts(10, 20, receipts)

        self.assertEqual(
            posted,
            {
                10: {
                    GATE_VISITING_ACCOUNT_CATEGORY: 1600,
                    GATE_HOME_ACCOUNT_CATEGORY: 4200,
                },
                20: {
                    GATE_VISITING_ACCOUNT_CATEGORY: 640,
                    GATE_HOME_ACCOUNT_CATEGORY: 1680,
                },
            },
        )
        # Balance.credit() also applies the exact category-1600 secondary
        # debit, so verify the primary gate postings themselves by category.
        self.assertEqual(
            [(p.amount, p.category) for p in state.finance_balances[10].ledger
             if p.category in (GATE_VISITING_ACCOUNT_CATEGORY, GATE_HOME_ACCOUNT_CATEGORY)],
            [(1600, GATE_VISITING_ACCOUNT_CATEGORY), (4200, GATE_HOME_ACCOUNT_CATEGORY)],
        )
        self.assertEqual(
            [(p.amount, p.category) for p in state.finance_balances[20].ledger
             if p.category in (GATE_VISITING_ACCOUNT_CATEGORY, GATE_HOME_ACCOUNT_CATEGORY)],
            [(640, GATE_VISITING_ACCOUNT_CATEGORY), (1680, GATE_HOME_ACCOUNT_CATEGORY)],
        )

    def test_uncontrolled_or_unmaterialized_participant_is_not_posted(self):
        state = GameState(
            calendar=GameCalendar(date(2000, 8, 19)),
            players={},
            finance_balances={10: BalanceRuntimeState(current_cash=10_000)},
            ticket_states={10: SimpleNamespace(seating_price=30, terrace_price=20)},
        )
        receipts = GateReceiptResult(
            home_seating=GateAttendanceCell(0.0, 1.0, 1, 1),
            visiting_seating=GateAttendanceCell(0.0, 1.0, 1, 1),
            home_terrace=GateAttendanceCell(0.0, 1.0, 1, 1),
            visiting_terrace=GateAttendanceCell(0.0, 1.0, 1, 1),
            home_revenue=0,
            visiting_revenue=0,
        )

        self.assertEqual(
            tuple(state.post_cup_gate_receipts(10, 20, receipts)),
            (10,),
        )


class WeeklyPlayerPayrollTests(unittest.TestCase):
    def test_recovered_finance_category_constants(self):
        self.assertEqual(PLAYER_COST_ACCOUNT_CATEGORY, 101)
        self.assertEqual(SUPPORT_STAFF_COST_ACCOUNT_CATEGORY, 102)

    def test_saturday_payroll_debits_registered_players_and_excludes_loaned_in(self):
        state = state_for(date(2000, 8, 19))

        result = state.run_weekly_player_payroll()

        self.assertEqual(result, {10: 1_500})
        self.assertEqual(state.finance_balances[10].current_cash, 8_500)
        self.assertEqual(len(state.finance_balances[10].ledger), 1)
        posting = state.finance_balances[10].ledger[0]
        self.assertEqual(posting.amount, -1_500)
        self.assertEqual(posting.category, 101)
        self.assertEqual(posting.posting_date, date(2000, 8, 19))

    def test_non_saturday_payroll_is_noop(self):
        state = state_for(date(2000, 8, 18))

        self.assertEqual(state.run_weekly_player_payroll(), {})
        self.assertEqual(state.finance_balances[10].current_cash, 10_000)
        self.assertEqual(state.finance_balances[10].ledger, [])

    def test_insufficient_cash_matches_balance_debit_refusal(self):
        state = state_for(date(2000, 8, 19), cash=1_499)

        self.assertEqual(state.run_weekly_player_payroll(), {})
        self.assertEqual(state.finance_balances[10].current_cash, 1_499)
        self.assertEqual(state.finance_balances[10].ledger, [])

    def test_day_advance_runs_payroll_when_friday_becomes_saturday(self):
        state = state_for(date(2000, 8, 18))

        self.assertEqual(state.advance_one_day(), date(2000, 8, 19))
        self.assertEqual(state.finance_balances[10].current_cash, 8_500)
        self.assertEqual(
            state.finance_balances[10].ledger[0].category,
            PLAYER_COST_ACCOUNT_CATEGORY,
        )


if __name__ == "__main__":
    unittest.main()
