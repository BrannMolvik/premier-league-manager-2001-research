import unittest
from types import SimpleNamespace
from native_club_report_state import (
    ClubAttendanceCounter, ordinary_human_adjustment,
    initialize_top_four_opponent_condition,
    produce_human_opponent_condition,
)
from game_state import GameState, GameCalendar
from datetime import date


class NativeClubReportStateTests(unittest.TestCase):
    def test_top_four_producer_guards_unknowns_and_all_four_positions(self):
        class Rng:
            def __init__(self):
                self.bounds = []
            def randbelow(self, bound):
                self.bounds.append(bound)
                return 5
        for rank in range(4):
            rng = Rng()
            player = SimpleNamespace(condition=90)
            self.assertIsNone(produce_human_opponent_condition(
                ClubAttendanceCounter.fresh(), rank, (player,), rng))
            self.assertEqual(rng.bounds, [])
            self.assertEqual(produce_human_opponent_condition(
                ClubAttendanceCounter(True, 1), rank, (player,), rng), 5)
            self.assertEqual(rng.bounds, [])
            self.assertEqual(produce_human_opponent_condition(
                ClubAttendanceCounter(True, 2), rank, (player,), rng), 16)
            self.assertEqual(rng.bounds, [6, 6])
            self.assertEqual(player.condition, 105)
        self.assertIsNone(produce_human_opponent_condition(
            ClubAttendanceCounter(True, 2), 0, (), None))

    def test_top_four_exact_draw_pairs_and_condition_bytes(self):
        for upper in range(6):
            for lower in range(6):
                draws = iter((upper, lower))
                bounds = []
                class Rng:
                    def randbelow(self, bound):
                        bounds.append(bound)
                        return next(draws)
                player = SimpleNamespace(condition=0)
                self.assertEqual(initialize_top_four_opponent_condition((player,), Rng()), 16)
                self.assertEqual(bounds, [6, 6])
                self.assertEqual(player.condition, 90 + (75 * (10 + upper + lower)) // 100)

    def test_top_four_second_full_roster_pass_precedes_snapshot(self):
        from unittest.mock import patch
        from match_preparation import build_premier_league_ai_match_side
        roster = [SimpleNamespace(condition=0) for _ in range(15)]
        bounds = []
        class Rng:
            def randbelow(self, bound):
                bounds.append(bound)
                return 0
        seen = []
        def snapshot(*args, **kwargs):
            seen.extend(p.condition for p in roster)
            return 'side'
        preparation = SimpleNamespace(selection='selection')
        with patch('match_preparation.build_prepared_match_side_from_selection', snapshot):
            side = build_premier_league_ai_match_side(preparation, roster, side=1,
                rng=Rng(), after_condition_initializer=initialize_top_four_opponent_condition)
        self.assertEqual(bounds, [6, 5] * 15 + [6, 6] * 15)
        self.assertEqual(seen, [97] * 15)
        self.assertEqual(side.match_side, 'side')

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

    def test_gate_tail_counter_is_independent_of_unknown_attendance(self):
        state = GameState(GameCalendar(date(2000, 7, 1)), {})
        state.native_club_attendance_counters[6] = ClubAttendanceCounter.fresh()
        class Rng:
            def randbelow(self, limit):
                return 0
        self.assertIsNone(state._finish_premier_league_gate_receipts(6, None, Rng()))
        self.assertEqual(state.native_club_attendance_counters[6], ClubAttendanceCounter(True, 1))

    def test_unretained_cup_lifecycle_invalidates_instead_of_resetting(self):
        from cup_progression import CupMatchResolutionSnapshot
        state = GameState(GameCalendar(date(2000, 7, 1)), {})
        state.cup_results = SimpleNamespace(record_match_resolution=lambda *args: 'recorded')
        state.native_club_attendance_counters = {6: ClubAttendanceCounter(True, 1),
                                               7: ClubAttendanceCounter.fresh()}
        self.assertEqual(state.record_cup_match_resolution((1,),
            CupMatchResolutionSnapshot(6, 7, 0, 0)), 'recorded')
        self.assertEqual(state.native_club_attendance_counters, {})

    def test_native_rank_guard_uses_source_key_and_global_user(self):
        state = GameState(GameCalendar(date(2000, 7, 1)), {},
                          clubs={i: SimpleNamespace(short_name=f'Club {i}') for i in range(6)})
        state.user_controlled_club_id = 5
        def table(key):
            self.assertEqual(key(5), b'Club 5')
            return tuple(SimpleNamespace(club_id=i) for i in range(6))
        state.premier_league = SimpleNamespace(club_ids=tuple(range(6)), table=table)
        fixture = SimpleNamespace(home_club_id=5, away_club_id=1)
        human = SimpleNamespace(attack_context=SimpleNamespace(user_controlled=True))
        ai = SimpleNamespace(attack_context=SimpleNamespace(user_controlled=False))
        self.assertEqual(state._ordinary_native_human_adjustment(fixture, human, ai), 5)
        state.user_controlled_club_id = 4
        self.assertIsNone(state._ordinary_native_human_adjustment(fixture, human, ai))

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
