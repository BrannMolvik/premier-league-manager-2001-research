import unittest
from types import SimpleNamespace
from native_club_report_state import ClubAttendanceCounter, ordinary_human_adjustment
from game_state import GameState, GameCalendar
from datetime import date


class NativeClubReportStateTests(unittest.TestCase):
    def test_bit9_first_write_does_not_read_unknown_counter(self):
        counter = ClubAttendanceCounter.fresh()
        self.assertIsNone(counter.count)
        self.assertIsNone(ordinary_human_adjustment(counter, 0))
        counter = counter.completed_home_gate()
        self.assertEqual(counter, ClubAttendanceCounter(True, 1))
        self.assertEqual(ordinary_human_adjustment(counter, None), 5)
        self.assertEqual(counter.completed_home_gate().count, 2)

    def test_native_byte_wrap(self):
        counter = ClubAttendanceCounter(True, 255).completed_home_gate()
        self.assertEqual(counter.count, 0)
        self.assertEqual(ordinary_human_adjustment(counter, 0), 5)

    def test_rank_guard_does_not_require_guessed_counter(self):
        for counter in (None, ClubAttendanceCounter.fresh(), ClubAttendanceCounter(True, 2)):
            self.assertIsNone(ordinary_human_adjustment(counter, 3))
            self.assertEqual(ordinary_human_adjustment(counter, 4), 5)
            self.assertIsNone(ordinary_human_adjustment(counter, -1))
            self.assertIsNone(ordinary_human_adjustment(counter, True))

    def test_display_fallback_cannot_authorize_adjustment(self):
        state = GameState(GameCalendar(date(2000, 7, 1)), {})
        state.user_controlled_club_id = 5
        state.premier_league = SimpleNamespace(club_ids=(5, 6),
                table=lambda *args: (_ for _ in ()).throw(AssertionError('missing source names')))
        fixture = SimpleNamespace(home_club_id=5, away_club_id=6)
        human = SimpleNamespace(attack_context=SimpleNamespace(user_controlled=True))
        ai = SimpleNamespace(attack_context=SimpleNamespace(user_controlled=False))
        self.assertIsNone(state._ordinary_native_human_adjustment(fixture, human, ai))
        state.native_club_attendance_counters[6] = ClubAttendanceCounter(True, 1)
        self.assertEqual(state._ordinary_native_human_adjustment(fixture, human, ai), 5)

    def test_invalid_counter_state_rejects(self):
        for flags, count in ((1, 1), (True, None), (True, 256), (False, True)):
            with self.assertRaises(ValueError):
                ClubAttendanceCounter(flags, count)

    def test_counter_state_roundtrip_and_duplicate_reject(self):
        from internal_save import snapshot_game_state, restore_game_state
        from test_human_gameplay import Database
        database = Database()
        state = GameState.from_database(database, date(2000, 7, 1), seed=1, season_year=2000)
        club_id = next(iter(state.clubs))
        state.native_club_attendance_counters[club_id] = ClubAttendanceCounter.fresh()
        snapshot = snapshot_game_state(state)
        loaded = restore_game_state(database, snapshot)
        self.assertIsNone(loaded.native_club_attendance_counters[club_id].count)
        state.native_club_attendance_counters[club_id] = ClubAttendanceCounter(True, 255)
        snapshot = snapshot_game_state(state)
        loaded = restore_game_state(database, snapshot)
        self.assertEqual(loaded.native_club_attendance_counters[club_id].completed_home_gate().count, 0)
        snapshot['native_club_attendance_counters'].append(snapshot['native_club_attendance_counters'][0])
        with self.assertRaises(ValueError):
            restore_game_state(database, snapshot)
