import unittest

from match_calculator import (
    FORM_MULTIPLIERS,
    MatchSkillPlayer,
    PositionRole,
    effective_match_skill,
    position_compatibility_multiplier,
    resolve_penalty,
)
from match_events import ChanceOutcome, ChanceSource


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
            raise AssertionError(f"scripted value {value} outside RNG({bound})")
        return value


class PositionCompatibilityTests(unittest.TestCase):
    def test_static_position_codes_match_known_roles(self):
        self.assertEqual(int(PositionRole.GOALKEEPER), 1)
        self.assertEqual(int(PositionRole.CENTRE_BACK), 4)
        self.assertEqual(int(PositionRole.CENTRE_MIDFIELD), 12)
        self.assertEqual(int(PositionRole.CENTRE_FORWARD), 18)
        self.assertEqual(int(PositionRole.STRIKER), 19)

    def test_exact_position_is_full_strength(self):
        self.assertEqual(position_compatibility_multiplier(19, (19, 18, 14)), 1.0)

    def test_goalkeeper_out_of_position_floor(self):
        self.assertEqual(position_compatibility_multiplier(1, (19, 18, 14)), 0.10)

    def test_defensive_fallbacks(self):
        self.assertEqual(position_compatibility_multiplier(2, (6, 0, 0)), 0.90)
        self.assertEqual(position_compatibility_multiplier(2, (3, 0, 0)), 0.75)
        self.assertEqual(position_compatibility_multiplier(4, (5, 0, 0)), 0.90)

    def test_midfield_and_forward_fallbacks(self):
        self.assertEqual(position_compatibility_multiplier(10, (13, 0, 0)), 0.85)
        self.assertEqual(position_compatibility_multiplier(10, (11, 0, 0)), 0.70)
        self.assertEqual(position_compatibility_multiplier(12, (15, 0, 0)), 0.90)
        self.assertEqual(position_compatibility_multiplier(15, (18, 0, 0)), 0.75)
        self.assertEqual(position_compatibility_multiplier(18, (19, 0, 0)), 0.90)


class EffectiveSkillTests(unittest.TestCase):
    def test_form_modifiers_match_shipped_values(self):
        self.assertEqual(FORM_MULTIPLIERS, (0.90, 0.95, 1.00, 1.05, 1.10))

    def test_effective_skill_exact_position_normal_form(self):
        self.assertEqual(effective_match_skill(100, 100, 19, (19, 18, 14), 2), 9900)

    def test_effective_skill_truncates_after_each_multiplier(self):
        self.assertEqual(effective_match_skill(100, 100, 15, (18, 0, 0), 3), 7796)

    def test_minimum_override_forces_one(self):
        self.assertEqual(effective_match_skill(255, 255, 19, (19, 0, 0), 4, True), 1)


class PenaltyResolverTests(unittest.TestCase):
    def setUp(self):
        self.taker = MatchSkillPlayer(
            side=0,
            player_index=9,
            condition=100,
            form_state=2,
            current_position=19,
            preferred_positions=(19, 18, 14),
            shooting=100,
        )
        self.keeper = MatchSkillPlayer(
            side=1,
            player_index=0,
            condition=100,
            form_state=2,
            current_position=1,
            preferred_positions=(1, 0, 0),
            goalkeeping=100,
        )

    def test_explicit_miss_path_and_rng_order(self):
        rng = ScriptedRng([0, 255, 50])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.source, ChanceSource.PENALTY)
        self.assertEqual(event.outcome, ChanceOutcome.MISS)
        self.assertEqual(event.raw_outcome, 1)
        self.assertTrue(event.context_flag)
        self.assertEqual(rng.calls, [3, 256, 100])

    def test_saved_penalty_and_presentation_variant(self):
        rng = ScriptedRng([1, 0, 5])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.outcome, ChanceOutcome.SAVE)
        self.assertEqual(event.raw_outcome, 5)
        self.assertEqual(rng.calls, [3, 800, 100])

    def test_goal_path_and_rng_order(self):
        rng = ScriptedRng([1, 799, 0, 50])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.outcome, ChanceOutcome.GOAL)
        self.assertEqual(event.raw_outcome, 0)
        self.assertEqual(event.credited_side, 0)
        self.assertEqual(rng.calls, [3, 800, 10, 100])

    def test_goal_presentation_variant(self):
        rng = ScriptedRng([1, 799, 0, 9])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.raw_outcome, 3)
        self.assertTrue(event.presentation_variant)

    def test_score_suppression_can_emit_no_record(self):
        rng = ScriptedRng([1, 799, 0])
        event = resolve_penalty(self.taker, self.keeper, 10, rng)
        self.assertIsNone(event)
        self.assertEqual(rng.calls, [3, 800, 10])

    def test_score_nine_allows_only_roll_zero(self):
        rng = ScriptedRng([1, 799, 1])
        self.assertIsNone(resolve_penalty(self.taker, self.keeper, 9, rng))
        rng = ScriptedRng([1, 799, 0, 50])
        self.assertEqual(resolve_penalty(self.taker, self.keeper, 9, rng).outcome, ChanceOutcome.GOAL)


if __name__ == '__main__':
    unittest.main()
