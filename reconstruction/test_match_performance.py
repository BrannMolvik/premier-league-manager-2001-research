import unittest

from match_performance import target_match_performance_rating


class ScriptedRng:
    def __init__(self, values=()):
        self.values = list(values)
        self.bounds = []

    def randbelow(self, bound: int) -> int:
        bound = int(bound)
        self.bounds.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected randbelow({bound})")
        value = int(self.values.pop(0))
        if not 0 <= value < bound:
            raise AssertionError(f"scripted value {value} outside bound {bound}")
        return value


class MatchPerformanceRatingTests(unittest.TestCase):
    def test_roles_8_to_15_win_bonus_uses_shared_crt_only(self):
        shared = ScriptedRng([1])
        engine = ScriptedRng()
        rating = target_match_performance_rating(
            current_role=10,
            own_score=2,
            opponent_score=0,
            primary_goal_count=0,
            secondary_goal_count=0,
            booked=False,
            sent_off=False,
            form_state=2,
            previous_rating=0,
            shared_rng=shared,
            match_engine_rng=engine,
        )
        self.assertEqual(rating, 7)
        self.assertEqual(shared.bounds, [2])
        self.assertEqual(engine.bounds, [])

    def test_roles_16_plus_opponent_penalty_then_separate_low_rating_lift(self):
        shared = ScriptedRng()
        engine = ScriptedRng([1])
        rating = target_match_performance_rating(
            current_role=17,
            own_score=0,
            opponent_score=4,
            primary_goal_count=0,
            secondary_goal_count=0,
            booked=False,
            sent_off=False,
            form_state=2,
            previous_rating=0,
            shared_rng=shared,
            match_engine_rng=engine,
        )
        self.assertEqual(rating, 6)
        self.assertEqual(shared.bounds, [])
        self.assertEqual(engine.bounds, [2])

    def test_roles_0_to_7_preserve_shared_rng_adjustment_order(self):
        shared = ScriptedRng([1, 0, 1, 1])
        engine = ScriptedRng()
        rating = target_match_performance_rating(
            current_role=4,
            own_score=0,
            opponent_score=2,
            primary_goal_count=3,
            secondary_goal_count=1,
            booked=True,
            sent_off=False,
            form_state=3,
            previous_rating=0,
            shared_rng=shared,
            match_engine_rng=engine,
        )
        self.assertEqual(rating, 9)
        self.assertEqual(shared.bounds, [2, 2, 2, 2])
        self.assertEqual(engine.bounds, [])

    def test_sent_off_suppresses_booking_random_draw(self):
        shared = ScriptedRng([0])
        engine = ScriptedRng()
        rating = target_match_performance_rating(
            current_role=4,
            own_score=0,
            opponent_score=0,
            primary_goal_count=0,
            secondary_goal_count=0,
            booked=True,
            sent_off=True,
            form_state=2,
            previous_rating=0,
            shared_rng=shared,
            match_engine_rng=engine,
        )
        self.assertEqual(rating, 6)
        self.assertEqual(shared.bounds, [2])

    def test_exact_ten_is_forced_to_nine_but_above_ten_caps_to_ten(self):
        exact_ten = target_match_performance_rating(
            current_role=4,
            own_score=0,
            opponent_score=0,
            primary_goal_count=4,
            secondary_goal_count=0,
            booked=False,
            sent_off=False,
            form_state=2,
            previous_rating=0,
            shared_rng=ScriptedRng([1]),
            match_engine_rng=ScriptedRng(),
        )
        above_ten = target_match_performance_rating(
            current_role=4,
            own_score=0,
            opponent_score=0,
            primary_goal_count=8,
            secondary_goal_count=0,
            booked=False,
            sent_off=False,
            form_state=2,
            previous_rating=0,
            shared_rng=ScriptedRng([1]),
            match_engine_rng=ScriptedRng(),
        )
        self.assertEqual(exact_ten, 9)
        self.assertEqual(above_ten, 10)

    def test_previous_history_clamps_change_to_one_point(self):
        high_previous = target_match_performance_rating(
            current_role=10,
            own_score=0,
            opponent_score=0,
            primary_goal_count=1,
            secondary_goal_count=0,
            booked=False,
            sent_off=False,
            form_state=2,
            previous_rating=10,
            shared_rng=ScriptedRng(),
            match_engine_rng=ScriptedRng(),
        )
        low_previous = target_match_performance_rating(
            current_role=10,
            own_score=0,
            opponent_score=0,
            primary_goal_count=1,
            secondary_goal_count=0,
            booked=False,
            sent_off=False,
            form_state=2,
            previous_rating=4,
            shared_rng=ScriptedRng(),
            match_engine_rng=ScriptedRng(),
        )
        self.assertEqual(high_previous, 9)
        self.assertEqual(low_previous, 7)


if __name__ == "__main__":
    unittest.main()
