import copy
import json
import unittest
from datetime import date
from types import SimpleNamespace
from native_club_capacity_state import (
    SOURCE_SHA256, RetainedClubAllocationCapacities, retained_capacity_lifecycle,
    fresh_windows_club_array_capacity_bytes,
)
from game_state import GameState, GameCalendar
from test_gate_source_materialization import RecordingRng


def receipt():
    return dict(source_sha256=SOURCE_SHA256, stop_reason='selected_club_uncontrolled_read',
        selected_club_import_observed=True, capacity_initializer_proven=False,
        write_watch_coverage=dict(broken=False,
            continuous_all_user_thread_write_watch_coverage_proven=True,
            debug_events_checked_without_gap=True, start_debug_event_number=10,
            stop_debug_event_number=12, checks=3, resumed_events_checked=2,
            checkpoints=[dict(all_live_threads_armed=True,
                native_all_live_threads_armed=True, wow64_all_live_threads_armed=True)]),
        events=[dict(kind='allocation_before_constructor', club_address=0x10000,
                     visiting_capacity_u32=[17, 23]),
                dict(kind='source_breakpoint', source_va=0x5DA538,
                     identity_import_observed=True, observed_club_plus4_word_u16=5,
                     attendance_receiver=dict(address=0x10000, vftable_u32=0x7BD614,
                         plus4_word_u16=5, capacity_u32=[17, 23]))])


class AllocationCapacityTests(unittest.TestCase):
    def test_native_allocator_reads_actual_nonzero_bytes_with_exact_flags_size_and_stride(self):
        import ctypes as c
        import struct
        size = (4 + 7 * 0x2A8 + 15) & ~15
        storage = c.create_string_buffer(size)
        c.memmove(c.addressof(storage)+4+5*0x2A8+0x13C, struct.pack('<II',17,0xFFFFFFFF),8)
        calls=[]
        kernel=SimpleNamespace(
            HeapCreate=lambda *args: calls.append(('create',args)) or 123,
            HeapAlloc=lambda *args: calls.append(('alloc',args)) or c.addressof(storage),
            HeapDestroy=lambda *args: calls.append(('destroy',args)) or 1)
        values=fresh_windows_club_array_capacity_bytes(7,kernel=kernel)
        self.assertEqual(calls,[('create',(0,4096,0)),('alloc',(123,0,size)),('destroy',(123,))])
        self.assertEqual((values[5].plus13c,values[5].plus140),(17,0xFFFFFFFF))
        self.assertEqual(values[5].allocation_kind,'windows-heapalloc-flags0')
        self.assertEqual(values[5].visiting_terrace,0)

    def test_native_allocator_failure_never_supplies_zero_and_always_cleans_owned_heap(self):
        calls=[]
        kernel=SimpleNamespace(HeapCreate=lambda *_: 123,HeapAlloc=lambda *_:None,
            HeapDestroy=lambda *_:calls.append('destroy') or 1)
        with self.assertRaises(MemoryError):
            fresh_windows_club_array_capacity_bytes(7,kernel=kernel)
        self.assertEqual(calls,['destroy'])

    def test_actual_nonzero_bytes_are_retained_not_replaced(self):
        identity, state = retained_capacity_lifecycle(json.dumps(receipt()).encode())
        self.assertEqual(identity, 5)
        self.assertEqual((state.home_terrace, state.visiting_terrace), (17, 23))

    def test_missing_or_broken_coverage_never_becomes_zero(self):
        for key in ('broken', 'continuous_all_user_thread_write_watch_coverage_proven',
                    'debug_events_checked_without_gap', 'checks', 'resumed_events_checked'):
            data = receipt()
            data['write_watch_coverage'][key] = None
            with self.assertRaises(ValueError):
                retained_capacity_lifecycle(json.dumps(data).encode())

    def test_writer_identity_changes_or_single_context_proof_rejected(self):
        variants = [receipt() for _ in range(4)]
        variants[0]['events'].insert(1, dict(kind='hardware_dword_write_after_instruction'))
        variants[1]['events'][-1]['attendance_receiver']['address'] += 4
        variants[2]['write_watch_coverage']['checkpoints'][0]['native_all_live_threads_armed'] = False
        variants[3]['events'][-1]['attendance_receiver']['capacity_u32'][0] = 0
        for data in variants:
            with self.assertRaises(ValueError):
                retained_capacity_lifecycle(json.dumps(data).encode())

    def test_exact_unsigned_clamp_and_validation(self):
        values = RetainedClubAllocationCapacities(200000, 200001, 'a' * 64)
        self.assertEqual((values.home_terrace, values.visiting_terrace), (200000, 0))
        for value in (-1, True, 0x100000000, '0'):
            with self.assertRaises(ValueError):
                RetainedClubAllocationCapacities(value, 0, 'a' * 64)

    def state(self):
        state = GameState(calendar=GameCalendar(date(2000, 8, 19)), players={},
            clubs={5: SimpleNamespace(runtime_value_1c_source=10003), 1: SimpleNamespace()})
        state._premier_league_gate_fan_base_raw = lambda _: 20000
        state._premier_league_gate_side_modifier = lambda *_: 1.0
        return state

    def test_unobserved_home_stays_fail_closed(self):
        state = self.state()
        self.assertIsNone(state._prepare_premier_league_gate_inputs(5, 1, (), (), controlled_club_id=1))
        self.assertEqual(state.native_uncontrolled_capacity_bytes, {})

    def test_raw_fields_map_to_correct_cells_without_away_stadium_substitute(self):
        state = self.state()
        state.native_uncontrolled_capacity_bytes[5] = RetainedClubAllocationCapacities(17, 23, 'a' * 64)
        prepared = state._prepare_premier_league_gate_inputs(5, 1, (), (), controlled_club_id=1)
        self.assertEqual(tuple(prepared[k] for k in ('home_seating_capacity', 'visiting_seating_capacity',
            'home_terrace_capacity', 'visiting_terrace_capacity')), (7502, 2500, 17, 23))
        self.assertEqual(prepared['home_facility_factor'], 1.0)
        self.assertEqual(prepared['visiting_facility_factor'], 1.0)
        self.assertEqual(prepared['host_seating_price'], 30)
        self.assertEqual(state.finance_balances, {})

    def test_known_zero_cells_skip_native_rng_but_do_not_create_report_owner(self):
        state = self.state()
        state.native_uncontrolled_capacity_bytes[5] = RetainedClubAllocationCapacities(0, 0, 'a' * 64)
        prepared = state._prepare_premier_league_gate_inputs(5, 1, (), (), controlled_club_id=1)
        rng = RecordingRng((1, 2))
        result = state._finish_premier_league_gate_receipts(5, prepared, rng, fixture_id=3)
        self.assertEqual(rng.bounds, [32768, 32768])
        self.assertEqual((result.home_terrace.count, result.visiting_terrace.count), (0, 0))
        self.assertEqual(state.captured_match_reports, ())
        self.assertEqual(state.fixture_match_info_links, {})


if __name__ == '__main__':
    unittest.main()
