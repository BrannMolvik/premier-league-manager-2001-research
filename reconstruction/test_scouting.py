import unittest

from match_schedule import MsvcCrtRng
from scouting import (
    MAX_NUM_FOUND,
    MAX_NUM_USED1,
    MAX_NUM_USED2,
    SCOUT_ONE_AGE_BIAS,
    ScoutingReseedState,
    scouting_rank_score,
    primary_scouting_results,
    scouting_shuffle,
    secondary_scouting_results,
)


class ScoutingOrderingTests(unittest.TestCase):
    def test_scouting_tuning_defaults_match_executable(self):
        self.assertEqual(SCOUT_ONE_AGE_BIAS, 4)
        self.assertEqual(MAX_NUM_USED1, 80)
        self.assertEqual(MAX_NUM_USED2, 50)
        self.assertEqual(MAX_NUM_FOUND, 20)

    def test_exact_scouting_seed_xors_neutral_panel_fields(self):
        state = ScoutingReseedState(
            status_control_7738=1,
            status_control_76f8=2,
            status_control_76b8=3,
            value_high_64d0=123.9,
            value_low_64c8=-45.9,
            field_64e4=0x11223344,
            age_high_64dc=35,
            field_64e0=2,
            age_low_64d8=18,
            class_selector_64c0=3,
        )
        expected = 0
        for value in (1, 2, 3, 123, -45, 0x11223344, 35, 2, 18, 3, -1):
            expected ^= value & 0xFFFFFFFF
        self.assertEqual(state.exact_seed(-1), expected & 0xFFFFFFFF)

    def test_primary_scouting_shuffle_reseeds_instead_of_using_incoming_game_state(self):
        state = ScoutingReseedState(
            status_control_7738=1,
            value_high_64d0=1000.0,
            value_low_64c8=10.0,
            age_high_64dc=35,
            age_low_64d8=18,
            class_selector_64c0=2,
        )
        candidates = tuple(range(12))

        first = primary_scouting_results(candidates, state)
        second = primary_scouting_results(candidates, state)

        self.assertEqual(first, second)

        rng = MsvcCrtRng(state.exact_seed(-1))
        expected = list(candidates)
        for remaining in range(len(expected), 1, -1):
            selected = rng.randbelow(remaining)
            expected[selected], expected[remaining - 1] = (
                expected[remaining - 1],
                expected[selected],
            )
        self.assertEqual(first, tuple(expected))

    def test_plain_scouting_rank_uses_best_preferred_role_rating(self):
        skills = [128] * 17
        preferred = (1, 2, 3)
        plain = scouting_rank_score(skills, preferred, age=25, mode=16)
        from match_role_rating import best_preferred_role_rating
        self.assertEqual(
            plain,
            best_preferred_role_rating(skills, preferred),
        )

    def test_age_biased_scouting_rank_uses_exact_integer_factor(self):
        skills = [160] * 17
        preferred = (9, 10, 11)
        from match_role_rating import best_preferred_role_rating
        base = best_preferred_role_rating(skills, preferred)

        self.assertEqual(
            scouting_rank_score(skills, preferred, age=31, mode=5),
            base * 60 // 100,
        )
        self.assertEqual(
            scouting_rank_score(skills, preferred, age=36, mode=5),
            base * 80 // 100,
        )

    def test_skill_biased_scouting_rank_wraps_temporary_bytes_like_executable(self):
        skills = [250] * 17
        preferred = (9, 10, 11)
        transformed = list(skills)
        for slot, percent in ((1, 120), (2, 130), (3, 120), (9, 120)):
            transformed[slot] = (transformed[slot] * percent // 100) & 0xFF

        from match_role_rating import best_preferred_role_rating
        self.assertEqual(
            scouting_rank_score(skills, preferred, age=25, mode=15),
            best_preferred_role_rating(transformed, preferred),
        )
        self.assertEqual(skills, [250] * 17)

    def test_unhandled_scouting_mode_does_not_append_score(self):
        self.assertIsNone(
            scouting_rank_score([128] * 17, (1, 2, 3), age=25, mode=7)
        )

    def test_secondary_scouting_applies_used_and_found_caps_around_shuffle(self):
        state = ScoutingReseedState(field_64e4=9, age_low_64d8=16)
        ranked = tuple(range(100))

        result = secondary_scouting_results(
            ranked,
            state,
            caller_argument=7,
        )

        self.assertEqual(len(result), 20)
        self.assertTrue(set(result).issubset(set(range(50))))
        self.assertEqual(
            result,
            scouting_shuffle(range(50), state, caller_argument=7)[:20],
        )


if __name__ == "__main__":
    unittest.main()
