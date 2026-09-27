import unittest
from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

from player_contract import (
    contract_expiry_from_month_span,
    initial_weekly_wage,
    live_player_signing_on_fee_expectation,
    live_player_wage_expectation,
    live_player_wage_floor,
    round_transfer_signing_fee_amount,
    round_transfer_wage_amount,
    signing_fee_doubling_eligible,
)


@dataclass(frozen=True)
class FinancialRow:
    id: int
    weekly_wage_base: int
    weekly_wage_random_range: int
    field_18: int = 0
    field_1c: int = 0


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

    def test_wage_rounding_uses_1_2_3_significant_digits(self):
        self.assertEqual(round_transfer_wage_amount(949), 900)
        self.assertEqual(round_transfer_wage_amount(950), 1000)
        self.assertEqual(round_transfer_wage_amount(1125), 1100)
        self.assertEqual(round_transfer_wage_amount(1150), 1200)
        self.assertEqual(round_transfer_wage_amount(123456), 123000)

    def test_signing_fee_rounding_uses_exact_mode_minus2_ladder(self):
        self.assertEqual(round_transfer_signing_fee_amount(19.6), 20)
        # Preserve the observed executable 20..100 quotient branch exactly.
        self.assertEqual(round_transfer_signing_fee_amount(50), 10)
        self.assertEqual(round_transfer_signing_fee_amount(125), 130)
        self.assertEqual(round_transfer_signing_fee_amount(999), 1000)
        self.assertEqual(round_transfer_signing_fee_amount(123456), 123500)
        self.assertEqual(round_transfer_signing_fee_amount(1_234_567), 1_235_000)
        self.assertEqual(round_transfer_signing_fee_amount(12_345_678), 12_250_000)

    def test_live_contract_expectations_use_buyer_country_and_expired_eu_predicate(self):
        rows = tuple(
            FinancialRow(i, 100, 10, 1000, 100)
            for i in range(100)
        )
        rows = list(rows)
        rows[99] = FinancialRow(
            99,
            weekly_wage_base=1234,
            weekly_wage_random_range=266,
            field_18=10000,
            field_1c=2500,
        )
        player = SimpleNamespace(
            index=1,
            current_raw=[255] * 17,
            positions=(1, 0, 0),
            eu_status_code=2,
            contract_expiry_date=date(2000, 8, 1),
            age=lambda on_date: 25,
        )
        state = SimpleNamespace(
            players={1: player},
            clubs={7: SimpleNamespace(country_id=3)},
            countries={
                3: SimpleNamespace(financial_multiplier_percent=75),
            },
            access_skill_financial_values=tuple(rows),
            calendar=SimpleNamespace(current_date=date(2000, 8, 18)),
        )

        self.assertTrue(signing_fee_doubling_eligible(state, 1))
        self.assertEqual(live_player_wage_expectation(state, 1, 7), 1100)
        self.assertEqual(live_player_wage_floor(state, 1, 7), 900)
        # (10000+2500)*75% = 9375, doubled = 18750, rounded to 18800.
        self.assertEqual(
            live_player_signing_on_fee_expectation(state, 1, 7),
            18800,
        )

        player.eu_status_code = 1
        self.assertFalse(signing_fee_doubling_eligible(state, 1))
        self.assertEqual(
            live_player_signing_on_fee_expectation(state, 1, 7),
            9400,
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
