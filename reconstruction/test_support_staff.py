import unittest

from match_schedule import MsvcCrtRng
from support_staff import (
    SupportStaffState,
    generate_fresh_user_support_staff,
    initial_staff_rating_base,
    training_quality_multiplier,
)


class SupportStaffTrainingTests(unittest.TestCase):
    def test_initial_rating_tiers_match_4c9d40(self):
        self.assertEqual(
            [initial_staff_rating_base(value) for value in range(7)],
            [4, 3, 2, 1, 1, 1, 1],
        )

    def test_fresh_premier_league_staff_uses_exact_type_order_and_draws(self):
        rng = MsvcCrtRng(1)

        staff = generate_fresh_user_support_staff(rng, competition_context=6)

        self.assertEqual(
            [(item.staff_type, item.age_like, item.rating) for item in staff],
            [
                (1, 25, 2),
                (2, 29, 2),
                (3, 39, 1),
                (4, 33, 2),
                (5, 45, 2),
                (13, 29, 2),
            ],
        )
        self.assertEqual(rng.state, 0x6DF109FD)
        self.assertTrue(all(item.status == 1 for item in staff))

    def test_youth_coach_precedes_assistant_and_maps_rating_to_quality(self):
        staff = (
            SupportStaffState(2, 35, 5, 1),
            SupportStaffState(3, 40, 2, 1),
        )
        self.assertAlmostEqual(training_quality_multiplier(staff), 1.30)

    def test_status_two_forces_youth_rating_one(self):
        staff = (SupportStaffState(3, 40, 5, 2),)
        self.assertAlmostEqual(training_quality_multiplier(staff), 1.25)

    def test_assistant_fallback_and_training_centre_bonus(self):
        staff = (SupportStaffState(2, 35, 5, 1),)
        self.assertAlmostEqual(training_quality_multiplier(staff), 1.25)
        self.assertAlmostEqual(
            training_quality_multiplier(staff, has_training_centre=True),
            1.50,
        )

    def test_no_staff_is_neutral_before_facility_bonus(self):
        self.assertAlmostEqual(training_quality_multiplier(()), 1.0)
        self.assertAlmostEqual(
            training_quality_multiplier((), has_training_centre=True),
            1.25,
        )


if __name__ == "__main__":
    unittest.main()
