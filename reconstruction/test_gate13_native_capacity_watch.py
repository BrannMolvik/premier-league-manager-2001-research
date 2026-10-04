"""Bounded debugger ABI/planning contracts; NOT native capacity initialization proof."""
import ctypes
import json
import struct
import unittest
from unittest.mock import patch
from pathlib import Path
from datetime import datetime, timezone, timedelta

from gate13_native_capacity_watch import (
    ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ, CAPACITY_OFFSETS,
    CapacityWatchError, DebugEvent, WatchPlan, Wow64Context, arm_writes, observe,
    INSTALL_QUERY_RETURNS, RESOURCE_SELECTOR_RETURNS, STARTUP_SITES,
    GRAPHICS_SUCCESS, CREATE_WINDOW_CALL, qualify_windowed_display,
    require_desktop_safety_qualification,
    window_presentation_adaptation, CREATE_WINDOW_INSTRUCTION, PRESENTATION_SHIM,
    FOREGROUND_REQUEST,
    trace_window_activation,
    SupervisedWatchPlan, observe_supervised, write_watch_observation,
    all_thread_write_watch_readback, finalize_user_thread_write_watch_coverage,
    attendance_receiver_observation,
    renew_display_activation_consent,
    STARTUP_SURFACE_RETURNS, startup_surface_return_observation,
    trace_startup_surface_returns,
    native_control_debug_observation, AMD64_CONTEXT_SIZE, AMD64_CONTROL_DEBUG,
    native_write_watch_context,
)


