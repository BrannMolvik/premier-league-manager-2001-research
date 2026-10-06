import unittest
from dataclasses import dataclass

from cup_tied_state import (
    CupTiedPlayerCollection,
    cup_tied_root_competition_id,
    root_competition_id,
)


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    parent_competition_id: int | None = None


class CupTiedPlayerCollectionTests(unittest.TestCase):
    def test_first_club_record_wins_and_transfer_makes_player_tied(self):
        collection = CupTiedPlayerCollection()

        self.assertTrue(collection.record_appearance(123, 10))
        self.assertFalse(collection.record_appearance(123, 20))

        self.assertEqual(collection.recorded_club_id(123), 10)
        self.assertFalse(collection.is_cup_tied(123, 10))
        self.assertTrue(collection.is_cup_tied(123, 20))

    def test_absent_player_is_not_tied(self):
        collection = CupTiedPlayerCollection()

        self.assertIsNone(collection.recorded_club_id(123))
        self.assertFalse(collection.is_cup_tied(123, 10))

    def test_root_context_walks_parent_chain(self):
        competitions = {
            100: Competition(100, 2),
            101: Competition(101, 1, 100),
            102: Competition(102, 1, 101),
        }

        self.assertEqual(root_competition_id(102, competitions), 100)
        self.assertEqual(cup_tied_root_competition_id(102, competitions), 100)

    def test_ordinary_root_league_does_not_enable_cup_tied_collection(self):
        competitions = {
            0: Competition(0, 1),
            1: Competition(1, 1, 0),
        }

        self.assertEqual(root_competition_id(1, competitions), 0)
        self.assertIsNone(cup_tied_root_competition_id(1, competitions))

    def test_dummy_league_root_uses_same_true_virtual_predicate(self):
        competitions = {
            50: Competition(50, 3),
            51: Competition(51, 1, 50),
        }

        self.assertEqual(cup_tied_root_competition_id(51, competitions), 50)

    def test_malformed_parent_cycle_fails_closed(self):
        competitions = {
            1: Competition(1, 1, 2),
            2: Competition(2, 2, 1),
        }

        with self.assertRaisesRegex(RuntimeError, "cycle"):
            root_competition_id(1, competitions)


if __name__ == "__main__":
    unittest.main()
