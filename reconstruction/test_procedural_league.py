import unittest

from match_schedule import MsvcCrtRng
from procedural_league import (
    generate_procedural_league_round_robin,
    materialize_procedural_league_match_emissions,
    procedural_league_cycle_count,
)


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

    def test_cycle_count_matches_legacy_ceiling_division(self):
        self.assertEqual(procedural_league_cycle_count(4, 6), 2)
        self.assertEqual(procedural_league_cycle_count(4, 3), 1)
        self.assertEqual(procedural_league_cycle_count(12, 38), 4)

    def test_match_emission_reuses_matrix_and_alternates_home_away(self):
        replay = generate_procedural_league_round_robin(
            (0, 1, 2, 3),
            ZeroRng(),
        )

        emissions = materialize_procedural_league_match_emissions(replay, 6)

        self.assertEqual(len(emissions), 12)
        self.assertEqual(
            [
                (
                    item.round_index,
                    item.pair_index,
                    item.cycle_index,
                    item.schedule_index,
                    item.home_team,
                    item.away_team,
                )
                for item in emissions[:8]
            ],
            [
                (0, 0, 0, 0, 3, 2),
                (0, 0, 1, 3, 2, 3),
                (0, 1, 0, 0, 1, 0),
                (0, 1, 1, 3, 0, 1),
                (1, 0, 0, 1, 1, 2),
                (1, 0, 1, 4, 2, 1),
                (1, 1, 0, 1, 0, 3),
                (1, 1, 1, 4, 3, 0),
            ],
        )
    def test_odd_team_count_is_rejected_instead_of_inventing_byes(self):
        with self.assertRaises(ValueError):
            generate_procedural_league_round_robin((0, 1, 2), ZeroRng())


if __name__ == "__main__":
    unittest.main()
