from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import base64
import json
import platform
import subprocess
import unittest
from unittest.mock import patch

from original_startup_media import OriginalStartupMediaSpec
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_windows_backend import (
    WindowsMciStartupMediaBackend,
    WindowsWpfStartupMediaBackend,
    WindowsStartupMediaBackendError,
)


def derivative(path: Path, *, sequence: int = 0) -> VerifiedStartupMediaDerivative:
    spec = OriginalStartupMediaSpec(
        source_path="FMV/test.tgq",
        source_sha256=sha256(b"source").hexdigest(),
        size_bytes=6,
        startup_callsite_va=0x530000,
        playback_wrapper_va=0x461E20,
        playback_flag_bit0=False,
        video_width=320,
        video_height=480,
        frame_rate=25,
        decoded_video_frames=10,
        audio_sample_rate=22_050,
        audio_channels=2,
    )
    return VerifiedStartupMediaDerivative(
        sequence=sequence,
        spec=spec,
        path=path,
        converted_sha256="a" * 64,
        converted_size_bytes=123,
        container="mp4",
        video_codec="h264",
        pixel_format="yuv420p",
        audio_codec="aac",
    )


class RecordingSender:
    def __init__(self, statuses=()):
        self.statuses = list(statuses)
        self.calls = []

    def __call__(self, command):
        self.calls.append(command)
        return self.statuses.pop(0) if self.statuses else 0


