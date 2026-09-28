import unittest

from commercial_timers import UserCommercialTimerState


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


class CommercialTimerTests(unittest.TestCase):
    def test_fresh_waits_match_recovered_bounds_and_day_one_counting(self):
        rng = ScriptedRng([4, 6])
        state = UserCommercialTimerState()

        draws, expired = state.run_daily(rng)

        self.assertEqual(draws, 2)
        self.assertFalse(expired)
        self.assertEqual(rng.calls, [14, 7])
        self.assertEqual(state.concession_wait_days, 11)
        self.assertEqual(state.concession_elapsed_days, 1)
        self.assertEqual(state.sponsor_wait_days, 13)
        self.assertEqual(state.sponsor_elapsed_days, 1)

        for _ in range(9):
            draws, expired = state.run_daily(rng)
            self.assertEqual(draws, 0)
            self.assertFalse(expired)

        self.assertEqual(state.concession_elapsed_days, 10)
        self.assertEqual(state.sponsor_elapsed_days, 10)

    def test_failed_concession_retries_next_day_and_success_resets(self):
        rng = ScriptedRng([4, 6, 2, 6])
        state = UserCommercialTimerState()
        state.run_daily(rng)
        attempts = []

        def attempt(_rng):
            attempts.append(len(attempts) + 1)
            return len(attempts) >= 2

        for _ in range(9):
            state.run_daily(rng, concession_attempt=attempt)

        draws, expired = state.run_daily(rng, concession_attempt=attempt)
        self.assertEqual(draws, 0)
        self.assertTrue(expired)
        self.assertEqual(attempts, [1])
        self.assertEqual(state.concession_wait_days, 11)

        draws, expired = state.run_daily(rng, concession_attempt=attempt)
        self.assertEqual(draws, 0)
        self.assertFalse(expired)
        self.assertEqual(attempts, [1, 2])
        self.assertEqual(state.concession_wait_days, 0)
        self.assertEqual(state.sponsor_elapsed_days, 12)

        draws, expired = state.run_daily(rng, concession_attempt=attempt)
        self.assertEqual(draws, 1)
        self.assertFalse(expired)
        self.assertEqual(state.concession_wait_days, 9)
        self.assertEqual(state.concession_elapsed_days, 1)
        self.assertEqual(state.sponsor_wait_days, 0)

        draws, expired = state.run_daily(rng, concession_attempt=attempt)
        self.assertEqual(draws, 1)
        self.assertFalse(expired)
        self.assertEqual(state.sponsor_wait_days, 13)
        self.assertEqual(state.sponsor_elapsed_days, 1)
        self.assertEqual(rng.calls, [14, 7, 14, 7])

    def test_expired_concession_without_offer_body_does_not_invent_rng(self):
        rng = ScriptedRng([4, 6])
        state = UserCommercialTimerState()
        state.run_daily(rng)

        for _ in range(10):
            draws, expired = state.run_daily(rng)

        self.assertEqual(draws, 0)
        self.assertTrue(expired)
        self.assertEqual(rng.calls, [14, 7])
        self.assertEqual(state.concession_wait_days, 11)


if __name__ == "__main__":
    unittest.main()
