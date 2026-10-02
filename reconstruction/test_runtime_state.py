import unittest
from dataclasses import dataclass
from datetime import date, timedelta
from types import SimpleNamespace
from commercial_timers import UserCommercialTimerState
from game_state import GameCalendar, GameState
from match_schedule import MsvcCrtRng
from stadium_state import (
    MAP_HEADER_SIZE,
    MAP_TRAILING_SIZE,
    StadiumBuildingDefinition,
    StadiumBuildingInstance,
    StadiumSourceState,
)
from runtime_state import (
    RuntimePlayer,
    age_on,
    normalize_current_club_join_date,
)


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


class JoinDateNormalizationTests(unittest.TestCase):
    def test_old_or_future_join_dates_fall_back_to_200_days_ago(self):
        current = date(2000, 8, 18)
        self.assertEqual(
            normalize_current_club_join_date(date(1950, 1, 1), current),
            current - timedelta(days=200),
        )
        self.assertEqual(
            normalize_current_club_join_date(date(2000, 12, 1), current),
            current - timedelta(days=200),
        )

    def test_plausible_join_date_is_preserved(self):
        current = date(2000, 8, 18)
        joined = date(2000, 6, 1)
        self.assertEqual(
            normalize_current_club_join_date(joined, current),
            joined,
        )


