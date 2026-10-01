"""Synthetic tests for the Gate-14 verified TGQ conversion foundation."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from original_startup_media import OriginalStartupMediaSpec
from startup_media_conversion import (
    StartupMediaConversionError,
    convert_verified_startup_media,
)


PAYLOAD = b"synthetic verified tgq source"


def media_spec(
    *,
    source_path="FMV/test.tgq",
    payload=PAYLOAD,
    frames=7,
):
    return OriginalStartupMediaSpec(
        source_path=source_path,
        source_sha256=sha256(payload).hexdigest(),
        size_bytes=len(payload),
        startup_callsite_va=0x1000,
        playback_wrapper_va=0x2000,
        playback_flag_bit0=False,
        video_width=320,
        video_height=480,
        frame_rate=25,
        decoded_video_frames=frames,
        audio_sample_rate=22_050,
        audio_channels=2,
    )


class FakeMediaTools:
    def __init__(self, spec, *, probe_overrides=None, fail_ffmpeg=False):
        self.spec = spec
        self.probe_overrides = probe_overrides or {}
        self.fail_ffmpeg = fail_ffmpeg
        self.commands = []

    def __call__(self, command):
        command = tuple(str(item) for item in command)
        self.commands.append(command)
        executable = Path(command[0]).name

        if command[1:] == ("-version",):
            return f"{executable} version synthetic-1\n"

        if executable == "ffmpeg":
            if self.fail_ffmpeg:
                raise StartupMediaConversionError("synthetic ffmpeg failure")
            output = Path(command[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"lossless converted fixture")
            return ""

        if executable == "ffprobe":
            video = {
                "index": 0,
                "codec_type": "video",
                "codec_name": "ffv1",
                "width": self.spec.video_width,
                "height": self.spec.video_height,
                "r_frame_rate": f"{self.spec.frame_rate}/1",
                "nb_read_frames": str(self.spec.decoded_video_frames),
            }
            audio = {
                "index": 1,
                "codec_type": "audio",
                "codec_name": "pcm_s16le",
                "sample_rate": str(self.spec.audio_sample_rate),
                "channels": self.spec.audio_channels,
                "nb_read_frames": "1",
            }
            for key, value in self.probe_overrides.items():
                stream_name, field = key.split(".", 1)
                target = video if stream_name == "video" else audio
                target[field] = value
            return json.dumps({"streams": [video, audio]})

        raise AssertionError(f"unexpected command: {command}")


class StartupMediaConversionTests(unittest.TestCase):
    def fixture(self, temp, *, payload=PAYLOAD, spec=None):
        root = Path(temp)
        source_root = root / "source"
        output_root = root / "converted"
        spec = spec or media_spec(payload=payload)
        source = source_root / Path(*Path(spec.source_path).parts)
        source.parent.mkdir(parents=True)
        source.write_bytes(payload)
        return source_root, output_root, spec

    def test_verified_source_converts_transactionally_and_writes_provenance_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            source_root, output_root, spec = self.fixture(temp)
            tools = FakeMediaTools(spec)

            converted = convert_verified_startup_media(
                source_root,
                output_root,
                specs=(spec,),
                runner=tools,
            )

            self.assertEqual(len(converted), 1)
            item = converted[0]
            self.assertEqual(item.source_path, "FMV/test.tgq")
            self.assertEqual(item.source_sha256, spec.source_sha256)
            self.assertEqual(item.output_path, "FMV/test.mkv")
            self.assertEqual(item.video_codec, "ffv1")
            self.assertEqual(item.audio_codec, "pcm_s16le")
            self.assertEqual(item.frame_rate, "25/1")
            self.assertEqual(item.decoded_video_frames, spec.decoded_video_frames)
            self.assertEqual(item.audio_sample_rate, 22_050)
            self.assertEqual(item.audio_channels, 2)

            final = output_root / "FMV/test.mkv"
            self.assertEqual(final.read_bytes(), b"lossless converted fixture")
            self.assertFalse((output_root / "FMV/test.tmp.mkv").exists())

            receipt = json.loads(
                (output_root / "startup_media_conversion_receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["schema_version"], 1)
            self.assertEqual(receipt["container"], "matroska")
            self.assertEqual(receipt["video_codec"], "ffv1")
            self.assertEqual(receipt["audio_codec"], "pcm_s16le")
            self.assertFalse(receipt["final_playback_claimed"])
            self.assertEqual(receipt["files"][0]["source_sha256"], spec.source_sha256)
            self.assertEqual(receipt["files"][0]["output_path"], "FMV/test.mkv")
            self.assertNotIn(str(source_root.resolve()), json.dumps(receipt))
            self.assertNotIn(str(output_root.resolve()), json.dumps(receipt))
            self.assertEqual(
                receipt["files"][0]["conversion_command"][-1],
                "FMV/test.mkv",
            )

            ffmpeg_calls = [
                command for command in tools.commands
                if Path(command[0]).name == "ffmpeg"
                and command[1:] != ("-version",)
            ]
            self.assertEqual(len(ffmpeg_calls), 1)
            command = ffmpeg_calls[0]
            self.assertIn("-n", command)
            self.assertIn("ffv1", command)
            self.assertIn("pcm_s16le", command)
            self.assertTrue(command[-1].endswith("FMV/test.tmp.mkv"))

    def test_source_hash_mismatch_fails_before_tools_or_output_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            source_root, output_root, spec = self.fixture(
                temp,
                payload=b"wrong source bytes",
                spec=media_spec(),
            )
            tools = FakeMediaTools(spec)
            with self.assertRaisesRegex(
                StartupMediaConversionError,
                "source validation failed",
            ):
                convert_verified_startup_media(
                    source_root,
                    output_root,
                    specs=(spec,),
                    runner=tools,
                )
            self.assertEqual(tools.commands, [])
            self.assertFalse(output_root.exists())

    def test_probe_mismatch_removes_temporary_output_and_writes_no_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            source_root, output_root, spec = self.fixture(temp)
            tools = FakeMediaTools(
                spec,
                probe_overrides={"video.nb_read_frames": "6"},
            )
            with self.assertRaisesRegex(
                StartupMediaConversionError,
                "frame count differs",
            ):
                convert_verified_startup_media(
                    source_root,
                    output_root,
                    specs=(spec,),
                    runner=tools,
                )

            self.assertFalse((output_root / "FMV/test.mkv").exists())
            self.assertFalse((output_root / "FMV/test.tmp.mkv").exists())
            self.assertFalse(
                (output_root / "startup_media_conversion_receipt.json").exists()
            )

    def test_existing_final_or_receipt_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            source_root, output_root, spec = self.fixture(temp)
            final = output_root / "FMV/test.mkv"
            final.parent.mkdir(parents=True)
            final.write_bytes(b"keep me")
            tools = FakeMediaTools(spec)
            with self.assertRaisesRegex(
                StartupMediaConversionError,
                "already exists",
            ):
                convert_verified_startup_media(
                    source_root,
                    output_root,
                    specs=(spec,),
                    runner=tools,
                )
            self.assertEqual(final.read_bytes(), b"keep me")
            self.assertEqual(tools.commands, [])

        with tempfile.TemporaryDirectory() as temp:
            source_root, output_root, spec = self.fixture(temp)
            output_root.mkdir(parents=True)
            receipt = output_root / "startup_media_conversion_receipt.json"
            receipt.write_text("keep me", encoding="utf-8")
            tools = FakeMediaTools(spec)
            with self.assertRaisesRegex(
                StartupMediaConversionError,
                "receipt already exists",
            ):
                convert_verified_startup_media(
                    source_root,
                    output_root,
                    specs=(spec,),
                    runner=tools,
                )
            self.assertEqual(receipt.read_text(encoding="utf-8"), "keep me")
            self.assertEqual(tools.commands, [])

    def test_multi_file_failure_promotes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_root = root / "source"
            output_root = root / "converted"
            first = media_spec(source_path="FMV/one.tgq", frames=7)
            second = media_spec(source_path="FMV/two.tgq", frames=8)
            for spec in (first, second):
                path = source_root / Path(*Path(spec.source_path).parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(PAYLOAD)

            class FailSecondProbe(FakeMediaTools):
                def __call__(self, command):
                    command = tuple(str(item) for item in command)
                    if (
                        Path(command[0]).name == "ffprobe"
                        and command[1:] != ("-version",)
                        and command[-1].endswith("two.tmp.mkv")
                    ):
                        self.commands.append(command)
                        payload = {
                            "streams": [
                                {
                                    "index": 0,
                                    "codec_type": "video",
                                    "codec_name": "ffv1",
                                    "width": 320,
                                    "height": 480,
                                    "r_frame_rate": "25/1",
                                    "nb_read_frames": "999",
                                },
                                {
                                    "index": 1,
                                    "codec_type": "audio",
                                    "codec_name": "pcm_s16le",
                                    "sample_rate": "22050",
                                    "channels": 2,
                                },
                            ]
                        }
                        return json.dumps(payload)
                    return super().__call__(command)

            tools = FailSecondProbe(first)
            with self.assertRaises(StartupMediaConversionError):
                convert_verified_startup_media(
                    source_root,
                    output_root,
                    specs=(first, second),
                    runner=tools,
                )

            self.assertFalse((output_root / "FMV/one.mkv").exists())
            self.assertFalse((output_root / "FMV/two.mkv").exists())
            self.assertFalse((output_root / "FMV/one.tmp.mkv").exists())
            self.assertFalse((output_root / "FMV/two.tmp.mkv").exists())
            self.assertFalse(
                (output_root / "startup_media_conversion_receipt.json").exists()
            )

    def test_invalid_relative_paths_and_receipt_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = media_spec(source_path="../escape.tgq")
            with self.assertRaisesRegex(
                StartupMediaConversionError,
                "stay inside",
            ):
                convert_verified_startup_media(
                    root / "source",
                    root / "out",
                    specs=(spec,),
                    runner=FakeMediaTools(spec),
                )

        with tempfile.TemporaryDirectory() as temp:
            source_root, output_root, spec = self.fixture(temp)
            with self.assertRaisesRegex(
                StartupMediaConversionError,
                "receipt name",
            ):
                convert_verified_startup_media(
                    source_root,
                    output_root,
                    specs=(spec,),
                    runner=FakeMediaTools(spec),
                    receipt_name="../receipt.json",
                )


if __name__ == "__main__":
    unittest.main()
