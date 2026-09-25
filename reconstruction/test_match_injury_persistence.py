import unittest
from dataclasses import dataclass
from datetime import date, timedelta

from match_injury_persistence import (
    MatchInjuryBucket,
    clear_expired_persistent_injury,
    generate_persistent_match_injury,
)


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


@dataclass
class Player:
    condition: int = 80
    injured: bool = False
    suspended: bool = False
    selection_excluded: bool = False
    injury_return_date: date | None = None
    injury_source_mode: int | None = None
    injury_severity_code: int | None = None
    injury_history_weight: int = 0


def roster(count=14, *, condition=80):
    return [Player(condition=condition) for _ in range(count)]


class PersistentMatchInjuryTests(unittest.TestCase):
    def test_ai_guard_suppresses_below_fourteen_without_rng(self):
        players = roster(13)
        rng = ScriptedRng([])
        result = generate_persistent_match_injury(
            players[0],
            players,
            date(2000, 8, 19),
            rng,
        )
        self.assertIsNone(result)
        self.assertEqual(rng.calls, [])
        self.assertFalse(players[0].injured)

    def test_fourteen_available_players_allows_injury(self):
        players = roster(14)
        rng = ScriptedRng([2, 1])
        result = generate_persistent_match_injury(
            players[0],
            players,
            date(2000, 8, 19),
            rng,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.bucket, MatchInjuryBucket.BROKEN_TOE)
        self.assertEqual(result.recovery_weeks, 4)
        self.assertEqual(result.severity_code, 4)
        self.assertEqual(result.condition_drop, 40)
        self.assertEqual(rng.calls, [100, 4])

    def test_mode_zero_ankle_boundary_and_minor_branch_rng(self):
        players = roster()
        rng = ScriptedRng([3, 49])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng
        )
        self.assertEqual(result.source_mode, 0)
        self.assertEqual(result.bucket, MatchInjuryBucket.ANKLE)
        self.assertEqual((result.severity_code, result.recovery_weeks), (0, 1))
        self.assertEqual(result.condition_drop, 10)
        self.assertEqual(rng.calls, [100, 100])
        self.assertEqual(players[0].condition, 70)

    def test_mode_zero_ankle_moderate_consumes_duration_rng(self):
        players = roster()
        rng = ScriptedRng([3, 50, 2])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng
        )
        self.assertEqual((result.severity_code, result.recovery_weeks), (1, 5))
        self.assertEqual(result.return_date, date(2000, 9, 23))
        self.assertEqual(rng.calls, [100, 100, 4])

    def test_low_condition_selects_mode_one_and_its_category_table(self):
        players = roster(condition=74)
        rng = ScriptedRng([79, 12, 2])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng
        )
        self.assertEqual(result.source_mode, 1)
        self.assertEqual(result.bucket, MatchInjuryBucket.HERNIA)
        self.assertEqual(result.severity_code, 1)
        self.assertEqual(result.recovery_weeks, 6)
        self.assertEqual(rng.calls, [100, 100, 3])

    def test_mode_one_80_and_above_falls_to_abdomen(self):
        players = roster(condition=74)
        rng = ScriptedRng([80, 0, 1])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng
        )
        self.assertEqual(result.bucket, MatchInjuryBucket.ABDOMEN)
        self.assertEqual((result.severity_code, result.recovery_weeks), (0, 2))
        self.assertEqual(rng.calls, [100, 100, 2])

    def test_special_bucket_uses_literal_six_weeks_and_one_unused_roll(self):
        players = roster()
        rng = ScriptedRng([90, 77])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng
        )
        self.assertEqual(result.bucket, MatchInjuryBucket.SPECIAL)
        self.assertEqual(result.recovery_weeks, 6)
        self.assertEqual(result.condition_drop, 35)
        self.assertEqual(rng.calls, [100, 100])

    def test_broken_leg_uses_literal_12_or_26_week_windows(self):
        for severity_roll, expected in ((59, (1, 12, 35)), (60, (2, 26, 60)), (90, (3, 26, 60))):
            players = roster()
            rng = ScriptedRng([99, severity_roll])
            result = generate_persistent_match_injury(
                players[0], players, date(2000, 8, 19), rng
            )
            self.assertEqual(
                (result.severity_code, result.recovery_weeks, result.condition_drop),
                expected,
            )
            self.assertEqual(rng.calls, [100, 100])

    def test_condition_drop_floors_at_one_and_history_weight_tracks_severity(self):
        players = roster(condition=30)
        # Mode 1: ankle, moderate -> drop 35.
        rng = ScriptedRng([0, 50, 0])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng, user_controlled=True
        )
        self.assertEqual(result.severity_code, 1)
        self.assertEqual(players[0].condition, 1)
        self.assertEqual(players[0].injury_history_weight, 4)

    def test_existing_injury_is_not_replaced(self):
        players = roster()
        players[0].injured = True
        players[0].injury_return_date = date(2000, 9, 1)
        rng = ScriptedRng([])
        self.assertIsNone(
            generate_persistent_match_injury(
                players[0], players, date(2000, 8, 19), rng
            )
        )
        self.assertEqual(rng.calls, [])

    def test_expiry_clears_object_state_on_return_date_without_restoring_condition(self):
        players = roster()
        rng = ScriptedRng([3, 49])
        result = generate_persistent_match_injury(
            players[0], players, date(2000, 8, 19), rng
        )
        before = players[0].condition
        self.assertFalse(
            clear_expired_persistent_injury(
                players[0], result.return_date - timedelta(days=1)
            )
        )
        self.assertTrue(players[0].injured)
        self.assertTrue(
            clear_expired_persistent_injury(players[0], result.return_date)
        )
        self.assertFalse(players[0].injured)
        self.assertIsNone(players[0].injury_return_date)
        self.assertIsNone(players[0].injury_source_mode)
        self.assertIsNone(players[0].injury_severity_code)
        self.assertEqual(players[0].condition, before)


if __name__ == "__main__":
    unittest.main()
