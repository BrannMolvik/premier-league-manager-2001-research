"""No launches: loss-free exact-process borderless evidence contracts."""
import copy
import unittest
from gate13_native_dxgi_evidence import windowed_dxgi_proof, qualify_borderless


def inputs():
    report = dict(schema_version=4, process_id=20, stop_reason='time_bound', elapsed_seconds=10,
        display_qualification_only=True, presentation_shim_verified=True,
        private_wrapper_load_observed=True, native_graphics_initialization_accepted=True,
        native_window_creation_returns=[dict(returned_hwnd=2)],
        display_observation=dict(problems=[], visible_window_observations={
            '2': dict(samples=12, duration_seconds=4)}))
    rows = [dict(id=10, process_id=20, provider='Microsoft-Windows-DXGI',
        fields=dict(Windowed='true', OutputWindow='0x2', Width='800', Height='600',
                    pIDXGISwapChain='0x1234'))]
    return report, rows


class DxgiEvidenceTests(unittest.TestCase):
    def test_visible_borderless_requires_actual_windowed_swapchain(self):
        report, rows = inputs()
        result = qualify_borderless(report, rows, 0)
        self.assertTrue(result['runtime_nonexclusive_qualified'])
        self.assertEqual(result['native_debugger_stop_reason'], 'time_bound')
        self.assertEqual(report['stop_reason'], 'time_bound')
        self.assertFalse(report.get('runtime_nonexclusive_qualified', False))

    def test_loss_wrong_pid_provider_hwnd_and_missing_state_reject(self):
        report, rows = inputs()
        for loss in (1, -1, None, False):
            with self.assertRaises(ValueError):
                windowed_dxgi_proof(report, rows, loss)
        for key, value in (('process_id', 21), ('provider', 'other')):
            changed = copy.deepcopy(rows)
            changed[0][key] = value
            with self.assertRaises(ValueError):
                windowed_dxgi_proof(report, changed, 0)
        for key, value in (('Windowed', 'false'), ('Windowed', None), ('OutputWindow', '0x3'),
                           ('Width', '1')):
            changed = copy.deepcopy(rows)
            changed[0]['fields'][key] = value
            with self.assertRaises(ValueError):
                windowed_dxgi_proof(report, changed, 0)

    def test_fullscreen_request_cannot_hide_behind_windowed_creation(self):
        report, rows = inputs()
        rows.append(dict(id=182, process_id=20, provider='Microsoft-Windows-DXGI',
                         fields=dict(bFullscreen='1')))
        with self.assertRaises(ValueError):
            qualify_borderless(report, rows, 0)

    def test_non_activation_failures_never_accepted(self):
        report, rows = inputs()
        report['approved_activation_windowed_qualification'] = True
        report['display_observation']['problems'] = ['probe_took_foreground', 'probe_took_focus']
        qualify_borderless(report, rows, 0)
        for problem in ('desktop_display_mode_changed', 'probe_window_always_on_top',
                        'probe_window_mouse_capture', 'unrelated_window_geometry_changed'):
            report['display_observation']['problems'] = [problem]
            with self.assertRaises(ValueError):
                qualify_borderless(report, rows, 0)

    def test_incomplete_or_trace_only_receipts_never_qualify(self):
        report, rows = inputs()
        for key, value in (('activation_trace_only', True), ('native_graphics_initialization_accepted', False),
                           ('private_wrapper_load_observed', False), ('presentation_shim_verified', False),
                           ('stop_reason', 'probe_error')):
            with self.assertRaises(ValueError):
                qualify_borderless(dict(report, **{key:value}), rows, 0)


if __name__ == '__main__':
    unittest.main()
