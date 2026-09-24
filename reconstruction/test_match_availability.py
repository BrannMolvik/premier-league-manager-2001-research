import unittest
from dataclasses import dataclass

from match_availability import (
    CupTiedEntry,
    base_lineup_eligible,
    find_cup_tied_entry,
    is_cup_tied,
    lineup_eligible_with_cup_tie,
)


@dataclass
class Player:
    club_id: int
    injured: bool = False
    suspended: bool = False
    selection_excluded: bool = False


class CupTiedTests(unittest.TestCase):
    def test_lookup_returns_first_matching_player_record(self):
        entries = (
            CupTiedEntry(7, 2),
            CupTiedEntry(8, 3),
        )
        self.assertEqual(find_cup_tied_entry(entries, 7), entries[0])
        self.assertIsNone(find_cup_tied_entry(entries, 9))

    def test_no_record_is_not_cup_tied(self):
        self.assertFalse(is_cup_tied((), 7, 2))

    def test_same_registered_club_is_not_cup_tied(self):
        entries = (CupTiedEntry(7, 2),)
        self.assertFalse(is_cup_tied(entries, 7, 2))

    def test_different_registered_club_is_cup_tied(self):
        entries = (CupTiedEntry(7, 2),)
        self.assertTrue(is_cup_tied(entries, 7, 3))

    def test_record_fields_match_original_uint16_width(self):
        with self.assertRaises(ValueError):
            CupTiedEntry(-1, 2)
        with self.assertRaises(ValueError):
            CupTiedEntry(1, 0x10000)


class BaseAvailabilityTests(unittest.TestCase):
    def test_same_club_without_low_bit_exclusion_is_eligible(self):
        self.assertTrue(base_lineup_eligible(Player(4), 4))

    def test_club_mismatch_is_ineligible(self):
        self.assertFalse(base_lineup_eligible(Player(4), 5))

    def test_each_low_bit_state_excludes_player(self):
        for kwargs in (
            {"injured": True},
            {"suspended": True},
            {"selection_excluded": True},
        ):
            with self.subTest(kwargs=kwargs):
                self.assertFalse(base_lineup_eligible(Player(4, **kwargs), 4))

    def test_cup_tie_layer_is_explicit(self):
        player = Player(4)
        entries = (CupTiedEntry(7, 3),)

        self.assertTrue(
            lineup_eligible_with_cup_tie(
                player,
                7,
                4,
                entries,
                apply_cup_tied_check=False,
            )
        )
        self.assertFalse(
            lineup_eligible_with_cup_tie(
                player,
                7,
                4,
                entries,
                apply_cup_tied_check=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
