import unittest

from concession_offer import (
    choose_concession_local_value,
    concession_candidate_value,
    select_fresh_concession_candidate,
)


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(int(bound))
        if not self.values:
            raise AssertionError("unexpected RNG draw")
        value = int(self.values.pop(0))
        if not 0 <= value < int(bound):
            raise AssertionError((value, bound))
        return value


class ConcessionOfferTests(unittest.TestCase):
    def test_arsenal_day12_value_branch_reproduces_1510(self):
        rng = ScriptedRng([409])

        value = concession_candidate_value(
            rng,
            club_metric=38500,
            access_metric=80000,
            stadium_total=62,
            adjustment_percent=20.0,
        )

        self.assertEqual(value, 1510)
        self.assertEqual(rng.calls, [800])

    def test_day12_slot7_selects_candidate_8_on_fourth_attempt(self):
        rng = ScriptedRng([24, 12, 2, 8])

        selected, draws = select_fresh_concession_candidate(
            rng,
            capacity=14,
            candidate_value=1510,
        )

        self.assertEqual(selected, 8)
        self.assertEqual(draws, 4)
        self.assertEqual(rng.calls, [25, 25, 25, 25])

    def test_candidate_8_local_value_is_fixed_and_rng_clean(self):
        rng = ScriptedRng([])

        value, draws = choose_concession_local_value(rng, 8)

        self.assertEqual(value, 3)
        self.assertEqual(draws, 0)
        self.assertEqual(rng.calls, [])

    def test_selector_stops_after_25_rejections(self):
        rng = ScriptedRng([0] * 25)

        selected, draws = select_fresh_concession_candidate(
            rng,
            capacity=60,
            candidate_value=2000,
        )

        self.assertIsNone(selected)
        self.assertEqual(draws, 25)
        self.assertEqual(rng.calls, [25] * 25)


if __name__ == "__main__":
    unittest.main()
