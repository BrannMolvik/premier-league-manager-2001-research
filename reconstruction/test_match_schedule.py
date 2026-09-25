import unittest

from match_schedule import (
    MsvcCrtRng,
    build_and_shuffle_schedule_bucket,
    schedule_bucket_pre_shuffle_order,
    shuffle_schedule_bucket,
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
            raise AssertionError(f"{value} outside RNG({bound})")
        return value


class MsvcCrtRngTests(unittest.TestCase):
    def test_seed_one_matches_classic_msvc_rand_sequence(self):
        rng = MsvcCrtRng(1)
        self.assertEqual(
            [rng.rand15() for _ in range(10)],
            [41, 18467, 6334, 26500, 19169, 15724, 11478, 29358, 26962, 24464],
        )

    def test_bounded_rng_matches_64d540_scaling(self):
        rng = MsvcCrtRng(1)
        self.assertEqual(
            [rng.randbelow(bound) for bound in (5, 4, 3, 2)],
            [0, 2, 0, 1],
        )

    def test_seed_is_stored_as_32_bit_state(self):
        rng = MsvcCrtRng(0x1_0000_0001)
        self.assertEqual(rng.state, 1)
        rng.seed(-1)
        self.assertEqual(rng.state, 0xFFFFFFFF)


class ScheduleBucketShuffleTests(unittest.TestCase):
    def test_head_insertion_reverses_insertion_order(self):
        self.assertEqual(
            schedule_bucket_pre_shuffle_order([0, 1, 2, 3, 4]),
            (4, 3, 2, 1, 0),
        )

    def test_shuffle_uses_descending_fisher_yates_bounds(self):
        rng = RecordingRng([0, 2, 0, 1])
        self.assertEqual(
            shuffle_schedule_bucket([0, 1, 2, 3, 4], rng),
            (3, 1, 4, 2, 0),
        )
        self.assertEqual(rng.calls, [5, 4, 3, 2])

    def test_exact_head_insert_then_msvc_shuffle_composition(self):
        rng = MsvcCrtRng(1)
        self.assertEqual(
            build_and_shuffle_schedule_bucket([0, 1, 2, 3, 4], rng),
            (1, 3, 0, 2, 4),
        )

    def test_zero_or_one_entry_consumes_no_rng(self):
        rng = RecordingRng([])
        self.assertEqual(shuffle_schedule_bucket([], rng), ())
        self.assertEqual(shuffle_schedule_bucket([7], rng), (7,))
        self.assertEqual(rng.calls, [])


if __name__ == "__main__":
    unittest.main()
