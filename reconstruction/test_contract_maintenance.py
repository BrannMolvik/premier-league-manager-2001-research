import unittest
from datetime import date, timedelta

from contract_maintenance import (
    AiContractMaintenanceOutcome,
    run_ai_monthly_contract_maintenance,
)
from game_state import GameCalendar, GameState


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(int(bound))
        if not self.values:
            raise AssertionError("unexpected RNG draw")
        value = int(self.values.pop(0))
        if not 0 <= value < int(bound):
            raise AssertionError("scripted RNG value outside bound")
        return value


class FakePlayer:
    def __init__(
        self,
        *,
        index=1,
        on_date=date(2000, 7, 1),
        expiry=None,
        high_rating=False,
        age=24,
        tenure_weeks=105,
    ):
        self.index = int(index)
        self.current_raw = [255 if high_rating else 0] * 17
        self.positions = (1, 0, 0)
        self.contract_expiry_date = (
            on_date + timedelta(days=20) if expiry is None else expiry
        )
        self.current_club_join_date = on_date - timedelta(weeks=tenure_weeks)
        self.age_value = age
        self.ai_transfer_block_value_64 = -1
        self.loan_club_id = None
        self.transfer_listed = False
        self.out_of_contract = False
        self.startup_month_span = 12
        self.signed_for_other_club = False

    def age(self, _on_date):
        return self.age_value


class ContractMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.on_date = date(2000, 7, 1)

    def test_more_than_30_days_before_expiry_consumes_no_rng(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=31),
        )
        rng = ScriptedRng([])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=30,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.NOT_DUE)
        self.assertEqual(rng.bounds, [])

    def test_low_rating_release_uses_one_draw_and_sets_exact_mapped_state(self):
        player = FakePlayer(on_date=self.on_date, high_rating=False)
        rng = ScriptedRng([7])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=19,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.OUT_OF_CONTRACT)
        self.assertEqual(rng.bounds, [100])
        self.assertTrue(player.transfer_listed)
        self.assertTrue(player.out_of_contract)
        self.assertEqual(player.startup_month_span, 0)
        self.assertEqual(player.contract_expiry_date, self.on_date + timedelta(days=20))

    def test_low_rating_non_release_consumes_second_draw_but_second_cannot_release(self):
        expiry = date(2000, 7, 21)
        player = FakePlayer(
            on_date=self.on_date,
            expiry=expiry,
            high_rating=False,
        )
        player.out_of_contract = True
        player.signed_for_other_club = True
        rng = ScriptedRng([8, 0])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=30,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.RENEWED)
        self.assertEqual(rng.bounds, [100, 100])
        self.assertEqual(player.contract_expiry_date, date(2001, 7, 21))
        self.assertFalse(player.out_of_contract)
        self.assertFalse(player.signed_for_other_club)

    def test_high_rating_release_is_decided_by_second_draw(self):
        player = FakePlayer(on_date=self.on_date, high_rating=True)
        rng = ScriptedRng([99, 1])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=30,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.OUT_OF_CONTRACT)
        self.assertEqual(rng.bounds, [100, 100])

    def test_failed_release_eligibility_renews_without_an_extra_draw(self):
        player = FakePlayer(on_date=self.on_date, high_rating=False)
        rng = ScriptedRng([0])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=18,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.RENEWED)
        self.assertEqual(rng.bounds, [100])
        self.assertEqual(player.contract_expiry_date, date(2001, 7, 21))

    def test_417580_equivalent_block_and_loan_gates_force_renewal(self):
        for blocked, loan_club_id in ((0, None), (-1, 9)):
            with self.subTest(blocked=blocked, loan_club_id=loan_club_id):
                player = FakePlayer(on_date=self.on_date, high_rating=False)
                player.ai_transfer_block_value_64 = blocked
                player.loan_club_id = loan_club_id
                rng = ScriptedRng([0])

                outcome = run_ai_monthly_contract_maintenance(
                    player,
                    on_date=self.on_date,
                    roster_count=30,
                    rng=rng,
                )

                self.assertEqual(outcome, AiContractMaintenanceOutcome.RENEWED)
                self.assertEqual(rng.bounds, [100])

    def test_game_state_monthly_ai_pass_skips_controlled_club(self):
        controlled = FakePlayer(index=1, on_date=self.on_date, high_rating=False)
        ai_player = FakePlayer(index=2, on_date=self.on_date, high_rating=False)
        rng = ScriptedRng([8, 50])
        state = GameState(
            calendar=GameCalendar(self.on_date),
            players={1: controlled, 2: ai_player},
            club_roster_order={10: [1], 20: [2]},
            user_controlled_club_id=10,
            rng=rng,
        )

        state._run_monthly_ai_contract_maintenance(self.on_date)

        self.assertEqual(rng.bounds, [100, 100])
        self.assertEqual(
            controlled.contract_expiry_date,
            self.on_date + timedelta(days=20),
        )
        self.assertEqual(ai_player.contract_expiry_date, date(2001, 7, 21))


if __name__ == "__main__":
    unittest.main()
