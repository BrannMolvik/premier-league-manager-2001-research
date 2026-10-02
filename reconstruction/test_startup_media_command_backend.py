from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import unittest

from original_startup_media import OriginalStartupMediaSpec
from startup_media_command_backend import (
    StartupMediaCommandBackendError,
    SynchronousCommandStartupMediaBackend,
)
from startup_media_derivatives import VerifiedStartupMediaDerivative


def derivative(path: Path) -> VerifiedStartupMediaDerivative:
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
        sequence=0,
        spec=spec,
        path=path,
        converted_sha256="a" * 64,
        converted_size_bytes=123,
        container="mp4",
        video_codec="h264",
        pixel_format="yuv420p",
        audio_codec="aac",
    )


class RecordingRunner:
    def __init__(self, returncode=0):
        self.returncode = returncode
        self.calls = []

    def __call__(self, command, *, check):
        self.calls.append((command, check))
        return SimpleNamespace(returncode=self.returncode)


class StartupMediaCommandBackendTests(unittest.TestCase):
    def test_verified_derivative_is_passed_as_final_command_argument_and_waited(self):
        runner = RecordingRunner()
        backend = SynchronousCommandStartupMediaBackend(
            "player.exe",
            ("--fullscreen", "--no-ui"),
            runner=runner,
        )
        item = derivative(Path(r"C:\private\fm2001\easp.mp4"))

        self.assertTrue(backend.play(item))
        self.assertEqual(
            runner.calls,
            [
                (
                    (
                        "player.exe",
                        "--fullscreen",
                        "--no-ui",
                        str(item.path),
                    ),
                    False,
                )
            ],
        )

    def test_nonzero_exit_is_not_reported_as_completed(self):
        runner = RecordingRunner(returncode=9)
        backend = SynchronousCommandStartupMediaBackend("player.exe", runner=runner)

        self.assertFalse(backend.play(derivative(Path("/private/easp.mp4"))))

    def test_non_verified_item_fails_without_launching_process(self):
        runner = RecordingRunner()
        backend = SynchronousCommandStartupMediaBackend("player.exe", runner=runner)

        self.assertFalse(backend.play(object()))
        self.assertEqual(runner.calls, [])

    def test_invalid_configuration_fails_closed(self):
        for executable in ("", "   ", None):
            with self.subTest(executable=executable):
                with self.assertRaises(StartupMediaCommandBackendError):
                    SynchronousCommandStartupMediaBackend(executable)
        with self.assertRaises(StartupMediaCommandBackendError):
            SynchronousCommandStartupMediaBackend("player.exe", ("ok", 1))
        with self.assertRaises(StartupMediaCommandBackendError):
            SynchronousCommandStartupMediaBackend(
                "player.exe",
                runner=object(),
            )


if __name__ == "__main__":
    unittest.main()
