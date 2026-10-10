from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import ctypes
import platform
import subprocess
import unittest

from startup_media_input import (
    NATIVE_STARTUP_INPUT_MESSAGES, parse_native_skip_receipt, startup_input_allowed,
)
from startup_media_windows_backend import (
    WindowsWpfStartupMediaBackend, WindowsStartupMediaBackendError,
    _GameOwnedChildViewport,
    _WPF_PLAYBACK_SCRIPT,
)
from startup_media_playback import play_verified_startup_sequence, StartupMediaPlaybackError
from test_startup_media_windows_backend import derivative


class NativeStartupInputTests(unittest.TestCase):
    @unittest.skipUnless(platform.system() == 'Windows', 'requires stock Windows WPF')
    def test_stock_wpf_hook_delegate_without_creating_a_window(self):
        hook = _WPF_PLAYBACK_SCRIPT.split('$inputHook = ', 1)[1].split('$source.AddHook', 1)[0]
        script = r'''
Add-Type -AssemblyName PresentationFramework
$script:mediaFailed = $false
$script:mediaEnded = $false
$script:mediaOpened = $true
$script:allowNativeInput = $true
$script:skipMessage = 0
$script:frame = [PSCustomObject]@{Continue=$true}
$media = New-Object PSObject
$media | Add-Member ScriptMethod Stop { $script:stopped = $true }
$inputHook = ''' + hook + r'''
foreach ($message in @(0x101, 0x104)) {
    $handled = $false
    [void]$inputHook.Invoke([IntPtr]::Zero,$message,[IntPtr]::Zero,[IntPtr]::Zero,[ref]$handled)
    if ($handled -or $script:skipMessage -ne 0) { exit 8 }
}
foreach ($message in @(0x100,0x201,0x204)) {
    $script:skipMessage = 0; $script:stopped = $false
    $handled = $false
    [void]$inputHook.Invoke([IntPtr]::Zero,$message,[IntPtr]::Zero,[IntPtr]::Zero,[ref]$handled)
    if ($handled -or -not $script:stopped -or $script:skipMessage -ne $message) {
        Write-Output "message=$message handled=$handled stopped=$script:stopped skip=$script:skipMessage failed=$script:mediaFailed"; exit 9
    }
}
$script:allowNativeInput = $false; $script:skipMessage = 0
$handled = $false
[void]$inputHook.Invoke([IntPtr]::Zero,0x100,[IntPtr]::Zero,[IntPtr]::Zero,[ref]$handled)
if ($handled -or $script:skipMessage -ne 0) { exit 10 }
exit 0
'''
        result = subprocess.run(('powershell.exe', '-NoProfile', '-NonInteractive', '-Sta', '-Command', script),
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_only_three_registered_messages_and_true_clip_flag(self):
        for message in NATIVE_STARTUP_INPUT_MESSAGES:
            self.assertTrue(startup_input_allowed(True, message))
            for flag in (False, 1, None):
                self.assertFalse(startup_input_allowed(flag, message))
        for message in (True, 0x101, 0x104, 0x202, 0, '256'):
            self.assertFalse(startup_input_allowed(True, message))

    def test_receipt_is_exact_and_flag_qualified(self):
        for message in NATIVE_STARTUP_INPUT_MESSAGES:
            receipt = f'FM2001_STARTUP_SKIPPED={message}\r\n'
            self.assertEqual(parse_native_skip_receipt(receipt, True), message)
            with self.assertRaises(ValueError):
                parse_native_skip_receipt(receipt, False)
        for receipt in ('', 'FM2001_STARTUP_SKIPPED=260',
                        'FM2001_STARTUP_SKIPPED=２５６',
                        'FM2001_STARTUP_SKIPPED=+256',
                        'FM2001_STARTUP_SKIPPED=256\nextra'):
            with self.assertRaises(ValueError):
                parse_native_skip_receipt(receipt, True)

    def test_input_exit_is_not_a_media_failure_or_unqualified_skip(self):
        item = derivative(Path('intro.mp4'))
        for flag, code, stdout, succeeds in (
            (True, 4, 'FM2001_STARTUP_SKIPPED=256', True),
            (False, 4, 'FM2001_STARTUP_SKIPPED=256', False),
            (True, 3, 'FM2001_STARTUP_SKIPPED=256', False),
            (True, 4, '', False),
            (True, 4, 'FM2001_STARTUP_SKIPPED=260', False),
        ):
            with self.subTest(flag=flag, code=code, stdout=stdout):
                calls = []
                def runner(*args, **kwargs):
                    calls.append(kwargs['env'])
                    return SimpleNamespace(returncode=code, stdout=stdout, stderr='')
                backend = WindowsWpfStartupMediaBackend(platform_system='Windows', runner=runner)
                backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
                current = replace(item, spec=replace(item.spec, playback_flag_bit0=flag))
                if succeeds:
                    self.assertTrue(backend.play(current))
                    self.assertEqual(backend.last_native_input_message, 256)
                else:
                    with self.assertRaises(WindowsStartupMediaBackendError):
                        backend.play(current)
                self.assertEqual(calls[0]['FM2001_STARTUP_INPUT_BIT0'], '1' if flag else '0')
                self.assertFalse(backend.request_native_input(256, 27))

    def test_forwarding_is_only_to_the_live_owned_direct_child(self):
        viewport = _GameOwnedChildViewport.__new__(_GameOwnedChildViewport)
        viewport.parent_hwnd, viewport.player_pid, viewport.child_hwnd = 123, 456, None
        viewport.pid_type = ctypes.c_ulong
        calls, identity = [], [456, 123]
        def pid(hwnd, output):
            output._obj.value = identity[0]
        viewport.user32 = SimpleNamespace(GetWindowThreadProcessId=pid,
            GetParent=lambda hwnd: identity[1],
            PostMessageW=lambda *args: calls.append(args) or True)
        self.assertFalse(viewport.post_native_input(256, 27))
        viewport.child_hwnd = 20
        self.assertTrue(viewport.post_native_input(256, 27))
        self.assertEqual(calls, [(20, 256, 27, 0)])
        with self.assertRaises(WindowsStartupMediaBackendError):
            viewport.post_native_input(260, 27)
        for wrong in ([999, 123], [456, 999]):
            identity[:] = wrong
            with self.assertRaises(WindowsStartupMediaBackendError):
                viewport.post_native_input(256, 27)
        self.assertEqual(len(calls), 1)

    def test_destroyed_child_waits_for_player_exit_not_success(self):
        viewport = _GameOwnedChildViewport.__new__(_GameOwnedChildViewport)
        viewport.parent_hwnd, viewport.player_pid, viewport.child_hwnd = 123, 456, 20
        viewport.pid_type = ctypes.c_ulong
        viewport.last_rect = None
        def pid(hwnd, output):
            output._obj.value = 0
        viewport.user32 = SimpleNamespace(GetWindowThreadProcessId=pid,
            GetParent=lambda hwnd: None, IsWindow=lambda hwnd: False,
            SetWindowPos=lambda *args: self.fail('must not move destroyed HWND'),
            PostMessageW=lambda *args: self.fail('must not post to destroyed HWND'))
        viewport((80, 60, 640, 480))
        self.assertFalse(viewport.post_native_input(256, 27))
        process = SimpleNamespace(pid=456, returncode=3, poll=lambda: None,
            communicate=lambda **kwargs: ('', 'MediaFailed'))
        backend = WindowsWpfStartupMediaBackend(platform_system='Windows',
            process_factory=lambda *a, **k: process, viewport_factory=lambda *a: viewport)
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        backend.bind_event_pump(lambda: None)
        backend.bind_presentation_geometry(lambda: dict(parent_hwnd=123, x=80, y=60, width=640, height=480))
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, 'exit code 3.*MediaFailed'):
            backend.play(derivative(Path('ea.mp4')))

    def test_pumped_input_callback_and_cleanup(self):
        calls = []
        class Viewport:
            def __call__(self, rect):
                calls.append(('rect', rect))
            def post_native_input(self, message, value):
                calls.append(('input', message, value))
                return True
        process = SimpleNamespace(pid=456, returncode=4, poll=lambda: None,
            communicate=lambda **kwargs: ('FM2001_STARTUP_SKIPPED=256', ''),
            kill=lambda: self.fail('must not kill completed player'))
        backend = WindowsWpfStartupMediaBackend(platform_system='Windows',
            process_factory=lambda *a, **k: process,
            viewport_factory=lambda *a: Viewport())
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        backend.bind_presentation_geometry(lambda: dict(parent_hwnd=123, x=80, y=60, width=640, height=480))
        backend.bind_event_pump(lambda: self.assertTrue(backend.request_native_input(256, 27)))
        item = derivative(Path('intro.mp4'))
        item = replace(item, spec=replace(item.spec, playback_flag_bit0=True))
        self.assertTrue(backend.play(item))
        self.assertIn(('input', 256, 27), calls)
        self.assertIsNone(backend._active_viewport)
        self.assertFalse(backend.request_native_input(256, 27))

    def test_orchestration_distinguishes_stop_from_end_and_preserves_order(self):
        first = derivative(Path('ea.mp4'))
        second = replace(derivative(Path('intro.mp4'), sequence=1),
                         spec=replace(first.spec, source_path='FMV/intro.tgq', playback_flag_bit0=True))
        class Backend:
            source_input_contract_recovered = True
            last_native_input_message = None
            def play(self, item):
                self.last_native_input_message = 256 if item.sequence == 1 else None
                return True
        result = play_verified_startup_sequence((first, second), Backend(), specs=(first.spec, second.spec))
        self.assertFalse(result.steps[0].skipped)
        self.assertTrue(result.steps[1].skipped)
        self.assertEqual(result.steps[1].native_input_message, 256)
        self.assertFalse(result.transition_timing_recovered)
        self.assertFalse(result.gate14_complete)
        bad = Backend()
        bad.play = lambda item: True
        bad.last_native_input_message = 256
        with self.assertRaises(StartupMediaPlaybackError):
            play_verified_startup_sequence((first,), bad, specs=(first.spec,))


if __name__ == '__main__':
    unittest.main()
