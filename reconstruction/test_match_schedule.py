import unittest
from dataclasses import dataclass

from match_schedule import (
    MsvcCrtRng,
    build_and_shuffle_schedule_bucket,
    choose_ordinary_league_schedule_bucket,
    first_ordinary_league_conflict_near,
    insert_ordinary_league_match,
    ordinary_league_matches_conflict,
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



@dataclass(frozen=True)
class LeagueMatch:
    id: int
    home_club_id: int
    away_club_id: int


class OrdinaryLeaguePlacementTests(unittest.TestCase):
    def empty_buckets(self, count=20):
        return [[] for _ in range(count)]

    def test_overlap_predicate_matches_either_club(self):
        existing = LeagueMatch(1, 10, 20)
        self.assertTrue(
            ordinary_league_matches_conflict(
                existing,
                LeagueMatch(2, 10, 30),
            )
        )
        self.assertTrue(
            ordinary_league_matches_conflict(
                existing,
                LeagueMatch(3, 40, 20),
            )
        )
        self.assertFalse(
            ordinary_league_matches_conflict(
                existing,
                LeagueMatch(4, 30, 40),
            )
        )

    def test_near_search_scans_previous_current_next_in_order(self):
        buckets = self.empty_buckets()
        candidate = LeagueMatch(9, 1, 2)
        buckets[6].append(LeagueMatch(1, 1, 30))
        buckets[7].append(LeagueMatch(2, 2, 40))

        self.assertEqual(
            first_ordinary_league_conflict_near(buckets, 7, candidate),
            6,
        )

    def test_no_conflict_keeps_nominal_bucket(self):
        buckets = self.empty_buckets()
        candidate = LeagueMatch(9, 1, 2)

        self.assertEqual(
            choose_ordinary_league_schedule_bucket(buckets, 8, candidate),
            8,
        )

    def test_conflict_on_nominal_prefers_later_side_on_distance_tie(self):
        buckets = self.empty_buckets()
        candidate = LeagueMatch(9, 1, 2)
        buckets[8].append(LeagueMatch(1, 1, 30))

        # Initial conflict C=8 gives lower=6 / upper=10. Equal distance from
        # nominal 8 falls through to the executable's upper-side probe.
        self.assertEqual(
            choose_ordinary_league_schedule_bucket(buckets, 8, candidate),
            10,
        )

    def test_conflict_on_next_day_pushes_to_earlier_side(self):
        buckets = self.empty_buckets()
        candidate = LeagueMatch(9, 1, 2)
        buckets[9].append(LeagueMatch(1, 1, 30))

        # Search around nominal 8 finds C=9. lower=7 is closer than upper=11,
        # and its 6..8 neighborhood is clear.
        self.assertEqual(
            choose_ordinary_league_schedule_bucket(buckets, 8, candidate),
            7,
        )

    def test_repeated_upper_conflict_can_switch_search_to_lower_side(self):
        buckets = self.empty_buckets()
        candidate = LeagueMatch(9, 1, 2)
        buckets[8].append(LeagueMatch(1, 1, 30))
        buckets[11].append(LeagueMatch(2, 2, 40))

        # C=8 ties -> probe center 10, whose 9..11 neighborhood conflicts at
        # 11. upper becomes 13; lower=6 is now closer and clear.
        self.assertEqual(
            choose_ordinary_league_schedule_bucket(buckets, 8, candidate),
            6,
        )

    def test_insertion_is_head_insertion_at_resolved_bucket(self):
        buckets = self.empty_buckets()
        first = LeagueMatch(1, 10, 20)
        second = LeagueMatch(2, 30, 40)

        self.assertEqual(insert_ordinary_league_match(buckets, 8, first), 8)
        self.assertEqual(insert_ordinary_league_match(buckets, 8, second), 8)
        self.assertEqual([match.id for match in buckets[8]], [2, 1])
