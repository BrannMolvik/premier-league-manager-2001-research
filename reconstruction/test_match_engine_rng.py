import unittest

from match_engine_rng import MatchEngineRng


class MatchEngineRngTests(unittest.TestCase):
    def test_known_ran1_sequence_from_seed_one(self):
        rng = MatchEngineRng(1)
        # Numerical Recipes ran1 reference sequence for idum=-1.
        expected = (
            0.41599935685098144,
            0.09196489075755929,
            0.7564104859514211,
            0.5297001933351626,
            0.9304364947278223,
        )
        for value in expected:
            self.assertAlmostEqual(rng.random(), value, places=14)

    def test_bounded_draw_truncates_product(self):
        rng = MatchEngineRng(1)
        self.assertEqual(rng.randbelow(100), 41)
        self.assertEqual(rng.randbelow(7), 0)
        self.assertEqual(rng.randbelow(2), 1)

    def test_zero_seed_normalizes_to_one_seed_path(self):
        zero = MatchEngineRng(0)
        one = MatchEngineRng(1)
        self.assertEqual(
            [zero.randbelow(1000) for _ in range(10)],
            [one.randbelow(1000) for _ in range(10)],
        )


    def test_full_shuffle_state_roundtrip_continues_exact_sequence(self):
        original = MatchEngineRng(123456789)
        prefix = [original.randbelow(10000) for _ in range(47)]
        self.assertEqual(len(prefix), 47)

        snapshot = original.snapshot_state()
        restored = MatchEngineRng.from_snapshot(snapshot)

        self.assertEqual(restored.snapshot_state(), snapshot)
        self.assertEqual(
            [restored.randbelow(10000) for _ in range(64)],
            [original.randbelow(10000) for _ in range(64)],
        )

    def test_snapshot_rejects_wrong_table_length(self):
        rng = MatchEngineRng(1)
        snapshot = rng.snapshot_state()
        snapshot["table"] = snapshot["table"][:-1]
        with self.assertRaisesRegex(ValueError, "32 table entries"):
            MatchEngineRng.from_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
