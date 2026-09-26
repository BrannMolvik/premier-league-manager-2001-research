import unittest

from match_schedule import MsvcCrtRng
from procedural_league import generate_procedural_league_round_robin


class ZeroRng:
    def __init__(self):
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(int(bound))
        return 0


class ProceduralLeagueRoundRobinTests(unittest.TestCase):
    def test_four_team_zero_rng_matches_legacy_recursive_order(self):
        rng = ZeroRng()

        replay = generate_procedural_league_round_robin((0, 1, 2, 3), rng)

        self.assertEqual(
            replay.bounds,
            (3, 1, 2, 1, 1, 1),
        )
        self.assertEqual(
            replay.rounds,
            (
                ((3, 2), (1, 0)),
                ((1, 2), (0, 3)),
                ((0, 2), (1, 3)),
            ),
        )

    def test_fixed_msvc_seed_locks_bounds_pairs_and_state(self):
        rng = MsvcCrtRng(0x12345678)

        replay = generate_procedural_league_round_robin((0, 1, 2, 3), rng)

        self.assertEqual(replay.bounds, (3, 1, 2, 1, 1, 1))
        self.assertEqual(
            replay.rounds,
            (
                ((3, 1), (2, 0)),
                ((0, 1), (2, 3)),
                ((2, 1), (0, 3)),
            ),
        )
        self.assertEqual(replay.state_after, 0xB795D116)

    def test_backtracking_can_add_draws_beyond_pair_count(self):
        rng = MsvcCrtRng(0x12345678)

        replay = generate_procedural_league_round_robin(tuple(range(20)), rng)

        self.assertEqual(replay.pairing_count, 190)
        self.assertEqual(len(replay.bounds), 213)
        self.assertGreater(len(replay.bounds), replay.pairing_count)

        unordered = {
            tuple(sorted(pair))
            for round_pairs in replay.rounds
            for pair in round_pairs
        }
        self.assertEqual(len(unordered), 190)

    def test_odd_team_count_is_rejected_instead_of_inventing_byes(self):
        with self.assertRaises(ValueError):
            generate_procedural_league_round_robin((0, 1, 2), ZeroRng())


if __name__ == "__main__":
    unittest.main()
