import unittest
from dataclasses import dataclass
from datetime import date
from random import Random

from game_state import GameCalendar, GameState
from runtime_state import RuntimePlayer, age_on


@dataclass(frozen=True)
class FakePlayer:
    index: int = 10
    first_name: str = "Test"
    surname: str = "Player"
    club_id: int = 0
    nationality_id: int = 0
    date_of_birth: date | None = date(1980, 6, 15)
    shirt_number: int = 9
    height_cm: int = 180
    weight_kg: int = 75
    positions: tuple[int, int, int] = (0, 1, 2)
    current_raw: tuple[int, ...] = (100,) * 17
    target_raw: tuple[int, ...] = (180,) * 17


class RuntimePlayerTests(unittest.TestCase):
    def test_age_on_birthday_boundary(self):
        dob = date(1980, 6, 15)
        self.assertEqual(age_on(dob, date(2000, 6, 14)), 19)
        self.assertEqual(age_on(dob, date(2000, 6, 15)), 20)

    def test_database_player_becomes_mutable_runtime_player(self):
        player = RuntimePlayer.from_database_player(FakePlayer(), date(2000, 7, 1), Random(1))
        self.assertEqual(player.full_name, "Test Player")
        self.assertEqual(player.current_raw, [100] * 17)
        player.current_raw[0] = 101
        self.assertEqual(player.current_raw[0], 101)
        self.assertIsNotNone(player.development)
        self.assertEqual(player.development.baseline_age, 20)

    def test_base_match_unavailable_tracks_low_three_exclusion_states(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(),
            date(2000, 7, 1),
            Random(1),
        )
        self.assertFalse(player.base_match_unavailable)

        player.injured = True
        self.assertTrue(player.base_match_unavailable)
        player.injured = False

        player.suspended = True
        self.assertTrue(player.base_match_unavailable)
        player.suspended = False

        player.selection_excluded = True
        self.assertTrue(player.base_match_unavailable)

    def test_database_player_gets_exact_initial_match_state(self):
        subject = FakePlayer(positions=(12, 18, 0))
        player = RuntimePlayer.from_database_player(
            subject,
            date(2000, 7, 1),
            Random(1),
        )

        self.assertEqual(player.condition, 80)
        self.assertEqual(player.form_state, 2)
        self.assertEqual(player.current_position, 12)
        self.assertEqual(player.position_aux_code, 0)
        self.assertEqual(player.balance_position_code, 10)
        self.assertEqual(player.skills, (100,) * 17)
        self.assertEqual(player.preferred_positions, (12, 18, 0))

    def test_match_position_assignment_and_reset_preserve_balance_code(self):
        subject = FakePlayer(positions=(12, 18, 0))
        player = RuntimePlayer.from_database_player(
            subject,
            date(2000, 7, 1),
            Random(1),
        )

        player.assign_match_position(19, 2)
        self.assertEqual(player.current_position, 19)
        self.assertEqual(player.position_aux_code, 2)
        self.assertEqual(player.balance_position_code, 10)

        player.reset_match_position()
        self.assertEqual(player.current_position, 12)
        self.assertEqual(player.position_aux_code, 0)
        self.assertEqual(player.balance_position_code, 10)

    def test_runtime_player_exposes_selection_player_index_alias(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(index=42),
            date(2000, 7, 1),
            Random(1),
        )
        self.assertEqual(player.player_index, 42)

    def test_clear_selection_can_apply_exact_position_reset(self):
        subject = FakePlayer(positions=(12, 18, 0))
        player = RuntimePlayer.from_database_player(
            subject,
            date(2000, 7, 1),
            Random(1),
        )
        player.assign_match_position(19, 2)
        player.set_match_active()

        player.clear_match_selection(reset_position=True)

        self.assertFalse(player.match_active)
        self.assertFalse(player.match_substitute_available)
        self.assertEqual(player.current_position, 12)
        self.assertEqual(player.position_aux_code, 0)
        self.assertEqual(player.balance_position_code, 10)

    def test_match_selection_flags_are_mutually_exclusive(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(),
            date(2000, 7, 1),
            Random(1),
        )
        self.assertFalse(player.match_active)
        self.assertFalse(player.match_substitute_available)

        player.set_match_active()
        self.assertTrue(player.match_active)
        self.assertFalse(player.match_substitute_available)

        player.set_match_substitute_available()
        self.assertFalse(player.match_active)
        self.assertTrue(player.match_substitute_available)

        player.clear_match_selection()
        self.assertFalse(player.match_active)
        self.assertFalse(player.match_substitute_available)

    def test_initializer_clamps_stored_baseline_age(self):
        young = FakePlayer(date_of_birth=date(1995, 1, 1))
        player = RuntimePlayer.from_database_player(young, date(2000, 7, 1), Random(1))
        self.assertEqual(player.development.baseline_age, 15)

    def test_monthly_update_mutates_current_skills(self):
        player = RuntimePlayer.from_database_player(FakePlayer(), date(2000, 7, 1), Random(1))
        before = tuple(player.current_raw)
        changed = player.monthly_development_update(date(2001, 7, 1))
        self.assertTrue(changed)
        self.assertNotEqual(tuple(player.current_raw), before)


class CalendarTests(unittest.TestCase):
    def test_monthly_hook_fires_when_entering_first_day(self):
        calls = []
        cal = GameCalendar(date(2000, 1, 31))
        cal.monthly_hooks.append(calls.append)
        cal.advance_one_day()
        self.assertEqual(cal.current_date, date(2000, 2, 1))
        self.assertEqual(calls, [date(2000, 2, 1)])

    def test_monthly_hook_fires_once_across_month_boundary(self):
        calls = []
        cal = GameCalendar(date(2000, 1, 30))
        cal.monthly_hooks.append(calls.append)
        cal.advance(4)
        self.assertEqual(calls, [date(2000, 2, 1)])

    def test_game_state_runs_player_updates_on_month_boundary(self):
        runtime = RuntimePlayer.from_database_player(FakePlayer(), date(2000, 1, 31), Random(1))
        state = GameState.from_players([runtime], date(2000, 1, 31))
        self.assertEqual(state.monthly_player_updates, 0)
        state.advance_one_day()
        self.assertEqual(state.monthly_player_updates, 1)


if __name__ == "__main__":
    unittest.main()
