import unittest
from datetime import date
from types import SimpleNamespace

from match_role_rating import best_preferred_role_rating
from transfer_decision import SellingClubDecision
from transfer_state import ContractTerms, TransferProposal, TransferRuntimeState
from transfer_workflow import (
    cash_only_proposal_total_value,
    evaluate_live_cash_bid,
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
