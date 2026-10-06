import unittest
from dataclasses import dataclass
from datetime import date

from cup_tied_state import (
    CupTiedPlayerCollection,
    CupTiedTransferWindowState,
    cup_tied_root_competition_id,
    root_competition_id,
)


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    parent_competition_id: int | None = None


class CupTiedTransferWindowStateTests(unittest.TestCase):
    def test_initialization_uses_exact_relative_date_offsets(self):
        state = CupTiedTransferWindowState.initialize(date(2000, 8, 18))

        self.assertEqual(state.selector, 0)
        self.assertEqual(state.cutoff_1, date(2000, 10, 17))
        self.assertEqual(state.cutoff_2, date(2001, 3, 13))
        self.assertIsNone(state.selected_cutoff())

    def test_daily_boundaries_select_one_then_two_and_other_days_preserve(self):
        state = CupTiedTransferWindowState.initialize(date(2000, 7, 1))

        self.assertEqual(state.advance_day(date(2000, 8, 29)), 0)
        self.assertEqual(state.advance_day(date(2000, 8, 30)), 1)
        self.assertEqual(state.advance_day(date(2000, 8, 31)), 1)
        self.assertEqual(state.advance_day(date(2001, 1, 30)), 2)
        self.assertEqual(state.advance_day(date(2001, 1, 31)), 2)

    def test_transfer_history_requires_available_record_and_strictly_later_date(self):
        state = CupTiedTransferWindowState.initialize(date(2000, 7, 1))
        state.advance_day(date(2000, 8, 30))
        cutoff = state.cutoff_1

        self.assertFalse(
            state.transfer_history_is_tied(
                history_club_id=None,
                transfer_date=cutoff.replace(day=cutoff.day),
            )
        )
        self.assertFalse(
            state.transfer_history_is_tied(
                history_club_id=-1,
                transfer_date=cutoff,
            )
        )
        self.assertFalse(
            state.transfer_history_is_tied(
                history_club_id=10,
                transfer_date=cutoff,
            )
        )
        self.assertTrue(
            state.transfer_history_is_tied(
                history_club_id=10,
                transfer_date=date.fromordinal(cutoff.toordinal() + 1),
            )
        )

    def test_selector_two_uses_second_cutoff(self):
        state = CupTiedTransferWindowState.initialize(date(2000, 7, 1))
        state.advance_day(date(2001, 1, 30))

        self.assertEqual(state.selected_cutoff(), state.cutoff_2)
        self.assertFalse(
            state.transfer_history_is_tied(
                history_club_id=10,
                transfer_date=state.cutoff_2,
            )
        )
        self.assertTrue(
            state.transfer_history_is_tied(
                history_club_id=10,
                transfer_date=date.fromordinal(state.cutoff_2.toordinal() + 1),
            )
        )


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

    def test_incomplete_competition_metadata_fails_closed(self):
        competitions = {100: object()}
        self.assertIsNone(cup_tied_root_competition_id(100, competitions))

    def test_malformed_parent_cycle_fails_closed(self):
        competitions = {
            1: Competition(1, 1, 2),
            2: Competition(2, 2, 1),
        }

        with self.assertRaisesRegex(RuntimeError, "cycle"):
            root_competition_id(1, competitions)


if __name__ == "__main__":
    unittest.main()
