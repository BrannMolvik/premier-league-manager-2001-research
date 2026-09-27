from datetime import date
import unittest

from finance_state import (
    BalanceRuntimeState,
    CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY,
    CREDIT_SECONDARY_DEBIT_RATE,
    FinancialObjectiveState,
    TRANSFER_ACCOUNT_CATEGORY,
)


class BalanceRuntimeStateTests(unittest.TestCase):
    def test_can_afford_uses_current_cash_qword_semantics(self):
        balance = BalanceRuntimeState(current_cash=1_000_000)
        self.assertTrue(balance.can_afford(1_000_000))
        self.assertFalse(balance.can_afford(1_000_001))

    def test_debit_subtracts_and_records_negative_posting(self):
        balance = BalanceRuntimeState(current_cash=1_000_000)
        posting = balance.debit(
            750_000,
            category=TRANSFER_ACCOUNT_CATEGORY,
            posting_date=date(2000, 8, 19),
        )
        self.assertEqual(balance.current_cash, 250_000)
        self.assertEqual(posting.amount, -750_000)
        self.assertEqual(posting.category, 1000)

    def test_credit_adds_and_records_positive_posting(self):
        balance = BalanceRuntimeState(current_cash=250_000)
        posting = balance.credit(
            750_000,
            category=TRANSFER_ACCOUNT_CATEGORY,
            posting_date=date(2000, 8, 19),
        )
        self.assertEqual(balance.current_cash, 998_500)
        self.assertEqual(posting.amount, 750_000)
        self.assertEqual(posting.category, 1000)
        self.assertEqual(
            [(entry.category, entry.amount) for entry in balance.ledger],
            [
                (CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY, -1_500),
                (TRANSFER_ACCOUNT_CATEGORY, 750_000),
            ],
        )

    def test_debit_rejects_insufficient_cash_without_mutation(self):
        balance = BalanceRuntimeState(current_cash=749_999)
        with self.assertRaisesRegex(ValueError, "insufficient"):
            balance.debit(
                750_000,
                category=TRANSFER_ACCOUNT_CATEGORY,
                posting_date=date(2000, 8, 19),
            )
        self.assertEqual(balance.current_cash, 749_999)
        self.assertEqual(balance.ledger, [])


    def test_credit_secondary_debit_preserves_fraction_instead_of_truncating(self):
        balance = BalanceRuntimeState(current_cash=10)
        posting = balance.credit(
            1,
            category=TRANSFER_ACCOUNT_CATEGORY,
            posting_date=date(2000, 8, 19),
        )
        self.assertEqual(CREDIT_SECONDARY_DEBIT_RATE, 0.002)
        self.assertEqual(posting.amount, 1)
        self.assertAlmostEqual(balance.current_cash, 10.998)
        self.assertEqual(balance.ledger[0].category, 1600)
        self.assertAlmostEqual(balance.ledger[0].amount, -0.002)
        self.assertEqual(balance.ledger[1], posting)

    def test_fractional_finance_posting_is_not_rejected_as_zero(self):
        posting = __import__("finance_state").FinancePosting(
            amount=-0.002,
            category=1600,
            posting_date=date(2000, 8, 19),
        )
        self.assertAlmostEqual(posting.amount, -0.002)


class FinancialObjectiveStateTests(unittest.TestCase):
    def test_fresh_premier_league_candidates_use_recovered_rank_half(self):
        self.assertEqual(
            FinancialObjectiveState.premier_league_candidates(19, 20),
            (13, 1, 5),
        )
        self.assertEqual(
            FinancialObjectiveState.premier_league_candidates(9, 20),
            (1, 5, 6),
        )
        # The executable comparison is >=, so rank 10 is already high-half.
        self.assertEqual(
            FinancialObjectiveState.premier_league_candidates(10, 20),
            (13, 1, 5),
        )

    def test_selection_replaces_cash_from_exact_objective_percentages(self):
        objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        replacement = objective.select(0, date(2000, 8, 18))
        self.assertEqual(objective.selected_objective_id, 13)
        self.assertEqual(replacement, 47_600_000)
        self.assertEqual(objective.starting_funds_snapshot, 47_600_000)
        self.assertEqual(objective.target_cash, 51_800_000)
        self.assertEqual(objective.deadline, date(2003, 8, 18))
        self.assertTrue(objective.active)
        self.assertFalse(objective.progression_gate_reached)

    def test_deadline_threshold_is_strict_above_95_percent(self):
        objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        objective.select(0, date(2000, 8, 18))
        objective.progression_gate_reached = True

        self.assertIsNone(objective.evaluate(0, date(2002, 8, 18)))
        self.assertEqual(
            objective.evaluate(51_800_001, date(2003, 1, 1)).outcome,
            "success",
        )
        near = objective.evaluate(49_210_001, date(2003, 1, 1))
        self.assertEqual((near.outcome, near.sacking_reason), ("near_miss", None))
        dismissed = objective.evaluate(49_210_000, date(2003, 1, 1))
        self.assertEqual((dismissed.outcome, dismissed.sacking_reason), ("dismissed", 5))

    def test_deadline_without_progression_gate_uses_original_reason_four_branch(self):
        objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        objective.select(0, date(2000, 8, 18))
        result = objective.evaluate(100_000_000, date(2003, 6, 1))
        self.assertEqual((result.outcome, result.sacking_reason), ("dismissed", 4))


if __name__ == "__main__":
    unittest.main()
