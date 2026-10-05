from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import unittest

from original_startup_media import OriginalStartupMediaSpec
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_windows_backend import (
    WindowsMciStartupMediaBackend,
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
