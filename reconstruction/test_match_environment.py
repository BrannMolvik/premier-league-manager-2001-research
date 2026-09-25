import unittest
from datetime import date

from match_environment import (
    MAX_PITCH_WEAR,
    MatchEnvironment,
    generate_match_environment,
    pitch_wear_after_match,
    recover_ai_pitch_wear,
    weekday_evening_flag,
)


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError(f"{value} outside RNG({bound})")
        return value


class MatchEnvironmentTests(unittest.TestCase):
    def test_weekend_and_weekday_match_flag(self):
        self.assertFalse(weekday_evening_flag(date(2000, 8, 19)))  # Saturday
        self.assertTrue(weekday_evening_flag(date(2000, 8, 23)))   # Wednesday

    def test_summer_hot_branch_consumes_only_temperature_rng(self):
        # July base 30, weekend, RNG(6)=3 -> 30C, therefore weather code 1.
        rng = ScriptedRng([3])
        env = generate_match_environment(date(2000, 7, 1), rng)
        self.assertEqual(env, MatchEnvironment(30, 1, False))
        self.assertEqual(rng.calls, [6])

    def test_midrange_weather_roll_maps_zero_to_rain(self):
        # October base 15, weekend, RNG(6)=3 -> 15C.
        rng = ScriptedRng([3, 0])
        env = generate_match_environment(date(2000, 10, 7), rng)
        self.assertEqual(env.temperature_c, 15)
        self.assertEqual(env.weather_code, 2)
        self.assertTrue(env.raining)
        self.assertEqual(rng.calls, [6, 4])

        rng = ScriptedRng([3, 1])
        env = generate_match_environment(date(2000, 10, 7), rng)
        self.assertEqual(env.weather_code, 0)
        self.assertEqual(rng.calls, [6, 4])

    def test_freezing_branch_uses_two_way_weather_roll(self):
        # January base 0, weekend, RNG(6)=3 -> 0C.
        self.assertEqual(
            generate_match_environment(
                date(2001, 1, 6),
                ScriptedRng([3, 0]),
            ).weather_code,
            4,
        )
        self.assertEqual(
            generate_match_environment(
                date(2001, 1, 6),
                ScriptedRng([3, 1]),
            ).weather_code,
            3,
        )

    def test_weekday_evening_subtracts_five_before_randomization(self):
        # October Wednesday: 15 - 5 + (3-3) = 10.
        env = generate_match_environment(
            date(2000, 10, 11),
            ScriptedRng([3, 1]),
        )
        self.assertEqual(env.temperature_c, 10)
        self.assertTrue(env.weekday_evening)

    def test_pitch_wear_increment_and_daily_recovery(self):
        self.assertEqual(pitch_wear_after_match(0, 0), 16)
        self.assertEqual(pitch_wear_after_match(0, 2), 32)
        self.assertEqual(pitch_wear_after_match(185, 0), MAX_PITCH_WEAR)
        self.assertEqual(pitch_wear_after_match(175, 2), MAX_PITCH_WEAR)

        self.assertEqual(recover_ai_pitch_wear(0), 0)
        self.assertEqual(recover_ai_pitch_wear(1), 0)
        self.assertEqual(recover_ai_pitch_wear(2), 0)
        self.assertEqual(recover_ai_pitch_wear(16), 14)


if __name__ == "__main__":
    unittest.main()
