"""Tests for fail-closed ordered startup-media playback orchestration."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import unittest
from unittest.mock import patch

from original_startup_media import OriginalStartupMediaSpec
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_playback import (
    StartupMediaPlaybackError,
    load_and_play_verified_startup_sequence,
    play_verified_startup_sequence,
)


def spec(name: str, *, marker: bytes, flag: bool, frames: int):
    return OriginalStartupMediaSpec(
        source_path=f"FMV/{name}.tgq",
        source_sha256=sha256(marker).hexdigest(),
        size_bytes=len(marker),
        startup_callsite_va=0x5000 + frames,
        playback_wrapper_va=0x461E20,
        playback_flag_bit0=flag,
        video_width=320,
        video_height=480,
        frame_rate=25,
        decoded_video_frames=frames,
        audio_sample_rate=22_050,
        audio_channels=2,
    )


def derivative(sequence: int, item: OriginalStartupMediaSpec, path: Path):
    return VerifiedStartupMediaDerivative(
        sequence=sequence,
        spec=item,
        path=path,
        converted_sha256=("a" if sequence == 0 else "b") * 64,
        converted_size_bytes=100 + sequence,
        container="mp4",
        video_codec="h264",
        pixel_format="yuv420p",
        audio_codec="aac",
    )


class RecordingBackend:
    def __init__(self, *, reject_sequence=None, raise_sequence=None, return_value=True):
        self.calls = []
        self.reject_sequence = reject_sequence
        self.raise_sequence = raise_sequence
        self.return_value = return_value

    def play(self, item):
        self.calls.append(item)
        if item.sequence == self.raise_sequence:
            raise OSError("synthetic player failure")
        if item.sequence == self.reject_sequence:
            return False
        return self.return_value


class StartupMediaPlaybackTests(unittest.TestCase):
    def fixture(self):
        specs = (
            spec("first", marker=b"first-source", flag=False, frames=7),
            spec("second", marker=b"second-source", flag=True, frames=11),
        )
        items = (
            derivative(0, specs[0], Path("/private/first.mp4")),
            derivative(1, specs[1], Path("/private/second.mp4")),
        )
        return specs, items

    def test_verified_sequence_plays_synchronously_in_source_order(self):
        specs, items = self.fixture()
        backend = RecordingBackend()

        summary = play_verified_startup_sequence(
            items,
            backend,
            specs=specs,
        )

        self.assertEqual(backend.calls, list(items))
        self.assertEqual(
            tuple(step.source_path for step in summary.steps),
            ("FMV/first.tgq", "FMV/second.tgq"),
        )
        self.assertEqual(
            tuple(step.playback_flag_bit0 for step in summary.steps),
            (False, True),
        )
        self.assertTrue(all(step.completed for step in summary.steps))
        self.assertTrue(summary.source_order_preserved)
        self.assertFalse(summary.playback_flag_semantics_recovered)
        self.assertFalse(summary.skip_input_recovered)
        self.assertFalse(summary.transition_timing_recovered)
        self.assertFalse(summary.gate14_complete)

    def test_reordered_or_mismatched_verified_derivatives_fail_before_backend(self):
        specs, items = self.fixture()
        backend = RecordingBackend()

        for bad in (
            tuple(reversed(items)),
            (items[0],),
            (items[0], derivative(2, specs[1], Path("/private/second.mp4"))),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(StartupMediaPlaybackError):
                    play_verified_startup_sequence(
                        bad,
                        backend,
                        specs=specs,
                    )
                self.assertEqual(backend.calls, [])

    def test_duplicate_derivative_path_fails_before_backend(self):
        specs, items = self.fixture()
        duplicate = derivative(1, specs[1], items[0].path)
        backend = RecordingBackend()

        with self.assertRaisesRegex(
            StartupMediaPlaybackError,
            "reuses one derivative path",
        ):
            play_verified_startup_sequence(
                (items[0], duplicate),
                backend,
                specs=specs,
            )
        self.assertEqual(backend.calls, [])

    def test_backend_rejection_aborts_before_later_media(self):
        specs, items = self.fixture()
        backend = RecordingBackend(reject_sequence=0)

        with self.assertRaisesRegex(
            StartupMediaPlaybackError,
            "did not complete sequence 0",
        ):
            play_verified_startup_sequence(items, backend, specs=specs)

        self.assertEqual(backend.calls, [items[0]])

    def test_backend_exception_is_wrapped_and_aborts(self):
        specs, items = self.fixture()
        backend = RecordingBackend(raise_sequence=0)

        with self.assertRaisesRegex(
            StartupMediaPlaybackError,
            "synthetic player failure",
        ):
            play_verified_startup_sequence(items, backend, specs=specs)

        self.assertEqual(backend.calls, [items[0]])

    def test_truthy_non_boolean_backend_result_is_not_accepted(self):
        specs, items = self.fixture()
        backend = RecordingBackend(return_value=1)

        with self.assertRaisesRegex(
            StartupMediaPlaybackError,
            "did not complete sequence 0",
        ):
            play_verified_startup_sequence(items, backend, specs=specs)
        self.assertEqual(backend.calls, [items[0]])

    def test_missing_backend_or_empty_source_contract_fails_closed(self):
        specs, items = self.fixture()
        with self.assertRaisesRegex(StartupMediaPlaybackError, "play\(\)"):
            play_verified_startup_sequence(items, object(), specs=specs)
        with self.assertRaisesRegex(StartupMediaPlaybackError, "empty source contract"):
            play_verified_startup_sequence((), RecordingBackend(), specs=())

    def test_load_and_play_revalidates_receipt_derivatives_before_backend(self):
        specs, items = self.fixture()
        backend = RecordingBackend()
        receipt = Path("/private/receipt.json")
        repo = Path("/repo")

        with patch(
            "startup_media_playback.load_verified_startup_media_derivatives",
            return_value=items,
        ) as load:
            summary = load_and_play_verified_startup_sequence(
                receipt_path=receipt,
                repo_root=repo,
                backend=backend,
                specs=specs,
            )

        load.assert_called_once_with(
            receipt_path=receipt,
            repo_root=repo,
            specs=specs,
        )
        self.assertEqual(backend.calls, list(items))
        self.assertEqual(len(summary.steps), 2)


if __name__ == "__main__":
    unittest.main()
