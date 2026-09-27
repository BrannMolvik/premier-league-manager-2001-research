import unittest
from datetime import date
from types import SimpleNamespace

from match_role_rating import best_preferred_role_rating
from transfer_decision import SellingClubDecision
from transfer_state import ContractTerms, TransferProposal, TransferRuntimeState
from transfer_workflow import (
    ScheduledTransferOutcome,
    cash_only_proposal_total_value,
    evaluate_live_cash_bid,
    execute_due_ordinary_cash_transfers,
    schedule_ordinary_cash_transfer,
    submit_live_cash_bid,
)


class Row:
    def __init__(self, id, field_08=1000, field_0c=0):
        self.id = id
        self.field_08 = field_08
        self.field_0c = field_0c


def build_state(*, eligible_count=20):
    target = SimpleNamespace(
        index=1,
        club_id=10,
        current_raw=[200] * 17,
        positions=(4, 0, 0),
        current_position=4,
        age=lambda on_date: 25,
        selling_squad_count_excluded=False,
    )
    target_rating = best_preferred_role_rating(
        target.current_raw,
        target.positions,
    )

    roster = [target]
    for index in range(2, 21):
        excluded = index > eligible_count
        roster.append(
            SimpleNamespace(
                index=index,
                club_id=10,
                current_raw=[100] * 17,
                positions=(4, 0, 0),
                current_position=4,
                age=lambda on_date: 25,
                selling_squad_count_excluded=excluded,
            )
        )

    rows = tuple(Row(i) for i in range(target_rating + 1))
    return SimpleNamespace(
        players={int(player.index): player for player in roster},
        clubs={
            10: SimpleNamespace(competition_id=20, country_id=30),
            11: SimpleNamespace(competition_id=20, country_id=30),
        },
        competitions={
            20: SimpleNamespace(valuation_division_category=5),
        },
        countries={
            30: SimpleNamespace(eu_status_flag=1),
        },
        positions={
            4: SimpleNamespace(lineup_group=0),
        },
        access_skill_financial_values=rows,
        calendar=SimpleNamespace(current_date=date(2000, 8, 18)),
        transfers=TransferRuntimeState(),
        ordered_club_roster=lambda club_id: tuple(roster)
        if int(club_id) == 10 else (),
    )


def build_completion_state(*, buyer_roster_count=5):
    target = SimpleNamespace(
        index=1,
        club_id=10,
        weekly_wage=500,
        contract_expiry_date=date(2001, 8, 18),
        promotion_bonus=0,
        appearance_fee=0,
        relegation_transfer_request_clause=False,
        big_club_offer_clause=False,
        big_money_offer_clause=False,
        house=False,
        car=False,
        signed_for_other_club=False,
        transfer_listed=True,
        loan_club_id=99,
        current_club_join_date=date(1999, 7, 1),
    )
    seller_roster = [1, *range(2, 20)]
    buyer_roster = list(range(100, 100 + buyer_roster_count))
    return SimpleNamespace(
        players={1: target},
        clubs={10: SimpleNamespace(), 11: SimpleNamespace()},
        club_roster_order={10: seller_roster, 11: buyer_roster},
        calendar=SimpleNamespace(current_date=date(2000, 8, 18)),
        transfers=TransferRuntimeState(),
    )


class ScheduledTransferCompletionTests(unittest.TestCase):
    def proposal(self):
        return TransferProposal(
            target_player_id=1,
            buying_club_id=11,
            cash_fee=750_000,
            contract_terms=ContractTerms(
                weekly_wage=12_000,
                signing_on_fee=80_000,
                promotion_bonus=25_000,
                contract_length_months=36,
                appearance_fee=1_250,
                relegation_transfer_request_clause=True,
                big_club_offer_clause=True,
                big_money_offer_clause=False,
                house=True,
                car=False,
            ),
        )

    def test_due_completion_moves_player_and_applies_contract(self):
        state = build_completion_state()
        proposal = self.proposal()
        state.transfers.submit_proposal(
            proposal,
            selling_club_id=10,
            current_date=state.calendar.current_date,
        )

        scheduled = schedule_ordinary_cash_transfer(state, proposal)
        self.assertEqual(scheduled.due_date, date(2000, 8, 19))
        self.assertTrue(state.players[1].signed_for_other_club)

        state.calendar.current_date = date(2000, 8, 19)
        result = execute_due_ordinary_cash_transfers(
            state,
            user_controlled_club_id=11,
            can_afford=lambda club_id, amount: (
                club_id == 11 and amount == 750_000
            ),
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].outcome, ScheduledTransferOutcome.COMPLETED)
        self.assertNotIn(1, state.club_roster_order[10])
        self.assertEqual(state.club_roster_order[11].count(1), 1)

        player = state.players[1]
        self.assertEqual(player.club_id, 11)
        self.assertEqual(player.current_club_join_date, date(2000, 8, 19))
        self.assertFalse(player.signed_for_other_club)
        self.assertFalse(player.transfer_listed)
        self.assertIsNone(player.loan_club_id)
        self.assertEqual(player.weekly_wage, 12_000)
        self.assertEqual(player.contract_expiry_date, date(2003, 8, 19))
        self.assertEqual(player.promotion_bonus, 25_000)
        self.assertEqual(player.appearance_fee, 1_250)
        self.assertTrue(player.relegation_transfer_request_clause)
        self.assertTrue(player.big_club_offer_clause)
        self.assertFalse(player.big_money_offer_clause)
        self.assertTrue(player.house)
        self.assertFalse(player.car)

        self.assertEqual(len(state.transfers.movements), 1)
        movement = state.transfers.movements[0]
        self.assertEqual(
            (
                movement.player_id,
                movement.from_club_id,
                movement.to_club_id,
                movement.consideration,
                movement.movement_date,
            ),
            (1, 10, 11, 750_000, date(2000, 8, 19)),
        )
        self.assertEqual(state.transfers.scheduled_transfers, [])
        self.assertNotIn((1, 11), state.transfers.proposals)
        self.assertNotIn(1, state.transfers.deals)

    def test_forty_player_buyer_reschedules_mode_zero_plus_seven_days(self):
        state = build_completion_state(buyer_roster_count=40)
        proposal = self.proposal()
        schedule_ordinary_cash_transfer(state, proposal)
        state.calendar.current_date = date(2000, 8, 19)

        result = execute_due_ordinary_cash_transfers(state)

        self.assertEqual(
            result[0].outcome,
            ScheduledTransferOutcome.RESCHEDULED_SQUAD_FULL,
        )
        self.assertEqual(len(state.transfers.scheduled_transfers), 1)
        retry = state.transfers.scheduled_transfers[0]
        self.assertEqual(retry.mode, 1)
        self.assertEqual(retry.due_date, date(2000, 8, 26))
        self.assertEqual(state.players[1].club_id, 10)
        self.assertEqual(state.transfers.movements, [])

    def test_controlled_buyer_requires_explicit_gate10_affordability(self):
        state = build_completion_state()
        proposal = self.proposal()
        schedule_ordinary_cash_transfer(state, proposal)
        state.calendar.current_date = date(2000, 8, 19)

        with self.assertRaisesRegex(RuntimeError, "affordability"):
            execute_due_ordinary_cash_transfers(
                state,
                user_controlled_club_id=11,
            )


