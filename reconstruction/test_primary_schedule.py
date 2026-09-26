import unittest

from competition_schedule import StartupScheduleNode, direct_club_ref
from match_schedule import MsvcCrtRng
from primary_schedule import (
    fixed_league_fixture_order_by_round,
    nominal_primary_schedule_bucket,
    place_primary_schedule_nodes,
    shuffle_primary_schedule_buckets,
)


def node(token, home, away, *, week=7, weekday=6):
    return StartupScheduleNode(
        node_kind="league_match",
        competition_id=0,
        competition_context=0,
        round_id=0,
        pair_index=0,
        schedule_index=None,
        scheduled_week=week,
        scheduled_weekday=weekday,
        participant_0_ref=direct_club_ref(home),
        participant_1_ref=direct_club_ref(away),
        node_token=(token,),
    )


class PrimarySchedulePlacementTests(unittest.TestCase):
    def test_first_premier_league_date_maps_to_bucket_54(self):
        self.assertEqual(
            nominal_primary_schedule_bucket(7, 6),
            54,
        )

    def test_christmas_day_is_advanced_one_bucket(self):
        # 7*26 + 1 - 1 = 182 before 0x615950's 25-December skip.
        self.assertEqual(
            nominal_primary_schedule_bucket(26, 1),
            183,
        )

    def test_non_conflicting_same_day_nodes_head_insert(self):
        first = node("first", 1, 2)
        second = node("second", 3, 4)

        placed = place_primary_schedule_nodes((first, second))

        self.assertEqual(
            tuple(entry.node_token for entry in placed.buckets[54]),
            (("second",), ("first",)),
        )
        self.assertEqual(placed.chosen_bucket_indices, (54, 54))

    def test_equal_distance_conflict_moves_to_later_side(self):
        existing = node("existing", 1, 2)
        conflict = node("conflict", 1, 3)

        placed = place_primary_schedule_nodes((existing, conflict))

        self.assertEqual(
            placed.nominal_bucket_indices,
            (54, 54),
        )
        self.assertEqual(
            placed.chosen_bucket_indices,
            (54, 56),
        )


class PrimaryScheduleExecutionOrderTests(unittest.TestCase):
    def test_fixed_league_order_follows_bucket_then_head_to_tail(self):
        first = StartupScheduleNode(
            node_kind="fixed_league_match",
            competition_id=0,
            competition_context=0,
            round_id=10,
            pair_index=0,
            schedule_index=None,
            scheduled_week=7,
            scheduled_weekday=6,
            participant_0_ref=direct_club_ref(1),
            participant_1_ref=direct_club_ref(2),
            node_token=("fixed_league_match", 0, 0, 100),
        )
        second = StartupScheduleNode(
            node_kind="fixed_league_match",
            competition_id=0,
            competition_context=0,
            round_id=10,
            pair_index=1,
            schedule_index=None,
            scheduled_week=7,
            scheduled_weekday=6,
            participant_0_ref=direct_club_ref(3),
            participant_1_ref=direct_club_ref(4),
            node_token=("fixed_league_match", 0, 0, 101),
        )
        later = StartupScheduleNode(
            node_kind="fixed_league_match",
            competition_id=0,
            competition_context=0,
            round_id=11,
            pair_index=0,
            schedule_index=None,
            scheduled_week=8,
            scheduled_weekday=3,
            participant_0_ref=direct_club_ref(5),
            participant_1_ref=direct_club_ref(6),
            node_token=("fixed_league_match", 0, 0, 102),
        )

        self.assertEqual(
            fixed_league_fixture_order_by_round(
                (
                    (second, first),
                    (),
                    (later,),
                )
            ),
            (
                (10, (101, 100)),
                (11, (102,)),
            ),
        )