class RecordingRunner:
    def __init__(self, *, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return SimpleNamespace(
            returncode=self.returncode,
            stderr=self.stderr,
            stdout="",
        )


def transport_receipt_json(
    *,
    parent_hwnd=12345,
    child_hwnd=54321,
    x=80,
    y=60,
    width=640,
    height=480,
):
    payload = {
        "parent_hwnd": parent_hwnd,
        "child_hwnd": child_hwnd,
        "requested_child_rect": {"x": x, "y": y, "width": width, "height": height},
        "parent_window_rect": {
            "left": 90, "top": 70, "right": 910, "bottom": 710,
            "width": 820, "height": 640,
        },
        "parent_client_rect": {
            "left": 0, "top": 0, "right": 800, "bottom": 600,
            "width": 800, "height": 600,
        },
        "parent_client_origin_screen": {"x": 100, "y": 100},
        "child_window_rect": {
            "left": 100 + x, "top": 100 + y,
            "right": 100 + x + width, "bottom": 100 + y + height,
            "width": width, "height": height,
        },
        "child_client_rect": {
            "left": 0, "top": 0, "right": width, "bottom": height,
            "width": width, "height": height,
        },
        "child_client_origin_screen": {"x": 100 + x, "y": 100 + y},
        "child_offset_from_parent_client": {"x": x, "y": y},
        "parent_dpi": 96,
        "child_dpi": 96,
        "parent_dpi_awareness_context": -4,
        "child_dpi_awareness_context": -4,
        "probe_thread_dpi_awareness_context": -4,
        "parent_dpi_awareness": 2,
        "child_dpi_awareness": 2,
        "probe_thread_dpi_awareness": 2,
    }
    return "FM2001_TRANSPORT_RECEIPT:" + json.dumps(payload, separators=(",", ":"))


class WindowsWpfStartupMediaBackendTests(unittest.TestCase):
    def test_game_owned_child_creation_requires_parent_pump_before_completion(self):
        # Model the real HwndSource constructor's cross-process parent request.
        # A blocking runner cannot service it; communicate must yield to Tk.
        requests = []
        process = SimpleNamespace(returncode=0, poll=lambda: None)
        waits = []
        def communicate(timeout=None):
            waits.append(timeout)
            if len(requests) < 2:
                raise subprocess.TimeoutExpired('child awaits parent', timeout)
            return '', ''
        process.communicate = communicate
        process.kill = lambda: self.fail('completed player must not be killed')
        launches = []
        def factory(command, **kwargs):
            launches.append((command, kwargs))
            return process
        backend = WindowsWpfStartupMediaBackend(platform_system='Windows',
            runner=lambda *a, **k: self.fail('blocking subprocess.run recreates issue482'),
            process_factory=factory)
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        backend.bind_event_pump(lambda: requests.append('parent message serviced'))
        self.assertTrue(backend.play(derivative(Path('easp.mp4'))))
        self.assertEqual(len(requests), 2)
        self.assertTrue(all(0 < interval <= .02 for interval in waits))
        self.assertEqual(launches[0][1]['env']['FM2001_STARTUP_PARENT_HWND'], '123')
        self.assertEqual(launches[0][1]['env']['FM2001_STARTUP_MEDIA_WIDTH'], '640')
        self.assertEqual(launches[0][1]['stdout'], subprocess.PIPE)

    def test_pumped_timeout_stays_bounded_and_kills_drains_only_owned_player(self):
        process = unittest.mock.Mock()
        process.poll.return_value = None
        process.communicate.return_value = ('', '')
        backend = WindowsWpfStartupMediaBackend(platform_system='Windows',
            process_factory=lambda *a, **k: process)
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        backend.bind_event_pump(lambda: None)
        with patch('startup_media_windows_backend.time.monotonic', side_effect=(0, 34)):
            with self.assertRaisesRegex(WindowsStartupMediaBackendError, 'timed out'):
                backend.play(derivative(Path('easp.mp4')))
        process.kill.assert_called_once_with()
        process.communicate.assert_called_once_with()

    def test_parent_close_and_media_failure_remain_fail_closed(self):
        process = unittest.mock.Mock()
        process.poll.return_value = None
        process.communicate.return_value = ('', '')
        backend = WindowsWpfStartupMediaBackend(platform_system='Windows',
            process_factory=lambda *a, **k: process)
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        def closed():
            raise RuntimeError('Tk owner destroyed')
        backend.bind_event_pump(closed)
        with self.assertRaises(WindowsStartupMediaBackendError):
            backend.play(derivative(Path('easp.mp4')))
        process.kill.assert_called_once_with()
        process.communicate.assert_called_once_with()

        process.returncode = 3
        process.communicate.return_value = ('', 'MediaFailed: codec error')
        backend.bind_event_pump(lambda: None)
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, 'exit code 3.*codec error'):
            backend.play(derivative(Path('easp.mp4')))
        with self.assertRaises(WindowsStartupMediaBackendError):
            backend.bind_event_pump(None)

    @unittest.skipUnless(platform.system() == "Windows", "requires stock Windows WPF")
    def test_stock_windows_runtime_loads_wpf_mediaelement(self):
        completed = subprocess.run(
            (
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Sta",
                "-Command",
                (
                    "Add-Type -AssemblyName PresentationFramework; "
                    "$m = New-Object System.Windows.Controls.MediaElement; "
                    "if ($null -eq $m) { exit 7 }; exit 0"
                ),
            ),
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=(completed.stderr or completed.stdout),
        )

    def test_verified_mp4_uses_hidden_sta_wpf_process_and_environment_path(self):
        runner = RecordingRunner()
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
            powershell_executable=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        )
        path = Path(r"C:\FM2001\startup media\easp.mp4")
        backend.bind_parent_window(
            12345, x=144, y=108, width=1152, height=864
        )

        self.assertTrue(backend.play(derivative(path)))
        self.assertEqual(len(runner.calls), 1)
        command, kwargs = runner.calls[0]
        self.assertEqual(
            command[:9],
            (
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Sta",
                "-ExecutionPolicy",
                "Bypass",
                "-WindowStyle",
                "Hidden",
                "-EncodedCommand",
            ),
        )
        script = base64.b64decode(command[9]).decode("utf-16le")
        self.assertIn("PresentationFramework", script)
        self.assertIn("MediaElement", script)
        self.assertIn("HwndSourceParameters", script)
        self.assertIn("ParentWindow", script)
        self.assertIn("BitmapScalingMode", script)
        self.assertIn("NearestNeighbor", script)
        self.assertNotIn("New-Object Windows.Window", script)
        self.assertNotIn(str(path), script)
        self.assertEqual(
            kwargs["env"]["FM2001_STARTUP_MEDIA_PATH"],
            str(path),
        )
        self.assertEqual(kwargs["env"]["FM2001_STARTUP_PARENT_HWND"], "12345")
        self.assertEqual(kwargs["env"]["FM2001_STARTUP_MEDIA_X"], "144")
        self.assertEqual(kwargs["env"]["FM2001_STARTUP_MEDIA_Y"], "108")
        self.assertEqual(kwargs["env"]["FM2001_STARTUP_MEDIA_WIDTH"], "1152")
        self.assertEqual(kwargs["env"]["FM2001_STARTUP_MEDIA_HEIGHT"], "864")
        self.assertFalse(kwargs["check"])
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertGreater(kwargs["timeout"], 30.0)
        self.assertIn("MediaFailed", script)
        self.assertIn("ErrorException.Message", script)
        self.assertIn("DispatcherFrame", script)
        self.assertIn("RootVisual", script)
        self.assertIn("GetWindowDpiAwarenessContext", script)
        self.assertIn("GetWindowRect", script)
        self.assertIn("ClientToScreen", script)
        self.assertIn("FM2001_TRANSPORT_RECEIPT:", script)
        self.assertNotIn("FM2001_STARTUP_CAPTURE_TRANSPORT", kwargs["env"])

    def test_transport_receipt_capture_is_opt_in_and_records_actual_hwnd_dpi_state(self):
        class ReceiptRunner(RecordingRunner):
            def __call__(self, command, **kwargs):
                self.calls.append((command, kwargs))
                env = kwargs["env"]
                stdout = transport_receipt_json(
                    parent_hwnd=int(env["FM2001_STARTUP_PARENT_HWND"]),
                    x=int(env["FM2001_STARTUP_MEDIA_X"]),
                    y=int(env["FM2001_STARTUP_MEDIA_Y"]),
                    width=int(env["FM2001_STARTUP_MEDIA_WIDTH"]),
                    height=int(env["FM2001_STARTUP_MEDIA_HEIGHT"]),
                )
                return SimpleNamespace(returncode=0, stderr="", stdout=stdout)

        runner = ReceiptRunner()
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
        )
        backend.bind_parent_window(12345, x=80, y=60, width=640, height=480)
        backend.enable_transport_receipt_capture()

        self.assertTrue(backend.play(derivative(Path(r"C:\private\easp.mp4"))))
        self.assertEqual(
            runner.calls[0][1]["env"]["FM2001_STARTUP_CAPTURE_TRANSPORT"],
            "1",
        )
        self.assertEqual(len(backend.transport_receipts), 1)
        receipt = backend.transport_receipts[0]
        self.assertEqual(receipt["sequence"], 0)
        self.assertEqual(receipt["source_path"], "FMV/test.tgq")
        self.assertEqual(receipt["parent_hwnd"], 12345)
        self.assertEqual(receipt["child_hwnd"], 54321)
        self.assertEqual(receipt["child_offset_from_parent_client"], {"x": 80, "y": 60})
        self.assertEqual(receipt["child_window_rect"]["width"], 640)
        self.assertEqual(receipt["parent_dpi"], 96)
        self.assertEqual(receipt["child_dpi"], 96)
        self.assertEqual(receipt["parent_dpi_awareness"], 2)
        self.assertEqual(receipt["child_dpi_awareness"], 2)
        self.assertTrue(receipt["transport_comparison"]["offset_matches_request"])
        self.assertTrue(receipt["transport_comparison"]["window_size_matches_request"])
        self.assertFalse(receipt["transport_comparison"]["visual_equivalence_assessed"])

    def test_transport_receipt_rejects_inconsistent_win32_structural_fields(self):
        # Reject internally self-contradictory captures instead of treating
        # presence of fields as sufficient Windows evidence.
        def mutate_edge(row):
            row["child_window_rect"]["right"] += 1

        def mutate_client_origin(row):
            row["parent_client_rect"]["top"] = 1

        def mutate_child_offset(row):
            row["child_offset_from_parent_client"]["x"] += 1

        def mutate_invalid_awareness(row):
            row["child_dpi_awareness"] = -1

        for label, mutate, error in (
            ("rect edge", mutate_edge, "inconsistent child_window_rect edges"),
            ("client origin", mutate_client_origin, "nonzero parent_client_rect origin"),
            ("child offset", mutate_child_offset, "inconsistent child offset"),
            ("invalid DPI context", mutate_invalid_awareness, "invalid child_dpi_awareness enumeration"),
        ):
            with self.subTest(label=label):
                row = json.loads(transport_receipt_json().split(":", 1)[1])
                mutate(row)
                backend = WindowsWpfStartupMediaBackend(
                    platform_system="Windows", runner=RecordingRunner()
                )
                backend.enable_transport_receipt_capture()
                completed = SimpleNamespace(
                    stdout="FM2001_TRANSPORT_RECEIPT:" + json.dumps(row)
                )
                with self.assertRaisesRegex(WindowsStartupMediaBackendError, error):
                    backend._record_transport_receipt(
                        completed, derivative(Path(r"C:\\private\\easp.mp4"))
                    )
                self.assertEqual(backend.transport_receipts, ())

    def test_transport_receipt_preserves_observed_dpi_and_size_disagreements(self):
        # Requested geometry and measured geometry may differ in real Windows.
        # A coherent mismatch must remain usable diagnostic evidence, not be
        # silently forced to 640x480 or promoted to visual acceptance.
        row = json.loads(transport_receipt_json().split(":", 1)[1])
        row["child_window_rect"]["right"] += 80
        row["child_window_rect"]["width"] += 80
        row["child_client_rect"]["right"] += 80
        row["child_client_rect"]["width"] += 80
        row["parent_dpi"] = 144
        row["child_dpi"] = 96
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows", runner=RecordingRunner()
        )
        backend.enable_transport_receipt_capture()
        backend._record_transport_receipt(
            SimpleNamespace(stdout="FM2001_TRANSPORT_RECEIPT:" + json.dumps(row)),
            derivative(Path(r"C:\\private\\easp.mp4")),
        )
        receipt = backend.transport_receipts[0]
        self.assertEqual(receipt["child_window_rect"]["width"], 720)
        self.assertEqual(
            receipt["transport_comparison"],
            {
                "offset_matches_request": True,
                "window_size_matches_request": False,
                "client_size_matches_request": False,
                "parent_child_dpi_equal": False,
                "visual_equivalence_assessed": False,
            },
        )

    def test_failed_wpf_process_surfaces_exit_and_stderr(self):
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=RecordingRunner(returncode=3, stderr="media failed"),
        )
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            r"exit code 3: media failed",
        ):
            backend.play(derivative(Path(r"C:\private\a.mp4")))

    def test_timeout_is_source_duration_bounded_and_surfaces_failure(self):
        item = derivative(Path(r"C:\private\long.mp4"))
        long_spec = OriginalStartupMediaSpec(
            source_path=item.spec.source_path,
            source_sha256=item.spec.source_sha256,
            size_bytes=item.spec.size_bytes,
            startup_callsite_va=item.spec.startup_callsite_va,
            playback_wrapper_va=item.spec.playback_wrapper_va,
            playback_flag_bit0=item.spec.playback_flag_bit0,
            video_width=item.spec.video_width,
            video_height=item.spec.video_height,
            frame_rate=25,
            decoded_video_frames=1250,
            audio_sample_rate=item.spec.audio_sample_rate,
            audio_channels=item.spec.audio_channels,
        )
        long_item = VerifiedStartupMediaDerivative(
            sequence=item.sequence,
            spec=long_spec,
            path=item.path,
            converted_sha256=item.converted_sha256,
            converted_size_bytes=item.converted_size_bytes,
            container=item.container,
            video_codec=item.video_codec,
            pixel_format=item.pixel_format,
            audio_codec=item.audio_codec,
        )

        class TimeoutRunner:
            def __call__(self, command, **kwargs):
                raise subprocess.TimeoutExpired(command, kwargs["timeout"])

        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=TimeoutRunner(),
        )
        backend.bind_parent_window(123, x=80, y=60, width=640, height=480)
        self.assertEqual(backend._timeout_seconds(long_item), 80.0)
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "playback timed out",
        ):
            backend.play(long_item)

    def test_invalid_timing_contract_is_defensively_rejected(self):
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=RecordingRunner(),
        )
        invalid_item = SimpleNamespace(
            spec=SimpleNamespace(
                decoded_video_frames=10,
                frame_rate=0,
            )
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "timing contract is invalid",
        ):
            backend._timeout_seconds(invalid_item)


    def test_wpf_backend_requires_valid_game_window_binding(self):
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=RecordingRunner(),
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError, "not bound to the game window"
        ):
            backend.play(derivative(Path(r"C:\private\a.mp4")))

        for args in (
            (0, 0, 0, 640, 480),
            (123, -1, 0, 640, 480),
            (123, 0, 0, 0, 480),
        ):
            with self.subTest(args=args):
                with self.assertRaises(WindowsStartupMediaBackendError):
                    backend.bind_parent_window(
                        args[0],
                        x=args[1],
                        y=args[2],
                        width=args[3],
                        height=args[4],
                    )

    def test_wpf_backend_rejects_non_windows_invalid_runner_and_wrong_codec(self):
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, "requires Windows"):
            WindowsWpfStartupMediaBackend(
                platform_system="Linux",
                runner=lambda *args, **kwargs: None,
            )
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, "runner must be callable"):
            WindowsWpfStartupMediaBackend(
                platform_system="Windows",
                runner=object(),
            )

        runner = RecordingRunner()
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
        )
        self.assertFalse(backend.play(object()))
        item = derivative(Path(r"C:\private\a.mp4"))
        self.assertFalse(
            backend.play(
                VerifiedStartupMediaDerivative(
                    sequence=item.sequence,
                    spec=item.spec,
                    path=item.path,
                    converted_sha256=item.converted_sha256,
                    converted_size_bytes=item.converted_size_bytes,
                    container=item.container,
                    video_codec="vp9",
                    pixel_format=item.pixel_format,
                    audio_codec=item.audio_codec,
                )
            )
        )
        self.assertEqual(runner.calls, [])


