"""Tests for the minimal FFmpeg synthetic roundtrip proof."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate17_ffmpeg_minimal_roundtrip import (
    MinimalFfmpegRoundtripError,
    SYNTHETIC_FRAME_COUNT,
    build_minimal_conversion_command,
    validate_build_proof,
    validate_decode_progress,
    validate_media_probe,
)
from startup_fmv_presentation import ORIGINAL_STARTUP_FMV_PRESENTATION


def probe_payload(width=320, height=480, frames=25):
    return json.dumps(
        {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "pix_fmt": "yuv420p",
                    "width": width,
                    "height": height,
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
    )


class Gate17MinimalFfmpegRoundtripTests(unittest.TestCase):
    def test_canonical_conversion_command_uses_recovered_scale_and_minimal_codecs(self):
        command = build_minimal_conversion_command(
            Path("minimal-ffmpeg.exe"),
            Path("input.mp4"),
            Path("output.mp4"),
        )
        self.assertIn(ORIGINAL_STARTUP_FMV_PRESENTATION.ffmpeg_filter, command)
        self.assertEqual(command[command.index("-c:v") + 1], "h264_mf")
        self.assertEqual(command[command.index("-c:a") + 1], "aac")
        self.assertEqual(command[command.index("-pix_fmt") + 1], "yuv420p")
        self.assertIn("-n", command)
        self.assertNotIn("libx264", command)

    def test_probe_accepts_input_and_scaled_output_shapes(self):
        source = validate_media_probe(
            probe_payload(),
            expected_width=320,
            expected_height=480,
            label="synthetic input",
        )
        output = validate_media_probe(
            probe_payload(width=640, height=480),
            expected_width=640,
            expected_height=480,
            label="minimal output",
        )
        self.assertEqual(source["video_frames"], SYNTHETIC_FRAME_COUNT)
        self.assertEqual(output["width"], 640)

    def test_probe_rejects_wrong_geometry_or_frame_count(self):
        with self.assertRaisesRegex(MinimalFfmpegRoundtripError, "video shape"):
            validate_media_probe(
                probe_payload(width=319),
                expected_width=320,
                expected_height=480,
                label="synthetic input",
            )
        with self.assertRaisesRegex(MinimalFfmpegRoundtripError, "frame count"):
            validate_media_probe(
                probe_payload(frames=24),
                expected_width=320,
                expected_height=480,
                label="synthetic input",
            )

    def test_decode_progress_requires_exact_frames_and_end(self):
        result = validate_decode_progress("frame=25\nprogress=end\n")
        self.assertTrue(result["video_decode_verified"])
        with self.assertRaisesRegex(MinimalFfmpegRoundtripError, "progress=end"):
            validate_decode_progress("frame=25\nprogress=continue\n")
        with self.assertRaisesRegex(MinimalFfmpegRoundtripError, "frame count"):
            validate_decode_progress("frame=24\nprogress=end\n")

    def test_build_proof_must_match_exact_minimal_binaries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg = root / "ffmpeg.exe"
            ffprobe = root / "ffprobe.exe"
            ffmpeg.write_bytes(b"ffmpeg")
            ffprobe.write_bytes(b"ffprobe")
            import hashlib
            payload = {
                "schema_version": 1,
                "audit_kind": "gate17_minimal_ffmpeg_build",
                "passed": True,
                "build_verified": True,
                "synthetic_roundtrip_verified": False,
                "production_migration_ready": False,
                "legal_compliance_claimed": False,
                "ffmpeg_sha256": hashlib.sha256(b"ffmpeg").hexdigest(),
                "ffprobe_sha256": hashlib.sha256(b"ffprobe").hexdigest(),
            }
            result = validate_build_proof(payload, ffmpeg, ffprobe)
            self.assertEqual(result["build_proof_ffmpeg_sha256"], payload["ffmpeg_sha256"])

            payload["ffmpeg_sha256"] = "0" * 64
            with self.assertRaisesRegex(MinimalFfmpegRoundtripError, "differs from build proof"):
                validate_build_proof(payload, ffmpeg, ffprobe)


if __name__ == "__main__":
    unittest.main()
