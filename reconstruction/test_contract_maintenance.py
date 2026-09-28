import unittest
from datetime import date, timedelta

from contract_maintenance import (
    AiContractMaintenanceOutcome,
    ContractRenewalSuggestion,
    ContractRenewalSuggestionKind,
    ControlledContractMaintenanceOutcome,
    run_ai_monthly_contract_maintenance,
    run_controlled_monthly_contract_maintenance,
)
from game_state import GameCalendar, GameState
from transfer_state import ContractTerms, DealInProgress


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
        self.suspended = False
        self.loan_listed = False
        self.ai_transfer_status_bit_9 = False
        self.eu_status_code = 2
        self.contract_special_state_138 = 0
        self.contract_renewal_suggestion_pending = False
        self.previous_club_id_74 = None
        self.club_id = 10
        self.morale = 50

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
        player.contract_renewal_suggestion_pending = True
        rng = ScriptedRng([8, 0, 0])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=30,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.RENEWED)
        self.assertEqual(rng.bounds, [100, 100, 2])
        self.assertEqual(player.contract_expiry_date, date(2001, 7, 21))
        self.assertEqual(player.morale, 82)
        self.assertFalse(player.out_of_contract)
        self.assertFalse(player.signed_for_other_club)
        self.assertFalse(player.contract_renewal_suggestion_pending)

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
        rng = ScriptedRng([0, 0])

        outcome = run_ai_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            roster_count=18,
            rng=rng,
        )

        self.assertEqual(outcome, AiContractMaintenanceOutcome.RENEWED)
        self.assertEqual(rng.bounds, [100, 2])
        self.assertEqual(player.contract_expiry_date, date(2001, 7, 21))
        self.assertEqual(player.morale, 82)

    def test_417580_equivalent_block_and_loan_gates_force_renewal(self):
        for blocked, loan_club_id in ((0, None), (-1, 9)):
            with self.subTest(blocked=blocked, loan_club_id=loan_club_id):
                player = FakePlayer(on_date=self.on_date, high_rating=False)
                player.ai_transfer_block_value_64 = blocked
                player.loan_club_id = loan_club_id
                rng = ScriptedRng([0, 0])

                outcome = run_ai_monthly_contract_maintenance(
                    player,
                    on_date=self.on_date,
                    roster_count=30,
                    rng=rng,
                )

                self.assertEqual(outcome, AiContractMaintenanceOutcome.RENEWED)
                self.assertEqual(rng.bounds, [100, 2])

    def test_controlled_more_than_112_days_before_expiry_consumes_no_rng(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=113),
        )
        rng = ScriptedRng([])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.PRE_EXPIRY_NO_SUGGESTION,
        )
        self.assertFalse(player.out_of_contract)
        self.assertEqual(rng.bounds, [])

    def test_controlled_21_day_pre_expiry_sets_status_and_uses_one_suggestion_draw(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=21),
        )
        rng = ScriptedRng([9])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.PRE_EXPIRY_NO_SUGGESTION,
        )
        self.assertTrue(player.out_of_contract)
        self.assertEqual(rng.bounds, [10])

    def test_controlled_112_day_window_queues_bosman_suggestion_and_latches(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=112),
            age=24,
        )
        player.eu_status_code = 2
        rng = ScriptedRng([3])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.SUGGEST_BOSMAN_RENEWAL,
        )
        self.assertTrue(player.contract_renewal_suggestion_pending)
        self.assertEqual(rng.bounds, [10])

    def test_controlled_non_bosman_suggestion_uses_same_single_draw(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=100),
            age=23,
        )
        rng = ScriptedRng([0])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.SUGGEST_ORDINARY_RENEWAL,
        )
        self.assertTrue(player.contract_renewal_suggestion_pending)
        self.assertEqual(rng.bounds, [10])

    def test_controlled_existing_suggestion_latch_consumes_no_rng(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=50),
        )
        player.contract_renewal_suggestion_pending = True
        rng = ScriptedRng([])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.PRE_EXPIRY_NO_SUGGESTION,
        )
        self.assertEqual(rng.bounds, [])

    def test_controlled_pending_workflow_suppression_occurs_after_rng(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=50),
        )
        rng = ScriptedRng([2])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
            pending_contract_workflow=True,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome
            .SUGGESTION_SUPPRESSED_PENDING_WORKFLOW,
        )
        self.assertFalse(player.contract_renewal_suggestion_pending)
        self.assertEqual(rng.bounds, [10])

    def test_controlled_expired_grace_cleans_mapped_status_without_rng(self):
        expiry = self.on_date - timedelta(days=20)
        player = FakePlayer(on_date=self.on_date, expiry=expiry)
        player.loan_club_id = 30
        player.suspended = True
        player.out_of_contract = True
        player.transfer_listed = True
        player.ai_transfer_status_bit_9 = True
        player.loan_listed = True
        rng = ScriptedRng([])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.EXPIRED_GRACE,
        )
        self.assertEqual(player.club_id, 10)
        self.assertIsNone(player.loan_club_id)
        self.assertFalse(player.suspended)
        self.assertFalse(player.out_of_contract)
        self.assertFalse(player.transfer_listed)
        self.assertFalse(player.ai_transfer_status_bit_9)
        self.assertFalse(player.loan_listed)
        self.assertEqual(rng.bounds, [])

    def test_controlled_exact_21_days_past_expiry_detaches_free_player(self):
        expiry = self.on_date - timedelta(days=21)
        player = FakePlayer(on_date=self.on_date, expiry=expiry)
        rng = ScriptedRng([])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.DETACHED_OUT_OF_CONTRACT,
        )
        self.assertTrue(player.out_of_contract)
        self.assertEqual(player.previous_club_id_74, 10)
        self.assertEqual(player.club_id, -1)
        self.assertEqual(rng.bounds, [])

    def test_controlled_not_in_registered_roster_exits_before_cleanup(self):
        player = FakePlayer(
            on_date=self.on_date,
            expiry=self.on_date - timedelta(days=30),
        )
        player.transfer_listed = True
        rng = ScriptedRng([])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
            in_registered_roster=False,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.NOT_IN_REGISTERED_ROSTER,
        )
        self.assertTrue(player.transfer_listed)
        self.assertEqual(player.club_id, 10)
        self.assertEqual(rng.bounds, [])

    def test_controlled_special_state_remains_explicitly_deferred(self):
        player = FakePlayer(on_date=self.on_date)
        player.contract_special_state_138 = 0xFE
        rng = ScriptedRng([])

        outcome = run_controlled_monthly_contract_maintenance(
            player,
            on_date=self.on_date,
            rng=rng,
        )

        self.assertEqual(
            outcome,
            ControlledContractMaintenanceOutcome.SPECIAL_STATE_DEFERRED,
        )
        self.assertEqual(rng.bounds, [])

    def test_unified_monthly_pass_queues_live_controlled_suggestion(self):
        player = FakePlayer(
            index=1,
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=50),
            age=24,
        )
        rng = ScriptedRng([0])
        state = GameState(
            calendar=GameCalendar(self.on_date),
            players={1: player},
            club_roster_order={10: [1]},
            user_controlled_club_id=10,
            rng=rng,
        )

        state._run_monthly_contract_maintenance(self.on_date)

        self.assertEqual(rng.bounds, [10])
        self.assertTrue(player.contract_renewal_suggestion_pending)
        self.assertEqual(len(state.contract_renewal_suggestions), 1)
        suggestion = state.contract_renewal_suggestions[0]
        self.assertEqual(suggestion.player_id, 1)
        self.assertEqual(suggestion.queued_on, self.on_date)
        self.assertEqual(suggestion.kind, ContractRenewalSuggestionKind.BOSMAN)
        self.assertEqual(suggestion.message_id, 0x1B7)
        self.assertEqual(
            suggestion.event_class,
            "EAMAssManSuggestBosmanPlayerContractRenewalMsub",
        )
        self.assertEqual(suggestion.accepted_action_class, "EAMAmendContractsub")

    def test_unified_monthly_pass_suppresses_swap_family_deal_after_rng(self):
        player = FakePlayer(
            index=1,
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=50),
        )
        rng = ScriptedRng([0])
        state = GameState(
            calendar=GameCalendar(self.on_date),
            players={1: player},
            club_roster_order={10: [1]},
            user_controlled_club_id=10,
            rng=rng,
        )
        state.transfers.deals[1] = DealInProgress(
            player_id=1,
            buying_club_id=20,
            selling_club_id=10,
            state=3,
            contract_terms=ContractTerms(),
            created_date=self.on_date,
        )

        state._run_monthly_contract_maintenance(self.on_date)

        self.assertEqual(rng.bounds, [10])
        self.assertFalse(player.contract_renewal_suggestion_pending)
        self.assertEqual(state.contract_renewal_suggestions, [])

    def test_unified_monthly_detachment_removes_roster_and_player_mail(self):
        player = FakePlayer(
            index=1,
            on_date=self.on_date,
            expiry=self.on_date - timedelta(days=21),
        )
        rng = ScriptedRng([])
        state = GameState(
            calendar=GameCalendar(self.on_date),
            players={1: player},
            club_roster_order={10: [1]},
            user_controlled_club_id=10,
            rng=rng,
            contract_renewal_suggestions=[
                ContractRenewalSuggestion(
                    player_id=1,
                    queued_on=self.on_date - timedelta(days=30),
                    kind=ContractRenewalSuggestionKind.ORDINARY,
                )
            ],
        )

        state._run_monthly_contract_maintenance(self.on_date)

        self.assertEqual(rng.bounds, [])
        self.assertEqual(state.club_roster_order[10], [])
        self.assertEqual(player.club_id, -1)
        self.assertTrue(player.out_of_contract)
        self.assertEqual(player.previous_club_id_74, 10)
        self.assertEqual(state.contract_renewal_suggestions, [])

    def test_unified_monthly_dispatch_uses_active_loan_club_for_control(self):
        player = FakePlayer(
            index=1,
            on_date=self.on_date,
            expiry=self.on_date + timedelta(days=50),
        )
        player.club_id = 20
        player.loan_club_id = 10
        rng = ScriptedRng([9])
        state = GameState(
            calendar=GameCalendar(self.on_date),
            players={1: player},
            club_roster_order={20: [1]},
            user_controlled_club_id=10,
            rng=rng,
        )

        state._run_monthly_contract_maintenance(self.on_date)

        # Controlled 0x41BEE0 uses RNG(10); the AI branch would use RNG(100).
        self.assertEqual(rng.bounds, [10])

    def test_game_state_monthly_ai_pass_skips_controlled_club(self):
        controlled = FakePlayer(index=1, on_date=self.on_date, high_rating=False)
        ai_player = FakePlayer(index=2, on_date=self.on_date, high_rating=False)
        ai_player.club_id = 20
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
