"""Regression for issue482: pre-mainloop startup must service its Tk owner."""
from pathlib import Path
from types import SimpleNamespace
import json
import os
import platform
import unittest
from unittest.mock import Mock, patch

from original_game_host import OriginalGameTkHost, OriginalGameHostError, run_original_game_ui
from startup_media_runtime_cache import CACHE_RECEIPT_NAME, _load_cache
from startup_media_windows_backend import WindowsWpfStartupMediaBackend


class StartupMediaTkIntegrationTests(unittest.TestCase):
    def test_normal_launch_binds_pump_before_synchronous_media_and_mainloop(self):
        events = []
        root = SimpleNamespace(mainloop=lambda: events.append('mainloop'))
        pump = lambda: events.append('pump')
        host = SimpleNamespace(
            show_startup_media_backdrop=lambda: events.append('black backdrop'),
            hide_startup_media_backdrop=lambda: events.append('restore menu'),
            pump_startup_media_events=pump,
            startup_media_child_binding=lambda: dict(parent_hwnd=123, x=80, y=60, width=640, height=480))
        class Backend:
            def bind_event_pump(self, callback):
                self.pump = callback
                events.append('bind pump')
            def bind_parent_window(self, parent_hwnd, **rect):
                self.binding = (parent_hwnd, rect)
                events.append('bind child')
        backend = Backend()
        def play(**kwargs):
            self.assertIs(kwargs['backend'], backend)
            self.assertIs(backend.pump, pump)
            events.append('easp then premintro')
            backend.pump()
        with (patch('original_game_host.build_original_game_presenter'),
              patch('tkinter.Tk', return_value=root),
              patch('original_game_host.OriginalGameTkHost', return_value=host),
              patch('original_game_host.play_configured_startup_media', side_effect=play),
              patch('original_game_host.install_live_first_screen_audio', return_value=None)):
            run_original_game_ui(Path('game'), startup_media_backend=backend,
                startup_media_derivatives=('verified sequence',))
        self.assertEqual(events, ['black backdrop', 'bind pump', 'bind child',
            'easp then premintro', 'pump', 'restore menu', 'mainloop'])
        self.assertEqual(backend.binding, (123, dict(x=80, y=60, width=640, height=480)))

    def test_pumping_does_not_accept_hidden_menu_input_or_redraw_over_movie(self):
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host._startup_media_active = True
        for callback in (host.on_click, host.on_fixture_report_press,
                         host.on_script_arrow_release, host.on_fixtures_pager_motion,
                         host.on_fixtures_pager_leave, host.redraw):
            if callback == host.redraw:
                callback()
            else:
                callback(None)  # No presenter/event fields may be accessed.

    def test_pump_services_owner_and_detects_closed_game(self):
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.root = SimpleNamespace(update=Mock(), winfo_exists=lambda: 1)
        host.pump_startup_media_events()
        host.root.update.assert_called_once_with()
        host.root.winfo_exists = lambda: 0
        with self.assertRaisesRegex(OriginalGameHostError, 'closed during startup'):
            host.pump_startup_media_events()

    @unittest.skipUnless(platform.system() == 'Windows' and
        os.environ.get('FM2001_WPF_TEST_CACHE'),
        'opt-in Windows/Tk playback requires a private verified startup-media cache')
    def test_real_wpf_child_completes_before_tk_mainloop(self):
        """Actual constructor/playback regression, using unmodified WPF code.

        Set FM2001_WPF_TEST_CACHE to the existing private conversion cache.
        This plays the first clip with its normal audio in a windowed Tk owner;
        no original game is launched and no media is stored in the repository.
        """
        import tkinter as tk
        cache = Path(os.environ['FM2001_WPF_TEST_CACHE'])
        receipt = json.loads((cache / CACHE_RECEIPT_NAME).read_text(encoding='utf-8'))
        items = _load_cache(cache, ffmpeg_sha256=receipt['ffmpeg_sha256'])
        self.assertIsNotNone(items, 'private cache must pass the full existing verifier')
        root = tk.Tk()
        try:
            root.title('FM2001 WPF/Tk bounded regression')
            root.geometry('800x600')
            root.update()
            host = OriginalGameTkHost.__new__(OriginalGameTkHost)
            host.root = root
            pumps = []
            def pump():
                pumps.append(True)
                host.pump_startup_media_events()
            backend = WindowsWpfStartupMediaBackend()
            backend.bind_parent_window(root.winfo_id(), x=80, y=60, width=640, height=480)
            backend.bind_event_pump(pump)
            # True is returned only after WPF MediaEnded, not just MediaOpened.
            self.assertTrue(backend.play(items[0]))
            self.assertGreater(len(pumps), 1)
        finally:
            if root.winfo_exists():
                root.destroy()


if __name__ == '__main__':
    unittest.main()
