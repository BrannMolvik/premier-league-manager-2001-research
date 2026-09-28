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
    def test_corrected_day12_slot3_value_branch_reproduces_1290(self):
        rng = ScriptedRng([225])

        value = concession_candidate_value(
            rng,
            club_metric=38500,
            access_metric=80000,
            stadium_total=62,
            adjustment_percent=20.0,
        )

        self.assertEqual(value, 1290)
        self.assertEqual(rng.calls, [800])

    def test_corrected_day12_slot3_selects_candidate_19(self):
        sequence = [
            9, 10, 9, 15, 13, 21, 11, 8, 21, 10, 2, 10,
            6, 7, 20, 8, 1, 8, 7, 16, 13, 21, 7, 19,
        ]
        rng = ScriptedRng(sequence)

        selected, draws = select_fresh_concession_candidate(
            rng,
            capacity=20,
            candidate_value=1290,
        )

        self.assertEqual(selected, 19)
        self.assertEqual(draws, 24)
        self.assertEqual(rng.calls, [25] * 24)

    def test_candidate_19_local_range_consumes_rng1(self):
        rng = ScriptedRng([0])

        value, draws = choose_concession_local_value(rng, 19)

        self.assertEqual(value, 3)
        self.assertEqual(draws, 1)
        self.assertEqual(rng.calls, [1])

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
