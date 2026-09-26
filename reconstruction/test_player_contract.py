import unittest
from dataclasses import dataclass
from datetime import date

from player_contract import contract_expiry_from_month_span, initial_weekly_wage


@dataclass(frozen=True)
class FinancialRow:
    id: int
    weekly_wage_base: int
    weekly_wage_random_range: int


class RecordingRng:
    def __init__(self, value):
        self.value = int(value)
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(int(bound))
        return self.value


class PlayerContractTests(unittest.TestCase):
    def test_starting_wage_uses_best_role_row_base_range_and_country_percent(self):
        # Maximum preferred goalkeeper rating is exactly 99.
        rows = tuple(
            FinancialRow(i, 1000 + i * 10, 200 + i)
            for i in range(100)
        )
        rng = RecordingRng(50)

        wage = initial_weekly_wage(
            (255,) * 17,
            (1, 0, 0),
            rows,
            75,
            rng,
        )

        self.assertEqual(rng.bounds, [299])
        self.assertEqual(wage, ((1000 + 990) + 50) * 75 // 100)

    def test_starting_wage_rejects_nonpositive_range(self):
        rows = [
            FinancialRow(i, 1000, 1)
            for i in range(100)
        ]
        rows[99] = FinancialRow(99, 1000, 0)

        with self.assertRaisesRegex(ValueError, "random range"):
            initial_weekly_wage(
                (255,) * 17,
                (1, 0, 0),
                rows,
                100,
                RecordingRng(0),
            )

    def test_contract_expiry_advances_months_preserving_day(self):
        self.assertEqual(
            contract_expiry_from_month_span(date(2000, 8, 18), 12),
            date(2001, 8, 18),
        )
        self.assertEqual(
            contract_expiry_from_month_span(date(2000, 8, 18), 60),
            date(2005, 8, 18),
        )


if __name__ == "__main__":
    unittest.main()
