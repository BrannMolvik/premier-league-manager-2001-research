from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from original_startup_media import (
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE,
)
from startup_media_runtime_cache import (
    PACKAGED_FFMPEG_RELATIVE_PATH,
    RuntimeStartupMediaError,
    _validate_derivative_decode,
    prepare_runtime_startup_media,
    resolve_startup_ffmpeg,
    runtime_startup_media_contract,
)


class FakeRunner:
    def __init__(self):
        self.calls = []
        self.conversions = 0

    def __call__(self, command, **kwargs):
        command = tuple(str(item) for item in command)
        self.calls.append(command)
        if len(command) >= 2 and command[1] == "-version":
            return SimpleNamespace(
                returncode=0,
                stdout="ffmpeg version test-build\n",
                stderr="",
            )
        if len(command) >= 2 and command[1] == "convert":
            output = Path(command[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(
                b"converted-" + output.stem.encode("ascii")
            )
            self.conversions += 1
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if "-progress" in command:
            path = Path(command[command.index("-i") + 1])
            frames = 97 if path.stem == "easp" else 1275
            return SimpleNamespace(
                returncode=0,
                stdout=f"frame={frames}\nprogress=end\n",
                stderr="",
            )
        if "-map" in command and "0:a:0" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(command)


def fake_plan_builder(source, output, *, ffmpeg_executable, **kwargs):
    output = Path(output)
    plans = []
    for spec in ORIGINAL_STARTUP_MEDIA_SEQUENCE:
        target = output / (Path(spec.source_path).stem + ".mp4")
        plans.append(
            SimpleNamespace(
                spec=spec,
                source_path=Path(source) / spec.source_path,
                output_path=target,
                ffmpeg_args=(str(ffmpeg_executable), "convert", str(target)),
            )
        )
    return tuple(plans)


class RuntimeStartupMediaTests(unittest.TestCase):
    def test_packaged_ffmpeg_is_preferred_over_system_lookup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            packaged = root / PACKAGED_FFMPEG_RELATIVE_PATH
            packaged.parent.mkdir(parents=True)
            packaged.write_bytes(b"ffmpeg")
            lookup = unittest.mock.Mock(return_value="/system/ffmpeg")

            self.assertEqual(
                resolve_startup_ffmpeg(root, system_which=lookup),
                packaged.resolve(),
            )
            lookup.assert_not_called()

    def test_missing_ffmpeg_fails_visibly(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeStartupMediaError, "FFmpeg is unavailable"):
                resolve_startup_ffmpeg(
                    temp,
                    system_which=lambda _name: None,
                )

    def test_decode_validator_requires_exact_video_frame_count_and_audio_stream(self):
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "easp.mp4"
            path.write_bytes(b"placeholder")
            _validate_derivative_decode(
                path,
                expected_frames=97,
                ffmpeg=Path("/fake/ffmpeg"),
                runner=runner,
            )
        self.assertTrue(any("-progress" in call for call in runner.calls))
        self.assertTrue(any("0:a:0" in call for call in runner.calls))

    def test_first_run_converts_receipts_and_second_run_reuses_hash_checked_cache(self):
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "game"
            app = root / "app"
            cache = root / "cache"
            ffmpeg = root / "ffmpeg.exe"
            game.mkdir()
            app.mkdir()
            ffmpeg.write_bytes(b"verified-ffmpeg-binary")

            with patch(
                "startup_media_runtime_cache.build_startup_media_conversion_plans",
                side_effect=fake_plan_builder,
            ) as plans:
                first = prepare_runtime_startup_media(
                    game,
                    app,
                    cache_root=cache,
                    ffmpeg_executable=ffmpeg,
                    runner=runner,
                )
                first_conversion_count = runner.conversions
                second = prepare_runtime_startup_media(
                    game,
                    app,
                    cache_root=cache,
                    ffmpeg_executable=ffmpeg,
                    runner=runner,
                )

        self.assertEqual(first_conversion_count, 2)
        self.assertEqual(runner.conversions, 2)
        self.assertEqual(tuple(item.spec for item in first), ORIGINAL_STARTUP_MEDIA_SEQUENCE)
        self.assertEqual(
            tuple(item.converted_sha256 for item in first),
            tuple(item.converted_sha256 for item in second),
        )
        self.assertGreaterEqual(plans.call_count, 3)

    def test_profile_change_forces_fresh_conversion_and_receipt_identity(self):
        runner = FakeRunner()
        candidate = WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "game"
            app = root / "app"
            cache = root / "cache"
            ffmpeg = root / "ffmpeg.exe"
            game.mkdir()
            app.mkdir()
            ffmpeg.write_bytes(b"same-verified-ffmpeg-binary")

            with patch(
                "startup_media_runtime_cache.build_startup_media_conversion_plans",
                side_effect=fake_plan_builder,
            ):
                prepare_runtime_startup_media(
                    game,
                    app,
                    cache_root=cache,
                    ffmpeg_executable=ffmpeg,
                    runner=runner,
                )
                self.assertEqual(runner.conversions, 2)
                prepare_runtime_startup_media(
                    game,
                    app,
                    cache_root=cache,
                    ffmpeg_executable=ffmpeg,
                    profile=candidate,
                    runner=runner,
                )

            self.assertEqual(runner.conversions, 4)
            receipt = __import__("json").loads(
                (cache / "startup-media-runtime-receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["profile"]["video_encoder"], "h264_mf")
            self.assertEqual(
                runtime_startup_media_contract(candidate)["conversion_profile"][
                    "video_encoder"
                ],
                "h264_mf",
            )

    def test_cache_byte_drift_forces_fresh_conversion(self):
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "game"
            app = root / "app"
            cache = root / "cache"
            ffmpeg = root / "ffmpeg.exe"
            game.mkdir()
            app.mkdir()
            ffmpeg.write_bytes(b"verified-ffmpeg-binary")

            with patch(
                "startup_media_runtime_cache.build_startup_media_conversion_plans",
                side_effect=fake_plan_builder,
            ):
                prepare_runtime_startup_media(
                    game,
                    app,
                    cache_root=cache,
                    ffmpeg_executable=ffmpeg,
                    runner=runner,
                )
                (cache / "easp.mp4").write_bytes(b"tampered")
                prepare_runtime_startup_media(
                    game,
                    app,
                    cache_root=cache,
                    ffmpeg_executable=ffmpeg,
                    runner=runner,
                )

        self.assertEqual(runner.conversions, 4)

    def test_contract_keeps_player_visible_windows_acceptance_open(self):
        contract = runtime_startup_media_contract()
        self.assertTrue(contract["one_time_private_cache"])
        self.assertTrue(contract["source_hash_reverified_before_cache_use"])
        self.assertTrue(contract["cached_output_hash_reverified"])
        self.assertTrue(contract["decoded_video_frame_count_reverified_on_conversion"])
        self.assertTrue(contract["audio_stream_decode_reverified_on_conversion"])
        self.assertFalse(contract["windows_playback_verified"])
        self.assertFalse(contract["skip_input_recovered"])
        self.assertFalse(contract["transition_timing_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
