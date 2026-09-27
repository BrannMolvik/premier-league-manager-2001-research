import unittest
from dataclasses import dataclass

from player_valuation import (
    access_financial_base_value,
    player_transfer_value,
    recent_rating_value_multiplier,
)


@dataclass(frozen=True)
class Row:
    field_08: int
    field_0c: int


class PlayerValuationTests(unittest.TestCase):
    def test_423980_base_uses_half_of_second_field(self):
        self.assertEqual(access_financial_base_value(Row(1000, 501)), 1250)

    def test_shipped_position_and_division_multipliers(self):
        # Adult EU-club defender, division category 0:
        # 1000 * DIV1(2.0) * DEFVALUE(1.05)
        value = player_transfer_value(
            Row(1000, 0),
            position_group=0,
            age=25,
            division_category=0,
            club_country_eu_status_flag=1,
        )
        self.assertEqual(value, 2100.0)

    def test_young_and_old_boundaries_are_strict(self):
        base = Row(1000, 0)
        age17 = player_transfer_value(
            base,
            position_group=2,
            age=17,
            division_category=5,
            club_country_eu_status_flag=1,
        )
        age18 = player_transfer_value(
            base,
            position_group=2,
            age=18,
            division_category=5,
            club_country_eu_status_flag=1,
        )
        age31 = player_transfer_value(
            base,
            position_group=2,
            age=31,
            division_category=5,
            club_country_eu_status_flag=1,
        )
        age32 = player_transfer_value(
            base,
            position_group=2,
            age=32,
            division_category=5,
            club_country_eu_status_flag=1,
        )
        self.assertAlmostEqual(age17, 1000 * 0.75 * 1.10 * 1.20)
        self.assertAlmostEqual(age18, 1000 * 1.10 * 1.20)
        self.assertAlmostEqual(age31, 1000 * 1.10 * 1.20)
        self.assertAlmostEqual(age32, 1000 * 0.60 * 1.10 * 1.20)

    def test_non_eu_club_country_fee_factor_is_seventy_percent(self):
        eu = player_transfer_value(
            Row(1000, 0),
            position_group=1,
            age=25,
            division_category=2,
            club_country_eu_status_flag=1,
        )
        non_eu = player_transfer_value(
            Row(1000, 0),
            position_group=1,
            age=25,
            division_category=2,
            club_country_eu_status_flag=0,
        )
        self.assertAlmostEqual(non_eu, eu * 0.70)

    def test_recent_rating_piecewise_multiplier(self):
        self.assertEqual(recent_rating_value_multiplier([7]), 1.0)
        self.assertAlmostEqual(recent_rating_value_multiplier([6]), 0.9)
        self.assertAlmostEqual(recent_rating_value_multiplier([5]), 0.8)
        self.assertAlmostEqual(recent_rating_value_multiplier([8]), 1.2)
        self.assertAlmostEqual(recent_rating_value_multiplier([9]), 1.4)
        self.assertEqual(recent_rating_value_multiplier([]), 1.0)

    def test_recent_rating_is_not_applied_until_sixth_appearance_counter_state(self):
        without = player_transfer_value(
            Row(1000, 0),
            position_group=0,
            age=25,
            division_category=0,
            club_country_eu_status_flag=1,
            appearance_count=4,
            recent_ratings=[5, 5, 5, 5],
        )
        with_adjustment = player_transfer_value(
            Row(1000, 0),
            position_group=0,
            age=25,
            division_category=0,
            club_country_eu_status_flag=1,
            appearance_count=5,
            recent_ratings=[5, 5, 5, 5, 5],
        )
        self.assertAlmostEqual(without, 2100.0)
        self.assertAlmostEqual(with_adjustment, 1680.0)

    def test_rating_history_is_limited_to_six_entries(self):
        with self.assertRaisesRegex(ValueError, "at most six"):
            recent_rating_value_multiplier([7] * 7)


if __name__ == "__main__":
    unittest.main()
