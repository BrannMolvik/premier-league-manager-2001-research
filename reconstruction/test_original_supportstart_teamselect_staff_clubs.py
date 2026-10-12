"""Source club table for the actual TeamSelect staff constructor (+0x58)."""
import unittest

from fm2001_data import Club
from original_supportstart_teamselect_staff_clubs import (
    ORIGINAL_STAFF_CANDIDATE_CAP,
    OriginalTeamSelectStaffClubError,
    original_teamselect_staff_club_candidates,
)


def club(index: int, competition_id: int) -> Club:
    return Club(index, f"Source club {index}", f"C{index}", "Ground", 0,
                competition_id=competition_id)


class OriginalTeamSelectStaffClubTests(unittest.TestCase):
    def test_source_record_order_and_exact_competition_predicate(self):
        clubs = (
            club(0, 5), club(1, 1), club(2, 5),
            club(3, 9), club(4, 5), club(5, 2)
        )
        group = original_teamselect_staff_club_candidates(
            clubs, group_id=5, require_shipped_count=False
        )
        self.assertEqual(group.original_group_id, 5)
        self.assertEqual(group.matched_original_club_count, 3)
        self.assertEqual(group.original_random_bound, 3)
        self.assertEqual(group.source_club_indices, (0, 2, 4))
        self.assertEqual(group.truncated_original_club_count, 0)
        self.assertEqual(group.require_nonempty_source_pool(), (0, 2, 4))

    def test_original_24_pointer_cap_and_first_source_records_only(self):
        clubs = tuple(club(i, 170 if i % 2 == 0 else 0) for i in range(60))
        group = original_teamselect_staff_club_candidates(
            clubs, group_id=170, require_shipped_count=False
        )
        self.assertEqual(group.matched_original_club_count, 30)
        self.assertEqual(group.original_random_bound, ORIGINAL_STAFF_CANDIDATE_CAP)
        self.assertEqual(group.truncated_original_club_count, 6)
        self.assertEqual(group.source_club_indices, tuple(range(0, 48, 2)))
        self.assertEqual(group.require_nonempty_source_pool(), tuple(range(0, 48, 2)))

    def test_no_source_group_does_not_fabricate_random_bound(self):
        group = original_teamselect_staff_club_candidates(
            (club(0, 1), club(1, 2)), group_id=3, require_shipped_count=False
        )
        self.assertEqual(group.source_club_indices, ())
        self.assertEqual(group.original_random_bound, 0)
        with self.assertRaises(OriginalTeamSelectStaffClubError):
            group.require_nonempty_source_pool()

    def test_no_country_or_team_category_substitution(self):
        clubs = (club(0, 17), club(1, 17), club(2, 11))
        group = original_teamselect_staff_club_candidates(
            clubs, group_id=11, require_shipped_count=False
        )
        self.assertEqual(group.source_club_indices, (2,))

    def test_invalid_source_data_fail_closed(self):
        source = (club(0, 1), club(1, 2))
        samples = (
            (source, -1, False),
            (source, True, False),
            (source, 0x100000000, False),
            (source, 1, True),
            ((club(1, 1),), 1, False),
            ((club(0, 1), club(0, 1)), 1, False),
            ((), 1, False),
        )
        for clubs, group_id, require_shipped_count in samples:
            with self.subTest(clubs=clubs, group_id=group_id,
                              require_shipped_count=require_shipped_count):
                with self.assertRaises(OriginalTeamSelectStaffClubError):
                    original_teamselect_staff_club_candidates(
                        clubs, group_id=group_id,
                        require_shipped_count=require_shipped_count
                    )


if __name__ == "__main__":
    unittest.main()
