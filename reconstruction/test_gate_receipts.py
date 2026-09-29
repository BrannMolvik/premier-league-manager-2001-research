import unittest

from gate_receipts import (
    FRESH_CONTROLLED_FACILITY_FACTOR,
    PREMIER_LEAGUE_SEATING_REFERENCE,
    PREMIER_LEAGUE_TERRACE_REFERENCE,
    PREMIER_LEAGUE_TIER_FACTOR,
    calculate_gate_cell,
    calculate_matchday_gate_receipts,
    capped_gate_demand,
    first_xi_rating_factor,
    league_end_play_factor,
    league_importance_factor,
    league_position_factor,
    ordinary_league_side_modifier,
    randomized_gate_count,
    signed_trunc_division,
    ticket_price_response,
    cup_round_attendance_modifier,
    fan_factor_for_root_competition_index,
)


class CupGatePrimitiveTests(unittest.TestCase):
    def test_fan_factor_uses_exact_root_index_table(self):
        self.assertEqual(
            tuple(fan_factor_for_root_competition_index(i) for i in range(7)),
            (0.9, 0.8, 0.7, 0.6, 0.5, 0.5, 0.5),
        )

    def test_cup_round_modifier_matches_shipped_tuning(self):
        total = 8
        self.assertEqual(
            cup_round_attendance_modifier(
                total_round_count=total,
                zero_based_round_index=7,
            ),
            3.0,
        )
        self.assertEqual(
            cup_round_attendance_modifier(
                total_round_count=total,
                zero_based_round_index=6,
            ),
            2.0,
        )
        self.assertEqual(
            cup_round_attendance_modifier(
                total_round_count=total,
                zero_based_round_index=5,
            ),
            1.5,
        )
        self.assertEqual(
            cup_round_attendance_modifier(
                total_round_count=total,
                zero_based_round_index=4,
            ),
            1.4,
        )
        self.assertEqual(
            cup_round_attendance_modifier(
                total_round_count=total,
                zero_based_round_index=0,
            ),
            1.4,
        )

    def test_cup_round_modifier_rejects_invalid_runtime_index(self):
        with self.assertRaises(ValueError):
            cup_round_attendance_modifier(
                total_round_count=8,
                zero_based_round_index=8,
            )


class GateLiveInputTests(unittest.TestCase):
    def test_premier_league_source_constants(self):
        self.assertEqual(PREMIER_LEAGUE_TIER_FACTOR, 0.5)
        self.assertEqual(PREMIER_LEAGUE_SEATING_REFERENCE, 30.0)
        self.assertEqual(PREMIER_LEAGUE_TERRACE_REFERENCE, 22.5)
        self.assertEqual(FRESH_CONTROLLED_FACILITY_FACTOR, 0.9)

    def test_signed_division_and_importance_preserve_integer_step(self):
        self.assertEqual(signed_trunc_division(-10, 3), -3)
        self.assertEqual(signed_trunc_division(10, 3), 3)
        self.assertEqual(
            league_importance_factor(
                current_runtime_order=-7,
                first_runtime_order=-12,
                competition_count=11,
            ),
            1.0,
        )
        self.assertEqual(
            league_importance_factor(
                current_runtime_order=10,
                first_runtime_order=-12,
                competition_count=11,
            ),
            3.0,
        )

    def test_position_factor_uses_original_early_and_final_match_neutral_bands(self):
        self.assertEqual(
            league_position_factor(
                table_index=9, team_count=20, games_played=4, games_remaining=34
            ),
            1.0,
        )
        self.assertEqual(
            league_position_factor(
                table_index=9, team_count=20, games_played=35, games_remaining=3
            ),
            1.0,
        )
        self.assertAlmostEqual(
            league_position_factor(
                table_index=9, team_count=20, games_played=20, games_remaining=18
            ),
            0.55,
        )

    def test_end_play_uses_first_positive_reachable_objective(self):
        self.assertEqual(
            league_end_play_factor(
                games_remaining=4,
                objective_gaps=(
                    (True, 13, 1.0),
                    (True, 8, 0.3),
                ),
            ),
            0.3,
        )
        self.assertEqual(
            league_end_play_factor(
                games_remaining=4,
                objective_gaps=(
                    (True, 12, 1.0),
                    (True, 8, 0.3),
                ),
            ),
            1.0,
        )
        self.assertEqual(
            league_end_play_factor(
                games_remaining=5,
                objective_gaps=((True, 1, 1.0),),
            ),
            0.0,
        )

    def test_first_xi_and_weighted_side_modifier(self):
        ratings = (80,) * 11
        self.assertAlmostEqual(first_xi_rating_factor(ratings), 1.1)
        self.assertAlmostEqual(
            ordinary_league_side_modifier(
                first_xi_ratings=ratings,
                end_play_factor=0.0,
                position_factor=0.75,
                importance_factor=1.0,
            ),
            (1.1 + 0.0 + 0.75 + 1.0) / 4.0,
        )


class TicketPriceResponseTests(unittest.TestCase):
    def test_piecewise_boundaries_preserve_original_discontinuities(self):
        ref = 100.0
        self.assertEqual(ticket_price_response(101, ref), 0.1)
        self.assertEqual(ticket_price_response(100, ref), 0.1)
        self.assertAlmostEqual(ticket_price_response(50, ref), 0.5)
        self.assertEqual(ticket_price_response(0, ref), 1.0)
        self.assertAlmostEqual(ticket_price_response(-49, ref), 1.245)
        self.assertAlmostEqual(ticket_price_response(-50, ref), 1.625)
        self.assertAlmostEqual(ticket_price_response(-99, ref), 1.7475)
        self.assertEqual(ticket_price_response(-100, ref), 2.0)

    def test_nonpositive_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            ticket_price_response(0, 0)


