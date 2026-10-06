from __future__ import annotations

from types import SimpleNamespace
import unittest

from cup_tied_state import (
    COMPETITION_CUP_TIED_LOOKUP_VA,
    CUP_TIED_LOOKUP_VA,
    CupTiedPlayerRecord,
    CupTiedStateError,
    player_is_cup_tied,
)


class CupTiedStateTests(unittest.TestCase):
    def test_matching_player_is_tied_only_against_a_different_team(self):
        records = (
            CupTiedPlayerRecord(player_id=17, tied_club_id=4),
            CupTiedPlayerRecord(player_id=23, tied_club_id=9),
        )
        self.assertFalse(player_is_cup_tied(records, player_id=17, team_id=4))
        self.assertTrue(player_is_cup_tied(records, player_id=17, team_id=9))
        self.assertFalse(player_is_cup_tied(records, player_id=99, team_id=9))

    def test_lookup_preserves_recovered_native_addresses(self):
        self.assertEqual(CUP_TIED_LOOKUP_VA, 0x4E9710)
        self.assertEqual(COMPETITION_CUP_TIED_LOOKUP_VA, 0x4F8E40)

    def test_lookup_rejects_unproven_record_shapes_instead_of_guessing(self):
        with self.assertRaises(CupTiedStateError):
            player_is_cup_tied(
                (SimpleNamespace(player_id=17, tied_club_id=4),),
                player_id=17,
                team_id=9,
            )

    def test_record_ids_and_lookup_ids_must_remain_integers(self):
        with self.assertRaises(CupTiedStateError):
            CupTiedPlayerRecord(player_id="17", tied_club_id=4)
        with self.assertRaises(CupTiedStateError):
            player_is_cup_tied((), player_id=17, team_id=None)


if __name__ == "__main__":
    unittest.main()