class CanonicalFirstMatchdayShuffleRegressionTests(unittest.TestCase):
    def test_corrected_gate3_state_produces_first_pl_order(self):
        # Canonical complete-node placement at Gate 4:
        # buckets 0..53 contain these counts, totaling 391 shuffle draws.
        counts_before_54 = (
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            14, 0, 0, 0, 0, 0, 0, 14, 0, 0, 0, 0, 0, 0, 14, 0,
            0, 0, 0, 2, 0, 14, 2, 0, 0, 28, 0, 0, 26, 40, 0, 97,
            28, 3, 0, 84, 39, 0,
        )
        self.assertEqual(
            sum(max(0, count - 1) for count in counts_before_54),
            391,
        )

        buckets = [
            tuple(("earlier", bucket_index, item_index) for item_index in range(count))
            for bucket_index, count in enumerate(counts_before_54)
        ]

        bucket_54 = [
            ("other", index)
            for index in range(142)
        ]
        # Canonical linked-list/pre-shuffle relative slots 96..105 are
        # Premier League fixture IDs 9..0.
        for offset, fixture_id in enumerate(range(9, -1, -1)):
            bucket_54[96 + offset] = ("pl", fixture_id)
        buckets.append(tuple(bucket_54))

        rng = MsvcCrtRng(0x4F5CF274)
        shuffled = shuffle_primary_schedule_buckets(
            buckets,
            rng,
        )

        self.assertEqual(shuffled.draw_count, 532)
        self.assertEqual(shuffled.state_after, 0x81075208)

        pl_positions = [
            (index, item[1])
            for index, item in enumerate(shuffled.buckets[54])
            if item[0] == "pl"
        ]
        self.assertEqual(
            pl_positions,
            [
                (36, 0),
                (41, 6),
                (44, 8),
                (49, 5),
                (51, 1),
                (52, 9),
                (78, 3),
                (102, 2),
                (104, 4),
                (114, 7),
            ],
        )
        self.assertEqual(
            [fixture_id for _, fixture_id in pl_positions],
            [0, 6, 8, 5, 1, 9, 3, 2, 4, 7],
        )


class CanonicalEarlyMatchdayShuffleRegressionTests(unittest.TestCase):
    def test_first_ten_real_pl_matchday_orders(self):
        # These snapshots come from canonical shipped-data placement of all
        # 9,346 Gate-3 nodes. state_before is the CRT state immediately before
        # 0x615AE0 shuffles the target bucket. pre_start is the first relative
        # linked-list slot occupied by the ten PL fixtures before the shuffle.
        snapshots = (
            (1, 142, 0xD545A52D, 96, tuple(range(9, -1, -1)), (0, 6, 8, 5, 1, 9, 3, 2, 4, 7)),
            (2, 10, 0x8A86E535, 0, tuple(range(19, 9, -1)), (16, 14, 19, 11, 17, 13, 18, 15, 10, 12)),
            (3, 142, 0x6097BC6C, 96, tuple(range(29, 19, -1)), (20, 23, 21, 29, 22, 27, 26, 24, 25, 28)),
            (4, 142, 0x5F974FE3, 96, tuple(range(39, 29, -1)), (31, 35, 36, 37, 33, 38, 30, 32, 34, 39)),
            (5, 142, 0xA0CA8166, 96, tuple(range(49, 39, -1)), (49, 43, 44, 47, 42, 41, 46, 48, 45, 40)),
            (6, 138, 0x9AE8168B, 92, tuple(range(59, 49, -1)), (50, 58, 54, 59, 53, 51, 56, 55, 52, 57)),
            (7, 142, 0xE567E387, 96, tuple(range(69, 59, -1)), (64, 62, 61, 66, 67, 65, 63, 69, 68, 60)),
            (8, 142, 0x7EE89D5E, 96, tuple(range(79, 69, -1)), (75, 76, 78, 70, 72, 77, 79, 74, 73, 71)),
            (9, 142, 0x117F71A5, 96, tuple(range(89, 79, -1)), (88, 80, 82, 81, 89, 85, 83, 84, 87, 86)),
            (10, 142, 0x82282EF3, 96, tuple(range(99, 89, -1)), (99, 91, 97, 95, 92, 90, 94, 98, 93, 96)),
        )

        for (
            round_number,
            bucket_size,
            state_before,
            pre_start,
            pre_fixture_ids,
            expected_order,
        ) in snapshots:
            with self.subTest(round_number=round_number):
                bucket = [
                    ("other", index)
                    for index in range(bucket_size)
                ]
                for offset, fixture_id in enumerate(pre_fixture_ids):
                    bucket[pre_start + offset] = ("pl", fixture_id)

                shuffled = shuffle_primary_schedule_buckets(
                    (tuple(bucket),),
                    MsvcCrtRng(state_before),
                )
                actual_order = tuple(
                    item[1]
                    for item in shuffled.buckets[0]
                    if item[0] == "pl"
                )
                self.assertEqual(actual_order, expected_order)


if __name__ == "__main__":
    unittest.main()
