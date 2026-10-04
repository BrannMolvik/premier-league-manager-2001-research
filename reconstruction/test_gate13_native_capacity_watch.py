"""Bounded debugger ABI/planning contracts; NOT native capacity initialization proof."""
import ctypes
import json
import unittest
from unittest.mock import patch
from pathlib import Path

from gate13_native_capacity_watch import (
    ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ, CAPACITY_OFFSETS,
    CapacityWatchError, DebugEvent, WatchPlan, Wow64Context, arm_writes, observe,
    INSTALL_QUERY_RETURNS, RESOURCE_SELECTOR_RETURNS, STARTUP_SITES,
    GRAPHICS_SUCCESS, CREATE_WINDOW_CALL, qualify_windowed_display,
    require_desktop_safety_qualification,
)


class NativeCapacityWatchTests(unittest.TestCase):
    def test_display_probe_has_fixed_small_bound_and_no_capacity_watch(self):
        with patch('gate13_native_capacity_watch._observe', return_value={}) as observer:
            qualify_windowed_display(Path('original'), Path('private-output'))
        self.assertEqual(observer.call_args.args[2], WatchPlan(seconds=10, max_events=256))
        self.assertEqual(observer.call_args.kwargs, {'qualification_only': True})

    def test_graphics_acceptance_and_pre_window_guard_are_correct_sites(self):
        self.assertIn(GRAPHICS_SUCCESS, STARTUP_SITES)
        self.assertEqual(GRAPHICS_SUCCESS, 0x6153A0)
        self.assertNotIn(0x6151B5, STARTUP_SITES)
        self.assertEqual(CREATE_WINDOW_CALL, 0x6A6363)
        self.assertIn(CREATE_WINDOW_CALL, STARTUP_SITES)

    def test_failed_display_receipt_cannot_authorize_launch(self):
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value={}), \
                patch.object(Path, 'read_text', return_value='{"schema_version":1,"runtime_nonexclusive_qualified":false}'):
            with self.assertRaisesRegex(CapacityWatchError, 'does not qualify'):
                require_desktop_safety_qualification(Path('original'), Path('receipt'))

    def test_only_complete_exact_stage_display_receipt_is_accepted_audio_not_required(self):
        executable = Path('private-stage/original.exe').resolve()
        stage = dict(wrapper_sha256='wrapper', config_sha256='config')
        data = dict(schema_version=2, stop_reason='display_qualification_complete',
                    display_qualification_only=True, runtime_nonexclusive_qualified=True,
                    source_sha256='833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3',
                    private_stage=str(executable.parent), **stage,
                    private_wrapper_load_observed=True, native_graphics_initialization_accepted=True,
                    display_observation=dict(normal_window_observed=True, problems=[]))
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value=stage), \
                patch.object(Path, 'read_text', return_value=json.dumps(data)):
            require_desktop_safety_qualification(executable, Path('receipt'))
        for key, bad in (('schema_version', 1), ('wrapper_sha256', 'other'),
                         ('config_sha256', 'other'), ('private_stage', 'elsewhere'),
                         ('source_sha256', 'other'), ('private_wrapper_load_observed', False),
                         ('native_graphics_initialization_accepted', False),
                         ('runtime_nonexclusive_qualified', False),
                         ('stop_reason', 'display_safety_stop'),
                         ('display_qualification_only', False),
                         ('display_observation', dict(normal_window_observed=False, problems=[])),
                         ('display_observation', dict(normal_window_observed=True, problems=['topmost']))):
            with self.subTest(key=key, bad=bad), \
                    patch('gate13_native_capacity_watch.require_private_output_path'), \
                    patch('gate13_native_capacity_watch.check_private_stage', return_value=stage), \
                    patch.object(Path, 'read_text', return_value=json.dumps(dict(data, **{key: bad}))):
                with self.assertRaisesRegex(CapacityWatchError, 'does not qualify'):
                    require_desktop_safety_qualification(executable, Path('receipt'))

    def test_all_launch_modes_refused_before_read_or_execution_without_desktop_safety(self):
        for mode in ({}, {'stop_at_entry': True}, {'calibrate_crt_writes': True}):
            with self.subTest(mode=mode), self.assertRaisesRegex(CapacityWatchError, 'Original launch disabled'):
                observe(Path('not-an-executable'), Path('not-a-receipt'), WatchPlan(), **mode)

    def test_all_four_native_resource_query_returns_are_observed(self):
        self.assertEqual({INSTALL_QUERY_RETURNS[va] for va in RESOURCE_SELECTOR_RETURNS},
                         {'art', 'fmv', 'matchengine', 'stadia'})
        self.assertTrue(RESOURCE_SELECTOR_RETURNS.issubset(STARTUP_SITES))
        self.assertIn(0x530DD9, STARTUP_SITES)
        self.assertIn(0x50D630, STARTUP_SITES)

    def test_calibration_modes_cannot_be_combined_or_read_an_input(self):
        with self.assertRaisesRegex(CapacityWatchError, 'separate probes'):
            observe(Path('not-an-executable'), Path('not-a-receipt'), WatchPlan(),
                    stop_at_entry=True, calibrate_crt_writes=True)

    def test_source_qualified_lifecycle_sites(self):
        self.assertEqual((ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ),
                         (0x40BC14, 0x40BC43, 0x40BA2C, 0x5DA538))
        self.assertEqual(CAPACITY_OFFSETS, (0x13C, 0x140))

    def test_array_cookie_and_stride_not_club_id(self):
        self.assertEqual(WatchPlan(5).club_address(0x100000, 30), 0x100D4C)
        self.assertEqual(WatchPlan(0).club_address(0x100000, 1), 0x100004)

    def test_fail_closed_bounds(self):
        for kwargs in ({'club_index': -1}, {'club_index': True}, {'seconds': 0},
                       {'seconds': 61}, {'max_events': 0}, {'max_events': 4097}):
            with self.subTest(kwargs=kwargs), self.assertRaises(CapacityWatchError):
                WatchPlan(**kwargs)

    def test_allocation_bounds_and_alignment(self):
        for allocation, count in ((0, 6), (0x100001, 6), (0xFFFFFFF0, 6),
                                  (0x100000, 5), (0x100000, 4097)):
            with self.subTest(allocation=allocation, count=count), self.assertRaises(CapacityWatchError):
                WatchPlan().club_address(allocation, count)

    def test_native_wow64_context_layout(self):
        self.assertEqual(ctypes.sizeof(Wow64Context), 716)
        self.assertEqual(Wow64Context.Eip.offset, 184)
        self.assertEqual(Wow64Context.EFlags.offset, 192)
        self.assertEqual(Wow64Context.Dr7.offset, 24)

    @unittest.skipUnless(ctypes.sizeof(ctypes.c_void_p) == 8, '64-bit debugger ABI')
    def test_host_debug_event_layout(self):
        self.assertEqual(ctypes.sizeof(DebugEvent), 176)
        self.assertEqual(DebugEvent.u.offset, 16)

    def test_watch_is_exact_two_dword_writes_not_execute_or_values(self):
        context = Wow64Context()
        context.Eax, context.Eip = 0x12345678, 0x403660
        context.Dr2, context.Dr3, context.Dr6 = 99, 98, 3
        arm_writes(context, 0x100000)
        self.assertEqual((context.Dr0, context.Dr1), (0x10013C, 0x100140))
        self.assertEqual((context.Dr2, context.Dr3, context.Dr6), (0, 0, 0))
        self.assertEqual(context.Dr7, 0xDD0005)
        self.assertEqual((context.Eax, context.Eip), (0x12345678, 0x403660))

    def test_bad_watch_receiver_rejected(self):
        for value in (0, 0x100001, 0xFFFFFFF0):
            with self.subTest(value=value), self.assertRaises(CapacityWatchError):
                arm_writes(Wow64Context(), value)


if __name__ == '__main__':
    unittest.main()
