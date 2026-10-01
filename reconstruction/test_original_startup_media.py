"""Tests for the source-backed FM2001 startup-media and conversion contracts."""
from hashlib import sha256
import os
from pathlib import Path
import tempfile
import unittest

from original_startup_media import (
    EA_SPORTS_STARTUP_MEDIA,
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    PREMIER_LEAGUE_INTRO_MEDIA,
    OriginalStartupMediaError,
    OriginalStartupMediaSpec,
    build_startup_media_conversion_plans,
    build_startup_media_ffprobe_args,
    validate_original_startup_media,
    validate_startup_media_probe,
)


class OriginalStartupMediaTests(unittest.TestCase):
    def test_verified_startup_sequence_and_media_measurements_are_locked(self):
        self.assertEqual(
            ORIGINAL_STARTUP_MEDIA_SEQUENCE,
            (EA_SPORTS_STARTUP_MEDIA, PREMIER_LEAGUE_INTRO_MEDIA),
        )
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.source_path, "FMV/easp.tgq")
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.size_bytes, 1_383_304)
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.startup_callsite_va, 0x530FAE)
        self.assertFalse(EA_SPORTS_STARTUP_MEDIA.playback_flag_bit0)
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.source_path, "FMV/premintro.tgq")
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.size_bytes, 28_434_180)
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.startup_callsite_va, 0x531175)
        self.assertTrue(PREMIER_LEAGUE_INTRO_MEDIA.playback_flag_bit0)
        for spec in ORIGINAL_STARTUP_MEDIA_SEQUENCE:
            self.assertEqual(spec.playback_wrapper_va, 0x461E20)
            self.assertEqual((spec.video_width, spec.video_height), (320, 480))
            self.assertEqual(spec.frame_rate, 25)
            self.assertEqual(spec.audio_sample_rate, 22_050)
            self.assertEqual(spec.audio_channels, 2)
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.decoded_video_frames, 97)
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.decoded_video_frames, 1_275)

    def test_validator_can_prove_a_deliberately_supplied_source_without_special_cases(self):
        payload = b"synthetic tgq fixture"
        spec = OriginalStartupMediaSpec(
            source_path="FMV/test.tgq",
            source_sha256=sha256(payload).hexdigest(),
            size_bytes=len(payload),
            startup_callsite_va=0x1000,
            playback_wrapper_va=0x2000,
            playback_flag_bit0=False,
            video_width=320,
            video_height=480,
            frame_rate=25,
            decoded_video_frames=1,
            audio_sample_rate=22_050,
            audio_channels=2,
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / spec.source_path
            target.parent.mkdir(parents=True)
            target.write_bytes(payload)
            self.assertEqual(
                validate_original_startup_media(root, specs=(spec,)),
                (spec,),
            )
            target.write_bytes(payload + b"x")
            with self.assertRaisesRegex(
                OriginalStartupMediaError, "size mismatch"
            ):
                validate_original_startup_media(root, specs=(spec,))

    def test_playback_flag_is_kept_neutral_not_renamed_as_confirmed_skip_semantics(self):
        names = set(OriginalStartupMediaSpec.__dataclass_fields__)
        self.assertIn("playback_flag_bit0", names)
        self.assertNotIn("skippable", names)
        self.assertNotIn("skip_input", names)

    def test_conversion_plans_validate_sources_and_preserve_startup_order(self):
        first_payload = b"first synthetic tgq"
        second_payload = b"second synthetic tgq"
        first = OriginalStartupMediaSpec(
            source_path="FMV/first.tgq",
            source_sha256=sha256(first_payload).hexdigest(),
            size_bytes=len(first_payload),
            startup_callsite_va=0x1000,
            playback_wrapper_va=0x2000,
            playback_flag_bit0=False,
            video_width=320,
            video_height=480,
            frame_rate=25,
            decoded_video_frames=7,
            audio_sample_rate=22_050,
            audio_channels=2,
        )
        second = OriginalStartupMediaSpec(
            source_path="FMV/second.tgq",
            source_sha256=sha256(second_payload).hexdigest(),
            size_bytes=len(second_payload),
            startup_callsite_va=0x1001,
            playback_wrapper_va=0x2000,
            playback_flag_bit0=True,
            video_width=320,
            video_height=480,
            frame_rate=25,
            decoded_video_frames=11,
            audio_sample_rate=22_050,
            audio_channels=2,
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_root = root / "source"
            output_root = root / "converted"
            (source_root / "FMV").mkdir(parents=True)
            (source_root / first.source_path).write_bytes(first_payload)
            (source_root / second.source_path).write_bytes(second_payload)

            plans = build_startup_media_conversion_plans(
                source_root,
                output_root,
                specs=(first, second),
                ffmpeg_executable="ffmpeg-test",
            )
            self.assertEqual([item.spec for item in plans], [first, second])
            self.assertEqual(
                [item.output_path.name for item in plans],
                ["first.mp4", "second.mp4"],
            )
            for plan in plans:
                self.assertEqual(plan.ffmpeg_args[0], "ffmpeg-test")
                self.assertIn("-n", plan.ffmpeg_args)
                self.assertIn("-fps_mode", plan.ffmpeg_args)
                self.assertIn("passthrough", plan.ffmpeg_args)
                self.assertIn("libx264", plan.ffmpeg_args)
                self.assertIn("yuv420p", plan.ffmpeg_args)
                self.assertIn("aac", plan.ffmpeg_args)
                self.assertEqual(plan.ffmpeg_args[-1], str(plan.output_path))

            (source_root / second.source_path).write_bytes(second_payload + b"x")
            with self.assertRaisesRegex(
                OriginalStartupMediaError, "size mismatch"
            ):
                build_startup_media_conversion_plans(
                    source_root,
                    output_root,
                    specs=(first, second),
                )

    def test_probe_validator_requires_exact_stream_shape_and_original_geometry(self):
        spec = PREMIER_LEAGUE_INTRO_MEDIA
        probe = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "pix_fmt": "yuv420p",
                    "width": 320,
                    "height": 480,
                    "avg_frame_rate": "25/1",
                    "nb_read_frames": str(spec.decoded_video_frames),
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "22050",
                    "channels": 2,
                },
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            },
        }
        verified = validate_startup_media_probe(spec, probe)
        self.assertIs(verified.spec, spec)
        self.assertEqual(verified.container_name, "mp4")
        self.assertEqual(verified.video_frames, 1_275)
        self.assertEqual(verified.audio_sample_rate, 22_050)
        self.assertEqual(verified.audio_channels, 2)

        bad_frames = {
            **probe,
            "streams": [
                {**probe["streams"][0], "nb_read_frames": "1274"},
                probe["streams"][1],
            ],
        }
        with self.assertRaisesRegex(
            OriginalStartupMediaError, "frame count differs"
        ):
            validate_startup_media_probe(spec, bad_frames)

        extra_stream = {
            **probe,
            "streams": [
                *probe["streams"],
                {"codec_type": "subtitle", "codec_name": "mov_text"},
            ],
        }
        with self.assertRaisesRegex(
            OriginalStartupMediaError, "exactly one video and one audio"
        ):
            validate_startup_media_probe(spec, extra_stream)

    def test_probe_command_counts_frames_and_returns_json(self):
        args = build_startup_media_ffprobe_args(
            Path("converted") / "premintro.mp4",
            ffprobe_executable="ffprobe-test",
        )
        self.assertEqual(args[0], "ffprobe-test")
        self.assertIn("-count_frames", args)
        self.assertIn("-show_streams", args)
        self.assertIn("-show_format", args)
        self.assertIn("json", args)
        self.assertEqual(args[-1], str(Path("converted") / "premintro.mp4"))

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_GAME_ROOT"),
        "Original licensed startup media intentionally absent from hosted CI",
    )
    def test_opt_in_original_tgq_files_match_the_source_contract(self):
        root = Path(os.environ["FM2001_ORIGINAL_GAME_ROOT"])
        self.assertEqual(
            validate_original_startup_media(root),
            ORIGINAL_STARTUP_MEDIA_SEQUENCE,
        )


if __name__ == "__main__":
    unittest.main()
