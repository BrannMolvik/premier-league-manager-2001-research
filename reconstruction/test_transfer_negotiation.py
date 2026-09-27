import unittest
from datetime import date
from types import SimpleNamespace

from transfer_negotiation import (
    adjust_live_player_counter_offer,
    adjust_player_counter_offer,
)
from transfer_state import ContractTerms, TransferProposal


class RecordingRng:
    def __init__(self, values):
        self.values = list(values)
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(int(bound))
        if not self.values:
            raise AssertionError("unexpected RNG draw")
        value = int(self.values.pop(0))
        if not 0 <= value < int(bound):
            raise AssertionError("recorded RNG value outside bound")
        return value


class CounterOfferTransformTests(unittest.TestCase):
    def proposal(self, *, wage=1000, sign=2000, prev_wage=0, prev_sign=0):
        return TransferProposal(
            target_player_id=1,
            buying_club_id=2,
            cash_fee=500_000,
            contract_terms=ContractTerms(
                weekly_wage=wage,
                signing_on_fee=sign,
                contract_length_months=12,
            ),
            previous_wage_offer=prev_wage,
            previous_signing_on_fee_offer=prev_sign,
        )

    def test_desired_above_110_percent_raises_money_terms(self):
        rng = RecordingRng([0])
        result = adjust_player_counter_offer(
            self.proposal(),
            fresh_wage_expectation=1200,
            fresh_signing_on_fee_expectation=2300,
            current_player_weekly_wage=900,
            renewing_same_club=False,
            rng=rng,
        )
        self.assertEqual(result.proposal.contract_terms.weekly_wage, 1200)
        self.assertEqual(result.proposal.contract_terms.signing_on_fee, 2300)
        self.assertTrue(result.wage_was_raised)
        self.assertTrue(result.signing_fee_was_raised)
        self.assertEqual(result.proposal.previous_wage_offer, 1000)
        self.assertEqual(result.proposal.previous_signing_on_fee_offer, 2000)
        self.assertEqual(result.proposal.contract_terms.contract_length_months, 24)
        self.assertEqual(rng.bounds, [3])

    def test_exact_110_percent_does_not_raise(self):
        rng = RecordingRng([1])
        result = adjust_player_counter_offer(
            self.proposal(),
            fresh_wage_expectation=1100,
            fresh_signing_on_fee_expectation=2200,
            current_player_weekly_wage=900,
            renewing_same_club=False,
            rng=rng,
        )
        self.assertEqual(result.proposal.contract_terms.weekly_wage, 1000)
        self.assertEqual(result.proposal.contract_terms.signing_on_fee, 2000)
        self.assertFalse(result.money_terms_changed)
        self.assertEqual(result.proposal.contract_terms.contract_length_months, 36)

    def test_repeated_wage_uses_anchor_midpoint_and_current_wage_floor(self):
        rng = RecordingRng([2])
        result = adjust_player_counter_offer(
            self.proposal(wage=1400, sign=2500, prev_wage=1000, prev_sign=2000),
            fresh_wage_expectation=999999,
            fresh_signing_on_fee_expectation=999999,
            current_player_weekly_wage=1300,
            renewing_same_club=False,
            rng=rng,
        )
        # midpoint(1000, 1400)=1200, then floor to current wage 1300.
        self.assertEqual(result.desired_weekly_wage, 1300)
        # 1300 is not > 1540 (110% of 1400), so submitted wage stays 1400.
        self.assertEqual(result.proposal.contract_terms.weekly_wage, 1400)
        # signing midpoint(2000,2500)=2250, also within 10%.
        self.assertEqual(result.desired_signing_on_fee, 2250)
        self.assertEqual(result.proposal.contract_terms.signing_on_fee, 2500)
        self.assertEqual(result.proposal.contract_terms.contract_length_months, 48)

    def test_signed_midpoint_truncates_toward_zero(self):
        # midpoint(1001,1000): 1001 + trunc(-1/2) == 1001.
        rng = RecordingRng([0])
        result = adjust_player_counter_offer(
            self.proposal(wage=1000, sign=1000, prev_wage=1001, prev_sign=1001),
            fresh_wage_expectation=0,
            fresh_signing_on_fee_expectation=0,
            current_player_weekly_wage=0,
            renewing_same_club=False,
            rng=rng,
        )
        self.assertEqual(result.desired_weekly_wage, 1001)
        self.assertEqual(result.desired_signing_on_fee, 1001)

    def test_live_adapter_uses_runtime_expectations_and_current_wage(self):
        rows = tuple(
            SimpleNamespace(
                id=i,
                weekly_wage_base=100,
                weekly_wage_random_range=10,
                field_18=1000,
                field_1c=100,
            )
            for i in range(100)
        )
        player = SimpleNamespace(
            index=1,
            club_id=10,
            weekly_wage=950,
            current_raw=[255] * 17,
            positions=(1, 0, 0),
            eu_status_code=2,
            contract_expiry_date=date(2000, 8, 1),
            age=lambda on_date: 25,
        )
        state = SimpleNamespace(
            players={1: player},
            clubs={
                10: SimpleNamespace(country_id=3),
                11: SimpleNamespace(country_id=3),
            },
            countries={
                3: SimpleNamespace(financial_multiplier_percent=100),
            },
            access_skill_financial_values=rows,
            calendar=SimpleNamespace(current_date=date(2000, 8, 18)),
        )
        proposal = TransferProposal(
            target_player_id=1,
            buying_club_id=11,
            contract_terms=ContractTerms(
                weekly_wage=50,
                signing_on_fee=50,
                contract_length_months=12,
            ),
        )
        rng = RecordingRng([2])

        result = adjust_live_player_counter_offer(
            state,
            proposal,
            rng,
        )

        # Max row: wage fresh expectation 110 -> mode -1 => 100, then
        # current wage floor is only used on repeated negotiations.
        self.assertEqual(result.desired_weekly_wage, 100)
        self.assertEqual(result.proposal.contract_terms.weekly_wage, 100)
        # Signing raw (1000+100)*2 expired-EU bonus = 2200, mode -2 => 2200.
        self.assertEqual(result.desired_signing_on_fee, 2200)
        self.assertEqual(result.proposal.contract_terms.signing_on_fee, 2200)
        self.assertEqual(result.proposal.contract_terms.contract_length_months, 48)
        self.assertEqual(rng.bounds, [3])

    def test_same_club_renewal_skips_signing_fee_revision(self):
        rng = RecordingRng([1])
        result = adjust_player_counter_offer(
            self.proposal(wage=1000, sign=10),
            fresh_wage_expectation=1000,
            fresh_signing_on_fee_expectation=999999,
            current_player_weekly_wage=900,
            renewing_same_club=True,
            rng=rng,
        )
        self.assertEqual(result.proposal.contract_terms.signing_on_fee, 10)
        self.assertEqual(result.proposal.previous_signing_on_fee_offer, 10)
        self.assertFalse(result.signing_fee_was_raised)


if __name__ == "__main__":
    unittest.main()