class WindowsStartupMediaBackendTests(unittest.TestCase):
    def test_verified_mp4_plays_fullscreen_wait_and_closes(self):
        sender = RecordingSender()
        backend = WindowsMciStartupMediaBackend(
            platform_system="Windows",
            sender=sender,
        )
        item = derivative(Path(r"C:\FM2001\startup media\easp.mp4"), sequence=2)

        self.assertTrue(backend.play(item))
        self.assertEqual(
            sender.calls,
            [
                r'open "C:\FM2001\startup media\easp.mp4" alias fm2001_startup_2',
                "play fm2001_startup_2 fullscreen wait",
                "close fm2001_startup_2",
            ],
        )

    def test_open_or_play_error_surfaces_status_and_opened_device_is_closed(self):
        open_error = RecordingSender((7,))
        backend = WindowsMciStartupMediaBackend(
            platform_system="Windows",
            sender=open_error,
            error_describer=lambda status: "open failed detail",
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            r"7: open failed detail",
        ):
            backend.play(derivative(Path(r"C:\private\a.mp4")))
        self.assertEqual(len(open_error.calls), 1)

        play_error = RecordingSender((0, 9, 0))
        backend = WindowsMciStartupMediaBackend(
            platform_system="Windows",
            sender=play_error,
            error_describer=lambda status: "play failed detail",
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            r"9: play failed detail",
        ):
            backend.play(derivative(Path(r"C:\private\a.mp4")))
        self.assertEqual(
            play_error.calls[-1],
            "close fm2001_startup_0",
        )

    def test_non_windows_or_invalid_sender_fails_closed(self):
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, "requires Windows"):
            WindowsMciStartupMediaBackend(
                platform_system="Linux",
                sender=lambda command: 0,
            )
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, "callable"):
            WindowsMciStartupMediaBackend(
                platform_system="Windows",
                sender=object(),
            )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "error describer must be callable",
        ):
            WindowsMciStartupMediaBackend(
                platform_system="Windows",
                sender=lambda command: 0,
                error_describer=object(),
            )

    def test_wrong_item_or_codec_is_rejected_before_mci(self):
        sender = RecordingSender()
        backend = WindowsMciStartupMediaBackend(
            platform_system="Windows",
            sender=sender,
        )
        self.assertFalse(backend.play(object()))

        item = derivative(Path(r"C:\private\a.mp4"))
        self.assertFalse(
            backend.play(
                VerifiedStartupMediaDerivative(
                    sequence=item.sequence,
                    spec=item.spec,
                    path=item.path,
                    converted_sha256=item.converted_sha256,
                    converted_size_bytes=item.converted_size_bytes,
                    container="mp4",
                    video_codec="vp9",
                    pixel_format=item.pixel_format,
                    audio_codec=item.audio_codec,
                )
            )
        )
        self.assertEqual(sender.calls, [])

    def test_unsafe_command_path_is_rejected(self):
        sender = RecordingSender()
        backend = WindowsMciStartupMediaBackend(
            platform_system="Windows",
            sender=sender,
        )
        with self.assertRaisesRegex(WindowsStartupMediaBackendError, "represented safely"):
            backend.play(derivative(Path('C:/bad"name.mp4')))
        self.assertEqual(sender.calls, [])


if __name__ == "__main__":
    unittest.main()
