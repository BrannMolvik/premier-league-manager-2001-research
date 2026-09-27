import unittest

from gate_receipts import (
    calculate_gate_cell,
    calculate_matchday_gate_receipts,
    capped_gate_demand,
    randomized_gate_count,
    ticket_price_response,
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
