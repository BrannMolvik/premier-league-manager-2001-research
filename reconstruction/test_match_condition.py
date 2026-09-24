import unittest
from dataclasses import dataclass

from match_condition import (
    ConditionInjurySettings,
    ConditionInjuryState,
    apply_sequence_condition_and_injuries,
    condition_decay_threshold,
    injury_incidence_score,
)
from match_events import IncidentKind


@dataclass
class Player:
    side: int
    player_index: int
    condition: int
    current_position: int
    skills: tuple[int, ...]


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


def player(side, index, role, stamina=128, injury=0, condition=100):
    skills = [0] * 17
    skills[2] = stamina
    skills[4] = injury
    return Player(side, index, condition, role, tuple(skills))


class ConditionFormulaTests(unittest.TestCase):
    def test_exact_threshold(self):
        self.assertEqual(condition_decay_threshold(255, 5), 10)
        self.assertEqual(condition_decay_threshold(128, 5), 14)
        self.assertEqual(condition_decay_threshold(0, 9), 26)

    def test_exact_injury_score(self):
        self.assertEqual(injury_incidence_score(0, 80, 100), 10)
        self.assertEqual(injury_incidence_score(0xC0, 80, 70), 18)


class SequenceConditionTests(unittest.TestCase):
    def test_attacker_forwards_full_midfield_half_defenders_none(self):
        forward = player(0, 1, 19)
        midfield = player(0, 2, 12)
        defender = player(0, 3, 4)
        # Base threshold is 14. Rolls 13 and 6 pass full/half thresholds.
        # Each successful decrement then consumes an injury RNG(1000).
        rng = ScriptedRng([13, 999, 6, 999])
        state = ConditionInjuryState()

        events = apply_sequence_condition_and_injuries(
            0,
            [forward, midfield, defender],
            [],
            5,
            5,
            20,
            ConditionInjurySettings(0),
            state,
            rng,
        )

        self.assertEqual(forward.condition, 99)
        self.assertEqual(midfield.condition, 99)
        self.assertEqual(defender.condition, 100)
        self.assertEqual(events, ())
        self.assertEqual(rng.calls, [100, 1000, 100, 1000])

    def test_defender_full_midfield_half_forward_none_on_defending_side(self):
        defender = player(1, 1, 4)
        midfield = player(1, 2, 12)
        forward = player(1, 3, 19)
        rng = ScriptedRng([13, 999, 6, 999])

        apply_sequence_condition_and_injuries(
            0,
            [],
            [defender, midfield, forward],
            5,
            5,
            20,
            ConditionInjurySettings(0),
            ConditionInjuryState(),
            rng,
        )

        self.assertEqual(defender.condition, 99)
        self.assertEqual(midfield.condition, 99)
        self.assertEqual(forward.condition, 100)

    def test_injury_roll_precedes_ten_minute_cooldown(self):
        subject = player(0, 1, 19, injury=255, condition=76)
        state = ConditionInjuryState(last_injury_minute=15)
        # Condition succeeds. Injury score is 31, and roll succeeds, but at
        # minute 20 the last injury is not strictly earlier than 10 minutes ago.
        rng = ScriptedRng([0, 0])

        events = apply_sequence_condition_and_injuries(
            0,
            [subject],
            [],
            5,
            5,
            20,
            ConditionInjurySettings(0),
            state,
            rng,
        )

        self.assertEqual(subject.condition, 75)
        self.assertEqual(events, ())
        self.assertEqual(rng.calls, [100, 1000])

    def test_injury_event_after_cooldown(self):
        subject = player(0, 1, 19, injury=255, condition=76)
        state = ConditionInjuryState(last_injury_minute=0)
        rng = ScriptedRng([0, 0])

        events = apply_sequence_condition_and_injuries(
            0,
            [subject],
            [],
            5,
            5,
            20,
            ConditionInjurySettings(0),
            state,
            rng,
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].kind, IncidentKind.INJURED)
        self.assertEqual(state.last_injury_minute, 20)
        self.assertIn((0, 1), state.injured_players)


if __name__ == "__main__":
    unittest.main()
