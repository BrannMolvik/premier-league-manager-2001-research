"""Source-index projection deliberately does not invoke RNG or invent pool data."""
from dataclasses import replace
from types import SimpleNamespace
import unittest

from fm2001_data import Player
from original_supportstart_player_name_source import (
    OriginalSupportStaffNameSourceError,
    source_support_staff_name_from_observed_player_pair,
)


def player(index: int, first: str, last: str) -> Player:
    return Player(
        index=index, first_name=first, surname=last, club_id=0,
        nationality_id=0, date_of_birth=None, shirt_number=0,
        height_cm=0, weight_kg=0, positions=(0,0,0),
        current_raw=(), target_raw=(),
    )


class SourceSupportStaffNameTests(unittest.TestCase):
    def setUp(self):
        # Source text samples independently byte-checked from original
        # Master.dat and Core.str, NOT proof of native RNG-selected names.
        self.players = (player(0, "David", "Seaman"),
                        player(1, "Lee", "Dixon"),
                        player(2, "Nigel", "Winterburn"))

    def test_original_separate_first_and_surname_observed_indices(self):
        staff_name = source_support_staff_name_from_observed_player_pair(
            self.players, original_first_player_position=0,
            original_surname_player_position=1, source_group_club_count=10,
        )
        self.assertEqual(staff_name.full_name, "David Dixon")
        self.assertEqual(
            (staff_name.first_player_record_position,
             staff_name.surname_player_record_position), (0,1))
        self.assertEqual(
            source_support_staff_name_from_observed_player_pair(
                self.players, original_first_player_position=0,
                original_surname_player_position=0, source_group_club_count=10).full_name, "David Seaman")

    def test_original_dash_source_requires_new_input_not_guessed_random_draw(self):
        bad = (player(0, "-", "Example"), self.players[1])
        with self.assertRaisesRegex(OriginalSupportStaffNameSourceError, "retries"):
            source_support_staff_name_from_observed_player_pair(
                bad, original_first_player_position=0,
                original_surname_player_position=1, source_group_club_count=10)

    def test_reject_unknown_indices_reordered_records_and_unqualified_pool(self):
        for a, b in ((-1,0), (0,3), (True,0), (0,None), (1.0,1)):
            with self.subTest(indices=(a,b)):
                with self.assertRaises(OriginalSupportStaffNameSourceError):
                    source_support_staff_name_from_observed_player_pair(
                        self.players, original_first_player_position=a,
                        original_surname_player_position=b, source_group_club_count=10)
        with self.assertRaisesRegex(OriginalSupportStaffNameSourceError, "order changed"):
            source_support_staff_name_from_observed_player_pair(
                (self.players[1],self.players[0]),
                original_first_player_position=0,
                original_surname_player_position=1, source_group_club_count=10)
        with self.assertRaises(OriginalSupportStaffNameSourceError):
            source_support_staff_name_from_observed_player_pair(
                (), original_first_player_position=0,
                original_surname_player_position=0, source_group_club_count=10)
        with self.assertRaises(OriginalSupportStaffNameSourceError):
            source_support_staff_name_from_observed_player_pair(
                [self.players[0]], original_first_player_position=0,
                original_surname_player_position=0, source_group_club_count=10)

    def test_group_above_ten_must_not_be_looked_up_in_player_fallback(self):
        for count in (11, 36, 1246, -1, True, None):
            with self.subTest(group_club_count=count):
                with self.assertRaises(OriginalSupportStaffNameSourceError):
                    source_support_staff_name_from_observed_player_pair(
                        self.players,
                        original_first_player_position=0,
                        original_surname_player_position=1,
                        source_group_club_count=count,
                    )

    def test_source_preserves_valid_cp1252_and_rejects_nonoriginal_characters(self):
        french=(player(0, "René", "Seaman"), player(1,"Lee","Cézanne"))
        self.assertEqual(source_support_staff_name_from_observed_player_pair(
            french,original_first_player_position=0,
            original_surname_player_position=1, source_group_club_count=10).full_name, "René Cézanne")
        invalid=(player(0,"山田","Smith"),player(1,"Lee","Dixon"))
        with self.assertRaisesRegex(OriginalSupportStaffNameSourceError,"CP1252"):
            source_support_staff_name_from_observed_player_pair(
                invalid,original_first_player_position=0,
                original_surname_player_position=1, source_group_club_count=10)


if __name__ == "__main__":
    unittest.main()