class NativeCapacityWatchTests(unittest.TestCase):
    def test_native_watch_setter_selects_only_debug_registers_not_game_control(self):
        raw = native_write_watch_context(0x100000)
        self.assertEqual(len(raw), AMD64_CONTEXT_SIZE)
        self.assertEqual(struct.unpack_from('<I', raw, 0x30)[0], 0x100010)
        self.assertEqual(struct.unpack_from('<6Q', raw, 0x48), (0x10013C, 0x100140, 0, 0, 0, 0xDD0005))
        self.assertEqual(raw[:0x30], bytes(0x30))
        self.assertEqual(raw[0x34:0x48], bytes(0x14))
        self.assertEqual(raw[0x78:], bytes(AMD64_CONTEXT_SIZE - 0x78))

    def test_native_watch_setter_rejects_unqualified_receiver(self):
        for receiver in (0, True, -1, 0x100001, 0xFFFFFFFF):
            with self.assertRaises(CapacityWatchError):
                native_write_watch_context(receiver)

    def test_native_context_diagnostic_preserves_64bit_registers_without_coverage_override(self):
        raw = bytearray(AMD64_CONTEXT_SIZE)
        struct.pack_into('<I', raw, 0x30, AMD64_CONTROL_DEBUG)
        struct.pack_into('<H', raw, 0x38, 0x33)
        struct.pack_into('<I', raw, 0x44, 0x202)
        struct.pack_into('<6Q', raw, 0x48, 0x12340000, 0x12340004, 0, 0, 0, 0xDD0005)
        struct.pack_into('<Q', raw, 0x98, 0x7FFE12345670)
        struct.pack_into('<Q', raw, 0xF8, 0x7FFE99887766)
        result = native_control_debug_observation(bytes(raw))
        self.assertEqual(result['Dr7'], 0xDD0005)
        self.assertEqual(result['Rip'], 0x7FFE99887766)
        self.assertEqual(result['Rsp'], 0x7FFE12345670)
        self.assertEqual(result['SegCs'], 0x33)
        self.assertTrue(result['observation_only_not_coverage_override'])

    def test_native_context_diagnostic_rejects_missing_flags_and_wrong_layout(self):
        for raw in (bytes(AMD64_CONTEXT_SIZE), bytes(AMD64_CONTEXT_SIZE - 1), bytearray(AMD64_CONTEXT_SIZE)):
            with self.assertRaises(CapacityWatchError):
                native_control_debug_observation(raw)

    def test_supervised_surface_guard_keeps_fixed_capacity_plan_and_live_consent(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=10)
        with patch('gate13_native_capacity_watch.require_desktop_safety_qualification', return_value=until), \
                patch('gate13_native_capacity_watch._observe', return_value={}) as observer, \
                patch.object(Path, 'write_text'):
            result = observe_supervised(Path('original'), Path('private'),
                display_receipt=Path('qualified'), approved_until_utc=until, guard_startup_surfaces=True)
        self.assertEqual(observer.call_args.args[2], SupervisedWatchPlan(club_index=5))
        self.assertEqual(observer.call_args.kwargs, dict(activation_trace_until=until,
            allow_approved_activation_qualification=True, guard_startup_surfaces=True))
        self.assertTrue(result['supervised_human_operated'])

    def test_supervised_surface_guard_cannot_be_enabled_by_truthy_nonboolean(self):
        with self.assertRaisesRegex(CapacityWatchError, 'explicit boolean'):
            observe_supervised(Path('not-read'), Path('not-written'), display_receipt=Path('none'),
                approved_until_utc=datetime.now(timezone.utc), guard_startup_surfaces=1)

    def test_surface_guard_cannot_run_under_ordinary_plan_or_without_activation(self):
        from gate13_native_capacity_watch import _observe
        for plan, approved in ((WatchPlan(seconds=60, max_events=4096), True),
                               (SupervisedWatchPlan(), False)):
            with self.assertRaisesRegex(CapacityWatchError, 'distinct approved'):
                _observe(Path('not-read'), Path('not-written'), plan, guard_startup_surfaces=True,
                         allow_approved_activation_qualification=approved)

    def test_surface_trace_is_separate_and_has_exact_bound(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=10)
        with patch('gate13_native_capacity_watch.require_desktop_safety_qualification', return_value=until), \
                patch('gate13_native_capacity_watch._observe', return_value={}) as observer:
            trace_startup_surface_returns(Path('original'), Path('private'), display_receipt=Path('qualified'))
        plan = observer.call_args.args[2]
        self.assertEqual((plan.seconds, plan.max_events), (60, 4096))
        self.assertTrue(observer.call_args.kwargs['startup_surface_trace_only'])

    def test_surface_trace_refuses_missing_or_insufficient_activation_consent(self):
        for until in (None, datetime.now(timezone.utc) + timedelta(seconds=30)):
            with patch('gate13_native_capacity_watch.require_desktop_safety_qualification', return_value=until), \
                    patch('gate13_native_capacity_watch._observe') as observer:
                with self.assertRaises(CapacityWatchError):
                    trace_startup_surface_returns(Path('original'), Path('private'), display_receipt=Path('qualified'))
                observer.assert_not_called()

    def test_surface_diagnostic_sites_do_not_extend_ordinary_or_one_shot_probes(self):
        from gate13_native_capacity_watch import ONE_SHOT_SITES
        self.assertEqual(STARTUP_SURFACE_RETURNS, {0x5EE232: 0x1C, 0x5EE252: 0x88})
        self.assertTrue(set(STARTUP_SURFACE_RETURNS).isdisjoint(STARTUP_SITES))
        self.assertTrue(set(STARTUP_SURFACE_RETURNS).isdisjoint(ONE_SHOT_SITES))

    def test_surface_diagnostic_cannot_mix_with_other_modes_or_expand_bounds(self):
        from gate13_native_capacity_watch import _observe
        for plan, options in ((WatchPlan(seconds=10), {}),
                              (WatchPlan(seconds=60, max_events=4096), {'qualification_only': True}),
                              (WatchPlan(seconds=60, max_events=4096), {'calibrate_crt_writes': True}),
                              (WatchPlan(seconds=60, max_events=4096), {'stop_at_entry': True})):
            with patch('gate13_native_capacity_watch.check_private_stage') as stage:
                with self.assertRaisesRegex(CapacityWatchError, 'separate fixed'):
                    _observe(Path('not-read'), Path('not-written'), plan,
                             startup_surface_trace_only=True, **options)
                stage.assert_not_called()

    def test_surface_return_retains_actual_hresult_and_pointer_without_edit(self):
        raw = bytearray(108)
        struct.pack_into('<I', raw, 0, 108)
        struct.pack_into('<i', raw, 0x10, 1600)
        struct.pack_into('<I', raw, 0x24, 0x12340000)
        original = bytes(raw)
        for address, offset in STARTUP_SURFACE_RETURNS.items():
            good = startup_surface_return_observation(address, 0, original)
            self.assertFalse(good['diagnostic_stop_required'])
            self.assertEqual(good['descriptor_stack_offset'], offset)
            self.assertEqual(good['raw_descriptor'], original.hex())
            failed = startup_surface_return_observation(address, 0x887601C2, original)
            self.assertEqual(failed['hresult_u32'], 0x887601C2)
            self.assertTrue(failed['diagnostic_stop_required'])
        self.assertEqual(bytes(raw), original)

    def test_surface_return_null_or_malformed_descriptor_stops_even_on_zero_hresult(self):
        raw = bytearray(108)
        struct.pack_into('<I', raw, 0, 108)
        self.assertTrue(startup_surface_return_observation(0x5EE232, 0, bytes(raw))['diagnostic_stop_required'])
        struct.pack_into('<I', raw, 0x24, 0x12340000)
        struct.pack_into('<I', raw, 0, 0)
        self.assertTrue(startup_surface_return_observation(0x5EE232, 0, bytes(raw))['diagnostic_stop_required'])

    def test_surface_return_wrong_source_or_input_rejected(self):
        for address, hresult, raw in ((0x5EE233, 0, bytes(108)), (0x5EE232, -1, bytes(108)),
                                     (0x5EE232, True, bytes(108)), (0x5EE232, 0, bytes(107))):
            with self.assertRaises(CapacityWatchError):
                startup_surface_return_observation(address, hresult, raw)

    def test_consent_renewal_never_overwrites_receipt(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=10)
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch.object(Path, 'exists', return_value=True), \
                patch.object(Path, 'read_bytes') as reader:
            with self.assertRaisesRegex(CapacityWatchError, 'Preserve prior'):
                renew_display_activation_consent(Path('original'), Path('prior'), Path('next'),
                                                approved_until_utc=until)
            reader.assert_not_called()

    def test_consent_renewal_cannot_promote_failed_physical_evidence(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=10)
        data = dict(approved_activation_windowed_qualification=True,
                    activation_approval_expiry_utc='2000-01-01T00:00:00+00:00',
                    runtime_nonexclusive_qualified=False)
        written = []
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value={}), \
                patch.object(Path, 'exists', return_value=False), \
                patch.object(Path, 'read_bytes', return_value=json.dumps(data).encode()), \
                patch.object(Path, 'write_text', side_effect=lambda payload, **kw: written.append(payload)), \
                patch.object(Path, 'read_text', side_effect=lambda **kw: written[-1]):
            with self.assertRaisesRegex(CapacityWatchError, 'does not qualify'):
                renew_display_activation_consent(Path('original'), Path('prior'), Path('next'),
                                                approved_until_utc=until)
        renewed = json.loads(written[0])
        self.assertFalse(renewed['runtime_nonexclusive_qualified'])
        self.assertFalse(renewed['explicit_human_consent_renewal']['new_runtime_observation_claimed'])
        self.assertEqual(data['activation_approval_expiry_utc'], '2000-01-01T00:00:00+00:00')

    def test_supervised_probe_refuses_insufficient_remaining_time(self):
        until = datetime.now(timezone.utc) + timedelta(seconds=60)
        with patch('gate13_native_capacity_watch.require_desktop_safety_qualification', return_value=until), \
                patch('gate13_native_capacity_watch.observe') as observer:
            with self.assertRaisesRegex(CapacityWatchError, 'cover the five-minute'):
                observe_supervised(Path('original'), Path('output'),
                                   display_receipt=Path('receipt'), approved_until_utc=until)
            observer.assert_not_called()

    def test_supervised_probe_passes_only_the_exact_fixed_plan(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=10)
        with patch('gate13_native_capacity_watch.require_desktop_safety_qualification', return_value=until), \
                patch('gate13_native_capacity_watch.observe', return_value={}) as observer, \
                patch.object(Path, 'write_text'):
            result = observe_supervised(Path('original'), Path('output'), club_index=349,
                                        display_receipt=Path('receipt'), approved_until_utc=until)
        self.assertEqual(observer.call_args.args[2], SupervisedWatchPlan(club_index=349))
        self.assertEqual(observer.call_args.kwargs, dict(display_receipt=Path('receipt')))
        self.assertTrue(result['supervised_human_operated'])

    def test_attendance_snapshot_reads_actual_receiver_not_selected_watch(self):
        receiver = 0x200000
        values = {(receiver, 4): struct.pack('<I', 0x7BD614),
                  (receiver + 4, 2): struct.pack('<H', 349),
                  (receiver + 0x13C, 8): struct.pack('<II', 123, 456)}
        reads = []
        def read(address, length):
            reads.append((address, length))
            return values[address, length]
        row = attendance_receiver_observation(receiver, read)
        self.assertEqual(reads, list(values))
        self.assertEqual(row['capacity_u32'], [123, 456])
        self.assertEqual(row['plus4_word_u16'], 349)
        self.assertFalse(row['capacity_initializer_proven'])
        self.assertTrue(row['observation_not_runtime_input'])

    def test_attendance_snapshot_rejects_unqualified_object_before_reading_fields(self):
        def read(address, length):
            self.assertEqual((address, length), (0x200000, 4))
            return struct.pack('<I', 0x7BD615)
        with self.assertRaisesRegex(CapacityWatchError, 'not qualified DBRClub'):
            attendance_receiver_observation(0x200000, read)

    def test_watch_readback_is_not_continuous_coverage_or_initializer_proof(self):
        context = Wow64Context()
        arm_writes(context, 0x100000)
        row = write_watch_observation(context, 0x100000)
        self.assertTrue(row['selected_capacity_watches_present'])
        self.assertFalse(row['continuous_all_thread_coverage_proven'])
        self.assertEqual(row['registers']['Dr7'], 0xDD0005)
        context.Dr0 += 4
        self.assertFalse(write_watch_observation(context, 0x100000)['selected_capacity_watches_present'])
        arm_writes(context, 0x100000)
        context.Dr7 &= ~1
        self.assertFalse(write_watch_observation(context, 0x100000)['selected_capacity_watches_present'])

    def test_all_thread_readback_requires_every_live_thread_watch(self):
        contexts = {}
        for tid in (11, 7, 19):
            ctx = Wow64Context()
            arm_writes(ctx, 0x100000)
            contexts[tid] = ctx
        row = all_thread_write_watch_readback(contexts, 0x100000)
        self.assertEqual(row['thread_ids'], [7, 11, 19])
        self.assertEqual(row['thread_count'], 3)
        self.assertTrue(row['all_live_threads_armed'])
        self.assertFalse(row['continuous_all_thread_coverage_proven'])
        contexts[11].Dr0 += 4
        row = all_thread_write_watch_readback(contexts, 0x100000)
        self.assertFalse(row['all_live_threads_armed'])
        self.assertFalse(next(item for item in row['per_thread'] if item['tid'] == 11)
                         ['selected_capacity_watches_present'])

    def test_all_thread_readback_rejects_empty_or_non_context_ledger(self):
        for contexts in ({}, {1: object()}, {'1': Wow64Context()}):
            with self.subTest(contexts=contexts), self.assertRaises(CapacityWatchError):
                all_thread_write_watch_readback(contexts, 0x100000)

    def test_continuous_coverage_requires_one_check_per_debug_event_and_resume(self):
        coverage = dict(started=True, broken=False, checks=5, resumed_events_checked=4,
                        start_debug_event_number=100)
        finalize_user_thread_write_watch_coverage(coverage, 104)
        self.assertEqual(coverage['expected_debug_events_through_read'], 5)
        self.assertTrue(coverage['debug_events_checked_without_gap'])
        self.assertTrue(coverage['continuous_all_user_thread_write_watch_coverage_proven'])
        self.assertFalse(coverage['kernel_or_external_writer_coverage_proven'])

        for bad in (
            dict(started=True, broken=False, checks=4, resumed_events_checked=4),
            dict(started=True, broken=False, checks=5, resumed_events_checked=3),
            dict(started=True, broken=True, checks=5, resumed_events_checked=4),
        ):
            with self.subTest(bad=bad):
                bad['start_debug_event_number'] = 100
                finalize_user_thread_write_watch_coverage(bad, 104)
                self.assertFalse(bad['continuous_all_user_thread_write_watch_coverage_proven'])

    def test_supervised_plan_does_not_expand_ordinary_cli_bound(self):
        self.assertEqual(SupervisedWatchPlan().seconds, 300)
        self.assertEqual(SupervisedWatchPlan().max_events, 4096)
        for bad in (60, 301, True):
            with self.assertRaises(CapacityWatchError):
                SupervisedWatchPlan(seconds=bad)
        with self.assertRaises(CapacityWatchError):
            WatchPlan(seconds=300)

    def test_supervised_probe_requires_exact_matching_live_five_minute_consent(self):
        until=datetime.now(timezone.utc)+timedelta(minutes=10)
        with patch('gate13_native_capacity_watch.require_desktop_safety_qualification',
                   return_value=until-timedelta(seconds=1)), self.assertRaises(CapacityWatchError):
            observe_supervised(Path('not-read'),Path('not-written'),
                display_receipt=Path('private'),approved_until_utc=until)
    def test_activation_trace_is_separate_bounded_and_approval_expiring(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=5)
        with patch('gate13_native_capacity_watch._observe', return_value={}) as observer:
            trace_window_activation(Path('original'), Path('private'), approved_until_utc=until)
        self.assertEqual(observer.call_args.args[2], WatchPlan(seconds=10, max_events=256))
        self.assertEqual(observer.call_args.kwargs, dict(qualification_only=True, activation_trace_until=until))
        for invalid in (None, datetime.now(), datetime.now(timezone.utc) - timedelta(seconds=1),
                        datetime.now(timezone.utc) + timedelta(hours=2)):
            with self.assertRaises(CapacityWatchError):
                trace_window_activation(Path('not-read'), Path('not-written'), approved_until_utc=invalid)

    def test_presentation_shim_clears_only_topmost_at_exact_call(self):
        for original in (0, 8, 0x40108, 0xFFFFFFFF, 0xFFFFFFF7):
            arguments = struct.pack('<12I', original, *range(1, 12))
            row = window_presentation_adaptation(CREATE_WINDOW_CALL, CREATE_WINDOW_INSTRUCTION, arguments)
            self.assertEqual(row['modified_dwExStyle'], original & 0xFFFFFFF7)
            self.assertEqual(row['changed_bits'], original & 8)
            self.assertTrue(row['other_style_bits_unchanged'])
            self.assertEqual(row['applied'], bool(original & 8))
            self.assertTrue(row['probe_only_compatibility_not_native_evidence'])

    def test_presentation_shim_rejects_other_calls_code_or_partial_arguments(self):
        arguments = struct.pack('<12I', *range(12))
        for address, code, args in ((CREATE_WINDOW_CALL + 1, CREATE_WINDOW_INSTRUCTION, arguments),
                                     (CREATE_WINDOW_CALL, b'\x90' * 6, arguments),
                                     (CREATE_WINDOW_CALL, CREATE_WINDOW_INSTRUCTION, arguments[:4])):
            with self.assertRaises(CapacityWatchError):
                window_presentation_adaptation(address, code, args)

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
        self.assertEqual(FOREGROUND_REQUEST, 0x6A6016)
        self.assertIn(FOREGROUND_REQUEST, STARTUP_SITES)

    def test_failed_display_receipt_cannot_authorize_launch(self):
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value={}), \
                patch.object(Path, 'read_text', return_value='{"schema_version":1,"runtime_nonexclusive_qualified":false}'):
            with self.assertRaisesRegex(CapacityWatchError, 'does not qualify'):
                require_desktop_safety_qualification(Path('original'), Path('receipt'))

    def test_only_complete_exact_stage_display_receipt_is_accepted_audio_not_required(self):
        executable = Path('private-stage/original.exe').resolve()
        stage = dict(wrapper_sha256='wrapper', config_sha256='config')
        data = dict(schema_version=4, stop_reason='display_qualification_complete',
                    display_qualification_only=True, runtime_nonexclusive_qualified=True,
                    source_sha256='833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3',
                    private_stage=str(executable.parent), **stage,
                    presentation_shim=PRESENTATION_SHIM, presentation_shim_verified=True,
                    private_wrapper_load_observed=True, native_graphics_initialization_accepted=True,
                    display_observation=dict(normal_window_observed=True, problems=[]))
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value=stage), \
                patch.object(Path, 'read_text', return_value=json.dumps(data)):
            require_desktop_safety_qualification(executable, Path('receipt'))
        for key, bad in (('schema_version', 2), ('wrapper_sha256', 'other'),
                         ('config_sha256', 'other'), ('private_stage', 'elsewhere'),
                         ('source_sha256', 'other'), ('private_wrapper_load_observed', False),
                         ('native_graphics_initialization_accepted', False),
                         ('runtime_nonexclusive_qualified', False),
                         ('presentation_shim', 'other'), ('presentation_shim_verified', False),
                         ('activation_trace_only', True),
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

    def test_activation_receipt_expiry_checked_before_launch(self):
        data = dict(approved_activation_windowed_qualification=True,
                    activation_approval_expiry_utc=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat())
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value={}), \
                patch.object(Path, 'read_text', return_value=json.dumps(data)), \
                self.assertRaisesRegex(CapacityWatchError, 'missing/expired'):
            require_desktop_safety_qualification(Path('original'), Path('private-receipt'))

    def test_unknown_borderless_state_cannot_authorize_launch(self):
        data = dict(qualification_mode='dxgi_windowed_borderless_v1')
        with patch('gate13_native_capacity_watch.require_private_output_path'), \
                patch('gate13_native_capacity_watch.check_private_stage', return_value={}), \
                patch.object(Path, 'read_text', return_value=json.dumps(data)), \
                self.assertRaisesRegex(CapacityWatchError, 'DXGI evidence missing'):
            require_desktop_safety_qualification(Path('original'), Path('private-receipt'))

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
