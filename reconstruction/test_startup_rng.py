import unittest
from dataclasses import dataclass

from startup_rng import (
    select_startup_youth_candidate,
    startup_youth_candidate_ids,
    startup_youth_target_count,
)


class RecordingRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError((value, bound))
        return value


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    initial_flags: int = 0


class StartupYouthRngTests(unittest.TestCase):
    def test_option_target_count_preserves_exact_bounds_and_offsets(self):
        rng = RecordingRng([1, 0, 2])
        self.assertEqual(startup_youth_target_count(0, rng), 5)
        self.assertEqual(startup_youth_target_count(1, rng), 5)
        self.assertEqual(startup_youth_target_count(2, rng), 8)
        self.assertEqual(rng.calls, [2, 2, 3])

    def test_missing_or_unknown_option_consumes_no_rng(self):
        class NoRng:
            def randbelow(self, bound):
                raise AssertionError(f"unexpected RNG({bound})")
        rng = NoRng()
        self.assertEqual(startup_youth_target_count(None, rng), 4)
        self.assertEqual(startup_youth_target_count(99, rng), 4)

    def test_candidate_scan_uses_club_and_bit_three_in_source_order(self):
        players = (
            Player(7, 50, 0),
            Player(8, 50, 0x08),
            Player(9, 49, 0),
            Player(10, 50, 0x10),
        )
        self.assertEqual(startup_youth_candidate_ids(players, 50), (7, 10))

    def test_selection_uses_current_count_then_swap_deletes(self):
        candidates = [10, 20, 30, 40]
        rng = RecordingRng([1, 1])
        self.assertEqual(select_startup_youth_candidate(candidates, rng), 20)
        self.assertEqual(candidates, [10, 40, 30])
        self.assertEqual(select_startup_youth_candidate(candidates, rng), 40)
        self.assertEqual(candidates, [10, 30])
        self.assertEqual(rng.calls, [4, 3])


if __name__ == "__main__":
    unittest.main()
