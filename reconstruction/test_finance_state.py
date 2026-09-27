from datetime import date
import unittest
from types import SimpleNamespace

from game_state import GameCalendar, GameState
from finance_state import (
    BalanceRuntimeState,
    CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY,
    CREDIT_SECONDARY_DEBIT_RATE,
    FinancialObjectiveState,
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


class FinancialObjectiveStateTests(unittest.TestCase):
    def test_fresh_premier_league_candidates_use_recovered_rank_half(self):
        self.assertEqual(
            FinancialObjectiveState.premier_league_candidates(19, 20),
            (13, 1, 5),
        )
        self.assertEqual(
            FinancialObjectiveState.premier_league_candidates(9, 20),
            (1, 5, 6),
        )
        # The executable comparison is >=, so rank 10 is already high-half.
        self.assertEqual(
            FinancialObjectiveState.premier_league_candidates(10, 20),
            (13, 1, 5),
        )

    def test_selection_replaces_cash_from_exact_objective_percentages(self):
        objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        replacement = objective.select(0, date(2000, 8, 18))
        self.assertEqual(objective.selected_objective_id, 13)
        self.assertEqual(replacement, 47_600_000)
        self.assertEqual(objective.starting_funds_snapshot, 47_600_000)
        self.assertEqual(objective.target_cash, 51_800_000)
        self.assertEqual(objective.deadline, date(2003, 8, 18))
        self.assertTrue(objective.active)
        self.assertFalse(objective.progression_gate_reached)

    def test_deadline_threshold_is_strict_above_95_percent(self):
        objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        objective.select(0, date(2000, 8, 18))
        objective.progression_gate_reached = True

        self.assertIsNone(objective.evaluate(0, date(2002, 8, 18)))
        self.assertEqual(
            objective.evaluate(51_800_001, date(2003, 1, 1)).outcome,
            "success",
        )
        near = objective.evaluate(49_210_001, date(2003, 1, 1))
        self.assertEqual((near.outcome, near.sacking_reason), ("near_miss", None))
        dismissed = objective.evaluate(49_210_000, date(2003, 1, 1))
        self.assertEqual((dismissed.outcome, dismissed.sacking_reason), ("dismissed", 5))

    def test_deadline_without_progression_gate_uses_original_reason_four_branch(self):
        objective = FinancialObjectiveState(
            base_cash=28_000_000,
            candidate_ids=(13, 1, 5),
        )
        objective.select(0, date(2000, 8, 18))
        result = objective.evaluate(100_000_000, date(2003, 6, 1))
        self.assertEqual((result.outcome, result.sacking_reason), ("dismissed", 4))


class FinancialObjectiveGameStateTests(unittest.TestCase):
    def test_controlled_club_initialization_materializes_pl_candidates(self):
        clubs = {
            club_id: SimpleNamespace(
                starting_cash=28_000_000 if club_id == 0 else 1_000_000,
                fan_base_index=(31 if club_id == 0 else club_id),
            )
            for club_id in range(20)
        }
        state = GameState(
            calendar=GameCalendar(date(2000, 8, 18)),
            players={},
            clubs=clubs,
            premier_league=SimpleNamespace(club_ids=tuple(range(20))),
        )
        balance = state.initialize_controlled_club_balance(0)
        self.assertEqual(balance.current_cash, 28_000_000)
        self.assertEqual(state.financial_objective_candidates(0), (13, 1, 5))

        replacement = state.select_financial_objective(0, 0)
        self.assertEqual(replacement, 47_600_000)
        self.assertEqual(balance.current_cash, 47_600_000)

        state.calendar.current_date = date(2003, 1, 1)
        state.set_financial_objective_progression_gate(0)
        balance.current_cash = 49_210_000
        evaluation = state.evaluate_financial_objective(0)
        self.assertEqual(
            (evaluation.outcome, evaluation.sacking_reason),
            ("dismissed", 5),
        )


class PremierLeagueObjectiveProgressionTests(unittest.TestCase):
    @staticmethod
    def state_for(objective_id, table_index, *, complete=True):
        controlled_id = 100
        table = [SimpleNamespace(club_id=1000 + index) for index in range(20)]
        table[int(table_index)] = SimpleNamespace(club_id=controlled_id)
        league = SimpleNamespace(
            fixtures={0: object()},
            results=({0: object()} if complete else {}),
            table=lambda: tuple(table),
        )
        objective = FinancialObjectiveState(
            base_cash=1_000_000,
            candidate_ids=(13, 1, 5) if objective_id != 6 else (1, 5, 6),
        )
        candidate_index = objective.candidate_ids.index(objective_id)
        objective.select(candidate_index, date(2000, 8, 18))
        balance = BalanceRuntimeState(
            current_cash=objective.starting_funds,
            financial_objective=objective,
        )
        state = GameState(
            calendar=GameCalendar(date(2001, 5, 20)),
            players={},
            clubs={controlled_id: SimpleNamespace()},
            premier_league=league,
            finance_balances={controlled_id: balance},
            user_controlled_club_id=controlled_id,
        )
        return state, objective

    def test_id13_requires_champion(self):
        champion, objective = self.state_for(13, 0)
        self.assertIsNone(
            champion.run_premier_league_financial_objective_season_transition()
        )
        self.assertTrue(objective.progression_gate_reached)
        self.assertEqual(objective.progression_state, 1)

        runner_up, objective = self.state_for(13, 1)
        runner_up.run_premier_league_financial_objective_season_transition()
        self.assertFalse(objective.progression_gate_reached)
        self.assertEqual(objective.progression_state, 0)

    def test_id1_requires_top_two(self):
        second, objective = self.state_for(1, 1)
        second.run_premier_league_financial_objective_season_transition()
        self.assertTrue(objective.progression_gate_reached)

        third, objective = self.state_for(1, 2)
        third.run_premier_league_financial_objective_season_transition()
        self.assertFalse(objective.progression_gate_reached)

    def test_id5_preserves_inclusive_midpoint_quirk(self):
        eleventh, objective = self.state_for(5, 10)
        eleventh.run_premier_league_financial_objective_season_transition()
        self.assertTrue(objective.progression_gate_reached)

        twelfth, objective = self.state_for(5, 11)
        twelfth.run_premier_league_financial_objective_season_transition()
        self.assertFalse(objective.progression_gate_reached)

    def test_id6_succeeds_when_club_remains_in_current_pl_slice(self):
        state, objective = self.state_for(6, 19)
        state.run_premier_league_financial_objective_season_transition()
        self.assertTrue(objective.progression_gate_reached)
        self.assertEqual(objective.progression_state, 1)

    def test_progression_waits_for_completed_league(self):
        state, objective = self.state_for(13, 0, complete=False)
        self.assertIsNone(
            state.run_premier_league_financial_objective_season_transition()
        )
        self.assertFalse(objective.progression_gate_reached)

    def test_progression_skips_selection_year(self):
        state, objective = self.state_for(13, 0)
        state.calendar.current_date = date(2000, 12, 31)
        state.run_premier_league_financial_objective_season_transition()
        self.assertFalse(objective.progression_gate_reached)



    def test_deadline_dismissal_persists_reason_before_control_exit(self):
        state, objective = self.state_for(6, 19)
        state.calendar.current_date = date(2003, 5, 20)
        objective.selected_on = date(2000, 8, 18)
        objective.deadline = date(2003, 8, 18)
        objective.progression_gate_reached = True
        objective.progression_state = 1
        state.finance_balances[100].current_cash = objective.target_cash * 0.95

        evaluation = state.run_premier_league_financial_objective_season_transition()
        self.assertEqual((evaluation.outcome, evaluation.sacking_reason), ("dismissed", 5))
        self.assertEqual(state.user_sacking_reason, 5)
        self.assertEqual(state.user_controlled_club_id, 100)

        balance = state.finance_balances[100]
        self.assertEqual(state.finalize_single_user_sacking_control(), 5)
        self.assertIsNone(state.user_controlled_club_id)
        self.assertIs(state.finance_balances[100], balance)
        self.assertEqual(balance.financial_objective.selected_objective_id, 6)


if __name__ == "__main__":
    unittest.main()
