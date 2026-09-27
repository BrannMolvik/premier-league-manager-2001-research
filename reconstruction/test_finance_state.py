from datetime import date
import unittest

from finance_state import (
    BalanceRuntimeState,
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
        self.assertEqual(balance.current_cash, 1_000_000)
        self.assertEqual(posting.amount, 750_000)
        self.assertEqual(posting.category, 1000)

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


if __name__ == "__main__":
    unittest.main()
