import unittest

from match_role_rating import ROLE_SKILL_WEIGHTS, display_skill, role_rating


class RoleRatingTests(unittest.TestCase):
    def test_display_skill_uses_exact_30_over_255_conversion(self):
        self.assertEqual(display_skill(0), 0)
        self.assertEqual(display_skill(4), 0)
        self.assertEqual(display_skill(5), 1)
        self.assertEqual(display_skill(9), 1)
        self.assertEqual(display_skill(255), 30)

    def test_every_nonzero_role_weight_set_sums_to_3_3(self):
        for role, terms in ROLE_SKILL_WEIGHTS.items():
            with self.subTest(role=role):
                self.assertAlmostEqual(sum(weight for _, weight in terms), 3.3)

    def test_roles_16_and_17_take_zero_branch(self):
        skills = (255,) * 17
        preferred = (16, 17, 18)
        self.assertEqual(role_rating(skills, 16, preferred), 0)
        self.assertEqual(role_rating(skills, 17, preferred), 0)

    def test_maximum_preferred_goalkeeper_caps_at_99(self):
        self.assertEqual(
            role_rating((255,) * 17, 1, (1, 0, 0)),
            99,
        )

    def test_position_compatibility_is_applied_after_weighted_sum(self):
        skills = (128,) * 17
        preferred = (18, 19, 15)
        preferred_rating = role_rating(skills, 18, preferred)
        out_of_position_rating = role_rating(skills, 2, preferred)

        # Role 18 is directly preferred. Right back has no compatible preferred
        # role here and therefore receives the exact 0.50 compatibility factor.
        self.assertEqual(preferred_rating, 50)
        self.assertEqual(out_of_position_rating, 25)

    def test_invalid_skill_vector_is_rejected(self):
        with self.assertRaises(ValueError):
            role_rating((100,) * 16, 10, (10, 0, 0))


if __name__ == "__main__":
    unittest.main()
