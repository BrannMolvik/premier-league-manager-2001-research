from __future__ import annotations

import base64
from hashlib import sha256
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from original_startup_media import OriginalStartupMediaSpec
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_windows_backend import (
    WindowsMciStartupMediaBackend,
    WindowsStartupMediaBackendError,
    WindowsWpfStartupMediaBackend,
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


class RecordingProcessRunner:
    def __init__(self, *, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return SimpleNamespace(
            returncode=self.returncode,
            stdout="",
            stderr=self.stderr,
        )


class WindowsWpfStartupMediaBackendTests(unittest.TestCase):
    def test_verified_mp4_uses_synchronous_stock_wpf_transport(self):
        runner = RecordingProcessRunner()
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
        )
        item = derivative(Path(r"C:\private path\easp.mp4"))

        self.assertTrue(backend.play(item))
        self.assertEqual(len(runner.calls), 1)
        command, kwargs = runner.calls[0]
        self.assertEqual(
            command[:-1],
            (
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-STA",
                "-EncodedCommand",
            ),
        )
        script = base64.b64decode(command[-1]).decode("utf-16le")
        self.assertIn("PresentationFramework", script)
        self.assertIn("System.Windows.Controls.MediaElement", script)
        self.assertIn("MediaEnded", script)
        self.assertIn("MediaFailed", script)
        self.assertIn("MediaState]::Manual", script)
        self.assertIn("WindowState]::Maximized", script)
        self.assertNotIn(str(item.path), script)
        path_marker = "[Convert]::FromBase64String('"
        encoded_path = script.split(path_marker, 1)[1].split("')", 1)[0]
        self.assertEqual(
            base64.b64decode(encoded_path).decode("utf-16le"),
            str(item.path),
        )
        self.assertFalse(kwargs["check"])
        self.assertIs(kwargs["stdout"], subprocess.PIPE)
        self.assertIs(kwargs["stderr"], subprocess.PIPE)
        self.assertTrue(kwargs["text"])
        self.assertGreater(kwargs["timeout"], 30.0)

    def test_media_failure_surfaces_process_error(self):
        runner = RecordingProcessRunner(
            returncode=1,
            stderr="native playback failed",
        )
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "native playback failed",
        ):
            backend.play(derivative(Path(r"C:\private\easp.mp4")))

    def test_wrong_item_or_codec_is_rejected_before_process_launch(self):
        runner = RecordingProcessRunner()
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
        )
        self.assertFalse(backend.play(object()))
        item = derivative(Path(r"C:\private\easp.mp4"))
        self.assertFalse(
            backend.play(
                VerifiedStartupMediaDerivative(
                    sequence=item.sequence,
                    spec=item.spec,
                    path=item.path,
                    converted_sha256=item.converted_sha256,
                    converted_size_bytes=item.converted_size_bytes,
                    container=item.container,
                    video_codec=item.video_codec,
                    pixel_format="yuv444p",
                    audio_codec=item.audio_codec,
                )
            )
        )
        self.assertEqual(runner.calls, [])

    def test_non_windows_invalid_runner_and_unsafe_path_fail_closed(self):
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "requires Windows",
        ):
            WindowsWpfStartupMediaBackend(
                platform_system="Linux",
                runner=lambda *args, **kwargs: None,
            )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "runner must be callable",
        ):
            WindowsWpfStartupMediaBackend(
                platform_system="Windows",
                runner=object(),
            )
        runner = RecordingProcessRunner()
        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=runner,
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "represented safely",
        ):
            backend.play(derivative(Path("bad\npath.mp4")))
        self.assertEqual(runner.calls, [])

    def test_timeout_and_process_start_errors_are_visible(self):
        item = derivative(Path(r"C:\private\easp.mp4"))

        def timeout_runner(command, **kwargs):
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])

        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=timeout_runner,
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "timed out",
        ):
            backend.play(item)

        def missing_runner(command, **kwargs):
            raise OSError("missing")

        backend = WindowsWpfStartupMediaBackend(
            platform_system="Windows",
            runner=missing_runner,
        )
        with self.assertRaisesRegex(
            WindowsStartupMediaBackendError,
            "could not start",
        ):
            backend.play(item)
