import unittest

from competition_schedule import StartupScheduleNode, direct_club_ref
from match_schedule import MsvcCrtRng
from primary_schedule import (
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


if __name__ == "__main__":
    unittest.main()
