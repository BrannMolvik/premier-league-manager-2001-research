"""Native setup contracts, not synthetic report-owner success claims."""
from datetime import date
from types import SimpleNamespace
import unittest

from game_state import GameCalendar, GameState
from complete_fixture_report import LiveReportSetupFragment
from original_fixture_report_capture import NativeCapturedScalar
from ordinary_report_setup import NativeSetupPlayerPool, gate_report_scalar_copies, report_participant_metadata
from original_fixture_report_capture import NATIVE_CAPTURE_SCALAR_COPIES


class RecordingRng:
    def __init__(self, values):
        self.values = iter(values)
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(bound)
        return next(self.values)


class OrdinarySetupTests(unittest.TestCase):
    def test_constructor_seed_uses_distinct_stream_and_explicit_absence(self):
        state = GameState(GameCalendar(date(2000, 7, 1)), {})
        engine = RecordingRng((1234,))
        state._begin_native_report_calculator(7, engine)
        self.assertEqual(engine.bounds, [32767])
        self.assertEqual(state.prepared_match_report_scalars[7][0x94].value,
                         (1234).to_bytes(4, 'little'))
        state._begin_native_report_calculator(7, None)
        self.assertEqual(state.prepared_match_report_scalars[7], {})

    def test_fresh_constructor_cannot_promote_stale_metadata(self):
        state = GameState(GameCalendar(date(2000, 7, 1)), {})
        state.prepared_match_report_metadata[7] = object()
        state.prepared_match_report_tactics[7] = (1, 2)
        state.prepared_match_report_setup[7] = object()
        state._begin_native_report_calculator(7, None)
        self.assertNotIn(7, state.prepared_match_report_metadata)
        self.assertNotIn(7, state.prepared_match_report_tactics)
        self.assertNotIn(7, state.prepared_match_report_setup)

    def test_truncated_original_array_rejects(self):
        for master in (b'', (1).to_bytes(4, 'little')):
            database = SimpleNamespace(master=master,
                core=SimpleNamespace(native_prefix=lambda i, n: b'A' * n))
            with self.assertRaises(ValueError):
                NativeSetupPlayerPool.from_database(database)

    def test_original_array_fallback_and_first_only_retry(self):
        pool = NativeSetupPlayerPool((9, 2, 7), ((), (2,)))
        players = {9: SimpleNamespace(first_name='-'), 2: SimpleNamespace(first_name='Yes'),
                   7: SimpleNamespace(first_name='Other')}
        rng = RecordingRng((0, 1, 0))
        self.assertEqual(pool.draw_pair(1, players, rng), (2, 9))
        self.assertEqual(rng.bounds, [3, 3, 3])

    def test_nationality_pool_threshold_is_strictly_above_ten(self):
        players = {i: SimpleNamespace(first_name='A') for i in range(12)}
        for count, bound in ((10, 12), (11, 11)):
            pool = NativeSetupPlayerPool(tuple(range(12)), (tuple(reversed(range(count))),))
            rng = RecordingRng((0, 1))
            self.assertEqual(pool.draw_pair(0, players, rng),
                             (0, 1) if count == 10 else (10, 9))
            self.assertEqual(rng.bounds, [bound, bound])

    def test_missing_pool_name_withholds_before_rng(self):
        pool = NativeSetupPlayerPool((0,), ((),))
        rng = RecordingRng(())
        self.assertIsNone(pool.draw_pair(0, {}, rng))
        self.assertEqual(rng.bounds, [])

    def test_native_gate_classification_is_self_ratio_not_capacity(self):
        for home, away, flag in ((0, 0, 2), (100, 0, 3), (0, 100, 3), (100, 2, 4)):
            result = SimpleNamespace(home_attendance=home, visiting_attendance=away)
            copies = gate_report_scalar_copies(result, 31)
            self.assertEqual(tuple(int.from_bytes(c.value, 'little') for c in copies),
                             (home + away, 31, home, away, flag))
            self.assertEqual(tuple((c.report_offset, c.calculator_offset, len(c.value)) for c in copies),
                             NATIVE_CAPTURE_SCALAR_COPIES[:5])
        self.assertIsNone(gate_report_scalar_copies(None, 31))
        self.assertIsNone(gate_report_scalar_copies(SimpleNamespace(), None))

    def test_adjustment_and_secondary_shirt_never_default(self):
        players = ((SimpleNamespace(index=5, club_id=1, shirt_number=65),),
                   (SimpleNamespace(index=6, club_id=2, shirt_number=2),))
        result = SimpleNamespace(initial_report_condition_bits=((0, 0, 1), (1, 0, None)),
                                 report_booking_bits=((0, 0, 0), (1, 0, 1)))
        self.assertIsNone(report_participant_metadata((1, 2), players, result))
        result.initial_report_condition_bits = ((0, 0, 1), (1, 0, 0))
        captured = report_participant_metadata((1, 2), players, result)
        self.assertEqual(captured[0][0].shirt_number, 1)
        self.assertEqual(captured[1][0].booked_bit, 1)
        players[1][0].club_id = 3
        self.assertIsNone(report_participant_metadata((1, 2), players, result))

    def test_assembler_seam_requires_every_setup_producer(self):
        state = GameState(GameCalendar(date(2000, 7, 1)), {})
        fixture = SimpleNamespace(id=7, home_club_id=1, away_club_id=2)
        participants = tuple(tuple(SimpleNamespace(index=side * 100 + i,
                            club_id=side + 1, shirt_number=i + 1)
                            for i in range(11)) for side in range(2))
        result = SimpleNamespace(
            initial_report_condition_bits=tuple((s, i, 1) for s in range(2) for i in range(11)),
            report_booking_bits=tuple((s, i, 0) for s in range(2) for i in range(11)))
        state.prepared_match_report_setup[7] = LiveReportSetupFragment(b'Explicit contract', 1, ())
        state.prepared_match_report_tactics[7] = (1, 2)
        values = {d: NativeCapturedScalar(d, s, bytes(n)) for d, s, n in NATIVE_CAPTURE_SCALAR_COPIES}
        state.prepared_match_report_scalars[7] = values
        self.assertTrue(state._complete_native_report_setup(fixture, result, participants))
        self.assertEqual(state.prepared_match_report_metadata[7].team_ids, (1, 2))
        for destination in tuple(values):
            copy = values.pop(destination)
            self.assertFalse(state._complete_native_report_setup(fixture, result, participants))
            self.assertNotIn(7, state.prepared_match_report_metadata)
            values[destination] = copy
        state.prepared_match_report_tactics[7] = None
        self.assertFalse(state._complete_native_report_setup(fixture, result, participants))


if __name__ == '__main__':
    unittest.main()
