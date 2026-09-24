import unittest

from match_statistics import SegmentCounters, normalize_segment_statistics


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
            raise AssertionError(f"{value} outside RNG({bound})")
        return value


class SegmentStatisticsTests(unittest.TestCase):
    def test_exact_attack_share_and_possession_normalization_with_jitter(self):
        rng = ScriptedRng([9, 0, 9])
        record = normalize_segment_statistics(
            side0_attack_count=3,
            total_attack_count=6,
            counters=SegmentCounters(side0=4, neutral=2, side1=4),
            rng=rng,
        )
        self.assertEqual(record.territory, 54)
        self.assertEqual(record.side0_percent, 35)
        self.assertEqual(record.neutral_percent, 24)
        self.assertEqual(record.side1_percent, 41)
        self.assertEqual(rng.calls, [10, 10, 10])

    def test_no_attacks_keeps_territory_50_but_zero_possession_uses_33_defaults_and_jitter(self):
        rng = ScriptedRng([5, 5])
        record = normalize_segment_statistics(
            0,
            0,
            SegmentCounters(),
            rng,
        )
        self.assertEqual(record.territory, 50)
        self.assertEqual(record.side0_percent, 33)
        self.assertEqual(record.neutral_percent, 33)
        self.assertEqual(record.side1_percent, 34)
        self.assertEqual(rng.calls, [10, 10])

    def test_extreme_percentages_skip_jitter(self):
        rng = ScriptedRng([])
        record = normalize_segment_statistics(
            10,
            10,
            SegmentCounters(side0=19, neutral=1, side1=0),
            rng,
        )
        self.assertEqual(record.territory, 100)
        self.assertEqual(record.side0_percent, 95)
        self.assertEqual(record.neutral_percent, 5)
        self.assertEqual(record.side1_percent, 0)
        self.assertEqual(rng.calls, [])

    def test_sum_over_100_reduces_side0_to_remainder(self):
        rng = ScriptedRng([9, 9, 9])
        record = normalize_segment_statistics(
            1,
            2,
            SegmentCounters(side0=1, neutral=1, side1=0),
            rng,
        )
        # 50->54 territory; side0 50->54; neutral 50->54; executable
        # keeps neutral and reduces side0 to 100-neutral.
        self.assertEqual(record.territory, 54)
        self.assertEqual(record.side0_percent, 46)
        self.assertEqual(record.neutral_percent, 54)
        self.assertEqual(record.side1_percent, 0)


if __name__ == "__main__":
    unittest.main()