class CashProposalTotalTests(unittest.TestCase):
    def test_default_cash_only_4efa20_total_is_exactly_cash_fee(self):
        proposal = TransferProposal(
            target_player_id=1,
            buying_club_id=11,
            cash_fee=693,
            negotiation_state_14=0,
            exchange_player_ids=(-1, -1, -1),
        )
        self.assertEqual(
            cash_only_proposal_total_value(proposal),
            693.0,
        )

    def test_unproven_negotiation_mode_is_rejected(self):
        proposal = TransferProposal(
            target_player_id=1,
            buying_club_id=11,
            cash_fee=1000,
            negotiation_state_14=1,
        )
        with self.assertRaisesRegex(ValueError, "mode 0"):
            cash_only_proposal_total_value(proposal)

    def test_exchange_player_requires_separate_total_path(self):
        proposal = TransferProposal(
            target_player_id=1,
            buying_club_id=11,
            cash_fee=1000,
            exchange_player_ids=(2, -1, -1),
        )
        with self.assertRaisesRegex(ValueError, "exchange"):
            cash_only_proposal_total_value(proposal)


class LiveCashBidWorkflowTests(unittest.TestCase):
    def test_live_bid_uses_current_player_value_and_accepts_exact_60_percent(self):
        state = build_state()
        proposal = TransferProposal(
            target_player_id=1,
            buying_club_id=11,
            cash_fee=693,
        )

        evaluation = evaluate_live_cash_bid(state, proposal)

        # Base 1000 * DIV6 1.10 * DEF 1.05 = 1155.
        self.assertAlmostEqual(evaluation.player_value, 1155.0)
        self.assertEqual(evaluation.proposal_total_value, 693.0)
        self.assertEqual(
            evaluation.decision,
            SellingClubDecision.ACCEPTED,
        )

    def test_live_bid_one_unit_under_exact_60_percent_is_too_cheap(self):
        state = build_state()
        evaluation = evaluate_live_cash_bid(
            state,
            TransferProposal(
                target_player_id=1,
                buying_club_id=11,
                cash_fee=692,
            ),
        )
        self.assertEqual(
            evaluation.decision,
            SellingClubDecision.TOO_CHEAP,
        )

    def test_live_bid_preserves_small_squad_reason_after_price_passes(self):
        state = build_state(eligible_count=16)
        evaluation = evaluate_live_cash_bid(
            state,
            TransferProposal(
                target_player_id=1,
                buying_club_id=11,
                cash_fee=1000,
            ),
        )
        self.assertEqual(
            evaluation.decision,
            SellingClubDecision.SQUAD_TOO_SMALL,
        )

    def test_submit_creates_proposal_deal_and_bid_log_before_rejection(self):
        state = build_state()

        evaluation = submit_live_cash_bid(
            state,
            target_player_id=1,
            buying_club_id=11,
            cash_fee=100,
            contract_terms=ContractTerms(
                weekly_wage=500,
                contract_length_months=36,
            ),
        )

        self.assertEqual(
            evaluation.decision,
            SellingClubDecision.TOO_CHEAP,
        )
        key = (1, 11)
        self.assertIn(key, state.transfers.proposals)
        self.assertIn(key, state.transfers.bid_log)
        self.assertEqual(state.transfers.bid_log[key].bid_value, 100)
        self.assertIn(1, state.transfers.deals)
        self.assertEqual(
            state.transfers.deals[1].contract_terms.weekly_wage,
            500,
        )

    def test_submit_rejects_bidding_for_own_player(self):
        state = build_state()
        with self.assertRaisesRegex(ValueError, "already owns"):
            submit_live_cash_bid(
                state,
                target_player_id=1,
                buying_club_id=10,
                cash_fee=1000,
            )


if __name__ == "__main__":
    unittest.main()