class RuntimePlayerTests(unittest.TestCase):
    def test_age_on_birthday_boundary(self):
        dob = date(1980, 6, 15)
        self.assertEqual(age_on(dob, date(2000, 6, 14)), 19)
        self.assertEqual(age_on(dob, date(2000, 6, 15)), 20)

    def test_database_player_becomes_mutable_runtime_player(self):
        player = RuntimePlayer.from_database_player(FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1))
        self.assertEqual(player.full_name, "Test Player")
        self.assertEqual(player.current_raw, [100] * 17)
        player.current_raw[0] = 101
        self.assertEqual(player.current_raw[0], 101)
        self.assertIsNotNone(player.development)
        self.assertEqual(player.development.baseline_age, 20)

    def test_single_player_startup_consumes_exact_crt_draw_sequence(self):
        rng = MsvcCrtRng(1)
        player = RuntimePlayer.from_database_player(
            FakePlayer(),
            date(2000, 7, 1),
            rng,
        )

        self.assertEqual(player.morale, 100)
        self.assertEqual(
            (
                player.development.peak_ages.physical,
                player.development.peak_ages.skill,
                player.development.peak_ages.late,
            ),
            (25, 28, 31),
        )
        self.assertEqual(player.startup_month_span, 36)
        self.assertEqual(rng.state, 0x3D6C1037)

    def test_base_match_unavailable_tracks_low_three_exclusion_states(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(),
            date(2000, 7, 1),
            MsvcCrtRng(1),
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
            MsvcCrtRng(1),
        )

        self.assertEqual(player.condition, 80)
        self.assertEqual(player.form_state, 2)
        self.assertEqual(player.current_position, 12)
        self.assertEqual(player.position_aux_code, 0)
        self.assertEqual(player.balance_position_code, 10)
        self.assertFalse(player.non_eu)
        self.assertEqual(player.skills, (100,) * 17)
        self.assertEqual(player.preferred_positions, (12, 18, 0))

    def test_current_role_rating_uses_exact_assigned_role_helper(self):
        subject = FakePlayer(positions=(12, 18, 0))
        player = RuntimePlayer.from_database_player(
            subject,
            date(2000, 7, 1),
            MsvcCrtRng(1),
        )
        from match_role_rating import role_rating

        self.assertEqual(
            player.current_role_rating(),
            role_rating(player.skills, 12, player.preferred_positions),
        )
        player.assign_match_position(18, 0)
        self.assertEqual(
            player.current_role_rating(),
            role_rating(player.skills, 18, player.preferred_positions),
        )

    def test_match_position_assignment_and_reset_preserve_balance_code(self):
        subject = FakePlayer(positions=(12, 18, 0))
        player = RuntimePlayer.from_database_player(
            subject,
            date(2000, 7, 1),
            MsvcCrtRng(1),
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
            MsvcCrtRng(1),
        )
        self.assertEqual(player.player_index, 42)

    def test_clear_selection_can_apply_exact_position_reset(self):
        subject = FakePlayer(positions=(12, 18, 0))
        player = RuntimePlayer.from_database_player(
            subject,
            date(2000, 7, 1),
            MsvcCrtRng(1),
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
            MsvcCrtRng(1),
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
        player = RuntimePlayer.from_database_player(young, date(2000, 7, 1), MsvcCrtRng(1))
        self.assertEqual(player.development.baseline_age, 15)

    def test_monthly_update_mutates_current_skills(self):
        player = RuntimePlayer.from_database_player(FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1))
        before = tuple(player.current_raw)
        changed = player.monthly_development_update(date(2001, 7, 1))
        self.assertTrue(changed)
        self.assertNotEqual(tuple(player.current_raw), before)

    def test_training_state_uses_original_fresh_defaults(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        self.assertEqual(player.training_method_id, 5)
        self.assertEqual(player.training_countdown, 8)
        self.assertEqual(player.training_active_count, 0)
        self.assertEqual(player.training_modifiers, [0] * 17)
        self.assertEqual(player.training_skill_states, [1] * 17)
        self.assertEqual(player.training_method_results, [0] * 7)

    def test_training_method_change_preserves_accumulated_training_state(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        player.training_countdown = 3
        player.training_active_count = 2
        player.training_modifiers[4] = 2
        player.training_skill_states[4] = 0
        player.training_method_results[5] = 7

        player.set_training_method(2)

        self.assertEqual(player.training_method_id, 2)
        self.assertEqual(player.training_countdown, 3)
        self.assertEqual(player.training_active_count, 2)
        self.assertEqual(player.training_modifiers[4], 2)
        self.assertEqual(player.training_skill_states[4], 0)
        self.assertEqual(player.training_method_results[5], 7)
        with self.assertRaisesRegex(ValueError, "0..6"):
            player.set_training_method(7)

    def test_daily_training_condition_recovery_fresh_threshold(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        rng = MsvcCrtRng(0x73FCE2C8)

        draws = player.run_daily_training_condition_recovery(rng, 50)

        self.assertEqual(draws, 3)
        self.assertEqual(player.condition, 82)
        self.assertEqual(rng.state, 0x2284D03D)

    def test_daily_training_condition_recovery_high_condition_extra_draws(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        player.condition = 91
        rng = MsvcCrtRng(1)

        draws = player.run_daily_training_condition_recovery(rng, 50)

        self.assertEqual(draws, 5)
        self.assertEqual(player.condition, 91)
        self.assertEqual(rng.state, 0xCAE1DF84)

    def test_daily_training_condition_recovery_injury_skips_rng(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        player.injured = True
        rng = MsvcCrtRng(0x12345678)
        before = rng.state

        draws = player.run_daily_training_condition_recovery(rng, 50)

        self.assertEqual(draws, 0)
        self.assertEqual(player.condition, 80)
        self.assertEqual(rng.state, before)

    def test_weekly_training_exclusion_uses_injury_and_selection_bit_not_suspension(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        self.assertFalse(player.weekly_training_excluded)
        player.suspended = True
        self.assertFalse(player.weekly_training_excluded)
        player.injured = True
        self.assertTrue(player.weekly_training_excluded)
        player.injured = False
        player.selection_excluded = True
        self.assertTrue(player.weekly_training_excluded)

    def test_weekly_fitness_training_consumes_exact_six_draws_and_applies_success(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        # Use a fresh RNG here so the weekly stream is easy to assert exactly.
        rng = MsvcCrtRng(1)

        draws = player.run_weekly_training_primary(rng, 1.0)

        self.assertEqual(draws, 6)
        self.assertEqual(rng.state, 0x3D6C1037)
        self.assertEqual(player.training_countdown, 7)
        self.assertEqual(player.current_raw[0], 108)
        self.assertEqual(player.training_modifiers[0], 1)
        self.assertEqual(player.training_active_count, 1)
        self.assertEqual(player.training_method_results[5], 1)
        self.assertEqual(
            [i for i, value in enumerate(player.training_modifiers) if value],
            [0],
        )

    def test_rest_countdown_boundary_reverses_without_consuming_rng(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        player.set_training_method(0)
        player.training_countdown = 1
        player.training_modifiers[0] = 1
        player.training_skill_states[0] = 1
        player.training_active_count = 1
        player.current_raw[0] = 108
        rng = MsvcCrtRng(0x12345678)
        before = rng.state

        draws = player.run_weekly_training_primary(rng, 1.0)

        self.assertEqual(draws, 0)
        self.assertEqual(rng.state, before)
        self.assertEqual(player.training_countdown, 8)
        self.assertEqual(player.training_modifiers[0], 0)
        self.assertEqual(player.training_skill_states[0], 0)
        self.assertEqual(player.training_active_count, 0)
        self.assertEqual(player.current_raw[0], 100)

    def test_ineligible_weekly_training_consumes_no_rng_or_countdown(self):
        player = RuntimePlayer.from_database_player(
            FakePlayer(), date(2000, 7, 1), MsvcCrtRng(1)
        )
        player.injured = True
        rng = MsvcCrtRng(0x12345678)
        before = rng.state

        draws = player.run_weekly_training_primary(rng, 1.0)

        self.assertEqual(draws, 0)
        self.assertEqual(rng.state, before)
        self.assertEqual(player.training_countdown, 8)

    def test_nonzero_weight_consumes_rng_even_when_skill_is_already_at_target(self):
        subject = FakePlayer(
            current_raw=(180,) * 17,
            target_raw=(180,) * 17,
        )
        player = RuntimePlayer.from_database_player(
            subject, date(2000, 7, 1), MsvcCrtRng(1)
        )
        rng = MsvcCrtRng(1)

        draws = player.run_weekly_training_primary(rng, 1.0)

        self.assertEqual(draws, 6)
        self.assertEqual(rng.state, 0x3D6C1037)
        self.assertEqual(player.training_active_count, 0)
        self.assertEqual(player.training_modifiers, [0] * 17)


class RecordingRng:
    def __init__(self):
        self.calls = []

    def randbelow(self, bound):
        bound = int(bound)
        self.calls.append(bound)
        if bound == 800:
            return 150
        return 0


class UserTrainingDayTests(unittest.TestCase):
    def _state_with_two_players(self, on_date):
        players = [
            RuntimePlayer.from_database_player(
                FakePlayer(index=10), on_date, MsvcCrtRng(10)
            ),
            RuntimePlayer.from_database_player(
                FakePlayer(index=11), on_date, MsvcCrtRng(11)
            ),
        ]
        state = GameState.from_players(players, on_date)
        state.user_controlled_club_id = 0
        return state

    def test_user_training_day_preserves_daily_before_weekly_rng_order(self):
        state = self._state_with_two_players(date(2000, 7, 1))
        rng = MsvcCrtRng(1)

        daily_draws, weekly_draws = state.run_user_training_primary_day(
            rng,
            recovery_threshold=50,
            quality_multiplier=1.30,
        )

        self.assertEqual((daily_draws, weekly_draws), (6, 12))
        self.assertEqual(rng.state, 0xAEA69ED3)

    def test_user_training_day_non_saturday_runs_only_daily_recovery(self):
        state = self._state_with_two_players(date(2000, 7, 2))
        rng = MsvcCrtRng(1)

        daily_draws, weekly_draws = state.run_user_training_primary_day(
            rng,
            recovery_threshold=50,
            quality_multiplier=1.30,
        )

        self.assertEqual((daily_draws, weekly_draws), (6, 0))
        self.assertEqual(rng.state, 0x3D6C1037)

    def test_configured_training_runs_inside_normal_day_progression(self):
        state = self._state_with_two_players(date(2000, 7, 7))
        state.rng = MsvcCrtRng(1)
        state.configure_user_training_calendar(
            recovery_threshold=50,
            quality_multiplier=1.30,
        )

        state.advance_one_day()

        self.assertEqual(state.calendar.current_date, date(2000, 7, 8))
        self.assertEqual(state.rng.state, 0xAEA69ED3)
        self.assertEqual(
            [player.training_countdown for player in state.ordered_club_roster(0)],
            [7, 7],
        )

    def test_commercial_rng_precedes_training_rng_in_normal_progression(self):
        state = self._state_with_two_players(date(2000, 7, 7))
        rng = RecordingRng()
        state.rng = rng
        state.configure_user_training_calendar(
            recovery_threshold=50,
            quality_multiplier=1.30,
        )

        building = StadiumBuildingDefinition(
            building_id=0,
            first_extent=1,
            second_extent=1,
            terrace_capacity=0,
            auxiliary_capacity=0,
            seating_capacity=0,
            concession_capacity=2,
        )
        instance = StadiumBuildingInstance(
            first_min=0,
            second_min=0,
            first_max=1,
            second_max=1,
            building_id=0,
            rotation=0,
            flags=0,
            section_index=0,
        )
        sections = [None] * 26
        sections[0] = instance
        state.stadium_sources[0] = StadiumSourceState(
            buildings=(building,),
            instances=[instance],
            section_instances=tuple(sections),
            initial_section_states=(0,) * 26,
            map_state=bytes(MAP_HEADER_SIZE),
            trailing_state=bytes(MAP_TRAILING_SIZE),
        )
        state.clubs[0] = SimpleNamespace(
            fan_base_index=0,
            runtime_value_1c_source=20,
        )
        state.access_fan_bases = (SimpleNamespace(values=(40,)),)
        state.configure_user_commercial_calendar()
        state.user_commercial_timers = UserCommercialTimerState(
            concession_wait_days=1,
            concession_elapsed_days=1,
            sponsor_wait_days=99,
            sponsor_elapsed_days=1,
        )

        state.advance_one_day()

        # Expired concession: RNG(800), accepted RNG(25), offer-lifetime RNG(3).
        # Only then may the two-player daily/weekly training path consume RNG(100).
        self.assertEqual(rng.calls[:3], [800, 25, 3])
        self.assertEqual(rng.calls[3:21], [100] * 18)
        self.assertEqual(state.calendar.current_date, date(2000, 7, 8))
        self.assertEqual(state.user_commercial_timers.concession_wait_days, 0)
        self.assertEqual(
            [player.training_countdown for player in state.ordered_club_roster(0)],
            [7, 7],
        )

    def test_unconfigured_normal_day_progression_does_not_consume_training_rng(self):
        state = self._state_with_two_players(date(2000, 7, 2))
        state.rng = MsvcCrtRng(1)

        state.advance_one_day()

        self.assertEqual(state.calendar.current_date, date(2000, 7, 3))
        self.assertEqual(state.rng.state, 1)
        self.assertEqual(
            [player.condition for player in state.ordered_club_roster(0)],
            [80, 80],
        )

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
        runtime = RuntimePlayer.from_database_player(FakePlayer(), date(2000, 1, 31), MsvcCrtRng(1))
        state = GameState.from_players([runtime], date(2000, 1, 31))
        self.assertEqual(state.monthly_player_updates, 0)
        state.advance_one_day()
        self.assertEqual(state.monthly_player_updates, 1)


if __name__ == "__main__":
    unittest.main()
