"""Synthetic tests for the private Gate-14 startup-media conversion runner."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate14_startup_media_convert import (
    StartupMediaConversionAuditError,
    convert_and_receipt_startup_media,
    require_outside_repository,
)
from original_startup_media import OriginalStartupMediaSpec


def synthetic_spec(path: str, payload: bytes, *, frames: int, flag: bool):
    return OriginalStartupMediaSpec(
        source_path=path,
        source_sha256=sha256(payload).hexdigest(),
        size_bytes=len(payload),
        startup_callsite_va=0x1000 + frames,
        playback_wrapper_va=0x2000,
        playback_flag_bit0=flag,
        video_width=320,
        video_height=480,
        frame_rate=25,
        decoded_video_frames=frames,
        audio_sample_rate=22_050,
        audio_channels=2,
    )


def valid_probe(frames: int):
    return {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "h264",
                "pix_fmt": "yuv420p",
                "width": 320,
                "height": 480,
                "avg_frame_rate": "25/1",
                "nb_read_frames": str(frames),
            },
            {
                "codec_type": "audio",
                "codec_name": "aac",
                "sample_rate": "22050",
                "channels": 2,
            },
        ],
        "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
    }


class Gate14StartupMediaConversionTests(unittest.TestCase):
    def fixture(self, temp):
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        source = root / "private-source"
        (source / "FMV").mkdir(parents=True)
        output = root / "private-converted"
        receipt = root / "private-receipts" / "startup-media.json"

        first_payload = b"synthetic first tgq"
        second_payload = b"synthetic second tgq"
        first = synthetic_spec(
            "FMV/first.tgq", first_payload, frames=7, flag=False
        )
        second = synthetic_spec(
            "FMV/second.tgq", second_payload, frames=11, flag=True
        )
        (source / first.source_path).write_bytes(first_payload)
        (source / second.source_path).write_bytes(second_payload)
        return repo, source, output, receipt, (first, second)

    def fake_runner(self, probes):
        def run(command, *, label):
            if command == ("ffmpeg-test", "-version"):
                return "ffmpeg version test-build\n"
            if command == ("ffprobe-test", "-version"):
                return "ffprobe version test-build\n"
            if command[0] == "ffmpeg-test":
                target = Path(command[-1])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(("converted:" + target.stem).encode("ascii"))
                return ""
            if command[0] == "ffprobe-test":
                stem = Path(command[-1]).stem
                return json.dumps(probes[stem])
            raise AssertionError(f"unexpected command: {command!r} ({label})")
        return run

    def test_success_writes_receipt_only_after_both_exact_sources_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, source, output, receipt, specs = self.fixture(temp)
            runner = self.fake_runner({
                "first": valid_probe(7),
                "second": valid_probe(11),
            })
            with patch(
                "gate14_startup_media_convert._run_command",
                side_effect=runner,
            ):
                result = convert_and_receipt_startup_media(
                    source_root=source,
                    output_root=output,
                    receipt_path=receipt,
                    repo_root=repo,
                    ffmpeg_executable="ffmpeg-test",
                    ffprobe_executable="ffprobe-test",
                    specs=specs,
                )

            self.assertTrue(result["passed"])
            self.assertFalse(result["gate14_complete"])
            self.assertEqual(
                [item["source_path"] for item in result["outputs"]],
                ["FMV/first.tgq", "FMV/second.tgq"],
            )
            self.assertEqual(
                [item["decoded_video_frames"] for item in result["outputs"]],
                [7, 11],
            )
            self.assertEqual(
                [item["playback_flag_bit0"] for item in result["outputs"]],
                [False, True],
            )
            self.assertTrue(receipt.is_file())
            persisted = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(persisted, result)
            for item in result["outputs"]:
                converted = Path(item["converted_path"])
                self.assertTrue(converted.is_file())
                self.assertEqual(
                    item["converted_sha256"],
                    sha256(converted.read_bytes()).hexdigest(),
                )

    def test_tampered_source_fails_before_any_external_command_or_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, source, output, receipt, specs = self.fixture(temp)
            (source / specs[1].source_path).write_bytes(b"tampered")
            with patch("gate14_startup_media_convert._run_command") as command:
                with self.assertRaisesRegex(
                    StartupMediaConversionAuditError,
                    "source validation",
                ):
                    convert_and_receipt_startup_media(
                        source_root=source,
                        output_root=output,
                        receipt_path=receipt,
                        repo_root=repo,
                        specs=specs,
                    )
            command.assert_not_called()
            self.assertFalse(receipt.exists())

    def test_bad_probe_leaves_no_success_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, source, output, receipt, specs = self.fixture(temp)
            bad = valid_probe(11)
            bad["streams"][0]["nb_read_frames"] = "10"
            runner = self.fake_runner({
                "first": valid_probe(7),
                "second": bad,
            })
            with patch(
                "gate14_startup_media_convert._run_command",
                side_effect=runner,
            ):
                with self.assertRaisesRegex(
                    StartupMediaConversionAuditError,
                    "failed probe contract",
                ):
                    convert_and_receipt_startup_media(
                        source_root=source,
                        output_root=output,
                        receipt_path=receipt,
                        repo_root=repo,
                        ffmpeg_executable="ffmpeg-test",
                        ffprobe_executable="ffprobe-test",
                        specs=specs,
                    )
            self.assertFalse(receipt.exists())

    def test_existing_output_is_rejected_before_tool_version_or_conversion(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, source, output, receipt, specs = self.fixture(temp)
            output.mkdir()
            (output / "first.mp4").write_bytes(b"old evidence")
            with patch("gate14_startup_media_convert._run_command") as command:
                with self.assertRaisesRegex(
                    StartupMediaConversionAuditError,
                    "Refusing to overwrite existing converted media",
                ):
                    convert_and_receipt_startup_media(
                        source_root=source,
                        output_root=output,
                        receipt_path=receipt,
                        repo_root=repo,
                        specs=specs,
                    )
            command.assert_not_called()
            self.assertFalse(receipt.exists())

    def test_private_source_output_and_receipt_must_stay_outside_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            for target in (
                repo,
                repo / "source",
                repo / "converted",
                repo / "receipt.json",
            ):
                with self.assertRaisesRegex(
                    StartupMediaConversionAuditError,
                    "outside the Git repository",
                ):
                    require_outside_repository(target, repo, label="test path")


if __name__ == "__main__":
    unittest.main()
