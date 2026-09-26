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

        rng = MsvcCrtRng(0x0E556598)
        shuffled = shuffle_primary_schedule_buckets(
            buckets,
            rng,
        )

        self.assertEqual(shuffled.draw_count, 532)
        self.assertEqual(shuffled.state_after, 0xC290356C)

        pl_positions = [
            (index, item[1])
            for index, item in enumerate(shuffled.buckets[54])
            if item[0] == "pl"
        ]
        self.assertEqual(
            pl_positions,
            [
                (0, 8),
                (8, 3),
                (10, 2),
                (16, 4),
                (26, 6),
                (78, 9),
                (88, 5),
                (95, 0),
                (97, 1),
                (103, 7),
            ],
        )
        self.assertEqual(
            [fixture_id for _, fixture_id in pl_positions],
            [8, 3, 2, 4, 6, 9, 5, 0, 1, 7],
        )


class CanonicalEarlyMatchdayShuffleRegressionTests(unittest.TestCase):
    def test_first_ten_real_pl_matchday_orders(self):
        # These snapshots come from canonical shipped-data placement of all
        # 9,346 Gate-3 nodes. state_before is the CRT state immediately before
        # 0x615AE0 shuffles the target bucket. pre_start is the first relative
        # linked-list slot occupied by the ten PL fixtures before the shuffle.
        snapshots = (
            (1, 142, 0x1CBB48A1, 96, tuple(range(9, -1, -1)), (8, 3, 2, 4, 6, 9, 5, 0, 1, 7)),
            (2, 10, 0xC836DF29, 0, tuple(range(19, 9, -1)), (14, 10, 15, 12, 18, 17, 11, 19, 16, 13)),
            (3, 142, 0x2A01F910, 96, tuple(range(29, 19, -1)), (27, 24, 25, 23, 26, 21, 28, 20, 22, 29)),
            (4, 142, 0x24BF4337, 96, tuple(range(39, 29, -1)), (37, 36, 33, 30, 38, 32, 31, 35, 39, 34)),
            (5, 142, 0x895E0D2A, 96, tuple(range(49, 39, -1)), (43, 48, 42, 41, 47, 45, 46, 44, 40, 49)),
            (6, 138, 0xA13ED3A6, 92, tuple(range(59, 49, -1)), (53, 54, 51, 50, 56, 57, 59, 52, 58, 55)),
            (7, 142, 0x929F341B, 96, tuple(range(69, 59, -1)), (60, 65, 64, 68, 67, 69, 66, 62, 63, 61)),
            (8, 142, 0x555492A2, 96, tuple(range(79, 69, -1)), (73, 74, 78, 75, 70, 77, 72, 79, 76, 71)),
            (9, 142, 0x0191E699, 96, tuple(range(89, 79, -1)), (81, 88, 84, 82, 83, 87, 89, 80, 85, 86)),
            (10, 142, 0xC067FF47, 96, tuple(range(99, 89, -1)), (95, 98, 94, 90, 96, 99, 91, 97, 92, 93)),
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
