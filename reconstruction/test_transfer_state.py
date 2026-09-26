import unittest
from datetime import date

from transfer_state import (
    ContractTerms,
    DEAL_PENDING,
    DEAL_PLAYER_REJECTED,
    DEAL_READY,
    DEAL_SWAP_OFFSET,
    PlayerMovement,
    TransferProposal,
    TransferRuntimeState,
)


class TransferRuntimeStateTests(unittest.TestCase):
    def terms(self):
        return ContractTerms(
            weekly_wage=12500,
            signing_on_fee=100000,
            promotion_bonus=25000,
            contract_length_months=36,
            appearance_fee=750,
            relegation_transfer_request_clause=True,
            big_club_offer_clause=True,
            house=True,
        )

    def test_cash_proposal_creates_base_pending_deal_and_bid_log(self):
        state = TransferRuntimeState()
        proposal = TransferProposal(
            target_player_id=100,
            buying_club_id=1,
            cash_fee=2_500_000,
            contract_terms=self.terms(),
        )

        state.submit_proposal(
            proposal,
            selling_club_id=2,
            current_date=date(2000, 9, 1),
        )

        self.assertEqual(state.proposals[(100, 1)], proposal)
        self.assertEqual(state.deals[100].state, DEAL_PENDING)
        self.assertEqual(state.deals[100].buying_club_id, 1)
        self.assertEqual(state.deals[100].selling_club_id, 2)
        self.assertEqual(state.bid_log[(100, 1)].bid_value, 2_500_000)
        self.assertEqual(state.bid_log[(100, 1)].bid_date, date(2000, 9, 1))

    def test_repeated_bid_updates_keyed_log_instead_of_duplicating(self):
        state = TransferRuntimeState()
        first = TransferProposal(100, 1, cash_fee=1_000_000)
        second = TransferProposal(100, 1, cash_fee=1_500_000)

        state.submit_proposal(
            first,
            selling_club_id=2,
            current_date=date(2000, 9, 1),
        )
        entry = state.bid_log[(100, 1)]
        entry.status_counter = 7
        state.submit_proposal(
            second,
            selling_club_id=2,
            current_date=date(2000, 9, 3),
        )

        self.assertEqual(len(state.bid_log), 1)
        self.assertIs(state.bid_log[(100, 1)], entry)
        self.assertEqual(entry.bid_value, 1_500_000)
        self.assertEqual(entry.bid_date, date(2000, 9, 3))
        self.assertEqual(entry.status_counter, 7)

    def test_swap_proposal_marks_target_and_exchange_deals_with_plus_three(self):
        state = TransferRuntimeState()
        proposal = TransferProposal(
            target_player_id=100,
            buying_club_id=1,
            cash_fee=500_000,
            exchange_player_ids=(200, 201, -1),
            contract_terms=self.terms(),
        )

        state.submit_proposal(
            proposal,
            selling_club_id=2,
            current_date=date(2000, 9, 1),
        )

        self.assertTrue(proposal.has_exchange_player)
        self.assertEqual(proposal.involved_player_ids, (100, 200, 201))
        self.assertEqual(state.deals[100].state, DEAL_SWAP_OFFSET)
        self.assertEqual(state.deals[200].state, DEAL_SWAP_OFFSET)
        self.assertEqual(state.deals[201].state, DEAL_SWAP_OFFSET)
        self.assertEqual(state.deals[200].buying_club_id, 2)
        self.assertEqual(state.deals[200].selling_club_id, 1)

    def test_ready_and_rejected_transitions_preserve_swap_family(self):
        state = TransferRuntimeState()
        proposal = TransferProposal(
            target_player_id=100,
            buying_club_id=1,
            exchange_player_ids=(200, -1, -1),
        )
        state.submit_proposal(
            proposal,
            selling_club_id=2,
            current_date=date(2000, 9, 1),
        )
        deal = state.deals[100]

        deal.mark_player_rejected()
        self.assertEqual(
            deal.state,
            DEAL_PLAYER_REJECTED + DEAL_SWAP_OFFSET,
        )
        self.assertTrue(deal.player_rejected)
        deal.mark_ready()
        self.assertEqual(deal.state, DEAL_READY + DEAL_SWAP_OFFSET)
        self.assertTrue(deal.ready_for_execution)

    def test_movement_sentinels_match_free_and_bosman_records(self):
        free = PlayerMovement(10, 1, 2, 1, date(2000, 9, 1))
        bosman = PlayerMovement(11, 1, 2, 2, date(2000, 9, 1))
        fee = PlayerMovement(12, 1, 2, 500_000, date(2000, 9, 1))

        self.assertTrue(free.is_free_transfer)
        self.assertFalse(free.is_bosman)
        self.assertTrue(bosman.is_bosman)
        self.assertFalse(bosman.is_free_transfer)
        self.assertFalse(fee.is_free_transfer)
        self.assertFalse(fee.is_bosman)


if __name__ == "__main__":
    unittest.main()
