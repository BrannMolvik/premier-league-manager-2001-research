from datetime import date
import unittest

from finance_state import (
    BalanceRuntimeState,
    CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY,
    CREDIT_SECONDARY_DEBIT_RATE,
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


if __name__ == "__main__":
    unittest.main()