class GateDemandTests(unittest.TestCase):
    def test_ordinary_demand_caps_first_to_fan_base_then_capacity(self):
        # Raw expression is much larger than both caps.
        self.assertEqual(
            capped_gate_demand(
                fan_base_raw=10000,
                tier_factor=0.9,
                side_modifier=2.0,
                price_response=2.0,
                capacity=8000,
            ),
            8000.0,
        )

    def test_cup_special_skips_fan_base_cap_but_keeps_capacity_cap(self):
        self.assertAlmostEqual(
            capped_gate_demand(
                fan_base_raw=1000,
                tier_factor=0.9,
                side_modifier=2.0,
                price_response=2.0,
                capacity=5000,
                cup_special=True,
            ),
            3960.0,
        )

    def test_controlled_facility_factor_is_multiplicative(self):
        base = capped_gate_demand(
            fan_base_raw=10000,
            tier_factor=0.5,
            side_modifier=0.5,
            price_response=1.0,
            capacity=10000,
        )
        adjusted = capped_gate_demand(
            fan_base_raw=10000,
            tier_factor=0.5,
            side_modifier=0.5,
            price_response=1.0,
            capacity=10000,
            facility_factor=0.9,
        )
        self.assertAlmostEqual(adjusted, base * 0.9)


class RandomizedGateCountTests(unittest.TestCase):
    def test_response_at_or_below_one_uses_one_percent_span(self):
        result = randomized_gate_count(1234.9, 1.0, 0x7FFF)
        self.assertEqual(result.random_span, 12)
        self.assertEqual(result.count, 1223)

    def test_response_above_one_uses_recovered_denominator(self):
        # 5500 / (100 + 1000*0.5) = 9.166.. -> trunc 9.
        result = randomized_gate_count(5500.9, 1.5, 16384)
        self.assertEqual(result.random_span, 9)
        self.assertEqual(result.count, 5496)

    def test_span_has_minimum_one(self):
        result = randomized_gate_count(10.9, 1.0, 0x7FFF)
        self.assertEqual(result.random_span, 1)
        self.assertEqual(result.count, 10)

    def test_integrated_cell_preserves_price_response_and_capacity(self):
        result = calculate_gate_cell(
            fan_base_raw=10000,
            tier_factor=0.9,
            side_modifier=1.0,
            price_delta=0,
            reference_price=20,
            capacity=5000,
            rand15=0,
        )
        self.assertEqual(result.price_response, 1.0)
        self.assertEqual(result.demand, 5000.0)
        self.assertEqual(result.count, 5000)


class MatchdayGateReceiptTests(unittest.TestCase):
    def test_four_cell_order_revenue_and_season_ticket_attendance(self):
        result = calculate_matchday_gate_receipts(
            home_fan_base_raw=10000,
            visiting_fan_base_raw=10000,
            home_tier_factor=1.0,
            visiting_tier_factor=1.0,
            home_side_modifier=1.0,
            visiting_side_modifier=1.0,
            seating_reference=30.0,
            terrace_reference=22.5,
            home_seating_price_delta=0.0,
            visiting_seating_price_delta=0.0,
            home_terrace_price_delta=0.0,
            visiting_terrace_price_delta=0.0,
            home_seating_capacity=1000,
            visiting_seating_capacity=800,
            home_terrace_capacity=500,
            visiting_terrace_capacity=200,
            host_seating_price=30,
            host_terrace_price=22,
            rand15_values=(0, 0, 0, 0),
            season_ticket_quantity=100,
        )
        self.assertEqual(result.home_seating.count, 1000)
        self.assertEqual(result.visiting_seating.count, 800)
        self.assertEqual(result.home_terrace.count, 500)
        self.assertEqual(result.visiting_terrace.count, 200)
        self.assertEqual(result.home_revenue, 41000)
        self.assertEqual(result.visiting_revenue, 28400)
        self.assertEqual(result.ordinary_home_attendance, 1500)
        self.assertEqual(result.home_attendance, 1600)
        self.assertEqual(result.visiting_attendance, 1000)
        self.assertEqual(result.total_attendance, 2600)

    def test_four_rand_values_are_consumed_by_documented_cell_order(self):
        result = calculate_matchday_gate_receipts(
            home_fan_base_raw=10000,
            visiting_fan_base_raw=10000,
            home_tier_factor=1.0,
            visiting_tier_factor=1.0,
            home_side_modifier=1.0,
            visiting_side_modifier=1.0,
            seating_reference=30.0,
            terrace_reference=22.5,
            home_seating_price_delta=0.0,
            visiting_seating_price_delta=0.0,
            home_terrace_price_delta=0.0,
            visiting_terrace_price_delta=0.0,
            home_seating_capacity=10000,
            visiting_seating_capacity=10000,
            home_terrace_capacity=10000,
            visiting_terrace_capacity=10000,
            host_seating_price=30,
            host_terrace_price=22,
            rand15_values=(0, 8192, 16384, 32767),
        )
        # Demand 10000 gives span 100. Subtractions are 0,25,50,99.
        self.assertEqual(result.home_seating.count, 10000)
        self.assertEqual(result.visiting_seating.count, 9975)
        self.assertEqual(result.home_terrace.count, 9950)
        self.assertEqual(result.visiting_terrace.count, 9901)


if __name__ == "__main__":
    unittest.main()
