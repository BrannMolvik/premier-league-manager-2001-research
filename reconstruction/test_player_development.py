import unittest

from player_development import (
    DevelopmentState,
    PeakAges,
    TRAINING_PROFILES,
    active_training_step,
    apply_monthly_training_modifier,
    choose_peak_age,
    development_value,
    displayed_skill,
    enforce_minimum_display_rating,
    recalculate_monthly_skills,
    reverse_training_step,
    training_quality_multiplier,
    training_roll_succeeds,
    training_success_threshold,
)


class DevelopmentTests(unittest.TestCase):
    def test_display_conversion_and_floor(self):
        self.assertEqual(displayed_skill(0), 0)
        self.assertEqual(displayed_skill(9), 1)
        self.assertEqual(displayed_skill(255), 30)
        self.assertEqual(enforce_minimum_display_rating(0), 9)
        self.assertEqual(enforce_minimum_display_rating(9), 9)

    def test_forward_curve_hits_baseline_target_and_plateau(self):
        self.assertEqual(development_value(20, 20, 100, 180, 28), 100)
        self.assertEqual(development_value(28, 20, 100, 180, 28), 180)
        self.assertEqual(development_value(33, 20, 100, 180, 28), 180)
        self.assertEqual(development_value(34, 20, 100, 180, 28), int(180 * 26 / 32))

    def test_backward_reconstruction_before_baseline(self):
        self.assertEqual(development_value(15, 20, 100, 180, 28), 75)

    def test_baseline_already_past_peak(self):
        self.assertEqual(development_value(28, 32, 140, 180, 28), 180)
        self.assertEqual(development_value(32, 32, 140, 180, 28), 140)
        self.assertEqual(development_value(40, 32, 140, 180, 28), int(140 * 20 / 28))

    def test_peak_grouping(self):
        peaks = PeakAges(25, 28, 31)
        self.assertEqual([peaks.for_skill(i) for i in range(17)], [25]*5 + [28]*4 + [31]*8)

    def test_monthly_training_modifier_preserves_original_overshoot_quirk(self):
        self.assertEqual(apply_monthly_training_modifier(100, 130, 10), 110)
        self.assertEqual(apply_monthly_training_modifier(125, 130, 10), 120)

    def test_full_monthly_recalculation(self):
        state = DevelopmentState(
            baseline_age=20,
            baseline_raw=(100,) * 17,
            target_raw=(180,) * 17,
            peak_ages=PeakAges(25, 28, 31),
        )
        out = recalculate_monthly_skills(20, state)
        self.assertEqual(out, (100,) * 17)


class TrainingTests(unittest.TestCase):
    def test_exact_profiles(self):
        self.assertEqual(len(TRAINING_PROFILES), 7)
        self.assertTrue(all(len(p) == 17 for p in TRAINING_PROFILES))
        self.assertEqual(TRAINING_PROFILES[0], (0,) * 17)
        self.assertEqual(TRAINING_PROFILES[1][6], 25)
        self.assertEqual(TRAINING_PROFILES[3][11], 12)
        self.assertEqual(TRAINING_PROFILES[5][3], 9)
        self.assertEqual(TRAINING_PROFILES[6][15], 13)

    def test_quality_multiplier(self):
        self.assertEqual(training_quality_multiplier(), 1.0)
        self.assertEqual(training_quality_multiplier(assistant_manager_present=True), 1.25)
        self.assertEqual(training_quality_multiplier(5), 1.45)
        self.assertEqual(training_quality_multiplier(5, training_centre_present=True), 1.70)

    def test_training_threshold_and_strict_roll(self):
        self.assertEqual(training_success_threshold(25, 1.0), 12.5)
        self.assertTrue(training_roll_succeeds(25, 1.0, 12))
        self.assertFalse(training_roll_succeeds(25, 1.0, 13))

    def test_active_step_is_strictly_below_target(self):
        self.assertEqual(active_training_step(100, 120), 108)
        self.assertEqual(active_training_step(112, 120), 112)
        self.assertEqual(active_training_step(248, 255), 248)

    def test_reverse_step(self):
        self.assertEqual(reverse_training_step(40), 32)
        self.assertEqual(reverse_training_step(8), 8)

    def test_peak_selection_is_high_exclusive_and_avoids_current_age(self):
        self.assertEqual(choose_peak_age(20, 25, 26, lambda n: 0), 25)
        self.assertEqual(choose_peak_age(27, 27, 29, lambda n: 0), 28)


if __name__ == '__main__':
    unittest.main()
