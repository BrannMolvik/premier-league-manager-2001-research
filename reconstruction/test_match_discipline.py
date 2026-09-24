import unittest
from dataclasses import dataclass

from match_discipline import (
    DisciplineState,
    apply_sequence_discipline,
    discipline_incident_threshold,
    select_discipline_candidate,
)
from match_events import IncidentKind


@dataclass(frozen=True)
class Player:
    side: int
    player_index: int
    current_position: int
    balance_position_code: int


class ScriptedRng:
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


class DisciplineFormulaTests(unittest.TestCase):
    def test_outer_threshold(self):
        self.assertEqual(discipline_incident_threshold(0), 12)
        self.assertEqual(discipline_incident_threshold(5), 24)
        self.assertEqual(discipline_incident_threshold(9), 52)


class DisciplineCandidateTests(unittest.TestCase):
    def test_target_is_one_based_and_role_bounds_are_strict(self):
        players = [
            Player(1, 1, 2, 0),
            Player(1, 2, 3, 0),
            Player(1, 3, 7, 0),
            Player(1, 4, 8, 0),
        ]
        rng = ScriptedRng([1])
        selected = select_discipline_candidate(
            players,
            2,
            8,
            DisciplineState(),
            rng,
        )
        self.assertEqual(selected.player_index, 3)
        self.assertEqual(rng.calls, [2])

    def test_balance_code_8_can_select_before_random_target(self):
        players = [
            Player(1, 1, 4, 8),
            Player(1, 2, 5, 0),
            Player(1, 3, 6, 0),
        ]
        # target = third eligible, then first eligible gets the special 50% test.
        rng = ScriptedRng([2, 4])
        selected = select_discipline_candidate(
            players,
            2,
            8,
            DisciplineState(),
            rng,
        )
        self.assertEqual(selected.player_index, 1)
        self.assertEqual(rng.calls, [3, 10])


class SequenceDisciplineTests(unittest.TestCase):
    def setUp(self):
        self.side0 = [Player(0, 1, 4, 0)]
        self.side1 = [Player(1, 2, 4, 0)]

    def test_targets_defending_side_and_books_unbooked_player(self):
        # incident gate pass; role band 3..7; only candidate; booking roll >= A.
        rng = ScriptedRng([0, 0, 0, 99])
        state = DisciplineState()
        event = apply_sequence_discipline(
            0,
            self.side0,
            self.side1,
            5,
            5,
            state,
            rng,
        )
        self.assertEqual(event.kind, IncidentKind.BOOKED)
        self.assertEqual(event.player_side, 1)
        self.assertIn((1, 2), state.booked_players)
        self.assertEqual(rng.calls, [800, 100, 1, 100])

    def test_unbooked_player_can_take_direct_red_path(self):
        # booking roll < aggression, then both dismissal gates pass.
        rng = ScriptedRng([0, 0, 0, 0, 0, 0])
        state = DisciplineState()
        event = apply_sequence_discipline(
            0,
            self.side0,
            self.side1,
            9,
            9,
            state,
            rng,
        )
        self.assertEqual(event.kind, IncidentKind.SENT_OFF)
        self.assertNotIn((1, 2), state.booked_players)
        self.assertIn((1, 2), state.sent_off_players)
        self.assertEqual(state.red_counts, [0, 1])
        self.assertEqual(rng.calls, [800, 100, 1, 100, 10, 5])

    def test_booked_player_skips_second_booking_roll(self):
        rng = ScriptedRng([0, 0, 0, 0, 0])
        state = DisciplineState(booked_players={(1, 2)})
        event = apply_sequence_discipline(
            0,
            self.side0,
            self.side1,
            9,
            9,
            state,
            rng,
        )
        self.assertEqual(event.kind, IncidentKind.SENT_OFF)
        self.assertEqual(rng.calls, [800, 100, 1, 10, 5])

    def test_four_existing_reds_make_fifth_red_impossible(self):
        rng = ScriptedRng([0, 0, 0, 0, 0])
        state = DisciplineState(
            booked_players={(1, 2)},
            red_counts=[0, 4],
        )
        event = apply_sequence_discipline(
            0,
            self.side0,
            self.side1,
            9,
            9,
            state,
            rng,
        )
        self.assertIsNone(event)
        self.assertEqual(state.red_counts, [0, 4])

    def test_disabled_guard_consumes_no_rng(self):
        rng = ScriptedRng([])
        event = apply_sequence_discipline(
            0,
            self.side0,
            self.side1,
            5,
            5,
            DisciplineState(),
            rng,
            enabled=False,
        )
        self.assertIsNone(event)
        self.assertEqual(rng.calls, [])


if __name__ == "__main__":
    unittest.main()
